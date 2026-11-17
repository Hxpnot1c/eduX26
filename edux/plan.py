"""Choose the plan for one turn: at most two ordered steps for the chatbot to carry out, and nothing else.

Each step is {move, part_id, text, data}; text comes from text/moves/. The plan is built from the context
blocks the student's profile produced this turn, so a profile without a block never triggers its move.
Steps in STOP end the plan, because the student needs to reply.

Order (first match wins for the main step):
  answer given    -> feedback (prequestion, or all points met) / reteach_gap (points missing; ends the plan)
  fatigued        -> offer_stop (once a session; also replaces reteach_gap's re-ask, as do stuck moves)
  stuck on focus  -> step_back (weakest prerequisite) / switch_approach
  ambiguous focus -> ask_which (no focus at all: the top due review, if any)
  just_show_me    -> show (nothing else this turn)
  pre-question    -> prequestion
  weak prereq     -> check_prereq (level new, not checked this session)
  held misconc.   -> correct_misconception (unless already corrected this session)
  otherwise       -> teach at the support level
With an answer the plan is [feedback, main step]; without one it is [main step, extend or one review] when
the main step is not a stop step.
"""

from __future__ import annotations

import hashlib
import random

from edux import graph, learner
from edux.context_blocks import Turn, core_idea, held_misconceptions
from edux.settings import Settings, read_text

STOP = {"reteach_gap", "offer_stop", "step_back", "ask_which", "prequestion", "check_prereq"}
ASKS = {"reteach_gap", "step_back", "switch_approach", "prequestion", "check_prereq", "teach", "extend", "review"}
MAX_STEPS = 2
# The answer.type the chatbot sends back for a step that asks something.
ANSWER_TYPE = {"prequestion": "prequestion", "check_prereq": "review", "step_back": "review", "review": "review",
               "extend": "extend", "teach": "explain_back", "switch_approach": "explain_back"}


def _text(name: str) -> str:
    return read_text(f"moves/{name}.md").strip()


def _step(move: str, part_id: str | None, data: dict | None = None, text: str | None = None) -> dict:
    data = dict(data or {})
    if move in ANSWER_TYPE:
        data["answer_type"] = ANSWER_TYPE[move]
    return {"move": move, "part_id": part_id, "text": _text(text or move), "data": data}


def _summary(turn: Turn, part_id: str) -> dict:
    node = graph.get_node(part_id)
    return {"id": part_id, "name": node["name"], "level": learner.level(turn.p(part_id))}


def is_stop(step: dict) -> bool:
    return step["move"] in STOP or (step["move"] == "teach" and step["data"].get("level") == "explain_back")


# --- feedback on the student's answer -----------------------------------------------


def feedback(answer: dict, evidence: dict) -> dict:
    """The step answering what the student just said: answer is what the chatbot sent, evidence the scored item."""
    part = evidence["part_id"]
    shown = [graph.get_misconception(m) for m in evidence["misconception_ids"]]
    if answer["type"] == "prequestion":
        picked = answer.get("picked_misconception_id")
        wrong = graph.get_misconception(picked) if picked else None
        return _step("feedback", part, {
            "type": "prequestion", "correct": evidence["score"] == 1.0, "correct_idea": core_idea(part)[1],
            "picked": {"id": wrong["id"], "wrong_idea": wrong["wrong_idea"], "correction": wrong["correction"]} if wrong else None})
    points = graph.score_points(part)
    met = set(answer.get("points_met") or [])
    others = [{"id": m["id"], "wrong_idea": m["wrong_idea"], "correction": m["correction"]} for m in shown if m]
    if len(met) == len(points):
        return _step("feedback", part, {"type": answer["type"], "points_met": [p["point"] for p in points],
                                        "shown_misconceptions": others})
    return _step("reteach_gap", part, {"type": answer["type"], "answer_type": answer["type"], "missing": [p["point"] for p in points if p["id"] not in met],
                                       "shown_misconceptions": others})


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
    """Misconception ids a plan already corrected: by correct_misconception, or in feedback."""
    found: set[str] = set()
    for step in steps:
        data = step["data"]
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
            return _step("switch_approach", focus, {
                "anchor": {"id": anchor["part_id"], "name": anchor["name"], "note": anchor["note"]} if anchor else None})

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
        return _step("correct_misconception", m["node_id"], {"id": m["id"], "wrong_idea": m["wrong_idea"],
                                                             "correction": m["correction"]})

    support = blocks.get("support")
    if support:
        part_type = graph.get_node(support["part_id"])["part_type"]
        level = support["level"]
        if level == "hint":
            text = "teach_hint_procedural" if part_type in settings.support.procedural_types else "teach_hint_conceptual"
        else:
            text = f"teach_{level}"
        return _step("teach", support["part_id"], {"level": level, "part_type": part_type}, text=text)
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
        return _step("review", r["part_id"], data, text=f"review_{r['mode']}")
    return None


# --- the plan -----------------------------------------------------------------------


def choose(turn: Turn, blocks: dict, settings: Settings, choice: str = "none", answer: dict | None = None,
           evidence: dict | None = None, last_plan: list[dict] | None = None,
           corrected: set[str] | None = None, offered_stop: bool = False) -> list[dict]:
    """The plan for this turn (see the module docstring). answer is what the chatbot sent about the student's
    answer and evidence its scored item; last_plan is the plan issued on the previous turn; corrected holds the
    misconceptions already corrected this session, which aren't corrected again; offered_stop is true once
    stopping has been offered this session."""
    last_plan = last_plan or []
    steps: list[dict] = []
    handled: set[str] = set(corrected or ()) | corrected_in(last_plan)
    answered_prequestion = None
    if answer and evidence:
        first = feedback(answer, evidence)
        steps.append(first)
        handled |= set(evidence["misconception_ids"])
        if answer["type"] == "prequestion":
            answered_prequestion = evidence["part_id"]
        if is_stop(first):   # reteach_gap, unless they're tired or stuck: then say what's missing and do that instead
            urgent = main_step(turn, blocks, settings, choice, last_plan, handled, answered_prequestion, offered_stop)
            if urgent and urgent["move"] in ("offer_stop", "step_back", "switch_approach"):
                return [{**first, "move": "feedback", "text": _text("feedback")}, urgent]
            return steps
    main = main_step(turn, blocks, settings, choice, last_plan, handled, answered_prequestion, offered_stop)
    if main:
        steps.append(main)
    if len(steps) == 1 and main and not is_stop(main) and main["move"] not in ("show", "review"):
        second = _second_step(turn, blocks)
        if second:
            steps.append(second)
    return steps[:MAX_STEPS]


def score_next(plan: list[dict]) -> dict[str, list[dict]]:
    """For each part a step asks about (a pre-question is answered by option, so it has none): the points to
    tick in the student's next answer."""
    out: dict[str, list[dict]] = {}
    for step in plan:
        if step["move"] == "offer_stop":   # the short burst of quick questions, if they choose it
            for part in step["data"]["quick_parts"]:
                points = graph.score_points(part["id"])
                if points:
                    out.setdefault(part["id"], points)
        if step["move"] in ASKS and step["move"] != "prequestion" and step["part_id"] and step["part_id"] not in out:
            points = graph.score_points(step["part_id"])
            if points:
                out[step["part_id"]] = points
    return out
