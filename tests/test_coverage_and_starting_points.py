"""Step 05q: classes, coverage and starting points (with Vishnu's changes of 18 November)."""

import dataclasses
import math
from datetime import datetime, timedelta, timezone

import pytest

from edux import graph, learner, service

DAY = timedelta(days=1)


def _iso(dt):
    return dt.isoformat(timespec="seconds")


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


@pytest.fixture()
def klass(course, student):
    """A class holding the student, with the part's concept taught 20 days ago."""
    class_id = learner.add_class("Test class")
    learner.add_students_to_class(class_id, [student["id"]])
    return class_id


def _cover(klass, part, days_ago=20):
    concept = graph.concept_of(part) or part
    day = (_now() - days_ago * DAY).date().isoformat()
    learner.set_class_coverage(klass, [concept], day)
    return day


def _logit(p):
    return math.log(p / (1 - p))


def test_an_uncovered_part_starts_as_before(student, part):
    start = learner.starting_point(student["id"], part)
    assert start["p"] == pytest.approx(learner.initial_state(part)[0])
    assert start["clock_start"] is None and start["taught_on"] is None


def test_a_covered_part_starts_the_boost_up_in_log_odds_and_respects_difficulty(student, klass, part):
    day = _cover(klass, part)
    p0 = learner.initial_state(part)[0]
    start = learner.starting_point(student["id"], part)
    boost = learner._settings().coverage.boost_logit
    assert _logit(start["p"]) == pytest.approx(_logit(p0) + boost, abs=1e-6)
    assert start["p"] > p0 and start["taught_on"] == day and start["clock_start"] == day


def test_coverage_dated_after_the_time_asked_does_not_count(student, klass, part):
    _cover(klass, part, days_ago=-5)  # taught in five days' time
    assert learner.covered_since(student["id"], part) is None
    assert learner.covered_since(student["id"], part, _now() + 6 * DAY) is not None


def test_the_forgetting_clock_starts_on_the_taught_date(student, klass, part):
    day = _cover(klass, part, days_ago=20)
    start = learner.starting_point(student["id"], part)
    assert start["clock_start"] == day
    taught = learner.parse_ts(day)
    floor = learner.decay_floor(part)  # the normal start (decision 0025)
    assert learner.part_p(student["id"], part, taught) == pytest.approx(start["p"])
    one_half_life = taught + timedelta(days=start["half_life"])
    assert learner.p_now(start["p"], start["half_life"], start["clock_start"], one_half_life, floor) == pytest.approx(
        floor + (start["p"] - floor) / 2
    )


def test_a_covered_part_never_practised_is_due_for_review_and_not_listed_twice(student, klass, part):
    _cover(klass, part, days_ago=40)
    due = [r for r in learner.due_reviews(student["id"], 99) if r["part_id"] == part]
    assert len(due) == 1 and due[0]["reason"] == "taught_in_class"
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    assert [r for r in learner.due_reviews(student["id"], 99) if r["reason"] == "taught_in_class" and r["part_id"] == part] == []


def test_a_part_with_no_answer_never_shows_developing_or_secure(student, klass, part):
    assert learner.shown_level(student["id"], part) == "new"
    _cover(klass, part)
    p = learner.part_p(student["id"], part)
    assert learner.level(p) in ("new", "developing")  # the number may say developing...
    assert learner.shown_level(student["id"], part) == "taught_in_class"  # ...the display never does
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    assert learner.shown_level(student["id"], part) in ("new", "developing", "secure")


def test_the_display_changes_after_the_first_answer(student, klass, part):
    _cover(klass, part)
    before = learner.shown_level(student["id"], part)
    learner.record_evidence(student["id"], part, "mcq_check", 1.0, apply="now", n_options=4)
    assert before == "taught_in_class" and learner.shown_level(student["id"], part) != "taught_in_class"


