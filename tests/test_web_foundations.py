"""The web layer's foundations: routing next to /mcp, bearer-only sign-in, security headers, teachers and their classes,
and static checks that keep the pages private and accessible (no other origin, no inline code, contrast)."""

import importlib.util
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from edux import cli, learner, server, teachers
from edux.web import app as web

STATIC = Path(web.STATIC)


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


@pytest.fixture()
def teacher(course):
    return teachers.add_teacher("Ms Teacher")


def _auth(key):
    return {"Authorization": f"Bearer {key}"}


# --- routing and headers ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["/", "/map", "/me", "/teacher"])
def test_pages_are_public_and_carry_the_security_headers(client, path):
    res = client.get(path)
    assert res.status_code == 200 and res.headers["content-type"].startswith("text/html")
    csp = res.headers["content-security-policy"]
    assert "default-src 'none'" in csp and "'unsafe-inline'" not in csp and "http" not in csp
    assert res.headers["referrer-policy"] == "no-referrer" and res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"


def test_static_files_are_served_with_headers(client):
    css = client.get("/static/css/tokens.css")
    font = client.get("/static/fonts/newsreader-latin-400-normal.woff2")
    assert css.status_code == 200 and font.status_code == 200 and len(font.content) > 5000
    assert css.headers["content-security-policy"] and client.get("/static/nothing.css").status_code == 404


def test_the_mcp_endpoint_is_unchanged(client, student, teacher):
    assert client.post("/mcp").status_code == 401
    assert client.post("/mcp?key=wrong").status_code == 401
    assert client.post(f"/mcp?key={teacher['key']}").status_code == 401  # a teacher key never opens /mcp
    assert client.post(f"/mcp?key={student['key']}", json={}).status_code != 401


def test_the_api_is_never_cached(client, student):
    res = client.get("/api/whoami", headers=_auth(student["key"]))
    assert res.headers["cache-control"] == "no-store"


# --- sign-in ----------------------------------------------------------------------------------------------------


def test_whoami_needs_a_known_bearer_key(client, student):
    assert client.get("/api/whoami").status_code == 401
    assert client.get("/api/whoami", headers=_auth("wrong")).status_code == 401
    assert client.get("/api/whoami", headers={"Authorization": "Basic abc"}).status_code == 401


def test_a_student_is_a_student_and_nothing_about_them_is_returned(client, student):
    body = client.get("/api/whoami", headers=_auth(student["key"])).json()
    assert body == {"role": "student"}


def test_a_teacher_sees_their_name_and_only_their_classes(client, teacher):
    mine, other = learner.add_class("Year 12", None), learner.add_class("Year 13", None)
    teachers.assign_class(teacher["id"], mine)
    body = client.get("/api/whoami", headers=_auth(teacher["key"])).json()
    assert body["role"] == "teacher" and body["name"] == "Ms Teacher"
    assert [c["id"] for c in body["classes"]] == [mine] and other not in str(body)


def test_a_key_in_the_url_is_refused_even_if_it_is_right(client, student):
    res = client.get(f"/api/whoami?key={student['key']}", headers=_auth(student["key"]))
    assert res.status_code == 400 and "header" in res.json()["error"]


def test_a_teacher_who_has_left_is_signed_out(client, teacher):
    assert client.get("/api/whoami", headers=_auth(teacher["key"])).status_code == 200
    teachers.leave_teacher(teacher["id"])
    assert client.get("/api/whoami", headers=_auth(teacher["key"])).status_code == 401


# --- teachers ---------------------------------------------------------------------------------------------------


def test_teacher_keys_are_stored_only_as_hashes(teacher):
    row = learner._conn().execute("SELECT * FROM teacher WHERE id = ?", (teacher["id"],)).fetchone()
    assert teacher["key"] not in str(dict(row)) and row["key_hash"] == learner.key_hash(teacher["key"])
    assert teachers.teacher_by_key(teacher["key"])["id"] == teacher["id"]
    assert teachers.teacher_by_key("nope") is None and teachers.teacher_by_key(None) is None


def test_a_teacher_needs_a_name(course):
    with pytest.raises(ValueError):
        teachers.add_teacher("   ")


def test_classes_are_scoped_to_the_teacher(teacher):
    first = learner.add_class("Y12", None)
    second = learner.add_class("Y13", None)
    teachers.assign_class(teacher["id"], first)
    teachers.assign_class(teacher["id"], first)  # twice is fine
    assert teachers.may_see(teacher["id"], first) and not teachers.may_see(teacher["id"], second)
    with pytest.raises(ValueError):
        teachers.assign_class(teacher["id"], "nope")
    with pytest.raises(ValueError):
        teachers.assign_class("nobody", first)


