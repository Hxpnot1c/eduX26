"""Soak test: many random tutor_turn calls straight into the service (no server), with find-the-error and the
confidence question switched on. A seeded random walk of a student who mostly answers what they are asked (the right
multiple-choice option some of the time, a random subset of the points they are shown), and sometimes just chats, asks
to be shown, asks for reviews or researches something. The clock advances 4 seconds to 90 minutes a turn, as in real
chat (two turns inside one second are not realistic and replay in a different order).

Checks: no exception, every result within results.max_chars (or over it only with no reference left to drop, which is logged as over budget), no server-only item reaches the chatbot, and rebuilding
the derived state from the event logs gives the same state.

    python scripts/soak_turns.py [--turns 400] [--seed 1]

tests/test_soak.py runs the same walk in-process (so coverage sees it) with a few seeds.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LETTERS = list("abcd")


def _answer_for(out: dict | None, last_plan: dict, rng: random.Random, p_right: float, fallback_part: str) -> dict | None:
    """What a student would send for the question in the last reply, or None if it asked nothing."""
    if not out:
        return None
    for step in out.get("plan", []):
        data = step.get("data", {})
        kind, part = data.get("answer_type"), step.get("part_id") or fallback_part
        if not kind:
            continue
        if kind == "find_error":
            return {"part_id": part, "type": kind, "points_met": rng.sample(LETTERS, rng.randint(0, 3)), "choice": str(rng.randint(1, 4))}
        if data.get("options"):
            mcq = last_plan.get("mcq") or {}
            letters = [o["letter"] for o in data["options"]]
            right = next((letter for letter, option in (mcq.get(part) or {}).items() if option == "correct"), None)
            pick = right if right and rng.random() < p_right else rng.choice(letters)
            return {"part_id": part, "type": kind, "choice": pick, "correct": pick == right}
        points = [p["id"] for p in (out.get("score_next") or {}).get(part, [])]
        return {"part_id": part, "type": kind, "points_met": [p for p in points if rng.random() < p_right]}
    return None


def play(student_id: str, parts: list[str], turns: int, seed: int) -> tuple[dict, list[str]]:
    """Play the walk for one student in the already configured databases. Returns (stats, problems)."""
    from edux import learner, service

    rng, problems, stats = random.Random(seed), [], {"largest": 0, "over": 0, "moves": {}}
    cap = learner._settings().results.max_chars
    clock = datetime.now(timezone.utc) - timedelta(days=1)
    original = learner.now_iso
    learner.now_iso = lambda: clock.isoformat(timespec="seconds")
    out = None
    try:
        for i in range(turns):
            clock += timedelta(seconds=rng.choice([4, 8, 15, 30, 60, 120] * 6 + [1800, 5400]))  # now and then a long break
            part = rng.choice(parts)
            p_right = rng.choice([0.2, 0.6, 0.9])
            labels = {
                "question_depth": rng.choice(["surface", "mechanism", "transfer"]),
                "engagement": rng.choice(["passive", "active", "constructive"]),
                "choice": rng.choice(["none"] * 8 + ["just_show_me", "try_first", "hint", "skip_point", "quiz", "extend", "stop"]),
                "words": rng.choice([None, 3, 12, 60]),
                "confidence": rng.choice([None, "none", "guess", "fairly_sure", "certain"]),
                "request_type": rng.choice(["concept"] * 8 + ["research", "homework", "other"]),
                "asks_for_reviews": rng.random() < 0.05,
            }
            if labels["request_type"] == "research":
                labels["question_features"] = rng.sample(["concept", "context", "asks_sources", "asks_reasoning"], rng.randint(0, 3))
                labels["web_access"] = rng.choice([True, False, None])
            answer = _answer_for(out, service._last_plan(student_id), rng, p_right, part) if rng.random() < 0.8 else None
            try:
                out = service.tutor_turn(
                    learner.get_student(student_id),
                    "soak message",
                    labels,
                    node_ids=[part] if (answer is None and rng.random() < 0.8) else None,
                    answer=answer,
                    client="soak",
                )
            except Exception as exc:  # noqa: BLE001  (the point is to catch anything)
                problems.append(f"turn {i}: {type(exc).__name__}: {exc}")
                out = None
                continue
            size = len(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
            stats["largest"] = max(stats["largest"], size)
            if size > cap:  # fit_budget never cuts the plan: over budget is logged, but only once nothing else is left to drop
                stats["over"] += 1
                if out.get("reference"):
                    problems.append(f"turn {i}: result {size} > {cap} with reference blocks still in it")
            for step in out.get("plan", []):
                stats["moves"][step["move"]] = stats["moves"].get(step["move"], 0) + 1
                if "item" in step:
                    problems.append(f"turn {i}: a server-only item reached the chatbot")
    finally:
        learner.now_iso = original

    def snapshot() -> dict:
        conn, snap = learner._conn(), {}
        for table in learner.DERIVED_TABLES:
            columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})") if r["name"] != "id"]
            if "student_id" in columns and table != "learner_offset_cache":  # a lazily filled cache: presence differs
                rows = conn.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE student_id = ?", (student_id,))
                snap[table] = sorted((tuple(r) for r in rows), key=repr)
        return snap

    before = snapshot()
    learner.rebuild_state(student_id)
    after = snapshot()
    for table in before:
        if before[table] != after[table]:
            problems.append(f"rebuild changed {table}: {len(before[table])} rows before, {len(after[table])} after")
    return stats, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    os.environ.update(EDUX_DATA_DIR=tempfile.mkdtemp(prefix="soak-"), EDUX_FIND_ERROR="1", EDUX_CONFIDENCE="1")
    from edux import db, graph, learner
    from ingest import load

    report = load.load_pack(ROOT / "coursepacks" / "example-mini", db_path=db.content_db_path())
    learner.use_database(db.learner_db_path(), db.content_db_path())
    student = learner.add_student("soak", report.course_id)
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    stats, problems = play(student["id"], parts, a.turns, a.seed)
    print(
        f"{a.turns} turns, largest result {stats['largest']}, {stats['over']} over budget; moves seen: {dict(sorted(stats['moves'].items()))}"
    )
    for problem in problems[:20]:
        print("PROBLEM", problem)
    print("soak: ok" if not problems else f"soak: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
