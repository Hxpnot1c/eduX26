"""The per-student teacher view (decision 0030): the class with each student's card, and one student's review.

Off unless the school turns on web.teacher_student_view after its DPIA (students and parents told), or demo mode is on
and the class holds only seeded synthetic students. Everything here comes from the pack and the learner model: topic
names, wrong ideas, corrections and "try next" from the pack, levels and counts from the student's evidence. It never
reads or returns a chat or message text, and it shows levels and counts only: no probabilities, scores or rankings."""

from __future__ import annotations

import json
from collections import Counter

from edux import demo, graph, learner
from edux.settings import read_text
from edux.web import links, views

UNSURE = ("new", "developing", "needs_review")  # answered on and not yet secure
AT_DEVELOPING = ("developing", "secure")


def allowed(class_id: str) -> bool:
    """The per-student view is on for this class: the school's setting, or demo mode on a synthetic-only class."""
    if learner._settings().web.teacher_student_view:
        return True
    return links.demo_teacher_on() and demo.is_synthetic_class(class_id)


def _members(class_id: str) -> list[dict]:
    rows = learner._conn().execute("SELECT id, display_name FROM student WHERE class_id = ?", (class_id,)).fetchall()
    people = [{"id": r["id"], "name": r["display_name"] or r["id"]} for r in rows]
    return sorted(people, key=lambda p: (p["name"].split()[-1].lower() if p["name"].split() else "", p["name"].lower(), p["id"]))


def _topics() -> tuple[list[dict], dict[str, str]]:
    topics = [t for t in graph.topics() if not graph.is_literacy(t["id"])]
    part_topic = {p: t["id"] for t in topics for p in graph.parts_of(t["id"]) if not graph.is_literacy(p)}
    return topics, part_topic


def _answers(ids: list[str], at: str) -> dict[str, dict[str, dict]]:
    """student -> part -> {n, first, last} for course parts answered up to `at`."""
    out: dict[str, dict[str, dict]] = {sid: {} for sid in ids}
    if not ids:
        return out
    marks = ",".join("?" * len(ids))
    for r in learner._conn().execute(
        f"SELECT student_id, part_id, COUNT(*) AS n, MIN(ts) AS first, MAX(ts) AS last FROM evidence_log "
        f"WHERE student_id IN ({marks}) AND ts <= ? GROUP BY student_id, part_id",
        (*ids, learner._event_ts(at)),
    ):
        if not graph.is_literacy(r["part_id"]):
            out[r["student_id"]][r["part_id"]] = {"n": r["n"], "first": r["first"], "last": r["last"]}
    return out


def _held(ids: list[str]) -> dict[str, list[str]]:
    """student -> the course wrong ideas they hold now (AI-literacy ones left out)."""
    out: dict[str, list[str]] = {sid: [] for sid in ids}
    if not ids:
        return out
    marks = ",".join("?" * len(ids))
    for r in learner._conn().execute(
        f"SELECT student_id, misconception_id FROM student_misconception WHERE active = 1 AND student_id IN ({marks}) "
        "ORDER BY student_id, misconception_id",
        ids,
    ):
        m = graph.get_misconception(r["misconception_id"])
        if m and not graph.is_literacy(m["node_id"]):
            out[r["student_id"]].append(m["id"])
    return out


def try_next(part_id: str) -> str:
    """What to practise next for a part: its strongest prerequisite part if it has one (the gap is often there), else the
    part itself. A name from the pack."""
    before = [p for e in graph.prerequisites(part_id, 1) for p in graph.parts_of(e["other"]) if p != part_id]
    return graph.require_node(before[0] if before else part_id)["name"]


def _days(first: str, last: str) -> int:
    """The days a run of answers spans, first to last, counting a single day as 1."""
    return max(1, round((learner.parse_ts(last) - learner.parse_ts(first)).total_seconds() / 86400) + 1)


