"""Summarise results/<label>/*.json from gaming_sim.py into one table per label (markdown to stdout, JSON next to it).

    /home/vishnu/edux26/.venv/bin/python summarise.py results/base [--budget 10]

Columns
  effort      mean student effort over the run (minutes; effort per action is OUR CHOICE, see gaming_sim.EFFORT)
  gain@B      displayed level points gained by B effort-minutes (new 0 / developing 1 / secure 2, summed over the 9
              course parts for C*, over Ask + Verify + How-AI-works for L*)
  gain/min    end gain / effort minutes
  secure      course: mean parts shown secure at the end; literacy: share of students with Verify | Ask | How secure
  false-sec   share of students shown secure on something they don't know (C1-C3, L1-L5: anything secure, since the
              student has no skill; C5: a secure part with under half its points truly known; C0/L0: n/a)
  +7d         the same displayed points 7 days later, no further study
  signals     skipped (ask/verify/how), source_conflict count, just_show_me share, all-4-feature share, top-letter share,
              median seconds between messages
"""

from __future__ import annotations

import gzip
import json
import statistics
import sys
from pathlib import Path

GAMERS_NOSKILL = {"C1", "C2", "C2m", "C3", "L1", "L1d", "L2", "L3", "L4", "L5"}


def at_budget(traj: list[dict], key: str, budget: float) -> float:
    best = 0.0
    for row in traj:
        if row["effort_min"] <= budget:
            best = row[key]
    return best


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def summarise(folder: Path, budget: float) -> list[dict]:
    rows = []
    for f in sorted(list(folder.glob("*-*.json")) + list(folder.glob("*-*.json.gz"))):
        res = json.loads(gzip.decompress(f.read_bytes()) if f.suffix == ".gz" else f.read_text())
        for strat, run in res["runs"].items():
            sts = run["students"]
            course = strat.startswith("C")
            key = "course_pts" if course else "lit_pts"
            gains = [s["end"][key] - s["start"][key] for s in sts]
            eff = [s["effort_min"] for s in sts]
            row = {
                "strategy": strat, "labeller": run["labeller"], "n": len(sts), "turns": run["turns"],
                "effort_min": mean(eff), "wall_min": mean([s["wall_min"] for s in sts]),
                f"gain_at_{budget:g}min": mean([at_budget(s["traj"], key, budget) - s["start"][key] for s in sts]),
                "gain_end": mean(gains), "gain_per_min": mean([g / e for g, e in zip(gains, eff) if e > 0]),
                "plus7d": mean([s["later"]["+7d"][key] - s["start"][key] for s in sts]),
                "plus1.5d": mean([s["later"]["+1.5d"][key] - s["start"][key] for s in sts]),
            }
            if course:
                row["secure_parts"] = mean([s["end"]["course_secure"] for s in sts])
                row["any_secure_share"] = mean([s["end"]["course_secure"] > 0 for s in sts])
                row["secure_parts_7d"] = mean([s["later"]["+7d"]["course_secure"] for s in sts])
                row["true_known_share"] = mean([s["true_known_share"] for s in sts])
                # secure parts whose points the student truly knows less than half of (no-skill gamers: every secure part)
                def false_parts(s):
                    tp = s.get("true_part") or {}
                    return sum(1 for p, lv in s["end"]["course"].items()
                               if lv == "secure" and (strat in GAMERS_NOSKILL or tp.get(p, 0) < 0.5))
                row["false_secure_parts"] = mean([false_parts(s) for s in sts])
                row["false_secure_part_share"] = (row["false_secure_parts"] / row["secure_parts"]) if row["secure_parts"] else None
                row["false_secure_students"] = mean([false_parts(s) > 0 for s in sts])
                # minutes of effort to the first secure part
                firsts = [next((r["effort_min"] for r in s["traj"] if r["course_secure"] > 0), None) for s in sts]
                row["min_to_first_secure"] = mean(firsts)
                row["reached_secure"] = mean([x is not None for x in firsts])
            else:
                for sk in ("ask", "verify", "how"):
                    row[f"{sk}_secure"] = mean([s["end"]["lit"][sk] == "secure" for s in sts])
                    row[f"{sk}_secure_7d"] = mean([s["later"]["+7d"]["lit"][sk] == "secure" for s in sts])
                firsts = [next((r["effort_min"] for r in s["traj"] if r["lit"]["verify"] == "secure"), None) for s in sts]
                row["min_to_verify_secure"] = mean(firsts)
                row["p_verify_end"] = mean([s["end"]["p_verify"] for s in sts])
            row["false_secure"] = (row.get("false_secure_students") if course else
                                   mean([any(v == "secure" for v in s["end"]["lit"].values()) for s in sts])) \
                if strat in GAMERS_NOSKILL or strat == "C5" else None
            sig = [s["signals"] for s in sts]
            row["sig"] = {
                "skipped_ask": mean([x["skipped"]["ask"] for x in sig]), "skipped_verify": mean([x["skipped"]["verify"] for x in sig]),
                "skipped_how": mean([x["skipped"]["how_ai_works"] for x in sig]), "held_how": mean([x["held_how"] for x in sig]),
                "source_conflicts": mean([x["source_conflicts"] for x in sig]), "verify_evidence": mean([x["verify_evidence"] for x in sig]),
                "just_show_me": mean([x["trend_just_show_me"] for x in sig]), "all4": mean([x["all4_feature_share"] for x in sig]),
                "top_letter": mean([x["top_letter_share"] for x in sig]), "median_gap_s": mean([x["median_gap_s"] for x in sig]),
                "mcq_right": mean([x["mcq_right_share"] for x in sig]),
                "dodged": mean([s["counts"].get("dodged", 0) for s in sts]),
            }
            rows.append(row)
    return rows