def test_the_progress_view_shows_a_covered_untouched_topic_as_taught_in_class(student, klass, part):
    _cover(klass, part)
    tree = service.my_progress(learner.get_student(student["id"]))["tree"]
    flat = []

    def walk(nodes):
        for n in nodes:
            flat.append(n)
            walk(n.get("children", []))

    walk(tree)
    assert any(n["level"] == "taught_in_class" for n in flat)
    assert all(n["level"] in ("new", "taught_in_class", "developing", "secure") for n in flat)


def _answer(sid, part, kind, score, days_ago):
    learner.record_evidence(sid, part, kind, score, ts=_iso(_now() - days_ago * DAY), apply="now", n_options=4)


def test_pre_teaching_success_on_covered_parts_raises_only_the_covered_offset(student, klass, part):
    _cover(klass, part, days_ago=30)
    _answer(student["id"], part, "prequestion", 1.0, 10)
    o = learner.starting_offsets(student["id"])
    assert o["n_covered"] == 1 and o["covered"] > 0
    assert o["n_not_covered"] == 0 and o["not_covered"] == 0.0


def test_pre_teaching_success_on_uncovered_parts_leaves_the_covered_offset_alone(student, part):
    _answer(student["id"], part, "prequestion", 1.0, 10)
    o = learner.starting_offsets(student["id"])
    assert o["n_not_covered"] == 1 and o["not_covered"] > 0 and o["covered"] == 0.0


def test_a_first_answer_after_teaching_does_not_feed_the_offset(student, part):
    sid = student["id"]
    learner.record_exchange(sid, [part], "surface", "active", support_given="worked_example", ts=_iso(_now() - 12 * DAY), apply="now")
    _answer(sid, part, "explain_back", 1.0, 10)
    assert learner.starting_offsets(sid)["n_not_covered"] == 0


def test_an_explain_back_before_any_teaching_does_feed_it(student, part):
    _answer(student["id"], part, "explain_back", 1.0, 10)
    assert learner.starting_offsets(student["id"])["n_not_covered"] == 1


def test_an_all_right_and_an_all_wrong_start_give_finite_bounded_offsets(course):
    parts = [p for p in learner.all_parts() if not p.startswith("ail_")]
    bound = learner._settings().starting.bound_logits
    for score in (1.0, 0.0):
        s = learner.add_student(f"S{score}", course)
        for i, p in enumerate(parts[:6]):
            _answer(s["id"], p, "prequestion", score, 20 - i)
        o = learner.starting_offsets(s["id"])
        assert math.isfinite(o["not_covered"]) and abs(o["not_covered"]) <= bound
    assert learner.starting_offsets(learner.add_student("Fresh", course)["id"])["not_covered"] == 0.0


def test_the_offset_applies_to_parts_with_no_evidence(student, part):
    sid = student["id"]
    other = next(p for p in learner.all_parts() if p != part and not p.startswith("ail_") and not graph.prerequisites(p, 1))
    before = learner.starting_point(sid, other)["p"]
    _answer(sid, part, "prequestion", 1.0, 10)
    assert learner.starting_point(sid, other)["p"] > before


def _part_with_prereq():
    for p in learner.all_parts():
        pre = [pp for e in graph.prerequisites(p, 1) for pp in graph.parts_of(e["other"])]
        if pre and not p.startswith("ail_"):
            return p, pre[0]
    return None, None


def test_prerequisite_success_moves_a_new_part_forward(student):
    part, pre = _part_with_prereq()
    if part is None:
        pytest.skip("no part with a prerequisite")
    assert learner.forward_shift(student["id"], part) == 0.0
    for i in range(4):
        _answer(student["id"], pre, "mcq_check", 1.0, 3 - i * 0.1)
    assert learner.forward_shift(student["id"], part) > 0
    assert learner.starting_point(student["id"], part)["p"] > learner.initial_state(part)[0]


