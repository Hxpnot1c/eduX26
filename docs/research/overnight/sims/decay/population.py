"""w3-06 population simulation: does the decay-clock asymmetry rank economics parts and students wrongly on main?

Synthetic students study a random subset of the example-mini parts through the real learner code
(record_exchange / record_evidence, apply="now"). A student's hidden truth (one memory trace per part) decides
their answers. The study policy reads only the review queue (due dates come from days-to-exam, not p_now), so
the same event log can be replayed under each candidate fix and read at the same snapshot times.

Every simulated-student number here is OUR CHOICE; see TRUTH below and README.md. Nothing in the repo is edited:
fixes are in-memory monkeypatches (FIXES). Data dirs: /tmp/claude-1000/w3-06/pop-<worker>.

Usage:  python population.py --seeds 25 --workers 7     -> results/population.jsonl (one row per student x variant)
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edux_sim as S  # noqa: E402

EXAM = S.EXAM
TRUTH = {   # OUR CHOICE, matched to edux_sim.TRUTH_PARAMS where they overlap
    "learn": {"typical": 0.35, "slow": 0.15, "fast": 0.60, "guesser": 0.10},
    "slip": 0.10,
    "s0": 4.0, "grow_spaced": 2.0, "grow_massed": 1.1,
    "mcq_options": 4,
    "coverage": 0.6,          # chance a part is ever studied by this student
    "session_every": [1, 2, 3, 7],
    "parts_per_session": 2,
    "max_checks": 3,          # checks on a part per study visit (re-taught after each wrong one)
    "review_compliance": [0.0, 0.5, 1.0],
}
SCENARIOS = {"near": 35, "far": 148}   # days before the exam that study starts
STUDY_DAYS = 60                       # study window (the near scenario stops at the exam)
SNAP_DAYS = [3, 7, 14, 30, 45, 60]     # plus exam morning
VARIANTS = ["current", "a_clock_any", "b_cap_prior", "c_to_prior", "ac", "bc"]


def iso(t):
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- fixes (monkeypatches)

_ORIG: dict = {}


def install(variant: str) -> None:
    """Install one fix. Read-time fixes patch learner.part_p and learner._p_at (both looked up by name at call time).
    a: wrong evidence before any right answer also starts the clock (one line in _apply_evidence).
    b: read-time cap: a part never answered right reads at most its prior (display: "not yet shown").
       Stored state and updates are untouched (part_p only).
    c: decay towards the part's prior instead of towards 0: p = prior + (p_known - prior) * 0.5**(d/h).
       Used both at read time and inside updates (_p_at), as p_now is today."""
    from edux import learner as L
    if not _ORIG:
        _ORIG.update(part_p=L.part_p, _p_at=L._p_at, _apply_evidence=L._apply_evidence, p_now=L.p_now)
    L.part_p, L._p_at, L._apply_evidence = _ORIG["part_p"], _ORIG["_p_at"], _ORIG["_apply_evidence"]
    a = variant in ("a_clock_any", "ac")
    b = variant in ("b_cap_prior", "bc")
    c = variant in ("c_to_prior", "ac", "bc")

    def p_to_prior(part_id, p_known, half_life, since, now):
        if since is None:
            return p_known
        prior = L.initial_state(part_id)[0]
        days = max(0.0, (L.parse_ts(now or L.now_iso()) - L.parse_ts(since)).total_seconds() / 86400)
        return prior + (p_known - prior) * 0.5 ** (days / half_life)

    if c:
        def _p_at(state, ts):
            return p_to_prior(state["part_id"], state["p_known"], state["half_life_days"], state["clock_start"], ts)
        L._p_at = _p_at

    if c or b:
        def part_p(student_id, part_id, at=None):
            part_id = L.graph.canonical(part_id)
            row = L._conn().execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?",
                                    (student_id, part_id)).fetchone()
            prior = L.initial_state(part_id)[0]
            if row is None:
                return prior
            if c:
                p = p_to_prior(part_id, row["p_known"], row["half_life_days"], row["clock_start"], at)
            else:
                p = L.p_now(row["p_known"], row["half_life_days"], row["clock_start"], at)
            if b and row["last_correct"] is None:
                p = min(p, prior)
            return p
        L.part_p = part_p

    if a:
        orig = _ORIG["_apply_evidence"]

        def _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts, weight=1.0, slip_add=0.0):
            orig(conn, student_id, part_id, evidence_type, correct, ts, weight=weight, slip_add=slip_add)
            if not correct:
                node = L.graph.get_node(part_id)
                t = L.parse_ts(ts).isoformat(timespec="seconds")
                conn.execute("UPDATE part_state SET clock_start = ? WHERE student_id = ? AND part_id = ? "
                             "AND clock_start IS NULL", (t, student_id, node["id"]))
        L._apply_evidence = _apply_evidence


# ---------------------------------------------------------------- truth

@dataclass
class Trace:
    known: bool = False
    s: float = TRUTH["s0"]
    last: datetime | None = None


class Truth:
    def __init__(self, kind, rng, parts, floor):
        self.kind, self.rng, self.floor = kind, rng, floor
        self.t = {p: Trace() for p in parts}

    def recall(self, part, now):
        tr = self.t[part]
        if not tr.known:
            return 0.0
        d = max(0.0, (now - tr.last).total_seconds() / 86400)
        return self.floor + (1 - self.floor) * math.exp(-d / tr.s)

    def teach(self, part, now):
        tr = self.t[part]
        if tr.known and self.rng.random() < self.recall(part, now):
            tr.last = now
            return
        if self.rng.random() < TRUTH["learn"][self.kind]:
            tr.known, tr.last, tr.s = True, now, TRUTH["s0"]

    def answer(self, part, now):
        """An MCQ answer: right if recalled and no slip, otherwise a guess among the options."""
        ok = self.rng.random() < self.recall(part, now) and self.rng.random() >= TRUTH["slip"]
        if ok:
            tr = self.t[part]
            tr.s *= TRUTH["grow_spaced"] if (now - tr.last).total_seconds() >= 12 * 3600 else TRUTH["grow_massed"]
            tr.last = now
            return True
        right = self.rng.random() < 1 / TRUTH["mcq_options"]
        if not right:   # feedback after a wrong answer: a small chance to learn (edux_sim: 0.5x)
            if self.rng.random() < TRUTH["learn"][self.kind] * 0.5:
                tr = self.t[part]
                tr.known, tr.last, tr.s = True, now, max(tr.s, TRUTH["s0"])
        return right


# ---------------------------------------------------------------- one student

def generate(sid, kind, seed, scen, floor):
    """Run the student live under `current`; return the event log and snapshot times."""
    from edux import graph, learner as L
    install("current")
    rng = random.Random(f"{kind}-{seed}-{scen}-{floor}")
    parts = L.all_parts()
    truth = Truth(kind, rng, parts, floor)
    start = (EXAM - timedelta(days=SCENARIOS[scen])).replace(hour=17, minute=0)
    every = rng.choice(TRUTH["session_every"])
    compliance = rng.choice(TRUTH["review_compliance"])
    studied = [p for p in parts if rng.random() < TRUTH["coverage"]]
    rng.shuffle(studied)
    L.add_student(sid, "example-mini", student_id=sid)
    events = []

    def exch(part, t, support):
        events.append(("x", part, iso(t), support, None))
        L.record_exchange(sid, [part], "mechanism", "active", support_given=support, ts=iso(t), apply="now")

    def evid(part, t, ok, origin):
        events.append(("e", part, iso(t), origin, ok))
        L.record_evidence(sid, part, "mcq_check", 1.0 if ok else 0.0, ts=iso(t), origin=origin, apply="now")

    queue = list(studied)
    end_day = min(STUDY_DAYS, SCENARIOS[scen] - 1)
    for day in range(0, end_day, every):
        t = start + timedelta(days=day, minutes=rng.randint(0, 90))
        checked = set()
        if rng.random() < compliance:
            for r in L.due_reviews(sid, 3, iso(t)):
                t += timedelta(minutes=2)
                evid(r["part_id"], t, truth.answer(r["part_id"], t), "check")
        for _ in range(TRUTH["parts_per_session"]):
            if not queue:
                break
            part = queue.pop(0)
            # prerequisite check on any prerequisite part at level new (plan.py), once a session
            for edge in graph.prerequisites(part, 1):
                for pre in graph.parts_of(edge["other"]):
                    if pre not in checked and L.level(L.part_p(sid, pre, iso(t))) == "new":
                        checked.add(pre)
                        t += timedelta(minutes=2)
                        evid(pre, t, truth.answer(pre, t), "check")
            for k in range(TRUTH["max_checks"]):
                t += timedelta(minutes=2)
                exch(part, t, "worked_example")
                truth.teach(part, t)
                t += timedelta(minutes=2)
                ok = truth.answer(part, t)
                evid(part, t, ok, "chat")
                if ok:
                    break
    snaps = [start.replace(hour=8) + timedelta(days=d) for d in SNAP_DAYS if d < SCENARIOS[scen]] + [EXAM]
    # truth at each snapshot (does not depend on the model)
    truth_at = [{p: truth.recall(p, t) for p in parts} for t in snaps]
    meta = {"sid": sid, "kind": kind, "seed": seed, "scen": scen, "floor": floor, "every": every,
            "compliance": compliance, "n_studied": len(studied), "n_events": len(events)}
    return events, snaps, truth_at, meta


def replay(sid, events, snaps):
    """Apply the event log to a fresh student under the installed variant; read p and flags at each snapshot."""
    from edux import learner as L
    L.add_student(sid, "example-mini", student_id=sid)
    parts = L.all_parts()
    out, i = [], 0
    for t in snaps:
        while i < len(events) and events[i][2] <= iso(t):
            kind, part, ts, x, ok = events[i]
            if kind == "x":
                L.record_exchange(sid, [part], "mechanism", "active", support_given=x, ts=ts, apply="now")
            else:
                L.record_evidence(sid, part, "mcq_check", 1.0 if ok else 0.0, ts=ts, origin=x, apply="now")
            i += 1
        snap = {}
        for p in parts:
            row = L._conn().execute("SELECT n_evidence, last_correct FROM part_state WHERE student_id=? AND part_id=?",
                                    (sid, p)).fetchone()
            last = row["last_correct"] if row else None
            snap[p] = {"p": L.part_p(sid, p, iso(t)), "n": row["n_evidence"] if row else 0,
                       "lc_days": None if last is None else (t - L.parse_ts(last)).total_seconds() / 86400}
        out.append(snap)
    while i < len(events):   # rest of the log, for the determinism check
        kind, part, ts, x, ok = events[i]
        if kind == "x":
            L.record_exchange(sid, [part], "mechanism", "active", support_given=x, ts=ts, apply="now")
        else:
            L.record_evidence(sid, part, "mcq_check", 1.0 if ok else 0.0, ts=ts, origin=x, apply="now")
        i += 1
    return out


def state_rows(sid):
    from edux import learner as L
    return [tuple(r) for r in L._conn().execute(
        "SELECT part_id, p_known, half_life_days, clock_start, last_correct, n_evidence FROM part_state "
        "WHERE student_id=? ORDER BY part_id", (sid,)).fetchall()]


def job(args):
    worker, tasks = args
    S.setup_data_dir(f"/tmp/claude-1000/w3-06/pop-{worker}")
    S.use_settings("current")
    from edux import learner as L
    rows = []
    for kind, seed, scen, floor in tasks:
        base = f"s-{kind}-{seed}-{scen}-{floor}"
        events, snaps, truth_at, meta = generate(base + "-gen", kind, seed, scen, floor)
        for v in VARIANTS:
            install(v)
            sid = f"{base}-{v}"
            reads = replay(sid, events, snaps)
            live = state_rows(sid)
            L.rebuild_state(sid)
            r1 = state_rows(sid)
            L.rebuild_state(sid)
            r2 = state_rows(sid)
            det = {"rebuild_eq_rebuild": r1 == r2, "rebuild_eq_live": r1 == live}
            rows.append({**meta, "variant": v, "snaps": [iso(t) for t in snaps], "truth": truth_at, "reads": reads,
                         "det": det, "final_state": live})
        install("current")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=25)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--out", default=str(HERE / "results" / "population.jsonl"))
    a = ap.parse_args()
    tasks = [(k, s, sc, fl) for s in range(1, a.seeds + 1) for k in TRUTH["learn"] for sc in SCENARIOS
             for fl in (0.0, 0.3)]
    chunks = [(w, tasks[w::a.workers]) for w in range(a.workers)]
    with Pool(a.workers) as pool, open(a.out, "w") as f:
        for rows in pool.imap_unordered(job, chunks):
            for r in rows:
                f.write(json.dumps(r) + "\n")
    print("wrote", a.out, len(tasks), "students x", len(VARIANTS), "variants")


if __name__ == "__main__":
    main()
