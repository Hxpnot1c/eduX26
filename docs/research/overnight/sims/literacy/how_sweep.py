"""How AI works: the rollup of four parts, each checked only when a chatbot failure triggers it.
Sweeps trigger rate, half-life, ail_how guess, prior/learn rate and the ignored rule -> results/how_sweep.md.
FastBackend; the How stream doesn't interact with the Ask/Verify settings. All truth numbers are our choice."""

from __future__ import annotations

import itertools
from dataclasses import replace
from pathlib import Path

import grid
import lit_model as M

HERE = Path(__file__).resolve().parent


def run(n: int = 400) -> None:
    L = ["# How AI works sweep", "",
         f"Rollup = mean p of the four how-AI-works parts (equal importance), read weekly. 10% symmetric noise "
         f"doesn't touch How (the letter is scored by the server); ignoring = mnar. n = {n} per group.", "",
         "| triggers/week | half-life | prior / lr | ail_how guess | ignored | strong secure w3-10 | strong ever secure | none secure (max weekly) | gamer/none-like secure | AUC none-strong w8 | AUC partial-strong w8 | strong how moments (10 wk) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for rate in (0.6, 1.0):   # P(one trigger in a week); the model has at most one trigger a week
        M.TRUTH["how_trigger_per_week"] = rate
        M.make_script.cache_clear()
        for hl, (prior, lr), hg, ign in itertools.product((2.0, 14.0, 1e6), ((0.3, 0.10), (0.2, 0.02)), (0.25, 0.40), ("zero", "missing")):
            cfg = replace(M.BRANCH, half_life=hl, prior=prior, learn_rate=lr, h_guess=hg, ignored=ign)
            m = grid.cell_metrics(cfg, M.Noise.symmetric(0.10), "mnar", n)["how"]
            hls = "none" if hl >= 1e5 else f"{hl:g}"
            L.append(f"| {rate} | {hls} | {prior} / {lr} | {hg} | {ign} | {m['strong_secure_w3_10']:.2f} | {m['strong_ever_secure']:.2f} | "
                     f"{m['fs_point_max']:.2f} | {m['gamer_point_max']:.2f} | {m['auc_none_strong_w8']:.2f} | {m['auc_partial_strong_w8']:.2f} | "
                     f"{m['strong_moments_w10_mean']:.1f} |")
    M.TRUTH["how_trigger_per_week"] = 0.6
    (HERE / "results" / "how_sweep.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    run()
