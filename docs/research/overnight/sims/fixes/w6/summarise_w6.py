"""Summarise run_w6.sh results: one row per (label, strategy, labeller).

    python summarise_w6.py <res dir> <label> [label ...]  > table.md   (also writes <res dir>/summary_w6.json)
Columns: n; effort (min); course parts secure at the end / at +7 days (mean of 9); minutes of effort to the first
secure part (mean over students who reach one); share of students with Verify secure / Verify developing or better;
mean p(Verify) at the end; Ask secure share.
"""
import json
import statistics
import sys
from pathlib import Path


def first_secure(traj, key):
    for row in traj:
        if key(row):
            return row["effort_min"]
    return None


def row(run):
    st = run["students"]
    m = lambda xs: statistics.mean(xs) if xs else None  # noqa: E731
    fs = [first_secure(s["traj"], lambda r: r["course_secure"] > 0) for s in st]
    fv = [first_secure(s["traj"], lambda r: r["lit"]["verify"] == "secure") for s in st]
    return {
        "n": len(st), "effort": m([s["effort_min"] for s in st]),
        "secure": m([s["end"]["course_secure"] for s in st]), "secure7": m([s["later"]["+7d"]["course_secure"] for s in st]),
        "min_first_secure": m([x for x in fs if x is not None]),
        "v_secure": m([s["end"]["lit"]["verify"] == "secure" for s in st]),
        "v_dev": m([s["end"]["lit"]["verify"] != "new" for s in st]),
        "p_verify": m([s["end"]["p_verify"] for s in st]),
        "min_v_secure": m([x for x in fv if x is not None]),
        "a_secure": m([s["end"]["lit"]["ask"] == "secure" for s in st]),
    }


def f(x, d=1):
    return "–" if x is None else f"{x:.{d}f}"


def main():
    res = Path(sys.argv[1])
    out = {}
    print("| tree | strategy | lab | n | effort | parts secure | +7d | min to 1st secure | Verify secure | Verify ≥dev | p(V) | min to V secure | Ask secure |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for label in sys.argv[2:]:
        for p in sorted((res / label).glob("*.json")):
            d = json.loads(p.read_text())
            for s, run in d["runs"].items():
                r = row(run)
                out[f"{label}/{s}-{d['labeller']}"] = r
                print(f"| {label} | {s} | {d['labeller'][:4]} | {r['n']} | {f(r['effort'])} | {f(r['secure'])} | {f(r['secure7'])} | "
                      f"{f(r['min_first_secure'])} | {f(100 * r['v_secure'], 0)}% | {f(100 * r['v_dev'], 0)}% | {f(r['p_verify'], 3)} | "
                      f"{f(r['min_v_secure'])} | {f(100 * r['a_secure'], 0)}% |")
    (res / "summary_w6.json").write_text(json.dumps(out, indent=1))


main()
