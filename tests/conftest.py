"""Shared fixtures: the example-mini course loaded into a throwaway data folder.

Each test gets its own databases, so nothing touches ./data and tests can run in any order.
The settings and context are read once (they are cached by the learner module).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from edux import db, graph, learner
from ingest import load

PACK = Path(__file__).resolve().parent.parent / "coursepacks" / "example-mini"


@pytest.fixture()
def course(tmp_path, monkeypatch):
    """Load example-mini into a fresh data folder and point the learner model at it."""
    monkeypatch.setenv("EDUX_DATA_DIR", str(tmp_path))
    report = load.load_pack(PACK, db_path=db.content_db_path())
    assert not report.errors, report.errors
    learner.use_database(db.learner_db_path(), db.content_db_path())
    yield report.course_id
    learner.use_database(None, None)
    graph.use_database(None)


@pytest.fixture()
def student(course):
    """A new student on the example course; returns {"id", "key"}."""
    return learner.add_student("Test Student", course)


@pytest.fixture()
def part(course):
    """The most important part in the example pack."""
    return graph_part()


def graph_part() -> str:
    order = {p: i for i, p in enumerate(learner.all_parts())}
    return sorted(learner.all_parts(), key=lambda p: (-graph.weight(p)["importance"], order[p]))[0]
