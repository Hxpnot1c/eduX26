"""Step 05z and decision 0027: "how sure are you?" only after rapid guesses on checks in a row, once a session; the
rushing break offer waits until rushing continues; and the calibration line."""

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from edux import learner, service

PART = "ped_formula"
LABELS = {"question_depth": "mechanism", "engagement": "active", "words": 1}
SLOW, FAST = timedelta(minutes=3), timedelta(seconds=1)  # a 1-second, one-word answer is faster than any question can be read


class Clock:
    def __init__(self, start=None):
        self.t = start or datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=3)

    def step(self, gap):
        self.t += gap
        return self.t.isoformat()


@pytest.fixture()
def clock():
    return Clock()


@pytest.fixture(autouse=True)
def mcq_every_turn(monkeypatch):
    """These tests are about confidence, so multiple-choice checks may follow each other (no question-mix gap, 0028)."""
    s = service._settings()
    gapless = dataclasses.replace(s, questions=dataclasses.replace(s.questions, min_open_between_mcq=0))
    monkeypatch.setattr(service, "_settings", lambda: gapless)


def _turn(student, message, clock, gap=SLOW, answer=None, **labels):
    return service.tutor_turn(
        learner.get_student(student["id"]), message, {**LABELS, **labels}, node_ids=[PART], answer=answer, at=clock.step(gap)
    )


def _letter(student, right=True):
    mcq = service._last_plan(student["id"])["mcq"]
    want = (lambda o: o["id"] == "correct") if right else (lambda o: o["id"] not in ("correct", "extra"))
    return next(k for k, o in sorted(mcq["options"].items()) if want(o))


def _asking(student):
    return next((s for s in service._last_plan(student["id"])["plan"] if s["move"] == "ask_mcq"), None)


def _to_a_check(student, clock):
    """Play the point-by-point loop up to a check question, answering any pre-question slowly on the way."""
    out = _turn(student, "Teach me the PED formula", clock)
    for _ in range(4):
        asking = _asking(student)
        if asking and asking["data"].get("purpose") == "check":
            return out
        if asking is None:
            break
        letter = _letter(student)
        out = _turn(student, letter, clock, answer={"part_id": asking["part_id"], "type": asking["data"]["answer_type"], "choice": letter})
    pytest.skip("no check question reached in the example pack")


def _answer_check(student, clock, gap, right=True, **labels):
    asking = _asking(student)
    assert asking and asking["data"].get("purpose") in ("check", "review", "prereq"), asking
    letter = _letter(student, right)
    return _turn(student, letter, clock, gap, answer={"part_id": asking["part_id"], "type": "mcq", "choice": letter}, **labels)


def _moves(out):
    return [s["move"] for s in out["plan"]]


def _two_rapid_checks(student, clock):
    _to_a_check(student, clock)
    first = _answer_check(student, clock, FAST)
    assert "say_line" not in _moves(first)  # one rapid guess is not enough
    if _asking(student) is None or _asking(student)["data"].get("purpose") != "check":
        pytest.skip("no second check straight after the first in the example pack")
    return _answer_check(student, clock, FAST)


def test_an_ordinary_check_answer_is_never_asked_how_sure(student, clock):
    _to_a_check(student, clock)
    out = _answer_check(student, clock, SLOW)
    assert "say_line" not in _moves(out) and service._last_plan(student["id"])["confidence_for"] is None


def test_the_second_rapid_check_in_a_row_asks_how_sure_and_holds_the_break_offer(student, clock):
    out = _two_rapid_checks(student, clock)
    assert _moves(out) == ["say_line"] and out["score_next"] == {}
    assert "how sure" in out["plan"][0]["data"]["line"].lower() and "skip" in out["plan"][0]["data"]["line"].lower()
    held = service._last_plan(student["id"])
    assert held["confidence_for"]["part_id"] and learner.evidence_ids_of_exchange(held["confidence_for"]["exchange_id"])
    assert learner.session_state(student["id"], clock.t.isoformat())["fatigue_reason"] == "rushing"  # rushing mode is unchanged
    assert "offer_choice" not in [s["move"] for s in held["plan"]]  # the break offer waits
    assert held["rush_waits"] and "fatigued" not in held["offered"]


def test_the_reply_delivers_the_held_plan_without_the_break_offer_and_stores_the_rating(student, clock):
    _two_rapid_checks(student, clock)
    out = _turn(student, "fairly sure", clock, confidence="fairly_sure")
    assert _moves(out)[0] == "feedback" and "say_line" not in _moves(out) and "offer_choice" not in _moves(out)
    row = learner._conn().execute("SELECT level FROM confidence_log WHERE student_id = ?", (student["id"],)).fetchone()
    assert row["level"] == "fairly_sure"
    assert service._last_plan(student["id"])["confidence_for"] is None


