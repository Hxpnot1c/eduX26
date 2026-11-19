"""Deterministic probes of three behaviours found while simulating (no randomness; each prints PASS/FOUND lines).

    PYTHONPATH=<worktree> <venv>/bin/python docs/research/overnight/sims/probes.py

1. saturation: repeated correct evidence drives p_known to exactly 1.0, and the next ordinary exchange on the
   part then raises ZeroDivisionError in learner.apply_exchange (odds = p / (1 - p)), so tutor_turn would fail.
2. quiz_me: "Quiz me on what's due" (the review_due prompt) after studying another part returns teaching on the
   old focus, not the due review, because a message that names nothing keeps the previous turn's focus.
3. stepback_loop: once a part is stuck (the same point missed on its check and re-check), every later plan in the
   session on that part is the same prerequisite check; answering it right never ends the loop.
Runs in a fresh /tmp/claude-1000/w1-06/probes data dir, with the clamp shim OFF (the real code path).
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edux_sim as S   # noqa: E402


def main() -> None:
    S.setup_data_dir("/tmp/claude-1000/w1-06/probes")
    S.use_settings("current")
    from edux import learner, service
    learner._save_state = S._ORIG.get("orig_save", learner._save_state)   # the real _save_state: no clamp
    lab = {"question_depth": "mechanism", "engagement": "active"}
    t = S.EXAM - timedelta(days=30)

    # 1. saturation
    learner.add_student("p1", "example-mini", student_id="p1")
    n = None
    for i in range(200):
        learner.record_evidence("p1", "pes_definition", "mcq_check", 1.0, ts=S.iso(t + timedelta(minutes=2 * i)),
                                apply="now")
        p = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id='p1' AND part_id='pes_definition'"
                                    ).fetchone()[0]
        if p >= 1.0:
            n = i + 1
            break
    try:
        learner.record_exchange("p1", ["pes_definition"], "mechanism", "active",
                                ts=S.iso(t + timedelta(minutes=2 * (n or 200) + 2)), apply="now")
        print(f"1. saturation: p_known reached 1.0 after {n} correct mcq_check answers 2 min apart; next exchange ok")
    except ZeroDivisionError:
        print(f"1. FOUND saturation: p_known reached exactly 1.0 after {n} correct mcq_check answers (2 min apart, "
              f"one part); the next exchange raised ZeroDivisionError in learner.apply_exchange")

    # 2. quiz me on what's due
    learner.add_student("p2", "example-mini", student_id="p2")
    st = learner.get_student("p2")
    for i, part in enumerate(["pes_definition", "pes_formula"]):
        learner.record_evidence("p2", part, "explain_back", 1.0, ts=S.iso(t + timedelta(minutes=i)), apply="now")
    service.tutor_turn(st, "Can you help me with YED?", lab, node_ids=["yed_definition"], at=S.iso(t + timedelta(minutes=5)))
    later = t + timedelta(days=5)
    due = [r["part_id"] for r in learner.due_reviews("p2", 10, S.iso(later))]
    out = service.tutor_turn(st, "Quiz me on what's due.", lab, at=S.iso(later))
    plan = [(s["move"], s["part_id"], s["data"].get("purpose")) for s in out["plan"]]
    reviewed = any(s[2] == "review" for s in plan)
    print(f"2. {'ok' if reviewed else 'FOUND'} quiz_me: due {due}; 'Quiz me on what's due' 5 days later -> {plan}")

    # 3. step-back loop
    learner.add_student("p3", "example-mini", student_id="p3")
    st = learner.get_student("p3")
    clock = [t]

    def turn(msg, node_ids=None, answer=None):
        clock[0] += timedelta(minutes=2)
        return service.tutor_turn(st, msg, lab, node_ids=node_ids, answer=answer, at=S.iso(clock[0]))

    def mcq():
        return S._plan_json("p3").get("mcq") or {}

    def letter(right: bool) -> str:
        options = mcq()["options"]
        return next(k for k, o in sorted(options.items()) if (o["id"] == "correct") == right)

    out = turn("How do I calculate PED?", node_ids=["ped_formula"])
    moves = []
    for _ in range(14):
        m = mcq()
        if not m:
            break
        # wrong on ped_formula checks, right on everything else (the prerequisite)
        right = m["part_id"] != "ped_formula" or m["purpose"] == "intuition"
        out = turn(letter(right), answer={"part_id": m["part_id"], "type": "mcq", "choice": letter(right)})
        moves.append("/".join(f"{s['move']}:{s['part_id']}" + (":stuck" if s["data"].get("stuck") else "")
                              for s in out["plan"]))
    stuck_steps = sum(":stuck" in m for m in moves)
    print(f"3. {'FOUND' if stuck_steps >= 5 else 'ok'} stepback_loop: {stuck_steps} of the last {len(moves)} plans "
          f"were a step-back prerequisite check after ped_formula was stuck, while the prerequisite was answered right "
          f"every time")
    for i, m in enumerate(moves, 1):
        print(f"   turn {i}: {m}")


if __name__ == "__main__":
    main()
