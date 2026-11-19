"""Step 05s: fatigue follows time on task and rapid guesses, not how well a student answers."""

from datetime import datetime, timedelta, timezone

import pytest

from edux import learner, service


def test_extra_slip_is_zero_until_28_minutes_then_rises_to_its_cap():
    assert learner.extra_slip(0) == 0 and learner.extra_slip(27) == 0 and learner.extra_slip(28) == 0
    assert learner.extra_slip(50) == pytest.approx(0.044)
    assert learner.extra_slip(88) == pytest.approx(0.12)
    assert learner.extra_slip(300) == pytest.approx(0.12)  # capped


def test_rapid_guess_compares_latency_with_reading_plus_typing_time():
    # 60 question words at 300 wpm = 12 s; 5 answer words at 52 wpm = 5.8 s; threshold about 17.8 s
    assert learner.rapid_guess(10.0, 60, 5) is True
    assert learner.rapid_guess(25.0, 60, 5) is False
    assert learner.rapid_guess(None, 60, 5) is False  # no previous turn: unknown, not rapid
    assert learner.rapid_guess(1.0, 0, 5) is False  # no question text: unknown, not rapid
    assert learner.rapid_guess(1.0, None, None) is False
    assert learner.rapid_guess(1.0, 60, None) is False  # the chatbot didn't send the word count: unknown, not rapid


def _answer(student_id, part, minutes_in, latency, q_words=60, words=3, session_start=None):
    start = session_start or datetime(2026, 11, 10, 10, tzinfo=timezone.utc)
    ts = (start + timedelta(minutes=minutes_in)).isoformat(timespec="seconds")
    learner.record_exchange(
        student_id,
        [part],
        "surface",
        "active",
        ts=ts,
        apply="now",
        timing={"latency_s": latency, "question_words": q_words, "answer_words": words},
        evidence=[{"part_id": part, "type": "mcq_check", "score": 1.0, "n_options": 4}],
    )
    return ts


def _state(student_id, ts):
    return learner.session_state(student_id, ts)


def test_no_fatigued_mode_for_a_long_run_of_wrong_answers_alone(student, part):
    sid, ts = student["id"], None
    for i in range(8):
        start = datetime(2026, 11, 10, 10, tzinfo=timezone.utc)
        ts = (start + timedelta(minutes=2 * i)).isoformat(timespec="seconds")
        learner.record_evidence(sid, part, "mcq_check", 0.0, ts=ts, apply="now", n_options=4)
    assert _state(sid, ts)["fatigued"] is False


def test_long_session_mode_starts_at_the_mode_minutes(student, part):
    sid = student["id"]
    start = datetime(2026, 11, 10, 10, tzinfo=timezone.utc)
    learner.record_evidence(sid, part, "mcq_check", 1.0, ts=start.isoformat(timespec="seconds"), apply="now", n_options=4)
    for m in (10, 20, 30, 40, 49):  # keep one session going with gaps under gap_minutes
        learner.record_evidence(
            sid, part, "mcq_check", 1.0, ts=(start + timedelta(minutes=m)).isoformat(timespec="seconds"), apply="now", n_options=4
        )
    before = _state(sid, (start + timedelta(minutes=49)).isoformat(timespec="seconds"))
    assert before["fatigued"] is False
    after = _state(sid, (start + timedelta(minutes=50)).isoformat(timespec="seconds"))
    assert after["fatigued"] and after["fatigue_reason"] == "long_session"


def test_two_rapid_guesses_start_rushing_mode_and_a_rapid_guess_says_nothing_about_knowledge(student, part):
    sid = student["id"]
    t1 = _answer(sid, part, 1, latency=60.0)  # a considered answer: 60 s for a 60-word question
    p_after_one = learner.part_p(sid, part, t1)
    t2 = _answer(sid, part, 2, latency=3.0)  # rapid guess 1
    assert learner.part_p(sid, part, t2) == pytest.approx(p_after_one, abs=0.02)  # no knowledge update (only decay)
    assert _state(sid, t2)["fatigued"] is False
    t3 = _answer(sid, part, 3, latency=2.0)  # rapid guess 2
    state = _state(sid, t3)
    assert state["fatigued"] and state["fatigue_reason"] == "rushing" and state["rapid_guesses"] == 2


def test_a_rapid_guess_is_replayed_the_same_on_rebuild(student, part):
    sid = student["id"]
    for i, latency in enumerate((60.0, 3.0, 2.0)):
        _answer(sid, part, i + 1, latency)
    before = [dict(r) for r in learner._conn().execute("SELECT * FROM evidence_derived WHERE student_id = ? ORDER BY evidence_id", (sid,))]
    learner.rebuild_state(sid)
    after = [dict(r) for r in learner._conn().execute("SELECT * FROM evidence_derived WHERE student_id = ? ORDER BY evidence_id", (sid,))]
    assert [r["rapid"] for r in after] == [0, 1, 1] and after == before


def test_time_on_task_raises_the_slip_a_late_wrong_answer_costs_less(student, part):
    """The same wrong answer lowers p less late in a session than early (more of it is put down to slip)."""
    a, b = student, learner.add_student("Other", learner._conn().execute("SELECT course_id FROM student LIMIT 1").fetchone()[0])
    start = datetime(2026, 11, 10, 10, tzinfo=timezone.utc)
    for sid in (a["id"], b["id"]):
        for m in (0, 10, 20, 30, 40):  # five right answers to lift p, spread over 40 minutes (one session)
            learner.record_evidence(
                sid, part, "mcq_check", 1.0, ts=(start + timedelta(minutes=m)).isoformat(timespec="seconds"), apply="now", n_options=4
            )
    early = (start + timedelta(minutes=41)).isoformat(timespec="seconds")
    late = (start + timedelta(minutes=80)).isoformat(timespec="seconds")
    # keep b's session alive between 41 and 80 minutes with right answers on another part, so the wrong one lands late
    other = next(p for p in learner.all_parts() if p != part and not p.startswith("ail_"))
    for m in (50, 60, 70):
        learner.record_evidence(
            b["id"], other, "mcq_check", 1.0, ts=(start + timedelta(minutes=m)).isoformat(timespec="seconds"), apply="now", n_options=4
        )
    learner.record_evidence(a["id"], part, "mcq_check", 0.0, ts=early, apply="now", n_options=4)
    learner.record_evidence(b["id"], part, "mcq_check", 0.0, ts=late, apply="now", n_options=4)
    pa = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id=? AND part_id=?", (a["id"], part)).fetchone()[0]
    pb = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id=? AND part_id=?", (b["id"], part)).fetchone()[0]
    assert pb > pa


def test_the_timing_sent_to_the_exchange_is_counts_only(student):
    last = {
        "ts": "2026-11-10T10:00:00+00:00",
        "plan": [
            {
                "move": "ask_mcq",
                "part_id": "p",
                "key": "ask_mcq_check",
                "cue": "",
                "data": {"options": [{"letter": "A", "text": "one two three"}], "index": 1},
            }
        ],
    }
    t = service._timing(last, {"words": 4}, "2026-11-10T10:00:20+00:00")
    assert t["latency_s"] == 20 and t["answer_words"] == 4 and t["question_words"] >= 4
    assert service._timing({"ts": None, "plan": []}, {}, "2026-11-10T10:00:20+00:00") == {
        "latency_s": None,
        "question_words": None,
        "answer_words": None,
    }
    assert service._timing(last, {}, "2026-11-10T14:00:20+00:00")["latency_s"] is None  # a new session: no latency


def test_study_pattern_is_gone(student):
    assert "study_pattern" not in service.my_progress(learner.get_student(student["id"]))
