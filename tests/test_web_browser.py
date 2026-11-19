"""A real browser loads the pages from a live server: the map draws one disc per part, the views switch, nothing fails.
Skipped when no Chromium or Chrome is installed (CI installs none by default)."""

import shutil
import socket
import subprocess
import threading
import time

import pytest
import uvicorn

from edux import graph, learner, server

BROWSER = next((b for b in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable") if shutil.which(b)), None)
pytestmark = pytest.mark.skipif(BROWSER is None, reason="no Chromium or Chrome installed")


@pytest.fixture()
def live(course):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    srv = uvicorn.Server(uvicorn.Config(server.http_app(), host="127.0.0.1", port=port, log_level="error", access_log=False))
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    srv.should_exit = True
    thread.join(timeout=5)


def _dom(tmp_path, url):
    out = subprocess.run(
        [
            BROWSER,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={tmp_path}",
            "--virtual-time-budget=6000",
            "--dump-dom",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return out.stdout


def test_the_map_draws_a_disc_for_every_part(live, tmp_path):
    dom = _dom(tmp_path, f"{live}/map")
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    assert dom.count('class="node disc plain"') == len(parts)
    assert "Showing the public example course" in dom and 'aria-pressed="true"' in dom


def test_the_path_and_list_views_open_from_a_link(live, tmp_path):
    assert "Not linked into a path" in _dom(tmp_path, f"{live}/map?view=path")
    listed = _dom(tmp_path, f"{live}/map?view=list")
    assert "<table" in listed and "Needs first" in listed


def test_selecting_a_part_shows_what_it_needs_first(live, tmp_path):
    dom = _dom(tmp_path, f"{live}/map?select=ped_formula")
    assert "PED: formula and calculation" in dom and "Needs first" in dom


def test_a_student_key_in_the_fragment_signs_in_and_leaves_the_address_clean(live, student, tmp_path):
    dom = _dom(tmp_path, f"{live}/me#key={student['key']}")
    assert "Signed in as a" in dom and student["key"] not in dom


def test_the_student_page_draws_their_record(live, student, part, tmp_path):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    dom = _dom(tmp_path, f"{live}/me#key={student['key']}")
    assert "Ready for a check" in dom and "What next" in dom and "My record" in dom and "Copy" in dom
    assert dom.count('class="node disc ') >= len([p for p in learner.all_parts() if not graph.is_literacy(p)])
    assert "1 answer, last today" in dom  # the note on the answered part's disc is in its accessible label
    assert student["key"] not in dom and "**" not in dom


def test_a_teacher_key_on_the_student_page_gets_a_plain_refusal(live, tmp_path):
    from edux import teachers

    key = teachers.add_teacher("Ms T")["key"]
    dom = _dom(tmp_path, f"{live}/me#key={key}")
    assert "This key is for a teacher, and this page is for a student." in dom
    assert '<div id="me" hidden' in dom  # the student's sections stay hidden


def test_the_teacher_page_shows_a_class_and_never_a_student(live, tmp_path):
    from edux import demo, teachers

    demo.seed(pupils=8)
    teacher = teachers.add_teacher("Ms T")
    teachers.assign_class(teacher["id"], demo.CLASS_ID)
    dom = _dom(tmp_path, f"{live}/teacher#key={teacher['key']}")
    assert "Seeded data" in dom and "Class map" in dom and "Common wrong ideas" in dom and "Asking to be shown" in dom
    assert "demo-pupil" not in dom and "Synthetic pupil" not in dom and teacher["key"] not in dom
    assert 'id="class-body" hidden' not in dom  # the class sections were revealed once the class loaded
