"""AI-literacy scoring simulation (overnight research w2-02).

Synthetic students with a known AI-literacy skill (none / partial / strong, plus an "improver" who moves from none
to strong after week 4) go through the step 05e literacy flow for 10 weeks. The flow is the one in the 05e branch
(service.tutor_turn -> plan.literacy_task, service._literacy_followup, service._how_ai_works), emulated turn by turn
here, and the learner model underneath is either:

- RealBackend: the 05e branch's own edux.learner (record_exchange / record_evidence / part_p) on a throwaway
  EDUX_DATA_DIR, with settings swapped in memory (nothing on disk is edited); or
- FastBackend: a pure-Python replica of the same learner rules for literacy parts, used for the settings grid.
  validate.py checks that both give the same numbers on the same students.

"Literacy-only trick": the simulated students produce literacy evidence only, so the global keys bkt.prior,
bkt.learn_rate, bkt.correct_share and decay.base_half_life_days act as literacy-only settings here. In the product
they would need new per-literacy keys (a code change), because the global ones also move the economics parts.

EVERY number in TRUTH below is OUR CHOICE. The students are synthetic; results describe how the scoring rules behave
under these assumptions, not how real students behave.
"""

from __future__ import annotations

import functools
import math
import random
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

# --------------------------------------------------------------------------------------------------
# Truth model: ALL OUR CHOICE
# --------------------------------------------------------------------------------------------------
FEATURES = ("concept", "context", "asks_sources", "asks_reasoning")
TRUTH = {
    # P(the question shows each feature), per skill group, in FEATURES order
    # none: plain factual questions ("UK inflation in 2022?") often carry the idea and a setting without any skill
    "feat": {"none": (0.70, 0.40, 0.05, 0.10), "gamer": (0.80, 0.50, 0.60, 0.30), "partial": (0.90, 0.70, 0.35, 0.35), "strong": (0.95, 0.90, 0.75, 0.70)},
    # an Ask rewrite after coaching: each missing feature now shown with p + (1 - p) * coach_boost
    "coach_boost": 0.4,
    # P(each verify tick) when answering a verify task: p1 opened (a claim), p2 publisher+date, p3 compares, p4 matched
    "tick_task": {"none": (0.50, 0.10, 0.25, 0.40), "gamer": (0.90, 0.30, 0.50, 0.90), "partial": (0.70, 0.40, 0.60, 0.70), "strong": (0.90, 0.80, 0.85, 0.90)},
    # an unprompted "I checked" report: same ticks idea; the no-skill version is "I checked, it's right"
    "tick_unprompted": {"none": (0.80, 0.10, 0.20, 0.80), "gamer": (0.90, 0.30, 0.50, 0.90), "partial": (0.80, 0.40, 0.60, 0.80), "strong": (0.90, 0.80, 0.85, 0.90)},
    # P(an unprompted check report in a research session)
    "unprompted_rate": {"none": 0.03, "gamer": 0.15, "partial": 0.08, "strong": 0.25},
    # P(ignoring a task or check): "mcar" = the same for everyone; "mnar" = more ignoring at low skill
    "ignore": {"mcar": {"none": 0.30, "gamer": 0.30, "partial": 0.30, "strong": 0.30},
               "mnar": {"none": 0.50, "gamer": 0.30, "partial": 0.30, "strong": 0.15}},
    # P(rewriting the question when given an Ask task) = 1 - ignore (the same ignore model)
    # P(right letter) on a how-AI-works check; "none" is test-wise (absolute-wording cues), not 0.25
    "how_correct": {"none": 0.40, "gamer": 0.40, "partial": 0.65, "strong": 0.90},
    "research_per_week": (2, 3),     # 2 or 3 research questions a week, each equally likely
    "how_trigger_per_week": 0.6,     # P(a chatbot-failure trigger for a how-AI-works check in a week)
    "followon_continue": 0.7,        # P(another turn in the session after each turn): mean about 2.3 more turns
    "followon_cap": 6,
    "turn_minutes": (2, 4),
    "has_room": 0.3,                 # P(the plan has room for a one-line re-ask), else the task waits (max_waits); most course plans end in a question (smoke test)
    "how_session_continues": 0.8,    # P(the session goes on long enough to re-ask and then score an ignored check)
    "weeks": 10,
    "improver_switch_week": 4,       # improver: "none" in weeks 1-4, "strong" from week 5
}
# gamer: no checking skill, but has learnt the ritual: asks for sources by habit, restates the reply as a "check"
# (claims to have opened it and that it matched) and often says "I checked" unprompted. Our choice.
GROUPS = ("none", "partial", "strong", "improver", "gamer")
START = datetime(2026, 9, 7, 0, 0, tzinfo=timezone.utc)   # a Monday
T0 = int(START.timestamp())
DAY = 86400
WEEK = 7 * DAY

