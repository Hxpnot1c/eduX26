"""Step 05r: the per-session offset cache gives exactly the same values as computing from scratch."""

import dataclasses
import math
import random
from datetime import datetime, timedelta, timezone

import pytest

from edux import graph, learner


def _reference_learning_offset(student_id, before=None):
    """The learning-rate offset as step 05h/05m computed it: from the whole history, every call (the code before step 05r)."""
    p = learner._settings().personalisation
    rows = learner._conn().execute(
        """SELECT d.evidence_id, d.session_id, l.part_id, d.surprise FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id
           WHERE d.student_id = ? AND d.session_id < ? AND d.fatigued = 0 AND d.immediate = 0 AND d.weight > 0
           ORDER BY l.ts, l.id""", (student_id, learner._event_ts(before))).fetchall()
    firsts = {r[0] for r in learner._conn().execute("SELECT MIN(id) FROM evidence_log WHERE student_id = ? GROUP BY part_id", (student_id,))}
    rows = [r for r in rows if not graph.is_literacy(r["part_id"]) and r["evidence_id"] not in firsts]
    low, high = (math.log(b) for b in p.learn_rate_weight_bounds)
    offset, used = 0.0, 0
    for session_id in sorted({r["session_id"] for r in rows})[1:] + [None]:
        earlier = [r for r in rows if session_id is None or r["session_id"] < session_id]
        n = len(earlier)
        target = 0.0
        if n >= p.min_observations and len({r["part_id"] for r in earlier}) >= p.min_parts:
            weights = [0.5 ** ((n - 1 - i) / p.recency_half_life) for i in range(n)]
            mean = sum(w * r["surprise"] for w, r in zip(weights, earlier)) / sum(weights)
            target = min(high, max(low, n / (n + p.learn_rate_k) * mean * p.surprise_scale))
        step = p.max_change_per_session
        offset += min(step, max(-step * p.down_change_factor, target - offset))
        used = n
    return {"offset": offset, "n": used}


@pytest.fixture(autouse=True)
def _on(monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "1")
    # shorter recency and smaller thresholds so that a modest synthetic history moves the offset
    s = learner._settings()
    changed = dataclasses.replace(s, personalisation=dataclasses.replace(s.personalisation, min_observations=4, learn_rate_k=5))
    monkeypatch.setattr(learner, "_settings", lambda: changed)


def _history(student_id, sessions, per_session, seed=3, start_days=400):
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    rng = random.Random(seed)
    start = datetime.now(timezone.utc) - timedelta(days=start_days)
    for s in range(sessions):
        for a in range(per_session):
            ts = (start + timedelta(days=s * 2, minutes=3 * a)).isoformat(timespec="seconds")
            learner.record_evidence(student_id, rng.choice(parts), "mcq_check", float(rng.random() < 0.7), ts=ts,
                                    apply="now", n_options=4)


def test_the_cached_offset_equals_the_one_computed_from_scratch_after_every_session(student):
    sid = student["id"]
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    rng = random.Random(11)
    start = datetime.now(timezone.utc) - timedelta(days=200)
    for s in range(14):
        for a in range(4):
            ts = (start + timedelta(days=s * 2, minutes=3 * a)).isoformat(timespec="seconds")
            learner.record_evidence(sid, rng.choice(parts), "mcq_check", float(rng.random() < 0.6), ts=ts, apply="now", n_options=4)
        asked_at = (start + timedelta(days=s * 2 + 1)).isoformat(timespec="seconds")
        got, want = learner.learning_offset(sid, asked_at), _reference_learning_offset(sid, asked_at)
        assert got["n"] == want["n"] and got["offset"] == pytest.approx(want["offset"], abs=1e-9)


def test_the_offset_actually_moves_so_the_comparison_is_not_trivial(student):
    _history(student["id"], 14, 5, seed=5)
    assert abs(learner.learning_offset(student["id"])["offset"]) > 1e-6


def test_the_cache_fills_in_session_order_and_a_second_call_reads_it(student):
    _history(student["id"], 10, 4)
    learner.learning_offset(student["id"])
    rows = learner._conn().execute("SELECT session_id FROM learner_offset_cache WHERE student_id = ? AND learn_state IS NOT NULL "
                                   "ORDER BY session_id", (student["id"],)).fetchall()
    assert len(rows) >= 5 and [r[0] for r in rows] == sorted(r[0] for r in rows)
    again = learner.learning_offset(student["id"])
    assert again["offset"] == pytest.approx(_reference_learning_offset(student["id"])["offset"], abs=1e-9)


