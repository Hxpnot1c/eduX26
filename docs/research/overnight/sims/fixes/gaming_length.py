"""gaming_length.py (w6-fix-length): gaming/gaming_sim.py plus three more length strategies, same seeds and options.
  C2s  as C2m, but picks the shortest option          C2x  as C2m, but guesses between the longest and the shortest
  C2l2 as C2m, but picks the second-longest option (n >= 3; else guesses)
  C2r  control: as C2m's flow ("I know this"), but picks a uniformly random shown option (no cue)
A chatbot-written extra option (extra_option) is modelled as middle length, as in C2m: in the guess pool for C2m only.
Run exactly like gaming_sim.py, e.g. --only C2m,C2s,C2x,C2l2. Original docstring follows.
Adversarial-student simulation (w5-06g): treat eduX's scoring rules as a mechanism and look for profitable deviations.

Each synthetic student plays one strategy against the REAL service layer of a code copy (service.tutor_turn with the
labels an honest chatbot would send, then learner/service reads for what get_my_progress would display). Every
effort number and every truth-model number below is OUR CHOICE (marked); the students are synthetic.

    EDUX_DATA_DIR is set by the script to <data>/<strategy>; run from anywhere:
    PYTHONPATH=<code copy> /home/vishnu/edux26/.venv/bin/python gaming_sim.py --code <copy> --data /tmp/claude-1000/... \
        --n 30 --turns 40 --labeller literal --out results/base.json [--only C0,C1]

Course strategies (example-mini parts, one session):
  C0 honest          reads each point (40 s), answers checks from true knowledge, writes real explain-backs
  C1 same_letter     never reads, answers every MCQ "A", explain-back "dunno" (no points)
  C2 skip_cue        "I know this" on every part, picks the longest option, switches topic at explain-back
  C2m skip_middle    as C2, but drops the longest and shortest options and guesses among the rest
  C3 showme_match    "just show me" every time, picks the option that repeats the point just shown (upper bound:
                     assumes the chatbot shows the point near-verbatim); at explain_back says "just show me" again
  C4 copy_explain    honest teaching, but the explain-back is the chatbot's own text pasted back
  C5 selective       half-knows the course; answers an MCQ only when sure, otherwise switches topic (no evidence)
Literacy strategies (research questions, verify tasks, how-AI-works checks):
  L0 honest_partial  honest, "partial" skill (feature/tick rates from sims/literacy/lit_model.py TRUTH)
  L0s honest_strong  honest, "strong" skill
  L1 link_broken     2-feature template question; every verify task -> "the link is broken" (source_conflict)
  L1d broken_detail  as L1, plus the publisher and date copied from the chatbot's own citation (literal ticks b)
  L2 restate_task    2-feature template; every verify task -> restates the chatbot's answer as the check
  L3 restate_unprompted 2-feature template; after every answer, restates it as an unprompted check (ail_unprompted)
  L4 template4       pastes a 4-feature template question every time, ignores every task
  L5 vague           0-feature questions, ignores tasks
  L6 ignore_all      honest-partial questions, ignores every task and check
Labeller: literal (ticks whatever the student's words contain, the rule as written) or skeptical (doesn't tick points
that only repeat the chatbot's own reply; a bare "link is broken" still sets source_conflict: it can't be checked).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import random
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- effort per student action, seconds (OUR CHOICE) -------------------------------------------------------------
EFFORT = {
    "read": 40, "skim": 5,                         # reading a teaching reply carefully / skimming it
    "mcq_think": 30, "mcq_blind": 5, "mcq_match": 10,
    "explain_real": 120, "explain_copy": 20, "explain_oneliner": 10,
    "ask_topic": 10,                               # "teach me X" / switching topic / "I know this" / "just show me"
    "research_real": 45, "research_template": 15, "research_vague": 10,
    "verify_real": 180, "verify_broken": 8, "verify_restate": 25,
    "how_think": 30, "how_blind": 5,
}
BOT_SECONDS = 20          # chatbot reply time between messages (wall clock, not effort)
SCALE = 1.0               # effort multiplier for the sensitivity run (--effort-scale)

COURSE_PARTS = ["ped_definition", "ped_formula", "ped_values", "pes_definition", "pes_formula", "yed_definition",
                "tax_supply_shift", "tax_incidence_split", "externality_tax_eval"]
# honest truth model (OUR CHOICE): a point is known before teaching w.p. PRIOR_KNOWN, after reading it w.p. AFTER_READ,
# after a reteach the remaining gap closes by RETEACH_GAIN; an explain-back produces each known point w.p. RECALL.
PRIOR_KNOWN, AFTER_READ, RETEACH_GAIN, RECALL = 0.30, 0.75, 0.5, 0.9
SELECTIVE_KNOWN = 0.5     # C5 knows each point w.p. 0.5 and never learns in-session (OUR CHOICE)

# literacy truth (taken from sims/literacy/lit_model.py TRUTH, themselves OUR CHOICE in wave 2)
FEAT = {"partial": (0.90, 0.70, 0.35, 0.35), "strong": (0.95, 0.90, 0.75, 0.70)}      # concept, context, sources, reasoning
TICK_TASK = {"partial": (0.70, 0.40, 0.60, 0.70), "strong": (0.90, 0.80, 0.85, 0.90)}  # opens, names publisher/date, compares, says match
HOW_CORRECT = {"partial": 0.65, "strong": 0.90}
REAL_DEAD_LINK = 0.10     # share of honest verify tasks where the link really is dead or mismatched (OUR CHOICE)
FEATURES = ("concept", "context", "asks_sources", "asks_reasoning")

LEVEL_N = {"new": 0, "developing": 1, "secure": 2}


def iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


class Sim:
    def __init__(self, code: Path, data: Path):
        assert str(data).startswith("/tmp/claude-1000/")
        os.environ["EDUX_DATA_DIR"] = str(data)
        data.mkdir(parents=True, exist_ok=True)
        for f in data.glob("*.db*"):
            f.unlink()
        from ingest import load
        with contextlib.redirect_stdout(io.StringIO()):
            rep = load.load_pack(code / "coursepacks" / "example-mini")
        assert rep.ok, rep.errors
        from edux import graph, learner, plan, service
        self.graph, self.learner, self.plan, self.service = graph, learner, plan, service


class Student:
    def __init__(self, sim: Sim, sid: str, t0: datetime, rng: random.Random, labeller: str):
        self.sim, self.sid, self.t, self.rng, self.labeller = sim, sid, t0, rng, labeller
        sim.learner.add_student(sid, "example-mini", student_id=sid)
        self.student = sim.learner.get_student(sid)
        self.effort = 0.0
        self.r: dict | None = None
        self.turns = 0
        self.log: list[dict] = []          # per turn: effort so far, display
        self.counts = Counter()
        self.known: dict[str, bool] = {}   # point id -> known (truth)

    # one message to the chatbot, which calls tutor_turn with honest labels
    def say(self, message: str, effort_key: str, labels: dict | None = None, node_ids=None, answer=None) -> dict:
        lab = {"question_depth": "surface", "engagement": "active", "choice": "none"}
        lab.update(labels or {})
        e = EFFORT[effort_key] * SCALE
        self.t += timedelta(seconds=e + BOT_SECONDS)
        self.effort += e
        r = self.sim.service.tutor_turn(self.student, message, lab, node_ids, answer, client="claude", at=iso(self.t))
        if not r.get("ok"):
            raise RuntimeError(f"{self.sid} turn {self.turns}: {r} ({message!r}, {lab}, {answer})")
        self.r, self.turns = r, self.turns + 1
        self.counts[effort_key] += 1
        self.log.append({"turn": self.turns, "effort_min": round(self.effort / 60, 2), **self.display()})
        return r

    def display(self, at: datetime | None = None) -> dict:
        L, at = self.sim.learner, iso(at or self.t)
        course = {p: L.level(L.part_p(self.sid, p, at)) for p in COURSE_PARTS}
        lit = {"ask": L.level(L.part_p(self.sid, L.AIL_ASK, at)), "verify": L.level(L.part_p(self.sid, L.AIL_VERIFY, at)),
               "how": L.level(L.rollup(self.sid, L.AIL_HOW, at))}
        return {"course_pts": sum(LEVEL_N[v] for v in course.values()), "course_secure": sum(v == "secure" for v in course.values()),
                "lit_pts": sum(LEVEL_N[v] for v in lit.values()), "lit": lit, "course": course,
                "p_verify": round(L.part_p(self.sid, L.AIL_VERIFY, at), 3), "p_ask": round(L.part_p(self.sid, L.AIL_ASK, at), 3)}

    # --- reading the plan --------------------------------------------------------------------------------------
    def steps(self) -> list[dict]:
        return (self.r or {}).get("plan") or []

    def asking(self) -> dict | None:
        return next((s for s in reversed(self.steps()) if "answer_type" in s["data"]), None)

    def mcq_options(self, step: dict) -> list[dict] | None:
        return step["data"].get("options") if step["move"] in ("ask_mcq", "reask") else None

    def correct_letter(self) -> str | None:
        mcq = self.sim.service._last_plan(self.sid).get("mcq") or {}
        return next((l for l, o in (mcq.get("options") or {}).items() if o["id"] == "correct"), None)

    def letters(self) -> list[str]:
        mcq = self.sim.service._last_plan(self.sid).get("mcq") or {}
        return sorted((mcq.get("options") or {}).keys())

    def mcq_point_id(self) -> str | None:
        return (self.sim.service._last_plan(self.sid).get("mcq") or {}).get("point_id")

    def answer_mcq(self, step: dict, letter: str, effort_key: str) -> dict:
        self.counts["letter_" + letter] += 1
        return self.say(letter, effort_key, answer={"part_id": step["part_id"], "type": "mcq", "choice": letter})

    def guess(self, exclude_correct: bool = False) -> str:
        ls = self.letters()
        c = self.correct_letter()
        pool = [l for l in ls if not (exclude_correct and l == c)] or ls
        return self.rng.choice(pool)


# --- course strategies ----------------------------------------------------------------------------------------------

def points_of(sim: Sim, part: str) -> list[dict]:
    return sim.graph.score_points(part)


def course_run(st: Student, strategy: str, turns: int) -> None:
    sim = st.sim
    queue = list(COURSE_PARTS)
    current = queue[0]
    choice = {"C2": "skip_point", "C2m": "skip_point", "C2s": "skip_point", "C2x": "skip_point", "C2l2": "skip_point", "C2r": "skip_point",
              "C3": "just_show_me"}.get(strategy, "none")
    st.say(f"Teach me {current}", "ask_topic", {"choice": choice}, node_ids=[current])
    last_shown = None
    while st.turns < turns:
        step = st.asking()
        shown = next((s for s in st.steps() if s["move"] in ("show", "teach_point")), None)
        if shown:
            last_shown = shown["data"].get("point")
            for p in points_of(sim, shown["part_id"]):   # honest reading
                if p["point"] == last_shown and strategy in ("C0", "C4") and p["id"] not in st.known:
                    st.known[p["id"]] = st.rng.random() < AFTER_READ
        if step is None:   # nothing asked: next part
            queue = queue[1:] + queue[:1]
            current = queue[0]
            st.say(f"Teach me {current}", "ask_topic", {"choice": choice}, node_ids=[current])
            continue
        opts = st.mcq_options(step)
        part = step["part_id"]
        if opts:   # a multiple-choice question
            purpose = step["data"].get("purpose") or step["data"].get("asked")
            if strategy in ("C0", "C4"):
                pid = st.mcq_point_id()
                k = st.known.get(pid)
                if k is None:
                    k = st.known.setdefault(pid, st.rng.random() < PRIOR_KNOWN) if pid else st.rng.random() < PRIOR_KNOWN
                if step["move"] == "reask" or any(s["move"] == "reteach" for s in st.steps()):
                    if pid and not st.known.get(pid):
                        st.known[pid] = st.rng.random() < RETEACH_GAIN
                        k = st.known[pid]
                st.answer_mcq(step, st.correct_letter() if k else st.guess(), "mcq_think")
            elif strategy == "C1":
                ls = st.letters()
                st.answer_mcq(step, "A" if "A" in ls else ls[0], "mcq_blind")
            elif strategy == "C2":
                o = max(opts, key=lambda o: len(o["text"]))
                st.answer_mcq(step, o["letter"], "mcq_blind")
            elif strategy == "C2m":
                by = sorted(opts, key=lambda o: len(o["text"]))
                pool = by[1:-1] if len(by) > 2 else by
                extra = step["data"].get("extra_option")   # a chatbot-written option: modelled as middle length
                letters = [o["letter"] for o in pool] + ([extra] if extra else [])
                st.answer_mcq(step, st.rng.choice(letters), "mcq_blind")
            elif strategy in ("C2s", "C2x", "C2l2", "C2r"):
                by = sorted(opts, key=lambda o: len(o["text"]))
                pool = {"C2s": by[:1], "C2x": [by[0], by[-1]] if len(by) > 2 else by,
                        "C2l2": by[-2:-1] if len(by) > 2 else by, "C2r": by}[strategy]
                st.answer_mcq(step, st.rng.choice([o["letter"] for o in pool]), "mcq_blind")
            elif strategy == "C3":
                from edux.plan import option_form
                hit = next((o for o in opts if last_shown and o["text"] == option_form(last_shown)), None)
                st.answer_mcq(step, hit["letter"] if hit else st.guess(), "mcq_match")
            elif strategy == "C5":
                pid = st.mcq_point_id()
                k = st.known.setdefault(pid or f"{part}?", st.rng.random() < SELECTIVE_KNOWN)
                if k:
                    st.answer_mcq(step, st.correct_letter(), "mcq_think")
                else:   # dodge: switch topic, no evidence
                    st.counts["dodged"] += 1
                    queue = queue[1:] + queue[:1]
                    current = queue[0]
                    st.say(f"Actually, can we do {current}?", "ask_topic", node_ids=[current])
            continue
        # an open answer: explain_back, extend, reteach of missing points
        letters = [p["id"] for p in st.r["score_next"].get(part, [])]
        pts = points_of(sim, part)
        atype = step["data"]["answer_type"]
        if step["move"] == "reteach" and strategy in ("C0", "C4"):   # honest: reads the reteach of the missing points
            st.counts["reteach_seen"] += 1
            missing = set(step["data"].get("missing") or [])
            for p in pts:
                if p["point"] in missing and not st.known.get(p["id"]):
                    st.known[p["id"]] = st.rng.random() < RETEACH_GAIN
            if st.counts[f"reteach_{part}"] >= 2:   # honest student moves on after two re-teaches of the same part
                queue = queue[1:] + queue[:1]
                current = queue[0]
                st.say(f"Can we move on to {current}?", "ask_topic", node_ids=[current])
                continue
            st.counts[f"reteach_{part}"] += 1
        if step["move"] == "extend" and st.counts[f"extend_{part}"] >= 1:   # one harder question per part, then move on
            queue = queue[1:] + queue[:1]
            current = queue[0]
            st.say(f"Can we move on to {current}?", "ask_topic", {"choice": choice}, node_ids=[current])
            continue
        if step["move"] == "extend":
            st.counts[f"extend_{part}"] += 1
        if strategy == "C0" or (strategy == "C4" and atype != "explain_back") or strategy == "C5":
            known_pts = [l for l, p in zip(letters, pts) if (st.known.get(p["id"]) if strategy != "C5" else st.known.setdefault(p["id"], st.rng.random() < SELECTIVE_KNOWN)) and st.rng.random() < RECALL]
            if strategy == "C5" and len(known_pts) < len(letters):   # not sure: dodge
                st.counts["dodged"] += 1
                queue = queue[1:] + queue[:1]
                current = queue[0]
                st.say(f"Actually, can we do {current}?", "ask_topic", node_ids=[current])
                continue
            st.say("my explanation", "explain_real", answer={"part_id": part, "type": atype, "points_met": known_pts})
        elif strategy == "C4":
            ticked = letters if st.labeller == "literal" else []
            st.say("<the chatbot's own explanation pasted back>", "explain_copy",
                   answer={"part_id": part, "type": atype, "points_met": ticked})
        elif strategy in ("C1", "C2", "C2m", "C2s", "C2x", "C2l2", "C2r"):   # never writes an explanation: switches topic (no evidence)
            st.counts["dodged"] += 1
            queue = queue[1:] + queue[:1]
            current = queue[0]
            st.say(f"next topic: {current}", "ask_topic", {"choice": choice}, node_ids=[current])
        elif strategy == "C3":   # never explains: "just show me" again restarts the point loop; once secure, next part
            L = sim.learner
            if L.level(L.part_p(st.sid, part, iso(st.t))) == "secure":
                queue = queue[1:] + queue[:1]
                part = current = queue[0]
            st.say("just show me", "ask_topic", {"choice": "just_show_me"}, node_ids=[part])


# --- literacy strategies --------------------------------------------------------------------------------------------

TOPICS = ["UK petrol prices", "UK rail fares", "sugar tax", "cigarette duty", "UK inflation", "energy price cap",
          "bus fares", "alcohol duty", "streaming prices", "house prices"]


def literacy_run(st: Student, strategy: str, turns: int) -> None:
    rng = st.rng
    skill = {"L0": "partial", "L0s": "strong", "L6": "partial"}.get(strategy, "partial")
    i = 0
    honest = strategy in ("L0", "L0s")

    def features() -> list[str]:
        if strategy in ("L0", "L0s", "L6"):
            return [f for f, p in zip(FEATURES, FEAT[skill]) if rng.random() < p]
        if strategy == "L4":
            return list(FEATURES)
        if strategy == "L5":
            return []
        return ["concept", "context"]   # L1-L3, L1d: the cheapest template that earns a verify task

    def research(feats: list[str], key: str) -> dict:
        nonlocal i
        i += 1
        return st.say(f"research question {i} on {TOPICS[i % len(TOPICS)]}", key,
                      {"request_type": "research", "question_features": feats, "web_access": True, "asks_recent": False})

    research(features(), "research_template" if strategy in ("L1", "L1d", "L2", "L3", "L4") else
             "research_vague" if strategy == "L5" else "research_real")
    while st.turns < turns:
        steps = st.steps()
        how = next((s for s in steps if s["move"] in ("ask_mcq", "reask") and (s["part_id"] or "").startswith("ail_how")), None)
        task = next((s for s in steps if (s["move"] == "literacy_task" and s["data"].get("task"))
                     or (s["move"] == "reask" and s["data"].get("asked") == "literacy_task")), None)
        if how and strategy != "L6" and st.mcq_options(how):
            if honest:
                letter = st.correct_letter() if rng.random() < HOW_CORRECT[skill] else st.guess(exclude_correct=True)
                st.answer_mcq(how, letter, "how_think")
            else:
                st.answer_mcq(how, st.guess(), "how_blind")
            continue
        if task and strategy not in ("L4", "L5", "L6"):
            sk = task["data"].get("skill")
            if sk == "ask":   # rewrite the question with the missing feature (any research question completes it)
                f = features()
                if honest:
                    missing = [x for x in FEATURES if x not in f]
                    f = f + missing[:1]
                research(f, "research_real" if honest else "research_template")
                continue
            # a verify task
            if honest:
                if rng.random() < REAL_DEAD_LINK:   # says what they found: publisher/date (b) and what the page shows (c)
                    ticks = [l for l, p in zip("bc", TICK_TASK[skill][1:3]) if rng.random() < p]
                    st.say("the link doesn't say that ...", "verify_real", {"request_type": "other", "source_conflict": True},
                           answer={"part_id": "ail_verify", "type": "ail_task", "points_met": ticks} if ticks else None)
                else:
                    ticks = [l for l, p in zip("abcd", TICK_TASK[skill]) if rng.random() < p]
                    st.say("I checked the source ...", "verify_real", answer={"part_id": "ail_verify", "type": "ail_task", "points_met": ticks})
            elif strategy == "L1":
                st.say("the link is broken", "verify_broken", {"request_type": "other", "source_conflict": True})
            elif strategy == "L1d":
                ticks = ["b"] if st.labeller == "literal" else []
                st.say("the ONS link (March 2025) is broken", "verify_broken", {"request_type": "other", "source_conflict": True},
                       answer={"part_id": "ail_verify", "type": "ail_task", "points_met": ticks} if ticks else None)
            elif strategy in ("L2", "L3"):
                ticks = list("abcd") if st.labeller == "literal" else []
                st.say("I opened it, it's the ONS, March 2025, it says 3.4%, so it matches", "verify_restate",
                       answer={"part_id": "ail_verify", "type": "ail_task", "points_met": ticks})
            continue
        if strategy == "L3" and st.r and "ail_verify" in st.r.get("score_next", {}) and st.counts["unprompted_last"] != i:
            st.counts["unprompted_last"] = i
            ticks = list("abcd") if st.labeller == "literal" else []
            st.say("I checked that: ONS, March 2025, 3.4%, it matches", "verify_restate",
                   answer={"part_id": "ail_verify", "type": "ail_unprompted", "points_met": ticks})
            continue
        # nothing to do (or ignoring it): next research question
        research(features(), "research_template" if strategy in ("L1", "L1d", "L2", "L3", "L4") else
                 "research_vague" if strategy == "L5" else "research_real")


# --- signals a teacher / the progress view could see ----------------------------------------------------------------

def signals(st: Student) -> dict:
    L, S = st.sim.learner, st.sim.service
    prog = S.my_progress(st.student, include_parts=True, at=iso(st.t))
    conn = L._conn()
    ex = conn.execute("SELECT * FROM exchange_log WHERE student_id = ? ORDER BY ts", (st.sid,)).fetchall()
    ev = conn.execute("SELECT * FROM evidence_log WHERE student_id = ? ORDER BY ts", (st.sid,)).fetchall()
    research = [r for r in ex if r["request_type"] == "research"]
    letters = Counter({k[7:]: v for k, v in st.counts.items() if k.startswith("letter_")})
    n_letters = sum(letters.values())
    times = [L.parse_ts(r["ts"]) for r in ex]
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
    ail = prog["ai_literacy"]
    return {
        "skipped": {k: ail[k]["skipped"] for k in ("ask", "verify", "how_ai_works")},
        "held_how": len(ail["how_ai_works"]["held"]),
        "trend_just_show_me": prog["trends"]["just_show_me"]["recent"],
        "source_conflicts": sum(r["source_conflict"] for r in ex),
        "verify_evidence": sum(r["part_id"] == "ail_verify" for r in ev),
        "all4_feature_share": (sum(len((r["question_features"] or "").split(";")) == 4 for r in research) / len(research)) if research else None,
        "top_letter_share": (max(letters.values()) / n_letters) if n_letters else None,
        "median_gap_s": statistics.median(gaps) if gaps else None,
        "mcq_right_share": (lambda xs: sum(xs) / len(xs) if xs else None)([r["score"] for r in ev if r["evidence_type"] in ("mcq_check", "ail_how")]),
    }


def run(code: Path, data_root: Path, strategy: str, n: int, turns: int, labeller: str) -> dict:
    sim = Sim(code, data_root / f"{strategy}-{labeller}")
    t0 = datetime(2026, 12, 1, 16, 0, tzinfo=timezone.utc)   # ~6 months before the example-mini exam (2027-06-08)
    out = []
    for k in range(n):
        rng = random.Random(f"{strategy}-{k}")
        st = Student(sim, f"{strategy}-{labeller}-{k}", t0 + timedelta(days=k * 0), rng, labeller)
        start = st.display()
        (course_run if strategy.startswith("C") else literacy_run)(st, strategy, turns)
        later = {f"+{d}d": st.display(st.t + timedelta(days=d)) for d in (1.5, 7)}
        out.append({"sid": st.sid, "start": start, "end": st.display(), "later": later, "effort_min": st.effort / 60,
                    "wall_min": (st.t - t0).total_seconds() / 60, "turns": st.turns, "traj": st.log,
                    "counts": dict(st.counts), "signals": signals(st),
                    "true_known_share": (sum(st.known.values()) / len(st.known)) if st.known else None,
                    "true_part": {p: (sum(bool(st.known.get(x["id"])) for x in points_of(sim, p)) / max(1, len(points_of(sim, p))))
                                  for p in COURSE_PARTS}})
    return {"strategy": strategy, "labeller": labeller, "n": n, "turns": turns, "students": out}


def main() -> None:
    global SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--labeller", default="literal", choices=("literal", "skeptical"))
    ap.add_argument("--only", default="C0,C1,C2,C2m,C3,C4,C5,L0,L0s,L1,L1d,L2,L3,L4,L5,L6")
    ap.add_argument("--effort-scale", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    SCALE = a.effort_scale
    res = {"code": a.code, "labeller": a.labeller, "effort": EFFORT, "effort_scale": SCALE, "runs": {}}
    for s in a.only.split(","):
        res["runs"][s] = run(Path(a.code), Path(a.data), s, a.n, a.turns, a.labeller)
        print(s, "done", file=sys.stderr, flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res))


if __name__ == "__main__":
    main()
