"""What each tool does. server.py adapts arguments; the logic lives here."""

from __future__ import annotations

import functools
import statistics
from datetime import date, timedelta

from edux import context_blocks, graph, learner
from edux.settings import ContextConfig, Settings, load_context, load_settings, read_text


@functools.cache
def _settings() -> Settings:
    return load_settings()


@functools.cache
def _context() -> ContextConfig:
    return load_context()


def resolve_student(key: str | None) -> dict | None:
    """Look up the student for a connector key."""
    return learner.student_by_key(key) if key else None


def learning_context(student: dict, message: str, node_ids: list[str] | None = None, client: str | None = None,
                     at: str | None = None) -> dict:
    """Resolve the focus parts and assemble the student's context blocks for this turn."""
    at = at or learner.now_iso()
    resolution = graph.resolve(message or "", node_ids or None)
    parts = context_blocks.order_parts(student, resolution["parts"], message or "")
    turn = context_blocks.Turn(student=student, parts=parts, message=message or "", at=at,
                               limits=_context().limits, resolution=resolution)
    profile = learner.profile_of(student)
    return {"profile": profile, "blocks": context_blocks.assemble(profile, turn, _settings(), _context())}


def log_exchange(
    student: dict,
    node_ids: list[str],
    question_depth: str,
    engagement: str,
    offloading: bool,
    support_given: str | None = None,
    choice_taken: str | None = None,
    misconception_ids: list[str] | None = None,
    conflict_flagged: bool = False,
    prompt_text: str | None = None,
    evidence: list[dict] | None = None,
    client: str | None = None,
) -> dict:
    """Record the exchange (and any evidence) and return {"ok": True} at once; the update is applied in the
    background. A label or evidence item that doesn't fit returns {"ok": False, "error": ...} and records nothing."""
    try:
        learner.record_exchange(student["id"], node_ids, question_depth, engagement, offloading, support_given,
                                choice_taken, misconception_ids, conflict_flagged, prompt_text, client,
                                evidence=evidence, apply="background")
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True}


# --- progress ------------------------------------------------------------------


def _node_entry(student_id: str, node: dict, at: str) -> dict:
    p = learner.rollup(student_id, node["id"], at)
    return {"id": node["id"], "name": node["name"], "level": learner.level(p), "p": round(p, 2)}


def _tree(student_id: str, at: str, include_parts: bool) -> list[dict]:
    """topic -> subtopic -> concept with rolled-up levels; parts as well when include_parts."""
    def walk(node: dict) -> dict:
        entry = _node_entry(student_id, node, at)
        kids = [k for k in graph.children(node["id"]) if include_parts or k["level"] != "part"]
        if kids:
            entry["children"] = [walk(k) for k in kids]
        return entry

    return [walk(t) for t in graph.topics()]


def _levers(student_id: str, at: str, limit: int) -> list[dict]:
    """The parts where effort pays most: highest importance x (1 - p_now), leaving out secure ones."""
    found = []
    for part in learner.all_parts():
        p = learner.part_p(student_id, part, at)
        if learner.level(p) == "secure":
            continue
        importance = graph.weight(part)["importance"]
        found.append({"part_id": part, "name": graph.get_node(part)["name"], "level": learner.level(p),
                      "p_now": round(p, 2), "score": importance * (1 - p)})
    found.sort(key=lambda f: -f["score"])
    for f in found:
        del f["score"]
    return found[:limit]


def _weak_links(student_id: str, at: str, limit: int) -> list[dict]:
    """Confusable or causal pairs where one side is new and the other isn't: the link is where to work."""
    found = []
    for edge_type in ("confusable", "causal"):
        for edge in graph.links(edge_type):
            a, b = graph.get_node(edge["from_id"]), graph.get_node(edge["to_id"])
            pa, pb = learner.rollup(student_id, a["id"], at), learner.rollup(student_id, b["id"], at)
            la, lb = learner.level(pa), learner.level(pb)
            if (la == "new") == (lb == "new"):
                continue
            weak, strong = (a, b) if la == "new" else (b, a)
            found.append({"type": edge_type, "weak": {"id": weak["id"], "name": weak["name"]},
                          "strong": {"id": strong["id"], "name": strong["name"]}, "note": edge["note"],
                          "weight": edge["weight"] or 0.0})
    found.sort(key=lambda f: -f["weight"])
    for f in found:
        del f["weight"]
    return found[:limit]


