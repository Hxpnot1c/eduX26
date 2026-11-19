"""A seeded random soak (scripts/soak_turns.py), run in-process: no crash, results within budget, no server-only item
leaks, and a rebuild from the event logs gives the same derived state. The long version is run by hand with more turns."""

import importlib.util
from pathlib import Path

import pytest

from edux import graph, learner

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "soak_turns.py"


def _soak_module():
    spec = importlib.util.spec_from_file_location("soak_turns", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("seed", [21, 22, 23])
def test_a_random_walk_stays_inside_the_rules(course, monkeypatch, seed):
    monkeypatch.setenv("EDUX_FIND_ERROR", "1")
    monkeypatch.setenv("EDUX_CONFIDENCE", "1")
    student = learner.add_student("soak", course)
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    stats, problems = _soak_module().play(student["id"], parts, 200, seed)
    assert not problems, problems[:5]
    assert stats["over"] <= 10  # over budget is logged, not cut; a few replies with several wrong ideas to name are expected
