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
                     stuck moves). In rushing mode it waits while "how sure are you?" is asked, and until a later
                     answer is a rapid guess again (session.hold_offer, decision 0027)
  stuck on focus  -> ask_mcq on the weakest prerequisite (prereq, stuck) / reteach of the whole part (through the anchor);
                     each later miss on it that session climbs the stuck ladder (stuck_ladder): a worked example and
                     its check, an easier prerequisite check, an offer to stop or switch, then worked examples
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
from collections.abc import Sequence
from typing import Any

from edux import graph, learner
from edux.context_blocks import Turn, _quick_parts, core_idea, held_misconceptions, intuition_source, known_parts, known_terms, link_weight
from edux.settings import TEXT_DIR, Settings, SettingsError, read_text

log = logging.getLogger(__name__)

STOP = {
    "reteach",
    "offer_choice",
    "ask_which",
    "ask_mcq",
    "explain_back",
    "reask",
    "session_summary",
    "extend",
    "say_line",
}  # each ends in a question or the end of the chat
PICKS = ("quiz", "extend", "stop")  # ways on from offer_choice the student picks, sent back as this_message.choice
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
    "say_line_confidence": ({"line"}, set()),
    "say_line_find_error": ({"line", "answer_type"}, set()),
    "ask_mcq_intuition": ({"purpose", "options", "answer_type"}, {"note", "via", "extra_option"}),
    "ask_mcq_check": ({"purpose", "options", "index", "answer_type"}, {"extra_option"}),
    "ask_mcq_prereq": ({"purpose", "options", "name", "for", "answer_type"}, {"note", "stuck", "extra_option"}),
    "ask_mcq_review": ({"purpose", "options", "name", "mode", "answer_type"}, {"new_context", "extra_option"}),
    "ask_mcq_review_reason": ({"purpose", "options", "name", "mode", "reason", "answer_type"}, {"new_context", "extra_option"}),
    "ask_mcq_how_ai_works": ({"purpose", "options", "answer_type"}, {"extra_option"}),
    "ask_mcq_prequestion_bridge": ({"purpose", "options", "name", "answer_type"}, {"extra_option"}),
    "ask_mcq_prequestion_bridge_reason": ({"purpose", "options", "name", "reason", "answer_type"}, {"extra_option"}),
    "extend": ({"answer_type"}, set()),
    "feedback": (
        {"type", "misconceptions"},
        {"correct", "correct_idea", "correct_option", "purpose", "points_met", "missing", "intuition", "secure"},
    ),
    "offer_choice": ({"reason", "options"}, {"minutes", "quick_parts", "line"}),
    "session_summary": ({"covered"}, {"next_review"}),
    "reask": ({"asked"}, {"answer_type", "skill"}),
    "reteach": (set(), {"missing", "anchor", "point", "level", "answer_type"}),
    "show": ({"point"}, {"note"}),
    "show_stuck": ({"point"}, {"note", "stuck"}),
    "offer_choice_stuck": ({"reason", "options"}, {"minutes", "quick_parts"}),
    "explain_back": ({"answer_type"}, set()),
    "explain_back_point": ({"answer_type", "point", "point_id"}, set()),
    "explain_back_check": ({"answer_type", "point", "point_id", "purpose"}, {"index", "name", "for", "note", "stuck", "then_show"}),
    "explain_back_review": ({"answer_type", "point", "point_id", "purpose", "name", "mode"}, {"new_context", "reason"}),
    "teach_point": ({"index", "total", "point", "exemplar", "level", "max_words"}, set()),
    "teach_point_bridge": ({"index", "total", "point", "exemplar", "level", "max_words"}, {"can_stop"}),
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
            errors.append(f"text/moves/{key}.md: sections are sent once, so use data.<field>, not {{{sorted(placeholders(text))[0]}}}")
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
        raise SettingsError(
            f"server instructions are {words} words, over instructions.max_words "
            f"({settings.instructions.max_words}); longest move sections: "
            + ", ".join(f"{k} ({len(sections[k].split())})" for k in longest)
        )
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
    node = graph.require_node(part_id)
    return {"id": part_id, "name": node["name"], "level": learner.shown_level(turn.student_id, part_id, turn.at)}


# --- multiple-choice questions (step 05d) ---------------------------------------------


def distractors(part_id: str, settings: Settings) -> list[dict]:
    """The wrong options for a question on a part: its misconceptions (examiner-report sources first), at most
    mcq.max_options - 1, as {id, text}."""
    found = graph.misconceptions_for([part_id])
    found.sort(key=lambda m: "examiner_report" not in graph.source_types(m["source_ids"]))
    return [{"id": m["id"], "text": m["wrong_idea"]} for m in found[: settings.mcq.max_options - 1]]


def option_form(text: str) -> str:
    """An option as shown: trimmed, with no closing full stop, so the key can't be told apart by punctuation."""
    return text.strip().rstrip(".;!").rstrip()


def mcq_points(part_id: str) -> list[dict]:
    """The points a part's MCQs may use as the correct option: its own mark points only. Note key points, key
    wording and the description are never options (they are fragments or topic labels, so the key would stand
    out); a part without mark points gets open checks instead (open_check), and ingest warns about it."""
    return [
        {"id": mp["id"], "point": mp["point"], "exemplar": mp["exemplar"] or ""}
        for mp in graph.mark_points_for([part_id])
        if mp["node_id"] == part_id
    ]


def question(part_id: str, purpose: str, correct: str, settings: Settings, point_id: str | None = None) -> dict:
    """What a multiple-choice question asks, before it is lettered: the correct option's text, the part's
    misconceptions as wrong options, and whether the chatbot may write one more (the part has fewer than
    mcq.min_distractors). Kept with a pending question so it can be asked again with new letters. Every option
    is in option_form."""
    wrong = [{**w, "text": option_form(w["text"])} for w in distractors(part_id, settings)]
    return {
        "part_id": part_id,
        "purpose": purpose,
        "point_id": point_id,
        "correct": option_form(correct),
        "wrong": wrong,
        "extra": len(wrong) < settings.mcq.min_distractors,
    }


