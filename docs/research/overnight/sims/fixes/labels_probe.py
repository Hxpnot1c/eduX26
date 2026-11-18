"""w5-fix-labels probe: what a request_type label on an ANSWER does (05e + combined 0001-0005 [+0006b/0006c]).

    PYTHONPATH=<code copy> /home/vishnu/edux26/.venv/bin/python labels_probe.py <code copy> [--json out.json]

Data goes to fresh folders under /tmp/claude-1000/w5-fix-labels/data/ (never the repo's data/). Deterministic.
Turn 1 sets something to answer; turn 2 is the student's answer with a given request_type label. Cases:
- verify_*: turn 1 = a research question with all four features (the plan sets a Verify task on a fresh student);
  turn 2 = the student's check of a figure, with answer {ail_verify, ail_task, a,c,d}, labelled concept/other/research.
  verify_courseword uses a message with course words (price, demand) to see if a concept label pulls the course focus.
- verify_no_answer_obj: same, but the bot sends no answer object (labelled research): text-only fix territory.
- verify_plus_question: the student checks the figure AND asks a new research question (features given): Ask must
  still be recorded.
- course_answer_*: turn 1 = "explain PED" with node_ids [ped_definition] (sets an explain-back or check); turn 2 = an
  answer to it, labelled research/concept.
Reports: evidence written on turn 2, the plan's moves and parts, the stored focus, the pending literacy task, and
the request_type stored in exchange_log for turn 2.
"""
from __future__ import annotations
import json, os, shutil, sys, contextlib, io
from pathlib import Path

CODE = Path(sys.argv[1]).resolve()
OUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
BASE = Path("/tmp/claude-1000/w5-fix-labels/data/probe")
LAB = {"question_depth": "mechanism", "engagement": "active"}
Q1 = "What was UK CPI inflation in 2022, and why did it change? Sources please."
A2 = "I opened the ONS page and it says 9.1% for October 2022, which matches what you said."
A2_COURSE = "I opened it: the page says prices rose 9.1% and demand fell, which matches what you said."
A2_PLUS = ("I opened the ONS page and it says 9.1%, which matches. So what was UK unemployment in 2022, "
           "and why? Sources please.")
FEAT4 = ["concept", "context", "asks_sources", "asks_reasoning"]
VERIFY = {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "c", "d"]}


def main():
    shutil.rmtree(BASE, ignore_errors=True)
    BASE.mkdir(parents=True)
    os.environ["EDUX_DATA_DIR"] = str(BASE)
    from ingest import load
    from edux import learner, service
    with contextlib.redirect_stdout(io.StringIO()):
        rep = load.load_pack(CODE / "coursepacks/example-mini")
    assert rep.ok, rep.errors
    conn = learner._conn()

    def ev(sid, since):
        return [dict(r) for r in conn.execute(
            "SELECT part_id, evidence_type, score FROM evidence_log WHERE student_id = ? AND ts >= ? ORDER BY id", (sid, since))]

    def issued(sid):
        row = conn.execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (sid,)).fetchone()
        return json.loads(row[0]) if row else {}

    def logged_rt(sid, ts):
        row = conn.execute("SELECT request_type FROM exchange_log WHERE student_id = ? AND ts = ?", (sid, ts)).fetchone()
        return row[0] if row else None

    cases = [
        ("verify", "concept", A2, VERIFY, []), ("verify", "other", A2, VERIFY, []), ("verify", "research", A2, VERIFY, []),
        ("verify_courseword", "concept", A2_COURSE, VERIFY, []), ("verify_courseword", "other", A2_COURSE, VERIFY, []),
        ("verify_courseword", "research", A2_COURSE, VERIFY, []),
        ("verify_no_answer_obj", "research", A2, None, []),
        ("verify_plus_question", "research", A2_PLUS, VERIFY, FEAT4),
        ("course_answer", "research", None, "course", []), ("course_answer", "concept", None, "course", []),
    ]
    t1, t2 = "2026-11-18T10:00:00+00:00", "2026-11-18T10:02:00+00:00"
    results = []
    for i, (kind, rt, msg, ans, feats) in enumerate(cases):
        sid = f"p{i}-{kind}-{rt}"
        learner.add_student(sid, "example-mini", student_id=sid)
        st = learner.get_student(sid)
        if kind.startswith("verify"):
            r1 = service.tutor_turn(st, Q1, {**LAB, "request_type": "research", "web_access": False,
                                              "question_features": FEAT4}, client="claude", at=t1)
        else:
            r1 = service.tutor_turn(st, "Can you explain PED to me?", {**LAB, "request_type": "concept"},
                                    node_ids=["ped_definition"], client="claude", at=t1)
            step = r1["plan"][-1]
            if step["move"] == "ask_mcq":
                letter = next(iter(step["data"]["options"])) if isinstance(step["data"].get("options"), dict) else "A"
                ans = {"part_id": step["part_id"], "type": "mcq", "choice": letter}
                msg = letter
            else:
                ans = {"part_id": step["part_id"], "type": step["data"].get("answer_type", "explain_back"), "points_met": ["a"]}
                msg = "It's how much the quantity demanded responds when the price changes."
        task1 = issued(sid).get("literacy")
        labels = {**LAB, "request_type": rt}
        if feats:
            labels["question_features"] = feats
        r2 = service.tutor_turn(st, msg, labels, answer=ans, client="claude", at=t2)
        after = issued(sid)
        results.append({
            "case": kind, "request_type": rt, "turn1_last_step": [r1["plan"][-1]["move"], r1["plan"][-1]["part_id"]],
            "task_after_t1": task1 and task1.get("skill"), "answer_sent": ans, "ok": r2.get("ok"), "error": r2.get("error"),
            "turn2_evidence": ev(sid, t2), "turn2_steps": [[s["move"], s["part_id"]] for s in r2.get("plan", [])],
            "focus_after_t2": after.get("focus"), "task_after_t2": (after.get("literacy") or {}).get("skill"),
            "logged_request_type": logged_rt(sid, t2)})
    for r in results:
        print(f"{r['case']:22s} {r['request_type']:9s} ev={[(e['part_id'], e['evidence_type'], e['score']) for e in r['turn2_evidence']]} "
              f"steps={r['turn2_steps']} focus={r['focus_after_t2']} task={r['task_after_t2']} logged={r['logged_request_type']}"
              + (f" ERROR {r['error']}" if not r['ok'] else ""))
    if OUT:
        Path(OUT).write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
