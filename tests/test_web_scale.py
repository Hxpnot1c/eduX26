"""The map with a large course: a generated pack of 300 parts is loaded through the real ingest and the real page is
timed in a browser. Large concepts collapse to one disc, nothing overlaps off the page, and drawing stays quick."""

import csv
import shutil
import socket
import subprocess
import threading
import time

import pytest
import uvicorn

from edux import db, graph, learner, server
from edux.web import views
from ingest import load
from tests.conftest import PACK
from tests.test_web_browser import BROWSER

TOPICS, CONCEPTS, PARTS = 8, 5, 7  # 8 x 5 x 7 = 280 parts, plus the larger concepts below
BIG = 20  # every fifth concept has this many parts, so it collapses


def _write(path, rows, header):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _rows(path, rows):
    header = next(csv.reader(path.open(encoding="utf-8")))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows({k: row.get(k, "") for k in header} for row in rows)


def make_pack(target):
    """The example pack with its graph replaced by a generated one: TOPICS x CONCEPTS concepts, PARTS parts each (BIG in
    every third concept), the parts chained by prerequisite links. Everything else in the pack is emptied."""
    shutil.copytree(PACK, target)
    base = {"source_ids": "spec", "extraction_confidence": 1.0, "status": "approved", "updated_by": "gen"}
    nodes, edges, parts = [], [], []
    for t in range(TOPICS):
        nodes.append({**base, "id": f"t{t}", "level": "topic", "name": f"Topic {t}", "spec_ref": str(t + 1), "description": f"Topic {t}."})
        for c in range(CONCEPTS):
            cid = f"t{t}c{c}"
            nodes.append(
                {
                    **base,
                    "id": cid,
                    "parent_id": f"t{t}",
                    "level": "concept",
                    "name": f"Concept {t}.{c} with a longer name",
                    "spec_ref": f"{t + 1}.{c + 1}",
                    "description": "A concept.",
                }
            )
            for p in range(BIG if c == 2 else PARTS):
                pid = f"{cid}p{p}"
                nodes.append(
                    {
                        **base,
                        "id": pid,
                        "parent_id": cid,
                        "level": "part",
                        "name": f"Part {t}.{c}.{p} calculating the thing",
                        "part_type": "calculation",
                        "description": "A part.",
                        "intuition": "Think of it simply.",
                    }
                )
                if parts:
                    edges.append(
                        {
                            **base,
                            "from_id": parts[-1],
                            "to_id": pid,
                            "type": "prerequisite",
                            "note": "Comes first.",
                            "confidence": 0.9,
                            "teach_use": "intuition",
                        }
                    )
                parts.append(pid)
    _rows(target / "nodes.csv", nodes)
    _rows(target / "edges.csv", edges)
    for name in (
        "mark_points",
        "misconceptions",
        "notes",
        "questions",
        "past_papers",
        "exam_papers",
        "mark_scheme_items",
        "trusted_sources",
        "id_map",
    ):
        _rows(target / f"{name}.csv", [])
    return len(parts)


@pytest.fixture()
def big(tmp_path, monkeypatch):
    monkeypatch.setenv("EDUX_DATA_DIR", str(tmp_path / "data"))
    pack = tmp_path / "pack"
    n = make_pack(pack)
    report = load.load_pack(pack, db_path=db.content_db_path())
    assert report.ok, report.errors[:3]
    learner.use_database(db.learner_db_path(), db.content_db_path())
    yield n
    learner.use_database(None, None)
    graph.use_database(None)


def test_the_view_serves_a_large_course_quickly(big):
    started = time.perf_counter()
    data = views.course_map()
    elapsed = time.perf_counter() - started
    assert len([n for n in data["nodes"] if n["level"] == "part"]) == big and len(data["edges"]) == big - 1
    assert elapsed < 3.0, f"{elapsed:.1f}s to build a {big}-part map"


@pytest.mark.skipif(BROWSER is None, reason="no Chromium or Chrome installed")
def test_a_large_map_collapses_big_concepts_and_draws_quickly(big, tmp_path, monkeypatch):
    monkeypatch.setattr(views, "EXAMPLE_COURSE_ID", views.course_for(None)["id"])  # let the generated course be the public one
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
    try:

        def dom(query):
            return subprocess.run(
                [
                    BROWSER,
                    "--headless=new",
                    "--no-sandbox",
                    "--disable-gpu",
                    f"--user-data-dir={tmp_path}/b",
                    "--virtual-time-budget=9000",
                    "--dump-dom",
                    f"http://127.0.0.1:{port}/map{query}",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            ).stdout

        page = dom("")
        collapsed = page.count('class="node collapsed"')
        assert collapsed == TOPICS, f"{collapsed} collapsed concepts"  # one big concept per topic
        assert page.count('class="node disc plain"') == TOPICS * (CONCEPTS - 1) * PARTS  # the rest are drawn as discs
        ms = int(page.split('data-draw-ms="')[1].split('"')[0])
        print(f"\n{big} parts drawn in {ms} ms")
        assert ms < 1500, f"{ms} ms to draw {big} parts"
        listed = dom("?view=list")
        assert listed.count("<tr>") >= big  # the accessible list has a row for every part
    finally:
        srv.should_exit = True
        thread.join(timeout=5)
