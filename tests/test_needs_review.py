"""Decision 0025: "needs review" is shown for a part answered right before that has faded below new. A display state
only: level() still reads the number."""

from datetime import datetime, timedelta, timezone

from edux import graph, learner, service
from edux.web import views

DAY = timedelta(days=1)
MIN = 5


def _ago(days):
    return (datetime.now(timezone.utc).replace(microsecond=0) - days * DAY).isoformat(timespec="seconds")


def _right_long_ago(student_id, part, days=60):
    learner.record_evidence(student_id, part, "mcq_check", 1.0, ts=_ago(days), apply="now", n_options=4)


def _course_parts():
    return [p for p in learner.all_parts() if not graph.is_literacy(p)]


def test_never_answered_reads_new(student, part):
    assert learner.shown_level(student["id"], part) == "new"


def test_covered_and_never_answered_reads_taught_in_class(student, part):
    class_id = learner.add_class("C")
    learner.add_students_to_class(class_id, [student["id"]])
    learner.set_class_coverage(class_id, [graph.concept_of(part) or part], _ago(20)[:10])
    assert learner.shown_level(student["id"], part) == "taught_in_class"


def test_right_once_then_faded_below_new_reads_needs_review(student, part):
    sid = student["id"]
    _right_long_ago(sid, part)
    p = learner.part_p(sid, part)
    assert p < learner._settings().levels.new and learner.level(p) == "new"  # the number still says new...
    assert learner.shown_level(sid, part) == "needs_review"  # ...the display says what happened
    assert learner.shown_rollup(sid, part) == "needs_review"  # the every-part tree reads a part the same way


def test_right_recently_reads_its_level(student, part):
    sid = student["id"]
    learner.record_evidence(sid, part, "mcq_check", 1.0, apply="now", n_options=4)
    assert learner.shown_level(sid, part) == learner.level(learner.part_p(sid, part)) != "needs_review"


def test_never_right_and_low_reads_new(student, part):
    sid = student["id"]
    learner.record_evidence(sid, part, "explain_back", 0.0, ts=_ago(30), apply="now")
    learner.record_evidence(sid, part, "mcq_check", 0.0, ts=_ago(29), apply="now", n_options=4)
    assert learner.shown_level(sid, part) == "new"


def test_ai_literacy_parts_never_read_needs_review(student):
    sid = student["id"]
    learner.record_evidence(sid, learner.AIL_VERIFY, "ail_task", 1.0, ts=_ago(60), apply="now")
    assert learner.shown_level(sid, learner.AIL_VERIFY) == "new"


def test_the_progress_tool_and_the_student_page_show_it(student, part):
    sid = student["id"]
    _right_long_ago(sid, part)
    full = service.my_progress(learner.get_student(sid), include_parts=True)

    def parts(nodes):
        for n in nodes:
            yield n
            yield from parts(n.get("children", []))

    assert {n["id"]: n["level"] for n in parts(full["tree"])}[part] == "needs_review"
    assert views.student_overlay(sid, learner.now_iso())[part]["level"] == "review"


def test_progress_results_stay_within_their_limits_when_every_part_needs_review(student):
    sid = student["id"]
    for p in _course_parts():
        _right_long_ago(sid, p)
    assert all(learner.shown_level(sid, p) == "needs_review" for p in _course_parts())
    results = service._settings().results
    me = learner.get_student(sid)
    assert service.result_size(service.my_progress(me)) <= results.max_chars
    assert service.result_size(service.my_progress(me, include_parts=True)) <= results.max_chars_full_progress


def _class_of(course, n):
    class_id = learner.add_class("Y12", None)
    ids = [learner.add_student(f"S{i}", course)["id"] for i in range(n)]
    learner.add_students_to_class(class_id, ids)
    return class_id, ids


def test_the_class_note_says_five_or_more_need_review_never_the_count(course, part):
    class_id, ids = _class_of(course, 9)
    for sid in ids[:7]:
        _right_long_ago(sid, part)
    for sid in ids[7:]:
        learner.record_evidence(sid, part, "mcq_check", 1.0, apply="now", n_options=4)
    cell = views.class_summary(class_id)["overlay"][part]
    assert f"{MIN} or more need review" in cell["note"] and "7 need" not in cell["note"]
    assert set(cell) == {"level", "band", "label", "note", "fade"}
    assert cell["band"] == "few"  # needs review is not practised


def test_the_class_note_is_left_out_under_five(course, part):
    class_id, ids = _class_of(course, 9)
    for sid in ids[: MIN - 1]:
        _right_long_ago(sid, part)
    for sid in ids[MIN - 1 :]:
        learner.record_evidence(sid, part, "mcq_check", 1.0, apply="now", n_options=4)
    assert "need review" not in views.class_summary(class_id)["overlay"][part]["note"]
