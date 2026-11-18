"""Branch vs quick fixes vs the proposal, every noise x ignore cell (including the lenient stress test), N=1000
per group per cell -> results/final.md and results/final.json. The proposal is read from results/chosen.json."""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path

import grid
import lit_model as M

HERE = Path(__file__).resolve().parent
RES = HERE / "results"


def variants() -> dict:
    chosen = json.loads((RES / "chosen.json").read_text())
    b = M.BRANCH
    return {
        "branch": b,
        "wave1_quick_fixes": replace(b, ask_min_features=3, u_guess=0.20, ignored="missing"),
        # settable on the branch with no code change: only ail_* slip/guess and literacy.ask_min_features
        "settable_now": replace(b, ask_min_features=3, q_guess=0.30, t_guess=0.35, u_guess=0.20),
        "settable_now_keep_task": replace(b, ask_min_features=3, q_guess=0.30, u_guess=0.20),
        "proposal": replace(b, **chosen),
    }


def fmt(x):
    return "never" if x == float("inf") else (f"{x:.2f}" if isinstance(x, float) else str(x))


def main(n: int) -> None:
    vs = variants()
    with ProcessPoolExecutor(8) as ex:
        futs = {(k, nk, ig): ex.submit(grid.cell_metrics, v, nv, ig, n)
                for k, v in vs.items() for nk, nv in grid.NOISES.items() for ig in grid.IGNORES}
        res = {key: f.result() for key, f in futs.items()}
    out = {f"{k}|{nk}|{ig}": m for (k, nk, ig), m in res.items()}
    (RES / "final.json").write_text(json.dumps({"variants": {k: asdict(v) for k, v in vs.items()}, "metrics": out}, indent=1))
    cols = [("fs_point_max", "none secure, worst weekly read"), ("fs_event_ever", "none ever secure (incl. in-chat)"),
            ("gamer_secure_w3_10", "gamer secure w3-10"), ("partial_secure_w3_10", "partial secure w3-10"),
            ("strong_secure_w3_10", "strong secure w3-10"), ("strong_days_to_secure_median", "strong median days to secure"),
            ("strong_moments_to_secure_median", "strong median moments to secure"), ("strong_secure_by_w4", "strong secure by day 28"),
            ("improver_secure_w6", "improver secure w6"), ("auc_none_strong_w8", "AUC none-strong w8"),
            ("auc_partial_strong_w8", "AUC partial-strong w8"), ("auc_gamer_strong_w8", "AUC gamer-strong w8")]
    L = ["# Branch vs proposal (final check)", "", f"N = {n} synthetic students per group per cell. FastBackend (equal to the real "
         "05e learner code: see validate.json). Every truth-model number is our choice.", ""]
    for k, v in vs.items():
        L.append(f"- **{k}**: " + ", ".join(f"{f}={getattr(v, f)}" for f in ("prior", "learn_rate", "correct_share", "verify_share",
                 "ask_min_features", "half_life", "q_slip", "q_guess", "t_slip", "t_guess", "u_slip", "u_guess", "h_guess", "ignored")))
    for sk in ("ask", "verify", "how"):
        L += ["", f"## {sk}", "", "| metric | " + " | ".join(f"{k} {nk} {ig}" for k in vs for nk in ("0", "sym10", "sym20", "len20") for ig in ("mnar",)) + " |",
              "|---|" + "---|" * (len(vs) * 4)]
        for key, label in cols:
            L.append(f"| {label} | " + " | ".join(fmt(out[f"{k}|{nk}|mnar"][sk][key]) for k in vs for nk in ("0", "sym10", "sym20", "len20")) + " |")
        L += ["", f"mcar ignoring, {sk}: none secure worst weekly / strong secure w3-10", "",
              "| variant | " + " | ".join(grid.NOISES) + " |", "|---|" + "---|" * len(grid.NOISES)]
        for k in vs:
            L.append(f"| {k} | " + " | ".join(f"{out[f'{k}|{nk}|mcar'][sk]['fs_point_max']:.3f} / {out[f'{k}|{nk}|mcar'][sk]['strong_secure_w3_10']:.2f}"
                                             for nk in grid.NOISES) + " |")
    (RES / "final.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
