"""A short random soak (scripts/soak_turns.py): no crash, results within budget, no server-only item leaks, and a
rebuild from the event logs gives the same derived state. The long version is run by hand with more turns and seeds."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "soak_turns.py"


@pytest.mark.parametrize("seed", [21, 22])
def test_a_short_random_walk_stays_inside_the_rules(seed):
    out = subprocess.run([sys.executable, str(SCRIPT), "--turns", "150", "--seed", str(seed)], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0 and "soak: ok" in out.stdout, out.stdout[-800:] + out.stderr[-800:]
