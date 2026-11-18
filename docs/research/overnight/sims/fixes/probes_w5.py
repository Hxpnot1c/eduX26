"""Wave-5 probes for the residuals after 0001-0005 (w5-fix-residual). Deterministic; no randomness.

Copy this file into <code copy>/docs/research/overnight/sims/fixes/ (next to a copy of sims/edux_sim.py) and run
    PYTHONPATH=<code copy> /home/vishnu/edux26/.venv/bin/python <copy>/docs/research/overnight/sims/fixes/probes_w5.py <data dir> [--json out.json]
edux_sim.ROOT then resolves to the code copy, so its own settings.toml, text/ and coursepack are used.

A. stuck: a student who misses every check and every explain-back on ped_formula (prerequisite checks right),
   30 turns; after a plan with nothing to answer they say "OK, let's keep going." Reports each plan, the longest run
   of plans with no multiple-choice question, the longest run of bare reteaches (feedback + reteach only), and the turn
   of the first stop-or-switch offer. Also a recovering student (misses until the step back, then right) and a
   student who misses only open answers (no MCQs missed), and a strong student who misses only the harder
   (extend) questions, who should never get the ladder.
B. review requests: 30 messages in our own words (18 asking for the due reviews, 12 that don't), each to a fresh
   student who studied two parts 5 days ago and YED just before. Conditions: due + request_type concept; due +
   request_type other; due, 2 minutes after a pending check (same session); nothing due.
"""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edux_sim as S   # noqa: E402

LAB = {"question_depth": "mechanism", "engagement": "active"}

# (message, wants the due reviews?, request_type). Our own words; no exam-board text.
MESSAGES = [
    ("Quiz me on what's due.", True, "concept"),
    ("quiz me", True, "concept"),
    ("Can you test me on my reviews?", True, "concept"),
    ("What should I revise?", True, "concept"),
    ("do my reviews", True, "concept"),
    ("Let's do some revision", True, "concept"),
    ("Test me!", True, "concept"),
    ("What's due today?", True, "concept"),
    ("anything due?", True, "concept"),
    ("Can we go through my reviews please", True, "concept"),
    ("what needs revising", True, "concept"),
    ("help me revise", True, "concept"),
    ("quiz me on stuff I've done before", True, "concept"),
    ("I want to revise, what should I work on?", True, "concept"),
    ("drill me on older topics", True, "concept"),
    ("Time for a revision session", True, "concept"),
    ("start my reviews", True, "concept"),
    ("Give me some practice questions on what’s due", True, "concept"),
    ("Can you explain that again?", False, "concept"),
    ("Quiz me on this", False, "concept"),
    ("test me on what we just did", False, "concept"),
    ("How should I revise for the exam?", False, "concept"),
    ("I did my revision yesterday but I still don't get it", False, "concept"),
    ("What is due to the fall in supply?", False, "concept"),
    ("Is my review of this article right?", False, "research"),
    ("Can you check my working?", False, "concept"),
    ("Quiz me on price elasticity of demand", False, "concept"),
    ("How do my reviews work?", False, "concept"),
    ("Why is that the answer?", False, "concept"),
    ("Give me another example", False, "concept"),
]

# Written after the patterns were frozen and run once, untuned: how far the patterns carry to new wordings.
HOLDOUT = [
    ("Ask me some questions on the old stuff", True, "concept"),
    ("can you give me my spaced repetition questions", True, "concept"),
    ("What have I forgotten?", True, "concept"),
    ("I've got 10 minutes, test me on something", True, "concept"),
    ("Let's practise what I learned last week", True, "concept"),
    ("Which topics should I go over today?", True, "concept"),
    ("hit me with a review question", True, "concept"),
    ("Quiz me pls", True, "concept"),
    ("Can you check what I've remembered?", True, "concept"),
    ("Is there anything I should review?", True, "concept"),
    ("Can you test my understanding of this graph?", False, "concept"),
    ("what do you mean by that", False, "concept"),
    ("Could you quiz me on that last bit again?", False, "concept"),
    ("Is revision better in the morning or evening?", False, "concept"),
    ("Can you mark my answer?", False, "concept"),
    ("That's due on Friday, can you help me plan the essay?", False, "concept"),
]