ASK, VERIFY = "ail_ask", "ail_verify"
HOW_PARTS = ("ail_how_fabrication", "ail_how_confidence", "ail_how_cutoff", "ail_how_agreement")
LIT_PARTS = (ASK, VERIFY) + HOW_PARTS
DIFFICULTY = {ASK: 0.4, VERIFY: 0.5, **{p: 0.4 for p in HOW_PARTS}}   # from ingest/ai_literacy/nodes.csv


# --------------------------------------------------------------------------------------------------
# Settings under test (literacy-relevant subset). Defaults = the 05e branch's settings.toml.
# --------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Cfg:
    prior: float = 0.30
    learn_rate: float = 0.10
    correct_share: float = 0.67      # Ask (and, if verify_share is None, Verify)
    verify_share: float | None = None
    half_life: float = 2.0            # decay.base_half_life_days (literacy-only here)
    on_success: float = 2.0
    on_failure: float = 0.5
    min_half_life: float = 1.0
    seen_refresh: float = 0.2
    q_slip: float = 0.15              # ail_question
    q_guess: float = 0.20
    t_slip: float = 0.10              # ail_task
    t_guess: float = 0.15
    u_slip: float = 0.05              # ail_unprompted
    u_guess: float = 0.10
    h_slip: float = 0.10              # ail_how
    h_guess: float = 0.25
    ignored: str = "zero"             # "zero" (05e branch) or "missing" (recorded as an engagement event only)
    ask_min_features: int = 2
    secure_every: int = 3
    how_secure_every: int = 3
    max_followups: int = 1
    max_waits: int = 2
    secure: float = 0.75
    new: float = 0.40
    prior_shift: float = 0.15
    half_life_shift: float = 0.5

    def slip_guess(self, kind: str) -> tuple[float, float]:
        return {"ail_question": (self.q_slip, self.q_guess), "ail_task": (self.t_slip, self.t_guess),
                "ail_unprompted": (self.u_slip, self.u_guess), "ail_how": (self.h_slip, self.h_guess)}[kind]

    def level(self, p: float) -> str:
        return "new" if p < self.new else "secure" if p >= self.secure else "developing"


BRANCH = Cfg()


