"""Synthetic-student simulation harness for eduX (overnight research w1-06).

Drives synthetic students through the REAL code (edux.service.tutor_turn -> edux.learner) on the example-mini
pack, in a throwaway EDUX_DATA_DIR, with a simulated clock. Each synthetic student has a hidden true state
(which points they know, how fast they forget) so the model's beliefs can be scored against the truth.

Nothing here edits settings.toml: a settings variant is built in memory (settings.toml + overlay) and the
cached accessors learner._settings, service._settings and graph._settings are replaced in this process.

Every simulated-student number below is OUR CHOICE (not evidence); see TRUTH_PARAMS and README.md.
Results apply to the example-mini pack and synthetic students only.
"""

from __future__ import annotations

import copy
import json
import math
import os
import random
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # worktree root
PACK = ROOT / "coursepacks" / "example-mini"
PROPOSAL = ROOT / "docs" / "research" / "settings-proposal.toml"
EXAM = datetime(2027, 6, 8, 9, 0, tzinfo=timezone.utc)   # paper1 date in the example-mini pack

# --------------------------------------------------------------------------------------------------
# Truth model parameters: ALL OUR CHOICE. They make the synthetic students; they are not findings.
# --------------------------------------------------------------------------------------------------
TRUTH_PARAMS = {
    "learn": {"typical": 0.35, "slow": 0.15, "fast": 0.60, "guesser": 0.10, "offloader": 0.35,
              "tired": 0.35, "stuck": 0.35},          # P(learn a point) per teaching of it
    "show_learn_factor": 0.4,      # a "just show me" show teaches at this share of the learn rate
    "feedback_learn_factor": 0.5,  # feedback after a wrong answer teaches at this share
    "slip": 0.10,                  # P(knows but answers wrong)
    "tired_after_min": 30,         # the tired student's accuracy drops from this session minute
    "tired_slip": 0.45,            # their slip once tired
    "tired_learn_factor": 0.5,     # and their learning
    "stability0_days": 4.0,        # memory stability of a newly learnt point (recall = exp(-days/S))
    "stability_growth_spaced": 2.0,   # S multiplier after a successful retrieval >= 12 h after the last
    "stability_growth_massed": 1.1,   # ... within 12 h
    "open_answer_lucky_tick": 0.05,   # P(an unknown point is ticked in an open answer anyway)
    "extend_factor": 0.8,          # extend answers are harder: P(tick) x this
    "offloader_answers": 0.5,      # share of checks the offloader answers (else "just show me" again)
    "minutes_per_turn": (1.0, 2.5),   # uniform
    "session_minutes": 45,
    "reviews_per_session": 2,      # due parts the student works through at the start of a session
    "turns_per_part_cap": 12,      # per session, then move to the next part
    "false_secure_below": 0.5,     # model secure while true mastery below this = false secure
    "true_secure_from": 0.75,      # true mastery at or above this = truly secure
}
TYPES = ["typical", "slow", "fast", "guesser", "offloader", "tired", "stuck"]
STUCK_PART = "ped_formula"   # the stuck student can never learn this part (our choice)


# --------------------------------------------------------------------------------------------------
# Settings variants
# --------------------------------------------------------------------------------------------------

def _deep_merge(base: dict, over: dict, applied: list, skipped: list, schema: dict, path: str = "") -> None:
    for k, v in over.items():
        where = f"{path}{k}"
        if isinstance(v, dict) and isinstance(schema.get(k), dict):
            if k == "evidence" and path == "bkt.":   # evidence types: a new type key is fine (a dict of types)
                for t, sg in v.items():
                    if base[k].get(t) != sg:
                        applied.append(f"bkt.evidence.{t}={sg}")
                    base[k][t] = sg
                continue
            _deep_merge(base[k], v, applied, skipped, schema[k], where + ".")
        elif k in schema and not isinstance(schema.get(k), dict):
            if base[k] != v:
                applied.append(f"{where}={v}")
            base[k] = v
        else:
            skipped.append(where)


def settings_dict(variant: str) -> tuple[dict, list[str], list[str]]:
    """(settings dict, applied keys, proposal keys skipped because the code doesn't read them)."""
    with open(ROOT / "settings.toml", "rb") as f:
        current = tomllib.load(f)
    if variant == "current":
        return current, [], []
    d = copy.deepcopy(current)
    applied: list[str] = []
    skipped: list[str] = []
    base = VARIANT_BASE.get(variant, "proposal" if variant.startswith("proposal") else "current")
    if base == "proposal":
        with open(PROPOSAL, "rb") as f:
            prop = tomllib.load(f)
        _deep_merge(d, prop, applied, skipped, current)
    for key, value in VARIANT_EXTRA.get(variant, {}).items():
        section, name = key.rsplit(".", 1)
        node = d
        for s in section.split("."):
            node = node[s]
        node[name] = value
        applied.append(f"{key}={value}")
    return d, applied, skipped