def test_delete_and_purge(course):
    gone = teachers.add_teacher("Gone")
    kept = teachers.add_teacher("Kept")
    teachers.leave_teacher(gone["id"], (datetime.now(timezone.utc) - timedelta(days=400)).date().isoformat())
    teachers.leave_teacher(kept["id"])
    assert teachers.purge_left_teachers() == 1 and teachers.get_teacher(gone["id"]) is None and teachers.get_teacher(kept["id"])
    teachers.delete_teacher(kept["id"])
    for call in (teachers.delete_teacher, teachers.leave_teacher):
        with pytest.raises(ValueError):
            call("nobody")


def test_the_teacher_commands(course, capsys):
    def run(*argv):
        with pytest.raises(SystemExit) as stop:
            cli.main(list(argv))
        out = capsys.readouterr()
        return stop.value.code, out.out, out.err

    code, out, _ = run("teacher", "add", "--name", "Mr Test")
    teacher_id = re.search(r"teacher: (t-\w+)", out).group(1)
    assert code == 0 and "key:" in out
    class_id = learner.add_class("Y12", None)
    assert run("teacher", "assign", "--teacher", teacher_id, "--class", class_id)[0] == 0
    assert run("teacher", "assign", "--teacher", teacher_id, "--class", "nope")[0] == 1
    code, out, _ = run("teacher", "list")
    assert code == 0 and "Mr Test" in out and class_id in out
    assert run("teacher", "leave", "--teacher", teacher_id)[0] == 0
    assert "left" in run("teacher", "list")[1]
    assert run("teacher", "leave", "--teacher", "nobody")[0] == 1
    assert run("teacher", "delete", "--teacher", teacher_id)[0] == 1  # needs --yes
    assert run("teacher", "delete", "--teacher", teacher_id, "--yes")[0] == 0
    assert run("purge")[0] == 0


# --- static checks: privacy and accessibility ---------------------------------------------------------------------


def _static_files(*suffixes):
    return [p for p in STATIC.rglob("*") if p.suffix in suffixes]


def test_no_page_asks_another_origin_for_anything():
    for path in _static_files(".html", ".css", ".js"):
        text = path.read_text(encoding="utf-8").replace("http://www.w3.org/2000/svg", "")  # an XML namespace, not a request
        assert not re.search(r"https?://|//cdn\.|@import\s+url\(\s*['\"]?//", text), f"{path.name} refers to another origin"


def test_no_inline_script_or_style_that_the_policy_would_block():
    for path in _static_files(".html"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"<script(?![^>]*\ssrc=)[^>]*>", text), f"{path.name} has an inline script"
        assert not re.search(r"<style|\sstyle=|\son[a-z]+=", text), f"{path.name} has inline style or an event attribute"


def test_every_referenced_asset_exists():
    for path in _static_files(".html", ".css"):
        text = path.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="(/static/[^"]+)"', text):
            assert (STATIC / ref.removeprefix("/static/")).exists(), f"{path.name}: {ref} is missing"
        for ref in re.findall(r'url\("(\.\./[^"]+)"\)', text):
            assert (path.parent / ref).resolve().exists(), f"{path.name}: {ref} is missing"


def test_fonts_travel_with_their_licences():
    fonts = {p.name for p in (STATIC / "fonts").iterdir()}
    assert "OFL-Atkinson-Hyperlegible-Next.txt" in fonts and "OFL-Newsreader.txt" in fonts
    assert all(" Open Font License" in (STATIC / "fonts" / n).read_text(encoding="utf-8") for n in fonts if n.endswith(".txt"))


def test_the_pages_are_british_english_and_name_their_language():
    for path in _static_files(".html"):
        assert 'lang="en-GB"' in path.read_text(encoding="utf-8")


def _contrast_module():
    spec = importlib.util.spec_from_file_location(
        "check_contrast", Path(__file__).resolve().parent.parent / "scripts" / "check_contrast.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_colour_tokens_meet_the_contrast_rules():
    assert _contrast_module().check() == []


def test_the_contrast_check_catches_a_weak_palette():
    module = _contrast_module()
    css = module.TOKENS.read_text(encoding="utf-8")
    assert module.check(css.replace("--muted: #5a5548", "--muted: #b0aa99", 1))  # muted text too pale
    assert module.check(css.replace("--lv-developing-fill: #5b9a97", "--lv-developing-fill: #e8dfc4", 1))  # two levels merge
