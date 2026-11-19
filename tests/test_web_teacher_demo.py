"""The demo teacher and the per-student teacher view (decision 0030): demo mode off by default and refused unless the
class is all synthetic, the per-student view off by default, no message text anywhere, bands withheld under five,
counts that agree between cards, bands and wrong ideas, and a seeded class that rebuilds to the same view."""

import dataclasses
import json

import pytest
from starlette.testclient import TestClient

from edux import cli, demo, learner, server, teachers
from edux.web import review

TEXT_KEYS = {"text", "message", "messages", "chat", "chats", "content", "reply", "transcript", "key", "key_hash", "score", "p", "rank"}


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


@pytest.fixture()
def seeded(course):
    return demo.seed_class_demo()


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


def _demo_session(client):
    got = client.post("/api/demo/teacher", json={})
    assert got.status_code == 200, got.text
    return got.json()


def test_the_settings_are_off_by_default(course):
    web = learner._settings().web
    assert web.demo_teacher is False and web.teacher_student_view is False


def test_demo_mode_off_refuses_the_button_and_the_routes(client, seeded):
    assert client.get("/api/demo/teacher").status_code == 404
    assert client.post("/api/demo/teacher", json={}).status_code == 404
    teacher = teachers.add_teacher("Ms Real")
    teachers.assign_class(teacher["id"], demo.DEMO_CLASS_ID)
    assert client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/review", headers=_auth(teacher["key"])).status_code == 404
    sid = seeded["students"][0]
    assert client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/student/{sid}", headers=_auth(teacher["key"])).status_code == 404


def test_demo_mode_on_signs_in_with_a_read_only_session(client, seeded, monkeypatch):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "1")
    assert client.get("/api/demo/teacher").json() == {"available": True}
    got = _demo_session(client)
    assert got["class_id"] == demo.DEMO_CLASS_ID and got["expires_in"] > 0
    who = client.get("/api/whoami", headers=_auth(got["session"])).json()
    assert who["role"] == "teacher" and [c["id"] for c in who["classes"]] == [demo.DEMO_CLASS_ID]
    page = client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/review", headers=_auth(got["session"]))
    assert page.status_code == 200 and page.json()["synthetic"] is True
    sid = page.json()["students"][0]["id"]
    one = client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/student/{sid}", headers=_auth(got["session"]))
    assert one.status_code == 200
    # read-only: a change is refused, and the session never opens the student side or MCP
    refused = client.post(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/coverage", json={"sections": []}, headers=_auth(got["session"]))
    assert refused.status_code == 403
    assert client.get("/api/me", headers=_auth(got["session"])).status_code == 403
    # the session is not accepted in the URL
    assert client.get(f"/api/whoami?key={got['session']}").status_code == 400


def test_a_class_with_a_real_student_is_refused_even_in_demo_mode(client, seeded, monkeypatch, course):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "1")
    session = _demo_session(client)["session"]
    real = learner.add_student("A Real Student", course)
    learner.add_students_to_class(demo.DEMO_CLASS_ID, [real["id"]])
    assert not demo.is_synthetic_class(demo.DEMO_CLASS_ID)
    assert client.get("/api/demo/teacher").status_code == 404
    assert client.post("/api/demo/teacher", json={}).status_code == 404
    assert client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/review", headers=_auth(session)).status_code == 404


def test_demo_mode_never_opens_a_real_class(client, seeded, monkeypatch, course):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "1")
    class_id = learner.add_class("Y12", None)
    ids = [learner.add_student(f"Real {i}", course)["id"] for i in range(6)]
    learner.add_students_to_class(class_id, ids)
    teacher = teachers.add_teacher("Ms Real")
    teachers.assign_class(teacher["id"], class_id)
    assert client.get(f"/api/teacher/class/{class_id}/review", headers=_auth(teacher["key"])).status_code == 404
    assert client.get(f"/api/teacher/class/{class_id}/student/{ids[0]}", headers=_auth(teacher["key"])).status_code == 404


def test_the_school_setting_turns_the_view_on(client, monkeypatch, course):
    s = learner._settings()
    changed = dataclasses.replace(s, web=dataclasses.replace(s.web, teacher_student_view=True))
    monkeypatch.setattr(learner, "_settings", lambda: changed)
    class_id = learner.add_class("Y12", None)
    ids = [learner.add_student(f"Real {i}", course)["id"] for i in range(3)]
    learner.add_students_to_class(class_id, ids)
    teacher = teachers.add_teacher("Ms Real")
    teachers.assign_class(teacher["id"], class_id)
    assert client.get(f"/api/teacher/class/{class_id}/review", headers=_auth(teacher["key"])).status_code == 200
    other = learner.add_student("Elsewhere", course)
    assert client.get(f"/api/teacher/class/{class_id}/student/{other['id']}", headers=_auth(teacher["key"])).status_code == 404


