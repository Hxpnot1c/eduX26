"""Answers to secure with multiple-choice checks against open (one-point) checks (decision 0028).

    python scripts/simulate_open_checks.py [--runs 20]

SYNTHETIC STUDENTS on the example pack, in a throwaway data folder (never ./data). Each answers up to 12 point checks
per part (the parts with at least 3 points), right with a fixed probability, three minutes apart, and we count the
answers until the real learner model calls the part secure. Patterns: every check multiple choice (4 options); one
multiple-choice check then two open ones (the question-mix rule); every check open. "Delayed" answers come with no
teaching just before; "after teaching" answers each follow a worked example, so they count as immediate evidence.
These test the model's arithmetic, not real learning.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PATTERNS = {"all MCQ": ["mcq"], "MCQ, open, open": ["mcq", "open", "open"], "all open": ["open"]}
T0 = datetime(2026, 1, 5, 9, tzinfo=timezone.utc)


def run(learner, graph, course: str, parts: list[str], pattern: list[str], p_right: float, seed: int, taught: bool) -> list[int | None]:
    sid = learner.add_student("sim", course)["id"]
    rng, out = random.Random(seed), []
    for part in parts:
        points = graph.score_points(part)
        for i in range(12):
            ts = T0 + timedelta(minutes=3 * i)
            if taught:
                learner.record_exchange(
                    sid,
                    [part],
                    "mechanism",
                    "active",
                    False,
                    "worked_example",
                    "try_first",
                    None,
                    ts=(ts - timedelta(minutes=1)).isoformat(),
                    apply="now",
                )
            right, point = float(rng.random() < p_right), points[i % len(points)]["id"]
            if pattern[i % len(pattern)] == "mcq":
                learner.record_evidence(sid, part, "mcq_check", right, ts=ts.isoformat(), apply="now", point_id=point, n_options=4)
            else:
                learner.record_evidence(sid, part, "explain_back", right, ts=ts.isoformat(), apply="now", point_id=point)
            p = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id = ? AND part_id = ?", (sid, part)).fetchone()[0]
            if p >= learner._settings().levels.secure:
                out.append(i + 1)
                break
        else:
            out.append(None)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()
    os.environ["EDUX_DATA_DIR"] = tempfile.mkdtemp(prefix="sim-open-")
    from edux import db, graph, learner
    from ingest import load

    report = load.load_pack(Path(__file__).resolve().parent.parent / "coursepacks" / "example-mini", db_path=db.content_db_path())
    learner.use_database(db.learner_db_path(), db.content_db_path())
    parts = [p for p in learner.all_parts() if len(graph.score_points(p)) >= 3]
    print("| answers | right | " + " | ".join(PATTERNS) + " |")
    print("|---|---|" + "---|" * len(PATTERNS))
    for taught in (False, True):
        for p_right in (1.0, 0.85, 0.7):
            cells = []
            for pattern in PATTERNS.values():
                got = [x for seed in range(args.runs) for x in run(learner, graph, report.course_id, parts, pattern, p_right, seed, taught)]
                hit = [x for x in got if x]
                cells.append(f"{sum(hit) / len(hit):.2f} ({len(hit)}/{len(got)})" if hit else f"never (0/{len(got)})")
            print(f"| {'after teaching' if taught else 'delayed'} | {p_right:.0%} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
