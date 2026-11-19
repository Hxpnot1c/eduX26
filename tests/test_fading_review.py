"""Decision 0025: after a right answer, a learnt part is due before it fades below new (reason "fading")."""

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from edux import learner

GAP = 30.0  # a share gap far enough off that any crossing comes first


def _review(student_id, part_id):
    return learner._conn().execute("SELECT * FROM review_queue WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()


def _wrong_then_right(student_id, part):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    learner.record_evidence(student_id, part, "mcq_check", 0.0, ts=(now - timedelta(minutes=2)).isoformat(), apply="now", n_options=4)
    ts = (now - timedelta(minutes=1)).isoformat()
    learner.record_evidence(student_id, part, "mcq_check", 1.0, ts=ts, apply="now", n_options=4)
    state = learner._conn().execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part)).fetchone()
    return dict(state), datetime.fromisoformat(ts)


@pytest.fixture()
def far_gap(monkeypatch):
    monkeypatch.setattr(learner, "review_gap_days", lambda *a, **k: GAP)


def test_a_right_answer_below_review_when_below_queues_a_fading_review_before_the_gap(student, part, far_gap):
    state, at = _wrong_then_right(student["id"], part)
    s = learner._settings()
    assert s.levels.new < state["p_known"] < s.scheduling.review_when_below  # e.g. about 0.45: recall_below can't fire
    row = _review(student["id"], part)
    assert row["reason"] == "fading"
    floor = learner.decay_floor(part)
    expected = max(s.scheduling.min_gap_days, learner.days_until_below(state, s.levels.new, floor))
    assert expected < GAP
    assert abs((datetime.fromisoformat(row["due"]) - at).total_seconds() - expected * 86400) < 2


def test_with_review_before_new_off_the_share_gap_stands(student, part, far_gap, monkeypatch):
    s = learner._settings()
    changed = dataclasses.replace(s, scheduling=dataclasses.replace(s.scheduling, review_before_new=False))
    monkeypatch.setattr(learner, "_settings", lambda: changed)
    _wrong_then_right(student["id"], part)
    assert _review(student["id"], part)["reason"] == "scheduled"


def test_above_review_when_below_the_earlier_recall_below_review_wins(student, part, far_gap):
    learner.record_evidence(student["id"], part, "mcq_check", 1.0, apply="now", n_options=4)
    state = learner._conn().execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?", (student["id"], part)).fetchone()
    assert state["p_known"] > learner._settings().scheduling.review_when_below
    assert _review(student["id"], part)["reason"] == "recall_below"


def test_a_wrong_answer_never_queues_a_fading_review(student, part, far_gap):
    learner.record_evidence(student["id"], part, "mcq_check", 1.0, apply="now", n_options=4)
    learner.record_evidence(student["id"], part, "mcq_check", 0.0, apply="now", n_options=4)
    assert _review(student["id"], part)["reason"] != "fading"
