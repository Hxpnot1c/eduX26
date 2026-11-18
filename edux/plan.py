"""Choose the plan for one turn: at most three ordered steps for the chatbot to carry out, and nothing else.

Each step is {move, part_id, cue, data}. What each move means is in the server instructions, sent once
(server_instructions below); the cue is one line from text/moves/<key>.cue.md, so the move stays clear in a long chat. The plan is built from the context
blocks the student's profile produced this turn, so a profile without a block never triggers its move.
Steps in STOP end the plan, because the student needs to reply.

Order (first match wins for the main step):
  answer given    -> feedback, then reteach when points are missing (which ends the plan); after a multiple-choice
                     intuition answer, teaching; after a check, the next point (or the same point re-taught)
  question instead of the pending answer -> answer_brief, then reask the same question (fatigue and stuck first)
  fatigued        -> offer_choice: stop or quick questions (once a session; also replaces reteach's re-ask, as do
                     stuck moves)
  stuck on focus  -> ask_mcq on the weakest prerequisite (prereq, stuck) / reteach of the whole part (through the anchor)
  ambiguous focus -> ask_which (no focus at all: the top due review, as ask_mcq)
  just_show_me    -> show the current point, then its check (after show.max_per_part_session shows of the part this
                     session: a 2-option check on the point first); skip_point ("I know this") -> its check only;
                     a pick from offer_choice: quiz -> the current point's check, extend -> extend, stop -> nothing
  passive streak  -> offer_choice: quiz, extend or stop (engagement.passive_run passive messages in a row; once a
                     session, never when fatigued)
  intuition       -> ask_mcq (intuition), once per part
  weak prereq     -> ask_mcq (prereq) (level new, not checked this session)
  held misconc.   -> feedback with the held misconception (unless already corrected this session), then teaching
  otherwise       -> teaching: teach_point and ask_mcq (check) on the point reached; after the last point, or
                     for a secure part, explain_back of the whole part (a coasting student, passive or "just show
                     me" for engagement.low_share of recent messages: their weakest point only)
Every multiple-choice question is built, lettered and scored by the server (ask_mcq). Without an answer, or after
a complete explain-back, a plan with no stop step gets extend or one due review. feedback is the only move that
names misconceptions; reteach never repeats them.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re

from edux import graph, learner
from edux.context_blocks import Turn, core_idea, held_misconceptions, intuition_source, known_parts, known_terms
from edux.settings import TEXT_DIR, Settings, SettingsError, read_text

log = logging.getLogger(__name__)

STOP = {"reteach", "offer_choice", "ask_which", "ask_mcq", "explain_back", "reask"}
PICKS = ("quiz", "extend", "stop")   # ways on from offer_choice the student picks, sent back as this_message.choice
ASKS = {"reteach", "ask_mcq", "explain_back", "extend", "reask"}
MAX_STEPS = 3
# The answer.type the chatbot sends back for a step that asks something.
ANSWER_TYPE = {"ask_mcq": "mcq", "extend": "extend", "explain_back": "explain_back"}
LETTERS = "ABCDEFGHIJ"


# The data fields each move's cue can name as a {field} placeholder: (always present, sometimes present).
# A placeholder outside both is a startup error; one that is only sometimes present is a warning. Sections
# (text/moves/<key>.md) are sent once with no data, so they name fields as data.<field> and have no placeholders.
TEXT_FIELDS: dict[str, tuple[set[str], set[str]]] = {
    "answer_brief": (set(), set()),
    "ask_which": ({"candidates"}, set()),
    "ask_mcq_intuition": ({"purpose", "options", "answer_type"}, {"note", "via", "extra_option"}),
    "ask_mcq_check": ({"purpose", "options", "index", "answer_type"}, {"extra_option"}),
    "ask_mcq_prereq": ({"purpose", "options", "name", "for", "answer_type"}, {"note", "stuck", "extra_option"}),
    "ask_mcq_review": ({"purpose", "options", "name", "mode", "answer_type"}, {"new_context", "extra_option"}),
    "ask_mcq_how_ai_works": ({"purpose", "options", "answer_type"}, {"extra_option"}),
    "extend": ({"answer_type"}, set()),
    "feedback": ({"type", "misconceptions"}, {"correct", "correct_idea", "correct_option", "purpose", "points_met", "missing",
                                             "intuition", "secure"}),
    "offer_choice": ({"reason", "options"}, {"minutes", "quick_parts"}),
    "reask": ({"asked"}, {"answer_type", "skill"}),
    "reteach": (set(), {"missing", "anchor", "point", "level", "answer_type"}),
    "show": ({"point"}, {"note"}),
    "explain_back": ({"answer_type"}, set()),
    "explain_back_point": ({"answer_type", "point", "point_id"}, set()),
    "teach_point": ({"index", "total", "point", "exemplar", "level", "max_words"}, set()),
    "answer_with_sources": ({"trusted_sources"}, set()),
    "literacy_task": ({"skill", "level", "task", "features", "pattern"}, {"answer_type"}),
    "source_conflict": (set(), set()),
}
PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER.findall(text))


def fill(text: str, data: dict) -> str:
    """Fill {field} placeholders from the step's data; a field that is missing this time is left out."""
    def value(m: re.Match) -> str:
        v = data.get(m.group(1))
        if v is None:
            log.warning("move text placeholder {%s} has no value in this step's data", m.group(1))
            return ""
        return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return PLACEHOLDER.sub(value, text)


