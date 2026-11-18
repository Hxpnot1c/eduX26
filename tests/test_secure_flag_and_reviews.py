"""Step 05k: feedback judges "secure" on the level before the answer; review_when_below edge cases."""

from datetime import datetime, timedelta, timezone

import pytest

from edux import learner


def _review(student_id, part_id):
    return learner._conn().execute(
        "SELECT * FROM review_queue WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()


def test_answer_p_before_is_the_level_before_the_answer(student, part):
    sid, ts = student["id"], learner.now_iso()
    start = learner.initial_state(part)[0]
    learner.record_evidence(sid, part, "explain_back", 1.0, ts=ts, apply="now")
    assert learner.answer_p_before(sid, part, ts) == pytest.approx(start)
    ts2 = (datetime.fromisoformat(ts) + timedelta(minutes=1)).isoformat(timespec="seconds")
    learner.record_evidence(sid, part, "explain_back", 1.0, ts=ts2, apply="now")
    assert learner.answer_p_before(sid, part, ts2) > start      # the second answer starts from the first's result


def test_the_answer_that_tips_a_part_to_secure_was_not_secure_before_it(student, part):
    sid, now = student["id"], datetime.now(timezone.utc)
    secure_after = None
    for i in range(12):
        ts = (now + timedelta(minutes=i)).isoformat(timespec="seconds")
        learner.record_evidence(sid, part, "mcq_check", 1.0, ts=ts, apply="now", n_options=4)
        before, after = learner.answer_p_before(sid, part, ts), learner.part_p(sid, part, ts)
        if secure_after is None and learner.level(after) == "secure":
            secure_after = i
            assert learner.level(before) != "secure"      # tipped here: the flag, read on `before`, is off
        elif secure_after is not None:
            assert learner.level(before) == "secure"       # the next right answer is on a secure part
            return
    pytest.fail("the part never reached secure")


def test_no_answer_p_before_when_nothing_was_recorded(student, part):
    assert learner.answer_p_before(student["id"], part, learner.now_iso()) is None


def test_days_until_below_edge_cases():
    base = {"p_known": 0.8, "half_life_days": 2.0, "clock_start": "2026-11-01T00:00:00+00:00"}
    assert learner.days_until_below(base, 0.5) == pytest.approx(2.0 * 0.6780719, rel=1e-4)    # 2 * log2(0.8 / 0.5)
    assert learner.days_until_below({**base, "p_known": 0.5}, 0.5) is None                      # already at the threshold
    assert learner.days_until_below({**base, "p_known": 0.3}, 0.5) is None                      # already below it
    assert learner.days_until_below({**base, "clock_start": None}, 0.5) is None                 # no clock, no forgetting


def test_a_part_at_or_below_the_threshold_keeps_the_share_gap(student, part):
    sid = student["id"]
    learner.record_evidence(sid, part, "explain_back", 0.0, apply="now")      # a wrong answer: p stays low
    row = _review(sid, part)
    assert row["reason"] == "scheduled"


def test_min_gap_days_floors_a_crossing_that_would_be_sooner(student, part, monkeypatch):
    sid = student["id"]
    monkeypatch.setattr(learner, "review_gap_days", lambda *a, **k: 30.0)
    monkeypatch.setattr(learner, "days_until_below", lambda *a, **k: 0.2)    # sooner than min_gap_days
    ts = learner.now_iso()
    learner.record_evidence(sid, part, "mcq_check", 1.0, ts=ts, apply="now", n_options=4)
    row = _review(sid, part)
    due = datetime.fromisoformat(row["due"])
    expected = datetime.fromisoformat(ts) + timedelta(days=learner._settings().scheduling.min_gap_days)
    assert row["reason"] == "recall_below"
    assert abs((due - expected).total_seconds()) < 2
