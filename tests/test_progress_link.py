"""Map links from get_my_progress (decision 0026): present only with a public base URL, single-use, expiring, stored as a
hash only, never the student's key, within the result size limit, and opening only the student's own read-only pages."""

import json
from datetime import timedelta

import pytest
from starlette.testclient import TestClient

from edux import learner, server, service
from edux.web import links

BASE = "https://synapse.example.org"


@pytest.fixture(autouse=True)
def _no_env_base(monkeypatch):
    monkeypatch.delenv("EDUX_PUBLIC_BASE_URL", raising=False)


@pytest.fixture()
def base(monkeypatch):
    monkeypatch.setenv("EDUX_PUBLIC_BASE_URL", BASE + "/")


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


def _token(url):
    assert url.startswith(f"{BASE}/me#link=")
    return url.split("#link=", 1)[1]


def _later(monkeypatch, minutes):
    """Move the clock the links read forward by this many minutes."""
    moved = (learner.parse_ts(learner.now_iso()) + timedelta(minutes=minutes)).isoformat(timespec="seconds")
    monkeypatch.setattr(learner, "now_iso", lambda: moved)


def _rows():
    return [dict(r) for r in learner._conn().execute("SELECT * FROM web_link")]


# --- present or absent -------------------------------------------------------------------------------------------


def test_no_base_url_means_no_link_and_no_token(student):
    assert links.public_base_url() == ""
    out = service.my_progress(student)
    assert "map_url" not in out and "map_url_expires_minutes" not in out
    assert _rows() == []


def test_a_base_url_gives_a_single_use_map_link(student, base):
    out = service.my_progress(student)
    _token(out["map_url"])
    assert out["map_url_expires_minutes"] == learner._settings().web.link_minutes == 15


def test_the_environment_overrides_the_setting(student, monkeypatch):
    monkeypatch.setattr(links.learner, "_settings", lambda: _with_base("https://from-settings.example"))
    assert links.public_base_url() == "https://from-settings.example"
    monkeypatch.setenv("EDUX_PUBLIC_BASE_URL", "")
    assert links.public_base_url() == "https://from-settings.example"  # empty, as copied from .env.example: the setting
    monkeypatch.setenv("EDUX_PUBLIC_BASE_URL", "https://from-env.example/")
    assert links.public_base_url() == "https://from-env.example"


def _with_base(url):
    import dataclasses

    s = learner.load_settings()
    return dataclasses.replace(s, web=dataclasses.replace(s.web, public_base_url=url))


def test_every_call_issues_a_new_link(student, base):
    first, second = service.my_progress(student)["map_url"], service.my_progress(student)["map_url"]
    assert first != second


# --- what is stored, and what is never sent -------------------------------------------------------------------------


def test_only_the_hash_is_stored(student, base):
    token = _token(service.my_progress(student)["map_url"])
    (row,) = _rows()
    assert row["token_hash"] == learner.key_hash(token) and row["kind"] == "link" and row["used_at"] is None
    assert row["student_id"] == student["id"]
    assert all(token not in str(v) for r in _rows() for v in r.values())


def test_the_token_has_32_random_bytes(student, base):
    token = _token(service.my_progress(student)["map_url"])
    assert len(token) >= 43  # 32 bytes, URL-safe base64


def test_neither_the_token_nor_the_key_is_stored_anywhere(student, base):
    sent = server.timed("get_my_progress", lambda: service.my_progress(learner.student_by_key(student["key"])))()
    token = _token(json.loads(sent.content[0].text)["map_url"])
    conn = learner._conn()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    for table in tables:
        for row in conn.execute(f"SELECT * FROM {table}"):
            text = " ".join(str(v) for v in tuple(row))
            assert token not in text and student["key"] not in text, table


def test_the_students_key_is_never_in_the_result(student, base):
    sent = server.timed("get_my_progress", lambda: service.my_progress(learner.student_by_key(student["key"])))()
    text = sent.content[0].text
    assert student["key"] not in text and learner.key_hash(student["key"]) not in text
    assert "key" not in service.my_progress(student)  # no key field at all


# --- the size limit ----------------------------------------------------------------------------------------------


