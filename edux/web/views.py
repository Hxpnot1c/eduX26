"""What the web pages read: plain dictionaries built from the graph and the learner model, one function per view.

Every view is a pure function of the databases and returns JSON-ready data. The rules the pages keep (decision 0024) are
kept here, in one place, so a page cannot bypass them: levels never carry a probability, a class cell under the minimum
size is withheld, and nothing a teacher can reach holds a student's id, name or key."""

from __future__ import annotations

from edux import graph, learner

EXAMPLE_COURSE_ID = "example-mini"  # the synthetic pack that may be shown without a key (web.public_example_map)
EDGE_TYPES = ("prerequisite", "analogous", "confusable", "causal")


def courses() -> list[dict]:
    """Every loaded course: {id, name, exam_board}."""
    rows = learner._conn().execute("SELECT id, name, exam_board FROM content.course ORDER BY id")
    return [dict(r) for r in rows]


def course_for(course_id: str | None) -> dict | None:
    """The named course, or the only loaded course if none is named and there is exactly one."""
    found = courses()
    if course_id:
        return next((c for c in found if c["id"] == course_id), None)
    return found[0] if len(found) == 1 else None


def course_map(course_id: str | None = None) -> dict | None:
    """The structure of a course for the map: topics, concepts and parts as a flat node list (each with its parent), and
    the links between them. Structure only: no student data. AI-literacy parts are left out, as in the chatbot's view.
    None if the course is unknown or ambiguous."""
    course = course_for(course_id)
    if course is None:
        return None
    nodes: list[dict] = []
    ids: set[str] = set()
    top_weight = max((graph.weight(p)["importance"] for t in graph.topics() for p in graph.parts_of(t["id"])), default=0.0) or 1.0
    for topic in graph.topics():
        nodes.append({"id": topic["id"], "parent": None, "level": "topic", "name": topic["name"], "spec_ref": topic.get("spec_ref") or ""})
        ids.add(topic["id"])
        for concept in graph.children(topic["id"]):
            nodes.append(
                {
                    "id": concept["id"],
                    "parent": topic["id"],
                    "level": "concept",
                    "name": concept["name"],
                    "spec_ref": concept.get("spec_ref") or "",
                }
            )
            ids.add(concept["id"])
            for part in graph.children(concept["id"]):
                importance = graph.weight(part["id"])["importance"]
                nodes.append(
                    {
                        "id": part["id"],
                        "parent": concept["id"],
                        "level": "part",
                        "name": part["name"],
                        "spec_ref": part.get("spec_ref") or "",
                        "part_type": part.get("part_type") or "",
                        "description": part.get("description") or "",
                        "importance": round(importance / top_weight, 3),
                        "mark_points": len(graph.score_points(part["id"])),
                        "misconceptions": len(graph.misconceptions_for([part["id"]])),
                    }
                )
                ids.add(part["id"])
    edges = [
        {"from": e["from_id"], "to": e["to_id"], "type": kind, "note": e["note"], "weight": e.get("weight")}
        for kind in EDGE_TYPES
        for e in graph.links(kind)
        if e["from_id"] in ids and e["to_id"] in ids
    ]
    return {"course": {"id": course["id"], "name": course["name"], "exam_board": course["exam_board"]}, "nodes": nodes, "edges": edges}
