"""The HTTP layer: the key check in front of the MCP endpoint, the tool adapters and the prompts."""

import asyncio
from types import SimpleNamespace

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from starlette.testclient import TestClient

from edux import learner, server

LABELS = server.ThisMessage(question_depth="mechanism", engagement="active")


def _ctx(key):
    """The part of the MCP context the adapters read: the request's query string."""
    return SimpleNamespace(request_context=SimpleNamespace(request=SimpleNamespace(query_params={"key": key} if key else {})))


def test_a_request_without_a_known_key_is_refused_before_the_handshake(student):
    client = TestClient(server.http_app(), raise_server_exceptions=False)
    assert client.post("/mcp").status_code == 401
    assert client.post("/mcp?key=wrong").status_code == 401
    assert "key" in client.post("/mcp?key=wrong").json()["error"]
    assert client.post(f"/mcp?key={student['key']}", json={}).status_code != 401


def test_non_http_scopes_pass_straight_through():
    seen = []

    async def app(scope, receive, send):
        seen.append(scope["type"])

    asyncio.run(server.RequireKey(app)({"type": "lifespan"}, None, None))
    assert seen == ["lifespan"]


def test_the_key_is_read_from_the_query_string():
    assert server._key_from_scope({"query_string": b"key=abc&x=1"}) == "abc"
    assert server._key_from_scope({"query_string": b""}) is None
    assert server._key_from_scope({}) is None


def test_an_unknown_key_is_a_tool_error(course):
    with pytest.raises(ToolError, match="unknown or missing key"):
        server.student_from_request(_ctx("nope"))
    with pytest.raises(ToolError):
        server.student_from_request(SimpleNamespace(request_context=SimpleNamespace(request=None)))
    assert server._student_id(_ctx("nope")) is None
    assert server._student_id(None) is None


def test_the_tool_adapters_call_the_service_as_the_keyed_student(student, part):
    ctx = _ctx(student["key"])
    assert server._student_id(ctx) == student["id"]
    turn = server.tutor_turn(ctx, "what is elasticity?", LABELS, node_ids=[part], client="test")
    assert turn["ok"] is True and turn["plan"]
    assert server.get_my_progress(ctx)["tree"] is not None
    assert server.get_my_progress(ctx, include_parts=True)["tree"] is not None
    assert server.update_my_profile(ctx, interests="football")["profile"]["interests"] == "football"
    assert isinstance(server.plan_my_study(ctx), dict)


def test_the_prompts_read_their_text(course):
    assert "due" in server.review_due().lower()
    assert "elasticity" in server.check_me("  elasticity ").lower()


def test_the_wrapper_returns_a_compact_result_and_logs_the_call(student, part):
    wrapped = server.timed("get_my_progress", server.get_my_progress)
    result = wrapped(ctx=_ctx(student["key"]))
    assert result.content and "\n" not in result.content[0].text
    with pytest.raises(ToolError):  # the SDK turns the raised error into an error result; the call is logged first
        server.timed("get_my_progress", server.get_my_progress)(ctx=_ctx("nope"))
    rows = learner._conn().execute("SELECT ok FROM call_log WHERE tool = 'get_my_progress'").fetchall()
    assert [r["ok"] for r in rows] == [1, 0]


def test_serve_starts_uvicorn_without_an_access_log(course, monkeypatch):
    calls = {}
    monkeypatch.setattr("uvicorn.run", lambda app, **kw: calls.update(kw))
    server.serve("127.0.0.1", 9)
    assert calls == {"host": "127.0.0.1", "port": 9, "access_log": False}


def test_the_allowed_hosts_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "example.org, tunnel.test")
    security = server._security()
    assert "example.org:*" in security.allowed_hosts and "https://tunnel.test" in security.allowed_origins