def test_the_link_counts_towards_the_limit_and_the_result_still_fits(student, base, monkeypatch):
    item = {"part_id": "p", "name": "x" * 60, "level": "new"}
    big = {
        "tree": {"a": "b"},
        "levers": [dict(item) for _ in range(12)],
        "weak_links": [dict(item) for _ in range(12)],
        "reviews_due": [dict(item) for _ in range(12)],
        "trends": {},
        "ai_literacy": {},
    }
    monkeypatch.setattr(service, "progress_parts", lambda *a, **k: {k2: (list(v) if isinstance(v, list) else v) for k2, v in big.items()})
    lists = ("levers", "weak_links", "reviews_due")
    out = service.my_progress(student)
    assert "map_url" in out and service.result_size(out) <= service.result_limit("get_my_progress") == 3000
    monkeypatch.delenv("EDUX_PUBLIC_BASE_URL")
    without = service.my_progress(student)
    assert sum(len(out[n]) for n in lists) < sum(len(without[n]) for n in lists)  # the link's characters were counted


def test_the_link_is_left_out_if_the_uncuttable_parts_leave_no_room(student, base, monkeypatch):
    huge = {"tree": {"t": "x" * 2900}, "levers": [], "weak_links": [], "reviews_due": [], "trends": {}, "ai_literacy": {}}
    monkeypatch.setattr(service, "progress_parts", lambda *a, **k: dict(huge))
    out = service.my_progress(student)
    assert "map_url" not in out and "map_url_expires_minutes" not in out
    assert service.result_size(out) <= 3000


def _pack_sized(include_parts):
    """A progress result shaped and sized like the real Edexcel Theme 1 pack's, measured 19 Nov (the pack itself can't be
    in the tests): a tree of 1 topic, 5 subtopics and 16 concepts (about 1,900 characters; about 5,450 with its parts),
    5 levers, 3 reviews, 2 weak links, trends, and AI literacy for a student with no research questions yet."""
    concepts_per = [5, 3, 3, 3, 2]

    def concept(i, j):
        entry = {"id": f"concept_{i}_{j}_name", "name": f"Concept {i}.{j} with a typical name", "level": "taught_in_class"}
        if include_parts:
            entry["children"] = [
                {"id": f"part_{i}_{j}_{k}", "name": f"Part {i}.{j}.{k} with a typical name", "level": "new"} for k in range(3)
            ]
        return entry

    tree = [
        {
            "id": "theme1",
            "name": "Theme 1: Markets and market failure",
            "level": "new",
            "children": [
                {"id": f"subtopic_{i}", "name": f"Subtopic {i} name", "level": "new", "children": [concept(i, j) for j in range(n)]}
                for i, n in enumerate(concepts_per)
            ],
        }
    ]
    item = {"part_id": "a_part_id_of_usual_length", "name": "A part name of a usual length", "level": "new"}
    return {
        "tree": tree,
        "levers": [dict(item, score=0.5) for _ in range(5)],
        "weak_links": [{"from": dict(item), "to": dict(item), "type": "causal", "note": "x" * 90} for _ in range(2)],
        "reviews_due": [dict(item, reason="fading", due="2026-11-20", note="x" * 60) for _ in range(3)],
        "trends": {k: {"recent": 0.5, "before": None, "direction": None} for k in ("deep_questions", "constructive", "just_show_me")},
        "ai_literacy": {
            "formative": "practice feedback, not a grade",
            **{k: {"level": "new", "evidence": {"checks": 0, "over_days": 0}, "skipped": 0} for k in ("ask", "verify")},
            "how_ai_works": {"level": "new", "held": [], "evidence": {"checks": 0, "over_days": 0}, "skipped": 0},
            "question_features": {},
        },
    }


@pytest.mark.parametrize("include_parts, tree_at_least", [(False, 1900), (True, 5400)])
def test_the_link_survives_on_a_result_the_size_of_the_real_pack(student, base, monkeypatch, include_parts, tree_at_least):
    sized = _pack_sized(include_parts)
    assert service.result_size(sized["tree"]) >= tree_at_least  # as big as the real pack's tree
    assert service.result_size(sized) > 2400  # it would not have fitted the old limit
    monkeypatch.setattr(service, "progress_parts", lambda *a, **k: _pack_sized(include_parts))
    out = service.my_progress(student, include_parts)
    assert "map_url" in out
    assert service.result_size(out) <= service.result_limit("get_my_progress", include_parts) == (6500 if include_parts else 3000)
    assert len(out["levers"]) >= 1  # something still says what to do next


