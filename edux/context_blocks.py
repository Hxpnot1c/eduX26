"""Context blocks: the inputs tutor_turn chooses its plan from, and the reference it sends.

Blocks carry data, not instructions; the wording for the chatbot is in text/moves/ (see plan.py).
Each block is one function taking (turn, settings) and returning a small dict, or None to leave it out.
A Turn carries the student, the focus parts and the message, so every block chooses what to show for
this turn: content weights (importance, link weight, authority, marks), the student's state and the
message's relevance, never a fixed top N. context.toml chooses the blocks, their order and limits per profile.
"""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field

from edux import graph, learner
from edux.settings import ContextConfig, Settings, read_text

log = logging.getLogger(__name__)


@dataclass
class Turn:
    """What one turn (tutor_turn, or service.learning_context for debugging) is about."""

    student: dict
    parts: list[str]  # focus parts, best first
    message: str
    at: str  # ISO time the state is read at
    limits: dict[str, int]
    resolution: dict  # graph.resolve() output
    blocks: dict[str, dict | None] = field(default_factory=dict)  # blocks produced so far this turn
    cache: dict = field(default_factory=dict)  # values worked out once a turn (priorities)
    mcq_ok: bool = True  # a multiple-choice question may be asked this turn (questions.min_open_between_mcq, decision 0028)

    @property
    def student_id(self) -> str:
        return self.student["id"]

    def p(self, part_id: str) -> float:
        return learner.part_p(self.student_id, part_id, self.at)

    def value(self, part_id: str) -> float:
        """Expected marks from a step on the part (learner.step_value), cached for the turn."""
        return self.valued(part_id)["value"]

    def valued(self, part_id: str) -> dict:
        values = self.cache.setdefault("values", {})
        if part_id not in values:
            values[part_id] = learner.step_value(self.student_id, part_id, self.at)
        return values[part_id]

    def limit(self, name: str, default: int = 3) -> int:
        return self.limits.get(name, default)


# --- helpers -----------------------------------------------------------------


def _r(value: float) -> float:
    return round(value, 2)


def _part_summary(turn: Turn, part_id: str) -> dict:
    node = graph.require_node(part_id)
    p = turn.p(part_id)
    return {
        "id": part_id,
        "name": node["name"],
        "part_type": node["part_type"],
        "level": learner.shown_level(turn.student_id, part_id, turn.at),
        "p_now": _r(p),
    }


def _node_level(turn: Turn, node_id: str) -> str:
    """Level to show for a concept or topic from the rollup of its parts (learner.shown_rollup: before any answer, never
    developing or secure)."""
    return learner.shown_rollup(turn.student_id, node_id, turn.at)


def link_weight(edge: dict, from_id: str, settings: Settings) -> float:
    """An edge's weight as read now: the loaded weight (teacher's or computed, else link_weight.base) mixed with
    the cross-student misconception signal at share link_weight.w_misconception."""
    base = edge["weight"] if edge["weight"] is not None else settings.link_weight.base
    w = settings.link_weight.w_misconception
    return (1 - w) * base + w * learner.misconception_link_signal(from_id, edge["other"])


def _state_rows(turn: Turn) -> dict[str, dict]:
    rows = learner._conn().execute("SELECT * FROM part_state WHERE student_id = ?", (turn.student_id,))
    return {r["part_id"]: dict(r) for r in rows}


def _held_misconceptions(turn: Turn, active_only: bool) -> dict[str, dict]:
    """The student's misconception rows (id -> {node_id, last_seen, active})."""
    rows = learner._conn().execute(
        """SELECT sm.misconception_id, sm.last_seen, sm.active, m.node_id FROM student_misconception sm
           JOIN content.misconception m ON m.id = sm.misconception_id WHERE sm.student_id = ?""",
        (turn.student_id,),
    )
    return {r["misconception_id"]: dict(r) for r in rows if r["active"] or not active_only}


def held_misconceptions(student_id: str, parts: list[str]) -> list[dict]:
    """Misconceptions on the parts that the student currently holds, most recently seen first."""
    held = {
        r["misconception_id"]: r["last_seen"]
        for r in learner._conn().execute(
            "SELECT misconception_id, last_seen FROM student_misconception WHERE student_id = ? AND active = 1", (student_id,)
        )
    }
    found = [m for m in graph.misconceptions_for(parts) if m["id"] in held]
    found.sort(key=lambda m: -learner.parse_ts(held[m["id"]]).timestamp())
    return found


