"""The two design pages: served byte for byte with their own policy in demo mode only (EDUX_DEMO_TEACHER=1); with demo
mode off, /teacher and /me are as before and /me/demo is not found."""

import hashlib

import pytest
from starlette.testclient import TestClient

from edux import server
from edux.web import app as web
from edux.web import links

TEACHER, STUDENT = web.STATIC / web.DEMO_PAGES["/teacher"], web.STATIC / web.DEMO_PAGES["/me/demo"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


@pytest.fixture()
def demo(monkeypatch):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "1")


def test_in_demo_mode_teacher_returns_the_teacher_design_byte_for_byte(client, demo):
    res = client.get("/teacher")
    assert res.status_code == 200 and _sha(res.content) == _sha(TEACHER.read_bytes())
    assert res.headers["content-security-policy"] == web.DEMO_CSP


def test_in_demo_mode_me_demo_returns_the_student_design_byte_for_byte(client, demo):
    res = client.get("/me/demo")
    assert res.status_code == 200 and _sha(res.content) == _sha(STUDENT.read_bytes())
    assert res.headers["content-security-policy"] == web.DEMO_CSP


def test_the_design_pages_policy_allows_only_what_they_need():
    for directive in (
        "script-src 'unsafe-inline'",
        "style-src 'unsafe-inline' https://fonts.googleapis.com",
        "font-src https://fonts.gstatic.com",
        "img-src data:",
    ):
        assert directive in web.DEMO_CSP
    assert "connect-src" not in web.DEMO_CSP and "default-src 'none'" in web.DEMO_CSP


def test_every_other_route_keeps_its_policy_in_demo_mode(client, demo):
    for path in ("/", "/map", "/me", "/static/css/base.css", "/api/public/map"):
        res = client.get(path)
        assert res.headers["content-security-policy"] == web.SECURITY_HEADERS["Content-Security-Policy"], path
    assert _sha(client.get("/me").content) == _sha((web.STATIC / "me.html").read_bytes())  # /me itself is unchanged


def test_with_demo_mode_off_teacher_and_me_are_as_before_and_me_demo_is_not_found(client, monkeypatch):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "0")
    teacher, me = client.get("/teacher"), client.get("/me")
    assert teacher.content == (web.STATIC / "teacher.html").read_bytes() and me.content == (web.STATIC / "me.html").read_bytes()
    assert teacher.headers["content-security-policy"] == web.SECURITY_HEADERS["Content-Security-Policy"]
    assert client.get("/me/demo").status_code == 404


def test_demo_mode_is_off_by_default(client):
    assert not links.demo_teacher_on()
    assert client.get("/me/demo").status_code == 404 and client.get("/teacher").content == (web.STATIC / "teacher.html").read_bytes()


@pytest.mark.parametrize("on", ["0", "1"])
def test_the_design_files_are_never_served_as_static_files(client, monkeypatch, on):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", on)
    for path in web.DEMO_PAGES.values():
        assert client.get(f"/static/{path}").status_code == 404


def test_a_link_swap_in_demo_mode_says_to_go_on_to_the_student_design(client, student, demo):
    token = links.issue_link(student["id"])
    swapped = client.post("/api/link", json={"token": token}).json()
    assert swapped["session"] and swapped["demo"] is True
    again = client.post("/api/link", json={"token": token})  # a used link still fails, with the same message
    assert again.status_code == 401 and "already been used or has expired" in again.json()["error"]


def test_a_link_swap_with_demo_mode_off_is_as_before(client, student, monkeypatch):
    monkeypatch.setenv("EDUX_DEMO_TEACHER", "0")
    swapped = client.post("/api/link", json={"token": links.issue_link(student["id"])}).json()
    assert set(swapped) == {"session", "expires_in"}


def test_the_page_goes_on_to_the_student_design_only_after_a_successful_swap():
    js = (web.STATIC / "js" / "api.js").read_text(encoding="utf-8")
    ok = js.index("if (!res.ok) { linkFailed = true; return; }")
    go = js.index('if (swapped.demo) location.replace("/me/demo")')
    assert ok < go  # a failed swap returns before it, so the "already used or expired" message still shows


def test_the_files_are_kept_byte_for_byte():
    attributes = (web.STATIC.parents[2] / ".gitattributes").read_text(encoding="utf-8")
    assert "edux/web/static/demo/*.html -text" in attributes