def test_a_part_with_its_own_evidence_ignores_the_prerequisite_shift(student):
    part, pre = _part_with_prereq()
    if part is None:
        pytest.skip("no part with a prerequisite")
    _answer(student["id"], part, "mcq_check", 1.0, 1)
    p_with_row = learner.part_p(student["id"], part)
    for i in range(4):
        _answer(student["id"], pre, "mcq_check", 1.0, 0.5 - i * 0.05)
    assert learner.part_p(student["id"], part) == pytest.approx(p_with_row, abs=0.02)  # only decay, no shift


def test_no_starting_point_is_above_the_cap(student, klass, part, monkeypatch):
    _cover(klass, part)
    monkeypatch.setattr(learner, "forward_shift", lambda *a, **k: 6.0)
    assert learner.starting_point(student["id"], part)["p"] == pytest.approx(learner._settings().starting.cap)


def test_ai_literacy_parts_have_no_coverage_offset_or_shift(student, klass):
    assert learner.covered_since(student["id"], "ail_ask") is None
    assert learner.starting_point(student["id"], "ail_ask")["p"] == pytest.approx(learner.initial_state("ail_ask")[0])
    assert learner.shown_level(student["id"], "ail_ask") == learner.level(learner.part_p(student["id"], "ail_ask"))


@pytest.mark.parametrize(("points", "guess"), [(1, 0.20), (2, 0.20), (3, 0.15), (4, 0.10), (6, 0.10)])
def test_the_explain_back_guess_falls_with_the_number_of_points(points, guess):
    assert learner.slip_guess("explain_back", n_points=points)[1] == guess


def test_a_narrowed_explain_back_counts_as_one_point(student, part):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now", point_id="x")
    row = learner._conn().execute("SELECT p_before, surprise FROM evidence_derived WHERE student_id = ?", (student["id"],)).fetchone()
    expected = row["p_before"] * 0.9 + (1 - row["p_before"]) * 0.20
    assert row["surprise"] == pytest.approx(1.0 - expected, abs=1e-6)


# --- the class estimate (off by default) ---------------------------------------------------------------------


def _with_class_estimate(monkeypatch, enabled=True):
    s = learner._settings()
    changed = dataclasses.replace(s, coverage=dataclasses.replace(s.coverage, class_estimate_enabled=enabled))
    monkeypatch.setattr(learner, "_settings", lambda: changed)
    monkeypatch.setattr(service, "_settings", lambda: changed)


def test_the_class_estimate_is_off_by_default(klass, part):
    assert learner._settings().coverage.class_estimate_enabled is False
    assert learner.class_shift(klass) is None


def _class_of(course, n, part, score):
    class_id = learner.add_class("Cohort")
    learner.set_class_coverage(class_id, [graph.concept_of(part) or part], (_now() - 40 * DAY).date().isoformat())
    for i in range(n):
        s = learner.add_student(f"M{i}", course)
        learner.add_students_to_class(class_id, [s["id"]])
        learner.record_evidence(s["id"], part, "prequestion", score, ts=_iso(_now() - 10 * DAY), apply="now", n_options=4)
    return class_id


def test_fewer_than_five_students_give_no_class_estimate(course, part, monkeypatch):
    _with_class_estimate(monkeypatch)
    assert learner.class_shift(_class_of(course, 4, part, 1.0)) is None


def test_five_students_give_an_estimate_and_it_never_goes_below_the_floor(course, part, monkeypatch):
    _with_class_estimate(monkeypatch)
    right, wrong = _class_of(course, 5, part, 1.0), _class_of(course, 5, part, 0.0)
    assert learner.class_shift(right) > 0 and learner.class_shift(wrong) < 0
    member = learner._conn().execute("SELECT id FROM student WHERE class_id = ? LIMIT 1", (wrong,)).fetchone()["id"]
    p0 = learner.initial_state(part)[0]
    boosted = 1 / (1 + math.exp(-(_logit(p0) + learner._settings().coverage.boost_logit)))
    assert learner.base_start(member, part)["p"] >= boosted - learner._settings().coverage.class_max_down - 1e-9


