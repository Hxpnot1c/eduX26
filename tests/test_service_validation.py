"""What the service refuses, and says: bad labels, bad answers, bad profile changes and bad assessments. Each is an
`ok: false` result with a message the chatbot can act on, never an exception."""

from datetime import date, timedelta

import pytest

from edux import graph, learner, service

GOOD = {"question_depth": "mechanism", "engagement": "active"}


def _turn(student, **over):
    labels = {**GOOD, **over.pop("labels", {})}
    return service.tutor_turn(learner.get_student(student["id"]), "hello", labels, **over)


def _profile(student, **kwargs):
    return service.update_profile(learner.get_student(student["id"]), **kwargs)


def _future(days=30):
    return (date.today() + timedelta(days=days)).isoformat()


@pytest.mark.parametrize(
    ("labels", "needle"),
    [
        ({"question_depth": "deep"}, "question_depth"),
        ({"engagement": "bored"}, "engagement"),
        ({"choice": "teleport"}, "choice"),
        ({"request_type": "gossip"}, "request_type"),
    ],
)
def test_a_bad_label_is_refused_with_the_allowed_values(student, labels, needle):
    out = _turn(student, labels=labels)
    assert out["ok"] is False and needle in out["error"]


def test_a_bad_answer_is_refused(student, part):
    bad_part = _turn(student, answer={"part_id": "no_such_part", "type": "explain_back", "points_met": []})
    bad_type = _turn(student, answer={"part_id": part, "type": "telepathy"})
    bad_letter = _turn(student, answer={"part_id": part, "type": "explain_back", "points_met": ["z"]})
    assert not bad_part["ok"] and not bad_type["ok"] and not bad_letter["ok"]


def test_an_answer_to_a_question_that_was_never_asked_is_not_fatal(student, part):
    out = _turn(student, answer={"part_id": part, "type": "mcq", "choice": "A"}, node_ids=[part])
    assert out["ok"] is True


def test_profile_changes_are_checked(student):
    assert _profile(student, exam_date_override="not a date")["ok"] is False
    assert _profile(student, exam_date_override=_future(60))["ok"] is True
    assert _profile(student, exam_date_override="  ")["ok"] is True  # blank clears the override
    assert _profile(student, answer_length=0)["ok"] is False
    assert _profile(student, answer_length=80)["ok"] is True
    assert _profile(student, reminders=True)["ok"] is True


def test_assessments_are_checked(student):
    topic = graph.topics()[0]["name"]
    base = {"name": "Mock", "kind": "mock", "date": _future(), "topics": [topic]}
    assert _profile(student, add_assessment={**base, "kind": "quiz"})["ok"] is False
    assert _profile(student, add_assessment={**base, "name": "  "})["ok"] is False
    assert _profile(student, add_assessment={**base, "date": "soon"})["ok"] is False
    assert _profile(student, add_assessment={**base, "date": "2001-01-01"})["ok"] is False
    nothing = _profile(student, add_assessment={**base, "topics": ["zzz nothing"]})
    assert nothing["ok"] is False and nothing["topics"]
    added = _profile(student, add_assessment={**base, "topics": [topic, "zzz nothing"]})
    assert added["ok"] is True and added["added"]["unmatched"] == ["zzz nothing"]
    assert _profile(student, remove_assessment=999)["ok"] is False
    assert _profile(student, remove_assessment=added["added"]["id"])["ok"] is True


def test_a_teacher_set_assessment_cannot_be_removed_by_the_student(student):
    class_id = learner.add_class("Y12", None)
    learner.add_students_to_class(class_id, [student["id"]])
    topic = graph.topics()[0]
    parts = graph.parts_of(topic["id"])
    learner.add_class_assessment(class_id, "Class test", "class_test", _future(10), parts)
    mine = learner.get_student(student["id"])
    row = learner._conn().execute("SELECT id FROM student_assessment WHERE class_id = ?", (class_id,)).fetchone()
    out = service.update_profile(mine, remove_assessment=row["id"])
    assert out["ok"] is False and "teacher" in out["error"]


def test_covered_in_class_is_checked(student):
    topic = graph.topics()[0]["name"]
    assert _profile(student, covered_in_class={"topics": ["zzz nothing"]})["ok"] is False
    done = _profile(student, covered_in_class={"topics": [topic], "when": "2026-10-01"})
    assert done["ok"] is True
    assert _profile(student, covered_in_class={"topics": [topic], "when": "tomorrow"})["ok"] is False


def test_call_stats_summarise_the_log(student, part):
    _turn(student, node_ids=[part])
    service.log_call(student["id"], "tutor_turn", __import__("datetime").datetime.now(), 12.0, 900, True, None, False)
    stats = service.call_stats(student["id"], last=5)
    assert stats["recent"] and stats["tools"]["tutor_turn"]["median_ms"] >= 0
    assert service.call_stats()["tools"]
