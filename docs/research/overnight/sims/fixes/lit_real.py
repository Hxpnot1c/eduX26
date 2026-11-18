"""How-AI-works ranking on the real learner code of a given copy (w4-fix-core, task 5).

grid.py/final.py use FastBackend, a replica of the ORIGINAL rules, so they can't test a patched learner. This runs
lit_model.run_student with RealBackend (the copy's own edux.learner) at reduced N, and reports week-8 AUC
(no-skill vs strong, partial vs strong, gamer vs strong) per skill, with the share of tied pairs and group means.

    PYTHONPATH=<code copy>:<sims/literacy dir> /home/vishnu/edux26/.venv/bin/python lit_real.py <code copy> <data dir> <N> <out.json>
All students are synthetic; every truth-model number is our choice (lit_model.TRUTH).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import statistics
import sys
from dataclasses import replace
from pathlib import Path


def pairs(neg, pos):
    gt = sum(1 for a in neg for b in pos if b > a)
    eq = sum(1 for a in neg for b in pos if b == a)
    n = len(neg) * len(pos)
    return {"auc": (gt + eq / 2) / n, "tied": eq / n}


def main(code: str, data: str, n: int, out: str) -> None:
    assert data.startswith("/tmp/claude-1000/")
    os.environ["EDUX_DATA_DIR"] = data
    Path(data).mkdir(parents=True, exist_ok=True)
    for f in Path(data).glob("*.db*"):
        f.unlink()
    from ingest import load
    with contextlib.redirect_stdout(io.StringIO()):
        assert load.load_pack(Path(code) / "coursepacks" / "example-mini").ok
    import lit_model as M
    cfgs = {"branch": M.BRANCH, "branch_missing": replace(M.BRANCH, ignored="missing")}
    noise = M.Noise.symmetric(0.10)
    res = {}
    for cname, cfg in cfgs.items():
        for ign in ("mcar", "mnar"):
            runs = {g: [M.run_student(M.RealBackend(cfg, f"{cname}-{ign}-{g}-{k}"), cfg, g, 1000 + 100000 * gi + k, noise, ign)
                        for k in range(n)] for gi, g in enumerate(M.GROUPS)}
            cell = {}
            for sk in ("ask", "verify", "how"):
                w8 = {g: [r["reads"][7][sk] for r in runs[g]] for g in M.GROUPS}
                cell[sk] = {
                    "none_vs_strong": pairs(w8["none"], w8["strong"]),
                    "partial_vs_strong": pairs(w8["partial"], w8["strong"]),
                    "gamer_vs_strong": pairs(w8["gamer"], w8["strong"]),
                    "mean_w8": {g: round(statistics.mean(v), 3) for g, v in w8.items()},
                    "secure_share_w8": {g: sum(x >= cfg.secure for x in v) / n for g, v in w8.items()},
                }
            res[f"{cname}|sym10|{ign}"] = cell
            h = cell["how"]
            print(f"{cname:15s} {ign}: how AUC none-strong {h['none_vs_strong']['auc']:.2f} (tied {h['none_vs_strong']['tied']:.2f}), "
                  f"partial-strong {h['partial_vs_strong']['auc']:.2f}, gamer-strong {h['gamer_vs_strong']['auc']:.2f}; "
                  f"means {h['mean_w8']}; ask AUC {cell['ask']['none_vs_strong']['auc']:.2f}, "
                  f"verify AUC {cell['verify']['none_vs_strong']['auc']:.2f}", flush=True)
    Path(out).write_text(json.dumps({"code": code, "n_per_group": n, "noise": "sym10", "cells": res}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
