"""Step 05n: the value score has no learning-chance factor, and its edge choices behave as built."""

import inspect
from datetime import datetime, timedelta, timezone

import pytest

from edux import learner


def test_there_is_no_move_chance_and_step_value_takes_no_chance():
    assert not hasattr(learner, "move_chance")
    assert list(inspect.signature(learner.step_value).parameters) == ["student_id", "part_id", "at"]


def test_with_no_final_exam_ahead_the_final_counts_at_the_urgency_floor_with_todays_p(student, part, monkeypatch):
    monkeypatch.setattr(learner, "final_exam_days", lambda *a, **k: None)
    s = learner._settings().priorities
    found = learner.step_value(student["id"], part)
    expected = s.weight_final * s.urgency_floor * (1 - learner.part_p(student["id"], part))
    assert found["value"] == pytest.approx(expected, rel=1e-6)
    assert found["reason"] is None


def test_an_upcoming_mock_raises_the_value_and_names_itself_as_the_reason(student, part, monkeypatch):
    monkeypatch.setattr(learner, "final_exam_days", lambda *a, **k: None)
    plain = learner.step_value(student["id"], part)["value"]
    soon = (datetime.now(timezone.utc) + timedelta(days=3)).date().isoformat()
    monkeypatch.setattr(
        learner, "assessments", lambda *a, **k: [{"id": 1, "name": "Mock", "kind": "mock", "date": soon, "part_ids": [part]}]
    )
    found = learner.step_value(student["id"], part)
    assert found["value"] > plain
    assert found["reason"]["name"] == "Mock"


def test_the_value_does_not_depend_on_the_learning_rate_offset(student, part, monkeypatch):
    base = learner.step_value(student["id"], part)["value"]
    monkeypatch.setattr(learner, "learning_offset", lambda *a, **k: {"offset": 1.0, "n": 99, "weight": 2.7})
    assert learner.step_value(student["id"], part)["value"] == pytest.approx(base)