# Extra overrides on top of current (or proposal) for candidate variants found in sweeps. Filled in run_sims.
VARIANT_EXTRA: dict[str, dict] = {}
# The settings a variant starts from: "current" (settings.toml) or "proposal" (settings.toml + the proposal's keys).
VARIANT_BASE: dict[str, str] = {}
# Code-level proposal rules emulated by wrappers in this process ("shim, not built"): variant -> set of shims.
VARIANT_SHIMS: dict[str, dict] = {}


def build_settings(variant: str):
    from edux.settings import Settings, _build
    d, applied, skipped = settings_dict(variant)
    return _build(Settings, d, ""), applied, skipped


def use_settings(variant: str):
    """Point every cached settings accessor in this process at the variant; install its shims."""
    from edux import graph, learner, service
    s, applied, skipped = build_settings(variant)
    shims = VARIANT_SHIMS.get(variant, {})
    if "mcq_guess_from_options" in shims:
        # proposal bkt.mcq_guess_from_options: guess = 1 / options shown, as extra evidence types "<type>_n<n>"
        import dataclasses
        from edux.settings import SlipGuess
        ev = dict(s.bkt.evidence)
        for n in (2, 3, 4, 5):
            for t in ("mcq_check", "prequestion"):
                ev[f"{t}_n{n}"] = SlipGuess(slip=ev[t].slip, guess=1 / n)
        s = dataclasses.replace(s, bkt=dataclasses.replace(s.bkt, evidence=ev))
    learner._settings = lambda: s
    service._settings = lambda: s
    graph._settings = lambda: s
    _install_shims(shims)
    return s, applied, skipped


_ORIG = {}


CLAMPS = {"n": 0}


def _install_clamp() -> None:
    """Sim-only workaround for a bug found here: BKT can drive p_known to exactly 1.0 (float saturation after ~40
    correct answers on a part), and the next ordinary exchange then divides by zero in learner.apply_exchange
    (odds = p / (1 - p)), so tutor_turn crashes. In every variant we clamp p_known to 1 - 1e-9 when state is
    saved and count how often that was needed (CLAMPS)."""
    from edux import learner
    if "orig_save" in _ORIG:
        return
    _ORIG["orig_save"] = learner._save_state

    def save(conn, state):
        if state["p_known"] > 1 - 1e-9:
            state["p_known"] = 1 - 1e-9
            CLAMPS["n"] += 1
        _ORIG["orig_save"](conn, state)

    learner._save_state = save


def _install_shims(shims) -> None:
    """Shims (sim-only emulations of proposal rules the code doesn't have yet), as {name: value}:
    - mcq_guess_from_options: True -> guess = 1 / options shown for mcq_check and prequestion evidence
      (a part's option count is fixed: 1 + its misconceptions up to max_options - 1, + 1 chatbot-written extra
      option when it has fewer than min_distractors).
    - on_success_immediate: x -> correct `immediate` evidence multiplies the half-life by x instead of on_success.
    - on_success_scaled: True -> on correct evidence the half-life grows by 1 + (factor - 1) * (1 - p_now/p_known),
      i.e. only as much as the memory had decayed since the clock started (massed successes barely grow it).
    """
    from edux import graph, learner
    shims = dict.fromkeys(shims, True) if isinstance(shims, (set, list, tuple)) else dict(shims or {})
    if shims.get("on_success_immediate") is True:
        shims["on_success_immediate"] = 1.0
    _install_clamp()
    if "orig_apply" not in _ORIG:
        _ORIG["orig_apply"] = learner._apply_evidence
    orig = _ORIG["orig_apply"]
    if not shims:
        learner._apply_evidence = orig
        return

    def options_shown(part_id: str) -> int:
        s = learner._settings()
        n_wrong = min(len(graph.misconceptions_for([part_id])), s.mcq.max_options - 1)
        return 1 + n_wrong + (1 if n_wrong < s.mcq.min_distractors else 0)

    def wrapped(conn, student_id, part_id, evidence_type, correct, ts, weight=1.0, slip_add=0.0):
        s = learner._settings()
        state = learner._load_state(conn, student_id, part_id, ts)
        hl_before = state["half_life_days"]
        decayed = 1.0 - (learner._p_at(state, ts) / state["p_known"] if state["clock_start"] else 1.0)
        kind = evidence_type
        if shims.get("mcq_guess_from_options") and evidence_type in ("mcq_check", "prequestion"):
            kind = f"{evidence_type}_n{options_shown(part_id)}"
        orig(conn, student_id, part_id, kind, correct, ts, weight=weight, slip_add=slip_add)
        if not correct:
            return
        factor = None
        if "on_success_immediate" in shims and evidence_type == "immediate":
            factor = shims["on_success_immediate"]
        if shims.get("on_success_scaled") and state["clock_start"]:
            base = factor if factor is not None else s.decay.on_success
            factor = 1 + (base - 1) * max(0.0, min(1.0, decayed))
        if factor is not None:
            conn.execute("UPDATE part_state SET half_life_days = ? WHERE student_id = ? AND part_id = ?",
                         (max(s.decay.min_half_life_days, hl_before * factor), student_id, part_id))

    learner._apply_evidence = wrapped


