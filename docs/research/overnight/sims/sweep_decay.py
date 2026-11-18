"""Open-loop replay of recorded event logs under different scoring/decay rules; scored on exam day against the
simulated truth (the same answers, re-scored; plan feedback is ignored).

    PYTHONPATH=<worktree> <venv>/bin/python docs/research/overnight/sims/sweep_decay.py \
        [--runs results/runs.jsonl] [--variant current] [--out results]

For each rule set: of the parts the model calls secure on exam day, the share the student truly doesn't know
(true mastery < 0.5: false-discovery rate); of the parts truly secure (mastery >= 0.75), the share the model
calls secure (coverage); mean (p_now - true mastery). Writes decay_sweep.csv and decay_sweep.md.
Synthetic students, example-mini pack only.
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

# rule sets (name -> (base variant, extra settings, shims)); all OUR CHOICE except "proposal" (the review's values)
RULES = {
    "current": ("current", {}, {}),
    "proposal": ("proposal", {}, {}),
    "proposal+mcq_guess": ("proposal", {}, {"mcq_guess_from_options": True}),
    "proposal+immediate_x1.0": ("proposal", {}, {"on_success_immediate": 1.0}),
    "proposal+immediate_x1.5": ("proposal", {}, {"on_success_immediate": 1.5}),
    "proposal+on_success_1.5": ("proposal", {"decay.on_success": 1.5}, {}),
    "proposal+scaled": ("proposal", {}, {"on_success_scaled": True}),
    "proposal+scaled+mcq_guess": ("proposal", {}, {"on_success_scaled": True, "mcq_guess_from_options": True}),
    "proposal+immediate_x1.0+mcq_guess": ("proposal", {}, {"on_success_immediate": 1.0, "mcq_guess_from_options": True}),
    "proposal+window10": ("proposal", {"evidence.immediate_window_minutes": 10}, {}),
    "proposal+window5": ("proposal", {"evidence.immediate_window_minutes": 5}, {}),
    "proposal+window5+mcq_guess": ("proposal", {"evidence.immediate_window_minutes": 5}, {"mcq_guess_from_options": True}),
    "proposal+window10+immediate_x1.5": ("proposal", {"evidence.immediate_window_minutes": 10}, {"on_success_immediate": 1.5}),
}


def register() -> None:
    for name, (base, extra, shims) in RULES.items():
        if name in ("current", "proposal"):
            continue
        S.VARIANT_EXTRA[name] = extra
        S.VARIANT_SHIMS[name] = shims
        S.VARIANT_BASE[name] = base


def job_db(runs: list[dict]) -> list[dict]:
    from edux import learner
    register()
    out = []
    for run in runs:
        learner.use_database(Path(run["db"]), Path(run["content_db"]))
        sid = run["student_id"]
        for name in RULES:
            S.use_settings(name)
            learner.rebuild_state(sid)
            at = S.iso(S.EXAM)
            for part, m in run["final_true"].items():
                row = learner._conn().execute("SELECT last_correct, n_evidence FROM part_state WHERE student_id = ? "
                                              "AND part_id = ?", (sid, part)).fetchone()
                stale = ((S.EXAM - learner.parse_ts(row["last_correct"])).total_seconds() / 86400
                         if row and row["last_correct"] else None)
                out.append({"rule": name, "scenario": run["scenario"], "kind": run["kind"], "seed": run["seed"],
                            "part": part, "p": learner.part_p(sid, part, at), "m": m, "days_since_correct": stale})
        S.use_settings("current")
        learner.rebuild_state(sid)   # leave the database as it was
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(HERE / "results" / "runs.jsonl"))
    ap.add_argument("--variant", default="current")
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    runs = [json.loads(l) for l in open(a.runs)]
    runs = [{k: r[k] for k in ("db", "content_db", "student_id", "scenario", "kind", "seed", "final_true")}
            for r in runs if r["variant"] == a.variant]
    by_db = defaultdict(list)
    for r in runs:
        by_db[r["db"]].append(r)
    with mp.get_context("fork").Pool(a.workers) as pool:
        rows = [x for res in pool.imap_unordered(job_db, list(by_db.values())) for x in res]
    out = Path(a.out)
    with open(out / "decay_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    md = [f"# Scoring/decay rules replayed on the same answers ({a.variant} closed-loop logs), scored on exam day\n",
          "Synthetic students (all 7 types; guesser included), example-mini pack. FDR = model-secure parts the student "
          "truly doesn't know (mastery < 0.5) / model-secure parts. Coverage = truly secure parts (>= 0.75) the model "
          "calls secure. Spread = SD over students of each student's FDR. Rules marked shim are emulated in the sim, "
          "not built.\n",
          "| rule | scenario | FDR of 'secure' | FDR SD over students | coverage | mean p_now - truth |", "|---|---|---|---|---|---|"]
    for name in RULES:
        for sc in sorted({r["scenario"] for r in rows}):
            rs = [r for r in rows if r["rule"] == name and r["scenario"] == sc]
            sec = [r for r in rs if r["p"] >= 0.75]
            tru = [r for r in rs if r["m"] >= 0.75]
            per = defaultdict(list)
            for r in sec:
                per[(r["kind"], r["seed"])].append(r["m"] < 0.5)
            fdrs = [sum(v) / len(v) for v in per.values()]
            md.append(f"| {name} | {sc} | {100*sum(r['m'] < 0.5 for r in sec)/max(1, len(sec)):.0f}% ({len(sec)} secure) | "
                      f"{100*statistics.stdev(fdrs) if len(fdrs) > 1 else 0:.0f} | "
                      f"{100*sum(r['p'] >= 0.75 for r in tru)/max(1, len(tru)):.0f}% | "
                      f"{statistics.mean(r['p'] - r['m'] for r in rs):+.2f} |")
    md += ["\n## Staleness: exam-day 'secure' by days since the last correct answer (rule: current)\n",
           "| scenario | days since last correct | model-secure parts | of which truly not known (< 0.5) |",
           "|---|---|---|---|"]
    for sc in sorted({r["scenario"] for r in rows}):
        for lo, hi in ((0, 14), (14, 45), (45, 90), (90, 10_000)):
            rs = [r for r in rows if r["rule"] == "current" and r["scenario"] == sc and r["p"] >= 0.75
                  and r["days_since_correct"] is not None and lo <= r["days_since_correct"] < hi]
            if rs:
                md.append(f"| {sc} | {lo}-{hi if hi < 10_000 else ''} | {len(rs)} | "
                          f"{100*sum(r['m'] < 0.5 for r in rs)/len(rs):.0f}% |")
    (out / "decay_sweep.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out / "decay_sweep.md")


if __name__ == "__main__":
    main()