def iso(t: int) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------------------------------
# Backends
# --------------------------------------------------------------------------------------------------
class FastBackend:
    """Pure-Python replica of edux.learner for literacy parts (no prerequisites, no course parts, no fatigue:
    sessions here are under 25 minutes, so the fatigue rule can't fire). Times are integer seconds."""

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.state: dict[str, list] = {}
        self.research = 0

    def _init(self, part: str) -> list:
        c = self.cfg
        shift = max(-1.0, min(1.0, (DIFFICULTY[part] - 0.5) / 0.5))
        prior = min(0.99, max(0.01, c.prior - c.prior_shift * shift))
        hl = max(c.min_half_life, c.half_life * (1 - c.half_life_shift * shift))
        return [prior, hl, None]          # p_known, half_life_days, clock_start

    def _get(self, part: str) -> list:
        st = self.state.get(part)
        if st is None:
            st = self.state[part] = self._init(part)
        return st

    @staticmethod
    def _pnow(st: list, t: int) -> float:
        if st[2] is None:
            return st[0]
        days = max(0.0, (t - st[2]) / 86400)
        return st[0] * 0.5 ** (days / st[1])

    def p(self, part: str, t: int) -> float:
        st = self.state.get(part)
        return self._init(part)[0] if st is None else self._pnow(st, t)

    def _exchange(self, part: str, t: int) -> None:
        st = self._get(part)
        odds = st[0] / (1 - st[0])          # nudge multiplier 1.0 (surface, active): a float round trip only
        st[0] = odds / (1 + odds)
        if st[2] is not None:
            d = timedelta(seconds=t - st[2]) * self.cfg.seen_refresh
            st[2] = st[2] + int(d.total_seconds() // 1)   # the code stores the clock to the second (truncated)

    def _evidence(self, part: str, kind: str, score: float, t: int) -> None:
        c = self.cfg
        st = self._get(part)
        before = self._pnow(st, t)
        correct = score >= (c.verify_share if part == VERIFY and c.verify_share is not None else c.correct_share)
        slip, guess = c.slip_guess(kind)
        if correct:
            p = before * (1 - slip) / (before * (1 - slip) + (1 - before) * guess)
        else:
            p = before * slip / (before * slip + (1 - before) * (1 - guess))
        p += (1 - p) * c.learn_rate
        st[1] = max(c.min_half_life, st[1] * (c.on_success if correct else c.on_failure))
        st[0] = p
        if correct or st[2] is not None:
            st[2] = t

    # the turn-level API used by the driver
    def research_turn(self, t: int, labelled: list[str]) -> None:
        self.research += 1
        self._exchange(ASK, t)
        self._evidence(ASK, "ail_question", len(labelled) / 4, t)

    def research_turns(self, t: int) -> int:
        return self.research

    def answer_turn(self, part: str, kind: str, score: float, t: int) -> None:
        self._exchange(part, t)
        self._evidence(part, kind, score, t)

    def ignored(self, part: str, kind: str, t: int) -> None:
        if self.cfg.ignored == "zero":
            self._evidence(part, kind, 0.0, t)


class RealBackend:
    """The 05e branch's edux.learner, on the database in EDUX_DATA_DIR, with cfg swapped in as settings."""

    def __init__(self, cfg: Cfg, student_name: str):
        from edux import graph, learner, service
        from edux.settings import Settings, _build, SETTINGS_PATH
        import tomllib, dataclasses
        self.learner = learner
        with open(SETTINGS_PATH, "rb") as f:
            d = tomllib.load(f)
        d["bkt"]["prior"], d["bkt"]["learn_rate"], d["bkt"]["correct_share"] = cfg.prior, cfg.learn_rate, cfg.correct_share
        d["decay"]["base_half_life_days"] = cfg.half_life
        ev = d["bkt"]["evidence"]
        for kind in ("ail_question", "ail_task", "ail_unprompted", "ail_how"):
            slip, guess = cfg.slip_guess(kind)
            ev[kind] = {"slip": slip, "guess": guess}
        d["literacy"]["ask_min_features"] = cfg.ask_min_features
        s = _build(Settings, d, "")
        learner._settings = lambda: s
        service._settings = lambda: s
        graph._settings = lambda: s
        self.cfg = cfg
        self.sid = learner.add_student(student_name, "example-mini")["id"]

    def p(self, part: str, t: int) -> float:
        return self.learner.part_p(self.sid, part, iso(t))

    def research_turn(self, t: int, labelled: list[str]) -> None:
        ev = self.learner.question_evidence(labelled)
        self.learner.record_exchange(self.sid, [ASK], "surface", "active", ts=iso(t), evidence=[ev], apply="now",
                                     request={"request_type": "research", "question_features": labelled})

    def research_turns(self, t: int) -> int:
        return self.learner.research_turns(self.sid, iso(t))

    def answer_turn(self, part: str, kind: str, score: float, t: int) -> None:
        if part == VERIFY and self.cfg.verify_share is not None and self.cfg.verify_share != self.cfg.correct_share:
            # emulate a Verify-only threshold exactly: the BKT update only sees score >= correct_share
            score = 1.0 if score >= self.cfg.verify_share else 0.0
        self.learner.record_exchange(self.sid, [part], "surface", "active", ts=iso(t), apply="now",
                                     evidence=[{"part_id": part, "type": kind, "score": score}],
                                     request={"request_type": "concept"})

    def ignored(self, part: str, kind: str, t: int) -> None:
        if self.cfg.ignored == "zero":
            self.learner.record_evidence(self.sid, part, kind, 0.0, ts=iso(t), apply="now", check_id="ignored")


# --------------------------------------------------------------------------------------------------
# Behaviour scripts (drawn once per student, so every settings variant sees the same student)
# --------------------------------------------------------------------------------------------------
@dataclass
class Session:
    t: int
    week: int
    u_feat: list            # 4 uniforms: true features
    u_feat_noise: list      # 4 uniforms: label flips
    u_rewrite: float
    u_rew_feat: list
    u_rew_noise: list
    u_answer: float
    u_ticks: list
    u_tick_noise: list
    n_follow: int
    u_room: list            # one per follow-on turn
    u_unprompted: float
    u_unp_turn: float
    u_unp_ticks: list
    u_unp_noise: list
    u_false_unp: float
    u_false_ticks: list


@dataclass
class HowSession:
    t: int
    week: int
    part: str
    u_answer: float
    u_correct: float
    u_continue: float


def _u(rng: random.Random, n: int) -> list:
    return [rng.random() for _ in range(n)]


@functools.lru_cache(maxsize=None)
def make_script(seed: int) -> tuple[list[Session], list[HowSession]]:
    rng = random.Random(seed)
    sessions, hows = [], []
    for w in range(TRUTH["weeks"]):
        n = rng.choice(TRUTH["research_per_week"])
        days = sorted(rng.sample(range(7), n))
        for d in days:
            t = T0 + w * WEEK + d * DAY + rng.randint(16 * 3600, 21 * 3600)
            n_follow = 0
            while n_follow < TRUTH["followon_cap"] and rng.random() < TRUTH["followon_continue"]:
                n_follow += 1
            sessions.append(Session(
                t=t, week=w, u_feat=_u(rng, 4), u_feat_noise=_u(rng, 4), u_rewrite=rng.random(),
                u_rew_feat=_u(rng, 4), u_rew_noise=_u(rng, 4), u_answer=rng.random(), u_ticks=_u(rng, 4),
                u_tick_noise=_u(rng, 4), n_follow=n_follow, u_room=_u(rng, TRUTH["followon_cap"]),
                u_unprompted=rng.random(), u_unp_turn=rng.random(), u_unp_ticks=_u(rng, 4), u_unp_noise=_u(rng, 4),
                u_false_unp=rng.random(), u_false_ticks=_u(rng, 4)))
        if rng.random() < TRUTH["how_trigger_per_week"]:
            d = rng.randrange(7)
            t = T0 + w * WEEK + d * DAY + rng.randint(16 * 3600, 21 * 3600) + 1800   # not inside a research session
            hows.append(HowSession(t=t, week=w, part=rng.choice(HOW_PARTS), u_answer=rng.random(),
                                   u_correct=rng.random(), u_continue=rng.random()))
    sessions.sort(key=lambda s: s.t)
    hows.sort(key=lambda s: s.t)
    return sessions, hows


# --------------------------------------------------------------------------------------------------
# Noise model
# --------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Noise:
    fp: float = 0.0    # P(a label is ticked when the student didn't show it)
    fn: float = 0.0    # P(a label is missed when the student did show it)
    false_unprompted: float = 0.0   # P(per research session) the chatbot reports an unprompted check that wasn't there

    @staticmethod
    def symmetric(e: float) -> "Noise":
        return Noise(fp=e, fn=e, false_unprompted=e / 4)

    @staticmethod
    def lenient(e: float) -> "Noise":
        return Noise(fp=e, fn=e / 3, false_unprompted=e / 4)


def _label(true: list[bool], u: list[float], noise: Noise) -> list[bool]:
    return [(u_i >= noise.fn) if x else (u_i < noise.fp) for x, u_i in zip(true, u)]


# --------------------------------------------------------------------------------------------------
# The driver: the 05e literacy flow, turn by turn
# --------------------------------------------------------------------------------------------------
def skill_at(group: str, week: int) -> str:
    if group == "improver":
        return "none" if week < TRUTH["improver_switch_week"] else "strong"
    return group


def read_times() -> list[int]:
    """Weekly progress reads: Sunday 21:00 of each week."""
    return [T0 + w * WEEK + 6 * DAY + 21 * 3600 for w in range(TRUTH["weeks"])]


def run_student(backend, cfg: Cfg, group: str, seed: int, noise: Noise, ignore_model: str) -> dict:
    sessions, hows = make_script(seed)
    events = [(s.t, 0, s) for s in sessions] + [(h.t, 1, h) for h in hows]
    reads = read_times()
    events += [(t, 2, None) for t in reads]
    events.sort(key=lambda e: (e[0], e[1]))
    out = {"reads": [], "first_secure": {}, "moments": {"ask": 0, "verify": 0, "how": 0},
           "scores": {"ask": [], "verify": [], "unprompted": [], "how": []},
           "ignored": {"ask": 0, "verify": 0, "how": 0}}
    how_count = {p: 0 for p in HOW_PARTS}

    def note_secure(skill: str, part_or_none, t: int) -> None:
        if skill in out["first_secure"]:
            return
        if skill == "how":
            p = sum(backend.p(x, t) for x in HOW_PARTS) / len(HOW_PARTS)
        else:
            p = backend.p(part_or_none, t)
        if p >= cfg.secure:
            out["first_secure"][skill] = {"t": t - T0, "moments": out["moments"][skill]}

    for t, kind, obj in events:
        if kind == 2:
            out["reads"].append({"ask": backend.p(ASK, t), "verify": backend.p(VERIFY, t),
                                 "how": sum(backend.p(x, t) for x in HOW_PARTS) / len(HOW_PARTS),
                                 **{x: backend.p(x, t) for x in HOW_PARTS}})
            continue
        sk = skill_at(group, obj.week)
        ign = TRUTH["ignore"][ignore_model][sk]
        if kind == 1:   # a how-AI-works trigger (its own session)
            h = obj
            how_count[h.part] += 1
            if cfg.level(backend.p(h.part, t)) == "secure" and how_count[h.part] % cfg.how_secure_every:
                continue
            if h.u_answer >= ign:
                score = 1.0 if h.u_correct < TRUTH["how_correct"][sk] else 0.0
                backend.answer_turn(h.part, "ail_how", score, t + 180)
                out["scores"]["how"].append(score)
                out["moments"]["how"] += 1
                note_secure("how", None, t + 180)
            elif h.u_continue < TRUTH["how_session_continues"]:
                out["ignored"]["how"] += 1
                backend.ignored(h.part, "ail_how", t + 360)   # re-asked once, then scored 0 (or missing)
                if cfg.ignored == "zero":
                    out["moments"]["how"] += 1
            continue

        s = obj
        noise_on = noise
        # turn 0: the research question
        true_f = [u < p for u, p in zip(s.u_feat, TRUTH["feat"][sk])]
        lab = [f for f, x in zip(FEATURES, _label(true_f, s.u_feat_noise, noise_on)) if x]
        backend.research_turn(t, lab)
        out["scores"]["ask"].append(len(lab) / 4)
        out["moments"]["ask"] += 1
        note_secure("ask", ASK, t)
        task = _new_task(backend, cfg, lab, t)
        rewritten = answered = False
        # unprompted report: which follow-on turn (if any)
        unp_turn = None
        unp_kind = None
        if s.n_follow:
            if s.u_unprompted < TRUTH["unprompted_rate"][sk]:
                unp_kind = "real"
            elif s.u_false_unp < noise.false_unprompted:
                unp_kind = "false"
            if unp_kind:
                unp_turn = 1 + int(s.u_unp_turn * s.n_follow)
        tt = t
        for i in range(1, s.n_follow + 1):
            tt += 60 * (TRUTH["turn_minutes"][0] + (i % (TRUTH["turn_minutes"][1] - TRUTH["turn_minutes"][0] + 1)))
            will = s.u_answer >= ign   # answers a verify task / rewrites after an ask task
            if task and task["skill"] == "verify" and will and not answered:
                true_t = [u < p for u, p in zip(s.u_ticks, TRUTH["tick_task"][sk])]
                ticks = sum(_label(true_t, s.u_tick_noise, noise_on))
                backend.answer_turn(VERIFY, "ail_task", ticks / 4, tt)
                out["scores"]["verify"].append(ticks / 4)
                answered = True
                out["moments"]["verify"] += 1
                note_secure("verify", VERIFY, tt)
                task = None
                continue
            if task and task["skill"] == "ask" and will and not rewritten:
                probs = [p + (1 - p) * TRUTH["coach_boost"] for p in TRUTH["feat"][sk]]
                true_f = [u < p for u, p in zip(s.u_rew_feat, probs)]
                lab = [f for f, x in zip(FEATURES, _label(true_f, s.u_rew_noise, noise_on)) if x]
                backend.research_turn(tt, lab)
                out["scores"]["ask"].append(len(lab) / 4)
                rewritten = True
                out["moments"]["ask"] += 1
                note_secure("ask", ASK, tt)
                task = _new_task(backend, cfg, lab, tt)   # the rewrite is done; a new task may follow it
                continue
            if i == unp_turn:
                prof = TRUTH["tick_unprompted"][sk if unp_kind == "real" else "none"]
                u_t = s.u_unp_ticks if unp_kind == "real" else s.u_false_ticks
                true_t = [u < p for u, p in zip(u_t, prof)]
                ticks = sum(_label(true_t, s.u_unp_noise, noise_on))
                backend.answer_turn(VERIFY, "ail_unprompted", ticks / 4, tt)
                out["scores"]["unprompted"].append(ticks / 4)
                out["moments"]["verify"] += 1
                note_secure("verify", VERIFY, tt)
            # service._literacy_followup on a turn that didn't do the task
            if task:
                if task["followups"] >= cfg.max_followups:
                    part = ASK if task["skill"] == "ask" else VERIFY
                    out["ignored"][task["skill"]] += 1
                    backend.ignored(part, "ail_task", tt)
                    if cfg.ignored == "zero":
                        out["moments"][task["skill"]] += 1
                    task = None
                elif s.u_room[i - 1] < TRUTH["has_room"]:
                    task["followups"] += 1
                elif task["waited"] >= cfg.max_waits:
                    task["followups"] += 1
                else:
                    task["waited"] += 1
        # session ends: a pending task is dropped unscored
    return out


def _new_task(backend, cfg: Cfg, labelled: list[str], t: int) -> dict | None:
    """plan.literacy_task: Ask below ask_min_features labelled features, else Verify; at secure, a task only every
    secure_every research questions."""
    ask = len(set(labelled)) < cfg.ask_min_features
    part = ASK if ask else VERIFY
    if cfg.level(backend.p(part, t)) == "secure" and backend.research_turns(t) % cfg.secure_every:
        return None
    return {"skill": "ask" if ask else "verify", "followups": 0, "waited": 0}
