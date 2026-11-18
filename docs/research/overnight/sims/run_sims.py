"""Run the synthetic-student simulation over seeds, student types, scenarios and settings variants.

    PYTHONPATH=<worktree> <venv>/bin/python docs/research/overnight/sims/run_sims.py [--seeds 30] [--workers 8]
        [--variants current,proposal,proposal_shims,tuned] [--scenarios near,far] [--out <dir>]

Writes raw per-run JSON lines to <out>/runs.jsonl (appended as runs finish), then summarise.py builds the tables.
Every database lives under /tmp/claude-1000/w1-06/sim/ (a fresh folder per worker); settings.toml is never edited.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import shutil
import sys
import time
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edux_sim as S   # noqa: E402

BASE = "/tmp/claude-1000/w1-06/sim"

# Scenarios (our choice): when the student starts relative to the exam and how often they study.
SCENARIOS = {
    # 35 days before the exam, a 45-minute session every day up to the day before
    "near": {"start_days_before": 35, "session_days": list(range(0, 35))},
    # 150 days before, a session every 3 days for 20 sessions (60 days), then nothing until the exam
    "far": {"start_days_before": 150, "session_days": list(range(0, 60, 3))},
}

# Candidate variants from the sweeps (see README / notes). "tuned" = proposal + the changes we recommend.
S.VARIANT_EXTRA.update({
    "proposal_shims": {},
    "tuned": {"session.fatigue_threshold": -0.35},
})
S.VARIANT_BASE.update({"tuned": "proposal"})
S.VARIANT_SHIMS.update({
    "proposal_shims": {"on_success_immediate": 1.0, "mcq_guess_from_options": True},
    "tuned": {"on_success_immediate": 1.5, "mcq_guess_from_options": True},
})

_state = {}


def _worker_init() -> None:
    root = f"{BASE}/{os.getpid()}"
    shutil.rmtree(root, ignore_errors=True)
    S.setup_data_dir(f"{root}/base")
    _state["root"] = root


def _use_variant_db(variant: str) -> None:
    from edux import learner
    root = _state["root"]
    Path(f"{root}/{variant}").mkdir(parents=True, exist_ok=True)
    learner.use_database(Path(f"{root}/{variant}/learner.db"), Path(f"{root}/base/content.db"))


def task(args: tuple) -> dict:
    variant, scenario, kind, seed = args
    _use_variant_db(variant)
    _, applied, skipped = S.use_settings(variant)
    sc = SCENARIOS[scenario]
    start = (S.EXAM - timedelta(days=sc["start_days_before"])).replace(hour=8, minute=0)
    run = S.Run(variant, kind, seed, start, sc["session_days"], tag=scenario)
    t0 = time.time()
    log = S.run_student(run)
    return {"variant": variant, "scenario": scenario, "kind": kind, "seed": seed, "secs": time.time() - t0,
            "student_id": run.student_id, "db": f"{_state['root']}/{variant}/learner.db",
            "content_db": f"{_state['root']}/base/content.db", "applied": applied, "skipped": skipped,
            "shims": S.VARIANT_SHIMS.get(variant, {}),
            "truth": {k: S.TRUTH_PARAMS[k] for k in ("stability0_days", "stability_growth_massed")}, **log}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--variants", default="current,proposal,proposal_shims,tuned")
    ap.add_argument("--scenarios", default="near,far")
    ap.add_argument("--types", default=",".join(S.TYPES))
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--truth", default="{}", help='JSON overrides of edux_sim.TRUTH_PARAMS, e.g. {"stability0_days": 8}')
    a = ap.parse_args()
    S.TRUTH_PARAMS.update(json.loads(a.truth))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(v, sc, k, seed) for seed in range(1, a.seeds + 1) for sc in a.scenarios.split(",")
            for k in a.types.split(",") for v in a.variants.split(",")]
    print(f"{len(jobs)} runs on {a.workers} workers", flush=True)
    t0 = time.time()
    with mp.get_context("fork").Pool(a.workers, initializer=_worker_init) as pool, \
            open(out / "runs.jsonl", "a") as f:
        for i, res in enumerate(pool.imap_unordered(task, jobs, chunksize=1), 1):
            f.write(json.dumps(res, default=str) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"{i}/{len(jobs)} done, {time.time() - t0:.0f}s", flush=True)
    print(f"all done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