def move_keys() -> list[str]:
    """Every move key with a section text: text/moves/<key>.md (cue files aside)."""
    return sorted(f.name[:-3] for f in (TEXT_DIR / "moves").glob("*.md") if not f.name.endswith(".cue.md"))


def cue_keys() -> list[str]:
    """Every key with a cue: text/moves/<key>.cue.md. A key is a move, or a move plus its variant
    (ask_mcq_<purpose>), whose section is the move's."""
    return sorted(f.name[:-7] for f in (TEXT_DIR / "moves").glob("*.cue.md"))


def section_of(key: str) -> str | None:
    """The section a cue key belongs to: its own, else the longest move whose name it extends (<move>_<variant>)."""
    sections = move_keys()
    if key in sections:
        return key
    found = [m for m in sections if key.startswith(m + "_")]
    return max(found, key=len) if found else None


def _text(key: str) -> str:
    return read_text(f"moves/{key}.md").strip()


def _cue(key: str) -> str:
    return read_text(f"moves/{key}.cue.md").strip()


def _sentences(text: str) -> int:
    return len(re.findall(r"[.!?]\"?(?=\s|$)", text))


def check_texts(settings: Settings) -> list[str]:
    """Check the move texts at startup. Raises SettingsError for a section with a placeholder or a backticked
    data field (sections are sent once, with no data), a missing cue, or a cue placeholder the move never has
    data for. Returns warnings (also logged) for a cue placeholder the move only sometimes has, a section over
    instructions.max_sentences and a cue over instructions.cue_max_words."""
    limits = settings.instructions
    errors, warnings = [], []
    cues = cue_keys()
    for key in move_keys():
        mine = [c for c in cues if section_of(c) == key]
        fields = set().union(*(a | b for c in mine for a, b in [TEXT_FIELDS.get(c, (set(), set()))]))
        text = _text(key)
        if placeholders(text):
            errors.append(f"text/moves/{key}.md: sections are sent once, so use data.<field>, "
                          f"not {{{sorted(placeholders(text))[0]}}}")
        stray = sorted(set(re.findall(r"`([a-z_]+)`", text)) & fields)
        if stray:
            errors.append(f"text/moves/{key}.md: write data fields as data.<field>, not `{stray[0]}`")
        if _sentences(text) > limits.max_sentences:
            warnings.append(f"text/moves/{key}.md: {_sentences(text)} sentences, over {limits.max_sentences}")
        if not mine:
            errors.append(f"text/moves/{key}.cue.md (or {key}_<variant>.cue.md) is missing")
    for key in cues:
        if section_of(key) is None:
            errors.append(f"text/moves/{key}.cue.md has no section text/moves/<move>.md")
            continue
        always, sometimes = TEXT_FIELDS.get(key, (set(), set()))
        cue = _cue(key)
        if len(cue.split()) > limits.cue_max_words:
            warnings.append(f"text/moves/{key}.cue.md: {len(cue.split())} words, over {limits.cue_max_words}")
        for name in sorted(placeholders(cue)):
            if name in sometimes:
                warnings.append(f"text/moves/{key}.cue.md: {{{name}}} is only sometimes in the step's data")
            elif name not in always:
                errors.append(f"text/moves/{key}.cue.md: {{{name}}} is never in the step's data")
    for skill in LITERACY_SKILLS:
        for level in ("new", "developing", "secure"):
            if not (TEXT_DIR / "literacy" / f"{skill}_{level}.md").exists():
                errors.append(f"text/literacy/{skill}_{level}.md is missing")
    if errors:
        raise SettingsError("; ".join(errors))
    for w in warnings:
        log.warning(w)
    return warnings


def server_instructions(settings: Settings) -> str:
    """The MCP server instructions, sent once per chat: server_instructions.md, style.md, then one section per
    move ("## <key>" and its text). Over instructions.max_words is a SettingsError naming the longest sections."""
    check_texts(settings)
    sections = {key: f"## {key}\n{_text(key)}" for key in move_keys()}
    text = "\n\n".join([read_text("server_instructions.md").strip(), read_text("style.md").strip(), *sections.values()])
    words = len(text.split())
    if words > settings.instructions.max_words:
        longest = sorted(sections, key=lambda k: -len(sections[k].split()))[:3]
        raise SettingsError(f"server instructions are {words} words, over instructions.max_words "
                            f"({settings.instructions.max_words}); longest move sections: "
                            + ", ".join(f"{k} ({len(sections[k].split())})" for k in longest))
    return text


