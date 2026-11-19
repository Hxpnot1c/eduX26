"""Decision 0028: after any multiple-choice question, the next questions.min_open_between_mcq questions are open
(written) ones, unless the student is fatigued or rushing."""

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from edux import context_blocks, graph, learner, plan, service

PART = "ped_formula"
LABELS = {"question_depth": "mechanism", "engagement": "active"}


class Session:
    """Drives tutor_turn for one student, answering whatever was asked correctly (or not), three minutes apart."""

    def __init__(self, student, part=PART):
        self.student, self.part = student, part
        self.t = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=3)
        self.out: dict = {}
        self.kinds: list[str] = []

    def turn(self, message, answer=None, gap=timedelta(minutes=3), **labels):
        self.t += gap
        self.out = service.tutor_turn(
            learner.get_student(self.student["id"]),
            message,
            {**LABELS, **labels},
            node_ids=[self.part],
            answer=answer,
            at=self.t.isoformat(),
        )
        assert self.out.get("ok"), self.out
        kind = plan.counts_as(plan.asking_step(service._last_plan(self.student["id"])["plan"]))
        if kind:
            self.kinds.append(kind)
        return self.out

    def asking(self):
        return plan.asking_step(service._last_plan(self.student["id"])["plan"])

    def answer(self, right=True, misconceptions=None):
        last, step = service._last_plan(self.student["id"]), self.asking()
        if step["move"] == "ask_mcq":
            want = (lambda o: o["id"] == "correct") if right else (lambda o: o["id"] not in ("correct", "extra"))
            letter = next(k for k, o in sorted(last["mcq"]["options"].items()) if want(o))
            ans = {"part_id": step["part_id"], "type": step["data"]["answer_type"], "choice": letter}
        else:
            letters = [p["id"] for p in self.out["score_next"].get(step["part_id"], [])] if right else []
            ans = {"part_id": step["part_id"], "type": step["data"]["answer_type"], "points_met": letters}
            if misconceptions:
                ans["misconception_ids"] = misconceptions
        return self.turn("my answer", ans)


def _gap():
    return service.question_gap()


def test_after_every_multiple_choice_question_the_next_two_are_open(course):
    for part in [p for p in learner.all_parts() if not graph.is_literacy(p)][:6]:
        s = Session(learner.add_student(f"S-{part}", course), part)
        s.turn("Teach me this")
        for i in range(12):
            if s.asking() is None:
                break
            s.answer(right=i % 3 != 1)
        for i, kind in enumerate(s.kinds):
            if kind == "mcq":
                assert s.kinds[i + 1 : i + 1 + _gap()] == ["open"] * len(s.kinds[i + 1 : i + 1 + _gap()]), (part, s.kinds)
        assert "open" in s.kinds, (part, s.kinds)


def test_a_check_after_a_multiple_choice_question_is_asked_open_on_the_same_point(student):
    s = Session(student)
    s.turn("Teach me the PED formula")
    assert s.asking()["move"] == "ask_mcq"
    s.answer()
    step = s.asking()
    assert step["move"] == "explain_back" and step["key"] == "explain_back_check" and step["data"]["purpose"] == "check"
    assert step["data"]["point_id"] and "options" not in step["data"]
    assert [p["id"] for p in s.out["score_next"][PART]] and len(s.out["score_next"][PART]) == 1  # its own letter only
    public = next(p for p in s.out["plan"] if p["move"] == "explain_back")
    assert "own words" in public["cue"] and "no options" in public["cue"]