def test_question_features_with_no_data_are_left_out(student):
    assert service.my_progress(student)["ai_literacy"]["question_features"] == {}


def test_a_real_progress_view_with_the_link_fits(student, part, base):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    for include_parts in (False, True):
        out = service.my_progress(student, include_parts)
        assert "map_url" in out and service.result_size(out) <= service.result_limit("get_my_progress", include_parts)


# --- swapping the link ---------------------------------------------------------------------------------------------


def test_a_link_swaps_once_for_a_session(client, student, base):
    token = _token(service.my_progress(student)["map_url"])
    res = client.post("/api/link", json={"token": token})
    assert res.status_code == 200
    session = res.json()["session"]
    assert res.json()["expires_in"] == 120 * 60 and session != token
    again = client.post("/api/link", json={"token": token})
    assert again.status_code == 401 and "already been used or has expired" in again.json()["error"]
    assert client.get("/api/me", headers={"Authorization": f"Bearer {session}"}).status_code == 200


def test_an_expired_link_is_refused(client, student, base, monkeypatch):
    token = _token(service.my_progress(student)["map_url"])
    _later(monkeypatch, 16)
    assert client.post("/api/link", json={"token": token}).status_code == 401
    assert links.exchange(token) is None


def test_a_link_inside_its_time_still_works(student, base, monkeypatch):
    token = _token(service.my_progress(student)["map_url"])
    _later(monkeypatch, 14)
    assert links.exchange(token) is not None


def test_a_session_expires(client, student, base, monkeypatch):
    session = links.exchange(_token(service.my_progress(student)["map_url"]))["session"]
    _later(monkeypatch, 121)
    assert client.get("/api/me", headers={"Authorization": f"Bearer {session}"}).status_code == 401


def test_bad_swap_requests_are_refused(client, student):
    assert client.post("/api/link", json={}).status_code == 401
    assert client.post("/api/link", json={"token": 5}).status_code == 401
    assert client.post("/api/link", json={"token": "made-up"}).status_code == 401
    assert client.post("/api/link", content=b"not json").status_code == 400
    assert client.post(f"/api/link?key={student['key']}", json={}).status_code == 400


def test_a_session_token_is_not_a_link_and_a_link_is_not_a_session(client, student, base):
    token = _token(service.my_progress(student)["map_url"])
    assert client.get("/api/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401  # unswapped link
    session = links.exchange(token)["session"]
    assert links.exchange(session) is None  # a session can't be swapped for another


# --- what a session opens ----------------------------------------------------------------------------------------


def test_a_session_opens_only_the_students_own_pages(client, course, base):
    a, b = learner.add_student("A", course), learner.add_student("B", course)
    session = links.exchange(_token(service.my_progress(a)["map_url"]))["session"]
    auth = {"Authorization": f"Bearer {session}"}
    assert client.get("/api/whoami", headers=auth).json() == {"role": "student"}
    assert client.get("/api/map", headers=auth).status_code == 200
    assert client.get("/api/me", headers=auth).json() == client.get("/api/me", headers={"Authorization": f"Bearer {a['key']}"}).json()
    assert links.student_by_session(session)["id"] == a["id"] != b["id"]
    class_id = learner.get_student(a["id"])["class_id"] or "c-any"
    assert client.get(f"/api/teacher/class/{class_id}", headers=auth).status_code == 403
    assert client.post(f"/api/teacher/class/{class_id}/coverage", headers=auth, json={"topics": []}).status_code == 403
    assert client.post(f"/mcp?key={session}").status_code == 401  # never the MCP endpoint


def test_deleting_the_student_deletes_their_links(student, base):
    links.exchange(_token(service.my_progress(student)["map_url"]))
    assert len(_rows()) == 2
    assert learner.delete_student(student["id"])["web_link"] == 2
    assert _rows() == []


def test_expired_rows_are_cleared_when_a_new_link_is_issued(student, base, monkeypatch):
    service.my_progress(student)
    _later(monkeypatch, 16)
    service.my_progress(student)
    assert len(_rows()) == 1
