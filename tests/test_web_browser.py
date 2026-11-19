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