def _neighbour_parts(part_id: str) -> set[str]:
    """Parts linked to a part by any edge, plus the other parts of its concept."""
    found: set[str] = set()
    concept = graph.concept_of(part_id)
    if concept:
        found.update(graph.parts_of(concept))
    for lookup in (graph.prerequisites, graph.dependents):
        for edge in lookup(part_id, 1):
            found.update(graph.parts_of(edge["other"]))
    for link_lookup in (graph.analogous, graph.confusables, graph.causal_out, graph.causal_in):
        for edge in link_lookup(part_id):
            found.update(graph.parts_of(edge["other"]))
    found.discard(part_id)
    return found


def order_parts(student: dict, parts: list[str], message: str) -> list[str]:
    """Focus parts best first: relevance to the message, then the parts the student touched most recently,
    then importance."""
    relevance = graph.node_relevance(message, parts)
    seen = {
        r["part_id"]: r["last_seen"]
        for r in learner._conn().execute("SELECT part_id, last_seen FROM part_state WHERE student_id = ?", (student["id"],))
    }

    def key(part: str) -> tuple:
        last = seen.get(part)
        return (-_r(relevance.get(part, 0.0)), -(learner.parse_ts(last).timestamp() if last else 0.0), -graph.weight(part)["importance"])

    return sorted(parts, key=key)


# --- blocks ------------------------------------------------------------------


def focus(turn: Turn, settings: Settings) -> dict | None:
    """Resolved parts with name, type and level, or candidates to ask about when the message is ambiguous."""
    r = turn.resolution
    out: dict = {}
    if turn.parts:
        out["parts"] = [_part_summary(turn, p) for p in turn.parts]
        if r.get("matched"):
            out["matched"] = {"id": r["matched"]["id"], "name": r["matched"]["name"], "level": r["matched"]["level"]}
    elif r.get("candidates"):
        out["candidates"] = [{"id": c["id"], "name": c["name"], "level": c["level"]} for c in r["candidates"]]
    else:
        out["parts"] = []
    if r.get("unknown"):
        out["unknown_ids"] = r["unknown"]
    return out


def _latest_evidence_correct(turn: Turn, part_id: str, settings: Settings) -> bool:
    row = (
        learner._conn()
        .execute(
            "SELECT score FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts <= ? ORDER BY ts DESC, id DESC LIMIT 1",
            (turn.student_id, part_id, learner._event_ts(turn.at)),
        )
        .fetchone()
    )
    return row is not None and row["score"] >= settings.bkt.correct_share


def support(turn: Turn, settings: Settings) -> dict | None:
    """Support level for the main focus part, from its p_now. extend is true when p_now >= support.extend_from
    and the student's latest answer on the part was correct. The wording is in text/moves/ (plan.py)."""
    if not turn.parts:
        return None
    part = turn.parts[0]
    p = turn.p(part)
    level = learner.support_level(p)
    extend = p >= settings.support.extend_from and _latest_evidence_correct(turn, part, settings)
    return {"part_id": part, "level": level, "extend": extend}


def _session_offloaded(turn: Turn) -> bool:
    """True if the student chose "just show me" (or offloaded) at any point in the current session."""
    session = learner.session_state(turn.student_id, turn.at)
    if session is None:
        return False
    row = (
        learner._conn()
        .execute(
            """SELECT 1 FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
           AND (offloading = 1 OR choice_taken = 'just_show_me') LIMIT 1""",
            (turn.student_id, session["session_id"], learner._event_ts(turn.at)),
        )
        .fetchone()
    )
    return row is not None


def core_idea(part_id: str) -> str:
    """The part's core idea, the correct option of its intuition question: its first mark point, else its main
    key wording, else its note's first key point, else its description. Never an exemplar: every MCQ's correct
    option is a point (exemplars are used only in teach_point)."""
    points = graph.mark_points_for([part_id])
    if points:
        return points[0]["point"]
    for note in graph.notes_for([part_id], limit=1):
        idea = (note["key_wording"] or note["key_points"] or [None])[0]
        if idea:
            return idea
    return graph.require_node(part_id)["description"]