def test_no_message_text_in_any_response(client, seeded, monkeypatch):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "1")
    session = _demo_session(client)["session"]
    page = client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/review", headers=_auth(session)).json()
    found = _keys(page)
    for sid in seeded["students"]:
        found |= _keys(client.get(f"/api/teacher/class/{demo.DEMO_CLASS_ID}/student/{sid}", headers=_auth(session)).json())
    assert not found & TEXT_KEYS
    assert "share" not in found and "probability" not in json.dumps(page)


def test_bands_are_withheld_under_five(course):
    class_id = learner.add_class("Small", None)
    ids = [learner.add_student(f"Real {i}", course)["id"] for i in range(4)]
    learner.add_students_to_class(class_id, ids)
    part = learner.all_parts()[0]
    for sid in ids:
        learner.record_evidence(sid, part, "explain_back", 1.0, apply="now")
    bands = review.class_review(class_id)["bands"]
    assert bands and all(not b["enough"] and "band" not in b for b in bands)
    sid = learner.add_student("Real 5", course)["id"]
    learner.add_students_to_class(class_id, [sid])
    learner.record_evidence(sid, part, "explain_back", 1.0, apply="now")
    assert any(b["enough"] and b["band"] for b in review.class_review(class_id)["bands"])


def test_counts_agree_between_cards_bands_and_wrong_ideas(seeded):
    page = review.class_review(demo.DEMO_CLASS_ID)
    cards = page["students"]
    assert [c["name"].split()[-1] for c in cards] == sorted(c["name"].split()[-1] for c in cards)
    assert page["wrong_ideas"], "the demo class should hold shared wrong ideas"
    for w in page["wrong_ideas"]:
        assert w["students"] == sum(w["id"] in c["held"] for c in cards) > 1
    for b in page["bands"]:
        assert b["answered"] == sum(b["topic_id"] in c["topics"] for c in cards)
    assert page["test"] and len(page["test"]["topics"]) <= demo.TEST_TOPICS
    for card in cards:
        one = review.student_review(demo.DEMO_CLASS_ID, card["id"])
        assert [r["part_id"] for r in one["unsure"]] == [w["part_id"] for w in card["weak"]]
        assert one["record"]["answers"] >= sum(r["answers"] for r in one["unsure"])
        assert all(r["over_days"] <= one["record"]["over_days"] for r in one["unsure"])
        assert {s["id"] for s in one["ai_literacy"]["skills"]} == {"ask", "verify", "how_ai_works"}
    assert any(r["wrong_idea"] for c in cards for r in review.student_review(demo.DEMO_CLASS_ID, c["id"])["unsure"])
    assert any(s["checks"] for c in cards for s in review.student_review(demo.DEMO_CLASS_ID, c["id"])["ai_literacy"]["skills"])


def test_rebuild_gives_the_same_view(seeded):
    at = learner.now_iso()
    before = (review.class_review(demo.DEMO_CLASS_ID, at), [review.student_review(demo.DEMO_CLASS_ID, s, at) for s in seeded["students"]])
    for sid in seeded["students"]:
        learner.rebuild_state(sid)
    after = (review.class_review(demo.DEMO_CLASS_ID, at), [review.student_review(demo.DEMO_CLASS_ID, s, at) for s in seeded["students"]])
    assert before == after


def test_seeding_is_deterministic_and_needs_reset(seeded):
    def view():
        page = review.class_review(demo.DEMO_CLASS_ID)
        page["test"].pop("id")  # a new row id each time
        return page

    first = view()
    with pytest.raises(demo.DemoError):
        demo.seed_class_demo()
    demo.seed_class_demo(reset=True)
    assert view() == first
    assert all(s.startswith(demo.SYNTH_PREFIX) for s in seeded["students"]) and len(seeded["students"]) == len(demo.CLASS_NAMES)


def _run(*argv):
    with pytest.raises(SystemExit) as done:
        cli.main(list(argv))
    return done.value.code


def test_the_cli_seeds_the_class(course, capsys):
    assert _run("seed-demo", "--class") == 0
    assert "synthetic students" in capsys.readouterr().out
    assert _run("seed-demo", "--class") == 1
    assert demo.is_synthetic_class(demo.DEMO_CLASS_ID)