def ask_mcq(turn: Turn, q: dict, data: dict | None = None, avoid: Sequence[str | None] | None = None) -> dict:
    """The ask_mcq step for a question: its options shuffled by the server and lettered A, B, C..., with
    data.extra_option naming a letter the chatbot fills when the part has too few misconceptions. The shuffle
    differs per student and per asking, and never repeats avoid (the last order of the same question). The
    step keeps the question and the letter -> option map (mcq), which service saves with the plan and
    public_steps leaves out."""
    ids = ["correct"] + [w["id"] for w in q["wrong"]] + (["extra"] if q["extra"] else [])
    texts = {"correct": q["correct"], **{w["id"]: w["text"] for w in q["wrong"]}}
    rng = random.Random(hashlib.sha256(f"{turn.student_id}:{q['part_id']}:{q['purpose']}:{turn.at}".encode()).digest())
    shown = [i for i in avoid or [] if i != "extra"]
    for _ in range(20):  # a repeat must look different: compare the options the student sees
        rng.shuffle(ids)
        if len(shown) < 2 or [i for i in ids if i != "extra"] != shown:
            break
    letters = dict(zip(LETTERS, ids))
    out = {
        "purpose": q["purpose"],
        **(data or {}),
        "options": [{"letter": letter, "text": texts[i]} for letter, i in letters.items() if i != "extra"],
    }
    extra = next((letter for letter, i in letters.items() if i == "extra"), None)
    if extra:
        out["extra_option"] = extra
    step = _step("ask_mcq", q["part_id"], out, key=f"ask_mcq_{q['purpose']}")
    step["question"] = q
    step["mcq"] = {
        "part_id": q["part_id"],
        "purpose": q["purpose"],
        "point_id": q["point_id"],
        "options": {letter: {"id": i, "text": texts.get(i, "")} for letter, i in letters.items()},
    }
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


# --- question mix (decision 0028) ------------------------------------------------------

OPEN_KEYS = {"check": "explain_back_check", "prereq": "explain_back_check", "review": "explain_back_review"}
NO_OPEN_FORM = ("intuition", "how_ai_works")  # guesses before teaching and how-AI-works checks only work as multiple choice


def open_instead(turn: Turn, steps: list[dict]) -> list[dict]:
    """While a multiple-choice question is not allowed (turn.mcq_ok false: fewer than questions.min_open_between_mcq
    open questions since the last one, and the student not fatigued), each check, prerequisite check and review MCQ
    becomes an open question on the same point (explain_back with data.point, scored on that point only), keeping its
    purpose and data; an intuition or how-AI-works MCQ, which has no open form, is dropped."""
    if turn.mcq_ok:
        return steps
    out = []
    for step in steps:
        purpose = step["data"].get("purpose") if step["move"] == "ask_mcq" else None
        if purpose in NO_OPEN_FORM:
            continue
        out.append(open_question(step) if purpose in OPEN_KEYS else step)
    return out


def open_question(step: dict) -> dict:
    """The open form of a check, prerequisite or review MCQ step: the same part, point and purpose, as an explain-back
    of that point (a review's answer is typed review)."""
    data, part = step["data"], step["part_id"]
    point_id = (step.get("question") or {}).get("point_id")
    point = next((p for p in _points(part) if p["id"] == point_id), None) if point_id else None
    if point is None:  # no single point to ask about: the whole part
        return _step("explain_back", part)
    keep = {k: v for k, v in data.items() if k not in ("options", "extra_option", "answer_type", "terms")}
    out = _step("explain_back", part, {**keep, "point": point["point"], "point_id": point_id}, key=OPEN_KEYS[data["purpose"]])
    if data["purpose"] == "review":
        out["data"]["answer_type"] = "review"
        out = _refill(out)
    return out


def counts_as(step: dict | None) -> str | None:
    """What a plan's asking step counts as for the question mix: mcq, open, or None (a re-ask of the same question, a
    choice of ways on, a literacy task, or nothing asked)."""
    if step is None or step["move"] == "reask":
        return None
    if step["move"] == "ask_mcq":  # a how-AI-works check counts too
        return "mcq"
    if graph.is_literacy(step["part_id"] or ""):
        return None
    return "open" if step["data"].get("answer_type") and step["move"] != "offer_choice" else None


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
    if answer["type"] == "mcq":  # the picked misconception comes first in misconception_ids
        data = {
            "type": "mcq",
            "purpose": evidence["purpose"],
            "correct": evidence["correct"],
            "correct_option": evidence["correct_option"],
            "misconceptions": shown,
        }
        if evidence["purpose"] == "how_ai_works":  # why chatbots do this, in one everyday line
            data["intuition"] = graph.require_node(part)["intuition"]
        return _step("feedback", part, data), None
    if answer["type"] == "find_error":  # always show the correct statement afterwards; never leave the planted error standing
        wrong = graph.get_misconception(evidence["shown_misconception"]) if evidence.get("shown_misconception") else None
        return _step(
            "feedback",
            part,
            {
                "type": "find_error",
                "purpose": "find_error",
                "correct": evidence["hit"],
                "correct_option": evidence["correct_option"],
                "misconceptions": [_misconception(wrong)] if wrong else [],
            },
        ), None
    if answer["type"] == "prequestion":  # the picked option comes first in misconception_ids
        return _step(
            "feedback",
            part,
            {"type": "prequestion", "correct": evidence["score"] == 1.0, "correct_idea": core_idea(part), "misconceptions": shown},
        ), None
    points = graph.score_points(part)
    if evidence.get("scope"):  # an explain-back of one point is answered on that point only
        points = [p for p in points if p["id"] in evidence["scope"]]
    met = set(evidence.get("points_met") or [])
    first = _step(
        "feedback", part, {"type": answer["type"], "points_met": [p["point"] for p in points if p["id"] in met], "misconceptions": shown}
    )
    missing = [p["point"] for p in points if p["id"] not in met]
    if evidence.get("open_check"):  # an open check, review or prerequisite question goes on as its MCQ would (decision 0028)
        data = {**first["data"], "purpose": evidence["purpose"], "correct": evidence["correct"]}
        return _refill({**first, "data": {**data, "missing": missing} if missing else data}), None
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
    return (
        learner._conn()
        .execute(
            "SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts >= ? AND ts <= ? LIMIT 1",
            (turn.student_id, part_id, session["session_id"], learner._event_ts(turn.at)),
        )
        .fetchone()
        is not None
    )


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