def intuition_source(turn: Turn, part_id: str) -> dict | None:
    """Where an intuition question on a part leads in from (step 05d): an edge with teach_use = intuition from a
    part or concept the student has at developing or above (the strongest link first), as {note, via}; else the
    part's own intuition line, as {note}; else None. Linked parts the student doesn't know are never named."""
    edges = [
        e
        for lookup in (graph.prerequisites, graph.analogous, graph.confusables, graph.causal_in)
        for e in (lookup(part_id, 1) if lookup is graph.prerequisites else lookup(part_id))
        if e["teach_use"] == "intuition" and e["direction"] == "in" and e["note"]
    ]
    known = [e for e in edges if _node_level(turn, e["other"]) not in ("new", "needs_review")]  # faded: not known now (decision 0025)
    if known:
        best = max(known, key=lambda e: e["weight"] or 0)
        return {"note": best["note"], "via": best["other_name"]}
    line = graph.require_node(part_id).get("intuition") or ""
    return {"note": line} if line else None


def prequestion(turn: Turn, settings: Settings) -> dict | None:
    """A multiple-choice question to ask before teaching an untaught, weak part (no evidence on it yet, even an
    untaught pre-question), with misconceptions as the wrong options (examiner-report sources first). Left out
    once the student has said "just show me" this session. From step 05d it is the intuition question, with
    its source (intuition_source)."""
    pq = settings.prequestion
    if not pq.enabled or not turn.parts:
        return None
    part = turn.parts[0]
    answered = (
        learner._conn()
        .execute(
            "SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts <= ? LIMIT 1",
            (turn.student_id, part, learner._event_ts(turn.at)),
        )
        .fetchone()
    )
    if answered or turn.p(part) >= settings.support.worked_example_below:
        return None
    found = graph.misconceptions_for([part])
    if len(found) < settings.mcq.min_distractors or _session_offloaded(turn):
        return None
    found.sort(key=lambda m: "examiner_report" not in graph.source_types(m["source_ids"]))
    keys = [mp for mp in graph.mark_points_for([part]) if mp["node_id"] == part]
    if not keys:  # the key is a mark point, never key wording or the description (plan.mcq_points)
        return None
    return {
        "part_id": part,
        "correct": keys[0]["point"],
        "source": intuition_source(turn, part),
        "distractors": [
            {"id": m["id"], "wrong_idea": m["wrong_idea"], "correction": m["correction"]} for m in found[: settings.mcq.max_options - 1]
        ],
    }


def _quick_parts(turn: Turn, settings: Settings, stuck: set[str]) -> list[dict]:
    """Up to session.quick_parts developing parts (between levels.new and levels.secure), most important first,
    leaving out parts the student is stuck on."""
    found = []
    for part in learner.all_parts():
        p = turn.p(part)
        if settings.levels.new <= p < settings.levels.secure and part not in stuck:
            found.append((graph.weight(part)["importance"], part))
    found.sort(key=lambda f: -f[0])
    return [_part_summary(turn, part) for _, part in found[: settings.session.quick_parts]]


def _step_back_to(turn: Turn, part_id: str) -> dict | None:
    """The weakest prerequisite part of a part, or None if it has none."""
    pres = {pre for edge in graph.prerequisites(part_id, 1) for pre in graph.parts_of(edge["other"])}
    if not pres:
        return None
    return _part_summary(turn, min(pres, key=turn.p))


def session(turn: Turn, settings: Settings) -> dict | None:
    """Only when there is something to say about this session: fatigued (offer stopping first, or a few quick
    questions on quick_parts) or stuck on a part (step back to its weakest prerequisite, or switch approach)."""
    state = learner.session_state(turn.student_id, turn.at)
    if state is None:
        return None
    if state["fatigued"]:
        out = {
            "state": "fatigued",
            "reason": state["fatigue_reason"],
            "minutes": round(state["minutes"]),
            "quick_parts": _quick_parts(turn, settings, {p["part_id"] for p in state["stuck_parts"]}),
        }
        if state["stuck_parts"]:
            out["also_stuck_on"] = [p["part_id"] for p in state["stuck_parts"]]
        return out
    if state["stuck_parts"]:
        parts = [
            {
                "part_id": p["part_id"],
                "name": p["name"],
                "attempts": p["attempts"],
                "mean_score": _r(p["mean_score"]),
                "step_back_to": _step_back_to(turn, p["part_id"]),
            }
            for p in state["stuck_parts"]
        ]
        return {"state": "stuck", "parts": parts, "step_back_to": parts[0]["step_back_to"]}
    return None


