"""Choose the plan for one turn: at most two ordered steps for the chatbot to carry out, and nothing else.

Each step is {move, part_id, cue, data}. What each move means is in the server instructions, sent once
(server_instructions below); the cue is one line from text/moves/<key>.cue.md, so the move stays clear in a long chat. The plan is built from the context
blocks the student's profile produced this turn, so a profile without a block never triggers its move.
Steps in STOP end the plan, because the student needs to reply.

Order (first match wins for the main step):
  answer given    -> feedback, then reteach when points are missing (which ends the plan)
  question instead of the pending answer -> answer_brief, then reask the same question (fatigue and stuck first)
  fatigued        -> offer_stop (once a session; also replaces reteach's re-ask, as do stuck moves)
  stuck on focus  -> step_back (weakest prerequisite) / reteach of the whole part (through the anchor)
  ambiguous focus -> ask_which (no focus at all: the top due review, if any)
  just_show_me    -> show (nothing else this turn)
  pre-question    -> prequestion
  weak prereq     -> check_prereq (level new, not checked this session)
  held misconc.   -> feedback with the held misconception (unless already corrected this session)
  otherwise       -> teach at the support level
With an answer the plan is [feedback, main step]; without one it is [main step, extend or one review] when
the main step is not a stop step. feedback is the only move that names misconceptions; reteach never repeats them.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re

from edux import graph, learner
from edux.context_blocks import Turn, core_idea, held_misconceptions, known_parts, known_terms
from edux.settings import TEXT_DIR, Settings, SettingsError, read_text

log = logging.getLogger(__name__)

STOP = {"reteach", "offer_stop", "step_back", "ask_which", "prequestion", "check_prereq", "reask"}
ASKS = {"reteach", "step_back", "prequestion", "check_prereq", "teach", "extend", "review", "reask"}
MAX_STEPS = 2
# The answer.type the chatbot sends back for a step that asks something.
ANSWER_TYPE = {"prequestion": "prequestion", "check_prereq": "review", "step_back": "review", "review": "review",
               "extend": "extend", "teach": "explain_back"}


# The data fields each move's cue can name as a {field} placeholder: (always present, sometimes present).
# A placeholder outside both is a startup error; one that is only sometimes present is a warning. Sections
# (text/moves/<key>.md) are sent once with no data, so they name fields as data.<field> and have no placeholders.
TEXT_FIELDS: dict[str, tuple[set[str], set[str]]] = {
    "answer_brief": (set(), set()),
    "ask_which": ({"candidates"}, set()),
    "check_prereq": ({"name", "for", "note", "answer_type"}, set()),
    "extend": ({"answer_type"}, set()),
    "feedback": ({"type", "misconceptions"}, {"correct", "correct_idea", "points_met", "missing"}),
    "offer_stop": ({"minutes", "quick_parts"}, set()),
    "prequestion": ({"target", "options", "answer_type"}, set()),
    "reask": ({"asked", "answer_type"}, set()),
    "reteach": ({"answer_type"}, {"missing", "anchor"}),
    "review_recall": ({"name", "mode", "answer_type"}, set()),
    "review_transfer": ({"name", "mode", "new_context", "answer_type"}, set()),
    "show": ({"part_type"}, set()),
    "step_back": ({"to", "for", "answer_type"}, set()),
    "teach_explain_back": ({"level", "part_type", "answer_type"}, set()),
    "teach_hint_conceptual": ({"level", "part_type", "answer_type"}, set()),
    "teach_hint_procedural": ({"level", "part_type", "answer_type"}, set()),
    "teach_worked_example": ({"level", "part_type", "answer_type"}, set()),
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
    for key in move_keys():
        always, sometimes = TEXT_FIELDS.get(key, (set(), set()))
        text = _text(key)
        if placeholders(text):
            errors.append(f"text/moves/{key}.md: sections are sent once, so use data.<field>, "
                          f"not {{{sorted(placeholders(text))[0]}}}")
        stray = sorted(set(re.findall(r"`([a-z_]+)`", text)) & (always | sometimes))
        if stray:
            errors.append(f"text/moves/{key}.md: write data fields as data.<field>, not `{stray[0]}`")
        if _sentences(text) > limits.max_sentences:
            warnings.append(f"text/moves/{key}.md: {_sentences(text)} sentences, over {limits.max_sentences}")
        if not (TEXT_DIR / "moves" / f"{key}.cue.md").exists():
            errors.append(f"text/moves/{key}.cue.md is missing")
            continue
        cue = _cue(key)
        if len(cue.split()) > limits.cue_max_words:
            warnings.append(f"text/moves/{key}.cue.md: {len(cue.split())} words, over {limits.cue_max_words}")
        for name in sorted(placeholders(cue)):
            if name in sometimes:
                warnings.append(f"text/moves/{key}.cue.md: {{{name}}} is only sometimes in the step's data")
            elif name not in always:
                errors.append(f"text/moves/{key}.cue.md: {{{name}}} is never in the step's data")
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
    """A plan step. key is the move text's name (teach_<level>, review_<mode>, otherwise the move): its
    section is in the server instructions, and its one-line cue goes with the step, filled from data. The key
    stays in the saved plan; service.public_steps leaves it out of the result."""
    data = dict(data or {})
    if move in ANSWER_TYPE:
        data["answer_type"] = ANSWER_TYPE[move]
    key = key or move
    return {"move": move, "part_id": part_id, "key": key, "cue": fill(_cue(key), data), "data": data}


def _summary(turn: Turn, part_id: str) -> dict:
    node = graph.get_node(part_id)
    return {"id": part_id, "name": node["name"], "level": learner.level(turn.p(part_id))}


def is_stop(step: dict) -> bool:
    return step["move"] in STOP or (step["move"] == "teach" and step["data"].get("level") == "explain_back")


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
    if answer["type"] == "prequestion":   # the picked option comes first in misconception_ids
        return _step("feedback", part, {"type": "prequestion", "correct": evidence["score"] == 1.0,
                                        "correct_idea": core_idea(part)[1], "misconceptions": shown}), None
    points = graph.score_points(part)
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
    if any(s["move"] == "check_prereq" and s["part_id"] == part_id for s in last_plan):
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


def _options(turn: Turn, block: dict) -> list[dict]:
    """The pre-question's options, the correct idea among the misconceptions, in an order fixed per student and part."""
    options = [{"id": "correct", "text": block["correct"]}] + [
        {"id": d["id"], "text": d["wrong_idea"]} for d in block["distractors"]]
    seed = hashlib.sha256(f"{turn.student_id}:{block['part_id']}".encode()).hexdigest()
    random.Random(seed).shuffle(options)
    return options