def main_step(
    turn: Turn,
    blocks: dict,
    settings: Settings,
    choice: str,
    last_plan: list[dict],
    handled: set[str],
    answered_prequestion: str | None,
    offered: frozenset[str] = frozenset(),
    progress: dict | None = None,
) -> list[dict]:
    """The steps of the first rule that matches, or [] when there is nothing to plan. Each offer_choice reason is
    offered once a session (offered holds those already made): if the student carries on, teaching goes on.
    progress is the point-by-point progress per part (step 05d), updated in place."""
    progress = {} if progress is None else progress
    session = blocks.get("session")
    focus = turn.parts[0] if turn.parts else None

    if session and session["state"] == "fatigued" and "fatigued" not in offered and not session.get("hold_offer"):
        quick = [{"id": p["id"], "name": p["name"], "level": p["level"]} for p in session["quick_parts"]]
        line = read_text(f"fatigue/{session['reason']}.md").strip().format(minutes=session["minutes"])
        return [
            offer_choice(
                "fatigued", ["stop"] + (["quick"] if quick else []), {"minutes": session["minutes"], "quick_parts": quick, "line": line}
            )
        ]

    if session and session["state"] == "stuck" and focus:
        stuck = next((p for p in session["parts"] if p["part_id"] == focus), None)
        # the step back (or whole-part reteach) comes once per stuck part a session; then teaching carries on.
        # Kept under its own key: a part's own progress is dropped when its explain_back is asked.
        stuck_done: Any = progress.setdefault("_stuck_handled", {})
        session_id = (learner.session_state(turn.student_id, turn.at) or {}).get("session_id") if stuck else None
        if stuck and stuck_done.get(focus) != session_id:
            stuck_done[focus] = session_id
            progress.pop("_misses", None)  # the stuck ladder counts misses from this step back on
            back = stuck["step_back_to"]
            stepped = prereq_check(turn, back["id"], focus, settings, stuck=True) if back else None
            if stepped:
                return [stepped]
            anchor = blocks.get("anchor")
            return [
                _step(
                    "reteach",
                    focus,
                    {
                        "anchor": {"id": anchor["part_id"], "name": anchor["name"], "note": anchor["note"]} if anchor else None,
                        "answer_type": "explain_back",
                    },
                )
            ]

    if focus is None:
        candidates = (blocks.get("focus") or {}).get("candidates")
        if candidates:
            return [_step("ask_which", None, {"candidates": [{k: c[k] for k in ("id", "name")} for c in candidates]})]
        review = _second_step(turn, blocks, settings, reviews_only=True)  # e.g. "quiz me on what's due"
        return [review] if review else []

    if choice in ("just_show_me", "skip_point"):
        return shown_or_skipped(turn, focus, settings, progress, choice, blocks)
    if choice in PICKS:
        return picked(turn, focus, settings, progress, choice)

    fatigued = bool(session and session["state"] == "fatigued")
    if "passive" not in offered and not fatigued and learner.passive_streak(turn.student_id, turn.at) >= settings.engagement.passive_run:
        earned = bool((blocks.get("support") or {}).get("extend"))  # extend is offered only when it is earned
        return [offer_choice("passive", ["quiz"] + (["extend"] if earned else []) + ["stop"])]

    pq = blocks.get("prequestion")
    asked_before = (progress.get(focus) or {}).get("intuition_asked") or any(
        s["move"] == "ask_mcq" and s["data"].get("purpose") == "intuition" and s["part_id"] == focus for s in last_plan
    )
    if pq and pq["part_id"] != answered_prequestion and not asked_before:
        if turn.mcq_ok:
            return [ask_mcq(turn, question(pq["part_id"], "intuition", pq["correct"], settings), pq.get("source") or {})]
        _progress(progress, focus)["intuition_asked"] = True  # no open form: dropped for this part (decision 0028)

    for item in (blocks.get("weak_prerequisites") or {}).get("items", []):
        if item["p_now"] < settings.levels.new and not _checked_this_session(turn, item["part_id"], last_plan):
            asked = prereq_check(turn, item["part_id"], item["for"], settings, note=item["note"])
            if asked:
                return [asked]

    teaching = teach(turn, focus, settings, progress)
    held = [m for m in held_misconceptions(turn.student_id, turn.parts) if m["id"] not in handled]
    if held:  # correct it, then carry on teaching
        m = held[0]
        return [_step("feedback", m["node_id"], {"type": "held", "misconceptions": [_misconception(m)]})] + teaching
    return teaching


# --- point by point (step 05d) ----------------------------------------------------


def _points(part_id: str) -> list[dict]:
    """The points a part is taught in: its score points, or its description as one point when it has none."""
    return graph.score_points(part_id) or [{"id": None, "point": graph.require_node(part_id)["description"], "exemplar": ""}]


def _progress(progress: dict, part_id: str) -> dict:
    return progress.setdefault(part_id, {"index": 1, "reteaches": 0, "intuition_asked": False})


def open_check(turn: Turn, part_id: str) -> list[dict]:
    """A part with no mark points has no MCQs: show its points, then the explain-back of the whole part, scored
    on its points (the open check). Ends the part's progress, as an explain-back does."""
    return [_step("show", part_id, {"point": "; ".join(p["point"] for p in _points(part_id))}), _step("explain_back", part_id)]


def check(turn: Turn, part_id: str, index: int, settings: Settings, avoid: list[str] | None = None) -> dict:
    """ask_mcq (check) on one point of a part: the point's wording is the correct option. Only for a part with
    mark points (mcq_points), whose points are then its mark points."""
    point = _points(part_id)[index - 1]
    return ask_mcq(turn, question(part_id, "check", point["point"], settings, point_id=point["id"]), {"index": index}, avoid)


def teach(turn: Turn, part_id: str, settings: Settings, progress: dict) -> list[dict]:
    """Teaching on a part. At worked_example or hint: the point it has reached, as teach_point and an ask_mcq
    check on it. After the last point, or for a part already at explain_back level (secure), explain_back of
    the whole part, which joins the points together, is scored on all of them and ends the part's progress.
    A point whose check was left out last reply (check_due: a how-AI-works check or a literacy re-ask took its
    slot) gets its check only."""
    level = learner.support_level(turn.p(part_id))
    points = _points(part_id)
    state = _progress(progress, part_id)
    if not mcq_points(part_id):
        progress.pop(part_id, None)
        return open_check(turn, part_id)
    if state.pop("check_due", False) and state["index"] <= len(points):  # taught, but its check was replaced
        return [check(turn, part_id, state["index"], settings)]
    if level == "explain_back" or state["index"] > len(points):
        progress.pop(part_id, None)
        return [explain_back(turn, part_id, points, settings)]
    point = points[state["index"] - 1]
    return [
        _step(
            "teach_point",
            part_id,
            {
                "index": state["index"],
                "total": len(points),
                "point": point["point"],
                "exemplar": point["exemplar"],
                "level": level,
                "max_words": settings.points.max_words,
            },
        ),
        check(turn, part_id, state["index"], settings),
    ]


