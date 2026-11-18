"""Measure false course focus on the frozen test set (focus_testset.py) against one code copy.

    EDUX_DATA_DIR=<fresh dir> PYTHONPATH=<code copy> python focus_measure.py --label NAME [--out results.jsonl]

The script loads example-mini into the (fresh) data dir itself. Two levels:
  (a) resolver: graph.resolve(message) alone;
  (b) end to end: a fresh student per message, service.tutor_turn(message, labels the chatbot would send), then a
      fixed follow-up "go on" (concept); records the focus saved after the message and whether the follow-up plan
      contains a course step (a step on a course part, i.e. not an AI-literacy part).
"""
import argparse, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from focus_testset import TESTSET  # noqa: E402
from focus_holdout import HOLDOUT  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True)
ap.add_argument("--out")
ap.add_argument("--holdout", action="store_true")
args = ap.parse_args()

code = os.environ["PYTHONPATH"].split(":")[0]
data = os.environ["EDUX_DATA_DIR"]
assert data.startswith("/tmp/claude-1000/"), data
if not os.path.exists(os.path.join(data, "content.db")):
    subprocess.run([sys.executable, "-m", "edux.cli", "load", "coursepacks/example-mini"], cwd=code, check=True,
                   capture_output=True)

from edux import graph, learner, service  # noqa: E402


def lineage(i):
    return {i} | {a["id"] for a in graph.ancestors(i)}


def under(ids, expected):
    return bool(ids) and all(lineage(i) & set(expected) for i in ids)


def course(i):
    return i is not None and graph.get_node(i) is not None and not graph.is_literacy(i)


course_id = learner._conn().execute("SELECT id FROM content.course").fetchone()[0]
t0 = datetime(2026, 11, 20, 10, 0, tzinfo=timezone.utc)
rows = []
for n, (cat, req, msg, exp) in enumerate(HOLDOUT if args.holdout else TESTSET):
    r = graph.resolve(msg, [])
    parts, cands = r["parts"], [c["id"] for c in r["candidates"]]
    if exp is None:
        res = "false_focus" if parts else ("false_candidates" if cands else "ok")
    elif parts:
        res = "ok" if under(parts, exp) else "wrong_focus"
    elif cands:
        res = "ok_candidates" if any(lineage(c) & set(exp) for c in cands) else "wrong_candidates"
    else:
        res = "miss"
    # (b) end to end on a fresh student
    sid = f"ff{n:02d}"
    student = learner.add_student(sid, course_id, student_id=sid)
    student = learner.get_student(sid)
    labels = {"question_depth": "surface", "engagement": "active", "request_type": req}
    if req == "research":
        labels.update(question_features=["concept"], web_access=False, asks_recent=False)
    at1 = (t0 + timedelta(minutes=n * 120)).isoformat()
    at2 = (t0 + timedelta(minutes=n * 120, seconds=30)).isoformat()
    out1 = service.tutor_turn(student, msg, labels, at=at1)
    saved = service._last_plan(sid)["focus"]
    out2 = service.tutor_turn(student, "go on", {"question_depth": "surface", "engagement": "passive",
                                                 "request_type": "concept"}, at=at2)
    follow = [(s["move"], s.get("part_id")) for s in out2.get("plan", [])]
    course_follow = [m for m in follow if course(m[1])]
    tagged = sorted({i for (ids,) in learner._conn().execute(
        "SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts <= ?", (sid, at1)) for i in ids.split(";") if i})
    saved_bad = bool(saved) and (exp is None or not under(saved, exp))
    rows.append({"label": args.label, "n": n, "cat": cat, "req": req, "msg": msg, "expected": exp,
                 "parts": parts, "candidates": cands, "resolver": res, "ok1": out1.get("ok"),
                 "turn1_moves": [(s["move"], s.get("part_id")) for s in out1.get("plan", [])],
                 "saved_focus": saved, "saved_bad": saved_bad, "follow": follow,
                 "follow_course": bool(course_follow), "tagged_course": [t for t in tagged if course(t)]})

none_rows = [x for x in rows if x["expected"] is None]
exp_rows = [x for x in rows if x["expected"] is not None]
ff = sum(x["resolver"] == "false_focus" for x in none_rows)
fc = sum(x["resolver"] == "false_candidates" for x in none_rows)
hit = sum(x["resolver"] in ("ok", "ok_candidates") for x in exp_rows)
wrong = sum(x["resolver"] in ("wrong_focus",) for x in exp_rows)
print(f"[{args.label}] resolver: false focus {ff}/{len(none_rows)}, false candidates {fc}/{len(none_rows)}; "
      f"genuine resolved right {hit}/{len(exp_rows)} (wrong part {wrong})")
sb = sum(x["saved_bad"] for x in none_rows)
fcourse = sum(x["follow_course"] for x in none_rows)
keep = sum(bool(x["saved_focus"]) and not x["saved_bad"] for x in exp_rows)
tag_bad = sum(bool(x["tagged_course"]) for x in none_rows)
print(f"[{args.label}] end to end: saved false focus {sb}/{len(none_rows)}; course step in follow-up {fcourse}/{len(none_rows)}; "
      f"exchange tagged on a course part {tag_bad}/{len(none_rows)}; genuine saved right focus {keep}/{len(exp_rows)}")
for cat in ("research", "verify", "homework", "nameword", "chat"):
    sub = [x for x in rows if x["cat"] == cat]
    sn = [x for x in sub if x["expected"] is None]
    se = [x for x in sub if x["expected"] is not None]
    print(f"   {cat:9s} n={len(sub):2d}  resolver FF {sum(x['resolver']=='false_focus' for x in sn)}/{len(sn)} "
          f"FC {sum(x['resolver']=='false_candidates' for x in sn)}/{len(sn)}  saved-bad {sum(x['saved_bad'] for x in sub)}/{len(sub)} "
          f"follow-course(none-rows) {sum(x['follow_course'] for x in sn)}/{len(sn)}  genuine hit {sum(x['resolver'] in ('ok','ok_candidates') for x in se)}/{len(se)} "
          f"genuine saved {sum(bool(x['saved_focus']) and not x['saved_bad'] for x in se)}/{len(se)}")
if args.out:
    with open(args.out, "a") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