def main_step(turn: Turn, blocks: dict, settings: Settings, choice: str, last_plan: list[dict],
              handled: set[str], answered_prequestion: str | None, offered_stop: bool = False) -> dict | None:
    """The first rule that matches, or None when there is nothing to plan. Stopping is offered once a session:
    if the student carries on, teaching goes on."""
    session = blocks.get("session")
    focus = turn.parts[0] if turn.parts else None

    if session and session["state"] == "fatigued" and not offered_stop:
        quick = [{"id": p["id"], "name": p["name"], "level": p["level"]} for p in session["quick_parts"]]
        return _step("offer_stop", None, {"minutes": session["minutes"], "quick_parts": quick})

    if session and session["state"] == "stuck" and focus:
        stuck = next((p for p in session["parts"] if p["part_id"] == focus), None)
        if stuck:
            back = stuck["step_back_to"]
            if back:
                return _step("step_back", back["id"], {"to": {k: back[k] for k in ("id", "name", "level")}, "for": focus})
            anchor = blocks.get("anchor")
            return _step("reteach", focus, {
                "anchor": {"id": anchor["part_id"], "name": anchor["name"], "note": anchor["note"]} if anchor else None,
                "answer_type": "explain_back"})

    if focus is None:
        candidates = (blocks.get("focus") or {}).get("candidates")
        if candidates:
            return _step("ask_which", None, {"candidates": [{k: c[k] for k in ("id", "name")} for c in candidates]})
        return _second_step(turn, blocks, reviews_only=True)   # e.g. "quiz me on what's due"

    if choice == "just_show_me":
        return _step("show", focus, {"part_type": graph.get_node(focus)["part_type"]})

    pq = blocks.get("prequestion")
    asked_before = any(s["move"] == "prequestion" and s["part_id"] == focus for s in last_plan)
    if pq and pq["part_id"] != answered_prequestion and not asked_before:
        return _step("prequestion", pq["part_id"], {"target": pq["target"], "options": _options(turn, pq)})

    for item in (blocks.get("weak_prerequisites") or {}).get("items", []):
        if item["level"] == "new" and not _checked_this_session(turn, item["part_id"], last_plan):
            return _step("check_prereq", item["part_id"], {"name": item["name"], "for": item["for"], "note": item["note"]})

    held = [m for m in held_misconceptions(turn.student_id, turn.parts) if m["id"] not in handled]
    if held:
        m = held[0]
        return _step("feedback", m["node_id"], {"type": "held", "misconceptions": [_misconception(m)]})

    support = blocks.get("support")
    if support:
        part_type = graph.get_node(support["part_id"])["part_type"]
        level = support["level"]
        if level == "hint":
            text = "teach_hint_procedural" if part_type in settings.support.procedural_types else "teach_hint_conceptual"
        else:
            text = f"teach_{level}"
        return _step("teach", support["part_id"], {"level": level, "part_type": part_type}, key=text)
    return None


def _second_step(turn: Turn, blocks: dict, reviews_only: bool = False) -> dict | None:
    """extend when earned, otherwise the top due review (not on a focus part) in its mode, otherwise nothing."""
    support = blocks.get("support")
    if support and support.get("extend") and not reviews_only:
        return _step("extend", support["part_id"])
    reviews = [r for r in (blocks.get("reviews_due") or {}).get("items") or [] if r["part_id"] not in turn.parts]
    if reviews:
        r = reviews[0]
        data = {"name": r["name"], "mode": r["mode"]}
        if r.get("new_context"):
            data["new_context"] = r["new_context"]
        return _step("review", r["part_id"], data, key=f"review_{r['mode']}")
    return None


