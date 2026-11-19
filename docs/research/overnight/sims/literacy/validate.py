"""Check that FastBackend (the replica used for the grid) matches the 05e branch's own edux.learner (RealBackend)
on the same synthetic students: every weekly read, first-secure time and moment count.

Run (one process per call; it makes its own EDUX_DATA_DIR under /tmp/claude-1000/w2-02/):
  PYTHONPATH=/tmp/claude-1000/edux-05e:<this folder> python validate.py [n_students]
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path("/tmp/claude-1000/w2-02/base")   # content.db loaded from coursepacks/example-mini (05e export)


def fresh_data_dir() -> Path:
    root = Path("/tmp/claude-1000/w2-02/runs")
    root.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(dir=root))
    shutil.copy(BASE / "content.db", d / "content.db")
    os.environ["EDUX_DATA_DIR"] = str(d)
    return d


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    fresh_data_dir()
    import lit_model as M
    cfgs = {
        "branch": M.BRANCH,
        "branch_missing": replace(M.BRANCH, ignored="missing"),
        "alt": replace(M.BRANCH, prior=0.2, learn_rate=0.02, correct_share=0.5, half_life=14.0, q_guess=0.3,
                       t_guess=0.3, u_guess=0.3, ignored="missing"),
        "alt_verify_share": replace(M.BRANCH, prior=0.2, learn_rate=0.05, correct_share=0.5, verify_share=0.67,
                                    half_life=30.0, ignored="missing"),
    }
    chosen = json.loads((HERE / "results" / "chosen.json").read_text())
    cfgs["proposal"] = replace(M.BRANCH, **chosen)
    noises = {"0": M.Noise(), "20sym": M.Noise.symmetric(0.2)}
    worst, compared, rows = 0.0, 0, []
    for cname, cfg in cfgs.items():
        for nname, noise in noises.items():
            for g in M.GROUPS:
                for k in range(n):
                    seed = 1000 + k
                    fast = M.run_student(M.FastBackend(cfg), cfg, g, seed, noise, "mnar")
                    real = M.run_student(M.RealBackend(cfg, f"{cname}-{nname}-{g}-{k}"), cfg, g, seed, noise, "mnar")
                    for rf, rr in zip(fast["reads"], real["reads"]):
                        for key in rf:
                            worst = max(worst, abs(rf[key] - rr[key]))
                            compared += 1
                    same = (fast["moments"] == real["moments"] and fast["ignored"] == real["ignored"]
                            and fast["first_secure"] == real["first_secure"])
                    if not same:
                        rows.append({"cfg": cname, "noise": nname, "group": g, "seed": seed,
                                     "fast": fast["first_secure"], "real": real["first_secure"]})
    res = {"students_per_cell": n, "values_compared": compared, "max_abs_diff": worst, "mismatched_students": len(rows),
           "mismatches": rows[:10]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "validate.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
