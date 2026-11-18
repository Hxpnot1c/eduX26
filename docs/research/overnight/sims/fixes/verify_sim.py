"""w4-fix-verify: the wave-2 literacy sim (../literacy/lit_model.py) with three scoring changes, alone and together.

  graded         Verify evidence that clears correct_share moves p_known `score` of the way (3/4 ticks = 3/4 of 4/4).
  found_problem  a Verify answer that reports a dead or mismatched source (labelled source_conflict) scores 1.
  ignored        "missing": an ignored task or check writes no evidence (lit_model already supports this).

lit_model has no bad-source outcome, so this adds one (EVERY number in EXTRA is OUR CHOICE):
  - each answered verify task has a bad source (dead or mismatched) with p = bad_source;
  - a student facing a bad source reports the problem with p = detect[group], else answers as usual ("it matched");
  - a student facing a good source falsely reports a problem with p = false_report[group];
  - a report is ticked a (opened) and d (said whether it matched), plus c (compared) for a mismatch, never b;
    label noise flips ticks as in lit_model; the chatbot misses the source_conflict label with p = noise.fn and
    sets it wrongly on an ordinary answer with p = noise.fp / 4.
Extra uniforms come from a separate RNG per (seed, session), so lit_model's common random numbers are unchanged.

  PYTHONPATH=../literacy python verify_sim.py [N] [bad_source]
"""
from __future__ import annotations

import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

import grid
import lit_model as M

EXTRA = {
    "bad_source": 0.20,   # share of verify tasks whose cited source is dead or doesn't say what was claimed
    "dead_share": 0.5,    # of bad sources (and of false reports), the share that are dead pages rather than mismatches
    "detect": {"none": 0.25, "gamer": 0.15, "partial": 0.60, "strong": 0.90},
    "false_report": {"none": 0.05, "gamer": 0.05, "partial": 0.03, "strong": 0.02},
}


@dataclass(frozen=True)
class Cfg(M.Cfg):
    graded: bool = False
    found_problem: bool = False


class FastBackend(M.FastBackend):
    def _evidence(self, part: str, kind: str, score: float, t: int) -> None:
        c = self.cfg
        if not (getattr(c, "graded", False) and part == M.VERIFY and score >= c.correct_share and score < 1.0):
            return super()._evidence(part, kind, score, t)
        st = self._get(part)
        before = self._pnow(st, t)
        slip, guess = c.slip_guess(kind)
        p = before * (1 - slip) / (before * (1 - slip) + (1 - before) * guess)
        p += (1 - p) * c.learn_rate
        p = before + score * (p - before)      # learner.apply_evidence_event: weight *= score on correct Verify
        st[1] = max(c.min_half_life, st[1] * c.on_success)
        st[0] = p
        st[2] = t


def verify_score(cfg, group: str, sk: str, seed: int, idx: int, ticks_true: list[bool], u_noise: list[float],
                 noise: M.Noise) -> tuple[float, str]:
    """The score of one answered verify task, and what happened (ok / caught / missed / false_report)."""
    r = random.Random(seed * 7919 + idx * 104729 + 17)
    u_bad, u_det, u_false, u_dead, u_lab, u_fc = (r.random() for _ in range(6))
    bad = u_bad < EXTRA["bad_source"]
    reports = (u_det < EXTRA["detect"][sk]) if bad else (u_false < EXTRA["false_report"][sk])
    if reports:
        dead = u_dead < EXTRA["dead_share"]
        ticks = sum(M._label([True, False, not dead, True], u_noise, noise))
        labelled = u_lab >= noise.fn
        score = 1.0 if (cfg.found_problem and labelled) else ticks / 4
        return score, ("caught" if bad else "false_report")
    ticks = sum(M._label(ticks_true, u_noise, noise))
    score = 1.0 if (cfg.found_problem and u_fc < noise.fp / 4) else ticks / 4
    return score, ("missed" if bad else "ok")