def weak_prerequisites(turn: Turn, settings: Settings) -> dict | None:
    """Prerequisites below secure, ranked by expected marks x link weight (learner.step_value, priorities), then,
    on a tie, by how weak the student is x link weight x importance."""
    found: dict[str, dict] = {}
    for part in turn.parts:
        for edge in graph.prerequisites(part, 1):
            w = link_weight(edge, part, settings)
            for pre in graph.parts_of(edge["other"]):
                p = turn.p(pre)
                if pre in turn.parts or p >= settings.levels.secure:
                    continue
                score = (turn.value(pre) * w, (1 - p) * w * graph.weight(pre)["importance"])
                if pre not in found or score > found[pre]["score"]:
                    node = graph.require_node(pre)
                    found[pre] = {
                        "part_id": pre,
                        "name": node["name"],
                        "level": learner.shown_level(turn.student_id, pre, turn.at),
                        "p_now": _r(p),
                        "for": part,
                        "note": edge["note"],
                        "score": score,
                    }
    items = sorted(found.values(), key=lambda i: (-i["score"][0], -i["score"][1]))[: turn.limit("weak_prerequisites")]
    for item in items:
        del item["score"]
    return {"items": items} if items else None


def anchor(turn: Turn, settings: Settings) -> dict | None:
    """A secure analogous part to teach through, with the edge note: the strongest link across the focus parts."""
    best = None
    for part in turn.parts:
        found = learner.anchor(turn.student_id, part, turn.at)
        if found and (best is None or (found["weight"] or 0) > (best["weight"] or 0)):
            best = {**found, "for": part}
    if best is None:
        return None
    best["p_now"] = _r(best["p_now"])
    best.pop("weight", None)
    return best


def confusables(turn: Turn, settings: Settings) -> dict | None:
    """Nodes to contrast with the focus, ranked by link weight x (1 + a past mix-up + the message mentioning them)."""
    b = settings.blocks
    held_nodes = {m["node_id"] for m in _held_misconceptions(turn, active_only=False).values()}
    edges = [(part, edge) for part in turn.parts for edge in graph.confusables(part)]
    relevance = graph.node_relevance(turn.message, list({e["other"] for _, e in edges}))
    found: dict[str, dict] = {}
    for part, edge in edges:
        other = edge["other"]
        sides = set(turn.parts) | set(graph.parts_of(other))
        mixup = 1.0 if held_nodes & sides else 0.0
        score = link_weight(edge, part, settings) * (1 + b.confusable_mixup * mixup + b.confusable_mention * relevance.get(other, 0.0))
        if other not in found or score > found[other]["score"]:
            found[other] = {
                "id": other,
                "name": edge["other_name"],
                "level": _node_level(turn, other),
                "note": edge["note"],
                "past_mixup": bool(mixup),
                "score": score,
            }
    items = sorted(found.values(), key=lambda i: -i["score"])[: turn.limit("confusables")]
    for item in items:
        del item["score"]
    return {"items": items} if items else None


def _asks_about_causes(message: str, cues: list[str]) -> bool:
    words = re.findall(r"[a-z]+", message.lower())
    return any(word.startswith(cue) for word in words for cue in cues)


def causal(turn: Turn, settings: Settings) -> dict | None:
    """What the focus affects and what affects it, shown when the message asks about causes or effects or
    mentions the other end; ranked by link weight x (1 + the message mentioning the other end)."""
    b = settings.blocks
    edges = [(part, edge, "affects") for part in turn.parts for edge in graph.causal_out(part)]
    edges += [(part, edge, "affected_by") for part in turn.parts for edge in graph.causal_in(part)]
    if not edges:
        return None
    cue = _asks_about_causes(turn.message, b.causal_cues)
    relevance = graph.node_relevance(turn.message, list({e["other"] for _, e, _ in edges}))
    found: dict[tuple, dict] = {}
    for part, edge, direction in edges:
        mention = relevance.get(edge["other"], 0.0)
        if not cue and mention <= 0:
            continue
        score = link_weight(edge, part, settings) * (1 + b.causal_mention * mention)
        key = (edge["other"], direction)
        if key not in found or score > found[key]["score"]:
            found[key] = {
                "direction": direction,
                "id": edge["other"],
                "name": edge["other_name"],
                "level": _node_level(turn, edge["other"]),
                "note": edge["note"],
                "for": part,
                "score": score,
            }
    items = sorted(found.values(), key=lambda i: -i["score"])[: turn.limit("causal")]
    for item in items:
        del item["score"]
    return {"items": items} if items else None


