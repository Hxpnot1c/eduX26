"""Turn results/runs.jsonl into per-run metrics (metrics.csv) and summary tables (summary.md), plus an SVG chart.

    python docs/research/overnight/sims/summarise.py [--runs results/runs.jsonl] [--out results]

Definitions (thresholds are OUR CHOICE, listed in edux_sim.TRUTH_PARAMS):
- first_secure_false: share of parts whose FIRST model-secure moment came while true mastery < 0.5.
- secure_fdr_<tag>: of the part-samples the model calls secure (p_now >= levels.secure) at that sample time,
  the share whose true mastery < 0.5 (false-discovery rate of "secure"). tag = next_morning (pooled over the run)
  or exam_day.
- overconf_<tag>: mean (model p_now - true mastery) over all parts at that sample time.
- ev_to_secure: pieces of evidence on a part when it first became model-secure (parts with true mastery >= 0.5 then).
- due_last14_mean / _max: reviews due per morning (uncapped) over the 14 days before the exam (near scenario).
- fatigue: per session. A tired student's session (45 min) is a positive from minute 30; others are negatives.
- stuck: per session. True stuck = the stuck student's session that attempted ped_formula. Any other flagged
  part is a false alarm (the slow learner's flags are reported, but labelled ambiguous).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUCK_PART = "ped_formula"
FALSE_BELOW = 0.5


def per_run(r: dict) -> dict:
    out = {k: r[k] for k in ("variant", "scenario", "kind", "seed")}
    fs = r["first_secure"]
    out["n_first_secure"] = len(fs)
    out["first_secure_false"] = (sum(f["true_mastery"] < FALSE_BELOW for f in fs) / len(fs)) if fs else math.nan
    out["true_mastery_at_secure"] = statistics.mean(f["true_mastery"] for f in fs) if fs else math.nan
    good = [f for f in fs if f["true_mastery"] >= FALSE_BELOW]
    out["ev_to_secure"] = statistics.mean(f["n_evidence"] for f in good) if good else math.nan
    for tag in ("next_morning", "exam_day", "session_end"):
        rows = [row for s in r["session_samples"] if s["tag"] == tag for row in s["rows"]]
        sec = [row for row in rows if row["p"] >= 0.75]
        out[f"secure_fdr_{tag}"] = (sum(row["m"] < FALSE_BELOW for row in sec) / len(sec)) if sec else math.nan
        out[f"overconf_{tag}"] = statistics.mean(row["p"] - row["m"] for row in rows) if rows else math.nan
        out[f"n_secure_{tag}"] = len(sec) / max(1, len({s["day"] for s in r["session_samples"] if s["tag"] == tag}))
    last = [s for s in r["session_samples"] if s["tag"] == "session_end"][-1]["rows"]
    out["parts_model_secure_end"] = sum(row["p"] >= 0.75 for row in last)
    out["parts_true_secure_end"] = sum(row["m"] >= 0.75 for row in last)
    out["parts_false_secure_end"] = sum(row["p"] >= 0.75 and row["m"] < FALSE_BELOW for row in last)
    days = [d for d in r["reviews_due_by_day"] if d["days_to_exam"] <= 14.1]
    out["due_last14_mean"] = statistics.mean(d["due"] for d in days) if days else math.nan
    out["due_last14_max"] = max(d["due"] for d in days) if days else math.nan
    out["due_all_mean"] = statistics.mean(d["due"] for d in r["reviews_due_by_day"])
    sessions = r["sessions"]
    out["n_sessions"] = len(sessions)
    out["fatigue_flag_share"] = sum(s["fatigued"] for s in sessions) / len(sessions)
    onsets = [s["onset"] for s in sessions if s["fatigued"]]
    out["fatigue_onset_mean"] = statistics.mean(onsets) if onsets else math.nan
    out["fatigue_early_share"] = (sum(o < 30 for o in onsets) / len(sessions)) if sessions else math.nan
    out["stuck_true_sessions"] = sum(STUCK_PART in s["attempted"] for s in sessions) if r["kind"] == "stuck" else 0
    out["stuck_true_hits"] = sum(STUCK_PART in s["attempted"] and STUCK_PART in s["stuck"] for s in sessions) \
        if r["kind"] == "stuck" else 0
    out["stuck_false_flags"] = sum(len([p for p in s["stuck"] if not (r["kind"] == "stuck" and p == STUCK_PART)])
                                   for s in sessions)
    out["stuck_false_session_share"] = sum(
        bool([p for p in s["stuck"] if not (r["kind"] == "stuck" and p == STUCK_PART)]) for s in sessions) / len(sessions)
    out["stepback_max_streak"] = max((s.get("stepback_max_streak", 0) for s in sessions), default=0)
    out["stepback_plans_per_session"] = statistics.mean(s.get("stepback_plans", 0) for s in sessions)
    out["evidence"] = r["evidence"]
    out["immediate_share"] = r["immediate_evidence"] / r["evidence"] if r["evidence"] else math.nan
    out["turns"] = r["turns"]
    g = r.get("guess_by_options") or {}
    for n in ("3", "4"):
        a, b = g.get(n, [0, 0])
        out[f"guesser_hit_{n}opt"] = b / a if a else math.nan
    out["clamps"] = r.get("clamps", 0)
    return out


def ms(values: list[float]) -> tuple[float, float, int]:
    v = [x for x in values if not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return math.nan, math.nan, 0
    return statistics.mean(v), (statistics.stdev(v) if len(v) > 1 else 0.0), len(v)


def fmt(values: list[float], pct: bool = False, digits: int = 2) -> str:
    m, sd, n = ms(values)
    if n == 0:
        return "–"
    if pct:
        return f"{100 * m:.0f}% ± {100 * sd:.0f}"
    return f"{m:.{digits}f} ± {sd:.{digits}f}"


def paired(rows: list[dict], metric: str, a: str, b: str, scenario: str, kinds: list[str] | None = None):
    """Mean paired difference b - a over (kind, seed) with a normal-approx 95% CI."""
    by = defaultdict(dict)
    for r in rows:
        if r["scenario"] == scenario and (kinds is None or r["kind"] in kinds):
            by[(r["kind"], r["seed"])][r["variant"]] = r[metric]
    d = [v[b] - v[a] for v in by.values() if a in v and b in v
         and not math.isnan(v[a]) and not math.isnan(v[b])]
    if len(d) < 2:
        return math.nan, math.nan, len(d)
    m, sd = statistics.mean(d), statistics.stdev(d)
    return m, 1.96 * sd / math.sqrt(len(d)), len(d)


def svg_bars(groups: list[tuple[str, list[tuple[str, float, float]]]], title: str, path: Path, unit: str = "%") -> None:
    """A small grouped bar chart (mean with ±SD whisker) as standalone SVG."""
    colors = {"current": "#9aa0a6", "proposal": "#4c78a8", "proposal_shims": "#2a5d8f", "tuned": "#e45756"}
    W, H, left, top, bottom = 760, 360, 60, 40, 70
    vmax = max((m + s) for _, bars in groups for _, m, s in bars) * 1.15 or 1
    gw = (W - left - 20) / len(groups)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{W/2}" y="20" text-anchor="middle" font-size="14" font-weight="bold">{title}</text>']
    for i in range(5):
        v = vmax * i / 4
        y = H - bottom - (H - top - bottom) * i / 4
        out.append(f'<line x1="{left}" x2="{W-20}" y1="{y}" y2="{y}" stroke="#eee"/>')
        out.append(f'<text x="{left-6}" y="{y+4}" text-anchor="end">{v:.0f}{unit}</text>')
    for gi, (label, bars) in enumerate(groups):
        bw = gw * 0.8 / len(bars)
        for bi, (variant, m, s) in enumerate(bars):
            x = left + gi * gw + gw * 0.1 + bi * bw
            h = (H - top - bottom) * m / vmax
            y = H - bottom - h
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-2:.1f}" height="{h:.1f}" fill="{colors.get(variant, "#999")}"/>')
            hi = H - bottom - (H - top - bottom) * min(vmax, m + s) / vmax
            lo = H - bottom - (H - top - bottom) * max(0, m - s) / vmax
            cx = x + (bw - 2) / 2
            out.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{hi:.1f}" y2="{lo:.1f}" stroke="#333"/>')
        out.append(f'<text x="{left + gi*gw + gw/2:.1f}" y="{H-bottom+16}" text-anchor="middle">{label}</text>')
    lx = left
    for variant in [v for v, _, _ in groups[0][1]]:
        out.append(f'<rect x="{lx}" y="{H-30}" width="12" height="12" fill="{colors.get(variant, "#999")}"/>'
                   f'<text x="{lx+16}" y="{H-20}">{variant}</text>')
        lx += 140
    out.append(f'<text x="{W-20}" y="{H-8}" text-anchor="end" fill="#666" font-size="10">'
               f'synthetic students, example-mini pack; whiskers = SD over seeds</text></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(HERE / "results" / "runs.jsonl"))
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    out = Path(a.out)
    runs = [json.loads(line) for line in open(a.runs)]
    rows = [per_run(r) for r in runs]
    keys = list(rows[0])
    with open(out / "metrics.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    variants = list(dict.fromkeys(r["variant"] for r in rows))
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    kinds = list(dict.fromkeys(r["kind"] for r in rows))
    seeds = len({r["seed"] for r in rows})
    md = [f"# Simulation summary (synthetic students, example-mini pack only)\n",
          f"{len(rows)} runs; {seeds} seeds per cell; mean ± SD over seeds. Generated by summarise.py from runs.jsonl.\n",
          "Applied settings per variant:\n"]
    for v in variants:
        r0 = next(r for r in runs if r["variant"] == v)
        shims = r0.get("shims") or {}
        md.append(f"- **{v}**: {'; '.join(r0['applied']) or 'settings.toml as is'}"
                  + (f"; shims (emulated, not built): {shims}" if shims else ""))
    r0 = next((r for r in runs if r["variant"].startswith("proposal")), None)
    if r0:
        md.append(f"\nProposal keys the code does not read (not applied unless a shim says so): {', '.join(r0['skipped'])}\n")

    def table(metric: str, label: str, pct: bool = False, scen: list[str] | None = None, only: list[str] | None = None):
        md.append(f"\n## {label}\n")
        md.append("| scenario | type | " + " | ".join(variants) + " |")
        md.append("|---|---|" + "---|" * len(variants))
        for sc in scen or scenarios:
            for k in only or kinds:
                cells = [fmt([r[metric] for r in rows if r["variant"] == v and r["scenario"] == sc and r["kind"] == k], pct)
                         for v in variants]
                md.append(f"| {sc} | {k} | " + " | ".join(cells) + " |")
            cells = [fmt([r[metric] for r in rows if r["variant"] == v and r["scenario"] == sc], pct) for v in variants]
            md.append(f"| {sc} | **all** | " + " | ".join(cells) + " |")

    table("first_secure_false", "False secure at the moment a part first turns secure (share of parts, true mastery < 0.5)", True)
    table("secure_fdr_next_morning", "False-discovery rate of 'secure' the morning after each session", True)
    table("secure_fdr_exam_day", "False-discovery rate of 'secure' on exam day", True)
    table("overconf_exam_day", "Overconfidence on exam day: mean (model p_now - true mastery) over parts")
    table("ev_to_secure", "Evidence pieces on a part when it first turns secure (truly learnt parts)")
    table("parts_model_secure_end", "Parts (of 9) model-secure at the end of the last session")
    table("parts_true_secure_end", "Parts (of 9) truly secure (mastery >= 0.75) at the end of the last session")
    table("due_last14_mean", "Reviews due per morning, last 14 days before the exam (uncapped)", scen=["near"])
    table("due_last14_max", "Max reviews due on one morning, last 14 days", scen=["near"])
    table("fatigue_flag_share", "Sessions flagged fatigued (tired type: recall; others: false-alarm rate)", True)
    table("fatigue_onset_mean", "Fatigue onset minute when flagged (tired student truly tires at 30)")
    table("stuck_false_session_share", "Sessions with a stuck flag on a part that is not the true stuck part", True)
    table("stepback_max_streak", "Longest run of consecutive 'step back' plans (stuck -> prerequisite check) in one session")
    table("immediate_share", "Share of evidence scored as 'immediate' (within 30 min of a worked example/hint)", True)
    table("guesser_hit_3opt", "Guesser's hit rate on 3-option MCQs (model assumes guess 0.25)", True, only=["guesser"])
    table("guesser_hit_4opt", "Guesser's hit rate on 4-option MCQs", True, only=["guesser"])
    table("clamps", "p_known saturations at 1.0 (would crash the next exchange without the sim clamp)")

    # stuck recall
    md.append("\n## Stuck detection on the true stuck part (stuck type)\n")
    md.append("| scenario | variant | sessions on ped_formula | flagged | recall |")
    md.append("|---|---|---|---|---|")
    for sc in scenarios:
        for v in variants:
            rs = [r for r in rows if r["variant"] == v and r["scenario"] == sc and r["kind"] == "stuck"]
            t, h = sum(r["stuck_true_sessions"] for r in rs), sum(r["stuck_true_hits"] for r in rs)
            md.append(f"| {sc} | {v} | {t} | {h} | {100*h/t:.0f}% |" if t else f"| {sc} | {v} | 0 | 0 | – |")

    md.append("\n## Paired differences vs current (same student type and seed), mean with 95% CI\n")
    md.append("| metric | scenario | variant | difference | n pairs |")
    md.append("|---|---|---|---|---|")
    for metric in ("first_secure_false", "secure_fdr_next_morning", "secure_fdr_exam_day", "overconf_exam_day",
                   "ev_to_secure", "parts_true_secure_end", "due_last14_mean", "fatigue_flag_share"):
        for sc in scenarios:
            for v in variants:
                if v == "current":
                    continue
                m, ci, n = paired(rows, metric, "current", v, sc)
                if n:
                    md.append(f"| {metric} | {sc} | {v} | {m:+.3f} ± {ci:.3f} | {n} |")
    (out / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # demo chart: false-discovery of "secure" on exam day, near and far, by variant
    groups = []
    for sc in scenarios:
        bars = []
        for v in variants:
            m, sd, _ = ms([r["secure_fdr_exam_day"] for r in rows if r["variant"] == v and r["scenario"] == sc])
            bars.append((v, 100 * m, 100 * sd))
        groups.append((f"{sc} start: exam day", bars))
        bars = []
        for v in variants:
            m, sd, _ = ms([r["first_secure_false"] for r in rows if r["variant"] == v and r["scenario"] == sc])
            bars.append((v, 100 * m, 100 * sd))
        groups.append((f"{sc} start: first secure", bars))
    svg_bars(groups, "'Secure' parts the student doesn't actually know", out / "false_secure.svg")
    groups = [("reviews due / morning, last 14 days", [
        (v, *ms([r["due_last14_mean"] for r in rows if r["variant"] == v and r["scenario"] == "near"])[:2])
        for v in variants])]
    if "near" in scenarios:
        svg_bars(groups, "Review load before the exam (near start)", out / "review_load.svg", unit="")
    print(out / "summary.md")


if __name__ == "__main__":
    main()
