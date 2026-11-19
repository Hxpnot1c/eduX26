"""Replay the recorded event logs under different fatigue / stuck detector settings (open loop: the same answers,
re-scored by learner.rebuild_state with each setting) and score each detector against the simulated truth.

    PYTHONPATH=<worktree> <venv>/bin/python docs/research/overnight/sims/sweep_detectors.py \
        [--runs results/runs.jsonl] [--variant current] [--scenario near] [--out results]

Truth (our choice, see edux_sim.TRUTH_PARAMS): the tired student is fatigued from minute 30 of every session;
nobody else ever is. The stuck student can never learn ped_formula; every other stuck flag is a false alarm
(the slow learner's are listed separately as ambiguous: a real teacher might call that stuck too).
Writes detector_sweep.csv and detector_sweep.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edux_sim as S   # noqa: E402

STUCK_PART = S.STUCK_PART
# grid (our choice); the first entry is settings.toml as is
FATIGUE_GRID = [(t, w, mp) for mp in (2, 1) for w in (4, 6, 8) for t in (-0.15, -0.25, -0.35, -0.45)]
FATIGUE_GRID.remove((-0.25, 4, 2))
FATIGUE_GRID.insert(0, (-0.25, 4, 2))


def stuck_rule_three(rows) -> set:
    """Alternative MCQ stuck rule (sim-only): the same point missed on three checks in the session."""
    misses = defaultdict(int)
    out = set()
    for r in rows:
        if r["evidence_type"] != "mcq_check" or r["weight"] <= 0:
            continue
        key = (r["part_id"], r["point_id"] or r["part_id"])
        if r["score"] < 0.67:
            misses[key] += 1
            if misses[key] >= 3:
                out.add(r["part_id"])
    return out


ALT_RULES = {
    # C (sim-only): errors on material the model thinks is known. After minute 25, the last k pieces of evidence
    # with p_before >= pb have mean score <= th.
    "C_known_k4_th0.25": ("C", 4, 0.25, 0.6),
    "C_known_k6_th0.5": ("C", 6, 0.5, 0.6),
    "C_known_k8_th0.6": ("C", 8, 0.6, 0.7),
    # D (sim-only, a control-chart idea): drop against the session's own baseline. Mean surprise of the last k
    # pieces after minute 25, minus the mean surprise before minute 25 (needs 4+ pieces), <= -drop.
    "D_baseline_k6_drop0.3": ("D", 6, 0.3, None),
    "D_baseline_k8_drop0.25": ("D", 8, 0.25, None),
}


def alt_flags(rows, start) -> dict:
    """Alternative fatigue rules on one session's weighted evidence rows (built-rule p_before and surprise).
    The parameters were picked on the pilot run (seeds 1-3) and are applied unchanged here."""
    from edux import learner
    mins = [(learner.parse_ts(r["ts"]) - learner.parse_ts(start)).total_seconds() / 60 for r in rows]
    out = {}
    for name, (kind, k, a, b) in ALT_RULES.items():
        flag = None
        if kind == "C":
            win = []
            for m, r in zip(mins, rows):
                if r["p_before"] >= b:
                    win.append(r["score"])
                if m >= 25 and len(win) >= k and statistics.mean(win[-k:]) <= a:
                    flag = m
                    break
        else:
            base = [r["surprise"] for m, r in zip(mins, rows) if m < 25]
            if len(base) >= 4:
                mean0, win = statistics.mean(base), []
                for m, r in zip(mins, rows):
                    if m >= 25:
                        win.append(r["surprise"])
                        if len(win) >= k and statistics.mean(win[-k:]) - mean0 <= -a:
                            flag = m
                            break
        out[name] = flag
    return out


def job_db(runs):
    """All the students in one database, one after another (rebuilds in one file can't run in parallel)."""
    return [x for run in runs for x in job((run, None))]


def job(args):
    run, scenario = args
    from edux import learner
    learner.use_database(Path(run["db"]), Path(run["content_db"]))
    sid = run["student_id"]
    results = []
    for threshold, window, min_parts in FATIGUE_GRID:
        name = f"fatigue_t{threshold}_w{window}_p{min_parts}"
        S.VARIANT_EXTRA[name] = {"session.fatigue_threshold": threshold, "session.fatigue_window": window,
                                 "session.fatigue_min_parts": min_parts}
        S.use_settings(name)
        learner.rebuild_state(sid)
        conn = learner._conn()
        first = (threshold, window, min_parts) == FATIGUE_GRID[0]
        for sess in learner.sessions(sid):
            rows = learner._session_evidence(conn, sid, sess["session_id"], sess["end"])
            alt = {}
            if first:
                weighted = conn.execute(
                    """SELECT l.ts, l.score, d.p_before, d.surprise FROM evidence_log l JOIN evidence_derived d
                       ON d.evidence_id = l.id WHERE l.student_id = ? AND l.ts >= ? AND l.ts <= ? AND d.weight > 0
                       ORDER BY l.ts, l.id""", (sid, sess["session_id"], sess["end"])).fetchall()
                alt = alt_flags(weighted, sess["session_id"])
            stuck_a = {p["part_id"] for p in learner.stuck_parts(rows)}
            stuck_b = stuck_rule_three(rows)
            attempted = {r["part_id"] for r in rows}
            results.append({"kind": run["kind"], "seed": run["seed"], "threshold": threshold, "window": window,
                            "min_parts": min_parts, "minutes": sess["minutes"], "onset": sess["fatigue_onset_minute"],
                            "stuck_true_attempted": int(run["kind"] == "stuck" and STUCK_PART in attempted),
                            "stuck_a_hit": int(run["kind"] == "stuck" and STUCK_PART in stuck_a),
                            "stuck_b_hit": int(run["kind"] == "stuck" and STUCK_PART in stuck_b),
                            "stuck_a_false": len(stuck_a - ({STUCK_PART} if run["kind"] == "stuck" else set())),
                            "stuck_b_false": len(stuck_b - ({STUCK_PART} if run["kind"] == "stuck" else set())),
                            **{f"alt_{k}": v for k, v in alt.items()}})
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(HERE / "results" / "runs.jsonl"))
    ap.add_argument("--variant", default="current")
    ap.add_argument("--scenario", default="near")
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    runs = [json.loads(l) for l in open(a.runs)]
    runs = [r for r in runs if r["variant"] == a.variant and r["scenario"] == a.scenario]
    for r in runs:   # keep only what the job needs
        for k in ("session_samples", "first_secure", "reviews_due_by_day", "evidence_fatigue"):
            r.pop(k, None)
    with mp.get_context("fork").Pool(a.workers) as pool:
        by_db = defaultdict(list)
        for r in runs:
            by_db[r["db"]].append(r)
        rows = [x for res in pool.imap_unordered(job_db, list(by_db.values())) for x in res]
    out = Path(a.out)
    with open(out / "detector_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), restval="")
        w.writeheader()
        w.writerows(rows)

    md = [f"# Detector sweep (open-loop replay; {a.variant} settings otherwise; {a.scenario} scenario; "
          f"synthetic students, example-mini pack)\n",
          "Each recorded event log is rebuilt with the detector setting below; truth is the simulated state.",
          "Fatigue: a session (>= 30 min long) of the tired student is a positive; any other student's session is a "
          "negative. Precision is for the simulated mix (1 tired type in 7).\n",
          "| fatigue_threshold | fatigue_window | fatigue_min_parts | recall (tired sessions flagged) | onset minute (mean ± SD) | "
          "flagged before minute 30 | false-alarm rate (other students' sessions) | likelihood ratio (recall / false-alarm rate) | precision at 1 in 7 | false alarms by type |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for threshold, window, min_parts in FATIGUE_GRID:
        rs = [r for r in rows if r["threshold"] == threshold and r["window"] == window and r["min_parts"] == min_parts
              and r["minutes"] >= 30]
        pos = [r for r in rs if r["kind"] == "tired"]
        neg = [r for r in rs if r["kind"] != "tired"]
        tp = sum(r["onset"] is not None for r in pos)
        early = sum(r["onset"] is not None and r["onset"] < 30 for r in pos)
        fp = sum(r["onset"] is not None for r in neg)
        onsets = [r["onset"] for r in pos if r["onset"] is not None]
        by_type = defaultdict(lambda: [0, 0])
        for r in neg:
            by_type[r["kind"]][0] += 1
            by_type[r["kind"]][1] += r["onset"] is not None
        bt = ", ".join(f"{k} {100*v[1]/v[0]:.0f}%" for k, v in sorted(by_type.items()))
        prec = tp / (tp + fp) if tp + fp else float("nan")
        lr = (tp / len(pos)) / (fp / len(neg)) if fp else float("inf")
        md.append(f"| {threshold} | {window} | {min_parts} | {100*tp/len(pos):.0f}% ({tp}/{len(pos)}) | "
                  f"{statistics.mean(onsets) if onsets else float('nan'):.0f} ± {statistics.stdev(onsets) if len(onsets) > 1 else 0:.0f} | "
                  f"{early} | {100*fp/len(neg):.1f}% ({fp}/{len(neg)}) | {lr:.1f} | {100*prec:.0f}% | {bt} |")

    base0 = [r for r in rows if (r["threshold"], r["window"], r["min_parts"]) == FATIGUE_GRID[0] and r["minutes"] >= 30]
    md += ["\n## Alternative fatigue rules (sim-only prototypes; parameters fixed on the pilot run, tested here)\n",
           "| rule | recall | false-alarm rate | likelihood ratio | precision at 1 in 7 |", "|---|---|---|---|---|"]
    for name in ALT_RULES:
        pos = [r for r in base0 if r["kind"] == "tired"]
        neg = [r for r in base0 if r["kind"] != "tired"]
        tp = sum(r[f"alt_{name}"] is not None for r in pos)
        fp = sum(r[f"alt_{name}"] is not None for r in neg)
        rec, far = tp / len(pos), fp / len(neg)
        md.append(f"| {name} | {100*rec:.0f}% ({tp}/{len(pos)}) | {100*far:.1f}% ({fp}/{len(neg)}) | "
                  f"{rec/far if far else float('inf'):.1f} | {100*tp/max(1, tp+fp):.0f}% |")

    base = [r for r in rows if (r["threshold"], r["window"], r["min_parts"]) == FATIGUE_GRID[0]]
    md += ["\n## Stuck rule (settings.toml fatigue values)\n",
           "Rule A = the built rule (same point missed on its check and again on the re-check after its reteach; open "
           "answers: 3 attempts, mean < 0.5, no improvement). Rule B = sim-only alternative: the same point missed on "
           "three checks in a session.\n",
           "| rule | recall on the true stuck part | sessions with a false stuck flag, by type |", "|---|---|---|"]
    for rule in ("a", "b"):
        att = sum(r["stuck_true_attempted"] for r in base)
        hit = sum(r[f"stuck_{rule}_hit"] for r in base)
        by_type = defaultdict(lambda: [0, 0])
        for r in base:
            by_type[r["kind"]][0] += 1
            by_type[r["kind"]][1] += r[f"stuck_{rule}_false"] > 0
        bt = ", ".join(f"{k}{' (ambiguous)' if k == 'slow' else ''} {100*v[1]/v[0]:.0f}%" for k, v in sorted(by_type.items()))
        md.append(f"| {rule.upper()} | {100*hit/att:.0f}% ({hit}/{att}) | {bt} |")
    (out / "detector_sweep.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out / "detector_sweep.md")


if __name__ == "__main__":
    main()
