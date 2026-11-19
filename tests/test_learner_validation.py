"""The learner module's refusals and edge cases: bad events, bad answers, the background worker, rebuild with missing
rows, and a few small helpers."""

import pytest

from edux import graph, learner

LABELS = ("mechanism", "active")


def _bad_exchange(student, part, **over):
    kwargs = {"student_id": student["id"], "node_ids": [part], "question_depth": LABELS[0], "engagement": LABELS[1], "apply": "now"}
    kwargs.update(over)
    return learner.record_exchange(**kwargs)


@pytest.mark.parametrize(
    "over",
    [
        {"student_id": "nobody"},
        {"node_ids": []},
        {"question_depth": "deep"},
        {"engagement": "bored"},
        {"support_given": "magic"},
        {"choice_taken": "teleport"},
        {"request": {"question_features": ["nonsense"]}},
    ],
)
def test_record_exchange_refuses_bad_input(student, part, over):
    with pytest.raises(ValueError):
        _bad_exchange(student, part, **over)


@pytest.mark.parametrize(
    "item",
    [
        {"part_id": "no_such_part", "type": "explain_back", "score": 1},
        {"part_id": "PART", "type": "made_up", "score": 1},
        {"part_id": "PART", "type": "explain_back", "score": "high"},
        {"part_id": "PART", "type": "explain_back", "score": None},
        {"part_id": "PART", "type": "explain_back", "score": 1.5},
        {"part_id": "PART", "type": "mcq_check", "score": 1, "n_options": 1},
        {"part_id": "PART", "type": "mcq_check", "score": 1, "n_options": True},
    ],
)
def test_evidence_items_are_validated(student, part, item):
    item = {**item, "part_id": part if item["part_id"] == "PART" else item["part_id"]}
    with pytest.raises(ValueError):
        learner._evidence_rows([item])


def test_a_concept_expands_to_its_parts_and_an_empty_one_is_refused(course):
    concept = next(n for n in graph.children(graph.topics()[0]["id"]) if n["level"] == "concept")
    rows = learner._evidence_rows([{"part_id": concept["id"], "type": "explain_back", "score": 1}])
    assert {r[0] for r in rows} == set(graph.parts_of(concept["id"]))


def test_record_evidence_refuses_an_unknown_student_origin_type_or_part(student, part):
    with pytest.raises(ValueError):
        learner.record_evidence("nobody", part, "explain_back", 1.0, apply="now")
    with pytest.raises(ValueError):
        learner.record_evidence(student["id"], part, "explain_back", 1.0, origin="elsewhere", apply="now")
    with pytest.raises(ValueError):
        learner.record_evidence(student["id"], part, "made_up", 1.0, apply="now")
    with pytest.raises(ValueError):
        learner.record_evidence(student["id"], "no_such_part", "explain_back", 1.0, apply="now")


def test_unknown_events_cannot_be_fetched(course):
    with pytest.raises(ValueError):
        learner.get_event(999999)
    with pytest.raises(ValueError):
        learner.get_evidence(999999)


def test_an_unknown_profile_or_student_is_refused(course, student):
    with pytest.raises(ValueError):
        learner.add_student("X", course, profile="nonsense")
    with pytest.raises(ValueError):
        learner.require_student("nobody")
    with pytest.raises(ValueError):
        learner.add_students_to_class(learner.add_class("Y", None), ["nobody"])


def test_the_background_worker_applies_queued_events(student, part):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="background")
    learner.wait_for_worker()
    assert learner.part_p(student["id"], part, learner.now_iso()) > learner._settings().bkt.prior


def test_a_failing_job_is_reported_and_does_not_stop_the_worker(student, part, capsys):
    learner._queue.put((None, [987654]))
    learner.start_worker()
    learner.wait_for_worker()
    assert "Traceback" in capsys.readouterr().err
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="background")
    learner.wait_for_worker()


# --- answer scoring ---------------------------------------------------------------------------------------------


def _mcq(part):
    return {
        "part_id": part,
        "purpose": "check",
        "options": {"A": {"id": "correct", "text": "right"}, "B": {"id": "m1", "text": "wrong"}},
    }


def test_mcq_answers_are_checked(student, part):
    with pytest.raises(ValueError, match="choice"):
        learner.score_answer({"part_id": part, "type": "mcq"}, _mcq(part))
    with pytest.raises(ValueError, match="not an option"):
        learner.score_answer({"part_id": part, "type": "mcq", "choice": "Z"}, _mcq(part))
    with pytest.raises(learner.LostQuestion):
        learner.score_answer({"part_id": part, "type": "mcq", "choice": "A"}, None)
    right = learner.score_answer({"part_id": part, "type": "mcq", "choice": "a"}, _mcq(part))
    wrong = learner.score_answer({"part_id": part, "type": "mcq", "choice": "B"}, _mcq(part))
    assert right["score"] == 1.0 and right["correct"] and wrong["score"] == 0.0 and wrong["misconception_ids"] == ["m1"]


def test_prequestion_and_verify_answers_are_checked(student, part):
    with pytest.raises(ValueError, match="correct"):
        learner.score_answer({"part_id": part, "type": "prequestion"})
    with pytest.raises(ValueError):
        learner.score_answer({"part_id": part, "type": "prequestion", "correct": False, "picked_misconception_id": "no_such_id"})
    ok = learner.score_answer({"part_id": part, "type": "prequestion", "correct": True})
    assert ok["score"] == 1.0
    with pytest.raises(ValueError, match="verify"):
        learner.score_answer({"part_id": part, "type": "ail_task"})


def test_open_answers_are_scored_against_the_points(student, part):
    points = learner.score_answer({"part_id": part, "type": "explain_back", "points_met": []})
    assert points["score"] == 0.0
    with pytest.raises(ValueError):
        learner.score_answer({"part_id": "no_such_part", "type": "explain_back"})
    with pytest.raises(ValueError):
        learner.score_answer({"part_id": part, "type": "explain_back", "points_met": ["not_a_point"]})
    with pytest.raises(ValueError):
        learner.score_answer({"part_id": part, "type": "explain_back", "misconception_ids": ["no_such_id"]})


# --- small helpers -----------------------------------------------------------------------------------------------


def test_the_confidence_and_find_error_switches_follow_the_environment(monkeypatch):
    monkeypatch.setenv("EDUX_CONFIDENCE", "1")
    monkeypatch.setenv("EDUX_FIND_ERROR", "0")
    assert learner.confidence_on() is True and learner.find_error_on() is False


def test_rebuild_all_replays_every_student(student, part):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    counts = learner.rebuild_all()
    assert counts[student["id"]] >= 1
