"""Step 05z (audit item C7): "how sure are you?" after an answer to a check, and the calibration line."""

import dataclasses

import pytest

from edux import learner, service

PART = "ped_formula"
LABELS = {"question_depth": "mechanism", "engagement": "active"}


def _turn(student, message, answer=None, **labels):
    return service.tutor_turn(learner.get_student(student["id"]), message, {**LABELS, **labels}, node_ids=[PART], answer=answer)


def _right_letter(student):
    mcq = service._last_plan(student["id"])["mcq"]
    return next(k for k, o in sorted(mcq["options"].items()) if o["id"] == "correct")


def _wrong_letter(student):
    mcq = service._last_plan(student["id"])["mcq"]
    return next(k for k, o in sorted(mcq["options"].items()) if o["id"] not in ("correct", "extra"))


def _to_a_check(student):
    """Play the point-by-point loop up to the first check question (answering any pre-question on the way)."""
    out = _turn(student, "Teach me the PED formula")
    for _ in range(4):
        asking = next((s for s in out["plan"] if s["move"] == "ask_mcq"), None)
        if asking and asking["data"].get("purpose") == "check":
            return out
        if asking:
            letter = _right_letter(student)
            out = _turn(student, letter, answer={"part_id": asking["part_id"], "type": asking["data"]["answer_type"], "choice": letter})
        else:
            break
    pytest.skip("no check question reached in the example pack")


def _answer_check(student, right=True):
    asking = next(s for s in service._last_plan(student["id"])["plan"] if s["move"] == "ask_mcq")
    letter = _right_letter(student) if right else _wrong_letter(student)
    return _turn(student, letter, answer={"part_id": asking["part_id"], "type": "mcq", "choice": letter})


def test_after_a_check_answer_the_reply_asks_how_sure_and_keeps_the_feedback_back(student):
    _to_a_check(student)
    out = _answer_check(student)
    assert [s["move"] for s in out["plan"]] == ["say_line"] and out["score_next"] == {}
    assert "how sure" in out["plan"][0]["data"]["line"].lower() and "skip" in out["plan"][0]["data"]["line"].lower()
    held = service._last_plan(student["id"])
    assert held["confidence_for"]["part_id"] and any(s["move"] in ("feedback", "teach_point", "explain_back", "ask_mcq") for s in held["plan"])
    assert learner.evidence_ids_of_exchange(held["confidence_for"]["exchange_id"])        # the answer was recorded and scored at once


def test_the_reply_to_how_sure_delivers_the_held_plan_and_stores_the_rating(student):
    _to_a_check(student)
    _answer_check(student)
    out = _turn(student, "fairly sure", confidence="fairly_sure")
    moves = [s["move"] for s in out["plan"]]
    assert "say_line" not in moves and moves[0] == "feedback"
    row = learner._conn().execute("SELECT level FROM confidence_log WHERE student_id = ?", (student["id"],)).fetchone()
    assert row["level"] == "fairly_sure"
    assert service._last_plan(student["id"])["confidence_for"] is None


def test_skipping_stores_a_skip_and_costs_nothing(student):
    _to_a_check(student)
    _answer_check(student)
    out = _turn(student, "just tell me", confidence="none")
    assert "say_line" not in [s["move"] for s in out["plan"]]
    assert learner._conn().execute("SELECT level FROM confidence_log").fetchone()["level"] == "skipped"
    assert learner.calibration(student["id"]) == {}


def test_the_rating_never_changes_what_the_model_thinks_they_know(course):
    results = []
    for said in ("certain", "guess"):
        s = learner.add_student(f"S{said}", course)
        _to_a_check(s)
        _answer_check(s, right=False)
        _turn(s, said, confidence=said)
        results.append([tuple(r) for r in learner._conn().execute(
            "SELECT part_id, p_known FROM part_state WHERE student_id = ? ORDER BY part_id", (s["id"],))])
    # identical to within the second or so between the two students' timestamps (forgetting decay), not because of the rating
    assert [r[0] for r in results[0]] == [r[0] for r in results[1]]
    assert [r[1] for r in results[0]] == pytest.approx([r[1] for r in results[1]], abs=1e-4)


def test_a_confidence_sent_with_the_answer_is_stored_without_asking(student):
    _to_a_check(student)
    asking = next(s for s in service._last_plan(student["id"])["plan"] if s["move"] == "ask_mcq")
    letter = _right_letter(student)
    out = _turn(student, letter, answer={"part_id": asking["part_id"], "type": "mcq", "choice": letter}, confidence="certain")
    assert "say_line" not in [s["move"] for s in out["plan"]]
    assert learner._conn().execute("SELECT level FROM confidence_log").fetchone()["level"] == "certain"


