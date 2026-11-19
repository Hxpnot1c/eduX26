"""Before/after table for the w4-fix-verify scenarios.
    python verify_digest.py <captures dir> <label_before> <label_after>"""
import json
import sys
from pathlib import Path

cap, before, after = Path(sys.argv[1]), sys.argv[2], sys.argv[3]


def summary(path: Path) -> dict:
    d = json.loads(path.read_text())
    turns = [t for t in d["turns"] if t.get("tool") == "tutor_turn"]
    ev = [(t["n"], e["part_id"], e["evidence_type"], round(e["score"], 2)) for t in turns for e in t["evidence"]
          if e["part_id"] == "ail_verify" or e["evidence_type"] in ("ail_task", "ail_how")]
    v0 = turns[0]["before"]["p"]["ail_verify"]
    v1 = turns[-1]["after"]["p"]["ail_verify"]
    prog = next((t for t in d["turns"] if t.get("tool") == "get_my_progress"), None)
    lit = (prog or {}).get("result", {}).get("ai_literacy", {}) if prog else {}
    return {"verify": f"{v0:.3f}->{v1:.3f} ({turns[-1]['after']['levels']['ail_verify']})", "ev": ev,
            "progress": {k: v for k, v in lit.items() if k in ("ask", "verify", "how_ai_works")}}


for path in sorted(cap.glob(f"{before}__*.json")):
    name = path.name.split("__", 1)[1][:-5]
    other = cap / f"{after}__{name}.json"
    b = summary(path)
    print(f"## {name}")
    print(f"  {before:6} Verify {b['verify']}; evidence {b['ev']}")
    if other.exists():
        a = summary(other)
        print(f"  {after:6} Verify {a['verify']}; evidence {a['ev']}")
        print(f"         progress after: {json.dumps(a['progress'])}")
