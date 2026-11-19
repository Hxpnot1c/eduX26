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


# --- the student's page ------------------------------------------------------------------------------------------

REVIEW_WHY = {
    "scheduled": "Time to check that you still remember it.",
    "recall_below": "Your answers suggest this is slipping, so a short check helps.",
    "taught_in_class": "Your class has covered this and you have not answered on it yet.",
    "just_show_me": "You were shown this. Trying it yourself is what makes it stick.",
    "untested": "You have talked about this but not been checked on it yet.",
}
FADE_FULL_DAYS = 7  # judgement call, starting values: a part answered within this many days is drawn at full strength...
FADE_FLOOR_DAYS = 60  # ...fading to half strength by this many days, so forgetting shows without a number
FADE_FLOOR = 0.5


def _ago(days: float) -> str:
    if days < 1:
        return "today"
    n = int(days)
    return "yesterday" if n == 1 else f"{n} days ago"


def student_overlay(student_id: str, at: str) -> dict[str, dict]:
    """For every course part: the level to show (never a probability), a short note on the evidence it rests on, and how
    faded to draw it. A part with no answer reads "taught in class, not yet checked" if the class covered it, else "no
    answers yet": never developing or secure before an answer (decision 0015)."""
    stamp = learner.parse_ts(at)
    rows = learner._conn().execute(
        "SELECT part_id, COUNT(*) AS n, MAX(ts) AS last FROM evidence_log WHERE student_id = ? AND ts <= ? GROUP BY part_id",
        (student_id, learner._event_ts(at)),
    )
    seen = {r["part_id"]: (r["n"], r["last"]) for r in rows}
    overlay = {}
    for part in learner.all_parts():
        if graph.is_literacy(part):
            continue
        n, last = seen.get(part, (0, None))
        shown = learner.shown_level(student_id, part, at)
        if n == 0:
            level = "taught" if shown == "taught_in_class" else "none"
            overlay[part] = {
                "level": level,
                "note": "taught in class, not yet checked" if level == "taught" else "no answers yet",
                "fade": 1.0,
            }
            continue
        days = max(0.0, (stamp - learner.parse_ts(last)).total_seconds() / 86400)
        fade = (
            1.0
            if days <= FADE_FULL_DAYS
            else max(FADE_FLOOR, 1 - (1 - FADE_FLOOR) * (days - FADE_FULL_DAYS) / (FADE_FLOOR_DAYS - FADE_FULL_DAYS))
        )
        overlay[part] = {"level": shown, "note": f"{n} answer{'s' if n != 1 else ''}, last {_ago(days)}", "fade": round(fade, 2)}
    return overlay


def _word(level: str) -> str:
    return "taught" if level == "taught_in_class" else level


def chatbot_setup() -> dict:
    """The text the student pastes into their chatbot, and the plain account of what Synapse keeps, both read from
    text/chatbot_setup.md so the page and the set-up sheet can never disagree."""
    from edux.settings import read_text

    text = read_text("chatbot_setup.md")
    pasted = text.split("\n---\n")[1].strip() if text.count("\n---\n") >= 2 else ""
    keeps = [ln[2:].strip().replace("**", "") for ln in text.split("## What Synapse keeps", 1)[-1].splitlines() if ln.startswith("- ")]
    return {"prompt": pasted, "keeps": keeps}


def student_page(student: dict, at: str | None = None) -> dict:
    """Everything the student's page shows, from their own record only. Levels, counts and dates; no probabilities, no
    scores, no comparison with anyone else, no confidence or fatigue data other than the calibration line they already
    get in chat (shown only once there are enough rated answers)."""
    from edux import service

    at = at or learner.now_iso()
    student_id = student["id"]
    progress = service.progress_parts(student, False, at, reviews_limit=8)
    reviews = [
        {
            "part_id": r["part_id"],
            "name": r["name"],
            "due": r["due"],
            "why": REVIEW_WHY.get(r["reason"], "Due for a check."),
            "level": _word(r["level"]),
        }
        for r in progress["reviews_due"]
    ]
    stamp = learner.parse_ts(at)
    for r in reviews:
        late = (stamp - learner.parse_ts(r["due"])).total_seconds() / 86400
        r["when"] = "due now" if late < 1 else f"due {_ago(late)}"
    plan = service.plan_study(student, at=at) if learner.upcoming(student_id, at, days=60) else None
    coming = learner.upcoming(student_id, at, days=60)
    counts = (
        learner._conn()
        .execute("SELECT COUNT(*) AS answers, MIN(ts) AS first, MAX(ts) AS last FROM evidence_log WHERE student_id = ?", (student_id,))
        .fetchone()
    )
    exchanges = learner._conn().execute("SELECT COUNT(*) FROM exchange_log WHERE student_id = ?", (student_id,)).fetchone()[0]
    ai = progress["ai_literacy"]
    return {
        "course": course_for(student.get("course_id")),
        "overlay": student_overlay(student_id, at),
        "next": [{"part_id": f["part_id"], "name": f["name"], "level": _word(f["level"])} for f in progress["levers"]],
        "reviews": reviews,
        "coming_up": {
            "assessments": coming,
            "plan": None
            if not plan or not plan.get("ok")
            else {"assessment": plan["assessment"], "sessions": plan["sessions"][:6], "note": plan.get("note", "")},
        },
        "ai_literacy": {
            "note": ai["formative"],
            "skills": [
                {
                    "id": key,
                    "name": name,
                    "level": ai[key]["level"],
                    "checks": ai[key]["evidence"]["checks"],
                    "over_days": ai[key]["evidence"]["over_days"],
                }
                for key, name in (("ask", "Asking good questions"), ("verify", "Checking claims"), ("how_ai_works", "How AI works"))
            ],
        },
        "calibration": progress.get("calibration"),
        "record": {
            "answers": counts["answers"],
            "chats": exchanges,
            "first": (counts["first"] or "")[:10],
            "last": (counts["last"] or "")[:10],
        },
        "parts": [{"id": p, "name": graph.require_node(p)["name"]} for p in learner.all_parts() if not graph.is_literacy(p)],
        "setup": chatbot_setup(),
    }
