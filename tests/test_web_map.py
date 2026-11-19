"""The course map: the view that feeds it, its two API routes, and what the page code may and may not do."""

import json

import pytest
from starlette.testclient import TestClient

from edux import graph, learner, server, teachers
from edux.web import app as web
from edux.web import views


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


def _auth(key):
    return {"Authorization": f"Bearer {key}"}


# --- the view ---------------------------------------------------------------------------------------------------


def test_the_map_has_every_course_node_and_link(course):
    data = views.course_map()
    by_level = {lv: [n for n in data["nodes"] if n["level"] == lv] for lv in ("topic", "concept", "part")}
    course_parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    assert sorted(n["id"] for n in by_level["part"]) == sorted(course_parts)
    assert len(by_level["topic"]) == len(graph.topics()) and by_level["concept"]
    assert data["course"]["id"] == course and {e["type"] for e in data["edges"]} <= set(views.EDGE_TYPES) and data["edges"]


def test_ai_literacy_parts_are_left_out(course):
    ids = {n["id"] for n in views.course_map()["nodes"]}
    assert not any(graph.is_literacy(i) for i in ids)


def test_every_link_joins_two_nodes_on_the_map(course):
    data = views.course_map()
    ids = {n["id"] for n in data["nodes"]}
    assert all(e["from"] in ids and e["to"] in ids for e in data["edges"])


def test_parts_carry_a_size_and_counts_but_never_the_content_of_a_mark_point(course):
    data = views.course_map()
    for n in (n for n in data["nodes"] if n["level"] == "part"):
        assert 0 <= n["importance"] <= 1 and n["mark_points"] >= 0 and n["misconceptions"] >= 0
    text = json.dumps(data)
    for point in graph.mark_points_for(learner.all_parts())[:5]:
        assert point["point"] not in text


def test_a_rejected_link_is_not_drawn(course):
    before = len(views.course_map()["edges"])
    conn = graph._conn()
    with conn:
        conn.execute("UPDATE edge SET status = 'rejected' WHERE rowid = (SELECT MIN(rowid) FROM edge WHERE type = 'prerequisite')")
    assert len(views.course_map()["edges"]) == before - 1


def test_an_unknown_course_has_no_map(course):
    assert views.course_map("elsewhere") is None
    assert views.course_for(None)["id"] == course


# --- the routes -------------------------------------------------------------------------------------------------


def test_the_public_map_needs_no_key_for_the_example_pack(client):
    res = client.get("/api/public/map")
    assert res.status_code == 200 and res.json()["course"]["id"] == views.EXAMPLE_COURSE_ID
    assert res.headers["cache-control"] == "no-store"


def test_the_public_map_can_be_switched_off(client, monkeypatch):
    import dataclasses

    settings = learner._settings()
    off = dataclasses.replace(settings, web=dataclasses.replace(settings.web, public_example_map=False))
    monkeypatch.setattr(learner, "_settings", lambda: off)
    assert client.get("/api/public/map").status_code == 404


def test_any_other_pack_is_never_public(client, monkeypatch):
    monkeypatch.setattr(views, "EXAMPLE_COURSE_ID", "some-real-pack")
    assert client.get("/api/public/map").status_code == 404


def test_the_keyed_map_needs_a_key_in_the_header(client, student, teacher_key):
    assert client.get("/api/map").status_code == 401
    assert client.get("/api/map", headers=_auth("wrong")).status_code == 401
    assert client.get(f"/api/map?key={student['key']}", headers=_auth(student["key"])).status_code == 400
    for key in (student["key"], teacher_key):
        res = client.get("/api/map", headers=_auth(key))
        assert res.status_code == 200 and res.json()["nodes"]


def test_a_teacher_can_name_a_course_and_gets_404_for_an_unknown_one(client, teacher_key):
    assert client.get("/api/map?course=nope", headers=_auth(teacher_key)).status_code == 404


@pytest.fixture()
def teacher_key(course):
    return teachers.add_teacher("Ms T")["key"]


# --- the page code ----------------------------------------------------------------------------------------------


def test_the_map_page_loads_its_scripts_in_order():
    html = (web.STATIC / "map.html").read_text(encoding="utf-8")
    assert html.index("api.js") < html.index("shell.js") < html.index("graph.js") < html.index("map.js")
    assert "map.css" in html and 'id="map"' in html and "data-level-key" in html


def test_the_graph_code_offers_a_list_alternative_and_keyboard_movement():
    code = (web.STATIC / "js" / "graph.js").read_text(encoding="utf-8")
    for needle in ('"list"', "ArrowRight", "aria-label", "role", "caption", "aria-pressed", "textContent"):
        assert needle in code, needle
