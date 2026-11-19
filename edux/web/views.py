"""What the web pages read: plain dictionaries built from the graph and the learner model, one function per view.

Every view is a pure function of the databases and returns JSON-ready data. The rules the pages keep (decision 0024) are
kept here, in one place, so a page cannot bypass them: levels never carry a probability, a class cell under the minimum
size is withheld, and nothing a teacher can reach holds a student's id, name or key."""

from __future__ import annotations

from datetime import timedelta

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


# --- the teacher's class view ------------------------------------------------------------------------------------
# Class level only (decision 0024). Nothing here names a student, and nothing is shown for fewer than the minimum
# number of students (coverage.class_min_students, 5): a cell with fewer answers than that is withheld, a class smaller
# than that shows nothing but its coverage and assessments, and a part is shown as a band, never as a count at each
# level, so that no small group can be picked out by subtraction.

THIN = 8  # judgement call, starting value: a cell resting on fewer students than this is drawn lighter and called thin
BAND_LOW, BAND_HIGH = 1 / 3, 2 / 3  # judgement call: the share at developing or secure that makes a part "few", "mixed" or "most"
BAND_WORDS = {
    "few": "few at developing yet",
    "mixed": "about half at developing or secure",
    "most": "most at developing or secure",
}
BAND_LEVEL = {"few": "new", "mixed": "developing", "most": "secure"}  # the level colour each band borrows, so colour keeps one meaning


def class_members(class_id: str) -> list[str]:
    return [r["id"] for r in learner._conn().execute("SELECT id FROM student WHERE class_id = ? ORDER BY id", (class_id,))]


def _class_overlay(members: list[str], at: str, minimum: int) -> dict[str, dict]:
    overlay = {}
    conn = learner._conn()
    marks = ",".join("?" * len(members))
    answered: dict[str, dict[str, str]] = {}
    for r in conn.execute(
        f"SELECT part_id, student_id, MAX(ts) AS last FROM evidence_log WHERE student_id IN ({marks}) AND ts <= ? GROUP BY part_id, student_id",
        (*members, learner._event_ts(at)),
    ):
        answered.setdefault(r["part_id"], {})[r["student_id"]] = r["last"]
    for part in learner.all_parts():
        if graph.is_literacy(part):
            continue
        who = answered.get(part, {})
        if len(who) < minimum:
            overlay[part] = {
                "level": "none",
                "label": "not enough answers to show",
                "note": f"Fewer than {minimum} students have answered.",
                "fade": 1.0,
            }
            continue
        practised = sum(learner.shown_level(sid, part, at) in ("developing", "secure") for sid in who)
        share = practised / len(who)
        band = "few" if share < BAND_LOW else "mixed" if share <= BAND_HIGH else "most"
        last = max(who.values())[:10]
        thin = len(who) < THIN
        overlay[part] = {
            "level": BAND_LEVEL[band],
            "band": band,
            "label": BAND_WORDS[band],
            "note": f"{len(who)} students have answered. Latest answer {last}." + (" Thin: this rests on few students." if thin else ""),
            "fade": 0.6 if thin else 1.0,
        }
    return overlay


def _held_wrong_ideas(members: list[str], minimum: int) -> list[dict]:
    marks = ",".join("?" * len(members))
    rows = learner._conn().execute(
        f"SELECT misconception_id, COUNT(*) AS n FROM student_misconception WHERE active = 1 AND student_id IN ({marks}) "
        "GROUP BY misconception_id HAVING COUNT(*) >= ? ORDER BY n DESC, misconception_id",
        (*members, minimum),
    )
    out = []
    for r in rows:
        m = graph.get_misconception(r["misconception_id"])
        if m is None:
            continue
        node = graph.get_node(m["node_id"]) or {}
        out.append(
            {
                "id": m["id"],
                "wrong_idea": m["wrong_idea"],
                "correction": m["correction"],
                "part": node.get("name", ""),
                "part_id": m["node_id"],
                "students": r["n"],
            }
        )
    return out


def _help_seeking(members: list[str], at: str, minimum: int) -> dict | None:
    """The class's share of messages where a student asked to be shown the answer, over the recent trend window against
    before it. Withheld unless at least `minimum` students wrote in each window."""
    from edux import service

    s = learner._settings().progress
    cut = learner._event_ts(learner.parse_ts(at) - timedelta(days=s.trend_days))
    marks = ",".join("?" * len(members))
    rows = (
        learner._conn()
        .execute(
            f"SELECT student_id, ts, choice_taken FROM exchange_log WHERE student_id IN ({marks}) AND ts <= ?",
            (*members, learner._event_ts(at)),
        )
        .fetchall()
    )
    windows = {"recent": [r for r in rows if r["ts"] > cut], "before": [r for r in rows if r["ts"] <= cut]}
    if any(len({r["student_id"] for r in w}) < minimum for w in windows.values()):
        return None
    share = {k: sum(r["choice_taken"] == "just_show_me" for r in w) / len(w) for k, w in windows.items()}
    trend = service._trend(share["recent"], share["before"])
    return {"recent": round(share["recent"], 2), "before": round(share["before"], 2), "direction": trend["direction"], "days": s.trend_days}


def _class_assessments(class_id: str, at: str) -> list[dict]:
    today = learner.parse_ts(at).date().isoformat()
    rows = learner._conn().execute(
        "SELECT DISTINCT name, kind, date FROM student_assessment WHERE class_id = ? AND date >= ? ORDER BY date, name", (class_id, today)
    )
    return [dict(r) for r in rows]


def _coverage(class_id: str) -> dict:
    taught = learner.class_coverage(class_id)
    done: set[str] = set()
    for row in taught:
        done |= set(graph.parts_of(row["node_id"]))
    left = [
        {"id": c["id"], "name": c["name"], "spec_ref": c.get("spec_ref") or ""}
        for t in graph.topics()
        for c in graph.children(t["id"])
        if c["level"] == "concept" and not (set(graph.parts_of(c["id"])) & done)
    ]
    return {"taught": [{k: r[k] for k in ("name", "spec_ref", "taught_on", "parts")} for r in taught], "not_yet": left if taught else []}


def class_summary(class_id: str, at: str | None = None) -> dict | None:
    """The class view: coverage, assessments, a band per part, wrong ideas held by at least the minimum number of
    students, and the help-seeking pattern. None if the class does not exist."""
    at = at or learner.now_iso()
    row = learner._conn().execute("SELECT id, name FROM class WHERE id = ?", (class_id,)).fetchone()
    if row is None:
        return None
    members = class_members(class_id)
    minimum = learner._settings().coverage.class_min_students
    summary = {
        "class": {"id": row["id"], "name": row["name"], "size": len(members)},
        "min_cell": minimum,
        "coverage": _coverage(class_id),
        "assessments": _class_assessments(class_id, at),
        "seeded": any(m.startswith("demo-") for m in members),
    }
    if len(members) < minimum:
        return summary | {"enough": False, "overlay": {}, "wrong_ideas": [], "help_seeking": None}
    return summary | {
        "enough": True,
        "overlay": _class_overlay(members, at, minimum),
        "wrong_ideas": _held_wrong_ideas(members, minimum),
        "help_seeking": _help_seeking(members, at, minimum),
    }
