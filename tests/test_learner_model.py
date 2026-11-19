"""The learner model's core behaviour: bayesian updates, forgetting, levels and rebuild."""

from datetime import datetime, timedelta, timezone

import pytest

from edux import learner


def _p_known(student_id, part_id):
    row = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    return row["p_known"] if row else None


def test_unseen_part_starts_at_its_prior(student, part):
    assert learner.part_p(student["id"], part) == pytest.approx(learner.initial_state(part)[0])


def test_correct_open_answer_raises_p_and_a_wrong_one_lowers_it(student, part):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    after_right = _p_known(student["id"], part)
    assert after_right > learner.initial_state(part)[0]
    learner.record_evidence(student["id"], part, "explain_back", 0.0, apply="now")
    assert _p_known(student["id"], part) < after_right


def test_one_open_answer_cannot_reach_secure(student, part):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    assert learner.level(learner.part_p(student["id"], part)) != "secure"


def test_p_known_stays_inside_the_clamp(student, part):
    for _ in range(60):
        learner.record_evidence(student["id"], part, "mcq_check", 1.0, apply="now", n_options=4)
    assert 0.001 <= _p_known(student["id"], part) <= 0.999


def test_forgetting_halves_recall_each_half_life():
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    assert learner.p_now(0.8, 2.0, start, start + timedelta(days=2)) == pytest.approx(0.4)
    assert learner.p_now(0.8, 2.0, start, start) == pytest.approx(0.8)
    assert learner.p_now(0.8, 2.0, None, start + timedelta(days=30)) == pytest.approx(0.8)  # no clock, no decay


@pytest.mark.parametrize(("p", "expected"), [(0.10, "new"), (0.50, "developing"), (0.90, "secure")])
def test_levels(p, expected):
    assert learner.level(p) == expected


def test_rebuild_reproduces_the_state(student, part):
    sid = student["id"]
    learner.record_exchange(sid, [part], "transfer", "constructive", apply="now")
    learner.record_evidence(sid, part, "explain_back", 1.0, apply="now")
    learner.record_evidence(sid, part, "review", 0.0, apply="now")
    before = learner._conn().execute("SELECT * FROM part_state WHERE student_id = ?", (sid,)).fetchall()
    learner.rebuild_state(sid)
    after = learner._conn().execute("SELECT * FROM part_state WHERE student_id = ?", (sid,)).fetchall()
    assert [dict(r) for r in before] == [dict(r) for r in after]