def _next_test(class_id: str, at: str) -> dict | None:
    today = learner.parse_ts(at).date().isoformat()
    row = (
        learner._conn()
        .execute(
            "SELECT id, name, kind, date, part_ids FROM student_assessment WHERE class_id = ? AND date >= ? ORDER BY date, id LIMIT 1",
            (class_id, today),
        )
        .fetchone()
    )
    if row is None:
        return None
    _, part_topic = _topics()
    parts = json.loads(row["part_ids"] or "[]")
    topic_ids = list(dict.fromkeys(part_topic[p] for p in parts if p in part_topic))
    return {"id": row["id"], "name": row["name"], "kind": row["kind"], "date": row["date"], "parts": parts, "topics": topic_ids}


def _misconception(mid: str) -> dict:
    m = graph.get_misconception(mid) or {}
    return {"id": mid, "wrong_idea": m.get("wrong_idea", ""), "correction": m.get("correction", ""), "part_id": m.get("node_id", "")}


def class_review(class_id: str, at: str | None = None) -> dict | None:
    """The class view of the design: header, topic chips, student cards (alphabetical by surname), the next test's topics
    that most need review, a band per topic (from 5 answering students) and wrong ideas held by more than one student."""
    at = at or learner.now_iso()
    row = learner._conn().execute("SELECT id, name FROM class WHERE id = ?", (class_id,)).fetchone()
    if row is None:
        return None
    minimum = learner._settings().coverage.class_min_students
    people = _members(class_id)
    ids = [p["id"] for p in people]
    topics, part_topic = _topics()
    answers, held = _answers(ids, at), _held(ids)
    levels = {sid: {p: views._word(learner.shown_level(sid, p, at)) for p in answers[sid]} for sid in ids}
    test = _next_test(class_id, at)
    test_parts = set(test["parts"]) if test else set()

    cards = []
    for person in people:
        sid = person["id"]
        weak = [p for p in answers[sid] if levels[sid][p] in ("new", "developing", "review")]
        order = {p: i for i, p in enumerate(learner.all_parts())}
        weak.sort(key=lambda p: (p not in test_parts, order.get(p, 0)))
        cards.append(
            {
                "id": sid,
                "name": person["name"],
                "weak": [{"part_id": p, "name": graph.require_node(p)["name"], "topic_id": part_topic.get(p)} for p in weak],
                "topics": sorted({part_topic[p] for p in answers[sid] if p in part_topic}),
                "held": held[sid],
            }
        )

    count = Counter(mid for sid in ids for mid in held[sid])
    bands = []
    for t in topics:
        parts = set(graph.parts_of(t["id"]))
        answered = [sid for sid in ids if parts & set(answers[sid])]
        if not answered:
            continue
        ok = sum(all(levels[sid][p] in AT_DEVELOPING for p in parts & set(answers[sid])) for sid in answered)
        common = sorted((m for m in count if _misconception(m)["part_id"] in parts), key=lambda m: (-count[m], m))
        entry: dict = {"topic_id": t["id"], "name": t["name"], "answered": len(answered), "enough": len(answered) >= minimum}
        if entry["enough"]:
            share = ok / len(answered)
            band = "few" if share < views.BAND_LOW else "mixed" if share <= views.BAND_HIGH else "most"
            entry |= {"band": band, "label": views.BAND_WORDS[band], "level": views.BAND_LEVEL[band], "share": share}
        entry["common"] = (_misconception(common[0]) | {"students": count[common[0]]}) if common else None
        bands.append(entry)

    before = []
    if test:
        in_test = [b for b in bands if b["topic_id"] in test["topics"]]
        in_test.sort(key=lambda b: (not b["enough"], b.get("share", 1.0), b["name"]))
        before = [{k: v for k, v in b.items() if k != "share"} for b in in_test]
    for b in bands:
        b.pop("share", None)

    wrong = []
    for mid, n in sorted(count.items(), key=lambda kv: (-kv[1], kv[0])):
        if n < 2:
            continue
        m = _misconception(mid)
        wrong.append(
            m
            | {
                "part": graph.require_node(m["part_id"])["name"] if m["part_id"] else "",
                "topic_id": part_topic.get(m["part_id"]),
                "students": n,
                "try_next": try_next(m["part_id"]) if m["part_id"] else "",
            }
        )

    names = {t["id"]: t["name"] for t in topics}
    return {
        "class": {"id": row["id"], "name": row["name"], "size": len(people)},
        "synthetic": demo.is_synthetic_class(class_id),
        "min_cell": minimum,
        "test": None
        if test is None
        else {
            "id": test["id"],
            "name": test["name"],
            "date": test["date"],
            "topics": [{"id": t, "name": names[t]} for t in test["topics"]],
        },
        "topics": [{"id": t["id"], "name": t["name"]} for t in topics if any(b["topic_id"] == t["id"] for b in bands)],
        "students": cards,
        "before_test": before,
        "bands": bands,
        "wrong_ideas": wrong,
    }