def test_it_is_not_asked_after_a_pre_question_or_on_ordinary_chat(student):
    out = _turn(student, "Teach me the PED formula")
    asking = next((s for s in out["plan"] if s["move"] == "ask_mcq"), None)
    if asking is None or asking["data"].get("purpose") != "intuition":
        pytest.skip("no pre-question in this run")
    letter = _right_letter(student)
    after = _turn(student, letter, answer={"part_id": asking["part_id"], "type": asking["data"]["answer_type"], "choice": letter})
    assert "say_line" not in [s["move"] for s in after["plan"]]
    assert "say_line" not in [s["move"] for s in _turn(student, "what is elasticity?")["plan"]]


def test_two_skips_in_a_row_stop_the_asking_for_the_session(student):
    sid = student["id"]
    for _ in range(2):
        e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
        learner.record_confidence(sid, e, "skipped")
    evidence = {"purpose": "check"}
    blocks = {}
    assert service._confidence_due(sid, evidence, {"x": 1}, {}, blocks, "none", learner.now_iso()) is False
    e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
    learner.record_confidence(sid, e, "certain")                  # an answer breaks the streak
    assert service._confidence_due(sid, evidence, {"x": 1}, {}, blocks, "none", learner.now_iso()) is True


def test_at_most_six_asks_a_session_and_none_while_rushing_or_off(student, monkeypatch):
    sid = student["id"]
    for _ in range(6):
        e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
        learner.record_confidence(sid, e, "certain")
    args = (sid, {"purpose": "check"}, {"x": 1}, {}, {}, "none", learner.now_iso())
    assert service._confidence_due(*args) is False
    s = service._settings()
    off = dataclasses.replace(s, confidence=dataclasses.replace(s.confidence, enabled=False))
    monkeypatch.setattr(service, "_settings", lambda: off)
    assert service._confidence_due(sid, {"purpose": "check"}, {"x": 1}, {}, {}, "none", learner.now_iso()) is False


def test_the_calibration_line_appears_only_after_five_rated_answers_in_a_group(student):
    sid = student["id"]
    for i in range(4):
        e = learner.record_evidence(sid, PART, "mcq_check", float(i < 3), apply="now", n_options=4)
        learner.record_confidence(sid, e, "certain")
    assert service._calibration(sid, learner.now_iso()) is None
    e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
    learner.record_confidence(sid, e, "certain")
    found = service._calibration(sid, learner.now_iso())
    assert found["groups"]["certain"] == {"right": 4, "n": 5} and found["line"] == "When you were certain, you were right 4 of 5 times"


def test_skipped_asks_are_not_counted_and_a_line_has_one_part_per_group(student):
    sid = student["id"]
    for level, right in (("guess", 2), ("certain", 5)):
        for i in range(5):
            e = learner.record_evidence(sid, PART, "mcq_check", float(i < right), apply="now", n_options=4)
            learner.record_confidence(sid, e, level)
    for _ in range(3):
        e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
        learner.record_confidence(sid, e, "skipped")
    line = service._calibration(sid, learner.now_iso())["line"]
    assert line == "When you were certain, you were right 5 of 5 times; When you were guessing, you were right 2 of 5 times"


def test_the_progress_view_carries_the_calibration_block_when_there_is_one(student):
    sid = student["id"]
    for i in range(5):
        e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
        learner.record_confidence(sid, e, "certain")
    assert "calibration" in service.my_progress(learner.get_student(sid))
    other = learner.add_student("Other", service._settings() and learner._conn().execute("SELECT course_id FROM student LIMIT 1").fetchone()[0])
    assert "calibration" not in service.my_progress(learner.get_student(other["id"]))


def test_an_unanswered_ask_is_dropped_after_the_session_gap(student):
    _to_a_check(student)
    _answer_check(student)
    out = service.tutor_turn(learner.get_student(student["id"]), "hello again", LABELS, node_ids=[PART],
                             at=(learner.parse_ts(learner.now_iso()).replace(microsecond=0) + __import__("datetime").timedelta(hours=5)).isoformat())
    assert learner._conn().execute("SELECT COUNT(*) FROM confidence_log").fetchone()[0] == 0
    assert "say_line" not in [s["move"] for s in out["plan"]]


def test_deleting_a_student_removes_their_ratings(student):
    sid = student["id"]
    e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
    learner.record_confidence(sid, e, "certain")
    learner.delete_student(sid)
    assert learner._conn().execute("SELECT COUNT(*) FROM confidence_log WHERE student_id = ?", (sid,)).fetchone()[0] == 0


def test_a_bad_level_is_refused(student):
    e = learner.record_evidence(student["id"], PART, "mcq_check", 1.0, apply="now", n_options=4)
    with pytest.raises(ValueError):
        learner.record_confidence(student["id"], e, "very sure")


def test_the_environment_switches_the_question_on_and_off(student, monkeypatch):
    evidence = {"purpose": "check"}
    args = (student["id"], evidence, {"x": 1}, {}, {}, "none", learner.now_iso())
    assert service._confidence_due(*args) is True
    monkeypatch.setenv("EDUX_CONFIDENCE", "0")
    assert learner.confidence_on() is False and service._confidence_due(*args) is False
    monkeypatch.setenv("EDUX_CONFIDENCE", "1")
    assert service._confidence_due(*args) is True