def test_rebuild_clears_and_refills_the_cache_to_the_same_values(student):
    sid = student["id"]
    _history(sid, 12, 4)
    before = learner.learning_offset(sid)
    rows_before = [dict(r) for r in learner._conn().execute("SELECT * FROM learner_offset_cache WHERE student_id = ? ORDER BY session_id", (sid,))]
    learner.rebuild_state(sid)
    assert learner.learning_offset(sid) == before
    rows_after = [dict(r) for r in learner._conn().execute("SELECT * FROM learner_offset_cache WHERE student_id = ? ORDER BY session_id", (sid,))]
    assert [r["learn_state"] for r in rows_after if r["learn_state"]] == [r["learn_state"] for r in rows_before if r["learn_state"]]


def test_an_event_out_of_order_drops_the_later_cached_sessions_and_the_answer_stays_right(student):
    sid = student["id"]
    _history(sid, 12, 4)
    learner.learning_offset(sid)
    old = (datetime.now(timezone.utc) - timedelta(days=350)).isoformat(timespec="seconds")
    part = next(p for p in learner.all_parts() if not graph.is_literacy(p))
    learner.record_evidence(sid, part, "mcq_check", 0.0, ts=old, apply="now", n_options=4)       # earlier than everything cached
    left = learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ? AND session_id > ?",
                                   (sid, learner.session_start(learner._conn(), sid, old))).fetchone()[0]
    assert left == 0
    assert learner.learning_offset(sid)["offset"] == pytest.approx(_reference_learning_offset(sid)["offset"], abs=1e-9)


def test_other_settings_do_not_reuse_the_cache(student, monkeypatch):
    sid = student["id"]
    _history(sid, 12, 4)
    learner.learning_offset(sid)
    s = learner._settings()
    stricter = dataclasses.replace(s, personalisation=dataclasses.replace(s.personalisation, recency_half_life=3))
    monkeypatch.setattr(learner, "_settings", lambda: stricter)
    monkeypatch.setattr(learner, "settings_hash", lambda *a, **k: "another")
    assert learner.learning_offset(sid)["offset"] == pytest.approx(_reference_learning_offset(sid)["offset"], abs=1e-9)


def test_off_by_default_nothing_is_written(course, monkeypatch):
    monkeypatch.setenv("EDUX_PERSONALISATION", "0")
    s = learner.add_student("Off", course)
    _history(s["id"], 6, 3)
    assert learner.learning_offset(s["id"]) == {"offset": 0.0, "n": 0, "weight": 1.0}
    assert learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE learn_state IS NOT NULL").fetchone()[0] == 0


def test_starting_offsets_are_cached_and_equal_when_computed_again(student):
    sid = student["id"]
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    for i, p in enumerate(parts[:5]):
        ts = (datetime.now(timezone.utc) - timedelta(days=30 - i)).isoformat(timespec="seconds")
        learner.record_evidence(sid, p, "prequestion", 1.0 if i % 2 else 0.0, ts=ts, apply="now", n_options=4)
    first = learner.starting_offsets(sid)
    cached = learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ? AND covered_offset IS NOT NULL", (sid,)).fetchone()[0]
    assert cached >= 1                  # one per session whose start was asked for, the current one included
    learner._conn().execute("DELETE FROM learner_offset_cache WHERE student_id = ?", (sid,))
    assert learner.starting_offsets(sid) == first


def test_changing_coverage_drops_the_cached_starting_offsets(student, course):
    sid = student["id"]
    learner.starting_offsets(sid)
    assert learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ?", (sid,)).fetchone()[0] >= 1
    class_id = learner.add_class("C")
    learner.add_students_to_class(class_id, [sid])
    assert learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ?", (sid,)).fetchone()[0] == 0
    learner.starting_offsets(sid)
    learner.set_class_coverage(class_id, ["ped"], "2026-10-01")
    assert learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ?", (sid,)).fetchone()[0] == 0


def test_deleting_a_student_removes_their_cache(student):
    _history(student["id"], 8, 4)
    learner.learning_offset(student["id"])
    learner.delete_student(student["id"])
    assert learner._conn().execute("SELECT COUNT(*) FROM learner_offset_cache WHERE student_id = ?", (student["id"],)).fetchone()[0] == 0
