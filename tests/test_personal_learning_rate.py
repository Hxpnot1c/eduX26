"""Step 05m: the personal learning rate is off by default, leaves out a part's first answer and AI-literacy
parts, and stays inside its bounds."""

import math
from datetime import datetime, timedelta, timezone

import pytest

from edux import learner


def _answers(student_id, parts, per_part=4):
    """per_part right answers on each part, one per day (so each is its own session), oldest first."""
    start = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
    day = 0
    for i in range(per_part):
        for part in parts:
            ts = (start + timedelta(days=day)).isoformat(timespec="seconds")
            learner.record_evidence(student_id, part, "mcq_check", 1.0, ts=ts, apply="now", n_options=4)
            day += 1


def _course_parts(n):
    return [p for p in learner.all_parts() if not p.startswith("ail_")][:n]


def test_it_is_off_by_default(monkeypatch):
    monkeypatch.delenv("EDUX_PERSONALISATION", raising=False)
    assert learner._settings().personalisation.enabled is False
    assert learner.personalisation_on() is False


def test_the_environment_switches_it_on_and_off(monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "1")
    assert learner.personalisation_on() is True
    monkeypatch.setenv("EDUX_PERSONALISATION", "0")
    assert learner.personalisation_on() is False


def test_the_offset_is_zero_when_it_is_off(student, monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "0")
    _answers(student["id"], _course_parts(4))
    assert learner.learning_offset(student["id"]) == {"offset": 0.0, "n": 0, "weight": 1.0}


def test_each_parts_first_answer_is_left_out(student, monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "1")
    parts = _course_parts(4)
    if len(parts) < 4:
        pytest.skip("needs four course parts")
    _answers(student["id"], parts, per_part=4)  # 16 answers, 4 of them first answers
    assert learner.learning_offset(student["id"])["n"] == 12


def test_ai_literacy_evidence_leaves_the_offset_alone(student, monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "1")
    parts = _course_parts(4)
    _answers(student["id"], parts, per_part=4)
    before = learner.learning_offset(student["id"])
    for i in range(6):
        ts = datetime(2026, 10, 20 + i, 10, tzinfo=timezone.utc).isoformat(timespec="seconds")
        learner.record_evidence(student["id"], "ail_verify", "ail_task", 1.0, ts=ts, apply="now")
    assert learner.learning_offset(student["id"]) == before


def test_the_offset_stays_inside_the_bounds(student, monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "1")
    _answers(student["id"], _course_parts(4), per_part=8)
    low, high = (math.log(b) for b in learner._settings().personalisation.learn_rate_weight_bounds)
    assert low - 1e-9 <= learner.learning_offset(student["id"])["offset"] <= high + 1e-9


def test_an_ai_literacy_part_learns_at_the_population_rate_whatever_the_offset(student, monkeypatch):
    monkeypatch.setattr(learner, "learning_offset", lambda *a, **k: {"offset": 1.0, "n": 99, "weight": math.e})
    sid = student["id"]
    learner.record_evidence(sid, "ail_verify", "ail_task", 1.0, apply="now")
    with_offset = (
        learner._conn()
        .execute("SELECT p_known FROM part_state WHERE student_id = ? AND part_id = 'ail_verify'", (sid,))
        .fetchone()["p_known"]
    )
    monkeypatch.setattr(learner, "learning_offset", lambda *a, **k: {"offset": 0.0, "n": 0, "weight": 1.0})
    other = learner.add_student("Other Student", learner._conn().execute("SELECT course_id FROM student LIMIT 1").fetchone()[0])
    learner.record_evidence(other["id"], "ail_verify", "ail_task", 1.0, apply="now")
    without = (
        learner._conn()
        .execute("SELECT p_known FROM part_state WHERE student_id = ? AND part_id = 'ail_verify'", (other["id"],))
        .fetchone()["p_known"]
    )
    assert with_offset == pytest.approx(without)