def _step(move: str, part_id: str | None, data: dict | None = None, key: str | None = None) -> dict:
    """A plan step. key is the cue's name (ask_mcq_<purpose>, review_<mode>, otherwise the
    move): its section is in the server instructions, and its one-line cue goes with the step, filled from
    data. The key stays in the saved plan; service.public_steps leaves it out of the result."""
    data = dict(data or {})
    if move in ANSWER_TYPE:
        data["answer_type"] = ANSWER_TYPE[move]
    key = key or move
    return {"move": move, "part_id": part_id, "key": key, "cue": fill(_cue(key), data), "data": data}


def _summary(turn: Turn, part_id: str) -> dict:
    node = graph.get_node(part_id)
    return {"id": part_id, "name": node["name"], "level": learner.level(turn.p(part_id))}


# --- multiple-choice questions (step 05d) ---------------------------------------------


def distractors(part_id: str, settings: Settings) -> list[dict]:
    """The wrong options for a question on a part: its misconceptions (examiner-report sources first), at most
    mcq.max_options - 1, as {id, text}."""
    found = graph.misconceptions_for([part_id])
    found.sort(key=lambda m: "examiner_report" not in graph.source_types(m["source_ids"]))
    return [{"id": m["id"], "text": m["wrong_idea"]} for m in found[:settings.mcq.max_options - 1]]


def question(part_id: str, purpose: str, correct: str, settings: Settings, point_id: str | None = None) -> dict:
    """What a multiple-choice question asks, before it is lettered: the correct option's text, the part's
    misconceptions as wrong options, and whether the chatbot may write one more (the part has fewer than
    mcq.min_distractors). Kept with a pending question so it can be asked again with new letters."""
    wrong = distractors(part_id, settings)
    return {"part_id": part_id, "purpose": purpose, "point_id": point_id, "correct": correct, "wrong": wrong,
            "extra": len(wrong) < settings.mcq.min_distractors}


def ask_mcq(turn: Turn, q: dict, data: dict | None = None, avoid: list[str] | None = None) -> dict:
    """The ask_mcq step for a question: its options shuffled by the server and lettered A, B, C..., with
    data.extra_option naming a letter the chatbot fills when the part has too few misconceptions. The shuffle
    differs per student and per asking, and never repeats avoid (the last order of the same question). The
    step keeps the question and the letter -> option map (mcq), which service saves with the plan and
    public_steps leaves out."""
    ids = ["correct"] + [w["id"] for w in q["wrong"]] + (["extra"] if q["extra"] else [])
    texts = {"correct": q["correct"], **{w["id"]: w["text"] for w in q["wrong"]}}
    rng = random.Random(hashlib.sha256(f"{turn.student_id}:{q['part_id']}:{q['purpose']}:{turn.at}".encode()).digest())
    shown = [i for i in avoid or [] if i != "extra"]
    for _ in range(20):   # a repeat must look different: compare the options the student sees
        rng.shuffle(ids)
        if len(shown) < 2 or [i for i in ids if i != "extra"] != shown:
            break
    letters = dict(zip(LETTERS, ids))
    out = {"purpose": q["purpose"], **(data or {}),
           "options": [{"letter": letter, "text": texts[i]} for letter, i in letters.items() if i != "extra"]}
    extra = next((letter for letter, i in letters.items() if i == "extra"), None)
    if extra:
        out["extra_option"] = extra
    step = _step("ask_mcq", q["part_id"], out, key=f"ask_mcq_{q['purpose']}")
    step["question"] = q
    step["mcq"] = {"part_id": q["part_id"], "purpose": q["purpose"], "point_id": q["point_id"],
                   "options": {letter: {"id": i, "text": texts.get(i, "")} for letter, i in letters.items()}}
    return step


def ask_again(turn: Turn, pending: dict) -> dict:
    """A pending multiple-choice question asked again with freshly shuffled options, in a different order
    from the one last shown (its map was lost, so the letter couldn't be scored)."""
    q, data = pending["question"], pending["data"]
    by_text = {q["correct"]: "correct", **{w["text"]: w["id"] for w in q["wrong"]}}
    shown = {o["letter"]: by_text.get(o["text"]) for o in data.get("options", [])}
    if data.get("extra_option"):
        shown[data["extra_option"]] = "extra"
    avoid = [shown[letter] for letter in sorted(shown)]
    keep = {k: v for k, v in data.items() if k not in ("options", "extra_option", "terms", "answer_type", "purpose")}
    return ask_mcq(turn, q, keep, avoid)


def is_stop(step: dict) -> bool:
    return step["move"] in STOP or (step["move"] == "literacy_task" and bool(step["data"].get("task")))


# --- feedback on the student's answer -----------------------------------------------


def _misconception(m: dict) -> dict:
    return {"id": m["id"], "wrong_idea": m["wrong_idea"], "correction": m["correction"]}


def _refill(step: dict) -> dict:
    """The step with its cue filled again after its data changed."""
    return {**step, "cue": fill(_cue(step["key"]), step["data"])}


