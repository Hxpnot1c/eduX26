"""Compare demo-05e scenario captures across the four copies (base, svc, gate, both) of w4-fix-focus.
    python focus_episodes.py [captures dir]   -> prints, per scenario, each turn's moves (part) and saved focus,
    and flags turns that differ from base and course-part steps after a literacy turn."""
import json, sys
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "captures-focus")
LABELS = ["base", "svc", "gate", "both", "all3"]
COURSE_PREFIX = ("ped", "pes", "yed", "tax", "externality", "elasticities", "indirect")


def summary(path):
    d = json.loads(path.read_text())
    out = []
    for t in d["turns"]:
        if t.get("tool") == "get_my_progress":
            continue
        res = t.get("result") or {}
        moves = [f"{st['move']}:{st.get('part_id') or ''}".rstrip(":") for st in res.get("plan", [])]
        focus = [f["id"] for f in res.get("focus", [])]
        src = sorted({s["name"] for st in res.get("plan", []) for s in (st.get("data") or {}).get("trusted_sources", [])})
        out.append((t.get("shot"), moves, focus, src))
    return out


scen = sorted({p.name.split("__", 1)[1][:-5] for p in D.glob("w4ff-base__*.json")})
course_after = {L: 0 for L in LABELS}
for s in scen:
    rows = {L: summary(D / f"w4ff-{L}__{s}.json") for L in LABELS if (D / f"w4ff-{L}__{s}.json").exists()}
    print(f"\n## {s}")
    for L, turns in rows.items():
        diff = "" if L == "base" or turns == rows["base"] else "  <-- differs"
        n_course = sum(any(m.split(":")[-1].startswith(COURSE_PREFIX) and m.startswith(("ask_mcq", "teach", "answer_brief", "reask"))
                           for m in mv) for shot, mv, f, src in turns if shot not in ("5",))
        if not s.startswith("ped_first"):   # the PED-first scenarios resume the course by design (reported apart)
            course_after[L] += n_course
        print(f"  {L:5s}{diff}  course-question turns in the literacy episode: {n_course}")
        for shot, mv, f, src in turns:
            print(f"      {str(shot):4s} {mv} focus={f} sources={src}")
print("\ncourse-question turns inside literacy episodes (the 28 demo-05e scenarios; excluding shot 5 = the PED question and the ped_first* extras):", course_after)
