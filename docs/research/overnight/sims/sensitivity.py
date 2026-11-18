"""Truth-model sensitivity: does the current-vs-proposal gap in exam-day false 'secure' survive other assumptions
about real memory? Runs run_sims.py for each (stability0_days, stability_growth_massed) pair (OUR CHOICE grid),
far scenario, current vs proposal, then tabulates.

    PYTHONPATH=<worktree> <venv>/bin/python docs/research/overnight/sims/sensitivity.py [--seeds 6] [--run]
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from summarise import paired, per_run   # noqa: E402

GRID = [(s0, g) for s0 in (2.0, 4.0, 8.0) for g in (1.1, 1.5, 2.0)]
TYPES = "typical,slow,fast,offloader,tired"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--run", action="store_true", help="run the simulations (else only tabulate)")
    a = ap.parse_args()
    root = HERE / "results" / "sensitivity"
    for s0, g in GRID:
        out = root / f"s0_{s0}_massed_{g}"
        if a.run:
            out.mkdir(parents=True, exist_ok=True)
            (out / "runs.jsonl").unlink(missing_ok=True)
            subprocess.run([sys.executable, str(HERE / "run_sims.py"), "--seeds", str(a.seeds), "--scenarios", "far",
                            "--variants", "current,proposal", "--types", TYPES, "--out", str(out),
                            "--truth", json.dumps({"stability0_days": s0, "stability_growth_massed": g})], check=True)
    md = ["# Truth-model sensitivity (far scenario; synthetic students, example-mini pack)\n",
          "stability0_days = memory stability of a newly learnt point; stability_growth_massed = how much a correct "
          "answer within 12 h of the last strengthens real memory (eduX's model always doubles its half-life). "
          f"Types: {TYPES}. Both are OUR CHOICE grids.\n",
          "| stability0_days | massed growth | exam-day FDR current | exam-day FDR proposal | paired diff (95% CI) | "
          "overconfidence current | overconfidence proposal | coverage current |", "|---|---|---|---|---|---|---|---|"]
    for s0, g in GRID:
        f = root / f"s0_{s0}_massed_{g}" / "runs.jsonl"
        if not f.exists():
            continue
        runs = [json.loads(l) for l in open(f)]
        rows = [per_run(r) for r in runs]

        def m(metric, v):
            vals = [r[metric] for r in rows if r["variant"] == v and not math.isnan(r[metric])]
            return statistics.mean(vals) if vals else math.nan

        cov = []
        for r in runs:
            if r["variant"] != "current":
                continue
            ex = [s for s in r["session_samples"] if s["tag"] == "exam_day"][0]["rows"]
            cov += [x["p"] >= 0.75 for x in ex if x["m"] >= 0.75]
        d, ci, n = paired(rows, "secure_fdr_exam_day", "current", "proposal", "far")
        md.append(f"| {s0} | {g} | {100*m('secure_fdr_exam_day', 'current'):.0f}% | "
                  f"{100*m('secure_fdr_exam_day', 'proposal'):.0f}% | {100*d:+.0f} ± {100*ci:.0f} pts (n={n}) | "
                  f"{m('overconf_exam_day', 'current'):+.2f} | {m('overconf_exam_day', 'proposal'):+.2f} | "
                  f"{100*sum(cov)/max(1, len(cov)):.0f}% |")
    (root / "sensitivity.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(root / "sensitivity.md")


if __name__ == "__main__":
    main()