def run_student(backend, cfg, group: str, seed: int, noise: M.Noise, ignore_model: str) -> dict:
    """lit_model.run_student, with the verify answer scored by verify_score (the only change)."""
    real_answer = backend.answer_turn
    # Re-run lit_model's driver with a hook on verify-task answers: we wrap backend.answer_turn and recompute the
    # score for ail_task on Verify from the same tick uniforms, so all other behaviour is lit_model's own.
    sessions, _ = M.make_script(seed)
    by_time = {}
    for i, s in enumerate(sessions):
        by_time[s.t] = (i, s)
    state = {"session": None}
    out_extra = {"caught": 0, "missed": 0, "false_report": 0, "ok": 0}

    def research_turn(t, labelled, _orig=backend.research_turn):
        if t in by_time:
            state["session"] = by_time[t]
        return _orig(t, labelled)

    def hooked_answer(part, kind, score, t):
        if part == M.VERIFY and kind == "ail_task" and state["session"] is not None:
            i, s = state["session"]
            sk = M.skill_at(group, s.week)
            true_t = [u < p for u, p in zip(s.u_ticks, M.TRUTH["tick_task"][sk])]
            score, what = verify_score(cfg, group, sk, seed, i, true_t, s.u_tick_noise, noise)
            out_extra[what] += 1
        return real_answer(part, kind, score, t)

    backend.research_turn = research_turn
    backend.answer_turn = hooked_answer
    out = M.run_student(backend, cfg, group, seed, noise, ignore_model)
    out["extra"] = out_extra
    return out


def cell(cfg, noise, ign, n):
    saved = M.run_student, M.FastBackend
    M.FastBackend = FastBackend
    orig_run = saved[0]
    # grid.cell_metrics calls M.run_student(M.FastBackend(cfg), ...): route it through our wrapper
    M.run_student = lambda backend, c, g, seed, nz, im: _wrapped(orig_run, backend, c, g, seed, nz, im)
    try:
        return grid.cell_metrics(cfg, noise, ign, n)
    finally:
        M.run_student, M.FastBackend = saved


def _wrapped(orig_run, backend, cfg, group, seed, noise, ign):
    saved = M.run_student
    M.run_student = orig_run
    try:
        return run_student(backend, cfg, group, seed, noise, ign)
    finally:
        M.run_student = saved


VARIANTS = {
    "branch": Cfg(),
    "missing": Cfg(ignored="missing"),
    "missing+graded": Cfg(ignored="missing", graded=True),
    "missing+found": Cfg(ignored="missing", found_problem=True),
    "fix (missing+graded+found)": Cfg(ignored="missing", graded=True, found_problem=True),
}
NOISES = {"0": M.Noise(), "sym10": M.Noise.symmetric(0.10), "sym20": M.Noise.symmetric(0.20), "len20": M.Noise.lenient(0.20)}


def main(n: int, bad: float) -> dict:
    EXTRA["bad_source"] = bad
    jobs = {(v, nk, ig): (cfg, nv, ig, n) for v, cfg in VARIANTS.items() for nk, nv in NOISES.items() for ig in ("mnar", "mcar")}
    with ProcessPoolExecutor(8, initializer=_set_bad, initargs=(bad,)) as ex:
        futs = {k: ex.submit(cell, *a) for k, a in jobs.items()}
        res = {k: f.result() for k, f in futs.items()}
    return {f"{v}|{nk}|{ig}": m for (v, nk, ig), m in res.items()}


def _set_bad(bad):
    EXTRA["bad_source"] = bad


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    bad = float(sys.argv[2]) if len(sys.argv) > 2 else EXTRA["bad_source"]
    res = main(n, bad)
    outp = Path(__file__).resolve().parent / "results" / f"verify_sim_n{n}_bad{bad}.json"
    outp.parent.mkdir(exist_ok=True)
    outp.write_text(json.dumps({"n": n, "extra": EXTRA, "metrics": res}, indent=1))
    keys = [("fs_point_max", "none secure (worst weekly)"), ("fs_event_ever", "none ever secure in-chat"),
            ("gamer_point_max", "gamer secure (worst weekly)"), ("gamer_secure_w3_10", "gamer secure w3-10"),
            ("partial_secure_w3_10", "partial secure w3-10"), ("strong_secure_w3_10", "strong secure w3-10"),
            ("auc_none_strong_w8", "AUC none-strong w8"), ("auc_gamer_strong_w8", "AUC gamer-strong w8"),
            ("strong_days_to_secure_median", "strong median days to secure")]
    for ig in ("mnar", "mcar"):
        for nk in NOISES:
            print(f"\n### Verify, noise {nk}, ignoring {ig}, N={n}/group, bad_source={bad}")
            print("| metric | " + " | ".join(VARIANTS) + " |")
            print("|---|" + "---|" * len(VARIANTS))
            for key, label in keys:
                vals = [res[f"{v}|{nk}|{ig}"]["verify"][key] for v in VARIANTS]
                print(f"| {label} | " + " | ".join("never" if x == float("inf") else f"{x:.3f}" if isinstance(x, float) else str(x) for x in vals) + " |")
    print(f"\nwritten {outp}")