def fmt(x, d=2):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def main() -> None:
    folder = Path(sys.argv[1])
    budget = float(sys.argv[sys.argv.index("--budget") + 1]) if "--budget" in sys.argv else 10.0
    rows = summarise(folder, budget)
    (folder / "summary.json").write_text(json.dumps(rows, indent=1))
    print(f"## {folder.name}\n")
    print(f"| strategy | lab | effort min | gain@{budget:g}min | gain end | gain/min | +7d | secure | false-sec | min to secure | skipped a/v/h | src_conflict | jsm | all4 | top letter | mcq right | med gap s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        s = r["sig"]
        if r["strategy"].startswith("C"):
            secure = f"{fmt(r['secure_parts'],1)} parts ({fmt(r['secure_parts_7d'],1)} at +7d; {fmt(r['false_secure_parts'],1)} false)"
            mts = fmt(r["min_to_first_secure"], 1)
        else:
            secure = f"A {fmt(r['ask_secure'])} V {fmt(r['verify_secure'])} H {fmt(r['how_secure'])}"
            mts = fmt(r["min_to_verify_secure"], 1) + " (V)"
        print(f"| {r['strategy']} | {r['labeller'][:4]} | {fmt(r['effort_min'],1)} | {fmt(r[f'gain_at_{budget:g}min'],1)} | "
              f"{fmt(r['gain_end'],1)} | {fmt(r['gain_per_min'])} | {fmt(r['plus7d'],1)} | {secure} | {fmt(r['false_secure'])} | {mts} | "
              f"{fmt(s['skipped_ask'],1)}/{fmt(s['skipped_verify'],1)}/{fmt(s['skipped_how'],1)} | {fmt(s['source_conflicts'],1)} | "
              f"{fmt(s['just_show_me'])} | {fmt(s['all4'])} | {fmt(s['top_letter'])} | {fmt(s['mcq_right'])} | {fmt(s['median_gap_s'],0)} |")


if __name__ == "__main__":
    main()
