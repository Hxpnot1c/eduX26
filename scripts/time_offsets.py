"""Time the per-session learner offsets on a long synthetic history (step 05r).

    EDUX_PERSONALISATION=1 python scripts/time_offsets.py [--sessions 200] [--answers 10]

Builds a throwaway database with one synthetic student (SESSIONS sessions of ANSWERS answers each, spread over the
course's parts, a day apart) and times: applying one more answer (what happens live, every turn), asking for the
current learning-rate offset and starting offsets, and a full rebuild. These are synthetic students on the example
pack: they time the code, they say nothing about learning. Run it before and after a change to compare.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sessions", type=int, default=200)
    parser.add_argument("--answers", type=int, default=10)
    args = parser.parse_args()
    os.environ.setdefault("EDUX_PERSONALISATION", "1")
    with tempfile.TemporaryDirectory() as folder:
        os.environ["EDUX_DATA_DIR"] = folder
        from edux import db, graph, learner
        from ingest import load

        pack = Path(__file__).resolve().parent.parent / "coursepacks" / "example-mini"
        report = load.load_pack(pack, db_path=db.content_db_path())
        learner.use_database(db.learner_db_path(), db.content_db_path())
        student = learner.add_student("Synthetic", report.course_id)["id"]
        parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
        rng = random.Random(7)
        start = datetime.now(timezone.utc) - timedelta(days=args.sessions + 2)
        for s in range(args.sessions):
            for a in range(args.answers):
                ts = (start + timedelta(days=s, minutes=3 * a)).isoformat(timespec="seconds")
                learner.record_evidence(student, rng.choice(parts), "mcq_check", float(rng.random() < 0.6), ts=ts, apply="now", n_options=4)
        n = args.sessions * args.answers

        def timed(label: str, fn, repeat: int = 5) -> None:
            t0 = time.perf_counter()
            for _ in range(repeat):
                fn()
            print(f"{label:46} {(time.perf_counter() - t0) / repeat * 1000:9.1f} ms")

        print(f"{args.sessions} sessions x {args.answers} answers = {n} pieces of evidence")
        timed("learning_offset (current session)", lambda: learner.learning_offset(student))
        timed("starting_offsets (current session)", lambda: learner.starting_offsets(student))
        counter = [0]

        def one_more() -> None:
            counter[0] += 1
            ts = (datetime.now(timezone.utc) + timedelta(seconds=counter[0])).isoformat(timespec="seconds")
            learner.record_evidence(student, rng.choice(parts), "mcq_check", 1.0, ts=ts, apply="now", n_options=4)

        timed("apply one more answer (live, per turn)", one_more)
        timed("rebuild_state (the whole history)", lambda: learner.rebuild_state(student), repeat=1)


if __name__ == "__main__":
    main()