def main(data_dir: str, out_json: str | None = None) -> None:
    S.setup_data_dir(data_dir)
    S.use_settings("current")
    from edux import learner, service
    learner._save_state = S._ORIG.get("orig_save", learner._save_state)
    t0 = S.EXAM - timedelta(days=30)
    result: dict = {"stuck": {}, "reviews": {}}

    # ---------------- A. stuck ----------------
    def stuck_run(sid: str, turns: int, miss_mcq, miss_open) -> dict:
        learner.add_student(sid, "example-mini", student_id=sid)
        st = learner.get_student(sid)
        clock = [t0]
        n_mcq = [0]

        def turn(msg, node_ids=None, answer=None):
            clock[0] += timedelta(minutes=2)
            return service.tutor_turn(st, msg, LAB, node_ids=node_ids, answer=answer, at=S.iso(clock[0]))

        out = turn("How do I calculate PED?", node_ids=["ped_formula"])
        plans = []
        for _ in range(turns):
            pj = S._plan_json(sid)
            m = pj.get("mcq")
            ask = next((s for s in reversed(pj.get("plan") or []) if s["data"].get("answer_type")), None)
            if m and ask and ask["move"] == "ask_mcq":
                on_focus = m["part_id"] == "ped_formula" and m["purpose"] == "check"
                n_mcq[0] += on_focus   # counts checks on ped_formula only
                wrong = on_focus and miss_mcq(n_mcq[0])
                options = m["options"]
                letter = next(k for k, o in sorted(options.items()) if (o["id"] == "correct") != wrong)
                out = turn(letter, answer={"part_id": m["part_id"], "type": "mcq", "choice": letter})
            elif ask:
                letters = [] if miss_open(ask["data"]["answer_type"]) else [p["id"] for p in service.plan.lettered(ask["part_id"])]
                out = turn("I think it is about price.", answer={"part_id": ask["part_id"], "type": ask["data"]["answer_type"],
                                                                  "points_met": letters})
            else:
                out = turn("OK, let's keep going.")
            if not out.get("ok"):
                plans.append("ERROR " + str(out.get("error")))
                continue
            plans.append("/".join(f"{s['move']}:{s['part_id']}" + (":stuck" if s["data"].get("stuck") else "")
                                  + (":" + s["data"]["purpose"] if s["data"].get("purpose") else "")
                                  + (f"#{s['data']['index']}" if s["move"] == "ask_mcq" and s["data"].get("index") else "")
                                  for s in out["plan"]))
        no_q = best_no_q = bare = best_bare = 0
        first_offer = None
        for i, p in enumerate(plans, 1):
            moves = [x.split(":")[0] for x in p.split("/")]
            no_q = 0 if "ask_mcq" in moves else no_q + 1
            best_no_q = max(best_no_q, no_q)
            bare = bare + 1 if moves and moves[-1] == "reteach" and "ask_mcq" not in moves else 0
            best_bare = max(best_bare, bare)
            if first_offer is None and "offer_stop" in moves:
                first_offer = i
        return {"plans": plans, "longest_no_mcq_run": best_no_q, "longest_bare_reteach_run": best_bare,
                "first_offer_stop_turn": first_offer, "mcq_plans": sum("ask_mcq" in p for p in plans),
                "worked_examples": sum("show:" in p for p in plans)}

    runs = {
        "always_misses": stuck_run("a1", 30, lambda n: True, lambda a: True),
        "recovers_after_step_back": stuck_run("a2", 20, lambda n: n <= 3, lambda a: False),
        "misses_open_only": stuck_run("a3", 20, lambda n: False, lambda a: True),
        # strong student: every check and explain-back right, every harder (extend) question missed -> no ladder
        "strong_misses_extend": stuck_run("a4", 10, lambda n: False, lambda a: a == "extend"),
    }
    for name, r in runs.items():
        print(f"A. {name}: longest run with no MCQ {r['longest_no_mcq_run']}, longest bare-reteach run "
              f"{r['longest_bare_reteach_run']}, first stop/switch offer at turn {r['first_offer_stop_turn']}, "
              f"{r['mcq_plans']}/{len(r['plans'])} plans with an MCQ, {r['worked_examples']} worked examples")
        for i, p in enumerate(r["plans"], 1):
            print(f"   turn {i}: {p}")
    result["stuck"] = runs

    # ---------------- B. review requests ----------------
    def review_case(k: int, msg: str, request_type: str, condition: str, label: bool | None = None) -> str:
        sid = f"b-{condition}-{k}"
        learner.add_student(sid, "example-mini", student_id=sid)
        st = learner.get_student(sid)
        if condition != "none_due":   # two parts studied 5 days ago are due for review by now
            for i, part in enumerate(["pes_definition", "pes_formula"]):
                learner.record_evidence(sid, part, "explain_back", 1.0, ts=S.iso(t0 + timedelta(minutes=i)), apply="now")
        if condition == "pending":   # YED taught just now, its check waiting; they ask this instead (same session)
            yed_at = t0 + timedelta(days=5)
            later = yed_at + timedelta(minutes=2)
        else:                        # YED was the focus 5 days ago; this opens a new session
            yed_at = t0 + timedelta(minutes=5)
            later = t0 + timedelta(days=5)
        service.tutor_turn(st, "Can you help me with YED?", LAB, node_ids=["yed_definition"], at=S.iso(yed_at))
        labels = {**LAB, "request_type": request_type}
        if label is not None:   # the chatbot's asks_for_reviews label (step 0006); an older server ignores it
            labels["asks_for_reviews"] = label
        out = service.tutor_turn(st, msg, labels, at=S.iso(later))
        if not out.get("ok"):
            return "error"
        plan = out["plan"]
        if any(s["move"] == "ask_mcq" and s["data"].get("purpose") == "review" for s in plan):
            return "review"
        if not plan:
            return "empty"
        if plan[-1]["move"] == "reask":
            return "reask"
        return "focus:" + ",".join(dict.fromkeys(s["part_id"] or "-" for s in plan))

    for condition, override in (("due_concept", None), ("due_other", "other"), ("pending", None), ("none_due", None)):
        rows = []
        for k, (msg, wants, rtype) in enumerate(MESSAGES):
            rtype2 = override if override and rtype == "concept" else rtype
            got = review_case(k, msg, rtype2, condition)
            ok = (got == "review") == (wants and condition != "none_due")
            if condition == "none_due" and wants:
                ok = got.startswith("focus")   # nothing due: stay on the topic, never an empty plan
            rows.append({"message": msg, "wants_reviews": wants, "request_type": rtype2, "got": got, "as_expected": ok})
        hits = sum(r["got"] == "review" for r in rows if r["wants_reviews"])
        stolen = sum(r["got"] == "review" for r in rows if not r["wants_reviews"])
        n_pos = sum(r["wants_reviews"] for r in rows)
        print(f"B. {condition}: review asks answered with a review {hits}/{n_pos}; ordinary messages turned into a "
              f"review {stolen}/{len(rows) - n_pos}; as expected {sum(r['as_expected'] for r in rows)}/{len(rows)}")
        for r in rows:
            if not r["as_expected"]:
                print(f"   unexpected: {r['message']!r} ({r['request_type']}) -> {r['got']}")
        result["reviews"][condition] = rows
    rows = []
    for k, (msg, wants, rtype) in enumerate(HOLDOUT):
        got = review_case(100 + k, msg, rtype, "due_concept")
        rows.append({"message": msg, "wants_reviews": wants, "got": got, "as_expected": (got == "review") == wants})
    hits = sum(r["got"] == "review" for r in rows if r["wants_reviews"])
    stolen = sum(r["got"] == "review" for r in rows if not r["wants_reviews"])
    n_pos = sum(r["wants_reviews"] for r in rows)
    print(f"B. holdout (due, concept): review asks answered with a review {hits}/{n_pos}; ordinary messages turned "
          f"into a review {stolen}/{len(rows) - n_pos}")
    for r in rows:
        if not r["as_expected"]:
            print(f"   unexpected: {r['message']!r} -> {r['got']}")
    result["reviews"]["holdout_due_concept"] = rows
    # with the chatbot's label: a perfect labeller (label = the expected answer) and a careless one (always true),
    # over all 46 messages, due + the message's own request_type
    for name, labeller in (("label_perfect", lambda w: w), ("label_always_true", lambda w: True)):
        rows = []
        for k, (msg, wants, rtype) in enumerate(MESSAGES + HOLDOUT):
            got = review_case(200 + k, msg, rtype, "label-" + name, label=labeller(wants))
            rows.append({"message": msg, "wants_reviews": wants, "got": got, "as_expected": (got == "review") == wants})
        hits = sum(r["got"] == "review" for r in rows if r["wants_reviews"])
        stolen = sum(r["got"] == "review" for r in rows if not r["wants_reviews"])
        n_pos = sum(r["wants_reviews"] for r in rows)
        print(f"B. {name} (due, all 46): review asks answered with a review {hits}/{n_pos}; ordinary messages turned "
              f"into a review {stolen}/{len(rows) - n_pos}")
        for r in rows:
            if not r["as_expected"]:
                print(f"   unexpected: {r['message']!r} -> {r['got']}")
        result["reviews"][name] = rows
    if out_json:
        Path(out_json).write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--json" else None)
