"""digest_q.py <cap dir> <label>...: per scenario, moves/evidence per turn, then final AI-literacy levels and progress."""
import json, sys, glob, os
cap, labels = sys.argv[1], sys.argv[2:]
names = sorted({os.path.basename(p).split("__")[1][:-5] for p in glob.glob(f"{cap}/*__*.json")})
for n in names:
    for L in labels:
        p = f"{cap}/{L}__{n}.json"
        if not os.path.exists(p): continue
        d = json.load(open(p))
        parts = []
        for t in d["turns"]:
            mv = ",".join(t["moves"]) if t["moves"] is not None else t["tool"]
            ev = ";".join(f"{e['part_id']}:{e['evidence_type']}:{e['score']}" for e in (t.get("evidence") or []))
            parts.append(f"{t['n']}:{mv}" + (f" [{ev}]" if ev else ""))
        last = [t for t in d["turns"] if t.get("after")][-1]["after"]
        lv = {k.replace('ail_',''): f"{v}" for k, v in last["levels"].items()}
        prog = d["turns"][-1]["result"].get("ai_literacy") if isinstance(d["turns"][-1]["result"], dict) else None
        print(f"{L:4} {n}: " + " | ".join(parts))
        print(f"     p={last['p']} levels={lv} held={last['held_ail']}")
        if prog: print(f"     progress.ai_literacy={ {k: v for k, v in prog.items() if k != 'question_features'} }")