def offer_choice(reason: str, options: list[str], data: dict | None = None) -> dict:
    """offer_choice (stop): the ways on in options, from stop, quick (questions on data.quick_parts), quiz and
    extend. reason is fatigued or passive; each is offered once a session."""
    return _step("offer_choice", None, {"reason": reason, "options": options, **(data or {})})


def picked(turn: Turn, part_id: str, settings: Settings, progress: dict, choice: str) -> list[dict]:
    """The way on the student picked from offer_choice: quiz, the current point's check (as "I know this");
    extend, a harder question on the part; stop, a session summary (what they covered, when to come back)."""
    if choice == "quiz":
        return shown_or_skipped(turn, part_id, settings, progress, "skip_point")
    if choice == "extend":
        return [_step("extend", part_id)]
    return [session_summary(turn)]


def session_summary(turn: Turn) -> dict:
    """session_summary (stop): the parts worked on this session by name, and the next review (name and date), if any."""
    covered = [graph.require_node(p)["name"] for p in learner.session_parts(turn.student_id, turn.at)]
    due = learner.next_review(turn.student_id)
    nxt = {"name": graph.require_node(due["part_id"])["name"], "due": due["due"][:10]} if due else None
    return _step("session_summary", None, {"covered": covered, "next_review": nxt})


def two_option_wrong(turn: Turn, part_id: str, blocks: dict | None = None) -> dict | None:
    """The wrong option for a two-option question, as {id, text}: a misconception the student holds on the part,
    else a watch-for one, else the first in pack order; None when the part has none (the chatbot writes one).
    A held misconception is the most useful wrong option: picking it and getting feedback corrects it."""
    found = {m["id"]: m for m in graph.misconceptions_for([part_id])}
    held = [m["id"] for m in held_misconceptions(turn.student_id, [part_id])]
    watch = [m["id"] for m in ((blocks or {}).get("misconceptions") or {}).get("watch_for", []) if m.get("part_id") == part_id]
    pick = next((i for i in held + watch + list(found) if i in found), None)
    return {"id": pick, "text": option_form(found[pick]["wrong_idea"])} if pick else None


def two_option_check(turn: Turn, part_id: str, index: int, settings: Settings, blocks: dict | None = None) -> dict:
    """ask_mcq (check) on one point with two options: the point and one wrong option (two_option_wrong, or one the
    chatbot writes, when the part has none). Asked before a repeated show, marked data.then_show: its answer gets
    feedback and then the full show. Its guess is 1/2 (bkt.mcq_guess_from_options)."""
    point = _points(part_id)[index - 1]
    q = question(part_id, "check", point["point"], settings, point_id=point["id"])
    wrong = two_option_wrong(turn, part_id, blocks)
    q = {**q, "wrong": [wrong] if wrong else [], "extra": wrong is None}
    return ask_mcq(turn, q, {"index": index, "then_show": True})


def ask_confidence(turn: Turn, part_id: str) -> dict:
    """ask_confidence (stop): "how sure are you?" after an answer to a check, before the feedback (step 05z). The plan with
    the feedback is kept back one turn (service). The wording is data.line, so the move text stays short."""
    return _step("say_line", part_id, {"line": read_text("confidence/ask.md").strip()}, key="say_line_confidence")


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


def shown_or_skipped(turn: Turn, part_id: str, settings: Settings, progress: dict, choice: str, blocks: dict | None = None) -> list[dict]:
    """ "I know this" (skip_point): the current point's check only, with no teaching. "Just show me": show, a
    one-line intuition (from the same source as the intuition question) and the point, then its check; after
    show.max_per_part_session shows of the part this session, a 2-option check first instead; its answer gets
    feedback and then the full show (full_show). A part with no mark points gets its open check."""
    if not mcq_points(part_id):
        progress.pop(part_id, None)
        return open_check(turn, part_id)
    state = _progress(progress, part_id)
    points = _points(part_id)
    index = min(state["index"], len(points))
    asked = check(turn, part_id, index, settings)
    if choice == "skip_point":
        return [asked]
    if learner.shows_this_session(turn.student_id, part_id, turn.at) > settings.show.max_per_part_session:
        return [two_option_check(turn, part_id, index, settings, blocks)]  # try it first; the show follows its answer
    return full_show(turn, part_id, settings, progress)


def full_show(turn: Turn, part_id: str, settings: Settings, progress: dict) -> list[dict]:
    """The show of the current point (a one-line intuition if there is one, then the point), then its check."""
    points = _points(part_id)
    index = min(_progress(progress, part_id)["index"], len(points))
    data = {"point": points[index - 1]["point"]}
    source = intuition_source(turn, part_id)
    if source:
        data["note"] = source["note"]
    return [_step("show", part_id, data), check(turn, part_id, index, settings)]


def _bridge_in(last_plan: list[dict]) -> bool:
    """The last plan asked a bridge question (a pre-question towards the next topic, step 05t)."""
    return any(s["move"] == "ask_mcq" and s["data"].get("bridge") for s in last_plan)


def _then_show(last_plan: list[dict]) -> bool:
    """The last plan asked a two-option question that is followed by the full show once answered."""
    return any(s["move"] in ("ask_mcq", "explain_back") and s["data"].get("then_show") for s in last_plan)


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
        return [
            _step("reteach", part, {"point": point["point"], "level": learner.support_level(turn.p(part))}),
            check(turn, part, min(state["index"], len(points)), settings, avoid),
        ]
    state["index"] += 1
    state["reteaches"] = 0
    return teach(turn, part, settings, progress)


def prereq_check(turn: Turn, part_id: str, for_part: str, settings: Settings, note: str = "", stuck: bool = False) -> dict | None:
    """ask_mcq (prereq) on a weak prerequisite: its first point is the correct option. stuck marks a step back
    from a part they're stuck on, so the chatbot says it is trying a different way in. None for a part with no
    mark points."""
    if not mcq_points(part_id):
        return None
    data = {"name": graph.require_node(part_id)["name"], "for": for_part}
    if note:
        data["note"] = note
    if stuck:
        data["stuck"] = True
    return ask_mcq(turn, question(part_id, "prereq", _points(part_id)[0]["point"], settings, point_id=_points(part_id)[0]["id"]), data)


