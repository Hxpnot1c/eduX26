"""Extra demo-05e scenarios for w4-fix-focus: a session that already has a genuine course focus (PED) before the
literacy episode. Wraps ../demo-05e/run_episode.py (same args) and adds the scenarios to its SCENARIOS table.
    cd ../demo-05e && python ../fixes/focus_episode_extra.py --code /tmp/claude-1000/w3-07/<copy> --label L --out ../fixes/captures-focus --scenario ped_first ped_first_as_written"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "demo-05e"))
import scenarios as S  # noqa: E402
import run_episode  # noqa: E402

S.SCENARIOS.update({
    "ped_first": {"about": "a judge asks the PED question first, then the clean literacy episode (pick m1)",
                  "turns": [S.PED, S.T1, S.T2C, S.T3C, S.T4_M1, S.PROGRESS]},
    "ped_first_as_written": {"about": "PED first, then the as-written literacy lines",
                             "turns": [S.PED, S.T1, S.T2, S.T3, S.T4_M1, S.PROGRESS]},
})
run_episode.SCENARIOS = S.SCENARIOS
run_episode.main()