def _explain_back(student, clock, gap):
    asking = next((s for s in service._last_plan(student["id"])["plan"] if s["move"] == "explain_back"), None)
    if asking is None:
        pytest.skip("the held plan asks no explain-back")
    return _turn(student, "my answer", clock, gap, answer={"part_id": asking["part_id"], "type": "explain_back", "points_met": ["a"]})


def test_a_slower_answer_after_the_question_keeps_the_break_offer_waiting(student, clock):
    _two_rapid_checks(student, clock)
    _turn(student, "fairly sure", clock, confidence="fairly_sure")
    out = _explain_back(student, clock, SLOW)
    assert "offer_choice" not in _moves(out) and service._last_plan(student["id"])["rush_waits"]


def test_the_break_offer_comes_when_rushing_continues(student, clock):
    _two_rapid_checks(student, clock)
    _turn(student, "fairly sure", clock, confidence="fairly_sure")
    out = _explain_back(student, clock, FAST)
    offer = next(s for s in out["plan"] if s["move"] == "offer_choice")
    assert offer["data"]["reason"] == "fatigued" and "say_line" not in _moves(out)
    assert service._last_plan(student["id"])["rush_waits"] is None


def test_rapid_guesses_not_in_a_row_get_the_break_offer_as_before_and_no_question(student, clock):
    _to_a_check(student, clock)
    _answer_check(student, clock, FAST)
    _answer_check(student, clock, SLOW, right=False)  # a slower check answer resets the run; wrong, so the check comes again
    out = _answer_check(student, clock, FAST)
    assert "say_line" not in _moves(out)
    assert any(s["move"] == "offer_choice" and s["data"]["reason"] == "fatigued" for s in out["plan"])


def test_skipping_stores_a_skip_and_costs_nothing(student, clock):
    _two_rapid_checks(student, clock)
    out = _turn(student, "just tell me", clock, confidence="none")
    assert "say_line" not in _moves(out)
    assert learner._conn().execute("SELECT level FROM confidence_log").fetchone()["level"] == "skipped"
    assert learner.calibration(student["id"]) == {}


def test_the_rating_never_changes_what_the_model_thinks_they_know(course):
    results = []
    start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=3)
    for said in ("certain", "guess"):
        s, clock = learner.add_student(f"S{said}", course), Clock(start)
        _two_rapid_checks(s, clock)
        _turn(s, said, clock, confidence=said)
        results.append(
            [
                tuple(r)
                for r in learner._conn().execute(
                    "SELECT part_id, p_known FROM part_state WHERE student_id = ? ORDER BY part_id", (s["id"],)
                )
            ]
        )
    assert results[0] == results[1]  # same answers at the same times: identical, whatever the rating


def test_a_confidence_sent_with_the_answer_is_stored_without_asking(student, clock):
    _to_a_check(student, clock)
    out = _answer_check(student, clock, SLOW, confidence="certain")
    assert "say_line" not in _moves(out)
    assert learner._conn().execute("SELECT level FROM confidence_log").fetchone()["level"] == "certain"


def test_it_is_not_asked_after_a_pre_question_or_on_ordinary_chat(student, clock):
    out = _turn(student, "Teach me the PED formula", clock)
    asking = next((s for s in out["plan"] if s["move"] == "ask_mcq"), None)
    if asking is None or asking["data"].get("purpose") != "intuition":
        pytest.skip("no pre-question in this run")
    letter = _letter(student)
    after = _turn(
        student, letter, clock, FAST, answer={"part_id": asking["part_id"], "type": asking["data"]["answer_type"], "choice": letter}
    )
    assert "say_line" not in _moves(after)
    assert "say_line" not in _moves(_turn(student, "what is elasticity?", clock, FAST))


def _due(sid, at, run=2):
    return service._confidence_due(sid, {"purpose": "check"}, {"x": 1}, {}, {}, "none", at, run)


def test_only_after_rapid_checks_in_a_row(student):
    at = learner.now_iso()
    assert _due(student["id"], at, 0) is False and _due(student["id"], at, 1) is False and _due(student["id"], at, 2) is True
    assert service._confidence_due(student["id"], {"purpose": "intuition"}, {"x": 1}, {}, {}, "none", at, 2) is False
    assert service._confidence_due(student["id"], {"purpose": "check"}, {"x": 1}, {}, {}, "just_show_me", at, 2) is False


