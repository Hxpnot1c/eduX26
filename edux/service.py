"""What each tool does. server.py adapts arguments; the logic lives here."""

from __future__ import annotations

import functools
import json
import re
import statistics
from datetime import date, datetime, timedelta, timezone

from edux import context_blocks, graph, learner, plan
from edux.settings import TEXT_DIR, ContextConfig, Settings, load_context, load_settings, read_text


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
    blocks = context_blocks.assemble(profile, turn, _settings(), _context())
    return {"profile": profile, "blocks": blocks, "ending_tiers": ending_view(turn, blocks)}


def ending_view(turn: context_blocks.Turn, blocks: dict) -> list[dict]:
    """The reply's ending candidates by tier, with their values (step 05t): for the CLI's student view, never sent to
    the chatbot. Each: {tier, kind, part_id, value}, plus the link and reason for a bridge."""
    out = []
    for t in plan.ending_tiers(turn, blocks, _settings()):
        item = {k: t[k] for k in ("tier", "kind", "part_id")} | {"value": round(t["value"], 5)}
        if t["kind"] == "bridge":
            item["link"] = {"from": t["target"]["from"], "text": t["target"]["text"], "from_class": t["target"]["from_class"]}
        out.append(item)
    return out


# Blocks the plan is built from; every other block the profile produces goes to reference.
PLAN_INPUTS = ("focus", "prequestion", "support", "session", "reviews_due", "teaching_note")


def _last_plan(student_id: str) -> dict:
    """The last plan issued to the student: {"ts", "plan": [steps], "focus": [part ids], "corrected": [misconception
    ids corrected so far in that session]}, empty if none."""
    row = learner._conn().execute("SELECT ts, plan_json FROM issued_plan WHERE student_id = ?", (student_id,)).fetchone()
    if row is None:
        return {"ts": None, "plan": [], "focus": [], "corrected": [], "offered": [], "points": {}}
    return {"ts": row["ts"], "corrected": [], "offered": [], "points": {}, **json.loads(row["plan_json"])}


def offered_in(steps: list[dict]) -> set[str]:
    """The offer_choice reasons (fatigued, passive) a plan offered. offer_stop, before offer_choice, was fatigue."""
    return {step["data"].get("reason", "fatigued") for step in steps if step["move"] in ("offer_choice", "offer_stop")}


def _narrowed(evidence: dict, last_plan: list[dict]) -> dict:
    """An explain-back the last plan asked about one point (a coasting student, engagement-rules) is scored on
    that point only: 1 if they produced it, else 0, with its point_id."""
    step = next((s for s in last_plan if s["move"] == "explain_back" and s["part_id"] == evidence["part_id"]
                 and s["data"].get("point_id")), None)
    if step is None:
        return evidence
    point = step["data"]["point_id"]
    return {**evidence, "score": float(point in (evidence.get("points_met") or [])), "point_id": point, "scope": [point]}


def _this_session(student_id: str, last: dict, at: str) -> tuple[set[str], frozenset[str]]:
    """(misconceptions already corrected, offer_choice reasons already offered) this session, carried in
    issued_plan while the session lasts."""
    session = learner.session_state(student_id, at)
    if last["ts"] is None or session is None or last["ts"] < session["session_id"]:
        return set(), frozenset()
    offered = set(last["offered"]) | ({"fatigued"} if last.get("offered_stop") else set()) | offered_in(last["plan"])
    return set(last["corrected"]) | plan.corrected_in(last["plan"]), frozenset(offered)


def _save_plan(student_id: str, at: str, steps: list[dict], focus: list[str], corrected: set[str],
               offered: set[str], style_sent: dict | None, pending: dict | None, mcq: dict | None,
               points: dict, literacy: dict | None = None, how: dict | None = None,
               considered: list[dict] | None = None, confidence_for: dict | None = None) -> None:
    """Save the plan issued this turn, with what the next turn needs: the focus, misconceptions corrected and
    the offer_choice reasons offered this session, the style sent, the question waiting for an answer, the MCQ
    letter map (step 05d), point-by-point progress per part (step 05d; kept across parts and sessions, so
    coming back to a part resumes where it stopped), and the pending literacy task and how-AI-works check
    (step 05e), and the add-on candidates not picked with their values (considered, priorities: data for learning
    the weights later; never sent to the chatbot)."""
    conn = learner._conn()
    with conn:
        conn.execute("INSERT OR REPLACE INTO issued_plan (student_id, ts, plan_json) VALUES (?, ?, ?)",
                     (student_id, at, json.dumps({"plan": steps, "focus": focus, "corrected": sorted(corrected),
                                                  "offered": sorted(offered), "style_sent": style_sent,
                                                  "pending": pending, "mcq": mcq, "points": points,
                                                  "literacy": literacy, "how": how,
                                                  "considered": considered or [], "confidence_for": confidence_for})))


def _how_ai_works(turn: context_blocks.Turn, blocks: dict, last: dict, steps: list[dict], evidence: dict | None,
                  labels: dict) -> tuple[list[dict], dict | None]:
    """A one-question how-AI-works check at the moment a chatbot fails (step 05e); returns (steps, the check still
    pending).

    Nothing while the student is fatigued or has just chosen to stop (a pending check is dropped unscored). A pending check not answered this
    turn is re-asked (reask, with the same options and letter map) up to literacy.max_followups times; not answered
    after that, it is counted as a skip (missing, not wrong: no evidence). Otherwise the first trigger in this turn's labels
    (plan.HOW_TRIGGERS) adds the check as the plan's last step, unless its part already had a check this session, or, with the part at secure, the trigger count isn't a multiple of
    literacy.how_secure_every. The check wins over the plan's own question and any literacy task."""
    s, sid = _settings(), turn.student_id
    if (blocks.get("session") or {}).get("state") == "fatigued" or labels.get("choice") == "stop":   # none while tired or stopping: a pending one is dropped
        return steps, None
    pending = last.get("how")
    if pending and last["ts"] is not None:
        gap = (learner.parse_ts(turn.at) - learner.parse_ts(last["ts"])).total_seconds() / 60
        answered = evidence is not None and evidence["type"] == "ail_how" and evidence["part_id"] == pending["part_id"]
        if not answered and gap <= s.session.gap_minutes:
            if pending["followups"] < s.literacy.max_followups:
                return (plan.with_check(steps, plan.reask(pending["step"])[1]),
                        {**pending, "followups": pending["followups"] + 1})
            learner.record_skip(sid, pending["part_id"], ts=turn.at)   # missing, not wrong
    session = learner.session_state(sid, turn.at)
    start = session["session_id"] if session else turn.at
    conn = learner._conn()
    for part, fired, condition in plan.HOW_TRIGGERS:
        if not fired(labels) or graph.get_node(part) is None:
            continue
        if conn.execute("SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND evidence_type = 'ail_how' "
                        "AND ts >= ? LIMIT 1", (sid, part, start)).fetchone():
            continue
        if learner.level(turn.p(part)) == "secure":
            count = conn.execute(f"SELECT COUNT(*) FROM exchange_log WHERE student_id = ? AND ts <= ? AND {condition}",
                                 (sid, turn.at)).fetchone()[0]
            if count % s.literacy.how_secure_every:
                continue
        check = plan.how_check(turn, part, s)
        if check is None:
            continue
        saved = {k: check[k] for k in ("move", "key", "part_id", "data", "question")}
        return plan.with_check(steps, check), {"part_id": part, "followups": 0, "step": saved}
    return steps, None


