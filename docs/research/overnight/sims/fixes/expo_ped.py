"""The live-expo PED run (demo-plan.md §B, 1:30-3:00) in-process on a code copy, after seed-demo --reset (w4-fix-core).

    EDUX_DATA_DIR=<fresh dir> PYTHONPATH=<copy> python expo_ped.py <copy>
For demo-weak: the PED question, the wrong letter (the "price changes when demand changes" option, else any wrong
one), the right letter, then six more right letters; prints each plan and ped_definition / ped_formula p_now.
For demo-secure and demo-showme: the first plan on the same question.
"""
import contextlib, io, json, subprocess, sys
from datetime import datetime, timedelta, timezone

code = sys.argv[1]
py = sys.executable
for args in (["load", "coursepacks/example-mini"], ["seed-demo", "--reset"]):
    subprocess.run([py, "-m", "edux.cli", *args], cwd=code, check=True, capture_output=True)
from edux import learner, service  # noqa: E402

lab = {"question_depth": "surface", "engagement": "active"}
t0 = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=1)


def show(out):
    return " / ".join(f"{s['move']}:{s['part_id']}" + (f":{s['data'].get('purpose')}" if s["move"] == "ask_mcq" else "")
                      + (":stuck" if s["data"].get("stuck") else "") for s in out.get("plan", [])) or out.get("error", "")


def mcq(sid):
    row = learner._conn().execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (sid,)).fetchone()
    return (json.loads(row[0]) if row else {}).get("mcq") or {}


for sid in ("demo-secure", "demo-showme"):
    st = learner.get_student(sid)
    print(f"{sid}: {show(service.tutor_turn(st, 'How do I calculate price elasticity of demand?', lab, at=learner._event_ts(t0)))}")

sid = "demo-weak"
st = learner.get_student(sid)
at = [t0]


def turn(msg, answer=None):
    at[0] += timedelta(seconds=70)
    return service.tutor_turn(st, msg, lab, answer=answer, at=learner._event_ts(at[0]))


def p(part):
    return round(learner.part_p(sid, part, learner._event_ts(at[0])), 3)


print(f"{sid} turn 0: {show(turn('How do I calculate price elasticity of demand?'))} | ped_definition {p('ped_definition')} ped_formula {p('ped_formula')}")
for k, want in enumerate(["wrong"] + ["right"] * 7, 1):
    m = mcq(sid)
    if not m:
        print(f"{sid} turn {k}: no MCQ waiting; stop")
        break
    opts = sorted(m["options"].items())
    if want == "right":
        letter = next(l for l, o in opts if o["id"] == "correct")
    else:
        letter = next((l for l, o in opts if o["id"] != "correct" and "price changes when demand" in o.get("text", "")),
                      next(l for l, o in opts if o["id"] != "correct"))
    out = turn(letter, {"part_id": m["part_id"], "type": "mcq", "choice": letter})
    print(f"{sid} turn {k} ({want} on {m['part_id']}:{m['purpose']}): {show(out)} | ped_definition {p('ped_definition')} ped_formula {p('ped_formula')}")