def feedback(answer: dict, evidence: dict) -> tuple[dict, dict | None]:
    """The steps answering what the student just said: answer is what the chatbot sent, evidence the scored
    item. Returns (feedback, reteach): feedback names every misconception the answer picked or showed; reteach
    re-teaches the missing points (None when nothing is missing)."""
    part = evidence["part_id"]
    shown = [_misconception(m) for m in map(graph.get_misconception, evidence["misconception_ids"]) if m]
    if answer["type"] == "mcq":   # the picked misconception comes first in misconception_ids
        data = {"type": "mcq", "purpose": evidence["purpose"], "correct": evidence["correct"],
                "correct_option": evidence["correct_option"], "misconceptions": shown}
        if evidence["purpose"] == "how_ai_works":   # why chatbots do this, in one everyday line
            data["intuition"] = graph.get_node(part)["intuition"]
        return _step("feedback", part, data), None
    if answer["type"] == "prequestion":   # the picked option comes first in misconception_ids
        return _step("feedback", part, {"type": "prequestion", "correct": evidence["score"] == 1.0,
                                        "correct_idea": core_idea(part), "misconceptions": shown}), None
    points = graph.score_points(part)
    if evidence.get("scope"):   # an explain-back of one point is answered on that point only
        points = [p for p in points if p["id"] in evidence["scope"]]
    met = set(evidence.get("points_met") or [])
    first = _step("feedback", part, {"type": answer["type"], "points_met": [p["point"] for p in points if p["id"] in met],
                                     "misconceptions": shown})
    missing = [p["point"] for p in points if p["id"] not in met]
    if not missing:
        return first, None
    return first, _step("reteach", part, {"missing": missing, "answer_type": answer["type"]})


# --- the main step --------------------------------------------------------------------


def _checked_this_session(turn: Turn, part_id: str, last_plan: list[dict]) -> bool:
    """Evidence on the part in the current session, or the last plan already asked about it."""
    if any(s["move"] == "ask_mcq" and s["data"].get("purpose") == "prereq" and s["part_id"] == part_id for s in last_plan):
        return True
    session = learner.session_state(turn.student_id, turn.at)
    if session is None:
        return False
    return learner._conn().execute(
        "SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts >= ? AND ts <= ? LIMIT 1",
        (turn.student_id, part_id, session["session_id"], learner._event_ts(turn.at))).fetchone() is not None


def corrected_in(steps: list[dict]) -> set[str]:
    """Misconception ids a plan already corrected, in feedback (or, in plans saved before step 05c, by
    correct_misconception, a picked option or shown misconceptions)."""
    found: set[str] = set()
    for step in steps:
        data = step["data"]
        found |= {m["id"] for m in data.get("misconceptions") or []}
        if step["move"] == "correct_misconception":
            found.add(data["id"])
        if (data.get("picked") or {}).get("id"):
            found.add(data["picked"]["id"])
        found |= {m["id"] for m in data.get("shown_misconceptions") or []}
    return found


def main_step(turn: Turn, blocks: dict, settings: Settings, choice: str, last_plan: list[dict],
              handled: set[str], answered_prequestion: str | None, offered: frozenset[str] = frozenset(),
              progress: dict | None = None) -> list[dict]:
    """The steps of the first rule that matches, or [] when there is nothing to plan. Each offer_choice reason is
    offered once a session (offered holds those already made): if the student carries on, teaching goes on.
    progress is the point-by-point progress per part (step 05d), updated in place."""
    progress = {} if progress is None else progress
    session = blocks.get("session")
    focus = turn.parts[0] if turn.parts else None

    if session and session["state"] == "fatigued" and "fatigued" not in offered:
        quick = [{"id": p["id"], "name": p["name"], "level": p["level"]} for p in session["quick_parts"]]
        return [offer_choice("fatigued", ["stop"] + (["quick"] if quick else []),
                             {"minutes": session["minutes"], "quick_parts": quick})]

    if session and session["state"] == "stuck" and focus:
        stuck = next((p for p in session["parts"] if p["part_id"] == focus), None)
        if stuck:
            back = stuck["step_back_to"]
            if back:
                return [prereq_check(turn, back["id"], focus, settings, stuck=True)]
            anchor = blocks.get("anchor")
            return [_step("reteach", focus, {
                "anchor": {"id": anchor["part_id"], "name": anchor["name"], "note": anchor["note"]} if anchor else None,
                "answer_type": "explain_back"})]

    if focus is None:
        candidates = (blocks.get("focus") or {}).get("candidates")
        if candidates:
            return [_step("ask_which", None, {"candidates": [{k: c[k] for k in ("id", "name")} for c in candidates]})]
        review = _second_step(turn, blocks, settings, reviews_only=True)   # e.g. "quiz me on what's due"
        return [review] if review else []

    if choice in ("just_show_me", "skip_point"):
        return shown_or_skipped(turn, focus, settings, progress, choice)
    if choice in PICKS:
        return picked(turn, focus, settings, progress, choice)

    fatigued = bool(session and session["state"] == "fatigued")
    if ("passive" not in offered and not fatigued
            and learner.passive_streak(turn.student_id, turn.at) >= settings.engagement.passive_run):
        return [offer_choice("passive", ["quiz", "extend", "stop"])]

    pq = blocks.get("prequestion")
    asked_before = (progress.get(focus) or {}).get("intuition_asked") or any(
        s["move"] == "ask_mcq" and s["data"].get("purpose") == "intuition" and s["part_id"] == focus for s in last_plan)
    if pq and pq["part_id"] != answered_prequestion and not asked_before:
        return [ask_mcq(turn, question(pq["part_id"], "intuition", pq["correct"], settings), pq.get("source") or {})]

    for item in (blocks.get("weak_prerequisites") or {}).get("items", []):
        if item["level"] == "new" and not _checked_this_session(turn, item["part_id"], last_plan):
            return [prereq_check(turn, item["part_id"], item["for"], settings, note=item["note"])]

    teaching = teach(turn, focus, settings, progress)
    held = [m for m in held_misconceptions(turn.student_id, turn.parts) if m["id"] not in handled]
    if held:   # correct it, then carry on teaching
        m = held[0]
        return [_step("feedback", m["node_id"], {"type": "held", "misconceptions": [_misconception(m)]})] + teaching
    return teaching


