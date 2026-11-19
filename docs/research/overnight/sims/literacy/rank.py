"""Apply the selection rule (see grid.py) to results/grid.jsonl and write results/ranked.md."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import grid

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
KEYS = ("prior", "learn_rate", "half_life", "ignored", "correct_share", "q_guess", "q_slip", "verify_share", "t_guess", "u_guess")


def short(cfg: dict) -> str:
    hl = "none" if cfg["half_life"] >= 1e5 else f"{cfg['half_life']:g}"
    return (f"prior {cfg['prior']}, lr {cfg['learn_rate']}, hl {hl}, ignored {cfg['ignored']}, ask_share {cfg['correct_share']}"
            f" (min_feat {cfg['ask_min_features']}), q {cfg['q_slip']}/{cfg['q_guess']}, verify_share {cfg['verify_share']},"
            f" t {cfg['t_slip']}/{cfg['t_guess']}, u_guess {cfg['u_guess']}")


def row_stats(m: dict) -> dict:
    c = m["sym10|mnar"]
    worst_fs = max(m[k][sk]["fs_point_max"] for k in m for sk in ("ask", "verify"))
    worst_ev = max(m[k][sk]["fs_event_ever"] for k in m for sk in ("ask", "verify"))
    return {
        "hold": (c["ask"]["strong_secure_w3_10"] + c["verify"]["strong_secure_w3_10"]) / 2,
        "ask_hold": c["ask"]["strong_secure_w3_10"], "ver_hold": c["verify"]["strong_secure_w3_10"],
        "ask_days": c["ask"]["strong_days_to_secure_median"], "ver_days": c["verify"]["strong_days_to_secure_median"],
        "ask_mom": c["ask"]["strong_moments_to_secure_median"], "ver_mom": c["verify"]["strong_moments_to_secure_median"],
        "worst_fs": worst_fs, "worst_ev": worst_ev,
        "partial": (c["ask"]["partial_secure_w3_10"] + c["verify"]["partial_secure_w3_10"]) / 2,
        "gamer_ver": c["verify"]["gamer_secure_w3_10"],
        "auc_ps": (c["ask"]["auc_partial_strong_w8"] + c["verify"]["auc_partial_strong_w8"]) / 2,
        "imp": (c["ask"]["improver_secure_w6"] + c["verify"]["improver_secure_w6"]) / 2,
        "s20_hold": (m["sym20|mnar"]["ask"]["strong_secure_w3_10"] + m["sym20|mnar"]["verify"]["strong_secure_w3_10"]) / 2,
    }


def fmt_days(x: float) -> str:
    return "never" if x == float("inf") else f"{x:.1f}"


def table(rows: list, n: int) -> list[str]:
    out = ["| # | settings | strong hold (A/V) | days to secure (A/V) | moments (A/V) | worst FS point / ever | partial secure | gamer V | AUC p-s | improver w6 | hold @20% |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (cfg, st) in enumerate(rows[:n], 1):
        out.append(f"| {i} | {short(cfg)} | {st['hold']:.2f} ({st['ask_hold']:.2f}/{st['ver_hold']:.2f}) | "
                   f"{fmt_days(st['ask_days'])}/{fmt_days(st['ver_days'])} | {st['ask_mom']}/{st['ver_mom']} | "
                   f"{st['worst_fs']:.2f} / {st['worst_ev']:.2f} | {st['partial']:.2f} | {st['gamer_ver']:.2f} | "
                   f"{st['auc_ps']:.2f} | {st['imp']:.2f} | {st['s20_hold']:.2f} |")
    return out


def main() -> None:
    rows = [json.loads(l) for l in open(RES / "grid.jsonl")]
    allr = [(r["cfg"], row_stats(r["metrics"]), r["metrics"]) for r in rows]
    branch_like = [x for x in allr if x[0]["prior"] == 0.3 and x[0]["learn_rate"] == 0.1 and x[0]["half_life"] == 2.0
                   and x[0]["ignored"] == "zero" and x[0]["correct_share"] == 0.67 and x[0]["q_guess"] == 0.2
                   and x[0]["verify_share"] == 0.67 and x[0]["t_guess"] == 0.15 and x[0]["u_guess"] == 0.1]
    passing = [x for x in allr if grid.passes(x[2])]
    strict = [x for x in allr if grid.passes(x[2], strict=True)]
    key = lambda x: (round(x[1]["hold"], 3), -(x[1]["ask_days"] + x[1]["ver_days"]))
    passing.sort(key=key, reverse=True)
    strict.sort(key=key, reverse=True)
    # balanced rule (added after the first look showed that "hold" alone rewards lax thresholds that also make
    # partial and gamer students secure): strict constraint + gamer Verify secure (w3-10) <= 10%; objective =
    # strong hold minus partial secure, at 10% noise, mnar.
    balanced = [x for x in strict if x[1]["gamer_ver"] <= 0.10]
    balanced.sort(key=lambda x: (round(x[1]["hold"] - x[1]["partial"], 3), -(x[1]["ask_days"] + x[1]["ver_days"])), reverse=True)
    L = ["# Settings grid: ranked", "",
         f"{len(allr)} settings combinations, 100 synthetic students per group per cell, cells = label noise "
         "{10%, 20% symmetric} x ignoring {mcar, mnar}. Constraint and objective: see grid.py. "
         "Hold = mean share of strong students shown secure at weekly reads, weeks 3-10, at 10% noise, mnar. "
         "A = Ask, V = Verify. FS = no-skill students shown secure (point: worst weekly read; ever: ever, incl. "
         "straight after a moment). All synthetic; every truth-model number is our choice.", "",
         f"- passing the constraint (FS point <= 5%): {len(passing)}", f"- passing the strict constraint (FS ever <= 5% too): {len(strict)}", ""]
    L += ["## Branch values but ask_min_features 3 (the grid ties min_features to the threshold; not the real branch: see final.md)", ""] + table([(c, s) for c, s, _ in branch_like], 1) + [""]
    L += [f"## Top 15, balanced rule ({len(balanced)} pass): strict + gamer Verify <= 10%, ranked by strong hold - partial secure", ""] + table([(c, s) for c, s, _ in balanced], 15) + [""]
    L += ["## Top 15, strict constraint", ""] + table([(c, s) for c, s, _ in strict], 15) + [""]
    L += ["## Top 10, point constraint only", ""] + table([(c, s) for c, s, _ in passing], 10) + [""]
    # marginals: best hold among strict-passing configs for each value of each key
    L += ["## Marginals (strict-passing configs): best and median hold by each setting value", "",
          "| setting | value | n passing | best hold | median hold | median worst FS ever |", "|---|---|---|---|---|---|"]
    for k in ("prior", "learn_rate", "half_life", "ignored", "correct_share", "q_guess", "verify_share", "t_guess", "u_guess"):
        groups = defaultdict(list)
        for c, s, _ in strict:
            groups[c[k]].append(s)
        tot = defaultdict(int)
        for c, s, _ in allr:
            tot[c[k]] += 1
        for v in sorted(tot):
            g = groups.get(v, [])
            if g:
                holds = sorted(x["hold"] for x in g)
                evs = sorted(x["worst_ev"] for x in g)
                L.append(f"| {k} | {v:g} | {len(g)}/{tot[v]} | {holds[-1]:.2f} | {holds[len(holds)//2]:.2f} | {evs[len(evs)//2]:.2f} |"
                         if not isinstance(v, str) else
                         f"| {k} | {v} | {len(g)}/{tot[v]} | {holds[-1]:.2f} | {holds[len(holds)//2]:.2f} | {evs[len(evs)//2]:.2f} |")
            else:
                L.append(f"| {k} | {v} | 0/{tot[v]} | - | - | - |")
    # decay: across ALL configs, how half-life moves strong hold and no-skill FS (others fixed at the best strict config)
    if strict:
        best = (balanced or strict)[0][0]
        L += ["", "## Half-life sweep around the best strict config (other settings fixed)", "",
              "| half-life | strong hold A/V | worst FS point / ever | partial secure | improver w6 | days to secure A/V |", "|---|---|---|---|---|---|"]
        for c, s, _ in sorted(allr, key=lambda x: x[0]["half_life"]):
            if all(c[k] == best[k] for k in KEYS if k != "half_life"):
                hl = "none" if c["half_life"] >= 1e5 else f"{c['half_life']:g}"
                L.append(f"| {hl} | {s['ask_hold']:.2f}/{s['ver_hold']:.2f} | {s['worst_fs']:.2f} / {s['worst_ev']:.2f} | "
                         f"{s['partial']:.2f} | {s['imp']:.2f} | {fmt_days(s['ask_days'])}/{fmt_days(s['ver_days'])} |")
        L += ["", "## Ignored = zero vs missing around the best strict config", "",
              "| ignored | strong hold A/V | worst FS point / ever | partial secure | AUC partial-strong |", "|---|---|---|---|---|"]
        for c, s, _ in allr:
            if all(c[k] == best[k] for k in KEYS if k != "ignored"):
                L.append(f"| {c['ignored']} | {s['ask_hold']:.2f}/{s['ver_hold']:.2f} | {s['worst_fs']:.2f} / {s['worst_ev']:.2f} | "
                         f"{s['partial']:.2f} | {s['auc_ps']:.2f} |")
    (RES / "ranked.md").write_text("\n".join(L) + "\n")
    json.dump({"best_balanced": balanced[0][0] if balanced else None, "top_balanced": [c for c, _, _ in balanced[:10]],
               "best_strict": strict[0][0] if strict else None, "best_point": passing[0][0] if passing else None,
               "top_strict": [c for c, _, _ in strict[:10]]}, open(RES / "best.json", "w"), indent=1)
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
