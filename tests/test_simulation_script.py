"""The review-threshold simulation script runs end to end (a short, tiny run: it is synthetic and slow at full size)."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "simulate_review_threshold.py"


def test_the_simulation_runs_and_prints_one_row_per_threshold(tmp_path):
    out = subprocess.run([sys.executable, str(SCRIPT), "--students", "2", "--thresholds", "0.5", "0.75", "--days", "45"],
                         capture_output=True, text=True, timeout=120, check=True).stdout
    assert "SYNTHETIC" in out and "Not learning gains" in out
    rows = [line for line in out.splitlines() if line.strip().startswith(("0.50", "0.75"))]
    assert len(rows) == 2