# --------------------------------------------------------------------------------------------------
# Data dir
# --------------------------------------------------------------------------------------------------

def setup_data_dir(path: str) -> None:
    """Fresh data dir with example-mini loaded. Must be called before edux touches a database."""
    assert path.startswith("/tmp/claude-1000/"), "simulations only write under /tmp/claude-1000/"
    os.environ["EDUX_DATA_DIR"] = path
    Path(path).mkdir(parents=True, exist_ok=True)
    for f in Path(path).glob("*.db*"):
        f.unlink()
    from ingest import load
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        report = load.load_pack(PACK)
    assert report.ok, report.errors


# --------------------------------------------------------------------------------------------------
# Synthetic student: hidden truth
# --------------------------------------------------------------------------------------------------

@dataclass
class Point:
    known: bool = False
    stability: float = TRUTH_PARAMS["stability0_days"]
    last: datetime | None = None


@dataclass
class Truth:
    kind: str
    rng: random.Random
    points: dict = field(default_factory=dict)    # part -> list[Point]
    point_ids: dict = field(default_factory=dict)  # part -> list[point id or None]
    point_texts: dict = field(default_factory=dict)

    def setup(self) -> None:
        from edux import graph, plan
        from edux import learner
        for part in learner.all_parts():
            pts = plan._points(part)
            self.points[part] = [Point() for _ in pts]
            self.point_ids[part] = [p["id"] for p in pts]
            self.point_texts[part] = [p["point"] for p in pts]

    def learn_rate(self, part: str, tired: bool) -> float:
        if self.kind == "stuck" and part == STUCK_PART:
            return 0.0
        L = TRUTH_PARAMS["learn"][self.kind]
        return L * (TRUTH_PARAMS["tired_learn_factor"] if tired else 1.0)

    def slip(self, tired: bool) -> float:
        return TRUTH_PARAMS["tired_slip"] if tired else TRUTH_PARAMS["slip"]

    def recall(self, part: str, i: int, now: datetime) -> float:
        p = self.points[part][i]
        if not p.known:
            return 0.0
        days = max(0.0, (now - p.last).total_seconds() / 86400)
        return math.exp(-days / p.stability)

    def mastery(self, part: str, now: datetime) -> float:
        n = len(self.points[part])
        return sum(self.recall(part, i, now) for i in range(n)) / n

    def teach(self, part: str, i: int, now: datetime, tired: bool, factor: float = 1.0) -> None:
        if part not in self.points:
            return
        p = self.points[part][i]
        if p.known:
            # restudy: memory refreshed if it was still there, else relearn chance
            if self.rng.random() < self.recall(part, i, now):
                p.last = now
                return
        if self.rng.random() < self.learn_rate(part, tired) * factor:
            p.known, p.last, p.stability = True, now, TRUTH_PARAMS["stability0_days"]

    def retrieve(self, part: str, i: int, now: datetime, tired: bool) -> bool:
        """Try to produce point i from memory; strengthens memory on success."""
        r = self.recall(part, i, now)
        ok = self.rng.random() < r and self.rng.random() >= self.slip(tired)
        if ok:
            p = self.points[part][i]
            spaced = (now - p.last).total_seconds() >= 12 * 3600
            p.stability *= TRUTH_PARAMS["stability_growth_spaced" if spaced else "stability_growth_massed"]
            p.last = now
        return ok

    def point_index(self, part: str, point_id: str | None = None, text: str | None = None) -> int:
        if point_id is not None and point_id in self.point_ids[part]:
            return self.point_ids[part].index(point_id)
        if text is not None and text in self.point_texts[part]:
            return self.point_texts[part].index(text)
        return 0