def misconceptions(turn: Turn, settings: Settings) -> dict | None:
    """Misconceptions on the focus parts, split in two. held: ones the student currently holds, most recently
    seen first (correct these). watch_for: the others, the ones the message touches first (raise them only if
    the student shows them). Each list is capped at limits.misconceptions."""
    held_rows = _held_misconceptions(turn, active_only=True)
    found = graph.misconceptions_for(turn.parts)
    relevance = graph.relevance(turn.message, {m["id"]: f"{m['wrong_idea']} {m['correction']}" for m in found})
    held = [m for m in found if m["id"] in held_rows]
    held.sort(key=lambda m: -learner.parse_ts(held_rows[m["id"]]["last_seen"]).timestamp())
    watch = [m for m in found if m["id"] not in held_rows]
    watch.sort(key=lambda m: -relevance[m["id"]])
    limit = turn.limit("misconceptions")

    def item(m: dict) -> dict:
        return {"id": m["id"], "part_id": m["node_id"], "wrong_idea": m["wrong_idea"], "correction": m["correction"]}

    out = {"held": [item(m) for m in held[:limit]], "watch_for": [item(m) for m in watch[:limit]]}
    return out if out["held"] or out["watch_for"] else None


def notes(turn: Turn, settings: Settings) -> dict | None:
    """Notes per focus part, the most relevant to the message first, then by source authority; plus the parts'
    mark points, which evidence is scored against."""
    if not turn.parts:
        return None
    found = graph.notes_for(turn.parts)
    relevance = graph.relevance(turn.message, {n["id"]: " ".join([n["summary"], *n["key_points"], *n["key_wording"]]) for n in found})
    items = []
    for part in turn.parts:
        mine = [n for n in found if n["part_id"] == part]
        mine.sort(key=lambda n: (-round(relevance[n["id"]], 1), -n["authority"]))
        for n in mine[: turn.limit("notes")]:
            items.append(
                {
                    "id": n["id"],
                    "part_id": part,
                    "summary": n["summary"],
                    "key_points": n["key_points"],
                    "key_wording": n["key_wording"][: turn.limit("key_wording")],
                    "source": n["source_title"],
                    "source_type": n["source_type"],
                    "location": n["location"],
                }
            )
    mark_points: dict[str, list[dict]] = {}
    for mp in graph.mark_points_for(turn.parts):
        mark_points.setdefault(mp["node_id"], []).append({"point": mp["point"], "exemplar": mp["exemplar"]})
    out: dict = {"items": items}
    if mark_points:
        out["mark_points"] = mark_points
    return out if items or mark_points else None


def _days_until(date: str | None, at: str) -> float | None:
    if not date:
        return None
    days = (learner.parse_ts(date) - learner.parse_ts(at)).total_seconds() / 86400
    return days if days > 0 else None


def exam_relevance(turn: Turn, settings: Settings) -> dict | None:
    """Past-paper questions on the focus parts, ranked by marks at stake, how close the exam is and whether
    the question's command word is in the message ("calculate", "explain"); plus the papers that cover them."""
    b = settings.blocks
    if not turn.parts:
        return None
    papers: dict[str, dict] = {}
    for part in turn.parts:
        for paper in graph.exam_papers_for(part):
            days = _days_until(paper["date"], turn.at)
            papers[paper["id"]] = {
                "id": paper["id"],
                "name": paper["name"],
                "date": paper["date"],
                "days_to_exam": None if days is None else math.ceil(days),  # calendar days: round(2.5) is 2 at midday
            }
    questions = graph.questions_for(turn.parts)
    if not questions and not papers:
        return None
    max_marks = max((q["marks"] for q in questions), default=1) or 1
    command = graph.relevance(turn.message, {q["id"]: q["command_word"] or "" for q in questions})
    scored = []
    for q in questions:
        days = _days_until(papers.get(q["paper_id"], {}).get("date"), turn.at)
        closeness = 0.0 if days is None else max(0.0, 1 - days / b.exam_horizon_days)
        score = (
            b.exam_w_marks * q["marks"] / max_marks
            + b.exam_w_closeness * closeness
            + b.exam_w_command * (1.0 if command[q["id"]] > 0 else 0.0)
        )
        scored.append((score, q))
    scored.sort(key=lambda sq: -sq[0])
    items = [
        {
            "id": q["id"],
            "paper": q["paper_name"],
            "series": q["series"],
            "number": q["number"],
            "marks": q["marks"],
            "command_word": q["command_word"],
            "summary": q["summary"],
            "parts": q["parts"],
        }
        for _, q in scored[: turn.limit("exam_questions")]
    ]
    return {"papers": list(papers.values()), "questions": items}


