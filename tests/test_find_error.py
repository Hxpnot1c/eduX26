"""Find-the-error practice (decision 0012): off by default, labelled as practice, one planted error or none,
scored as hits and false alarms apart, never shown to the chatbot, rare."""

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from edux import context_blocks, graph, learner, plan, service

PART = "ped_formula"
LABELS = {"question_depth": "mechanism", "engagement": "active"}


@pytest.fixture()
def on(monkeypatch):
    monkeypatch.setenv("EDUX_FIND_ERROR", "1")


def _known(student, part=PART, n=3):
    for i in range(n):
        learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now",
                                ts=(datetime.now(timezone.utc) - timedelta(days=2, minutes=5 * (n - i))).isoformat(timespec="seconds"))


def _turn(student, part=PART):
    return context_blocks.Turn(student=learner.get_student(student["id"]), parts=[part], message="", at=learner.now_iso(),
                               limits={}, resolution={})


def _step(student, blocks=None):
    return plan.find_error_step(_turn(student), blocks or {}, learner._settings())


def test_it_is_off_by_default(student, monkeypatch):
    monkeypatch.delenv("EDUX_FIND_ERROR", raising=False)
    _known(student)
    assert learner._settings().find_error.enabled is False and _step(student) is None


def test_it_needs_a_part_at_developing_or_above_with_an_answer(student, on):
    assert _step(student) is None                                             # nothing answered yet
    learner.record_evidence(student["id"], PART, "explain_back", 0.0, apply="now")
    assert _step(student) is None                                             # answered, but still new


def test_the_item_is_labelled_as_practice_and_gives_nothing_away(student, on):
    _known(student)
    step = _step(student)
    line = step["data"]["line"]
    assert "Practice, not a real answer" in line and "one mistake, or none" in line
    assert step["move"] == "say_line" and step["key"] == "say_line_find_error" and step["data"]["answer_type"] == "find_error"
    public = service.public_steps([step])[0]
    assert "item" not in public and "misconception" not in str(public).lower() and "kind" not in public["data"]
    letters = plan.score_next([step])[PART]
    assert [x["id"] for x in letters] == ["a", "b", "c", "d"]                  # the same four for every item


def test_an_error_item_swaps_exactly_one_sentence_for_the_misconception(student, on, monkeypatch):
    _known(student)
    monkeypatch.setattr(learner, "_settings", _with_clean_share(0.0))
    step = _step(student)
    item = step["item"]
    assert item["kind"] == "error" and item["misconception_id"] and "mistake was sentence" in item["reveal"]
    points = [p["point"].strip().rstrip(".") + "." for p in graph.score_points(PART)]
    shown = [ln.split(". ", 1)[1] for ln in step["data"]["line"].splitlines() if ln[:2] in ("1.", "2.", "3.", "4.")]
    changed = [i for i, (a, b) in enumerate(zip(points, shown)) if a != b]
    assert changed == [item["sentence"] - 1]
    assert shown[changed[0]].rstrip(".") == graph.get_misconception(item["misconception_id"])["wrong_idea"].strip().rstrip(".")


def _with_clean_share(share):
    import dataclasses
    s = learner._settings()
    changed = dataclasses.replace(s, find_error=dataclasses.replace(s.find_error, clean_share=share))
    return lambda: changed


def test_a_clean_item_is_the_explanation_unchanged(student, on, monkeypatch):
    _known(student)
    monkeypatch.setattr(learner, "_settings", _with_clean_share(1.0))
    step = _step(student)
    assert step["item"]["kind"] == "clean" and step["item"]["misconception_id"] is None and "no mistake" in step["item"]["reveal"]
    points = [p["point"].strip().rstrip(".") + "." for p in graph.score_points(PART)]
    shown = [ln.split(". ", 1)[1] for ln in step["data"]["line"].splitlines() if ln[:2] in ("1.", "2.", "3.", "4.")]
    assert shown == points


def test_about_two_fifths_of_items_are_clean_controls(on):
    clean = sum(int(hashlib.sha256(f"s-{i}:{PART}:2026-11-19T10:00:00".encode()).hexdigest(), 16) % 100 < 40 for i in range(500))
    assert 170 <= clean <= 230


@pytest.mark.parametrize(("kind", "ticked", "hit"), [
    ("error", ["b", "c"], True), ("error", ["a", "b", "c"], True), ("error", ["a"], False), ("error", ["a", "b"], False),
    ("error", ["b"], False), ("error", ["d"], False), ("error", [], False),
    ("clean", ["d"], True), ("clean", ["d", "a"], False), ("clean", ["a"], False), ("clean", ["a", "b", "c"], False), ("clean", [], False),
])
def test_hits_and_false_alarms_are_scored_apart(kind, ticked, hit):
    item = {"id": "x", "kind": kind, "part_id": PART, "reveal": "r", "misconception_id": "m" if kind == "error" else None}
    out = learner.score_find_error({"points_met": ticked}, item)
    assert out["hit"] is hit and out["score"] == (1.0 if hit else 0.0) and out["kind"] == kind


