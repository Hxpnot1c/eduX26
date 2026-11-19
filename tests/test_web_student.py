"""The student's page: what /api/me returns, who may ask, and that it never shows more than the rules allow."""

import json
from datetime import date, timedelta

import pytest
from starlette.testclient import TestClient

from edux import graph, learner, server, service, teachers
from edux.web import app as web
from edux.web import views

FORBIDDEN_KEYS = {"p_now", "p_known", "p", "probability", "score", "rank", "streak", "percentile"}


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


def _auth(key):
    return {"Authorization": f"Bearer {key}"}


def _keys(value, found=None):
    found = set() if found is None else found
    if isinstance(value, dict):
        for k, v in value.items():
            found.add(k)
            _keys(v, found)
    elif isinstance(value, list):
        for v in value:
            _keys(v, found)
    return found


def _answer(student, part, score=1.0, days_ago=0):
    ts = learner._event_ts(learner.parse_ts(learner.now_iso()) - timedelta(days=days_ago))
    learner.record_evidence(student["id"], part, "explain_back", score, apply="now", ts=ts)


# --- who may ask ------------------------------------------------------------------------------------------------


def test_the_page_data_needs_a_student_key_in_the_header(client, student):
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/me", headers=_auth("wrong")).status_code == 401
    assert client.get(f"/api/me?key={student['key']}", headers=_auth(student["key"])).status_code == 400
    assert client.get("/api/me", headers=_auth(student["key"])).status_code == 200


def test_a_teacher_cannot_read_a_students_record(client, student):
    key = teachers.add_teacher("Ms T")["key"]
    res = client.get("/api/me", headers=_auth(key))
    assert res.status_code == 403 and "teachers see classes" in res.json()["error"]


def test_one_student_never_sees_another(client, course):
    a, b = learner.add_student("A", course), learner.add_student("B", course)
    part = learner.all_parts()[0]
    _answer(b, part)
    text = json.dumps(client.get("/api/me", headers=_auth(a["key"])).json())
    assert b["id"] not in text and b["key"] not in text
    assert client.get("/api/me", headers=_auth(a["key"])).json()["overlay"][part]["level"] == "none"


# --- what it shows ---------------------------------------------------------------------------------------------


def test_no_probability_score_rank_or_streak_appears(student, part):
    _answer(student, part)
    data = views.student_page(learner.get_student(student["id"]))
    assert not (_keys(data) & FORBIDDEN_KEYS), _keys(data) & FORBIDDEN_KEYS
    assert "streak" not in json.dumps(data).lower() and "rank" not in json.dumps(data).lower()


def test_a_part_with_no_answers_is_none_or_taught_never_developing(student, part):
    class_id = learner.add_class("Y12", None)
    learner.add_students_to_class(class_id, [student["id"]])
    topic = graph.topics()[0]
    learner.set_class_coverage(class_id, [topic["id"]], (date.today() - timedelta(days=20)).isoformat(), "cli")
    overlay = views.student_overlay(student["id"], learner.now_iso())
    covered = {p for p in graph.parts_of(topic["id"])}
    assert all(overlay[p]["level"] == "taught" for p in covered)
    assert all(overlay[p]["level"] == "none" for p in overlay if p not in covered)
    assert overlay[next(iter(covered))]["note"] == "taught in class, not yet checked"


def test_an_answered_part_shows_its_level_its_evidence_and_fades_with_time(student, part):
    _answer(student, part, 1.0, days_ago=0)
    other = next(p for p in learner.all_parts() if p != part and not graph.is_literacy(p))
    _answer(student, other, 1.0, days_ago=40)
    overlay = views.student_overlay(student["id"], learner.now_iso())
    assert overlay[part]["level"] in ("new", "developing", "secure") and overlay[part]["note"] == "1 answer, last today"
    assert overlay[part]["fade"] == 1.0
    assert views.FADE_FLOOR <= overlay[other]["fade"] < 1.0 and "40 days ago" in overlay[other]["note"]


def test_ai_literacy_parts_are_not_on_the_map(student):
    assert not any(graph.is_literacy(p) for p in views.student_overlay(student["id"], learner.now_iso()))


def test_reviews_explain_themselves_in_plain_words(student):
    class_id = learner.add_class("Y12", None)
    learner.add_students_to_class(class_id, [student["id"]])
    learner.set_class_coverage(class_id, [graph.topics()[0]["id"]], (date.today() - timedelta(days=20)).isoformat(), "cli")
    service.update_profile(learner.get_student(student["id"]), exam_date_override=(date.today() + timedelta(days=20)).isoformat())
    data = views.student_page(learner.get_student(student["id"]))
    assert data["reviews"] and all(r["why"] and r["when"] for r in data["reviews"])
    assert {r["why"] for r in data["reviews"]} == {views.REVIEW_WHY["taught_in_class"]}
    assert "guilt" not in json.dumps(data) and not any(w in json.dumps(data["reviews"]).lower() for w in ("overdue", "behind", "failed"))


def test_the_plan_for_an_upcoming_test_is_offered(student, part):
    service.update_profile(
        learner.get_student(student["id"]),
        add_assessment={
            "name": "Mock",
            "kind": "mock",
            "date": (date.today() + timedelta(days=9)).isoformat(),
            "topics": [graph.topics()[0]["name"]],
        },
    )
    data = views.student_page(learner.get_student(student["id"]))
    assert data["coming_up"]["assessments"][0]["name"] == "Mock" and data["coming_up"]["plan"]["sessions"]


def test_literacy_is_practice_feedback_with_the_evidence_behind_it(student):
    ai = views.student_page(learner.get_student(student["id"]))["ai_literacy"]
    assert "not a grade" in ai["note"] and [s["id"] for s in ai["skills"]] == ["ask", "verify", "how_ai_works"]
    assert all({"level", "checks", "over_days"} <= set(s) for s in ai["skills"])


def test_calibration_only_appears_once_there_is_enough_to_say(student):
    assert views.student_page(learner.get_student(student["id"]))["calibration"] is None


def test_the_setup_text_comes_from_the_setup_sheet_without_markdown(course):
    setup = views.chatbot_setup()
    assert "tutor_turn" in setup["prompt"] and setup["keeps"]
    assert all("**" not in line for line in setup["keeps"]) and any("deleted" in line for line in setup["keeps"])


def test_the_chatbots_progress_is_still_trimmed_but_the_page_gets_it_whole(student, part):
    assert "reviews_due" in service.progress_parts(learner.get_student(student["id"]), False)
    assert service.my_progress(learner.get_student(student["id"]))["tree"]


# --- the page ---------------------------------------------------------------------------------------------------


def test_the_hidden_attribute_really_hides():
    css = (web.STATIC / "css" / "base.css").read_text(encoding="utf-8")
    assert "[hidden] { display: none !important; }" in css


def test_the_student_page_loads_its_scripts_and_sections():
    html = (web.STATIC / "me.html").read_text(encoding="utf-8")
    assert html.index("graph.js") < html.index("me.js") and "me.css" in html
    for section in ("next", "reviews", "coming", "literacy", "record", "setup"):
        assert f'data-fill="{section}"' in html