def review_check(turn: Turn, r: dict, settings: Settings) -> dict:
    """ask_mcq (review) on a due part, in its mode (recall, or transfer framed in data.new_context). The correct
    option rotates through the part's points: the point at (its evidence count) mod (its number of points)."""
    points = _points(r["part_id"])
    row = (
        learner._conn()
        .execute("SELECT n_evidence FROM part_state WHERE student_id = ? AND part_id = ?", (turn.student_id, r["part_id"]))
        .fetchone()
    )
    point = points[(row["n_evidence"] if row else 0) % len(points)]
    data = {"name": r["name"], "mode": r["mode"]}
    if r.get("new_context"):
        data["new_context"] = r["new_context"]
    return ask_mcq(turn, question(r["part_id"], "review", point["point"], settings, point_id=point["id"]), data)


def _prereqs_at_least_developing(turn: Turn, part_id: str, settings: Settings) -> bool:
    """Every direct prerequisite of the part is at least developing by the number (p_now >= levels.new)."""
    pre = [pp for edge in graph.prerequisites(part_id, 1) for pp in graph.parts_of(edge["other"])]
    return all(turn.p(pp) >= settings.levels.new for pp in pre)


def _first_key_point(part_id: str) -> dict | None:
    points = mcq_points(part_id)
    return points[0] if points else None


def bridge_target(turn: Turn, settings: Settings) -> dict | None:
    """The part to ask a bridge question about, with the link and why: {part_id, from, text, from_class}, or None.

    1. The class's next not-yet-covered section in spec order (the coverage record, step 05q), when a pack edge links
       it to the current part and its prerequisites are at least developing.
    2. Otherwise the not-yet-taught part with the strongest link (link_weight) to the current part whose
       prerequisites are at least developing.
    3. Otherwise None. Not yet taught means no evidence and no teaching step on the part."""
    if not turn.parts:
        return None
    here = turn.parts[0]
    edges = graph.linked(here)

    def candidate(part: str) -> bool:
        return (
            part != here
            and not graph.is_literacy(part)
            and _first_key_point(part) is not None
            and learner.not_yet_taught(turn.student_id, part, turn.at)
            and _prereqs_at_least_developing(turn, part, settings)
        )

    for section in learner.uncovered_sections(turn.student_id, turn.at)[:1]:  # only the very next section
        parts = graph.parts_of(section["id"])
        link = next((e for e in edges if e["other"] in parts or e["other"] == section["id"]), None)
        if link is None:
            break
        part = next((p for p in parts if candidate(p)), None)
        if part:
            return {"part_id": part, "from": here, "text": link["note"], "from_class": True}
    best = None
    for edge in edges:
        w = link_weight(edge, here, settings)
        for part in graph.parts_of(edge["other"]):
            if candidate(part) and (best is None or w > best[0]):
                best = (w, part, edge)
    return {"part_id": best[1], "from": here, "text": best[2]["note"], "from_class": False} if best else None


def bridge_question(turn: Turn, target: dict, settings: Settings) -> dict:
    """The bridge: the pre-question move (ask_mcq, purpose intuition) on the target part's first key point, carrying
    data.link and a cue of its own. Being pre-teaching, its answer feeds the starting offset of the target's sector."""
    point = _first_key_point(target["part_id"])
    assert point is not None  # a bridge target is chosen because it has a first key point
    q = question(target["part_id"], "intuition", point["point"], settings, point_id=point["id"])
    data = {
        "name": graph.require_node(target["part_id"])["name"],
        "bridge": True,
        "link": {"from": target["from"], "to": target["part_id"], "text": target["text"]},
    }
    if target["from_class"]:
        data["reason"] = read_text("bridge/reason.md").strip()
    step = ask_mcq(turn, q, data)
    return _refill({**step, "key": "ask_mcq_prequestion_bridge_reason" if target["from_class"] else "ask_mcq_prequestion_bridge"})


def find_error_step(turn: Turn, blocks: dict, settings: Settings) -> dict | None:
    """A find-the-error practice item (decision 0012), or None. Rare and off unless switched on (find_error.enabled or
    EDUX_FIND_ERROR=1): at most find_error.max_per_session a session, only on a focus part at developing or above that
    the student has answered on, never in long-session or rushing mode.

    The item is the part's own mark points as a short numbered explanation. With probability 1 - find_error.clean_share
    one sentence is swapped for one of the part's misconceptions (the sentence its correction most resembles); otherwise
    it is left whole, a clean control, so doubting everything is not rewarded. Items rotate: a misconception already
    used on this part is not used again. Always labelled as practice. The item (kind, which misconception, what to
    reveal) stays on the server; the chatbot sees only the text."""
    if not learner.find_error_on() or not turn.parts or (blocks.get("session") or {}).get("state") == "fatigued":
        return None
    part, conn = turn.parts[0], learner._conn()
    if graph.is_literacy(part) or not learner.has_evidence(turn.student_id, part, turn.at) or turn.p(part) < settings.levels.new:
        return None
    state = learner.session_state(turn.student_id, turn.at)
    start = state["session_id"] if state else turn.at
    done = [
        r["point_id"]
        for r in conn.execute(
            "SELECT point_id, ts FROM evidence_log WHERE student_id = ? AND evidence_type = 'find_error' ORDER BY id", (turn.student_id,)
        )
    ]
    this_session = conn.execute(
        "SELECT COUNT(*) FROM evidence_log WHERE student_id = ? AND evidence_type = 'find_error' AND ts >= ?", (turn.student_id, start)
    ).fetchone()[0]
    points, wrongs = graph.score_points(part), graph.misconceptions_for([part])
    if this_session >= settings.find_error.max_per_session or len(points) < 2 or not wrongs:
        return None
    roll = int(hashlib.sha256(f"{turn.student_id}:{part}:{start}".encode()).hexdigest(), 16) % 100
    clean_id = f"clean:{part}"
    want_clean = roll < settings.find_error.clean_share * 100 and clean_id not in done
    name, sentences = graph.require_node(part)["name"], [p["point"].strip().rstrip(".") + "." for p in points]
    item: dict[str, Any] | None = None
    if want_clean:
        item = {
            "id": clean_id,
            "kind": "clean",
            "part_id": part,
            "misconception_id": None,
            "reveal": read_text("find_error/reveal_clean.md").strip(),
        }
    else:
        for m in wrongs:
            item_id = f"err:{part}:{m['id']}"
            if item_id in done:
                continue
            scores = graph.relevance(m["correction"], {p["id"]: p["point"] for p in points})
            best = max(range(len(points)), key=lambda i: scores[points[i]["id"]])
            if scores[points[best]["id"]] <= 0:
                continue
            sentences[best] = m["wrong_idea"].strip().rstrip(".") + "."
            item = {
                "id": item_id,
                "kind": "error",
                "part_id": part,
                "misconception_id": m["id"],
                "sentence": best + 1,
                "reveal": read_text("find_error/reveal_error.md").strip().format(n=best + 1, correction=m["correction"].strip()),
            }
            break
    if item is None:
        return None
    statement = "\n".join(f"{i}. {s}" for i, s in enumerate(sentences, 1))
    step = _step(
        "say_line",
        part,
        {"line": read_text("find_error/intro.md").strip().format(name=name, statement=statement), "answer_type": "find_error"},
        key="say_line_find_error",
    )
    step["item"] = item
    return step


