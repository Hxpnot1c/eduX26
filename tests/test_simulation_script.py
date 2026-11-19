"""The simulation scripts run end to end (short, tiny runs: they are synthetic and slow at full size)."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "simulate_review_threshold.py"


def test_the_simulation_runs_and_prints_one_row_per_threshold(tmp_path):
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--students", "2", "--thresholds", "0.5", "0.75", "--days", "45"],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    ).stdout
    assert "SYNTHETIC" in out and "Not learning gains" in out
    rows = [line for line in out.splitlines() if line.strip().startswith(("0.50", "0.75"))]
    assert len(rows) == 2


CLASS_SCRIPT = SCRIPT.parent / "simulate_class_levels.py"


def test_the_class_simulation_runs_and_counts_every_shown_level(tmp_path):
    out = subprocess.run(
        [sys.executable, str(CLASS_SCRIPT), str(tmp_path / "out.json"), "--students", "3", "--days", "14"],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    ).stdout
    assert "SYNTHETIC" in out and "Not learning gains" in out
    data = json.loads((tmp_path / "out.json").read_text())
    weeks = data["B_final_only"]["weeks"]
    assert [w["week"] for w in weeks] == [1, 2]
    for w in weeks:
        assert set(w["shown"]) == {"new", "needs_review", "taught_in_class", "developing", "secure"}
        assert abs(sum(w["shown"].values()) - 1) < 0.01 and abs(sum(w["by_number"].values()) - 1) < 0.01
        assert w["reviews_per_student"] >= 0 and w["backlog_per_student"] >= 0