def test_an_open_check_is_scored_on_its_point_and_goes_on_as_the_mcq_would(student):
    s = Session(student)
    s.turn("Teach me the PED formula")
    s.answer()
    point = s.asking()["data"]["point_id"]
    s.answer(right=False)  # wrong: feedback with the missing point, then a re-teach and the same point's check again
    row = (
        learner._conn()
        .execute("SELECT evidence_type, score, point_id FROM evidence_log WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student["id"],))
        .fetchone()
    )
    assert tuple(row) == ("explain_back", 0.0, point)
    moves = [p["move"] for p in s.out["plan"]]
    fb = s.out["plan"][0]
    assert moves[0] == "feedback" and fb["data"]["purpose"] == "check" and fb["data"]["correct"] is False and fb["data"]["missing"]
    assert "reteach" in moves and s.asking()["data"].get("point_id") == point  # the same point again, still open
    s.answer()  # right: the next point
    assert s.out["plan"][0]["data"]["correct"] is True
    nxt = s.asking()
    assert nxt["data"].get("point_id") != point or nxt["move"] == "explain_back"


def test_open_and_multiple_choice_conversions(course):
    turn = context_blocks.Turn(student={"id": "x"}, parts=[PART], message="", at=learner.now_iso(), limits={}, resolution={})
    turn.mcq_ok = False
    settings = service._settings()
    point = plan._points(PART)[0]
    check = plan.ask_mcq(turn, plan.question(PART, "check", point["point"], settings, point_id=point["id"]), {"index": 1})
    review = plan.ask_mcq(
        turn,
        plan.question(PART, "review", point["point"], settings, point_id=point["id"]),
        {"name": "PED", "mode": "transfer", "new_context": "cinema"},
    )
    prereq = plan.ask_mcq(turn, plan.question(PART, "prereq", point["point"], settings, point_id=point["id"]), {"name": "PED", "for": "x"})
    intuition = plan.ask_mcq(turn, plan.question(PART, "intuition", point["point"], settings, point_id=point["id"]))
    out = plan.open_instead(turn, [check])
    assert out[0]["key"] == "explain_back_check" and out[0]["data"]["index"] == 1 and out[0]["data"]["answer_type"] == "explain_back"
    r = plan.open_instead(turn, [review])[0]
    assert r["key"] == "explain_back_review" and r["data"]["answer_type"] == "review" and r["data"]["new_context"] == "cinema"
    assert "PED" in r["cue"] and point["point"] in r["cue"] and "new_context" in r["cue"]
    p = plan.open_instead(turn, [prereq])[0]
    assert p["key"] == "explain_back_check" and p["data"]["purpose"] == "prereq" and p["data"]["for"] == "x"
    assert plan.open_instead(turn, [intuition]) == []  # no open form: dropped
    turn.mcq_ok = True
    assert plan.open_instead(turn, [check, intuition]) == [check, intuition]


def test_an_open_review_is_recorded_as_a_review_on_its_point(student):
    s = Session(student)
    s.turn("Teach me the PED formula")
    s.answer()
    turn = context_blocks.Turn(student=student, parts=[PART], message="", at=learner.now_iso(), limits={}, resolution={})
    turn.mcq_ok = False
    settings = service._settings()
    point = plan._points(PART)[1]
    step = plan.open_instead(
        turn,
        [
            plan.ask_mcq(
                turn, plan.question(PART, "review", point["point"], settings, point_id=point["id"]), {"name": "PED", "mode": "recall"}
            )
        ],
    )[0]
    evidence = learner.score_answer({"part_id": PART, "type": "review", "points_met": [point["id"]]})
    scored = service._narrowed(evidence, [step])
    assert scored["score"] == 1.0 and scored["point_id"] == point["id"] and scored["purpose"] == "review" and scored["open_check"]


def test_the_count_and_when_multiple_choice_is_allowed(course):
    mcq = {"move": "ask_mcq", "part_id": PART, "data": {"answer_type": "mcq"}}
    open_ = {"move": "explain_back", "part_id": PART, "data": {"answer_type": "explain_back"}}
    reask = {"move": "reask", "part_id": PART, "data": {"answer_type": "explain_back", "asked": "explain_back"}}
    assert service._open_since_after(None, [open_]) is None  # no multiple-choice question yet: nothing to count from
    assert service._open_since_after(None, [mcq]) == 0 and service._open_since_after(0, [open_]) == 1
    assert service._open_since_after(1, [reask]) == 1 and service._open_since_after(1, []) == 1  # the same question again counts once
    assert service._mcq_ok(None, {}) and not service._mcq_ok(0, {}) and not service._mcq_ok(_gap() - 1, {}) and service._mcq_ok(_gap(), {})
    assert service._mcq_ok(0, {"session": {"state": "fatigued"}})  # fatigued or rushing: no gap


def test_while_rushing_multiple_choice_comes_without_the_gap(student, monkeypatch):
    monkeypatch.setenv("EDUX_CONFIDENCE", "0")
    s = Session(student)
    s.turn("Teach me the PED formula", words=1)
    for _ in range(3):  # quick one-word answers, faster than the question can be read: rushing mode
        step = s.asking()
        if step is None:
            break
        last = service._last_plan(student["id"])
        if step["move"] == "ask_mcq":
            letter = next(k for k, o in sorted(last["mcq"]["options"].items()) if o["id"] == "correct")
            ans = {"part_id": step["part_id"], "type": "mcq", "choice": letter}
        else:
            ans = {"part_id": step["part_id"], "type": step["data"]["answer_type"], "points_met": []}
        s.turn("x", ans, gap=timedelta(seconds=1), words=1)
    state = learner.session_state(student["id"], s.t.isoformat())
    assert state["fatigued"]
    s.turn("quiz me", choice="quiz", gap=timedelta(minutes=1))
    assert s.asking() and s.asking()["move"] == "ask_mcq"  # straight after an open one, allowed while rushing


def _opens_with_intuition(course, part):
    probe = Session(learner.add_student(f"probe-{part}", course), part)
    probe.turn("Teach me this")
    step = probe.asking()
    return bool(step and step["move"] == "ask_mcq" and step["data"].get("purpose") == "intuition")


def test_the_intuition_question_is_dropped_when_too_soon_and_teaching_starts(course):
    others = [p for p in learner.all_parts() if p != PART and not graph.is_literacy(p) and _opens_with_intuition(course, p)]
    if not others:
        pytest.skip("no other part opens with a pre-question in the example pack")
    s = Session(learner.add_student("S", course))
    s.turn("Teach me the PED formula")
    s.answer()  # a multiple-choice question: the next two must be open
    s.part = others[0]
    s.turn("Now teach me this")
    step = s.asking()
    assert step is None or step["move"] != "ask_mcq"
    assert "teach_point" in [p["move"] for p in s.out["plan"]] or (step and step["move"] == "explain_back")
    assert service._last_plan(s.student["id"])["points"][others[0]]["intuition_asked"] is True  # not asked later, mid-teaching


def test_a_wrong_idea_in_a_written_answer_is_recorded_and_corrected(student):
    s = Session(student)
    s.turn("Teach me the PED formula")
    s.answer()
    wrong = graph.misconceptions_for([PART])[0]["id"]
    s.answer(right=False, misconceptions=[wrong])
    held = (
        learner._conn()
        .execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?", (student["id"], wrong))
        .fetchone()
    )
    assert held and held["active"] == 1
    assert wrong in [m["id"] for m in s.out["plan"][0]["data"]["misconceptions"]]


def test_a_one_point_answer_straight_after_teaching_cannot_make_a_part_secure(student):
    sid = student["id"]
    t = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=2)
    point = plan._points(PART)[0]["id"]
    for i in range(8):
        learner.record_exchange(
            sid,
            [PART],
            "mechanism",
            "active",
            False,
            "worked_example",
            "try_first",
            None,
            ts=(t + timedelta(minutes=2 * i)).isoformat(),
            apply="now",
        )
        learner.record_evidence(
            sid, PART, "explain_back", 1.0, ts=(t + timedelta(minutes=2 * i, seconds=30)).isoformat(), apply="now", point_id=point
        )
    p = learner._conn().execute("SELECT p_known FROM part_state WHERE student_id = ? AND part_id = ?", (sid, PART)).fetchone()[0]
    assert p < service._settings().levels.secure


