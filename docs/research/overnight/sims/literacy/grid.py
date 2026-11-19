"""Metrics for one settings variant, and the settings grid (FastBackend; validate.py shows it equals the real code).

  python grid.py baseline           # branch settings and single-change variants, N=1000 per cell -> results/baseline.json
  python grid.py search [N]         # the full grid, N per cell (default 120)    -> results/grid.jsonl
  python grid.py rank               # apply the selection rule                   -> results/ranked.md

Selection rule (fixed before the grid was run; our choice):
  constraint: for Ask and Verify, the share of no-skill students shown "secure" at a weekly progress read
              (max over weeks 2-10) is <= 5% in every cell of noise {0, 10%, 20% symmetric} x ignoring {mcar, mnar};
  objective:  the highest mean share of strong students shown secure at weekly reads in weeks 3-10, averaged over
              Ask and Verify, at 10% symmetric noise and mnar ignoring; ties broken by the faster median time to
              first secure. The 20% lenient-noise cell is reported as a stress test, not constrained.
"""

from __future__ import annotations

import itertools
import json
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path

import lit_model as M

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
NOISES = {"0": M.Noise(), "sym10": M.Noise.symmetric(0.10), "sym20": M.Noise.symmetric(0.20),
          "len20": M.Noise.lenient(0.20)}
IGNORES = ("mcar", "mnar")
SKILLS = ("ask", "verify", "how")