def reviews_due(turn: Turn, settings: Settings) -> dict | None:
    """Due reviews ranked by expected marks (learner.step_value, priorities), then, on a tie, by how overdue x
    importance, boosted when the part is linked to the current focus; each with a mode (recall or transfer).
    Only parts already due are here: an upcoming test orders reviews, it never makes one due."""
    b = settings.blocks
    due = learner.due_reviews(turn.student_id, 10_000, turn.at)
    if not due:
        return None
    linked: set[str] = set()
    for part in turn.parts:
        linked |= _neighbour_parts(part) | {part}
    at = learner.parse_ts(turn.at)
    scored = []
    for r in due:
        overdue_days = max(0.0, (at - learner.parse_ts(r["due"])).total_seconds() / 86400)
        is_linked = r["part_id"] in linked
        score = (1 + overdue_days) * (r["importance"] + b.review_importance_floor) * (1 + b.review_link_boost * is_linked)
        scored.append((turn.value(r["part_id"]), score, r, is_linked))
    scored.sort(key=lambda s: (-s[0], -s[1]))
    limit = min(turn.limit("reviews_due"), settings.scheduling.max_reviews_per_reply)
    return {"items": [_review_item(turn, r, is_linked, settings) for _, _, r, is_linked in scored[:limit]]}


def _new_context(part_id: str, settings: Settings) -> dict:
    """A new context for a transfer review: a causal or analogous link from the graph (strongest first), then a
    past-paper question on the part (most marks first), then an unseen case for the chatbot to make up.
    Which past questions a student has already seen isn't recorded yet, so any question can be suggested."""
    edges = [e for lookup in (graph.causal_out, graph.causal_in, graph.analogous) for e in lookup(part_id)]
    if edges:
        edge = max(edges, key=lambda e: link_weight(e, part_id, settings))
        return {"kind": "link", "type": edge["type"], "id": edge["other"], "name": edge["other_name"], "note": edge["note"]}
    questions = sorted(graph.questions_for([part_id]), key=lambda q: -q["marks"])
    if questions:
        q = questions[0]
        return {
            "kind": "past_question",
            "id": q["id"],
            "series": q["series"],
            "marks": q["marks"],
            "command_word": q["command_word"],
            "summary": q["summary"],
        }
    return {"kind": "unseen_case"}


def _review_item(turn: Turn, r: dict, is_linked: bool, settings: Settings) -> dict:
    """A due review with its mode: recall when the part is weak (p_now < levels.new), otherwise transfer to a new context."""
    mode = "recall" if r["p_now"] < settings.levels.new else "transfer"
    item = {
        "part_id": r["part_id"],
        "name": r["name"],
        "level": learner.shown_level(turn.student_id, r["part_id"], turn.at),
        "p_now": _r(r["p_now"]),
        "reason": r["reason"],
        "due": r["due"],
        "linked_to_focus": is_linked,
        "mode": mode,
    }
    if mode == "transfer":
        item["new_context"] = _new_context(r["part_id"], settings)
    return item


# --- teaching note -------------------------------------------------------------


def _note_templates() -> dict[str, str]:
    """text/teaching_note.md: one "## piece" heading per sentence template; HTML comments are ignored."""
    text = re.sub(r"<!--.*?-->", "", read_text("teaching_note.md"), flags=re.S)
    templates, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            templates[current] = ""
        elif current and line.strip():
            templates[current] = (templates[current] + " " + line.strip()).strip()
    return templates


def _names(items: list[dict], key: str = "name") -> str:
    return "; ".join(f"{i[key]} ({i['level']})" if "level" in i else i[key] for i in items)


