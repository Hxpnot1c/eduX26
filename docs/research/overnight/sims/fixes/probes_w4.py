"""Wave-4 probes for the four core fixes (w4-fix-core). Deterministic; no randomness.

Copy this file into <code copy>/docs/research/overnight/sims/fixes/ (next to a copy of sims/) and run
    PYTHONPATH=<code copy> /home/vishnu/edux26/.venv/bin/python <code copy>/docs/research/overnight/sims/fixes/probes_w4.py <data dir>
edux_sim.ROOT then resolves to the code copy, so its own settings.toml and coursepack are used.

1. saturation: 200 correct mcq_check answers 2 min apart on one part -> highest p_known, then one exchange;
   plus a legacy row forced to p_known = 1.0 (a database written before the fix) and one exchange.
2. quiz_me: "Quiz me on what's due." 5 days after studying another part -> is the plan a due review?
3. stepback: wrong on every ped_formula check, right on everything else; the 14 plans after the first.
4. talk_only: 14 transfer/constructive exchanges on a never-answered part, no checks -> p_now and level, at 0 and 90 days.
5. propagation: 6 right answers on ped_values -> its never-answered prerequisite ped_formula, and whether a
   prerequisite check is planned when the student asks about ped_values next session.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edux_sim as S   # noqa: E402


def main(data_dir: str) -> None:
    S.setup_data_dir(data_dir)
    S.use_settings("current")
    from edux import learner, service
    learner._save_state = S._ORIG.get("orig_save", learner._save_state)   # the real _save_state: no sim clamp
    lab = {"question_depth": "mechanism", "engagement": "active"}
    t = S.EXAM - timedelta(days=30)

    def pk(sid, part):
        r = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id=? AND part_id=?", (sid, part)).fetchone()
        return r[0] if r else None

    # 1. saturation
    learner.add_student("p1", "example-mini", student_id="p1")
    top, first_one = 0.0, None
    for i in range(200):
        learner.record_evidence("p1", "pes_definition", "mcq_check", 1.0, ts=S.iso(t + timedelta(minutes=2 * i)), apply="now")
        p = pk("p1", "pes_definition")
        top = max(top, p)
        if p >= 1.0 and first_one is None:
            first_one = i + 1
    try:
        learner.record_exchange("p1", ["pes_definition"], "mechanism", "active", ts=S.iso(t + timedelta(minutes=402)), apply="now")
        ok = "exchange ok"
    except ZeroDivisionError:
        ok = "ZeroDivisionError"
    with learner._conn() as c:
        c.execute("UPDATE part_state SET p_known = 1.0 WHERE student_id='p1' AND part_id='pes_definition'")
    try:
        learner.record_exchange("p1", ["pes_definition"], "mechanism", "active", ts=S.iso(t + timedelta(minutes=404)), apply="now")
        legacy = "exchange ok"
    except ZeroDivisionError:
        legacy = "ZeroDivisionError"
    print(f"1. saturation: max p_known {top!r} over 200 answers (first exactly 1.0 at answer {first_one}); "
          f"next exchange: {ok}; legacy row at 1.0: {legacy}")

    # 2. quiz me on what's due (a fresh student per wording, so one wording's pending question can't leak into the next)
    for k, msg in enumerate(["Quiz me on what's due.", "quiz me on what's due", "Can you test me on my reviews?",
                             "Can you explain that again?"]):
        sid = f"p2-{k}"
        learner.add_student(sid, "example-mini", student_id=sid)
        st = learner.get_student(sid)
        for i, part in enumerate(["pes_definition", "pes_formula"]):
            learner.record_evidence(sid, part, "explain_back", 1.0, ts=S.iso(t + timedelta(minutes=i)), apply="now")
        service.tutor_turn(st, "Can you help me with YED?", lab, node_ids=["yed_definition"], at=S.iso(t + timedelta(minutes=5)))
        later = t + timedelta(days=5)
        due = [r["part_id"] for r in learner.due_reviews(sid, 10, S.iso(later))]
        out = service.tutor_turn(st, msg, lab, at=S.iso(later))
        plan = [(s["move"], s["part_id"], s["data"].get("purpose")) for s in out["plan"]]
        print(f"2. quiz_me: due {due}; {msg!r} 5 days later -> {plan}")

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

    turn("How do I calculate PED?", node_ids=["ped_formula"])
    moves = []
    for _ in range(14):
        m = mcq()
        if not m:
            pl = S._plan_json("p3").get("plan") or []
            ask = next((s for s in reversed(pl) if s["data"].get("answer_type")), None)
            if not ask:
                break
            out = turn("I think it is about price.", answer={"part_id": ask["part_id"], "type": ask["data"]["answer_type"],
                                                              "points_met": []})
        else:
            right = m["part_id"] != "ped_formula" or m["purpose"] == "intuition"
            out = turn(letter(right), answer={"part_id": m["part_id"], "type": "mcq", "choice": letter(right)})
        if not out.get("ok"):
            moves.append("ERROR " + str(out.get("error")))
            continue
        moves.append("/".join(f"{s['move']}:{s['part_id']}" + (":stuck" if s["data"].get("stuck") else "")
                              for s in out["plan"]))
    stuck_steps = sum(":stuck" in m for m in moves)
    reteach_whole = sum(m.startswith("reteach") or "/reteach:" in m and "anchor" in m for m in moves)
    print(f"3. stepback: {stuck_steps} of {len(moves)} plans were a step-back prerequisite check")
    for i, m in enumerate(moves, 1):
        print(f"   turn {i}: {m}")

    # 4. talk-only exchanges
    learner.add_student("p4", "example-mini", student_id="p4")
    for i in range(14):
        learner.record_exchange("p4", ["yed_definition"], "transfer", "constructive", ts=S.iso(t + timedelta(minutes=2 * i)), apply="now")
    for days in (0, 90):
        p = learner.part_p("p4", "yed_definition", S.iso(t + timedelta(days=days, minutes=30)))
        print(f"4. talk_only: 14 transfer/constructive exchanges, day {days}: p_now {p:.3f} ({learner.level(p)}); "
              f"stored p_known {pk('p4', 'yed_definition'):.3f}")
    q = learner._conn().execute("SELECT reason FROM review_queue WHERE student_id='p4' AND part_id='yed_definition'").fetchone()
    print(f"   untested review queued: {q[0] if q else None}")

    # 5. propagation onto a never-answered prerequisite
    learner.add_student("p5", "example-mini", student_id="p5")
    for i in range(6):
        learner.record_evidence("p5", "ped_values", "mcq_check", 1.0, ts=S.iso(t + timedelta(minutes=2 * i)), apply="now")
    p = learner.part_p("p5", "ped_formula", S.iso(t + timedelta(days=1)))
    st = learner.get_student("p5")
    out = service.tutor_turn(st, "Can we do PED values?", lab, node_ids=["ped_values"], at=S.iso(t + timedelta(days=1)))
    plan = [(s["move"], s["part_id"], s["data"].get("purpose")) for s in out["plan"]]
    print(f"5. propagation: never-answered ped_formula reads {p:.3f} ({learner.level(p)}), stored "
          f"{pk('p5', 'ped_formula'):.3f}; next-day plan on ped_values -> {plan}")


if __name__ == "__main__":
    main(sys.argv[1])
