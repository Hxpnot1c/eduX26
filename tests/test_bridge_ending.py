"""Step 05t: the reply's ending in four tiers, and the bridge question towards the next topic."""

from datetime import datetime, timedelta, timezone


from edux import context_blocks, graph, learner, plan

DAY = timedelta(days=1)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _turn(student, part):
    return context_blocks.Turn(student=student, parts=[part], message="", at=learner.now_iso(), limits={}, resolution={})


def _know(sid, part, days_ago=1):
    """Make the part at least developing by the number, with some answers."""
    for i in range(3):
        learner.record_evidence(sid, part, "mcq_check", 1.0, ts=(_now() - (days_ago + 0.1 * i) * DAY).isoformat(timespec="seconds"),
                                apply="now", n_options=4)


def _review(part):
    return {"part_id": part, "name": graph.get_node(part)["name"], "mode": "recall", "p_now": 0.2, "level": "new",
            "reason": "scheduled", "due": learner.now_iso(), "linked_to_focus": False}


def _blocks(reviews=(), extend=None):
    out = {"reviews_due": {"items": [_review(p) for p in reviews]} if reviews else None}
    if extend:
        out["support"] = {"part_id": extend, "level": "explain_back", "extend": True}
    return out


def test_with_nothing_due_and_a_link_the_ending_is_a_bridge(student):
    _know(student["id"], "ped_formula")
    tiers = plan.ending_tiers(_turn(student, "ped_formula"), _blocks(), learner._settings())
    assert [t["kind"] for t in tiers][:1] == ["bridge"]
    step = plan._second_step(_turn(student, "ped_formula"), _blocks(), learner._settings())
    assert step["move"] == "ask_mcq" and step["data"]["purpose"] == "intuition" and step["data"]["bridge"] is True
    assert step["data"]["link"]["from"] == "ped_formula" and step["data"]["link"]["to"] == step["part_id"]
    assert step["key"] == "ask_mcq_prequestion_bridge"


def test_a_bridge_beats_an_earned_extend(student):
    _know(student["id"], "ped_formula")
    kinds = [t["kind"] for t in plan.ending_tiers(_turn(student, "ped_formula"), _blocks(extend="ped_formula"), learner._settings())]
    assert kinds.index("bridge") < kinds.index("extend")


def test_an_urgent_review_beats_the_bridge(student):
    sid = student["id"]
    _know(sid, "ped_formula")
    _know(sid, "yed_definition", days_ago=5)
    soon = (_now() + 3 * DAY).date().isoformat()
    learner._conn().execute("INSERT INTO student_assessment (student_id, name, kind, date, part_ids, created_at) VALUES (?, 'Mock', 'mock', ?, ?, ?)",
                            (sid, soon, '["yed_definition"]', learner.now_iso()))
    tiers = plan.ending_tiers(_turn(student, "ped_formula"), _blocks(reviews=["yed_definition"]), learner._settings())
    assert [t["kind"] for t in tiers][:2] == ["review", "bridge"] and tiers[0]["tier"] == 1


def test_an_ordinary_review_comes_after_the_bridge_and_the_extend(student):
    _know(student["id"], "ped_formula")
    tiers = plan.ending_tiers(_turn(student, "ped_formula"), _blocks(reviews=["yed_definition"], extend="ped_formula"), learner._settings())
    assert [t["tier"] for t in tiers] == sorted(t["tier"] for t in tiers)
    assert [t["kind"] for t in tiers] == ["bridge", "extend", "review"]


def test_no_link_means_no_bridge(student, monkeypatch):
    _know(student["id"], "ped_formula")
    monkeypatch.setattr(graph, "linked", lambda node_id: [])
    assert plan.bridge_target(_turn(student, "ped_formula"), learner._settings()) is None
    assert [t["kind"] for t in plan.ending_tiers(_turn(student, "ped_formula"), _blocks(), learner._settings())] == []


def test_a_target_whose_prerequisites_are_not_developing_is_skipped(student):
    # ped_definition is still new, so ped_formula (which needs it) cannot be the bridge from it
    target = plan.bridge_target(_turn(student, "ped_definition"), learner._settings())
    assert target is None or target["part_id"] != "ped_formula"


def test_the_target_has_not_been_taught_yet(student):
    sid = student["id"]
    _know(sid, "ped_formula")
    first = plan.bridge_target(_turn(student, "ped_formula"), learner._settings())["part_id"]
    _know(sid, first)
    second = plan.bridge_target(_turn(student, "ped_formula"), learner._settings())
    assert second is None or second["part_id"] != first


def test_the_class_next_section_is_preferred_and_carries_its_reason_line(course, student):
    sid = student["id"]
    _know(sid, "ped_formula")
    class_id = learner.add_class("C")
    learner.add_students_to_class(class_id, [sid])
    learner.set_class_coverage(class_id, ["ped"], (_now() - 20 * DAY).date().isoformat())       # PED taught; next is PES
    target = plan.bridge_target(_turn(student, "ped_formula"), learner._settings())
    assert target["from_class"] is True and target["part_id"].startswith("pes_")
    step = plan.bridge_question(_turn(student, "ped_formula"), target, learner._settings())
    assert step["key"] == "ask_mcq_prequestion_bridge_reason" and "next in class" in step["data"]["reason"]


def test_without_a_link_to_the_next_section_it_falls_back_to_the_strongest_link(course, student, monkeypatch):
    sid = student["id"]
    _know(sid, "ped_formula")
    class_id = learner.add_class("C")
    learner.add_students_to_class(class_id, [sid])
    learner.set_class_coverage(class_id, ["pes"], (_now() - 20 * DAY).date().isoformat())       # next uncovered is PED's neighbour? make it unlinked
    learner.set_class_coverage(class_id, ["ped"], (_now() - 20 * DAY).date().isoformat())
    learner.set_class_coverage(class_id, ["yed"], (_now() - 20 * DAY).date().isoformat())        # next uncovered: tax incidence, not linked to ped_formula
    target = plan.bridge_target(_turn(student, "ped_formula"), learner._settings())
    assert target is not None and target["from_class"] is False


def test_the_bridge_evidence_feeds_the_not_covered_offset_for_a_not_covered_target(student):
    sid = student["id"]
    target = "pes_definition"
    learner.record_evidence(sid, target, "prequestion", 1.0, ts=(_now() - 10 * DAY).isoformat(timespec="seconds"), apply="now", n_options=4)
    offsets = learner.starting_offsets(sid)
    assert offsets["n_not_covered"] == 1 and offsets["not_covered"] > 0 and offsets["n_covered"] == 0


def test_every_candidate_not_picked_is_logged_with_its_tier(student):
    _know(student["id"], "ped_formula")
    step = plan._second_step(_turn(student, "ped_formula"), _blocks(reviews=["yed_definition"], extend="ped_formula"), learner._settings())
    assert [c["move"] for c in step["considered"]] == ["extend", "review"] and [c["tier"] for c in step["considered"]] == [3, 4]


def test_quiz_me_requests_only_ever_get_reviews(student):
    _know(student["id"], "ped_formula")
    tiers = plan.ending_tiers(_turn(student, "ped_formula"), _blocks(reviews=["yed_definition"], extend="ped_formula"),
                              learner._settings(), reviews_only=True)
    assert {t["kind"] for t in tiers} == {"review"}
