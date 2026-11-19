"""Step 05y: Ask and Verify are formative and show their evidence; asking for sources earns nothing alone."""

from datetime import datetime, timedelta, timezone

from edux import learner, service


def test_asking_for_sources_earns_no_credit_on_its_own():
    features = ["concept", "context", "asks_sources", "asks_reasoning"]
    alone = learner.question_evidence(features)
    assert alone["score"] == 0.75  # three of four: the sources feature is not counted
    with_check = learner.question_evidence(features, sources_credit=True)
    assert with_check["score"] == 1.0


def test_the_other_features_are_unchanged_and_unknown_ones_ignored():
    assert learner.question_evidence(["concept"])["score"] == 0.25
    assert learner.question_evidence(["concept", "context", "nonsense"])["score"] == 0.5
    assert learner.question_evidence(None)["score"] == 0.0


def test_a_verify_moment_this_session_gives_the_sources_credit(student):
    sid = student["id"]
    assert learner.verified_this_session(sid) is False
    learner.record_evidence(sid, learner.AIL_VERIFY, "ail_task", 1.0, apply="now")
    assert learner.verified_this_session(sid) is True


def test_a_verify_moment_in_an_earlier_session_does_not(student):
    sid = student["id"]
    old = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(timespec="seconds")
    learner.record_evidence(sid, learner.AIL_VERIFY, "ail_task", 1.0, ts=old, apply="now")
    learner.record_exchange(sid, ["ail_ask"], "surface", "active", apply="now")  # a current session, with no verify
    assert learner.verified_this_session(sid) is False


def test_the_progress_view_is_formative_and_shows_the_evidence_behind_each_level(student):
    sid = student["id"]
    for i in range(4):
        ts = (datetime.now(timezone.utc) - timedelta(days=14 - 3 * i)).isoformat(timespec="seconds")
        learner.record_evidence(sid, learner.AIL_VERIFY, "ail_task", 1.0, ts=ts, apply="now")
    ai = service.my_progress(learner.get_student(sid))["ai_literacy"]
    assert ai["formative"] == "practice feedback, not a grade"
    assert ai["verify"]["evidence"] == {"checks": 4, "over_days": 14}
    assert ai["ask"]["evidence"] == {"checks": 0, "over_days": 0}
    assert "checks" in ai["how_ai_works"]["evidence"]
