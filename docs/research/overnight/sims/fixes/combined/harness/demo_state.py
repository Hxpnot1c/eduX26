import json, sys
from edux import learner, service
for sid in ("demo-secure", "demo-weak", "demo-showme"):
    st = learner.get_student(sid)
    pr = service.my_progress(st, include_parts=True)
    def flat(nodes, out):
        for n in nodes:
            out.append(f"{n['id']}={n['level']}")
            flat(n.get("children") or [], out)
        return out
    print(sid, " ".join(flat(pr["tree"], [])))
    print("   ai_literacy", {k: v for k, v in pr["ai_literacy"].items() if k != "question_features"}, "reviews_due", [r.get("part_id") for r in pr.get("reviews_due") or []], "weak_links", len(pr.get("weak_links") or []))