def _worked_before(turn: Turn, settings: Settings) -> str | None:
    """The support approach that most often led to a correct next answer on the main part, with enough records."""
    if not turn.parts:
        return None
    records = learner.approaches(turn.student_id, turn.parts[0])
    if len(records) < settings.teaching_note.approach_min_records:
        return None
    tally: dict[str, list[int]] = {}
    for r in records:
        if r["next_check_correct"] is not None:
            tally.setdefault(r["approach"], []).append(r["next_check_correct"])
    best = max(tally.items(), key=lambda kv: (sum(kv[1]) / len(kv[1]), len(kv[1])), default=None)
    return best[0].replace("_", " ") if best and sum(best[1]) else None


def teaching_note(turn: Turn, settings: Settings) -> dict | None:
    """A short paragraph from text/teaching_note.md, built only from the blocks produced this turn."""
    t, blocks, pieces = _note_templates(), turn.blocks, []

    def add(piece: str, **values: object) -> None:
        if t.get(piece):
            pieces.append(t[piece].format(**values))

    focus, support, weak = blocks.get("focus"), blocks.get("support"), blocks.get("weak_prerequisites")
    anchor, misconceptions = blocks.get("anchor"), blocks.get("misconceptions")
    if focus and focus.get("parts"):
        add("focus", parts=_names(focus["parts"]))
    if support:
        add("support", level=support["level"].replace("_", " "))
    if weak:
        add("weak_prerequisites", items=_names(weak["items"]))
    if anchor:
        add("anchor", name=anchor["name"], note=anchor["note"] or "")
    if misconceptions and misconceptions["held"]:
        add("misconceptions", items="; ".join(m["wrong_idea"].rstrip(".") for m in misconceptions["held"]))
    if turn.parts:
        days = learner.days_to_exam(turn.student_id, turn.parts[0], learner.parse_ts(turn.at))
        if days is not None and days <= settings.teaching_note.exam_close_days:
            add("exam_close", days=math.ceil(days))
    approach = _worked_before(turn, settings)
    if approach:
        add("worked_before", approach=approach)
    if not pieces:
        return None
    words = " ".join(pieces).split()
    text = " ".join(words[: settings.teaching_note.max_words])
    return {"text": text if len(words) <= settings.teaching_note.max_words else text + " ..."}


Block = Callable[[Turn, Settings], dict | None]

BLOCKS: dict[str, Block] = {
    "focus": focus,
    "prequestion": prequestion,
    "support": support,
    "session": session,
    "weak_prerequisites": weak_prerequisites,
    "anchor": anchor,
    "confusables": confusables,
    "causal": causal,
    "misconceptions": misconceptions,
    "notes": notes,
    "exam_relevance": exam_relevance,
    "reviews_due": reviews_due,
    "teaching_note": teaching_note,
}


def assemble(profile: str, turn: Turn, settings: Settings, context: ContextConfig) -> dict[str, dict]:
    """Run the profile's blocks in order and return the ones that produced something, in that order.

    An unknown profile falls back to the default; unknown block names are skipped with a warning.
    Blocks run in profile order, so teaching_note (last) sees what the others produced.
    """
    if profile not in context.profiles:
        log.warning("unknown context profile %r; using %r", profile, context.default_profile)
        profile = context.default_profile
    out: dict[str, dict] = {}
    for name in context.profiles[profile].blocks:
        block = BLOCKS.get(name)
        if block is None:
            log.warning("unknown context block %r in profile %r; skipped", name, profile)
            continue
        value = block(turn, settings)
        turn.blocks[name] = value
        if value is not None:
            out[name] = value
    return out


# --- reference per move (step 05c) ----------------------------------------------


def _move_table(context: ContextConfig, step: dict) -> list[str]:
    """The reference blocks a step's move uses: its key's table, else the bare move's, else none."""
    table = context.moves.get(step.get("key") or step["move"]) or context.moves.get(step["move"])
    return list(table.reference) if table else []


def asks_watch_for(context: ContextConfig, step: dict) -> bool:
    return bool({step.get("key"), step["move"]} & set(context.watch_for.moves))


def _part_turn(turn: Turn, part_id: str) -> Turn:
    """The same turn narrowed to one part, so a block shows only what that step is about."""
    return Turn(student=turn.student, parts=[part_id], message=turn.message, at=turn.at, limits=turn.limits, resolution=turn.resolution)


