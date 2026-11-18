"""Step 05l: the weakest point uses each point's last five answers; one passive message is not coasting."""

from datetime import datetime, timedelta, timezone

from edux import graph, learner




def _log(student_id, part, point, score, minute):
    ts = (datetime(2026, 11, 1, 10, tzinfo=timezone.utc) + timedelta(minutes=minute)).isoformat(timespec="seconds")
    learner.record_evidence(student_id, part, "explain_back", score, ts=ts, apply="none", point_id=point)


def test_early_misses_that_were_put_right_do_not_make_a_point_the_weakest(student, part):
    sid = student["id"]
    # point A: five early misses, then five right (last five all right); point B: five right, then three misses
    for i in range(5):
        _log(sid, part, "pa", 0.0, i)
    for i in range(5):
        _log(sid, part, "pa", 1.0, 10 + i)
    for i in range(5):
        _log(sid, part, "pb", 1.0, 20 + i)
    for i in range(3):
        _log(sid, part, "pb", 0.0, 30 + i)
    assert learner.weakest_point(sid, part, ["pa", "pb"]) == "pb"     # by all answers A (0.5) and B (0.625) would pick A


def test_a_point_never_asked_counts_as_half(student, part):
    sid = student["id"]
    _log(sid, part, "pa", 1.0, 0)
    assert learner.weakest_point(sid, part, ["pa", "pc"]) == "pc"      # 1.0 against 0.5
    _log(sid, part, "pa", 0.0, 1)
    _log(sid, part, "pa", 0.0, 2)
    assert learner.weakest_point(sid, part, ["pa", "pc"]) == "pa"      # 1/3 against 0.5


def _exchange(student_id, part, engagement, minute):
    ts = (datetime.now(timezone.utc) - timedelta(minutes=minute)).isoformat(timespec="seconds")
    learner.record_exchange(student_id, [part], "surface", engagement, ts=ts, apply="none")


def test_one_passive_first_message_is_not_coasting(student, part):
    _exchange(student["id"], part, "passive", 1)
    assert learner.coasting_share(student["id"]) is None


def test_two_passive_messages_are_coasting(student, part):
    _exchange(student["id"], part, "passive", 2)
    _exchange(student["id"], part, "passive", 1)
    assert learner.coasting_share(student["id"]) == 1.0


# --- plan-level rules (step 05l) -----------------------------------------------------------------------------

from edux import context_blocks, graph, plan  # noqa: E402


def _turn(student, part):
    return context_blocks.Turn(student=student, parts=[part], message="", at=learner.now_iso(), limits={}, resolution={})


def _part_with_misconceptions(n=2):
    for p in learner.all_parts():
        if len(graph.misconceptions_for([p])) >= n and not graph.is_literacy(p):
            return p
    return None


def test_the_two_option_wrong_option_is_a_held_misconception_first(student):
    part = _part_with_misconceptions()
    if part is None:
        import pytest
        pytest.skip("needs a part with two misconceptions")
    found = [m["id"] for m in graph.misconceptions_for([part])]
    turn = _turn(student, part)
    assert plan.two_option_wrong(turn, part)["id"] == found[0]                       # none held, no watch-for: pack order
    watch = {"misconceptions": {"watch_for": [{"id": found[1], "part_id": part}]}}
    assert plan.two_option_wrong(turn, part, watch)["id"] == found[1]                # watch-for beats pack order
    learner.record_exchange(student["id"], [part], "surface", "active", misconception_ids=[found[1]], apply="now")
    held = {"misconceptions": {"watch_for": [{"id": found[0], "part_id": part}]}}
    assert plan.two_option_wrong(_turn(student, part), part, held)["id"] == found[1]  # held beats watch-for


def test_the_two_option_check_is_marked_to_be_followed_by_the_show(student, part):
    step = plan.two_option_check(_turn(student, part), part, 1, learner._settings())
    assert step["data"]["then_show"] is True
    assert len(step["data"]["options"]) in (1, 2) or step["data"].get("extra_option")


def test_stop_returns_a_session_summary_with_what_was_covered_and_the_next_review(student, part):
    sid = student["id"]
    learner.record_evidence(sid, part, "explain_back", 1.0, apply="now")
    learner.record_exchange(sid, [part], "surface", "active", apply="now")
    step = plan.picked(_turn(student, part), part, learner._settings(), {}, "stop")[0]
    assert step["move"] == "session_summary"
    assert graph.get_node(part)["name"] in step["data"]["covered"]
    assert step["data"]["next_review"] is None or {"name", "due"} <= set(step["data"]["next_review"])


def test_the_passive_offer_includes_extend_only_when_it_is_earned(student, part):
    sid = student["id"]
    for i in range(5):
        _exchange(sid, part, "passive", 10 - i)
    turn, settings = _turn(student, part), learner._settings()
    not_earned = plan.main_step(turn, {"support": {"extend": False}}, settings, "none", [], set(), None)
    earned = plan.main_step(turn, {"support": {"extend": True}}, settings, "none", [], set(), None)
    assert not_earned[0]["data"]["options"] == ["quiz", "stop"]
    assert earned[0]["data"]["options"] == ["quiz", "extend", "stop"]