def auc(neg: list[float], pos: list[float]) -> float:
    """Mann-Whitney AUC: P(a random positive scores above a random negative), ties count half."""
    allv = sorted([(v, 0) for v in neg] + [(v, 1) for v in pos])
    ranks, i = {}, 0
    rank_sum = 0.0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        r = (i + 1 + j) / 2
        rank_sum += r * sum(1 for k in range(i, j) if allv[k][1] == 1)
        i = j
    n1, n0 = len(pos), len(neg)
    return (rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else float("nan")


def cell_metrics(cfg: M.Cfg, noise: M.Noise, ign: str, n: int, seed0: int = 0) -> dict:
    res = {g: [M.run_student(M.FastBackend(cfg), cfg, g, seed0 + 100000 * gi + k, noise, ign) for k in range(n)]
           for gi, g in enumerate(M.GROUPS)}
    sec = cfg.secure
    out = {}
    W = M.TRUTH["weeks"]
    for sk in SKILLS:
        m = {}
        none_sec = [[r["reads"][w][sk] >= sec for r in res["none"]] for w in range(W)]
        share = [sum(x) / n for x in none_sec]
        m["fs_point_max"] = max(share[1:])
        m["fs_point_mean"] = statistics.mean(share[1:])
        m["fs_ever"] = sum(any(r["reads"][w][sk] >= sec for w in range(1, W)) for r in res["none"]) / n
        m["fs_event_ever"] = sum(sk in r["first_secure"] for r in res["none"]) / n   # secure right after any moment
        gs = [sum(r["reads"][w][sk] >= sec for r in res["gamer"]) / n for w in range(W)]
        m["gamer_point_max"], m["gamer_secure_w3_10"] = max(gs[1:]), statistics.mean(gs[2:])
        m["auc_gamer_strong_w8"] = auc([r["reads"][7][sk] for r in res["gamer"]], [r["reads"][7][sk] for r in res["strong"]])
        for g in ("partial", "strong"):
            sh = [sum(r["reads"][w][sk] >= sec for r in res[g]) / n for w in range(W)]
            m[f"{g}_secure_w3_10"] = statistics.mean(sh[2:])
            m[f"{g}_secure_w10"] = sh[-1]
        firsts = [r["first_secure"].get(sk) for r in res["strong"]]
        days = sorted(f["t"] / 86400 if f else float("inf") for f in firsts)
        moms = sorted(f["moments"] if f else float("inf") for f in firsts)
        m["strong_days_to_secure_median"] = days[n // 2]
        m["strong_moments_to_secure_median"] = moms[n // 2]
        m["strong_secure_by_w4"] = sum(d <= 28 for d in days) / n
        m["strong_ever_secure"] = sum(d < float("inf") for d in days) / n
        m["strong_moments_w10_mean"] = statistics.mean(r["moments"][sk] for r in res["strong"])
        m["strong_ignored_mean"] = statistics.mean(r["ignored"][sk] for r in res["strong"])
        m["none_ignored_mean"] = statistics.mean(r["ignored"][sk] for r in res["none"])
        imp = [sum(r["reads"][w][sk] >= sec for r in res["improver"]) / n for w in range(W)]
        m["improver_secure_w6"], m["improver_secure_w10"] = imp[5], imp[9]
        for w in (3, 7):   # reads at the end of weeks 4 and 8
            m[f"auc_none_strong_w{w + 1}"] = auc([r["reads"][w][sk] for r in res["none"]], [r["reads"][w][sk] for r in res["strong"]])
            m[f"auc_partial_strong_w{w + 1}"] = auc([r["reads"][w][sk] for r in res["partial"]], [r["reads"][w][sk] for r in res["strong"]])
            m[f"auc_none_partial_w{w + 1}"] = auc([r["reads"][w][sk] for r in res["none"]], [r["reads"][w][sk] for r in res["partial"]])
        out[sk] = m
    return out


def evaluate(cfg: M.Cfg, n: int, noises=NOISES, ignores=IGNORES) -> dict:
    return {f"{nk}|{ig}": cell_metrics(cfg, nv, ig, n) for nk, nv in noises.items() for ig in ignores}


# Noise 0 and len20 are checked for the finalists only.
GRID_NOISES = {k: NOISES[k] for k in ("sym10", "sym20")}


def _eval_job(args):
    cfg, n = args
    return {"cfg": asdict(cfg), "metrics": evaluate(cfg, n, noises=GRID_NOISES)}


GRID = {
    "prior": (0.2, 0.3),
    "learn_rate": (0.10, 0.05, 0.02),
    "half_life": (2.0, 7.0, 14.0, 30.0, 1e6),  # 1e6 = no decay in practice
    "ignored": ("zero", "missing"),
    "correct_share": (0.5, 0.67),             # Ask; ask_min_features tied: 0.5 -> 2, 0.67 -> 3
    "q": ((0.15, 0.20), (0.15, 0.30), (0.10, 0.40)),
    "verify_share": (0.5, 0.67, 1.0),
    "t": ((0.10, 0.15), (0.10, 0.25), (0.10, 0.35)),
    "u_guess": (0.10, 0.20, 0.30),
}


def grid_cfgs():
    """Decomposed grid: Ask's own settings (q) don't touch Verify, and Verify's (verify_share, t, u) don't touch Ask,
    so vary Verify's settings with q fixed at (0.15, 0.30), and q with Verify's fixed at the branch values."""
    keys = list(GRID)
    for vals in itertools.product(*GRID.values()):
        d = dict(zip(keys, vals))
        verify_branch = d["verify_share"] == 0.67 and d["t"] == (0.10, 0.15) and d["u_guess"] == 0.10
        if d["q"] != (0.15, 0.30) and not verify_branch:
            continue
        yield replace(M.BRANCH, prior=d["prior"], learn_rate=d["learn_rate"], correct_share=d["correct_share"],
                      ask_min_features=2 if d["correct_share"] == 0.5 else 3, half_life=d["half_life"],
                      verify_share=d["verify_share"],
                      q_slip=d["q"][0], q_guess=d["q"][1], t_slip=d["t"][0], t_guess=d["t"][1],
                      u_guess=d["u_guess"], ignored=d["ignored"])


def passes(metrics: dict, fs_max: float = 0.05, strict: bool = False) -> bool:
    """fs_point_max <= fs_max for no-skill students on Ask and Verify in every constrained cell. strict also needs
    fs_event_ever <= fs_max (no more than 5% of no-skill students are ever shown secure, even straight after a
    moment, over the 10 weeks)."""
    for nk in ("0", "sym10", "sym20"):
        for ig in IGNORES:
            for sk in ("ask", "verify"):
                if f"{nk}|{ig}" not in metrics:
                    continue
                m = metrics[f"{nk}|{ig}"][sk]
                if m["fs_point_max"] > fs_max or (strict and m["fs_event_ever"] > fs_max):
                    return False
    return True


def objective(metrics: dict) -> tuple:
    c = metrics["sym10|mnar"]
    hold = (c["ask"]["strong_secure_w3_10"] + c["verify"]["strong_secure_w3_10"]) / 2
    days = (c["ask"]["strong_days_to_secure_median"] + c["verify"]["strong_days_to_secure_median"]) / 2
    return (round(hold, 3), -days)


def search(n: int) -> None:
    RES.mkdir(exist_ok=True)
    cfgs = list(grid_cfgs())
    with open(RES / "grid.jsonl", "w") as f, ProcessPoolExecutor(8) as ex:
        for i, row in enumerate(ex.map(_eval_job, [(c, n) for c in cfgs], chunksize=4)):
            f.write(json.dumps(row) + "\n")
            if i % 200 == 0:
                print(i, len(cfgs), flush=True)


def baseline(n: int = 1000) -> None:
    """The branch settings and one change at a time, with large N."""
    b = M.BRANCH
    variants = {
        "branch": b,
        "ignored_missing": replace(b, ignored="missing"),
        "unprompted_guess_0.20": replace(b, u_guess=0.20),
        "share_0.5_min2": replace(b, correct_share=0.5),
        "min_features_3": replace(b, ask_min_features=3),
        "half_life_14": replace(b, half_life=14.0),
        "learn_rate_0.02": replace(b, learn_rate=0.02),
        "prior_0.2": replace(b, prior=0.2),
    }
    RES.mkdir(exist_ok=True)
    with ProcessPoolExecutor(8) as ex:
        futs = {k: ex.submit(evaluate, v, n) for k, v in variants.items()}
        out = {k: {"cfg": asdict(variants[k]), "metrics": f.result()} for k, f in futs.items()}
    (RES / "baseline.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "baseline":
        baseline(int(sys.argv[2]) if len(sys.argv) > 2 else 1000)
    elif cmd == "search":
        search(int(sys.argv[2]) if len(sys.argv) > 2 else 120)
