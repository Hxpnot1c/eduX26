"""A pack with subtopics (topic > subtopic > concept > part), as the Edexcel pack has: the student's concept network, the
course map and the demo teacher view group by subtopic, and every part appears as a part."""

import csv
import shutil
from pathlib import Path

import pytest

from edux import db, demo, graph, learner
from edux.web import review, views
from ingest import load

PACK = Path(__file__).resolve().parent.parent / "coursepacks" / "example-mini"


@pytest.fixture()
def four_level(tmp_path, monkeypatch):
    """example-mini with its two topics moved under one new top-level topic, so they become subtopics."""
    pack = tmp_path / "pack"
    shutil.copytree(PACK, pack)
    path = pack / "nodes.csv"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0])
    top = {**{k: "" for k in fields}, "id": "theme_x", "level": "topic", "name": "Theme X", "description": "A theme.", "status": "approved"}
    for r in rows:
        if r["level"] == "topic":
            r["level"], r["parent_id"] = "subtopic", "theme_x"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows([top] + rows)
    monkeypatch.setenv("EDUX_DATA_DIR", str(tmp_path / "data"))
    (tmp_path / "data").mkdir()
    report = load.load_pack(pack, db_path=db.content_db_path())
    assert not report.errors, report.errors
    learner.use_database(db.learner_db_path(), db.content_db_path())
    yield report.course_id
    learner.use_database(None, None)
    graph.use_database(None)


def _parts():
    return sorted(p for p in learner.all_parts() if not graph.is_literacy(p))


def test_sections_are_the_subtopics(four_level):
    assert [t["id"] for t in graph.topics()] == ["theme_x"]
    assert [s["id"] for s in graph.sections()] == ["elasticities", "indirect_taxes"]
    assert graph.section_of("ped_formula")["id"] == "elasticities"


def test_the_course_map_shows_every_part_as_a_part(four_level):
    nodes = views.course_map()["nodes"]
    assert sorted(n["id"] for n in nodes if n["level"] == "part") == _parts()
    assert [n["id"] for n in nodes if n["level"] == "topic"] == ["elasticities", "indirect_taxes"]


def test_the_students_network_has_every_part_grouped_by_subtopic(four_level):
    student = learner.add_student("S", four_level)
    net = views.student_page(learner.get_student(student["id"]))["network"]
    assert sorted(n["id"] for n in net["nodes"]) == _parts()
    assert [b["id"] for b in net["bands"]] == ["elasticities", "indirect_taxes"]
    assert {n["band"] for n in net["nodes"]} == {"elasticities", "indirect_taxes"} and all(n["concept"] for n in net["nodes"])


def test_the_demo_teacher_view_groups_by_subtopic(four_level):
    demo.seed_class_demo(four_level)
    r = review.class_review(demo.DEMO_CLASS_ID)
    assert [t["id"] for t in r["topics"]] == ["elasticities", "indirect_taxes"]
    assert {t["id"] for t in r["test"]["topics"]} <= {"elasticities", "indirect_taxes"} and r["test"]["topics"]


def test_a_student_is_at_developing_in_a_topic_when_half_their_answered_parts_are():
    levels = {"a": "secure", "b": "developing", "c": "needs_review", "d": "new"}
    assert review._at_developing(levels, {"a", "b", "c", "d"})
    assert not review._at_developing(levels, {"a", "c", "d"})
    assert not review._at_developing(levels, set())