def _urgent_review(turn: Turn, part_id: str, settings: Settings) -> bool:
    """A test covering the part is within priorities.horizon_days."""
    for a in learner.assessments(turn.student_id, turn.at):
        if part_id in a["part_ids"] and 0 <= learner._days_until(a["date"], learner.parse_ts(turn.at)) <= settings.priorities.horizon_days:
            return True
    return False


def ending_tiers(turn: Turn, blocks: dict, settings: Settings, reviews_only: bool = False) -> list[dict]:
    """The reply's possible endings in four tiers, each tier's candidates ordered by the value score (priorities):
    1. a due review on a part covered by a test within priorities.horizon_days; 2. a bridge question towards the next
    topic; 3. extend, when earned; 4. any other due review. With reviews_only (a request to be quizzed), only reviews.
    Returns [{tier, kind, part_id, value, step?}, ...] in tier order."""
    reviews = []
    for r in (blocks.get("reviews_due") or {}).get("items") or []:
        if r["part_id"] not in turn.parts and mcq_points(r["part_id"]):
            reviews.append(r)
    valued = {r["part_id"]: turn.valued(r["part_id"]) for r in reviews}
    tiers: list[dict] = []
    urgent = sorted((r for r in reviews if _urgent_review(turn, r["part_id"], settings)), key=lambda r: -valued[r["part_id"]]["value"])
    tiers += [{"tier": 1, "kind": "review", "part_id": r["part_id"], "value": valued[r["part_id"]]["value"], "review": r} for r in urgent]
    if not reviews_only:
        item = find_error_step(turn, blocks, settings)
        if item:  # rare (once a session, off unless switched on): ahead of the bridge in the same tier
            tiers.append({"tier": 2, "kind": "find_error", "part_id": item["part_id"], "value": 0.0, "step": item})
        target = bridge_target(turn, settings) if turn.mcq_ok else None  # a pre-question has no open form (decision 0028)
        if target:
            tiers.append(
                {
                    "tier": 2,
                    "kind": "bridge",
                    "part_id": target["part_id"],
                    "value": turn.valued(target["part_id"])["value"],
                    "target": target,
                }
            )
        support = blocks.get("support")
        if support and support.get("extend"):
            tiers.append({"tier": 3, "kind": "extend", "part_id": support["part_id"], "value": turn.valued(support["part_id"])["value"]})
    rest = sorted((r for r in reviews if r not in urgent), key=lambda r: -valued[r["part_id"]]["value"])
    tiers += [{"tier": 4, "kind": "review", "part_id": r["part_id"], "value": valued[r["part_id"]]["value"], "review": r} for r in rest]
    return tiers


def _second_step(turn: Turn, blocks: dict, settings: Settings, reviews_only: bool = False) -> dict | None:
    """The reply's ending (ending_tiers): the first candidate of the first non-empty tier. A review picked because of one
    of the student's tests carries data.reason. The candidates not picked go on the step as considered (with their
    tier and value), which service saves in issued_plan and never sends."""
    tiers = ending_tiers(turn, blocks, settings, reviews_only)
    if not tiers:
        return None
    pick = tiers[0]
    if pick["kind"] == "extend":
        step = _step("extend", pick["part_id"])
    elif pick["kind"] == "find_error":
        step = pick["step"]
    elif pick["kind"] == "bridge":
        step = bridge_question(turn, pick["target"], settings)
    else:
        step = review_check(turn, pick["review"], settings)
        found = turn.valued(pick["part_id"])
        if found["reason"]:
            step = _refill(
                {**step, "key": "ask_mcq_review_reason", "data": {**step["data"], "reason": learner.reason_text(found["reason"], turn.at)}}
            )
    step["considered"] = [{"tier": t["tier"], "move": t["kind"], "part_id": t["part_id"], "value": round(t["value"], 5)} for t in tiers[1:]]
    return step


# --- the stuck ladder (research fixes, 0006) -------------------------------------------

# What a miss on the focus part gets once its step back has been done this session (misses counted from the step
# back): 1 a worked example and its check, 2 an easier prerequisite check, 3 an offer to stop or switch, 4+ a worked
# example of the next point (round the part's points), so it is never the same item again and again. Without a step
# back, a second miss in a row on an open answer gets the worked example instead of a second bare reteach. A right
# check straight after a worked example doesn't reset the count (they had just been shown it), and a miss on an
# open answer is cleared only by a complete open answer (right checks in between don't show they can explain it,
# research fixes, 0010b). Our choice; a rung that can't be built (no prerequisite, stopping already offered this
# session, for fatigue or being stuck) falls through to the next.
LADDER = ("worked_example", "easier_prereq", "offer_choice")
OPEN_RETEACHES_IN_A_ROW = 1


