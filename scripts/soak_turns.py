"""Soak test: many random tutor_turn calls straight into the service (no server), with find-the-error and the
confidence question switched on. Checks: no exception, every result within results.max_chars, the saved plan always
replays, and rebuilding the derived state from the event logs gives the same state. A random walk, seeded, so a failure
can be reproduced. The clock advances 4 seconds to 90 minutes a turn, as in real chat (two turns inside one second
are not realistic and replay in a different order).

    python scripts/soak_turns.py [--turns 400] [--seed 1]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    data = tempfile.mkdtemp(prefix="soak-")
    os.environ.update(EDUX_DATA_DIR=data, EDUX_FIND_ERROR="1", EDUX_CONFIDENCE="1")
    from edux import db, graph, learner, service
    from ingest import load

    report = load.load_pack(ROOT / "coursepacks" / "example-mini", db_path=db.content_db_path())
    learner.use_database(db.learner_db_path(), db.content_db_path())
    cap = learner._settings().results.max_chars
    from datetime import datetime, timedelta, timezone

    clock = [datetime.now(timezone.utc) - timedelta(days=1)]  # a chat clock: each turn is seconds to minutes after the last
    learner.now_iso = lambda: clock[0].isoformat(timespec="seconds")
    rng = random.Random(a.seed)
    student = learner.add_student("soak", report.course_id)
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    letters = list("abcd")
    worst, problems, step_counts = 0, [], {}
    for i in range(a.turns):
        clock[0] += timedelta(seconds=rng.choice([4, 8, 15, 30, 60, 120] * 6 + [1800, 5400]))  # now and then a long break
        part = rng.choice(parts)
        labels = {
            "question_depth": rng.choice(["surface", "mechanism", "transfer"]),
            "engagement": rng.choice(["passive", "active", "constructive"]),
            "choice": rng.choice(["none"] * 6 + ["just_show_me", "try_first", "hint", "skip_point", "quiz", "stop"]),
            "words": rng.choice([None, 3, 12, 60]),
            "confidence": rng.choice([None, "none", "guess", "fairly_sure", "certain"]),
            "request_type": rng.choice(["concept"] * 5 + ["research", "homework", "other"]),
        }
        answer = None
        if rng.random() < 0.45:
            kind = rng.choice(["mcq", "explain_back", "review", "extend", "find_error", "prequestion"])
            answer = {
                "part_id": part,
                "type": kind,
                "points_met": rng.sample(letters, rng.randint(0, 3)),
                "choice": rng.choice(letters),
                "correct": rng.choice([True, False]),
            }
        try:
            out = service.tutor_turn(
                learner.get_student(student["id"]),
                "soak message",
                labels,
                node_ids=[part] if rng.random() < 0.8 else None,
                answer=answer,
                client="soak",
            )
        except Exception as exc:  # noqa: BLE001  (the point is to catch anything)
            problems.append(f"turn {i}: {type(exc).__name__}: {exc}")
            continue
        size = len(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        worst = max(worst, size)
        if size > cap:
            problems.append(f"turn {i}: result {size} > {cap}")
        for step in out.get("plan", []):
            step_counts[step["move"]] = step_counts.get(step["move"], 0) + 1
            if "item" in step:
                problems.append(f"turn {i}: a server-only item reached the chatbot")

    def snapshot() -> dict:
        conn, out = learner._conn(), {}
        for table in learner.DERIVED_TABLES:
            columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})") if r["name"] != "id"]
            if (
                "student_id" in columns and table != "learner_offset_cache"
            ):  # a lazily filled cache: presence differs, values are tested in test_offset_cache
                out[table] = sorted(
                    (tuple(r) for r in conn.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE student_id = ?", (student["id"],))),
                    key=repr,
                )
        return out

    before = snapshot()
    learner.rebuild_state(student["id"])
    after = snapshot()
    if os.environ.get("SOAK_DEBUG"):
        c = learner._conn()
        for r in c.execute(
            "SELECT id, ts, part_id, evidence_type, score, origin FROM evidence_log WHERE id IN (9,10,11) AND student_id = ?",
            (student["id"],),
        ):
            print("EV", tuple(r))
        for r in c.execute("SELECT id, ts, node_ids FROM exchange_log WHERE student_id = ? ORDER BY id LIMIT 8", (student["id"],)):
            print("EX", tuple(r))
    for table in before:
        if before[table] != after[table]:
            only_before = [r for r in before[table] if r not in after[table]][:2]
            only_after = [r for r in after[table] if r not in before[table]][:2]
            problems.append(
                f"rebuild changed {table}: {len(before[table])} rows before, {len(after[table])} after; e.g. {only_before} vs {only_after}"
            )
    print(f"{a.turns} turns, largest result {worst} of {cap}; moves seen: {dict(sorted(step_counts.items()))}")
    for p in problems[:20]:
        print("PROBLEM", p)
    print("soak: ok" if not problems else f"soak: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