def _tip(skill: str, level: str) -> str:
    for line in read_text("teacher/ai_literacy_tips.md").splitlines():
        if line.startswith(f"- {skill}.{level}:"):
            return line.split(":", 1)[1].strip()
    return ""


def student_review(class_id: str, student_id: str, at: str | None = None) -> dict | None:
    """One student's review: what they are unsure about (with the wrong idea they hold, its correction and what to try
    next), the taught topics not yet checked, and AI-literacy levels with the evidence they rest on. None if the student
    is not in the class."""
    from edux import service

    at = at or learner.now_iso()
    person = next((p for p in _members(class_id) if p["id"] == student_id), None)
    if person is None:
        return None
    topics, part_topic = _topics()
    names = {t["id"]: t["name"] for t in topics}
    answers, held = _answers([student_id], at)[student_id], _held([student_id])[student_id]
    test = _next_test(class_id, at)
    test_parts = set(test["parts"]) if test else set()
    order = {p: i for i, p in enumerate(learner.all_parts())}
    unsure, not_checked = [], []
    for part in sorted(answers, key=lambda p: (p not in test_parts, order.get(p, 0))):
        level = views._word(learner.shown_level(student_id, part, at))
        if level not in ("new", "developing", "review"):
            continue
        wrong = next((_misconception(m) for m in held if _misconception(m)["part_id"] == part), None)
        unsure.append(
            {
                "part_id": part,
                "part": graph.require_node(part)["name"],
                "topic": names.get(part_topic.get(part, ""), ""),
                "level": level,
                "wrong_idea": wrong["wrong_idea"] if wrong else None,
                "correction": wrong["correction"] if wrong else None,
                "try_next": try_next(part),
                "answers": answers[part]["n"],
                "over_days": _days(answers[part]["first"], answers[part]["last"]),
                "in_test": part in test_parts,
            }
        )
    for part in sorted(part_topic, key=lambda p: (p not in test_parts, order.get(p, 0))):
        if part not in answers and learner.shown_level(student_id, part, at) == "taught_in_class":
            not_checked.append(
                {
                    "part_id": part,
                    "part": graph.require_node(part)["name"],
                    "topic": names.get(part_topic[part], ""),
                    "in_test": part in test_parts,
                }
            )
    # the header counts exactly what the rows rest on, so it always matches them
    shown = [answers[r["part_id"]] for r in unsure]
    total = sum(a["n"] for a in shown)
    first, last = min((a["first"] for a in shown), default=None), max((a["last"] for a in shown), default=None)
    ai = service._ai_literacy(student_id, at)
    skills = []
    for key, name in (("ask", "Ask"), ("verify", "Verify"), ("how_ai_works", "How AI works")):
        level = ai[key]["level"]
        skills.append(
            {
                "id": key,
                "name": name,
                "level": level,
                "checks": ai[key]["evidence"]["checks"],
                "over_days": max(1, ai[key]["evidence"]["over_days"]) if ai[key]["evidence"]["checks"] else 0,
                "tip": _tip(key, level),
            }
        )
    return {
        "student": {"id": person["id"], "name": person["name"]},
        "synthetic": person["id"].startswith(demo.SYNTH_PREFIX),
        "test": None if test is None else {"name": test["name"], "date": test["date"]},
        "record": {"answers": total, "over_days": _days(first, last) if first and last else 0, "parts": len(unsure)},
        "unsure": unsure,
        "not_checked": not_checked,
        "ai_literacy": {"note": ai["formative"], "skills": skills},
    }