def _misses(turn: Turn, progress: dict, evidence: dict, retry: dict | None, last_plan: list[dict]) -> int:
    """Count consecutive misses on the focus part this session in progress["_misses"] (kept under its own key, as
    teach() drops a part's own progress): a wrong check or an open answer with points missing adds one, a right
    check (unless just after a worked example) or a complete open answer resets it. A harder (extend) question
    neither counts nor resets: missing a stretch question isn't being stuck. Returns the count (0 when the evidence
    isn't on the focus or isn't a miss)."""
    focus = turn.parts[0] if turn.parts else None
    if evidence["type"] in ("extend", "find_error"):
        return 0
    open_answer = evidence["type"] not in ("mcq_check", "prequestion", "ail_how") and "correct" not in evidence
    if focus is None or evidence["part_id"] != focus or not (open_answer or evidence.get("purpose") == "check"):
        return 0
    session_id = (learner.session_state(turn.student_id, turn.at) or {}).get("session_id")
    state = progress.get("_misses")
    if not state or state.get("part") != focus or state.get("session") != session_id:
        state = progress["_misses"] = {"part": focus, "session": session_id, "n": 0}
    missed = retry is not None if open_answer else not evidence["correct"]
    just_shown = any(s.get("key") == "show_stuck" for s in last_plan)
    keep = not open_answer and (just_shown or state.get("open"))
    state["n"] = state["n"] + 1 if missed else (state["n"] if keep else 0)
    if open_answer:
        state["open"] = missed
    return state["n"] if missed else 0


def _point_index(part_id: str, point_id: str | None = None, text: str | None = None) -> int:
    """The 1-based index of a point of the part, by id or wording (1 if not found)."""
    for i, p in enumerate(_points(part_id), 1):
        if (point_id and p["id"] == point_id) or (text and p["point"] == text):
            return i
    return 1


def worked_example(turn: Turn, part_id: str, index: int, settings: Settings, progress: dict, avoid: list[str] | None = None) -> list[dict]:
    """show (stuck): the point as a worked example, then its check (the point loop carries on from it); a part with
    no mark points: the worked points, then its explain-back."""
    if not mcq_points(part_id):
        progress.pop(part_id, None)
        return [
            _step("show", part_id, {"point": "; ".join(p["point"] for p in _points(part_id)), "stuck": True}, key="show_stuck"),
            _step("explain_back", part_id),
        ]
    _progress(progress, part_id)["index"] = index
    data = {"point": _points(part_id)[index - 1]["point"], "stuck": True}
    source = intuition_source(turn, part_id)
    if source:
        data["note"] = source["note"]
    return [_step("show", part_id, data, key="show_stuck"), check(turn, part_id, index, settings, avoid)]


def easier_prereq(turn: Turn, part_id: str, settings: Settings, last_plan: list[dict]) -> dict | None:
    """A prerequisite check (stuck) on the weakest prerequisite of the part not yet checked this session (else the
    weakest one); None when the part has no prerequisite with mark points."""
    pres = sorted(
        {pre for edge in graph.prerequisites(part_id, 1) for pre in graph.parts_of(edge["other"]) if mcq_points(pre)},
        key=lambda p: (turn.p(p), p),
    )
    if not pres:
        return None
    fresh = [p for p in pres if not _checked_this_session(turn, p, last_plan)]
    return prereq_check(turn, (fresh or pres)[0], part_id, settings, stuck=True)


def stop_or_switch(turn: Turn, part_id: str, settings: Settings) -> dict:
    """offer_choice (stuck): stopping, or switching to a few developing parts other than the one they're stuck on."""
    session = learner.session_state(turn.student_id, turn.at) or {}
    quick = _quick_parts(turn, settings, {part_id})
    return _step(
        "offer_choice",
        None,
        {
            "reason": "stuck",
            "options": ["stop"] + (["quick"] if quick else []),
            "minutes": round(session.get("minutes") or 0),
            "quick_parts": quick,
        },
        key="offer_choice_stuck",
    )


def stuck_ladder(
    turn: Turn,
    settings: Settings,
    evidence: dict,
    retry: dict | None,
    progress: dict,
    offered: frozenset[str],
    last_plan: list[dict],
    last_mcq: dict | None,
    misses: int,
) -> list[dict] | None:
    """The steps for a miss on the focus part instead of another reteach (see LADDER), or None to carry on as
    before. misses is the count _misses returned this turn."""
    if not misses:
        return None
    part = evidence["part_id"]
    session_id = (learner.session_state(turn.student_id, turn.at) or {}).get("session_id")
    stepped_back = (progress.get("_stuck_handled") or {}).get(part) == session_id
    if retry is not None:
        index = _point_index(part, text=(retry["data"].get("missing") or [None])[0])
    else:
        index = _point_index(part, point_id=evidence.get("point_id"))
    avoid = [o["id"] for _, o in sorted((last_mcq or {}).get("options", {}).items())] or None
    if not stepped_back:  # not stuck yet: cap bare reteaches of an open answer
        if retry is not None and misses > OPEN_RETEACHES_IN_A_ROW:
            return worked_example(turn, part, index, settings, progress, avoid)
        return None
    for rung in LADDER[misses - 1 :]:  # empty past the last rung
        if rung == "worked_example":
            return worked_example(turn, part, index, settings, progress, avoid)
        if rung == "easier_prereq":
            asked = easier_prereq(turn, part, settings, last_plan)
            if asked:
                return [asked]
        if rung == "offer_choice" and not {"fatigued", "stuck"} & offered:  # stopping already offered this session
            return [stop_or_switch(turn, part, settings)]
    if misses > len(LADDER):  # past the ladder: the next point's worked example
        index = index % len(_points(part)) + 1
    return worked_example(turn, part, index, settings, progress, avoid)


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