def _merge(into: dict, name: str, value: object) -> None:
    """Add one step's block to the reference: lists and {"items"} blocks are joined without repeats, notes'
    mark points merged, anything else kept from the first step that brought it."""
    if name not in into:
        into[name] = value
        return
    have = into[name]
    if isinstance(have, dict) and isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, list) and isinstance(have.get(k), list):
                have[k] = have[k] + [x for x in v if x not in have[k]]
            elif isinstance(v, dict) and isinstance(have.get(k), dict):
                have[k] = {**have[k], **v}
            else:
                have.setdefault(k, v)


def _mentions_exam(turn: Turn, settings: Settings) -> bool:
    """The message mentions an exam (blocks.exam_cues) or a command word used in the focus parts' questions."""
    words = set(re.findall(r"[a-z]+", turn.message.lower()))
    commands = {(q["command_word"] or "").lower() for q in graph.questions_for(turn.parts)} - {""}
    return bool(words & set(settings.blocks.exam_cues)) or bool(words & commands)


def reference_for(turn: Turn, steps: list[dict], profile_blocks: list[str], settings: Settings, context: ContextConfig) -> dict:
    """The reference the plan's moves use, in priority order: for each step in plan order, the blocks in its
    move's table (context.toml [moves.<key>]), narrowed to the step's part; misconceptions are the step part's
    held ones in full. Then exam_relevance when the message mentions an exam or a command word, and last the
    watch-for misconceptions of steps that ask something, as id and wrong_idea only. Blocks not in the
    profile are never sent. Returns {name: block}; watch-for misconceptions are under "watch_for"."""
    out: dict[str, object] = {}
    cache: dict[tuple[str, str | None], dict | None] = {}

    def block(name: str, part: str | None) -> dict | None:
        if (name, part) not in cache:
            fn = BLOCKS.get(name)
            cache[(name, part)] = fn(_part_turn(turn, part), settings) if fn and part else None
        return cache[(name, part)]

    for step in steps:
        part = step.get("part_id")
        for name in _move_table(context, step):
            if name not in profile_blocks:
                continue
            value = block(name, part)
            if name == "misconceptions":
                value = {"held": value["held"]} if value and value["held"] else None
            if value:
                _merge(out, name, {k: v for k, v in value.items()} if isinstance(value, dict) else value)
    if "exam_relevance" in profile_blocks and turn.parts and _mentions_exam(turn, settings):
        value = exam_relevance(turn, settings)
        if value:
            out["exam_relevance"] = value
    if "misconceptions" in profile_blocks:
        watch: list[dict] = []
        for step in steps:
            if step.get("part_id") and asks_watch_for(context, step):
                value = block("misconceptions", step["part_id"]) or {}
                watch += [
                    {"id": m["id"], "wrong_idea": m["wrong_idea"]}
                    for m in value.get("watch_for", [])
                    if m["id"] not in {w["id"] for w in watch}
                ]
        if watch:
            out["watch_for"] = watch
    return out


# --- known terms (step 05c) ------------------------------------------------------


def _linked_parts(part_id: str) -> set[str]:
    """Parts linked to a part by an edge of any type."""
    found: set[str] = set()
    for lookup in (graph.prerequisites, graph.dependents):
        for edge in lookup(part_id, 1):
            found.update(graph.parts_of(edge["other"]))
    for link_lookup in (graph.analogous, graph.confusables, graph.causal_out, graph.causal_in):
        for edge in link_lookup(part_id):
            found.update(graph.parts_of(edge["other"]))
    found.discard(part_id)
    return found


def known_terms(turn: Turn, part_ids: list[str], known: list[str]) -> list[str]:
    """The course terms a plan may use: the names and aliases of its steps' parts, then of the known parts
    (developing or above) linked to them by an edge, then of the other known parts by importance; at most
    limits.terms. known is the student's known parts, most important first."""
    linked = set().union(*(_linked_parts(p) for p in part_ids)) if part_ids else set()
    order = list(part_ids) + [p for p in known if p in linked] + [p for p in known if p not in linked]
    terms: list[str] = []
    for part in dict.fromkeys(order):
        node = graph.require_node(part)
        for term in [node["name"], *node["aliases"]]:
            if term and term not in terms:
                terms.append(term)
    return terms[: turn.limit("terms", 30)]


def known_parts(turn: Turn) -> list[str]:
    """Parts the student has at developing or above, most important first."""
    found = [p for p in learner.all_parts() if learner.level(turn.p(p)) != "new"]
    return sorted(found, key=lambda p: -graph.weight(p)["importance"])