# --- the plan -----------------------------------------------------------------------


def add_terms(turn: Turn, steps: list[dict]) -> list[dict]:
    """Give the plan's first step on a part (every step that teaches or asks is on a part) data.terms: the course
    terms the student knows (context_blocks.known_terms), the steps' own parts first, so the chatbot doesn't
    introduce others. The list is sent once per plan, which keeps the result within its budget."""
    for step in steps:
        step["data"].pop("terms", None)
    parts = list(dict.fromkeys(s["part_id"] for s in steps if s["part_id"]))
    if parts:
        first = next(s for s in steps if s["part_id"])
        first["data"]["terms"] = known_terms(turn, parts, known_parts(turn))
    return steps


def asking_step(steps: list[dict]) -> dict | None:
    """The step in a plan that asks the student something they should answer (it carries data.answer_type)."""
    return next((s for s in reversed(steps) if "answer_type" in s["data"]), None)


def reask(pending: dict) -> list[dict]:
    """answer_brief, then the pending question again with the same data (so the same answer_type and score_next)."""
    data = {"asked": pending["move"], **{k: v for k, v in pending["data"].items() if k != "terms"}}
    return [_step("answer_brief", pending["part_id"]), {**_step("reask", pending["part_id"], data)}]


def choose(turn: Turn, blocks: dict, settings: Settings, choice: str = "none", answer: dict | None = None,
           evidence: dict | None = None, last_plan: list[dict] | None = None,
           corrected: set[str] | None = None, offered_stop: bool = False, pending: dict | None = None) -> list[dict]:
    """The plan for this turn (see the module docstring). answer is what the chatbot sent about the student's
    answer and evidence its scored item; last_plan is the plan issued on the previous turn; corrected holds the
    misconceptions already corrected this session, which aren't corrected again; offered_stop is true once
    stopping has been offered this session; pending is the question still waiting for an answer, when this
    message asked something instead (on the same part, or with no new focus)."""
    last_plan = last_plan or []
    steps: list[dict] = []
    handled: set[str] = set(corrected or ()) | corrected_in(last_plan)
    answered_prequestion = None
    if pending and not answer:
        urgent = main_step(turn, blocks, settings, choice, last_plan, handled, None, offered_stop)
        if urgent and urgent["move"] in ("offer_stop", "step_back", "reteach"):
            return [urgent]
        return reask(pending)
    if answer and evidence:
        first, retry = feedback(answer, evidence)
        steps.append(first)
        handled |= set(evidence["misconception_ids"])
        if answer["type"] == "prequestion":
            answered_prequestion = evidence["part_id"]
        if retry:   # reteach ends the plan, unless they're tired or stuck: then say what's missing and do that instead
            urgent = main_step(turn, blocks, settings, choice, last_plan, handled, answered_prequestion, offered_stop)
            if urgent and urgent["move"] in ("offer_stop", "step_back", "reteach"):
                return [_refill({**first, "data": {**first["data"], "missing": retry["data"]["missing"]}}), urgent]
            return [first, retry]
    main = main_step(turn, blocks, settings, choice, last_plan, handled, answered_prequestion, offered_stop)
    if main and main["move"] == "feedback" and steps:   # a held misconception joins the answer's feedback
        known = {m["id"] for m in steps[0]["data"]["misconceptions"]}
        extra = [m for m in main["data"]["misconceptions"] if m["id"] not in known]
        steps[0] = _refill({**steps[0], "data": {**steps[0]["data"],
                                                 "misconceptions": steps[0]["data"]["misconceptions"] + extra}})
        main = None
    if main:
        steps.append(main)
    if len(steps) == 1 and main and not is_stop(main) and main["move"] not in ("show", "review"):
        second = _second_step(turn, blocks)
        if second:
            steps.append(second)
    return steps[:MAX_STEPS]


def lettered(part_id: str) -> list[dict]:
    """A part's score points as the chatbot sees them: {id: a, b, c..., point}, in point order."""
    return [{"id": graph.point_letter(i), "point": p["point"]} for i, p in enumerate(graph.score_points(part_id))]


def score_next(plan: list[dict]) -> dict[str, list[dict]]:
    """For each part a step asks about (a pre-question is answered by option, so it has none): the points to
    tick in the student's next answer, lettered a, b, c... in point order. A letter is resolved from the
    course content when the answer comes back, so no mapping is saved."""
    out: dict[str, list[dict]] = {}
    for step in plan:
        if step["move"] == "offer_stop":   # the short burst of quick questions, if they choose it
            for part in step["data"]["quick_parts"]:
                points = lettered(part["id"])
                if points:
                    out.setdefault(part["id"], points)
        by_option = step["move"] == "prequestion" or step["data"].get("asked") == "prequestion"
        if step["move"] in ASKS and not by_option and step["part_id"] and step["part_id"] not in out:
            points = lettered(step["part_id"])
            if points:
                out[step["part_id"]] = points
    return out