# --- point by point (step 05d) ----------------------------------------------------


def _points(part_id: str) -> list[dict]:
    """The points a part is taught in: its score points, or its description as one point when it has none."""
    return graph.score_points(part_id) or [{"id": None, "point": graph.get_node(part_id)["description"], "exemplar": ""}]


def _progress(progress: dict, part_id: str) -> dict:
    return progress.setdefault(part_id, {"index": 1, "reteaches": 0, "intuition_asked": False})


def check(turn: Turn, part_id: str, index: int, settings: Settings, avoid: list[str] | None = None) -> dict:
    """ask_mcq (check) on one point of a part: the point's wording is the correct option."""
    point = _points(part_id)[index - 1]
    return ask_mcq(turn, question(part_id, "check", point["point"], settings, point_id=point["id"]),
                   {"index": index}, avoid)


def teach(turn: Turn, part_id: str, settings: Settings, progress: dict) -> list[dict]:
    """Teaching on a part. At worked_example or hint: the point it has reached, as teach_point and an ask_mcq
    check on it. After the last point, or for a part already at explain_back level (secure), explain_back of
    the whole part, which joins the points together, is scored on all of them and ends the part's progress.
    A point whose check was left out last reply (check_due: a how-AI-works check or a literacy re-ask took its
    slot) gets its check only."""
    level = learner.support_level(turn.p(part_id))
    points = _points(part_id)
    state = _progress(progress, part_id)
    if state.pop("check_due", False) and state["index"] <= len(points):   # taught, but its check was replaced
        return [check(turn, part_id, state["index"], settings)]
    if level == "explain_back" or state["index"] > len(points):
        progress.pop(part_id, None)
        return [explain_back(turn, part_id, points, settings)]
    point = points[state["index"] - 1]
    return [_step("teach_point", part_id, {"index": state["index"], "total": len(points), "point": point["point"],
                                           "exemplar": point["exemplar"], "level": level,
                                           "max_words": settings.points.max_words}),
            check(turn, part_id, state["index"], settings)]


def offer_choice(reason: str, options: list[str], data: dict | None = None) -> dict:
    """offer_choice (stop): the ways on in options, from stop, quick (questions on data.quick_parts), quiz and
    extend. reason is fatigued or passive; each is offered once a session."""
    return _step("offer_choice", None, {"reason": reason, "options": options, **(data or {})})


def picked(turn: Turn, part_id: str, settings: Settings, progress: dict, choice: str) -> list[dict]:
    """The way on the student picked from offer_choice: quiz, the current point's check (as "I know this");
    extend, a harder question on the part; stop, nothing (the chatbot wraps up with a one-line summary)."""
    if choice == "quiz":
        return shown_or_skipped(turn, part_id, settings, progress, "skip_point")
    if choice == "extend":
        return [_step("extend", part_id)]
    return []


def two_option_check(turn: Turn, part_id: str, index: int, settings: Settings) -> dict:
    """ask_mcq (check) on one point with two options: the point and the part's first misconception (or one the
    chatbot writes, when it has none). Asked before a repeated show; its guess is 1/2 (bkt.mcq_guess_from_options)."""
    point = _points(part_id)[index - 1]
    q = question(part_id, "check", point["point"], settings, point_id=point["id"])
    q = {**q, "wrong": q["wrong"][:1], "extra": not q["wrong"]}
    return ask_mcq(turn, q, {"index": index})


def explain_back(turn: Turn, part_id: str, points: list[dict], settings: Settings) -> dict:
    """explain_back of the whole part; for a coasting student (passive or "just show me" for at least
    engagement.low_share of their recent messages), of their weakest point only, scored on that point."""
    ids = [p["id"] for p in points if p["id"]]
    share = learner.coasting_share(turn.student_id, turn.at)
    if len(ids) < 2 or share is None or share < settings.engagement.low_share:
        return _step("explain_back", part_id)
    weakest = learner.weakest_point(turn.student_id, part_id, ids)
    point = next(p for p in points if p["id"] == weakest)
    return _step("explain_back", part_id, {"point": point["point"], "point_id": weakest}, key="explain_back_point")


