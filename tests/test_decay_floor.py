"""Decision 0025: a learnt part fades towards its normal start, not to 0 (research.md row 53, patch 0005)."""

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from edux import graph, learner

DAY = timedelta(days=1)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt):
    return dt.isoformat(timespec="seconds")


def _cover(student_id, parts, days_ago):
    class_id = learner.add_class("Decay class")
    learner.add_students_to_class(class_id, [student_id])
    concepts = sorted({graph.concept_of(p) or p for p in parts})
    learner.set_class_coverage(class_id, concepts, (_now() - days_ago * DAY).date().isoformat())


def test_p_now_fades_towards_the_floor():
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    assert learner.p_now(0.9, 2.0, start, start + 2 * DAY, floor=0.3) == pytest.approx(0.6)  # half the way down
    assert learner.p_now(0.9, 2.0, start, start + 200 * DAY, floor=0.3) == pytest.approx(0.3)
    assert learner.p_now(0.1, 2.0, start, start + 2 * DAY, floor=0.3) == pytest.approx(0.2)  # an old wrong answer counts for less too
    assert learner.p_now(0.9, 2.0, None, start + 200 * DAY, floor=0.3) == pytest.approx(0.9)  # no clock, no decay


def test_a_part_answered_right_once_reads_its_normal_start_after_60_days(course, student, part):
    sid, then = student["id"], _now() - 60 * DAY
    learner.record_evidence(sid, part, "mcq_check", 1.0, ts=_iso(then), apply="now", n_options=4)
    start = learner.initial_state(part)[0]
    for days in (1, 5, 20, 60):
        assert learner.part_p(sid, part, _iso(then + days * DAY)) >= start - 1e-9  # never below
    assert learner.part_p(sid, part) == pytest.approx(start, abs=1e-3)
    untouched = learner.add_student("Untouched", course)["id"]
    assert learner.part_p(untouched, part) <= learner.part_p(sid, part) + 1e-9  # the same part, untouched, reads the same or lower


def test_a_covered_part_answered_right_once_also_fades_to_its_normal_start(student, part):
    sid = student["id"]
    _cover(sid, [part], days_ago=70)
    then = _now() - 60 * DAY
    learner.record_evidence(sid, part, "mcq_check", 1.0, ts=_iso(then), apply="now", n_options=4)
    assert learner.part_p(sid, part) == pytest.approx(learner.initial_state(part)[0], abs=1e-3)
    assert learner.level(learner.part_p(sid, part)) == "new"  # the covered start (about 0.41) would never get here


def test_a_covered_part_never_answered_never_reads_below_its_untaught_start(student, part):
    """What _floored did for unanswered covered parts, now part of the floor."""
    sid = student["id"]
    _cover(sid, [part], days_ago=60)
    start = learner.initial_state(part)[0]
    taught = learner.parse_ts(learner.covered_since(sid, part))
    for days in (0, 1, 3, 10, 59):
        assert learner.part_p(sid, part, _iso(taught + days * DAY)) >= start - 1e-9
    assert learner.part_p(sid, part) == pytest.approx(start, abs=1e-3)


def test_ask_and_verify_fade_towards_zero(student):
    sid, then = student["id"], _now() - 60 * DAY
    for part in (learner.AIL_ASK, learner.AIL_VERIFY):
        assert learner.decay_floor(part) == 0.0
        learner.record_evidence(sid, part, "ail_task", 1.0, ts=_iso(then), apply="now")
        assert learner.part_p(sid, part) < 0.01


def test_how_ai_works_parts_fade_to_their_normal_start(course):
    how = graph.parts_of(learner.AIL_HOW)
    assert how and all(learner.decay_floor(p) == pytest.approx(learner.initial_state(p)[0]) for p in how)


def test_the_floor_is_the_same_for_every_student(course, part):
    a, b = learner.add_student("A", course)["id"], learner.add_student("B", course)["id"]
    then = _now() - 60 * DAY
    learner.record_evidence(a, part, "mcq_check", 1.0, ts=_iso(then), apply="now", n_options=4)
    for i in range(4):  # B has done well elsewhere, so B's own starting offset differs from A's
        for p in learner.all_parts():
            if p != part and not graph.is_literacy(p):
                learner.record_evidence(b, p, "mcq_check", 1.0, ts=_iso(then + i * timedelta(minutes=1)), apply="now", n_options=4)
    learner.record_evidence(b, part, "mcq_check", 1.0, ts=_iso(then + 5 * timedelta(minutes=1)), apply="now", n_options=4)
    assert learner.part_p(a, part) == pytest.approx(learner.part_p(b, part), abs=1e-3)


def test_floor_zero_keeps_the_old_rule(student, part, monkeypatch):
    s = learner._settings()
    changed = dataclasses.replace(s, decay=dataclasses.replace(s.decay, floor="zero"))
    monkeypatch.setattr(learner, "_settings", lambda: changed)
    sid, then = student["id"], _now() - 60 * DAY
    learner.record_evidence(sid, part, "mcq_check", 1.0, ts=_iso(then), apply="now", n_options=4)
    assert learner.decay_floor(part) == 0.0
    assert learner.part_p(sid, part) < 0.01


def test_days_until_below_with_a_floor():
    state = {"p_known": 0.9, "half_life_days": 2.0, "clock_start": "2026-11-01T00:00:00+00:00"}
    assert learner.days_until_below(state, 0.5, floor=0.3) == pytest.approx(2.0 * 1.5849625, rel=1e-6)  # 2 x log2(0.6 / 0.2)
    assert learner.days_until_below(state, 0.3, floor=0.3) is None  # the threshold is the floor: it never gets there
    assert learner.days_until_below(state, 0.2, floor=0.3) is None  # below the floor
    assert learner.days_until_below({**state, "p_known": 0.45}, 0.5, floor=0.3) is None  # already below it
    assert learner.days_until_below(state, 0.5) == pytest.approx(2.0 * 0.8479969, rel=1e-6)  # floor 0: 2 x log2(0.9 / 0.5)


def test_rebuild_after_long_gaps_gives_the_same_state_twice(student, part):
    sid, t = student["id"], _now() - 90 * DAY
    for days, score in ((0, 1.0), (30, 0.0), (31, 1.0), (75, 1.0)):
        learner.record_evidence(sid, part, "mcq_check", score, ts=_iso(t + days * DAY), apply="now", n_options=4)
    rows = lambda: [dict(r) for r in learner._conn().execute("SELECT * FROM part_state WHERE student_id = ? ORDER BY part_id", (sid,))]
    queue = lambda: [dict(r) for r in learner._conn().execute("SELECT * FROM review_queue WHERE student_id = ? ORDER BY part_id", (sid,))]
    live = rows(), queue()
    learner.rebuild_state(sid)
    first = rows(), queue()
    learner.rebuild_state(sid)
    assert first == (rows(), queue()) == live