def choose(
    turn: Turn,
    blocks: dict,
    settings: Settings,
    choice: str = "none",
    answer: dict | None = None,
    evidence: dict | None = None,
    last_plan: list[dict] | None = None,
    corrected: set[str] | None = None,
    offered: frozenset[str] = frozenset(),
    pending: dict | None = None,
    progress: dict | None = None,
    last_mcq: dict | None = None,
) -> list[dict]:
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
    misses = 0
    if answer and evidence:
        first, retry = feedback(answer, evidence)
        was = evidence.get("p_before")  # the level before this answer: the one that tips a part to secure still gets its why
        was = turn.p(evidence["part_id"]) if was is None else was
        if evidence["score"] >= settings.bkt.correct_share and learner.level(was) == "secure":
            first = _refill({**first, "data": {**first["data"], "secure": True}})  # right at secure: confirm, no why
        steps.append(first)
        handled |= set(evidence["misconception_ids"])
        if answer["type"] == "prequestion" or evidence.get("purpose") == "intuition":
            answered_prequestion = evidence["part_id"]
            _progress(progress, evidence["part_id"])["intuition_asked"] = True
        if evidence.get("purpose") == "check" and _then_show(last_plan):  # the repeated show's question: feedback, then the show
            return ([first] + full_show(turn, evidence["part_id"], settings, progress))[:MAX_STEPS]
        misses = _misses(turn, progress, evidence, retry, last_plan)
        if retry:  # reteach ends the plan, unless they're tired or stuck: then say what's missing and do that instead
            urgent = main()
            if not _urgent(urgent):  # missed again: the next rung of the stuck ladder, not another reteach
                urgent = stuck_ladder(turn, settings, evidence, retry, progress, offered, last_plan, last_mcq, misses) or urgent
            if _urgent(urgent):
                return ([_refill({**first, "data": {**first["data"], "missing": retry["data"]["missing"]}})] + urgent)[:MAX_STEPS]
            return [first, retry]
    rest = main()
    if misses and not _urgent(rest):  # a missed check after the step back: the ladder, not the reteach loop
        rest = stuck_ladder(turn, settings, evidence or {}, None, progress, offered, last_plan, last_mcq, misses) or rest
    # all points met on an explain-back or a harder question (a retry returned above): the part is done for now
    finished = bool(answer and evidence and answer["type"] in ("explain_back", "extend") and not evidence.get("open_check"))
    if not _urgent(rest):
        if rest and rest[0]["move"] == "feedback" and steps:  # a held misconception joins the answer's feedback
            known = {m["id"] for m in steps[0]["data"]["misconceptions"]}
            extra = [m for m in rest[0]["data"]["misconceptions"] if m["id"] not in known]
            steps[0] = _refill({**steps[0], "data": {**steps[0]["data"], "misconceptions": steps[0]["data"]["misconceptions"] + extra}})
            rest = rest[1:]
        if evidence and evidence.get("purpose") == "intuition":  # whatever the answer, teaching starts
            rest = teach(turn, evidence["part_id"], settings, progress)
            if _bridge_in(last_plan) and rest and rest[0]["move"] == "teach_point":  # after a bridge they can still stop or switch
                rest[0] = _refill({**rest[0], "key": "teach_point_bridge", "data": {**rest[0]["data"], "can_stop": True}})
        elif evidence and evidence.get("purpose") == "how_ai_works" and not turn.parts:
            rest = []  # back to what they were doing: with no course focus, nothing more
        elif evidence and evidence.get("purpose") == "check":
            rest = after_check(turn, evidence, settings, progress, last_mcq)
        elif finished:  # the part is done for now: extend or a due review instead of teaching it again
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
    data = {"skill": skill, "level": level, "task": task, "features": sorted(set(features)), "pattern": literacy_pattern(skill, level)}
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
    return [_step("source_conflict", None)] + steps[-(MAX_STEPS - 1) :]


# --- how-AI-works checks (step 05e) -----------------------------------------------------

# (part, does this turn's labels trigger it, the same trigger as a condition on exchange_log), in priority order
HOW_TRIGGERS = (
    ("ail_how_fabrication", lambda m: bool(m.get("source_conflict")), "source_conflict = 1"),
    ("ail_how_agreement", lambda m: bool(m.get("pushback_changed")), "pushback_changed = 1"),
    (
        "ail_how_confidence",
        lambda m: bool(m.get("conflict_flagged")) and not m.get("source_conflict"),
        "conflict_flagged = 1 AND source_conflict = 0",
    ),
    (
        "ail_how_cutoff",
        lambda m: m.get("request_type") == "research" and bool(m.get("asks_recent")) and m.get("web_access") is False,
        "request_type = 'research' AND asks_recent = 1 AND web_access = 0",
    ),
)


def how_check(turn: Turn, part_id: str, settings: Settings) -> dict | None:
    """ask_mcq (how_ai_works) on a how-AI-works part: its point and its misconceptions, shuffled and lettered.
    None for a part with no mark points."""
    if not mcq_points(part_id):
        return None
    point = _points(part_id)[0]
    return ask_mcq(turn, question(part_id, "how_ai_works", point["point"], settings, point_id=point["id"]))


def with_check(steps: list[dict], check: dict) -> list[dict]:
    """The plan with a how-AI-works check (or its re-ask) as the last step. The check wins: the plan's own question
    and any literacy task are left out, and the steps handling the moment are kept, within the step limit."""
    keep = [s for s in steps if not is_stop(s) and s["move"] != "literacy_task"]
    return keep[: MAX_STEPS - 1] + [check]


def lettered(part_id: str) -> list[dict]:
    """A part's score points as the chatbot sees them: {id: a, b, c..., point}, in point order."""
    return [{"id": graph.point_letter(i), "point": p["point"]} for i, p in enumerate(graph.score_points(part_id))]


def score_next(plan: list[dict]) -> dict[str, list[dict]]:
    """For each part a step asks about (a multiple-choice question is answered by letter, so it has none): the points to
    tick in the student's next answer, lettered a, b, c... in point order. A letter is resolved from the
    course content when the answer comes back, so no mapping is saved."""
    out: dict[str, list[dict]] = {}
    ends_in_mcq = bool(plan) and plan[-1]["move"] == "ask_mcq"  # the next answer is a letter, so no earlier step needs ticking
    for step in plan:
        if step.get("key") == "say_line_find_error":  # the same four letters for every item, so they give nothing away
            out[step["part_id"]] = [{"id": k, "point": text} for k, text in learner.FIND_ERROR_POINTS]
            continue
        if step["move"] == "offer_choice":  # the short burst of quick questions, if they choose it
            for part in step["data"].get("quick_parts") or []:
                points = lettered(part["id"])
                if points:
                    out.setdefault(part["id"], points)
        by_option = step["move"] == "ask_mcq" or step["data"].get("asked") in ("ask_mcq", "prequestion")
        if step["part_id"] == learner.AIL_ASK:  # an ask task is done by asking a research question, not ticked
            continue
        if step["move"] in ASKS and not by_option and not ends_in_mcq and step["part_id"] and step["part_id"] not in out:
            points = lettered(step["part_id"])
            if step["data"].get("point_id") and (step["move"] == "explain_back" or step["data"].get("asked") == "explain_back"):
                # one point: its own letter only
                ids = [p["id"] for p in graph.score_points(step["part_id"])]
                points = [points[ids.index(step["data"]["point_id"])]] if step["data"]["point_id"] in ids else points
            if points:
                out[step["part_id"]] = points
    return out
