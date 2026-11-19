"""Per-moment share scored correct (score >= threshold) by group and noise, under the proposal routing.
Lets the per-label noise model be compared with wave-1's outcome-flip model -> results/moment_rates.md"""
import json
from dataclasses import replace
from pathlib import Path
import grid, lit_model as M

HERE = Path(__file__).resolve().parent
cfg = replace(M.BRANCH, **json.loads((HERE / "results" / "chosen.json").read_text()))
L = ["# Share of moments scored correct (proposal settings, mnar, n = 500 per group)", "",
     "| noise | group | Ask (>= 3 of 4 features) | Verify task (>= 3 of 4 ticks) | unprompted (>= 3 of 4) | how-AI-works letter | Ask moments | Verify task moments | unprompted moments |",
     "|---|---|---|---|---|---|---|---|---|"]
for nk in ("0", "sym10", "sym20", "len20"):
    for g in ("none", "gamer", "partial", "strong"):
        sc = {"ask": [], "verify": [], "unprompted": [], "how": []}
        for k in range(500):
            r = M.run_student(M.FastBackend(cfg), cfg, g, k, grid.NOISES[nk], "mnar")
            for key in sc:
                sc[key] += r["scores"][key]
        f = lambda xs, t=0.67: f"{sum(x >= t for x in xs) / len(xs):.3f}" if xs else "-"
        L.append(f"| {nk} | {g} | {f(sc['ask'])} | {f(sc['verify'])} | {f(sc['unprompted'])} | {f(sc['how'], 1.0)} | "
                 f"{len(sc['ask'])/500:.1f} | {len(sc['verify'])/500:.1f} | {len(sc['unprompted'])/500:.1f} |")
(HERE / "results" / "moment_rates.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