def test_at_most_once_a_session_and_again_next_session(student):
    sid, start = student["id"], datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=2)
    e = learner.record_evidence(sid, PART, "mcq_check", 1.0, ts=start.isoformat(), apply="now", n_options=4)
    learner.record_confidence(sid, e, "certain", (start + timedelta(seconds=5)).isoformat())
    assert _due(sid, (start + timedelta(minutes=1)).isoformat()) is False
    later = start + timedelta(days=1)
    learner.record_evidence(sid, PART, "mcq_check", 1.0, ts=later.isoformat(), apply="now", n_options=4)
    assert _due(sid, (later + timedelta(minutes=1)).isoformat()) is True


def test_two_skipped_asks_in_a_row_across_sessions_stop_it_for_good_and_a_rating_breaks_the_streak(student):
    sid, start = student["id"], datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=5)

    def ask(day, level):
        t = start + timedelta(days=day)
        e = learner.record_evidence(sid, PART, "mcq_check", 1.0, ts=t.isoformat(), apply="now", n_options=4)
        learner.record_confidence(sid, e, level, (t + timedelta(seconds=5)).isoformat())

    def due_next_day(day):
        t = start + timedelta(days=day + 1)
        learner.record_evidence(sid, PART, "mcq_check", 1.0, ts=t.isoformat(), apply="now", n_options=4)
        return _due(sid, (t + timedelta(minutes=1)).isoformat())

    ask(0, "skipped")
    assert due_next_day(0) is True  # one skip is not a streak
    ask(2, "skipped")
    assert due_next_day(2) is False  # two in a row, in two sessions: no more asks
    ask(4, "certain")  # a rating sent with an answer breaks the streak
    assert due_next_day(4) is True


def test_one_ask_on_a_multi_point_answer_counts_once(student):
    sid = student["id"]
    e = learner.record_evidence(sid, PART, "mcq_check", 1.0, apply="now", n_options=4)
    e += learner.record_evidence(sid, PART, "explain_back", 1.0, apply="now")
    learner.record_confidence(sid, e, "skipped")
    assert learner.confidence_asks(sid) == {"asked": 1, "skips_in_a_row": 1}


def test_the_break_offer_never_waits_in_long_session_time():
    rapid = {"session": "s", "n": 2}
    rushing = {"session": {"state": "fatigued", "reason": "rushing", "minutes": 10}}
    assert service._rush_offer_waits({}, rushing, rapid, True, True, False) is True
    assert service._rush_offer_waits({"rush_waits": "s"}, rushing, rapid, False, False, False) is True
    assert service._rush_offer_waits({"rush_waits": "s"}, rushing, rapid, False, True, False) is False  # rushing continues
    long = {"session": {"state": "fatigued", "reason": "rushing", "minutes": 60}}
    assert service._rush_offer_waits({"rush_waits": "s"}, long, rapid, True, False, False) is False
    tired = {"session": {"state": "fatigued", "reason": "long_session", "minutes": 60}}
    assert service._rush_offer_waits({}, tired, rapid, True, False, False) is False


def test_settings_refuse_an_after_rapid_below_one(tmp_path):
    from edux import settings as settings_module

    text = settings_module.SETTINGS_PATH.read_text().replace("after_rapid = 2 ", "after_rapid = 0 ")
    (tmp_path / "settings.toml").write_text(text)
    with pytest.raises(settings_module.SettingsError, match="after_rapid"):
        settings_module.load_settings(tmp_path / "settings.toml")


def test_an_unanswered_ask_is_dropped_after_the_session_gap(student, clock):
    _two_rapid_checks(student, clock)
    out = _turn(student, "hello again", clock, timedelta(hours=5))
    assert learner._conn().execute("SELECT COUNT(*) FROM confidence_log").fetchone()[0] == 0
    assert "say_line" not in _moves(out)


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
    other = learner.add_student(
        "Other", service._settings() and learner._conn().execute("SELECT course_id FROM student LIMIT 1").fetchone()[0]
    )
    assert "calibration" not in service.my_progress(learner.get_student(other["id"]))


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
    at = learner.now_iso()
    assert _due(student["id"], at) is True
    monkeypatch.setenv("EDUX_CONFIDENCE", "0")
    assert learner.confidence_on() is False and _due(student["id"], at) is False
    monkeypatch.setenv("EDUX_CONFIDENCE", "1")
    assert _due(student["id"], at) is True
    s = service._settings()
    off = dataclasses.replace(s, confidence=dataclasses.replace(s.confidence, enabled=False))
    monkeypatch.delenv("EDUX_CONFIDENCE")
    monkeypatch.setattr(service, "_settings", lambda: off)
    monkeypatch.setattr(learner, "_settings", lambda: off)
    assert _due(student["id"], at) is False