def test_a_blanket_there_is_a_mistake_is_never_rewarded():
    clean = {"id": "c", "kind": "clean", "part_id": PART, "reveal": "r", "misconception_id": None}
    error = {"id": "e", "kind": "error", "part_id": PART, "reveal": "r", "misconception_id": "m"}
    blanket = {"points_met": ["a"]}
    assert learner.score_find_error(blanket, clean)["score"] == 0.0 and learner.score_find_error(blanket, error)["score"] == 0.0


def test_an_unknown_letter_is_refused():
    with pytest.raises(ValueError):
        learner.score_find_error({"points_met": ["z"]}, {"id": "x", "kind": "clean", "part_id": PART, "reveal": "", "misconception_id": None})


def test_not_while_rushing_and_at_most_one_a_session(student, on):
    _known(student)
    assert _step(student, {"session": {"state": "fatigued"}}) is None
    learner.record_evidence(student["id"], PART, "find_error", 1.0, apply="now", point_id="err:x")
    assert _step(student) is None


def test_items_rotate_through_the_parts_misconceptions(student, on, monkeypatch):
    _known(student)
    monkeypatch.setattr(learner, "_settings", _with_clean_share(0.0))
    first = _step(student)["item"]["id"]
    learner.record_evidence(student["id"], PART, "find_error", 1.0, ts=(datetime.now(timezone.utc) - timedelta(days=3)).isoformat(timespec="seconds"),
                            apply="now", point_id=first)
    second = _step(student)
    assert second is None or second["item"]["id"] != first


def test_a_literacy_part_never_gets_one(student, on):
    for i in range(3):
        learner.record_evidence(student["id"], "ail_verify", "ail_task", 1.0, apply="now")
    assert plan.find_error_step(_turn(student, "ail_verify"), {}, learner._settings()) is None


# --- the whole turn: scored against the kept item, recorded on the part and on Verify ---------------------------------


def _hold_an_item(student, monkeypatch, share):
    monkeypatch.setattr(learner, "_settings", _with_clean_share(share))
    monkeypatch.setattr(service, "_settings", learner._settings)
    step = _step(student)
    service._save_plan(student["id"], learner.now_iso(), [step], [PART], set(), set(), None, None, None, {})
    return step["item"]


def _answer(student, ticked):
    return service.tutor_turn(learner.get_student(student["id"]), "my answer", LABELS, node_ids=[PART],
                              answer={"part_id": PART, "type": "find_error", "points_met": ticked})


def test_a_hit_is_recorded_on_the_part_and_on_verify_as_its_own_type_and_the_error_is_corrected(student, on, monkeypatch):
    _known(student)
    item = _hold_an_item(student, monkeypatch, 0.0)
    out = _answer(student, ["a", "b", "c"])
    fb = out["plan"][0]
    assert fb["move"] == "feedback" and fb["data"]["correct"] is True and "right idea" in fb["data"]["correct_option"]
    assert fb["data"]["misconceptions"] and fb["data"]["misconceptions"][0]["id"] == item["misconception_id"]
    rows = learner._conn().execute("SELECT part_id, evidence_type, score, point_id FROM evidence_log WHERE student_id = ? "
                                   "AND evidence_type IN ('find_error', 'ail_find_error') ORDER BY id", (student["id"],)).fetchall()
    assert [(r["part_id"], r["evidence_type"], r["score"]) for r in rows] == [(PART, "find_error", 1.0), ("ail_verify", "ail_find_error", 1.0)]
    assert rows[0]["point_id"] == item["id"] and rows[0]["point_id"].startswith("err:")
    assert learner._conn().execute("SELECT COUNT(*) FROM student_misconception WHERE student_id = ?", (student["id"],)).fetchone()[0] == 0


def test_a_false_alarm_on_a_clean_item_scores_zero_and_still_reveals_it_was_clean(student, on, monkeypatch):
    _known(student)
    _hold_an_item(student, monkeypatch, 1.0)
    out = _answer(student, ["a", "b", "c"])
    fb = out["plan"][0]
    assert fb["data"]["correct"] is False and "no mistake" in fb["data"]["correct_option"] and fb["data"]["misconceptions"] == []
    row = learner._conn().execute("SELECT score, point_id FROM evidence_log WHERE student_id = ? AND evidence_type = 'find_error'", (student["id"],)).fetchone()
    assert row["score"] == 0.0 and row["point_id"].startswith("clean:")


def test_an_answer_with_no_item_waiting_is_a_lost_question(student, on):
    _known(student)
    out = _answer(student, ["d"])
    assert out["ok"] is True and not [r for r in learner._conn().execute("SELECT 1 FROM evidence_log WHERE evidence_type = 'find_error'")]


def test_the_verify_rows_use_their_own_type_so_real_verify_moments_are_not_inflated(student, on, monkeypatch):
    _known(student)
    _hold_an_item(student, monkeypatch, 0.0)
    before = learner.part_p(student["id"], "ail_verify")
    _answer(student, ["a", "b", "c"])
    assert "ail_find_error" in learner._settings().bkt.evidence and learner.part_p(student["id"], "ail_verify") >= before
    assert learner.verified_this_session(student["id"]) is False     # practice is not checking a source: no Ask sources credit
