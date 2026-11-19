"""Step 05u: class assessments, in-chat reminders and study plans."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from edux import graph, learner, service

DAY = timedelta(days=1)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _day(n):
    return (_now() + n * DAY).date().isoformat()


@pytest.fixture()
def klass(course, student):
    class_id = learner.add_class("Class")
    learner.add_students_to_class(class_id, [student["id"]])
    return class_id


def _parts(node):
    return graph.parts_of(node)


def test_a_class_assessment_reaches_every_member_and_nobody_else(course, student, klass):
    other_member = learner.add_student("Member", course)
    outsider = learner.add_student("Outsider", course)
    learner.add_students_to_class(klass, [other_member["id"]])
    learner.add_class_assessment(klass, "Class test", "class_test", _day(10), _parts("ped"))
    for who, expected in ((student, 1), (other_member, 1), (outsider, 0)):
        assert len(learner.assessments(who["id"])) == expected
    assert learner.assessments(student["id"])[0]["scope"] == "class"


def test_class_assessments_count_in_priorities(student, klass):
    part = _parts("ped")[0]
    plain = learner.step_value(student["id"], part)["value"]
    learner.add_class_assessment(klass, "Mock", "mock", _day(4), _parts("ped"))
    found = learner.step_value(student["id"], part)
    assert found["value"] > plain and found["reason"]["name"] == "Mock"


def test_exactly_one_of_student_and_class_is_set(course, student, klass):
    conn = learner._conn()
    with pytest.raises(Exception):
        conn.execute(
            "INSERT INTO student_assessment (student_id, class_id, name, kind, date, part_ids, created_at) VALUES (?, ?, 'x', 'mock', ?, '[]', ?)",
            (student["id"], klass, _day(5), learner.now_iso()),
        )
    with pytest.raises(Exception):
        conn.execute(
            "INSERT INTO student_assessment (name, kind, date, part_ids, created_at) VALUES ('x', 'mock', ?, '[]', ?)",
            (_day(5), learner.now_iso()),
        )


def test_a_student_cannot_remove_a_class_assessment(student, klass):
    a_id = learner.add_class_assessment(klass, "Class test", "class_test", _day(10), _parts("ped"))
    out = service.update_profile(learner.get_student(student["id"]), remove_assessment=a_id)
    assert out["ok"] is False and "teacher" in out["error"]
    assert len(learner.assessments(student["id"])) == 1


def test_a_student_can_still_add_and_remove_their_own(student):
    me = learner.get_student(student["id"])
    out = service.update_profile(me, add_assessment={"name": "Mine", "kind": "written_assignment", "date": _day(9), "topics": ["PED"]})
    assert out["ok"] and out["profile"]["assessments"][0]["scope"] == "own"
    assert service.update_profile(me, remove_assessment=out["added"]["id"])["profile"]["assessments"] == []


def test_deleting_a_student_keeps_the_class_assessments(student, klass):
    learner.add_class_assessment(klass, "Class test", "class_test", _day(10), _parts("ped"))
    learner.delete_student(student["id"])
    assert learner._conn().execute("SELECT COUNT(*) FROM student_assessment WHERE class_id = ?", (klass,)).fetchone()[0] == 1


def test_bad_class_assessments_are_refused(course, klass):
    with pytest.raises(ValueError):
        learner.add_class_assessment(klass, "x", "exam", _day(5), [])
    with pytest.raises(ValueError):
        learner.add_class_assessment("nope", "x", "mock", _day(5), [])
    with pytest.raises(ValueError):
        learner.add_class_assessment(klass, "x", "mock", "not-a-date", [])


# --- reminders ---------------------------------------------------------------------------------------------


def test_only_assessments_within_seven_days_are_upcoming(student, klass):
    learner.add_class_assessment(klass, "Soon", "class_test", _day(3), _parts("ped"))
    learner.add_class_assessment(klass, "Later", "mock", _day(20), _parts("pes"))
    found = learner.upcoming(student["id"])
    assert [f["name"] for f in found] == ["Soon"] and found[0]["days_left"] == 3 and found[0]["kind"] == "class_test"


def test_the_reminder_appears_on_the_first_turn_of_a_session_only(student, klass):
    sid = student["id"]
    learner.add_class_assessment(klass, "Soon", "class_test", _day(3), _parts("ped"))
    first = service._reminder(sid, {"ts": None}, learner.now_iso(), True)
    assert first and first["items"][0]["name"] == "Soon" and "once" in first["cue"]
    recent = (_now() - timedelta(minutes=5)).isoformat(timespec="seconds")
    assert service._reminder(sid, {"ts": recent}, learner.now_iso(), True) is None  # the same session
    assert service._reminder(sid, {"ts": None}, learner.now_iso(), False) is None  # style not being sent: not a new session
    long_ago = (_now() - 3 * DAY).isoformat(timespec="seconds")
    assert service._reminder(sid, {"ts": long_ago}, learner.now_iso(), True)  # a new session again


def test_no_reminder_when_nothing_is_due_or_the_student_switched_them_off(student, klass):
    sid = student["id"]
    assert service._reminder(sid, {"ts": None}, learner.now_iso(), True) is None
    learner.add_class_assessment(klass, "Soon", "class_test", _day(3), _parts("ped"))
    out = service.update_profile(learner.get_student(sid), reminders=False)
    assert out["profile"]["reminders"] is False
    assert service._reminder(sid, {"ts": None}, learner.now_iso(), True) is None
    assert service.update_profile(learner.get_student(sid), reminders=True)["profile"]["reminders"] is True
    assert service._reminder(sid, {"ts": None}, learner.now_iso(), True)


# --- study plans -------------------------------------------------------------------------------------------


def test_the_plan_covers_the_right_parts_spaced_from_today_to_the_due_date(student, klass):
    sid = student["id"]
    parts = _parts("elasticities")
    aid = learner.add_class_assessment(klass, "Mock", "mock", _day(14), parts)
    plan = learner.study_plan(sid, aid)
    assert plan["ok"] and plan["sessions_per_week"] == 3
    dates = [s["date"] for s in plan["sessions"]]
    assert dates == sorted(dates) and dates[0] == _day(0) and dates[-1] < _day(14)
    assert len(plan["sessions"]) == 6  # 14 days at 3 a week
    planned = {p["id"] for s in plan["sessions"] for p in s["parts"]}
    assert planned <= set(parts) and len(planned) > 1
    assert plan["sessions"][-1]["kind"] == "mixed practice"


def test_the_weakest_part_comes_first(student, klass):
    sid = student["id"]
    parts = _parts("elasticities")
    strong, weak = parts[0], parts[-1]
    for i in range(5):
        learner.record_evidence(
            sid, strong, "mcq_check", 1.0, ts=(_now() - (1 + 0.1 * i) * DAY).isoformat(timespec="seconds"), apply="now", n_options=4
        )
    learner.record_evidence(sid, weak, "mcq_check", 0.0, ts=(_now() - DAY).isoformat(timespec="seconds"), apply="now", n_options=4)
    plan = learner.study_plan(sid, learner.add_class_assessment(klass, "Test", "class_test", _day(10), parts))
    assert plan["sessions"][0]["parts"][0]["id"] != strong


def test_the_student_can_choose_how_many_sessions_a_week(student, klass):
    aid = learner.add_class_assessment(klass, "Mock", "mock", _day(14), _parts("elasticities"))
    assert len(learner.study_plan(student["id"], aid, 5)["sessions"]) == 10
    assert learner.study_plan(student["id"], aid, 9)["ok"] is False


def test_with_no_id_the_soonest_assessment_is_used_and_none_gives_an_error(student, klass):
    assert learner.study_plan(student["id"])["ok"] is False
    learner.add_class_assessment(klass, "Later", "mock", _day(20), _parts("pes"))
    learner.add_class_assessment(klass, "Sooner", "class_test", _day(6), _parts("ped"))
    assert learner.study_plan(student["id"])["assessment"]["name"] == "Sooner"
    assert learner.study_plan(student["id"], 99999)["ok"] is False


def test_a_written_assignment_gets_dated_stages_that_say_what_to_do_not_what_to_write(student, klass):
    aid = learner.add_class_assessment(klass, "Essay", "written_assignment", _day(16), _parts("elasticities"))
    plan = learner.study_plan(student["id"], aid)
    assert [s["stage"] for s in plan["stages"]] == ["knowledge", "application", "analysis", "evaluation"]
    dates = [s["date"] for s in plan["stages"]]
    assert dates == sorted(set(dates)) and "sessions" not in plan
    text = json.dumps(plan).lower()
    assert "write it yourself" in text and "malpractice" in text
    assert not any(w in text for w in ("price elasticity of demand is", "the answer is"))


def test_a_long_plan_stays_within_the_result_budget_and_keeps_the_mixed_practice_session(student, klass):
    aid = learner.add_class_assessment(klass, "Final mock", "mock", _day(120), _parts("elasticities") + _parts("indirect_taxes"))
    out = service.plan_study(learner.get_student(student["id"]), aid, 7)
    assert service.result_size(out) <= service._settings().results.max_chars
    assert out["sessions"][-1]["kind"] == "mixed practice" and out.get("more_sessions", 0) > 0