def shown_or_skipped(turn: Turn, part_id: str, settings: Settings, progress: dict, choice: str) -> list[dict]:
    """"I know this" (skip_point): the current point's check only, with no teaching. "Just show me": show, a
    one-line intuition (from the same source as the intuition question) and the point, then its check; after
    show.max_per_part_session shows of the part this session, a 2-option check first instead, whose feedback
    gives the point."""
    state = _progress(progress, part_id)
    points = _points(part_id)
    index = min(state["index"], len(points))
    asked = check(turn, part_id, index, settings)
    if choice == "skip_point":
        return [asked]
    if learner.shows_this_session(turn.student_id, part_id, turn.at) > settings.show.max_per_part_session:
        return [two_option_check(turn, part_id, index, settings)]   # try it first: the answer's feedback shows the point
    data = {"point": points[index - 1]["point"]}
    source = intuition_source(turn, part_id)
    if source:
        data["note"] = source["note"]
    return [_step("show", part_id, data), asked]


def after_check(turn: Turn, evidence: dict, settings: Settings, progress: dict, last_mcq: dict | None) -> list[dict]:
    """What follows an answered check: right, the next point (or the explain-back after the last); wrong, a
    re-teach of the same point a different way in and the check again, freshly shuffled, at most
    points.reteach_limit times before moving on."""
    part = evidence["part_id"]
    state = _progress(progress, part)
    points = _points(part)
    if not evidence["correct"] and state["reteaches"] < settings.points.reteach_limit:
        state["reteaches"] += 1
        point = points[min(state["index"], len(points)) - 1]
        avoid = [o["id"] for _, o in sorted((last_mcq or {}).get("options", {}).items())] or None
        return [_step("reteach", part, {"point": point["point"], "level": learner.support_level(turn.p(part))}),
                check(turn, part, min(state["index"], len(points)), settings, avoid)]
    state["index"] += 1
    state["reteaches"] = 0
    return teach(turn, part, settings, progress)


def prereq_check(turn: Turn, part_id: str, for_part: str, settings: Settings, note: str = "", stuck: bool = False) -> dict:
    """ask_mcq (prereq) on a weak prerequisite: its first point is the correct option. stuck marks a step back
    from a part they're stuck on, so the chatbot says it is trying a different way in."""
    data = {"name": graph.get_node(part_id)["name"], "for": for_part}
    if note:
        data["note"] = note
    if stuck:
        data["stuck"] = True
    return ask_mcq(turn, question(part_id, "prereq", _points(part_id)[0]["point"], settings,
                                  point_id=_points(part_id)[0]["id"]), data)


def review_check(turn: Turn, r: dict, settings: Settings) -> dict:
    """ask_mcq (review) on a due part, in its mode (recall, or transfer framed in data.new_context). The correct
    option rotates through the part's points: the point at (its evidence count) mod (its number of points)."""
    points = _points(r["part_id"])
    row = learner._conn().execute("SELECT n_evidence FROM part_state WHERE student_id = ? AND part_id = ?",
                                  (turn.student_id, r["part_id"])).fetchone()
    point = points[(row["n_evidence"] if row else 0) % len(points)]
    data = {"name": r["name"], "mode": r["mode"]}
    if r.get("new_context"):
        data["new_context"] = r["new_context"]
    return ask_mcq(turn, question(r["part_id"], "review", point["point"], settings, point_id=point["id"]), data)


def _second_step(turn: Turn, blocks: dict, settings: Settings, reviews_only: bool = False) -> dict | None:
    """extend when earned, otherwise the top due review (not on a focus part) as an MCQ, otherwise nothing."""
    support = blocks.get("support")
    if support and support.get("extend") and not reviews_only:
        return _step("extend", support["part_id"])
    reviews = [r for r in (blocks.get("reviews_due") or {}).get("items") or [] if r["part_id"] not in turn.parts]
    return review_check(turn, reviews[0], settings) if reviews else None


# --- the plan -----------------------------------------------------------------------


def add_terms(turn: Turn, steps: list[dict]) -> list[dict]:
    """Give the plan's first step on a part (every step that teaches or asks is on a part) data.terms: the course
    terms the student knows (context_blocks.known_terms), the steps' own parts first, so the chatbot doesn't
    introduce others. The list is sent once per plan, which keeps the result within its budget."""
    for step in steps:
        step["data"].pop("terms", None)
    parts = list(dict.fromkeys(s["part_id"] for s in steps if s["part_id"] and not graph.is_literacy(s["part_id"])))
    if parts:
        first = next(s for s in steps if s["part_id"] in parts)
        first["data"]["terms"] = known_terms(turn, parts, known_parts(turn))
    return steps


def asking_step(steps: list[dict]) -> dict | None:
    """The step in a plan that asks the student something they should answer (it carries data.answer_type)."""
    return next((s for s in reversed(steps) if "answer_type" in s["data"]), None)