def _found_problem(last: dict, evidence: dict | None, at: str) -> dict | None:
    """The student reported a dead or mismatched source (source_conflict) as a Verify answer, or while a verify task
    is pending this session: finding the problem is a successful check (learner.found_problem), always as ail_task
    so that one report can't make Verify secure (ail_unprompted's low slip would). Any other answer is kept as it
    is, and a report with no verify task or answer is left to the how-AI-works check (research fixes, 0003)."""
    if evidence is not None:
        if evidence["part_id"] == learner.AIL_VERIFY and evidence["type"] in learner.LITERACY_ANSWERS:
            return learner.found_problem("ail_task", evidence.get("points_met"))
        return evidence
    task = last.get("literacy")
    if task and task["skill"] == "verify" and last["ts"] is not None and (
            (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60 <= _settings().session.gap_minutes):
        return learner.found_problem()
    return None


def _literacy_followup(student_id: str, last: dict, steps: list[dict], evidence: dict | None, request: str,
                       at: str, stopping: bool = False) -> tuple[list[dict], dict | None]:
    """Follow up the literacy task set last turn (step 05e); returns (steps, the task still pending).

    The task is done when a verify task is answered (ail_task) or, for an ask task, when this message is a research
    question (its ail_question is the score). Not done:
    - re-asked already (literacy.max_followups times) and still not done: counted as a skip on its skill's part
      (missing, not wrong: no evidence), and dropped;
    - the plan doesn't end in a question: reask re-asks it in one line;
    - the plan ends in a question: it waits; after literacy.max_waits replies waiting, it takes the next reply's
      question slot in place of the course question (never a how-AI-works check's), and the course resumes after.
    A new session drops it unscored (a task never re-asked is never scored), and so does the student choosing to stop
    (stopping), which is treated like fatigue: no re-ask. A new task replaces it."""
    s = _settings().literacy
    task = last.get("literacy")
    if stopping:
        return steps, None
    if task and last["ts"] is not None:
        task = {"waited": 0, **task}
        gap = (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60
        done = ((task["skill"] == "verify" and evidence is not None and evidence["type"] == "ail_task")
                or (task["skill"] == "ask" and request == "research"))
        how_parts = set(graph.parts_of(learner.AIL_HOW))
        has_room = not any(plan.is_stop(step) for step in steps) and len(steps) < plan.MAX_STEPS
        if done or gap > _settings().session.gap_minutes:
            task = None
        elif task["followups"] >= s.max_followups:
            learner.record_skip(student_id, task["part_id"], ts=at)   # missing, not wrong
            task = None
        elif has_room:
            steps = steps + [plan.literacy_reask(task)]
            task = {**task, "followups": task["followups"] + 1}
        elif task["waited"] >= s.max_waits and not any(step["part_id"] in how_parts for step in steps):
            steps = plan.with_check(steps, plan.literacy_reask(task))
            task = {**task, "followups": task["followups"] + 1}
        else:
            task = {**task, "waited": task["waited"] + 1}
    else:
        task = None
    new = next((step for step in steps if step["move"] == "literacy_task" and step["data"].get("task")), None)
    if new:
        task = {"skill": new["data"]["skill"], "part_id": new["part_id"], "followups": 0, "waited": 0}
    return steps, task


def _unchecked(before: list[dict], after: list[dict], points: dict) -> None:
    """A course check dropped from the plan (a how-AI-works check or a literacy re-ask took its slot): the point
    stays unchecked, and its check comes in the next reply (plan.teach reads check_due)."""
    for step in before:
        if step["move"] == "ask_mcq" and step["data"].get("purpose") == "check" and not any(x is step for x in after):
            plan._progress(points, step["part_id"])["check_due"] = True


def _open_question(last: dict, parts: list[str], answer: dict | None, choice: str, at: str) -> dict | None:
    """The question last asked, if this message asked something instead of answering it: no answer, the same
    session, not "just show me", and on the same part or with no new focus. A message about another part
    drops it."""
    pending = last.get("pending")
    if not pending or answer or choice in ("just_show_me", "skip_point", *plan.PICKS) or last["ts"] is None:
        return None
    gap = (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60
    if gap > _settings().session.gap_minutes:
        return None
    same = set(last["focus"]) | {pending["part_id"]}
    return pending if not parts or set(parts) <= same else None


def _pending_after(steps: list[dict], pending: dict | None) -> dict | None:
    """The course question waiting for an answer after this plan: the same one after a reask, else the plan's asking
    step. A literacy task is not one: it has its own follow-up (step 05e)."""
    if steps and steps[-1]["move"] == "reask" and not graph.is_literacy(steps[-1]["part_id"] or ""):
        return pending
    step = plan.asking_step([s for s in steps if not graph.is_literacy(s["part_id"] or "")])
    return {k: step[k] for k in ("move", "key", "part_id", "data", "question") if k in step} if step else None


def _mcq_after(steps: list[dict], last: dict) -> dict | None:
    """The letter -> option map to score the next answer by (step 05d): the plan's ask_mcq, or the last map
    when the same question is asked again; otherwise none."""
    if steps and steps[-1]["move"] == "reask":   # a multiple-choice question asked again keeps its map
        return last.get("mcq") if steps[-1]["data"].get("asked") in ("ask_mcq", "prequestion") else None
    step = plan.asking_step(steps)
    return step["mcq"] if step and step["move"] == "ask_mcq" else None


def compact_json(result: object) -> str:
    """A tool result as the text the chatbot receives: JSON without spaces or newlines, non-ASCII characters
    written as they are (a "£" is one character, not six)."""
    return json.dumps(result, default=str, ensure_ascii=False, separators=(",", ":"))


def result_size(result: object) -> int:
    """Characters in a tool result as sent (compact_json), which is what the call log and the budget count."""
    return len(compact_json(result))


def fit_budget(out: dict) -> dict:
    """Keep a tutor_turn result within results.max_chars: drop reference blocks one at a time from the end of
    the priority order, the watch-for misconceptions last of all. plan, score_next, focus and style are never
    cut; a result still over with no reference left is sent as it is (the call log marks it over budget)."""
    limit = _settings().results.max_chars
    reference = out.get("reference") or {}
    while reference and result_size(out) > limit:
        droppable = [n for n in reference if n != "misconceptions" or set(reference[n]) - {"watch_for"}]
        if not droppable:                 # only the watch-for misconceptions are left
            del reference["misconceptions"]
            continue
        name = droppable[-1]
        if name == "misconceptions" and "watch_for" in reference[name]:
            reference[name] = {"watch_for": reference[name]["watch_for"]}   # held ones go now, watch-for last
        else:
            del reference[name]
    return out


def _style_due(last: dict, current: dict, at: str) -> bool:
    """Send style on the first tutor_turn of a session (no call within session.gap_minutes) or when it differs
    from the style last sent (client, interests or max_words changed)."""
    if last["ts"] is None or last.get("style_sent") is None:
        return True
    gap = (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60
    return gap > _settings().session.gap_minutes or last["style_sent"] != current


def _support_given(steps: list[dict]) -> str:
    """The support the chatbot gave last reply, from the plan it was given: a teach level (teach_point's, or a
    point re-taught at that level), or a worked example for show; otherwise none."""
    for step in steps:
        if step["move"] == "teach_point" or (step["move"] == "reteach" and step["data"].get("level")):
            return step["data"]["level"]
        if step["move"] == "show":
            return "worked_example"
    return "none"


def public_steps(steps: list[dict]) -> list[dict]:
    """The plan as the chatbot sees it: {move, part_id, cue, data} per step, levels only (the cue key, an MCQ's
    question and its letter map stay on the server)."""
    return levels_only([{k: step[k] for k in ("move", "part_id", "cue", "data")} for step in steps])


def levels_only(value: object) -> object:
    """A copy with every p_now dropped: what the chatbot sees carries levels only (the CLI keeps the numbers)."""
    if isinstance(value, dict):
        return {k: levels_only(v) for k, v in value.items() if k != "p_now"}
    if isinstance(value, list):
        return [levels_only(v) for v in value]
    return value


def _reference(blocks: dict) -> dict:
    """Background for a profile with no plan: its blocks that aren't plan inputs; {"items": [...]} becomes the
    list. Levels only."""
    return levels_only({name: block["items"] if set(block) == {"items"} else block
                        for name, block in blocks.items() if name not in PLAN_INPUTS})


def _plan_reference(turn: context_blocks.Turn, steps: list[dict], profile_blocks: list[str]) -> dict:
    """Only the reference blocks the plan's moves use (context_blocks.reference_for), as the chatbot sees
    them: {"items": [...]} becomes the list, and watch-for misconceptions join the misconceptions block."""
    found = context_blocks.reference_for(turn, steps, profile_blocks, _settings(), _context())
    watch = found.pop("watch_for", None)
    out = {name: block["items"] if isinstance(block, dict) and set(block) == {"items"} else block
           for name, block in found.items()}
    if watch:
        out["misconceptions"] = {**(out.get("misconceptions") or {}), "watch_for": watch}
    return levels_only(out)


def _format_for(client: str | None) -> str:
    """The formatting note for the chatbot: text/format/<name>.md when the client name contains <name>
    (claude, chatgpt, gemini), otherwise text/format/default.md."""
    name = (client or "").lower()
    found = next((f.stem for f in sorted((TEXT_DIR / "format").glob("*.md")) if f.stem != "default" and f.stem in name),
                 "default")
    return read_text(f"format/{found}.md").strip()


def style(student: dict, client: str | None) -> dict:
    """Reply length (profile answer_length, else style.max_words), the student's interests and the client's
    formatting note."""
    row = learner._conn().execute("SELECT interests, answer_length FROM student_profile WHERE student_id = ?",
                                  (student["id"],)).fetchone()
    return {"max_words": (row and row["answer_length"]) or _settings().style.max_words,
            "interests": (row and row["interests"]) or "", "format": _format_for(client)}


# Asking for the due reviews in other words than the review_due prompt (research fixes, 0006). Only consulted for
# a message that names no course part, and only acted on when a review is due. Matched on lower-case words with
# punctuation removed. The asks_for_reviews label is the real signal; these patterns are a fallback.
_REVIEW_ASKS = [re.compile(p) for p in (
    r"\b(quiz|test|drill|grill|check) (me|us)\b",                              # quiz me / test me (on ...)
    r"\b(do|start|begin|go through|run through|work through|get through|catch up on|lets do|can we do) "
    r"(a |my |some |the |todays |today s )?(reviews?|review questions|revision|flashcards|due ones)\b",
    r"\bwhat (should|shall|do|can|could) (i|we) (revise|review|go over|practise|practice|work on|study)\b",
    r"\bwhat (needs|need) (revising|reviewing|revision|a review)\b",
    r"\b(whats|what s|what is|anything|something|any reviews|reviews|is anything) (due|up for review)\b(?! to\b)",
    r"\bhelp me (revise|review)\b",
    r"\b(revise|revision|review) (time|session)\b",
)]
# The same words about the current topic, or about how revising works, stay on the topic.
_NOT_REVIEW_ASKS = [re.compile(p) for p in (
    r"\b(on|about|with) (this|that|it|these|those|what we (just )?(did|covered|went over|looked at|have done)|"
    r"what you (just )?(said|explained|taught)|the last (one|bit|point|question))\b",
    r"\bhow (should|do|can|could|would|does|do the|do my) (i|we|you|reviews|review|revision|my reviews)\b",
    r"\breview (of|for) (this|that|my|the|an?)\b",
)]


def _words(message: str) -> str:
    return " " + re.sub(r"[^a-z]+", " ", message.lower().replace("'", "")).strip() + " "


def _asks_for_reviews(message: str, labelled: bool = False) -> bool:
    """The message asks for the due reviews: the review_due prompt ("Quiz me on what's due.") in any case or
    punctuation, or the chatbot's asks_for_reviews label, or a common paraphrase ("test me on my reviews", "what
    should I revise", "do my reviews"); but not the same words about the current topic ("quiz me on this") or about
    how to revise."""
    said = _words(message)
    if _words(read_text("prompts/review_due.md")) in said:
        return True
    return ((labelled or any(p.search(said) for p in _REVIEW_ASKS))
            and not any(p.search(said) for p in _NOT_REVIEW_ASKS))


def _names_course_topic(message: str) -> bool:
    """The message names a course node (name, alias or description; not the notes, whose everyday words like "time"
    or "practice questions" match by chance)."""
    return any(not graph.is_literacy(node_id) for node_id, _ in graph.search_nodes(message, 5))


def _reviews_waiting(student_id: str, at: str) -> bool:
    """A course review with multiple-choice points is due (what a review request can be answered with)."""
    return any(plan.mcq_points(r["part_id"]) for r in learner.due_reviews(student_id, 10_000, at))


CHECKS = ("check", "review", "prereq")   # ask_mcq purposes that check a part (reply-style)


def reply_style(steps: list[dict], student: dict, turn: context_blocks.Turn, blocks: dict) -> list[dict]:
    """Per-step reply length and diagram flag (reply-style).

    Length: style.max_words (or the profile's answer_length) is the ceiling. A step gets data.max_words only below
    it: length_fatigued_share of it on every step while fatigued, otherwise length_known_share of it on a review or
    check of a part at developing or above (Kalyuga et al., 2003: full explanations slow down students who already
    know the material). A student's own answer_length always wins: nothing shrinks, and teach_point's word budget
    becomes it, up to points.max_words_requested (so a longer length never turns one point into several). Diagram: steps on a part the pack marks as a diagram carry data.diagram, and the first of them
    on each part gets the diagram line added to its cue. That follows the content, never the student."""
    s = _settings().style
    row = learner._conn().execute("SELECT answer_length FROM student_profile WHERE student_id = ?",
                                  (student["id"],)).fetchone()
    own = row["answer_length"] if row else None
    ceiling = own or s.max_words
    fatigued = (blocks.get("session") or {}).get("state") == "fatigued"
    out, drawn = [], set()
    for step in steps:
        data, part = dict(step["data"]), step["part_id"]
        if own:
            if step["move"] == "teach_point":   # a shorter length always wins; a longer one only up to one point's worth
                data["max_words"] = min(own, _settings().points.max_words_requested)
        else:
            share = s.length_fatigued_share if fatigued else (
                s.length_known_share if step["move"] == "ask_mcq" and data.get("purpose") in CHECKS and part
                and learner.level(turn.p(part)) != "new" else 1.0)
            target = round(ceiling * share)
            if target < ceiling:
                data["max_words"] = min(data.get("max_words") or target, target)
        diagram = bool(part) and graph.is_diagram(part)
        if diagram:
            data["diagram"] = True
        new = plan._refill({**step, "data": data}) if data != step["data"] else step
        if diagram and part not in drawn:
            drawn.add(part)
            new = {**new, "cue": f"{new['cue']} {read_text('cues/diagram.md').strip()}"}
        out.append(new)
    return out


def _words_in(value: object) -> int:
    """Words in every string inside a step's data."""
    if isinstance(value, str):
        return len(value.split())
    if isinstance(value, dict):
        return sum(_words_in(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(_words_in(v) for v in value)
    return 0


def _timing(last: dict, this_message: dict, at: str) -> dict:
    """What step 05s needs to flag a rapid guess later: seconds since the previous turn (within a session), words in the
    question last asked (the options and the point of the step that waits for an answer), and the word count of
    the student's message, which the chatbot sends as this_message.words. Counts only; no text."""
    gap = None
    if last.get("ts") is not None:
        seconds = (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds()
        gap = seconds if 0 <= seconds <= _settings().session.gap_minutes * 60 else None
    asking = next((s for s in reversed(last.get("plan") or []) if plan.is_stop(s)), None)
    return {"latency_s": gap, "question_words": _words_in(asking["data"]) if asking else None,
            "answer_words": this_message.get("words")}


REQUEST_LABELS = ("request_type", "question_features", "source_conflict", "web_access", "asks_recent", "pushback_changed")


def tutor_turn(
    student: dict,
    message: str,
    this_message: dict,
    node_ids: list[str] | None = None,
    answer: dict | None = None,
    client: str | None = None,
    at: str | None = None,
) -> dict:
    """One call at the start of each reply: score and record the student's message (and answer, if any) now,
    then return the plan for this reply, the points to score their next answer against, and reference.

    A bad label, part, point, letter or misconception returns {"ok": False, "error": ...} and records nothing.
    A multiple-choice answer whose letter map is gone records nothing either, and the question is asked again
    with new letters (step 05d).
    The focus is node_ids if given; else, with an answer, the previous turn's focus (or the answer's part);
    else the message; a message that names nothing keeps the previous turn's focus.
    """
    s = _settings()
    at = learner._event_ts(at)
    depth, engagement = this_message.get("question_depth"), this_message.get("engagement")
    choice = this_message.get("choice") or "none"
    if depth not in s.nudges.depth:
        return {"ok": False, "error": f"this_message.question_depth must be one of {', '.join(s.nudges.depth)}"}
    if engagement not in s.nudges.engagement:
        return {"ok": False, "error": f"this_message.engagement must be one of {', '.join(s.nudges.engagement)}"}
    if choice not in learner.CHOICE_TAKEN:
        return {"ok": False, "error": f"this_message.choice must be one of {', '.join(learner.CHOICE_TAKEN)}"}
    try:
        learner._request_labels({k: this_message.get(k) for k in REQUEST_LABELS})
    except ValueError as e:
        return {"ok": False, "error": f"this_message.{e}"}
    last = _last_plan(student["id"])
    held = last.get("confidence_for")        # the last reply asked "how sure are you?" and kept the plan back (step 05z)
    if held and (last["ts"] is None or (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60 > s.session.gap_minutes):
        held = None                            # they never answered and have gone away: drop it, nothing is recorded
    if held:
        answer = None                          # this message is the confidence word, not an answer
    lost = False
    try:
        if answer and answer.get("type") == "find_error":      # scored against the item kept from the last plan (decision 0012)
            item = next((s["item"] for s in last["plan"] if s.get("key") == "say_line_find_error" and s.get("item")), None)
            if item is None or item["part_id"] != graph.canonical(answer.get("part_id") or ""):
                raise learner.LostQuestion("no find-the-error practice is waiting for an answer")
            evidence = learner.score_find_error(answer, item)
        else:
            evidence = learner.score_answer(answer, last.get("mcq")) if answer else None
    except learner.LostQuestion:
        evidence, lost = None, True
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    if answer and this_message.get("request_type") == "research" and not this_message.get("question_features"):
        # an answer to something we asked is not a new research question: no Ask evidence, no research plan
        this_message = {**this_message, "request_type": "other" if graph.is_literacy(answer.get("part_id") or "") else "concept"}
    if evidence and evidence["type"] == "explain_back":
        evidence = _narrowed(evidence, last["plan"])

    if not node_ids and (evidence or lost):   # an answer continues the last turn's topic (after a prereq check or review too)
        # an AI-literacy part never becomes the course focus
        node_ids = last["focus"] or ([] if graph.is_literacy(answer["part_id"]) else [answer["part_id"]])
    # a research question or other message (not an answer, no ids given) never sets or changes the course focus:
    # its matches serve this turn only (trusted sources), and the focus stays where it was
    if this_message.get("source_conflict") and not lost:   # a dead or mismatched source found while checking
        evidence = _found_problem(last, evidence, at)
    side_turn = not node_ids and this_message.get("request_type") in ("research", "other")
    resolution = graph.resolve(message or "", node_ids)
    # "quiz me on what's due" and its paraphrases name no course topic: the due reviews, not the last focus or a
    # chance match in the notes (when one is due; with none due the message stays on the last focus). A research
    # question is never one.
    wants_reviews = (not node_ids and not answer and this_message.get("request_type") != "research"
                     and _asks_for_reviews(message or "", bool(this_message.get("asks_for_reviews")))
                     and not _names_course_topic(message or "")
                     and _reviews_waiting(student["id"], at))
    if wants_reviews:
        resolution = {"parts": [], "candidates": [], "matched": None, "unknown": resolution["unknown"]}
    if not resolution["parts"] and not resolution["candidates"] and last["focus"] and not wants_reviews:
        resolution = {**graph.resolve("", last["focus"]), "unknown": resolution["unknown"]}
    # a research question is Ask evidence; a verify answer is AI-literacy evidence, not an answer on the course
    recorded = ([evidence] if evidence else []) + (
        [{"part_id": learner.AIL_VERIFY, "type": "ail_find_error", "score": evidence["score"], "misconception_ids": []}]
        if evidence and evidence["type"] == "find_error" else []) + (
        [learner.question_evidence(this_message.get("question_features"),
                                   sources_credit=learner.verified_this_session(student["id"], at))]
        if this_message.get("request_type") == "research" else [])
    literacy_answer = bool(evidence and evidence["type"] in learner.LITERACY_ANSWERS)
    tagged = list(dict.fromkeys([e["part_id"] for e in recorded] + ([] if side_turn else resolution["parts"])))
    exchange_id = None
    if tagged and not lost:
        try:
            exchange_id = learner.record_exchange(student["id"], tagged, depth, engagement, choice == "just_show_me",
                                    _support_given(last["plan"]), choice,
                                    evidence["misconception_ids"] if evidence else None,
                                    conflict_flagged=bool(this_message.get("conflict_flagged")), client=client, ts=at,
                                    evidence=recorded or None, apply="now",
                                    request={k: this_message.get(k) for k in REQUEST_LABELS},
                                    timing=_timing(last, this_message, at))
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if held:          # the student's reply to "how sure are you?": store it (or that they skipped), then give the held reply
            said = this_message.get("confidence")
            learner.record_confidence(student["id"], learner.evidence_ids_of_exchange(held["exchange_id"]),
                                      said if said in learner.CONFIDENCE_LEVELS else "skipped", at)
        elif evidence and this_message.get("confidence") in learner.CONFIDENCE_LEVELS and exchange_id:   # sent with the answer
            learner.record_confidence(student["id"], learner.evidence_ids_of_exchange(exchange_id), this_message["confidence"], at)
        if evidence:   # feedback judges "secure" on the level before this answer was applied
            before = learner.answer_p_before(student["id"], evidence["part_id"], at)
            evidence = {**evidence, "p_before": before} if before is not None else evidence

    parts = context_blocks.order_parts(student, resolution["parts"], message or "")
    turn = context_blocks.Turn(student=student, parts=parts, message=message or "", at=at,
                               limits=_context().limits, resolution=resolution)
    profile = learner.profile_of(student)
    blocks = context_blocks.assemble(profile, turn, s, _context())
    config = _context().profiles.get(profile, _context().profiles[_context().default_profile])
    corrected, offered = _this_session(student["id"], last, at)
    pending = None if wants_reviews else _open_question(last, parts, answer, choice, at)   # they asked to move on
    points = dict(last["points"] or {})
    again = last.get("pending") if lost else None
    if again and not (again["move"] == "ask_mcq" and again["part_id"] == answer["part_id"] and again.get("question")):
        again = None
    request = this_message.get("request_type") or "concept"
    course_answer = None if lost or literacy_answer else answer
    if not config.plan or (request == "other" and not course_answer and not wants_reviews):
        steps = []
    elif held:      # deliver the reply kept back while we asked how sure they were
        steps = json.loads(json.dumps(last["plan"]))
    elif again:   # the letter can't be scored: the same question, freshly shuffled
        steps = plan.add_terms(turn, [plan.ask_again(turn, again)])
    elif request == "research" and not course_answer:   # answered in full with sources, plus a literacy task
        steps = plan.research(turn, blocks, s, this_message.get("question_features") or [])
    else:
        steps = plan.add_terms(turn, plan.choose(turn, blocks, s, choice, course_answer,
                                                 evidence if course_answer else None,
                                                 last["plan"], corrected, offered, pending, points,
                                                 last.get("mcq")))
    if config.plan and this_message.get("source_conflict") and not held:
        steps = plan.with_source_conflict(steps)
    how, literacy, course_steps = (last.get("how"), last.get("literacy"), steps) if held else (None, None, steps)
    if config.plan and not held:
        steps, how = _how_ai_works(turn, blocks, last, steps, evidence, this_message)
        steps, literacy = _literacy_followup(student["id"], last, steps, evidence, request, at, stopping=choice == "stop")
        _unchecked(course_steps, steps, points)
    considered = [c for step in steps for c in step.pop("considered", [])]   # add-on candidates not picked (priorities)
    if not held:
        steps = reply_style(steps, student, turn, blocks)
    current_style = style(student, client)
    send_style = _style_due(last, current_style, at)
    ask_how_sure = bool(not held and config.plan and exchange_id and _confidence_due(
        student["id"], evidence, course_answer, this_message, blocks, choice, at))
    _save_plan(student["id"], at, steps, last["focus"] if side_turn else parts, corrected | plan.corrected_in(steps),
               offered | offered_in(steps), current_style,
               _pending_after(steps, pending), _mcq_after(steps, last), points, literacy, how, considered,
               {"exchange_id": exchange_id, "part_id": evidence["part_id"]} if ask_how_sure else None)
    shown = [plan.ask_confidence(turn, evidence["part_id"])] if ask_how_sure else steps     # the reply is held back one turn
    # with no plan (a comparison profile), answers on the focus parts can still be scored
    next_points = {} if ask_how_sure else plan.score_next(steps) if config.plan else {
        p: points for p in parts if (points := plan.lettered(p))}
    if request == "research":   # a student who checks a claim unprompted can be scored on the next turn
        next_points.setdefault(learner.AIL_VERIFY, plan.lettered(learner.AIL_VERIFY))

    focus = blocks.get("focus") or {}
    out = {
        "ok": True,
        "plan": public_steps(shown),
        "score_next": next_points,
        "reference": _plan_reference(turn, shown, config.blocks) if config.plan else _reference(blocks),
        "focus": [{"id": p["id"], "name": p["name"], "level": p["level"]} for p in focus.get("parts", [])],
    }
    if send_style:
        out["style"] = current_style
        notice = _class_notice(student["id"])
        if notice:    # once, with the first call of a session
            out["notice"] = notice
    reminder = _reminder(student["id"], last, at, bool(send_style))
    if reminder:
        out["upcoming"] = reminder
    if focus.get("candidates"):
        out["candidates"] = [{"id": c["id"], "name": c["name"]} for c in focus["candidates"]]
    if resolution["unknown"]:
        out["unknown_ids"] = resolution["unknown"]
    return fit_budget(out)


# --- progress ------------------------------------------------------------------


def _node_entry(student_id: str, node: dict, at: str) -> dict:
    return {"id": node["id"], "name": node["name"], "level": learner.shown_rollup(student_id, node["id"], at)}


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
        found.append({"part_id": part, "name": graph.get_node(part)["name"],
                      "level": learner.shown_level(student_id, part, at), "score": importance * (1 - p)})
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
    return {name: _trend(recent and recent[name], before and before[name])
            for name in ("deep_questions", "constructive", "just_show_me")}


def _trend(now: float | None, then: float | None) -> dict:
    """A share now against before, as up, down or steady (progress.trend_min_change), or None without both."""
    s = _settings().progress
    if now is None or then is None:
        direction = None
    elif now - then >= s.trend_min_change:
        direction = "up"
    elif then - now >= s.trend_min_change:
        direction = "down"
    else:
        direction = "steady"
    return {"recent": None if now is None else round(now, 2), "before": None if then is None else round(then, 2),
            "direction": direction}


def _ai_literacy(student_id: str, at: str) -> dict:
    """AI-literacy skills (step 05e): the level of Ask and Verify, How AI works (the rollup of its parts, with the
    wrong ideas about AI the student still holds), and the share of research questions showing each question
    feature over the last progress.trend_days against before."""
    cut = learner._event_ts(learner.parse_ts(at) - timedelta(days=_settings().progress.trend_days))
    rows = learner._conn().execute(
        "SELECT ts, question_features FROM exchange_log WHERE student_id = ? AND request_type = 'research' AND ts <= ?",
        (student_id, at)).fetchall()

    def share(feature: str, chosen: list) -> float | None:
        return sum(feature in r["question_features"].split(";") for r in chosen) / len(chosen) if chosen else None

    recent, before = [r for r in rows if r["ts"] > cut], [r for r in rows if r["ts"] <= cut]
    how_parts = graph.parts_of(learner.AIL_HOW)
    held = [m["wrong_idea"] for m in context_blocks.held_misconceptions(student_id, how_parts)]

    def evidence(parts: list[str]) -> dict:   # what a level rests on: how many checks, over how long (counts only)
        marks = "?" + ",?" * (len(parts) - 1)
        row = learner._conn().execute(
            f"SELECT COUNT(*) AS n, MIN(ts) AS first FROM evidence_log WHERE student_id = ? AND ts <= ? AND part_id IN ({marks})",
            (student_id, at, *parts)).fetchone()
        days = round((learner.parse_ts(at) - learner.parse_ts(row["first"])).total_seconds() / 86400) if row["first"] else 0
        return {"checks": row["n"], "over_days": days}

    return {   # skipped: tasks or checks left unanswered, which count as missing, not wrong
        "formative": "practice feedback, not a grade",
        "ask": {"level": learner.level(learner.part_p(student_id, learner.AIL_ASK, at)),
                "evidence": evidence([learner.AIL_ASK]), "skipped": learner.skips(student_id, [learner.AIL_ASK], at)},
        "verify": {"level": learner.level(learner.part_p(student_id, learner.AIL_VERIFY, at)),
                   "evidence": evidence([learner.AIL_VERIFY]), "skipped": learner.skips(student_id, [learner.AIL_VERIFY], at)},
        "how_ai_works": {"level": learner.level(learner.rollup(student_id, learner.AIL_HOW, at)), "held": held,
                         "evidence": evidence(how_parts), "skipped": learner.skips(student_id, how_parts, at)},
        "question_features": {f: _trend(share(f, recent), share(f, before)) for f in learner.QUESTION_FEATURES},
    }


def my_progress(student: dict, include_parts: bool = False, at: str | None = None) -> dict:
    """Tree with levels, the biggest levers, weak links, reviews due, AI-literacy trends and AI-literacy skills (step
    05e). AI-literacy parts are left out of the tree, levers and reviews."""
    at = at or learner.now_iso()
    s, student_id = _settings(), student["id"]
    reviews = learner.due_reviews(student_id, _context().limits.get("reviews_due", 3), at)
    out = {
        "tree": _tree(student_id, at, include_parts),
        "levers": _levers(student_id, at, s.progress.levers),
        "weak_links": _weak_links(student_id, at, s.progress.weak_links),
        "reviews_due": [{"part_id": r["part_id"], "name": r["name"], "level": learner.shown_level(student_id, r["part_id"], at),
                         "due": r["due"], "reason": r["reason"]} for r in reviews],
        "trends": _trends(student_id, at),
        "ai_literacy": _ai_literacy(student_id, at),
    }
    calibration = _calibration(student_id, at)
    if calibration:
        out["calibration"] = calibration
    notice = _class_notice(student_id)
    if notice:
        out["notice"] = notice
    return fit_progress(out, result_limit(include_parts))


def _confidence_due(student_id: str, evidence: dict | None, course_answer: dict | None, this_message: dict,
                    blocks: dict, choice: str, at: str) -> bool:
    """Whether to ask "how sure are you?" after this answer (step 05z): only after an answer to a check, a review or a
    prerequisite check (never ordinary chat, a pre-question or a how-AI-works check), when the chatbot did not already
    send the confidence, not while they are in long-session or rushing mode or asking to be shown, at most
    confidence.max_per_session times a session, and not after confidence.stop_after_skips skips in a row."""
    c = _settings().confidence
    if (not c.enabled or evidence is None or course_answer is None or this_message.get("confidence") is not None
            or evidence.get("purpose") not in ("check", "review", "prereq") or choice == "just_show_me"
            or (blocks.get("session") or {}).get("state") == "fatigued"):
        return False
    asks = learner.confidence_asks(student_id, at)
    return asks["asked"] < c.max_per_session and asks["skips_in_a_row"] < c.stop_after_skips


def _calibration(student_id: str, at: str) -> dict | None:
    """The calibration line for get_my_progress: how often they were right at each confidence level, once a level has
    at least confidence.min_per_group rated answers. Feedback for the student; never an input to p_known."""
    groups = learner.calibration(student_id, at)
    if not groups:
        return None
    labels = {"certain": "certain", "fairly_sure": "fairly sure", "guess": "guessing"}
    template = read_text("progress/calibration.md").strip()
    parts = [template.format(label=labels[k], right=groups[k]["right"], n=groups[k]["n"]) for k in ("certain", "fairly_sure", "guess") if k in groups]
    return {"groups": groups, "line": "; ".join(parts)}


def _reminder(student_id: str, last: dict, at: str, new_session: bool) -> dict | None:
    """The in-chat deadline reminder (step 05u): the first call of a session only, and only when something is due within
    reminders.days_ahead, the student has not switched reminders off, and they are not tired or rushing. Synapse cannot
    push notifications, so it says it once, when the student next writes. Neutral wording, no streaks, no guilt."""
    first = last["ts"] is None or (learner.parse_ts(at) - learner.parse_ts(last["ts"])).total_seconds() / 60 > _settings().session.gap_minutes
    if not (new_session and first):
        return None
    row = learner._conn().execute("SELECT reminders FROM student_profile WHERE student_id = ?", (student_id,)).fetchone()
    if row is not None and not row["reminders"]:
        return None
    state = learner.session_state(student_id, at)
    if state and state["fatigued"]:
        return None
    items = learner.upcoming(student_id, at)
    return {"items": items, "cue": read_text("cues/upcoming.md").strip()} if items else None


def plan_study(student: dict, assessment_id: int | None = None, sessions_per_week: int | None = None, at: str | None = None) -> dict:
    """The plan_my_study tool: learner.study_plan, kept within results.max_chars by dropping middle sessions (the last,
    mixed-practice session is always kept)."""
    out = learner.study_plan(student["id"], assessment_id, sessions_per_week, at)
    limit = result_limit()
    while out.get("ok") and len(out.get("sessions", [])) > 2 and result_size(out) > limit:
        del out["sessions"][-2]
        out["more_sessions"] = out.get("more_sessions", 0) + 1
    return out


def _class_notice(student_id: str) -> str | None:
    """While the school's class estimate is on (coverage.class_estimate_enabled) and the student is in a class: the
    one-line notice that their class's results shape where new topics start for them (step 05q). Otherwise None."""
    if not _settings().coverage.class_estimate_enabled or learner.student_class(student_id) is None:
        return None
    return read_text("notices/class_estimate.md").strip()


PROGRESS_TRIM_ORDER = ("weak_links", "reviews_due", "levers")   # lowest-ranked item first: each list is ranked best first


def fit_progress(out: dict, limit: int | None = None) -> dict:
    """Keep get_my_progress within its limit (results.max_chars, or max_chars_full_progress for the every-part
    view) by dropping the last, lowest-ranked item of weak_links, then reviews_due, then levers, until it fits.
    The tree, trends and ai_literacy are never cut."""
    limit = limit or result_limit()
    for name in PROGRESS_TRIM_ORDER:
        while out.get(name) and result_size(out) > limit:
            out[name] = out[name][:-1]
    return out


# --- profile -------------------------------------------------------------------


def update_profile(
    student: dict,
    interests: str | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
    add_assessment: dict | None = None,
    remove_assessment: int | None = None,
    covered_in_class: dict | None = None,
    reminders: bool | None = None,
) -> dict:
    """Update student_profile and return it, with the student's upcoming assessments. covered_in_class {topics, when?}
    records what their class has been taught, for this student only (step 05q): topics are matched to nodes by id, spec
    code or name, and matched and unmatched ones are returned. An empty exam_date_override
    clears it. add_assessment {name, kind, date, topics} adds an upcoming test once its topics match the pack's
    topic names or spec codes (case and spacing aside); with no match nothing is added and the pack's topics come
    back to pick from. remove_assessment is an assessment id."""
    added = None
    if add_assessment is not None:
        added = _check_assessment(add_assessment)
        if not added.get("ok"):
            return added
    covered = None
    if covered_in_class is not None:
        covered = _check_coverage(covered_in_class)
        if not covered.get("ok"):
            return covered
    if remove_assessment is not None and not learner._conn().execute(
            "SELECT 1 FROM student_assessment WHERE id = ? AND student_id = ?", (remove_assessment, student["id"])).fetchone():
        if learner._conn().execute("SELECT 1 FROM student_assessment WHERE id = ? AND class_id IS NOT NULL", (remove_assessment,)).fetchone():
            return {"ok": False, "error": "that one was set by your teacher; ask them to change it"}
        return {"ok": False, "error": f"no assessment {remove_assessment} for this student"}
    changes: dict[str, object] = {}
    if reminders is not None:
        changes["reminders"] = int(reminders)
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
        if added:
            cur = conn.execute("INSERT INTO student_assessment (student_id, name, kind, date, part_ids, created_at) "
                               "VALUES (?, ?, ?, ?, ?, ?)", (student["id"], added["name"], added["kind"], added["date"],
                                                            json.dumps(added["part_ids"]), learner.now_iso()))
            added["id"] = cur.lastrowid
        if remove_assessment is not None:
            conn.execute("DELETE FROM student_assessment WHERE id = ? AND student_id = ?", (remove_assessment, student["id"]))
        if covered:
            for node_id in covered["node_ids"]:
                conn.execute("INSERT OR REPLACE INTO student_coverage (student_id, node_id, taught_on, set_by) VALUES (?, ?, ?, 'student')",
                             (student["id"], node_id, covered["taught_on"]))
            conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ?", (student["id"],))     # its starting offsets are stale
    row = conn.execute("SELECT interests, exam_date_override, answer_length, reminders FROM student_profile WHERE student_id = ?",
                       (student["id"],)).fetchone()
    out = {"ok": True, "profile": {**dict(row), "reminders": bool(row["reminders"]), "assessments": [
        {k: a[k] for k in ("id", "name", "kind", "date", "scope")} for a in learner.assessments(student["id"])]}}
    if covered:
        out["covered"] = {"topics": covered["topics"], "taught_on": covered["taught_on"], "unmatched": covered["unmatched"]}
    if added:
        out["added"] = {"id": added["id"], "name": added["name"], "kind": added["kind"], "date": added["date"],
                        "topics": added["topics"], "parts": len(added["part_ids"])}
        if added["unmatched"]:
            out["added"]["unmatched"] = added["unmatched"]
    return out


def _topic_key(text: str) -> str:
    return " ".join(str(text).split()).casefold()


def _pack_topics() -> list[dict]:
    """The pack's course topics, as the student can name them: {name, spec_ref}."""
    return [{"name": t["name"], "spec_ref": t.get("spec_ref") or ""} for t in graph.topics()]


def _check_coverage(item: dict) -> dict:
    """Validate what a student says their class covered. Returns {ok: True, node_ids, topics, taught_on, unmatched}, or
    {ok: False, error} (with the pack's topics when nothing matched)."""
    asked = [str(t) for t in item.get("topics") or [] if str(t).strip()]
    matched, unmatched = graph.match_sections(asked)
    if not matched:
        return {"ok": False, "error": "no topic matched; ask the student which of these they covered", "topics": _pack_topics()}
    today = learner.parse_ts(learner.now_iso()).date()
    try:
        taught = date.fromisoformat(str(item.get("when") or today.isoformat()).strip())
    except ValueError:
        return {"ok": False, "error": "covered_in_class.when must be a date like 2026-10-14"}
    if taught > today:
        return {"ok": False, "error": "covered_in_class.when cannot be in the future"}
    return {"ok": True, "node_ids": [n["id"] for n in matched], "topics": [n["name"] for n in matched],
            "taught_on": taught.isoformat(), "unmatched": unmatched}


def _check_assessment(item: dict) -> dict:
    """Validate an assessment to add and match its topics. Returns {ok: True, name, kind, date, part_ids, topics,
    unmatched}, or {ok: False, error} (with the pack's topics when nothing matched)."""
    kind, name = item.get("kind"), str(item.get("name") or "").strip()
    if kind not in learner.ASSESSMENT_KINDS:
        return {"ok": False, "error": f"add_assessment.kind must be one of {', '.join(learner.ASSESSMENT_KINDS)}"}
    if not name:
        return {"ok": False, "error": "add_assessment.name is empty"}
    try:
        day = date.fromisoformat(str(item.get("date") or "").strip())
    except ValueError:
        return {"ok": False, "error": "add_assessment.date must be a date like 2027-03-14"}
    if day <= learner.parse_ts(learner.now_iso()).date():
        return {"ok": False, "error": f"add_assessment.date {day.isoformat()} is not in the future"}
    asked = [str(t) for t in item.get("topics") or [] if str(t).strip()]
    matched, unmatched = graph.match_sections(asked)     # any topic, concept or part, by id, spec code or name
    if not matched:
        return {"ok": False, "error": "no topic matched; ask the student which of these it covers",
                "topics": _pack_topics()}
    parts = list(dict.fromkeys(p for t in matched for p in graph.parts_of(t["id"])))
    return {"ok": True, "name": name, "kind": kind, "date": day.isoformat(), "part_ids": parts,
            "topics": [t["name"] for t in matched], "unmatched": unmatched}


# --- call timing ---------------------------------------------------------------


def log_call(student_id: str | None, tool: str, started: datetime, ms: float, result_chars: int, ok: bool,
             error: str | None = None, over_budget: bool = False) -> None:
    """Write one call_log row (operational: rebuild ignores it)."""
    conn = learner._conn()
    with conn:
        conn.execute("INSERT INTO call_log (ts, student_id, tool, ms, result_chars, ok, error, over_budget) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (started.astimezone(timezone.utc).isoformat(timespec="milliseconds"), student_id, tool, ms,
                      result_chars, int(ok), error, int(over_budget)))


def result_limit(full_progress: bool = False) -> int:
    """results.max_chars for every tool, or results.max_chars_full_progress for get_my_progress with include_parts."""
    results = _settings().results
    return results.max_chars_full_progress if full_progress else results.max_chars


def over_budget(tool: str, result_chars: int, full_progress: bool = False) -> bool:
    """Any tool's result over its limit (result_limit), after fit_budget or fit_progress dropped what they could."""
    return result_chars > result_limit(full_progress and tool == "get_my_progress")


def _percentile(values: list[float], share: float) -> float:
    """Nearest-rank percentile of a non-empty list."""
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round(share * len(ordered) + 0.5) - 1))]


def call_stats(student_id: str | None = None, last: int = 20) -> dict:
    """Recent calls; per tool the median and 90th-percentile ms, the median and largest result size and how many
    calls were over budget; and the median gap between a student's consecutive calls (roughly the chatbot's
    time per turn)."""
    where, args = ("WHERE student_id = ?", (student_id,)) if student_id else ("", ())
    rows = [dict(r) for r in learner._conn().execute(f"SELECT * FROM call_log {where} ORDER BY ts, id", args)]
    per_tool: dict[str, list[dict]] = {}
    for r in rows:
        per_tool.setdefault(r["tool"], []).append(r)
    times: dict[str, list[datetime]] = {}
    for r in rows:
        if r["student_id"]:
            times.setdefault(r["student_id"], []).append(learner.parse_ts(r["ts"]))
    gaps = {sid: statistics.median([(b - a).total_seconds() for a, b in zip(ts, ts[1:])])
            for sid, ts in times.items() if len(ts) > 1}
    return {
        "recent": rows[-last:] if last > 0 else [],
        "tools": {tool: {"calls": len(rs), "median_ms": statistics.median([r["ms"] for r in rs]),
                         "p90_ms": _percentile([r["ms"] for r in rs], 0.9),
                         "median_chars": statistics.median([r["result_chars"] for r in rs]),
                         "max_chars": max(r["result_chars"] for r in rs),
                         "over_budget": sum(r["over_budget"] for r in rs)}
                  for tool, rs in sorted(per_tool.items())},
        "gaps": gaps,
    }