def test_the_student_notice_appears_only_while_the_class_estimate_is_on(student, klass, monkeypatch):
    assert service._class_notice(student["id"]) is None
    _with_class_estimate(monkeypatch)
    assert "class" in service._class_notice(student["id"]).lower()


# --- classes, coverage input and the student's own say -------------------------------------------------------


def test_sections_match_by_id_spec_code_or_name(course):
    nodes, unmatched = graph.match_sections(["ped", "3.1.2", "income elasticity of demand", "nonsense"])
    assert {n["id"] for n in nodes} == {"ped", "pes", "yed"} and unmatched == ["nonsense"]
    assert graph.match_sections(["ai_literacy"])[0] == []


def test_a_student_can_say_what_was_covered_and_it_applies_to_them_only(course, student, part):
    other = learner.add_student("Other", course)
    out = service.update_profile(
        learner.get_student(student["id"]), covered_in_class={"topics": [graph.concept_of(part), "nonsense"], "when": "2026-10-01"}
    )
    assert out["ok"] and out["covered"]["unmatched"] == ["nonsense"]
    at = "2026-11-01T00:00:00+00:00"
    assert learner.covered_since(student["id"], part, at) == "2026-10-01"
    assert learner.covered_since(other["id"], part, at) is None


def test_covered_in_class_refuses_a_future_date_and_no_match(student):
    me = learner.get_student(student["id"])
    assert service.update_profile(me, covered_in_class={"topics": ["nonsense"]})["ok"] is False
    future = (_now() + 3 * DAY).date().isoformat()
    assert service.update_profile(me, covered_in_class={"topics": ["ped"], "when": future})["ok"] is False


def test_class_coverage_can_be_listed_and_unknown_classes_are_refused(course, klass):
    learner.set_class_coverage(klass, ["ped"], "2026-10-01", "csv")
    rows = learner.class_coverage(klass)
    assert rows[0]["spec_ref"] == "3.1.1" and rows[0]["parts"] == 3 and rows[0]["set_by"] == "csv"
    with pytest.raises(ValueError):
        learner.set_class_coverage("nope", ["ped"], "2026-10-01")
    with pytest.raises(ValueError):
        learner.add_students_to_class("nope", ["x"])


def test_rebuild_gives_the_same_state_with_coverage(student, klass, part):
    sid = student["id"]
    _cover(klass, part, days_ago=30)
    _answer(sid, part, "prequestion", 1.0, 12)
    _answer(sid, part, "mcq_check", 1.0, 5)
    before = [dict(r) for r in learner._conn().execute("SELECT * FROM part_state WHERE student_id = ? ORDER BY part_id", (sid,))]
    learner.rebuild_state(sid)
    after = [dict(r) for r in learner._conn().execute("SELECT * FROM part_state WHERE student_id = ? ORDER BY part_id", (sid,))]
    assert after == before


def test_deleting_a_student_removes_their_own_coverage(course, student, part):
    service.update_profile(learner.get_student(student["id"]), covered_in_class={"topics": ["ped"]})
    learner.delete_student(student["id"])
    assert learner._conn().execute("SELECT COUNT(*) FROM student_coverage").fetchone()[0] == 0


def test_a_covered_part_never_answered_does_not_decay_below_where_it_would_start_untaught(student, klass, part):
    _cover(klass, part, days_ago=60)  # 60 days: the 2-day half-life would take it to nothing
    p = learner.part_p(student["id"], part)
    assert p >= learner.initial_state(part)[0] - 1e-9


def test_the_first_answer_on_a_covered_part_starts_from_the_floor_not_from_nothing(student, klass, part):
    _cover(klass, part, days_ago=60)
    learner.record_evidence(student["id"], part, "mcq_check", 1.0, apply="now", n_options=4)
    row = learner._conn().execute("SELECT p_before FROM evidence_derived WHERE student_id = ?", (student["id"],)).fetchone()
    assert row["p_before"] >= learner.initial_state(part)[0] - 1e-9
    assert learner.part_p(student["id"], part) > learner.initial_state(part)[0]
