"""Smoke test of the driver's flow emulation against the 05e branch's real service.tutor_turn.

Four scripted sessions go through tutor_turn on a throwaway EDUX_DATA_DIR. The literacy evidence that tutor_turn
writes (evidence_log) is printed next to what lit_model's driver logic predicts for the same script:
  A. a 1-feature research question (Ask task), then two non-research turns -> ail_task 0 on ail_ask
  B. a 2-feature question -> ail_question 0.5 (counts as wrong at correct_share 0.67) and a Verify task
  C. a 3-feature question, verify task answered with 2 ticks -> ail_task 0.5 on ail_verify
  D. a 3-feature question, verify task ignored for two turns -> ail_task 0 on ail_verify
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate import fresh_data_dir  # noqa: E402

fresh_data_dir()
from edux import learner, service  # noqa: E402

sid = learner.add_student("smoke", "example-mini")["id"]
student = learner.get_student(sid)


def turn(at, msg, labels, answer=None, node_ids=None):
    lab = {"question_depth": "surface", "engagement": "active", **labels}
    r = service.tutor_turn(student, msg, lab, node_ids=node_ids, answer=answer, at=at)
    moves = [s["move"] + (f"({s['data'].get('skill')})" if s["move"] in ("literacy_task", "reask") else "")
             for s in r.get("plan", r.get("steps", []))] if r.get("ok", True) else r
    return moves


def ev_since(at):
    rows = learner._conn().execute("SELECT ts, part_id, evidence_type, score, check_id FROM evidence_log "
                                   "WHERE student_id = ? AND ts >= ? ORDER BY id", (sid, at)).fetchall()
    return [dict(r) for r in rows]


hw = {"request_type": "homework"}
out = {}
# A
a = "2026-09-07T17:00:00+00:00"
out["A"] = {"turns": [turn(a, "what is inflation", {"request_type": "research", "question_features": ["concept"]}),
                      turn("2026-09-07T17:03:00+00:00", "ok, how do I draw a demand curve?", hw),
                      turn("2026-09-07T17:06:00+00:00", "and supply?", hw),
                      turn("2026-09-07T17:09:00+00:00", "thanks", hw),
                      turn("2026-09-07T17:12:00+00:00", "ok", hw)],
            "evidence": ev_since(a),
            "driver_predicts": "ail_question 0.25 on ail_ask; then ail_task 0.0 on ail_ask once re-asked and not done "
                               "(turn 2 if the plan had room for the re-ask, else after max_waits)"}
# B
b = "2026-09-09T17:00:00+00:00"
out["B"] = {"turns": [turn(b, "what was UK CPI in Feb 2025", {"request_type": "research",
                                                              "question_features": ["concept", "context"]})],
            "evidence": ev_since(b), "driver_predicts": "ail_question 0.5 (wrong at correct_share 0.67); a verify task"}
# C
c = "2026-09-11T17:00:00+00:00"
out["C"] = {"turns": [turn(c, "what was UK CPI in Feb 2025 and give sources", {"request_type": "research",
                      "question_features": ["concept", "context", "asks_sources"]}),
                      turn("2026-09-11T17:03:00+00:00", "I opened the ONS page and it matched",
                           hw, answer={"part_id": "ail_verify", "type": "ail_task", "points_met": ["ail_verify_p1", "ail_verify_p4"]})],
            "evidence": ev_since(c), "driver_predicts": "ail_question 0.75; ail_task 0.5 on ail_verify"}
# D
d = "2026-09-13T17:00:00+00:00"
out["D"] = {"turns": [turn(d, "what was UK CPI in Feb 2025 and give sources", {"request_type": "research",
                      "question_features": ["concept", "context", "asks_sources"]}),
                      turn("2026-09-13T17:03:00+00:00", "how do I draw a demand curve?", hw),
                      turn("2026-09-13T17:06:00+00:00", "and supply?", hw),
                      turn("2026-09-13T17:09:00+00:00", "what about elasticity", hw),
                      turn("2026-09-13T17:12:00+00:00", "ok", hw)],
            "evidence": ev_since(d), "driver_predicts": "ail_question 0.75; ail_task 0.0 on ail_verify after the re-ask"}
(HERE / "results").mkdir(exist_ok=True)
(HERE / "results" / "smoke_tutor_turn.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