# --------------------------------------------------------------------------------------------------
# Closed loop through tutor_turn
# --------------------------------------------------------------------------------------------------

def iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Run:
    variant: str
    kind: str
    seed: int
    start: datetime
    session_days: list            # day offsets of sessions
    tag: str = ""                 # scenario name, part of the student id
    student_id: str = ""
    log: dict = field(default_factory=lambda: {
        "first_secure": [], "session_samples": [], "sessions": [], "reviews_due_by_day": [],
        "turns": 0, "evidence": 0, "immediate_evidence": 0, "mcq_answers": 0, "guess_by_options": {},
        "quiz_me_check": None})


def _plan_json(student_id: str) -> dict:
    from edux import learner
    row = learner._conn().execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (student_id,)).fetchone()
    return json.loads(row[0]) if row else {}


def run_student(run: Run) -> dict:
    """Run one synthetic student through their sessions; returns the run log."""
    from edux import graph, learner, service
    rng = random.Random(f"{run.kind}-{run.seed}")
    truth = Truth(run.kind, rng)
    truth.setup()
    clamps0 = CLAMPS["n"]
    sid = f"sim-{run.kind}-{run.seed}-{run.tag}"
    run.student_id = sid
    learner.add_student(sid, "example-mini", student_id=sid)
    student = learner.get_student(sid)
    parts = learner.all_parts()
    secure_th = learner._settings().levels.secure
    seen_secure: set = set()
    evidence_on: dict = {p: 0 for p in parts}
    study_minutes: dict = {p: 0.0 for p in parts}
    labels = ({"question_depth": "surface", "engagement": "passive"} if run.kind in ("guesser", "offloader")
              else {"question_depth": "mechanism", "engagement": "active"})
    L = run.log

    def evidence_count() -> int:
        return learner._conn().execute("SELECT count(*) FROM evidence_log WHERE student_id = ?", (sid,)).fetchone()[0]

    def check_first_secure(now: datetime, minute: float) -> None:
        for p in parts:
            if p in seen_secure:
                continue
            if learner.part_p(sid, p, iso(now)) >= secure_th:
                seen_secure.add(p)
                n_ev = learner._conn().execute("SELECT count(*) FROM evidence_log WHERE student_id = ? AND part_id = ?",
                                               (sid, p)).fetchone()[0]
                L["first_secure"].append({"part": p, "true_mastery": truth.mastery(p, now), "n_evidence": n_ev,
                                          "study_minutes": study_minutes[p], "day": (now - run.start).days})

    def sample(now: datetime, tag: str) -> None:
        rows = []
        for p in parts:
            rows.append({"part": p, "p": learner.part_p(sid, p, iso(now)), "m": truth.mastery(p, now)})
        L["session_samples"].append({"tag": tag, "day": (now - run.start).total_seconds() / 86400, "rows": rows})

    clock = {"t": run.start, "session_start": run.start}
    streak = {"cur": 0, "max": 0, "n": 0}   # consecutive plans that step back from a stuck part

    def minute() -> float:
        return (clock["t"] - clock["session_start"]).total_seconds() / 60

    def tired_now() -> bool:
        return run.kind == "tired" and minute() >= TRUTH_PARAMS["tired_after_min"]

    def advance() -> None:
        lo, hi = TRUTH_PARAMS["minutes_per_turn"]
        clock["t"] += timedelta(seconds=int(rng.uniform(lo, hi) * 60))

    def turn(message: str, node_ids=None, answer=None, choice="none") -> dict:
        advance()
        this = {**labels, "choice": choice}
        out = service.tutor_turn(student, message, this, node_ids=node_ids, answer=answer, client="sim", at=iso(clock["t"]))
        L["turns"] += 1
        if not out.get("ok"):
            raise RuntimeError(f"tutor_turn error: {out.get('error')} (answer={answer})")
        return out

    def experience(out: dict, saved: dict) -> None:
        """The student reads the plan: teaching steps may teach points (truth update)."""
        t, tired = clock["t"], tired_now()
        for step in saved.get("plan", []):
            part, data = step.get("part_id"), step.get("data") or {}
            if part not in truth.points:
                continue
            mv = step["move"]
            if mv == "teach_point":
                truth.teach(part, data["index"] - 1, t, tired)
            elif mv == "show":
                truth.teach(part, truth.point_index(part, text=data.get("point")), t, tired,
                            TRUTH_PARAMS["show_learn_factor"])
            elif mv == "reteach":
                if data.get("point"):
                    truth.teach(part, truth.point_index(part, text=data["point"]), t, tired)
                for m in data.get("missing") or []:
                    truth.teach(part, truth.point_index(part, text=m), t, tired)
                if not data.get("point") and not data.get("missing"):   # whole-part reteach (stuck)
                    for i in range(len(truth.points[part])):
                        truth.teach(part, i, t, tired)
            elif mv == "feedback" and data.get("correct") is False:
                pass   # feedback learning handled at answer time

    def answer_for(saved: dict) -> tuple[dict | None, str]:
        """The student's answer to the plan's asking step (None: nothing asked)."""
        steps = saved.get("plan", [])
        asking = next((s for s in reversed(steps) if "answer_type" in (s.get("data") or {})), None)
        if asking is None:
            return None, "none"
        part, kind = asking["part_id"], asking["data"]["answer_type"]
        t, tired = clock["t"], tired_now()
        if run.kind == "offloader" and rng.random() > TRUTH_PARAMS["offloader_answers"]:
            return None, "just_show_me"
        if kind == "mcq":
            mcq = saved.get("mcq") or {}
            options = mcq.get("options") or {}
            letters = sorted(options)
            n = len(letters)
            if run.kind == "guesser":
                letter = "A"
            else:
                purpose = mcq.get("purpose")
                if purpose == "intuition":
                    # an untaught intuition question: knows it only if they already know point 1
                    knows = truth.retrieve(part, 0, t, tired)
                else:
                    i = truth.point_index(part, point_id=mcq.get("point_id"))
                    knows = truth.retrieve(part, i, t, tired)
                letter = (next(k for k in letters if options[k]["id"] == "correct") if knows
                          else rng.choice(letters))
            picked = options[letter]["id"]
            L["mcq_answers"] += 1
            g = L["guess_by_options"].setdefault(str(n), [0, 0])
            if run.kind == "guesser":
                g[0] += 1
                g[1] += picked == "correct"
            if picked != "correct" and mcq.get("purpose") != "intuition":
                i = truth.point_index(part, point_id=mcq.get("point_id"))
                truth.teach(part, i, t, tired, TRUTH_PARAMS["feedback_learn_factor"])
            return {"part_id": part, "type": "mcq", "choice": letter}, "none"
        # open answers: explain_back / extend
        n = len(truth.points[part])
        factor = TRUTH_PARAMS["extend_factor"] if kind == "extend" else 1.0
        met = []
        for i in range(n):
            if run.kind == "guesser":
                ok = rng.random() < TRUTH_PARAMS["open_answer_lucky_tick"]
            else:
                ok = (truth.retrieve(part, i, t, tired) and rng.random() < factor) or \
                     rng.random() < TRUTH_PARAMS["open_answer_lucky_tick"]
            if ok:
                met.append(graph.point_letter(i))
        return {"part_id": part, "type": kind, "points_met": met}, "none"

    def work_part(part: str, cap: int, deadline: datetime) -> None:
        """One thread on a part: ask about it, then answer whatever the plan asks until it stops asking."""
        name = graph.get_node(part)["name"]
        choice = "just_show_me" if run.kind == "offloader" else "none"
        out = turn(f"Can you help me with {name}?", node_ids=[part], choice=choice)
        for _ in range(cap):
            saved = _plan_json(sid)
            if any((st.get("data") or {}).get("stuck") for st in saved.get("plan", [])):
                streak["cur"] += 1
                streak["max"] = max(streak["max"], streak["cur"])
                streak["n"] += 1
            else:
                streak["cur"] = 0
            experience(out, saved)
            check_first_secure(clock["t"], minute())
            study_minutes[part] += 1.75
            if clock["t"] >= deadline:
                return
            moves = [s["move"] for s in saved.get("plan", [])]
            if "offer_stop" in moves:
                out = turn(f"I'll keep going with {name}", node_ids=[part])   # carries on (most students do)
                continue
            answer, choice = answer_for(saved)
            if answer is None and choice == "none":
                return
            if answer is None:   # offloader: "just show me" instead of answering
                out = turn("just show me", node_ids=[part], choice="just_show_me")
                continue
            before = evidence_count()
            out = turn("my answer", answer=answer)
            after = evidence_count()
            if after > before:
                row = learner._conn().execute(
                    "SELECT evidence_type, part_id, id FROM evidence_log WHERE student_id = ? ORDER BY id DESC LIMIT 1",
                    (sid,)).fetchone()
                L["evidence"] += 1
                d = learner._conn().execute("SELECT 1 FROM evidence_log l WHERE l.id = ? AND l.origin='chat'",
                                            (row["id"],)).fetchone()
                if row["evidence_type"] != "prequestion" and learner._recently_taught(learner._conn(), sid, row["part_id"],
                                                                                      iso(clock["t"])):
                    L["immediate_evidence"] += 1
        check_first_secure(clock["t"], minute())

    # --- the timeline ---
    last_day = -1
    for day in run.session_days:
        # morning count of reviews due (uncapped), for every day since the last session
        for d in range(last_day + 1, day + 1):
            morning = run.start.replace(hour=8) + timedelta(days=d)
            n_due = len(learner.due_reviews(sid, 10_000, iso(morning)))
            L["reviews_due_by_day"].append({"day": d, "days_to_exam": (EXAM - morning).total_seconds() / 86400,
                                            "due": n_due})
        last_day = day
        start = run.start.replace(hour=17) + timedelta(days=day, minutes=rng.randint(0, 90))
        clock["t"] = clock["session_start"] = start
        deadline = start + timedelta(minutes=TRUTH_PARAMS["session_minutes"])
        stuck_flags: set = set()
        attempted: set = set()
        streak.update(cur=0, max=0, n=0)
        # reviews first
        for r in learner.due_reviews(sid, TRUTH_PARAMS["reviews_per_session"], iso(start)):
            if clock["t"] >= deadline:
                break
            attempted.add(r["part_id"])
            work_part(r["part_id"], 6, deadline)
            st = learner.session_state(sid, iso(clock["t"]))
            if st:
                stuck_flags |= {p["part_id"] for p in st["stuck_parts"]}
        # then study: first part in pack order the model doesn't call secure
        per_part_turns: dict = {}
        while clock["t"] < deadline:
            open_parts = [p for p in parts if learner.level(learner.part_p(sid, p, iso(clock["t"]))) != "secure"
                          and per_part_turns.get(p, 0) < TRUTH_PARAMS["turns_per_part_cap"]]
            if not open_parts:
                open_parts = sorted(parts, key=lambda p: learner.part_p(sid, p, iso(clock["t"])))[:1]
            part = open_parts[0]
            attempted.add(part)
            t0 = L["turns"]
            work_part(part, TRUTH_PARAMS["turns_per_part_cap"], deadline)
            per_part_turns[part] = per_part_turns.get(part, 0) + (L["turns"] - t0)
            st = learner.session_state(sid, iso(clock["t"]))
            if st:
                stuck_flags |= {p["part_id"] for p in st["stuck_parts"]}
        st = learner.session_state(sid, iso(clock["t"])) or {}
        stuck_flags |= {p["part_id"] for p in st.get("stuck_parts", [])}
        L["sessions"].append({"day": day, "minutes": st.get("minutes"), "fatigued": bool(st.get("fatigued")),
                              "onset": st.get("fatigued_since_minute"), "stuck": sorted(stuck_flags),
                              "stepback_max_streak": streak["max"], "stepback_plans": streak["n"],
                              "attempted": sorted(attempted)})
        sample(clock["t"], "session_end")
        sample(run.start.replace(hour=8) + timedelta(days=day + 1), "next_morning")
    sample(EXAM, "exam_day")
    # per-evidence fatigue truth vs flag, from evidence_derived
    rows = learner._conn().execute(
        """SELECT l.ts, d.session_id, d.fatigued, d.weight FROM evidence_log l JOIN evidence_derived d ON d.evidence_id = l.id
           WHERE l.student_id = ? ORDER BY l.ts""", (sid,)).fetchall()
    L["evidence_fatigue"] = [{"min": (learner.parse_ts(r["ts"]) - learner.parse_ts(r["session_id"])).total_seconds() / 60,
                              "flag": r["fatigued"]} for r in rows]
    L["final_true"] = {p: truth.mastery(p, EXAM) for p in parts}
    L["clamps"] = CLAMPS["n"] - clamps0
    return L