def test_a_gap_of_zero_turns_the_rule_off(student, monkeypatch):
    s0 = service._settings()
    off = dataclasses.replace(s0, questions=dataclasses.replace(s0.questions, min_open_between_mcq=0))
    monkeypatch.setattr(service, "_settings", lambda: off)
    s = Session(student)
    s.turn("Teach me the PED formula")
    s.answer()
    assert s.asking()["move"] == "ask_mcq"


def test_settings_refuse_a_negative_gap(tmp_path):
    from edux import settings as settings_module

    text = settings_module.SETTINGS_PATH.read_text().replace("min_open_between_mcq = 2 ", "min_open_between_mcq = -1 ")
    (tmp_path / "settings.toml").write_text(text)
    with pytest.raises(settings_module.SettingsError, match="min_open_between_mcq"):
        settings_module.load_settings(tmp_path / "settings.toml")


def test_the_environment_sets_the_gap(student, monkeypatch):
    monkeypatch.setenv("EDUX_QUESTION_GAP", "0")
    assert service.question_gap() == 0 and service._mcq_ok(0, {})
    s = Session(student)
    s.turn("Teach me the PED formula")
    s.answer()
    assert s.asking()["move"] == "ask_mcq"
    monkeypatch.setenv("EDUX_QUESTION_GAP", "3")
    assert service.question_gap() == 3 and not service._mcq_ok(2, {})
    monkeypatch.setenv("EDUX_QUESTION_GAP", "x")  # not a number: the setting
    assert service.question_gap() == service._settings().questions.min_open_between_mcq
