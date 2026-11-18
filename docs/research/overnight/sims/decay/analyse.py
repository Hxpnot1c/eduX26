"""Summarise results/population.jsonl into results/population.md (w3-06).

Pairs compared (same part, same snapshot):
- across students: student A has never answered the part right (censored), student B has (at least once).
- within a student: part A never answered right, part B answered right at least once.
An inversion is p_A > p_B (ties count half). It is "wrong by truth" when the truth disagrees with the model's
order (truth_A < truth_B) and "right by truth" when truth_A > truth_B. Truth = the synthetic student's recall
probability for the part at the snapshot. AUC: model p vs truth "knows it" (recall >= 0.5), pooled per part.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW, SECURE = 0.40, 0.75


def level(p):
    return "new" if p < NEW else "secure" if p >= SECURE else "developing"


def load(path):
    rows = [json.loads(l) for l in open(path)]
    return rows


def pairs_stats(items):
    """items: list of (p, truth, censored). Returns counts over (censored A, uncensored B) pairs."""
    A = [(p, t) for p, t, c in items if c]
    B = [(p, t) for p, t, c in items if not c]
    n = inv = inv_wrong = inv_right = disagree = differ = ties = 0
    for pa, ta in A:
        for pb, tb in B:
            n += 1
            x = 1.0 if pa > pb + 1e-12 else 0.5 if abs(pa - pb) <= 1e-12 else 0.0
            ties += x == 0.5
            inv += x
            if ta < tb - 1e-9:
                inv_wrong += x
                differ += 1
                disagree += x
            elif ta > tb + 1e-9:
                inv_right += x
                differ += 1
                disagree += 1 - x
    return n, inv, inv_wrong, inv_right, differ, disagree, ties


def auc_counts(items):
    pos = [p for p, t, _ in items if t >= 0.5]
    neg = [p for p, t, _ in items if t < 0.5]
    s = 0.0
    for a in pos:
        for b in neg:
            s += 1.0 if a > b + 1e-12 else 0.5 if abs(a - b) <= 1e-12 else 0.0
    return s, len(pos) * len(neg)


def main(path=HERE / "results" / "population.jsonl", out=HERE / "results" / "population.md"):
    rows = load(path)
    variants = sorted({r["variant"] for r in rows}, key=["current", "a_clock_any", "b_cap_prior", "c_to_prior", "ac", "bc"].index)
    by = defaultdict(list)
    for r in rows:
        by[(r["scen"], r["floor"], r["variant"])].append(r)
    cur_index = {(r["sid"], r["scen"], r["floor"]): r for r in rows if r["variant"] == "current"}
    lines = ["# w3-06 population simulation: decay-clock asymmetry on economics parts", "",
             f"{len(rows)} rows ({len(cur_index)} synthetic students x {len(variants)} variants). Snapshots are mornings "
             "on study days 3, 7, 14, 30, 45, 60 (near: those before the exam) plus exam morning. Every number in the "
             "student model is our choice; results describe these rules on the example-mini pack, not real students.", ""]
    det_bad = [(r["sid"], r["variant"]) for r in rows if not all(r["det"].values())]
    lines.append(f"Determinism: rebuild twice equal and equal to the live state in {len(rows) - len(det_bad)}/{len(rows)} "
                 f"student x variant runs. Failures: {det_bad[:5]}")
    lines.append("")
    # share of readings that are censored
    meta = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["variant"] != "current":
            continue
        for snap in r["reads"]:
            for p, v in snap.items():
                k = (r["scen"], r["floor"])
                meta[k][0] += 1
                meta[k][1] += v["lc_days"] is None and v["n"] == 0
                meta[k][2] += v["lc_days"] is None and v["n"] > 0
    lines.append("## Readings by state (current)")
    lines.append("")
    lines.append("| scenario | truth floor | readings | untouched | answered, never right |")
    lines.append("|---|---|---|---|---|")
    for k, (n, u, w) in sorted(meta.items()):
        lines.append(f"| {k[0]} | {k[1]} | {n} | {u / n:.1%} | {w / n:.1%} |")
    lines.append("")

    for scope in ("across", "within"):
        lines.append(f"## {'Across students (same part)' if scope == 'across' else 'Within a student (across parts)'}: "
                     "never-right A vs right-at-least-once B")
        lines.append("")
        lines.append("Inv = share of pairs where A reads above B (a tie counts half; 'of which ties' = share of pairs tied). Wrong = share of pairs inverted while truth says B "
                     "knows it better. Disagree = share of truth-ordered pairs the model orders wrongly (ties half).")
        lines.append("")
        lines.append("| scenario | floor | variant | snapshot | pairs | Inv | of which ties | Wrong | Inv right by truth | Disagree |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for (scen, floor, v), rs in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1], variants.index(kv[0][2]))):
            nsnap = max(len(r["reads"]) for r in rs)
            for si in range(nsnap):
                acc = [0] * 7
                if scope == "across":
                    groups = defaultdict(list)
                    for r in rs:
                        if si >= len(r["reads"]):
                            continue
                        idx = si if si < len(r["reads"]) - 1 or si == nsnap - 1 else si
                        for p, val in r["reads"][si].items():
                            groups[p].append((val["p"], r["truth"][si][p], val["lc_days"] is None))
                    for items in groups.values():
                        for j, x in enumerate(pairs_stats(items)):
                            acc[j] += x
                else:
                    for r in rs:
                        if si >= len(r["reads"]):
                            continue
                        items = [(val["p"], r["truth"][si][p], val["lc_days"] is None) for p, val in r["reads"][si].items()]
                        for j, x in enumerate(pairs_stats(items)):
                            acc[j] += x
                n, inv, invw, invr, differ, dis, ties = acc
                if not n:
                    continue
                label = "exam" if si == nsnap - 1 else f"d{[3, 7, 14, 30, 45, 60][si]}"
                if si != nsnap - 1 and label in ("d3",):
                    continue
                lines.append(f"| {scen} | {floor} | {v} | {label} | {n} | {inv / n:.3f} | {ties / n:.3f} | {invw / n:.3f} | "
                             f"{invr / n:.3f} | {dis / differ if differ else float('nan'):.3f} |")
        lines.append("")

    # AUC, calibration, levels
    lines.append("## Prediction against truth, and levels shown")
    lines.append("")
    lines.append("AUC: model p vs truth recall >= 0.5, pooled within part across students (all snapshots). "
                 "Brier: (p - truth recall)^2. Level changed: share of readings whose level differs from current. "
                 "Never-right shown developing+: share of never-right readings shown developing or secure. "
                 "Gate flips: readings where `level == new` (prerequisite check, known_parts, intuition source) differs "
                 "from current. False secure: p >= 0.75 and truth < 0.5.")
    lines.append("")
    lines.append("| scenario | floor | variant | AUC | AUC exam day | Brier | Brier exam day | level changed | never-right shown developing+ | gate flips | false secure |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for (scen, floor, v), rs in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1], variants.index(kv[0][2]))):
        auc_g, auc_e = defaultdict(list), defaultdict(list)
        brier = brier_e = nb = nbe = 0.0
        changed = gate = nread = nr = nr_dev = fs = 0
        for r in rs:
            cur = cur_index[(r["sid"].rsplit("-", 1)[0] if False else r["sid"], scen, floor)]
            for si, snap in enumerate(r["reads"]):
                exam = si == len(r["reads"]) - 1
                for p, val in snap.items():
                    t = r["truth"][si][p]
                    auc_g[(p, si)].append((val["p"], t, None))
                    if exam:
                        auc_e[p].append((val["p"], t, None))
                        brier_e += (val["p"] - t) ** 2
                        nbe += 1
                    brier += (val["p"] - t) ** 2
                    nb += 1
                    pc = cur["reads"][si][p]["p"]
                    nread += 1
                    changed += level(val["p"]) != level(pc)
                    gate += (level(val["p"]) == "new") != (level(pc) == "new")
                    fs += val["p"] >= SECURE and t < 0.5
                    if val["lc_days"] is None:
                        nr += 1
                        nr_dev += level(val["p"]) != "new"

        def auc(groups):
            s = n = 0.0
            for items in groups.values():
                a, b = auc_counts(items)
                s += a
                n += b
            return s / n if n else float("nan")
        lines.append(f"| {scen} | {floor} | {v} | {auc(auc_g):.3f} | {auc(auc_e):.3f} | {brier / nb:.3f} | "
                     f"{brier_e / nbe:.3f} | {changed / nread:.3f} | {nr_dev / nr if nr else 0:.3f} | {gate / nread:.3f} | "
                     f"{fs / nread:.4f} |")
    lines.append("")

    # inversions by days since B's last right answer (current, across students)
    lines.append("## Current: across-student inversions by days since B's last right answer")
    lines.append("")
    lines.append("| scenario | floor | B's days since right | pairs | Inv | Wrong |")
    lines.append("|---|---|---|---|---|---|")
    bins = [(0, 3), (3, 7), (7, 14), (14, 30), (30, 60), (60, 999)]
    for (scen, floor, v), rs in sorted(by.items()):
        if v != "current":
            continue
        acc = {b: [0, 0, 0] for b in bins}
        nsnap = max(len(r["reads"]) for r in rs)
        for si in range(nsnap):
            groups = defaultdict(list)
            for r in rs:
                if si < len(r["reads"]):
                    for p, val in r["reads"][si].items():
                        groups[p].append((val["p"], r["truth"][si][p], val["lc_days"]))
            for items in groups.values():
                A = [(p, t) for p, t, d in items if d is None]
                for pb, tb, d in items:
                    if d is None:
                        continue
                    b = next(b for b in bins if b[0] <= d < b[1])
                    for pa, ta in A:
                        x = 1.0 if pa > pb + 1e-12 else 0.5 if abs(pa - pb) <= 1e-12 else 0.0
                        acc[b][0] += 1
                        acc[b][1] += x
                        acc[b][2] += x if ta < tb - 1e-9 else 0
        for b, (n, inv, w) in acc.items():
            if n:
                lines.append(f"| {scen} | {floor} | {b[0]}–{b[1] if b[1] < 999 else '…'} | {n} | {inv / n:.3f} | {w / n:.3f} |")
    lines.append("")

    # by review compliance (current, across, all snapshots)
    lines.append("## Current: inversions by review compliance (across students, all snapshots)")
    lines.append("")
    lines.append("B is restricted to students with the given compliance; A is any never-right student.")
    lines.append("")
    lines.append("| scenario | floor | compliance of B | pairs | Inv | Wrong |")
    lines.append("|---|---|---|---|---|---|")
    for (scen, floor, v), rs in sorted(by.items()):
        if v != "current":
            continue
        for comp in (0.0, 0.5, 1.0):
            n = inv = w = 0
            nsnap = max(len(r["reads"]) for r in rs)
            for si in range(nsnap):
                groups = defaultdict(lambda: ([], []))
                for r in rs:
                    if si < len(r["reads"]):
                        for p, val in r["reads"][si].items():
                            t = r["truth"][si][p]
                            if val["lc_days"] is None:
                                groups[p][0].append((val["p"], t))
                            elif r["compliance"] == comp:
                                groups[p][1].append((val["p"], t))
                for A, B in groups.values():
                    for pa, ta in A:
                        for pb, tb in B:
                            x = 1.0 if pa > pb + 1e-12 else 0.5 if abs(pa - pb) <= 1e-12 else 0.0
                            n += 1
                            inv += x
                            w += x if ta < tb - 1e-9 else 0
            if n:
                lines.append(f"| {scen} | {floor} | {comp} | {n} | {inv / n:.3f} | {w / n:.3f} |")
    lines.append("")
    Path(out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(*(sys.argv[1:]))