def reask(pending: dict) -> list[dict]:
    """answer_brief, then the pending question again with the same data (so the same answer_type and score_next;
    a multiple-choice question keeps its options and letter map)."""
    data = {"asked": pending["move"], **{k: v for k, v in pending["data"].items() if k != "terms"}}
    return [_step("answer_brief", pending["part_id"]), {**_step("reask", pending["part_id"], data)}]


def _urgent(steps: list[dict]) -> bool:
    """Fatigue, stuck or a passive streak: offer_choice, a step back to a prerequisite (ask_mcq with data.stuck) or
    a re-teach of the whole part. These come before a pending question, a re-teach of missing points and the point
    loop (a passive student who keeps leaving a question unanswered is offered ways on, not asked it again)."""
    return bool(steps) and (steps[0]["move"] in ("reteach", "offer_choice") or bool(steps[0]["data"].get("stuck")))


def choose(turn: Turn, blocks: dict, settings: Settings, choice: str = "none", answer: dict | None = None,
           evidence: dict | None = None, last_plan: list[dict] | None = None,
           corrected: set[str] | None = None, offered: frozenset[str] = frozenset(), pending: dict | None = None,
           progress: dict | None = None, last_mcq: dict | None = None) -> list[dict]:
    """The plan for this turn (see the module docstring). answer is what the chatbot sent about the student's
    answer and evidence its scored item; last_plan is the plan issued on the previous turn; corrected holds the
    misconceptions already corrected this session, which aren't corrected again; offered holds the offer_choice
    reasons already offered this session; pending is the question still waiting for an answer, when this
    message asked something instead (on the same part, or with no new focus). progress is the point-by-point
    progress per part, updated in place; last_mcq the last question's letter map, so a repeat is reshuffled."""
    last_plan = last_plan or []
    progress = {} if progress is None else progress
    steps: list[dict] = []
    handled: set[str] = set(corrected or ()) | corrected_in(last_plan)
    answered_prequestion = None

    def main() -> list[dict]:
        return main_step(turn, blocks, settings, choice, last_plan, handled, answered_prequestion, offered, progress)

    if pending and not answer:
        urgent = main()
        return urgent if _urgent(urgent) else reask(pending)
    if answer and evidence:
        first, retry = feedback(answer, evidence)
        if evidence["score"] >= settings.bkt.correct_share and learner.level(turn.p(evidence["part_id"])) == "secure":
            first = _refill({**first, "data": {**first["data"], "secure": True}})   # right at secure: confirm, no why
        steps.append(first)
        handled |= set(evidence["misconception_ids"])
        if answer["type"] == "prequestion" or evidence.get("purpose") == "intuition":
            answered_prequestion = evidence["part_id"]
            _progress(progress, evidence["part_id"])["intuition_asked"] = True
        if retry:   # reteach ends the plan, unless they're tired or stuck: then say what's missing and do that instead
            urgent = main()
            if _urgent(urgent):
                return [_refill({**first, "data": {**first["data"], "missing": retry["data"]["missing"]}}), urgent[0]]
            return [first, retry]
    rest = main()
    # all points met on an explain-back or a harder question (a retry returned above): the part is done for now
    finished = bool(answer and evidence and answer["type"] in ("explain_back", "extend"))
    if not _urgent(rest):
        if rest and rest[0]["move"] == "feedback" and steps:   # a held misconception joins the answer's feedback
            known = {m["id"] for m in steps[0]["data"]["misconceptions"]}
            extra = [m for m in rest[0]["data"]["misconceptions"] if m["id"] not in known]
            steps[0] = _refill({**steps[0], "data": {**steps[0]["data"],
                                                     "misconceptions": steps[0]["data"]["misconceptions"] + extra}})
            rest = rest[1:]
        if evidence and evidence.get("purpose") == "intuition":   # whatever the answer, teaching starts
            rest = teach(turn, evidence["part_id"], settings, progress)
        elif evidence and evidence.get("purpose") == "how_ai_works" and not turn.parts:
            rest = []   # back to what they were doing: with no course focus, nothing more
        elif evidence and evidence.get("purpose") == "check":
            rest = after_check(turn, evidence, settings, progress, last_mcq)
        elif finished:   # the part is done for now: extend or a due review instead of teaching it again
            rest = []
    steps += rest
    if (not answer or finished) and steps and not any(is_stop(s) for s in steps) and steps[-1]["move"] != "show":
        second = _second_step(turn, blocks, settings)
        if second:
            steps.append(second)
    return steps[:MAX_STEPS]


# --- research questions (step 05e) ------------------------------------------------------


LITERACY_SKILLS = ("ask", "verify")


def literacy_pattern(skill: str, level: str) -> str:
    """The feedback and task pattern for a skill at a level: text/literacy/<skill>_<level>.md."""
    return read_text(f"literacy/{skill}_{level}.md").strip()