def _shares(rows: list) -> dict[str, float] | None:
    if not rows:
        return None
    n = len(rows)
    return {
        "deep_questions": sum(r["question_depth"] in ("mechanism", "transfer") for r in rows) / n,
        "constructive": sum(r["engagement"] == "constructive" for r in rows) / n,
        "just_show_me": sum(bool(r["offloading"]) or r["choice_taken"] == "just_show_me" for r in rows) / n,
    }


def _trends(student_id: str, at: str) -> dict:
    """AI-literacy trends: each share over the last progress.trend_days against everything before, as a direction."""
    s = _settings().progress
    cut = learner._event_ts(learner.parse_ts(at) - timedelta(days=s.trend_days))
    rows = learner._conn().execute(
        "SELECT ts, question_depth, engagement, offloading, choice_taken FROM exchange_log WHERE student_id = ? AND ts <= ?",
        (student_id, at)).fetchall()
    recent, before = _shares([r for r in rows if r["ts"] > cut]), _shares([r for r in rows if r["ts"] <= cut])
    trends = {}
    for name in ("deep_questions", "constructive", "just_show_me"):
        now = recent[name] if recent else None
        then = before[name] if before else None
        if now is None or then is None:
            direction = None
        elif now - then >= s.trend_min_change:
            direction = "up"
        elif then - now >= s.trend_min_change:
            direction = "down"
        else:
            direction = "steady"
        trends[name] = {"recent": None if now is None else round(now, 2),
                        "before": None if then is None else round(then, 2), "direction": direction}
    return trends


def _study_pattern(student_id: str) -> dict | None:
    """When at least session.pattern_min_sessions sessions had a fatigue onset: the median onset minute and the
    line from text/progress/study_pattern.md. Otherwise None."""
    onsets = [s["fatigue_onset_minute"] for s in learner.sessions(student_id) if s["fatigue_onset_minute"] is not None]
    if len(onsets) < _settings().session.pattern_min_sessions:
        return None
    minutes = round(statistics.median(onsets))
    return {"minutes": minutes, "sessions": len(onsets),
            "text": read_text("progress/study_pattern.md").strip().format(minutes=minutes)}


def my_progress(student: dict, include_parts: bool = False, at: str | None = None) -> dict:
    """Tree with levels, the biggest levers, weak links, reviews due, AI-literacy trends and study pattern."""
    at = at or learner.now_iso()
    s, student_id = _settings(), student["id"]
    reviews = learner.due_reviews(student_id, _context().limits.get("reviews_due", 3), at)
    return {
        "tree": _tree(student_id, at, include_parts),
        "levers": _levers(student_id, at, s.progress.levers),
        "weak_links": _weak_links(student_id, at, s.progress.weak_links),
        "reviews_due": [{"part_id": r["part_id"], "name": r["name"], "level": learner.level(r["p_now"]),
                         "due": r["due"], "reason": r["reason"]} for r in reviews],
        "trends": _trends(student_id, at),
        "study_pattern": _study_pattern(student_id),
    }


# --- profile -------------------------------------------------------------------


def update_profile(
    student: dict,
    interests: str | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
) -> dict:
    """Update student_profile and return it. An empty exam_date_override clears it."""
    changes: dict[str, object] = {}
    if interests is not None:
        changes["interests"] = interests.strip()
    if exam_date_override is not None:
        if exam_date_override.strip():
            try:
                changes["exam_date_override"] = date.fromisoformat(exam_date_override.strip()).isoformat()
            except ValueError:
                return {"ok": False, "error": "exam_date_override must be a date like 2027-06-08"}
        else:
            changes["exam_date_override"] = None
    if answer_length is not None:
        if answer_length <= 0:
            return {"ok": False, "error": "answer_length must be a positive number of words"}
        changes["answer_length"] = answer_length
    conn = learner._conn()
    with conn:
        conn.execute("INSERT OR IGNORE INTO student_profile (student_id) VALUES (?)", (student["id"],))
        for column, value in changes.items():
            conn.execute(f"UPDATE student_profile SET {column} = ? WHERE student_id = ?", (value, student["id"]))
    row = conn.execute("SELECT interests, exam_date_override, answer_length FROM student_profile WHERE student_id = ?",
                       (student["id"],)).fetchone()
    return {"ok": True, "profile": dict(row)}