def literacy_task(turn: Turn, blocks: dict, settings: Settings, features: list[str]) -> dict | None:
    """One feedback line on an AI-literacy skill and, usually, one task to do now. The skill is Ask when the
    question shows fewer than literacy.ask_min_features features, otherwise Verify; data.level is that skill's
    level. At secure there is a task only every literacy.secure_every research questions (the rest get the
    feedback line only). None while the student is fatigued. A verify task is answered as ail_task."""
    if (blocks.get("session") or {}).get("state") == "fatigued":
        return None
    ask = len(set(features)) < settings.literacy.ask_min_features
    part = learner.AIL_ASK if ask else learner.AIL_VERIFY
    level = learner.level(turn.p(part))
    task = level != "secure" or learner.research_turns(turn.student_id, turn.at) % settings.literacy.secure_every == 0
    skill = "ask" if ask else "verify"
    data = {"skill": skill, "level": level, "task": task, "features": sorted(set(features)),
            "pattern": literacy_pattern(skill, level)}
    if task and not ask:
        data["answer_type"] = "ail_task"
    return _step("literacy_task", part, data)


def research(turn: Turn, blocks: dict, settings: Settings, features: list[str]) -> list[dict]:
    """A research question (a factual or current question about the world): answer_with_sources, never withheld,
    with the pack's trusted sources for the focus and its topic, then literacy_task."""
    near = turn.parts or [c["id"] for c in turn.resolution.get("candidates") or []]
    sources = graph.trusted_sources(near, turn.limits.get("trusted_sources", 3))
    task = literacy_task(turn, blocks, settings, features)
    return [_step("answer_with_sources", None, {"trusted_sources": sources})] + ([task] if task else [])


def literacy_reask(task: dict) -> dict:
    """reask of a pending literacy task, in one line (data.asked is literacy_task)."""
    data = {"asked": "literacy_task", "skill": task["skill"]}
    if task["skill"] == "verify":
        data["answer_type"] = "ail_task"
    return _step("reask", task["part_id"], data)


def with_source_conflict(steps: list[dict]) -> list[dict]:
    """source_conflict first (the student found a link that failed or didn't say what was claimed), keeping the
    end of the plan, where its question is."""
    return [_step("source_conflict", None)] + steps[-(MAX_STEPS - 1):]


# --- how-AI-works checks (step 05e) -----------------------------------------------------

# (part, does this turn's labels trigger it, the same trigger as a condition on exchange_log), in priority order
HOW_TRIGGERS = (
    ("ail_how_fabrication", lambda m: bool(m.get("source_conflict")), "source_conflict = 1"),
    ("ail_how_agreement", lambda m: bool(m.get("pushback_changed")), "pushback_changed = 1"),
    ("ail_how_confidence", lambda m: bool(m.get("conflict_flagged")) and not m.get("source_conflict"),
     "conflict_flagged = 1 AND source_conflict = 0"),
    ("ail_how_cutoff", lambda m: m.get("request_type") == "research" and bool(m.get("asks_recent"))
     and m.get("web_access") is False, "request_type = 'research' AND asks_recent = 1 AND web_access = 0"),
)


def how_check(turn: Turn, part_id: str, settings: Settings) -> dict:
    """ask_mcq (how_ai_works) on a how-AI-works part: its point and its misconceptions, shuffled and lettered."""
    point = _points(part_id)[0]
    return ask_mcq(turn, question(part_id, "how_ai_works", point["point"], settings, point_id=point["id"]))


def with_check(steps: list[dict], check: dict) -> list[dict]:
    """The plan with a how-AI-works check (or its re-ask) as the last step. The check wins: the plan's own question
    and any literacy task are left out, and the steps handling the moment are kept, within the step limit."""
    keep = [s for s in steps if not is_stop(s) and s["move"] != "literacy_task"]
    return keep[:MAX_STEPS - 1] + [check]


def lettered(part_id: str) -> list[dict]:
    """A part's score points as the chatbot sees them: {id: a, b, c..., point}, in point order."""
    return [{"id": graph.point_letter(i), "point": p["point"]} for i, p in enumerate(graph.score_points(part_id))]


def score_next(plan: list[dict]) -> dict[str, list[dict]]:
    """For each part a step asks about (a multiple-choice question is answered by letter, so it has none): the points to
    tick in the student's next answer, lettered a, b, c... in point order. A letter is resolved from the
    course content when the answer comes back, so no mapping is saved."""
    out: dict[str, list[dict]] = {}
    for step in plan:
        if step["move"] == "offer_choice":   # the short burst of quick questions, if they choose it
            for part in step["data"].get("quick_parts") or []:
                points = lettered(part["id"])
                if points:
                    out.setdefault(part["id"], points)
        by_option = step["move"] == "ask_mcq" or step["data"].get("asked") in ("ask_mcq", "prequestion")
        if step["part_id"] == learner.AIL_ASK:   # an ask task is done by asking a research question, not ticked
            continue
        if step["move"] in ASKS and not by_option and step["part_id"] and step["part_id"] not in out:
            points = lettered(step["part_id"])
            if step["data"].get("point_id") and step["move"] == "explain_back":   # one point: its own letter only
                ids = [p["id"] for p in graph.score_points(step["part_id"])]
                points = [points[ids.index(step["data"]["point_id"])]] if step["data"]["point_id"] in ids else points
            if points:
                out[step["part_id"]] = points
    return out
