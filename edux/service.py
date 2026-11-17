"""What each tool does. server.py adapts arguments; the logic lives here."""

from __future__ import annotations

import functools
import json
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
    return {"profile": profile, "blocks": context_blocks.assemble(profile, turn, _settings(), _context())}


# Blocks the plan is built from; every other block the profile produces goes to reference.
PLAN_INPUTS = ("focus", "prequestion", "support", "session", "reviews_due", "teaching_note")


def _last_plan(student_id: str) -> dict:
    """The last plan issued to the student: {"ts", "plan": [steps], "focus": [part ids], "corrected": [misconception
    ids corrected so far in that session]}, empty if none."""
    row = learner._conn().execute("SELECT ts, plan_json FROM issued_plan WHERE student_id = ?", (student_id,)).fetchone()
    if row is None:
        return {"ts": None, "plan": [], "focus": [], "corrected": [], "offered_stop": False, "points": {}}
    return {"ts": row["ts"], "corrected": [], "offered_stop": False, "points": {}, **json.loads(row["plan_json"])}


def _this_session(student_id: str, last: dict, at: str) -> tuple[set[str], bool]:
    """(misconceptions already corrected, stopping already offered) this session, carried in issued_plan
    while the session lasts."""
    session = learner.session_state(student_id, at)
    if last["ts"] is None or session is None or last["ts"] < session["session_id"]:
        return set(), False
    offered = last["offered_stop"] or any(step["move"] == "offer_stop" for step in last["plan"])
    return set(last["corrected"]) | plan.corrected_in(last["plan"]), offered


def _save_plan(student_id: str, at: str, steps: list[dict], focus: list[str], corrected: set[str],
               offered_stop: bool, style_sent: dict | None, pending: dict | None, mcq: dict | None,
               points: dict, literacy: dict | None = None, how: dict | None = None) -> None:
    """Save the plan issued this turn, with what the next turn needs: the focus, misconceptions corrected and
    whether stopping was offered this session, the style sent, the question waiting for an answer, the MCQ
    letter map (step 05d), point-by-point progress per part (step 05d; kept across parts and sessions, so
    coming back to a part resumes where it stopped), and the pending literacy task and how-AI-works check
    (step 05e)."""
    conn = learner._conn()
    with conn:
        conn.execute("INSERT OR REPLACE INTO issued_plan (student_id, ts, plan_json) VALUES (?, ?, ?)",
                     (student_id, at, json.dumps({"plan": steps, "focus": focus, "corrected": sorted(corrected),
                                                  "offered_stop": offered_stop, "style_sent": style_sent,
                                                  "pending": pending, "mcq": mcq, "points": points,
                                                  "literacy": literacy, "how": how})))


def _how_ai_works(turn: context_blocks.Turn, blocks: dict, last: dict, steps: list[dict], evidence: dict | None,
                  labels: dict) -> tuple[list[dict], dict | None]:
    """A one-question how-AI-works check at the moment a chatbot fails (step 05e); returns (steps, the check still
    pending).

    Nothing while the student is fatigued (a pending check is dropped unscored). A pending check not answered this
    turn is re-asked (reask, with the same options and letter map) up to literacy.max_followups times; not answered
    after that, it is recorded as ail_how with score 0. Otherwise the first trigger in this turn's labels
    (plan.HOW_TRIGGERS) adds the check as the plan's last step, unless its part already had a check this session, or, with the part at secure, the trigger count isn't a multiple of
    literacy.how_secure_every. The check wins over the plan's own question and any literacy task."""
    s, sid = _settings(), turn.student_id
    if (blocks.get("session") or {}).get("state") == "fatigued":   # no checks while tired: a pending one is dropped
        return steps, None
    pending = last.get("how")
    if pending and last["ts"] is not None:
        gap = (learner.parse_ts(turn.at) - learner.parse_ts(last["ts"])).total_seconds() / 60
        answered = evidence is not None and evidence["type"] == "ail_how" and evidence["part_id"] == pending["part_id"]
        if not answered and gap <= s.session.gap_minutes:
            if pending["followups"] < s.literacy.max_followups:
                return (plan.with_check(steps, plan.reask(pending["step"])[1]),
                        {**pending, "followups": pending["followups"] + 1})
            learner.record_evidence(sid, pending["part_id"], "ail_how", 0.0, ts=turn.at, apply="now",
                                    point_id=(pending["step"].get("question") or {}).get("point_id"))
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
        saved = {k: check[k] for k in ("move", "key", "part_id", "data", "question")}
        return plan.with_check(steps, check), {"part_id": part, "followups": 0, "step": saved}
    return steps, None


def _literacy_followup(student_id: str, last: dict, steps: list[dict], evidence: dict | None, request: str,
                       at: str) -> tuple[list[dict], dict | None]:
    """Follow up the literacy task set last turn (step 05e); returns (steps, the task still pending).

    The task is done when a verify task is answered (ail_task) or, for an ask task, when this message is a research
    question (its ail_question is the score). Not done:
    - re-asked already (literacy.max_followups times) and still not done: recorded as ail_task with score 0 on its
      skill's part, and dropped;
    - the plan doesn't end in a question: reask re-asks it in one line;
    - the plan ends in a question: it waits; after literacy.max_waits replies waiting, it takes the next reply's
      question slot in place of the course question (never a how-AI-works check's), and the course resumes after.
    A new session drops it unscored (a task never re-asked is never scored). A new task replaces it."""
    s = _settings().literacy
    task = last.get("literacy")
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
            learner.record_evidence(student_id, task["part_id"], "ail_task", 0.0, ts=at, apply="now")
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
    if not pending or answer or choice in ("just_show_me", "skip_point") or last["ts"] is None:
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


def result_size(result: object) -> int:
    """Characters in a tool result's JSON, as the call log counts them."""
    return len(json.dumps(result, default=str))


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
    lost = False
    try:
        evidence = learner.score_answer(answer, last.get("mcq")) if answer else None
    except learner.LostQuestion:
        evidence, lost = None, True
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    if not node_ids and (evidence or lost):   # an answer continues the last turn's topic (after a prereq check or review too)
        # an AI-literacy part never becomes the course focus
        node_ids = last["focus"] or ([] if graph.is_literacy(answer["part_id"]) else [answer["part_id"]])
    resolution = graph.resolve(message or "", node_ids)
    if not resolution["parts"] and not resolution["candidates"] and last["focus"]:
        resolution = {**graph.resolve("", last["focus"]), "unknown": resolution["unknown"]}
    # a research question is Ask evidence; a verify answer is AI-literacy evidence, not an answer on the course
    recorded = ([evidence] if evidence else []) + (
        [learner.question_evidence(this_message.get("question_features"))]
        if this_message.get("request_type") == "research" else [])
    literacy_answer = bool(evidence and evidence["type"] in learner.LITERACY_ANSWERS)
    tagged = list(dict.fromkeys([e["part_id"] for e in recorded] + resolution["parts"]))
    if tagged and not lost:
        try:
            learner.record_exchange(student["id"], tagged, depth, engagement, choice == "just_show_me",
                                    _support_given(last["plan"]), choice,
                                    evidence["misconception_ids"] if evidence else None,
                                    conflict_flagged=bool(this_message.get("conflict_flagged")), client=client, ts=at,
                                    evidence=recorded or None, apply="now",
                                    request={k: this_message.get(k) for k in REQUEST_LABELS})
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    parts = context_blocks.order_parts(student, resolution["parts"], message or "")
    turn = context_blocks.Turn(student=student, parts=parts, message=message or "", at=at,
                               limits=_context().limits, resolution=resolution)
    profile = learner.profile_of(student)
    blocks = context_blocks.assemble(profile, turn, s, _context())
    config = _context().profiles.get(profile, _context().profiles[_context().default_profile])
    corrected, offered_stop = _this_session(student["id"], last, at)
    pending = _open_question(last, parts, answer, choice, at)
    points = dict(last["points"] or {})
    again = last.get("pending") if lost else None
    if again and not (again["move"] == "ask_mcq" and again["part_id"] == answer["part_id"] and again.get("question")):
        again = None
    request = this_message.get("request_type") or "concept"
    course_answer = None if lost or literacy_answer else answer
    if not config.plan or (request == "other" and not course_answer):
        steps = []
    elif again:   # the letter can't be scored: the same question, freshly shuffled
        steps = plan.add_terms(turn, [plan.ask_again(turn, again)])
    elif request == "research" and not course_answer:   # answered in full with sources, plus a literacy task
        steps = plan.research(turn, blocks, s, this_message.get("question_features") or [])
    else:
        steps = plan.add_terms(turn, plan.choose(turn, blocks, s, choice, course_answer,
                                                 evidence if course_answer else None,
                                                 last["plan"], corrected, offered_stop, pending, points,
                                                 last.get("mcq")))
    if config.plan and this_message.get("source_conflict"):
        steps = plan.with_source_conflict(steps)
    how, literacy, course_steps = None, None, steps
    if config.plan:
        steps, how = _how_ai_works(turn, blocks, last, steps, evidence, this_message)
        steps, literacy = _literacy_followup(student["id"], last, steps, evidence, request, at)
        _unchecked(course_steps, steps, points)
    current_style = style(student, client)
    send_style = _style_due(last, current_style, at)
    _save_plan(student["id"], at, steps, parts, corrected | plan.corrected_in(steps),
               offered_stop or any(step["move"] == "offer_stop" for step in steps), current_style,
               _pending_after(steps, pending), _mcq_after(steps, last), points, literacy, how)
    # with no plan (a comparison profile), answers on the focus parts can still be scored
    next_points = plan.score_next(steps) if config.plan else {
        p: points for p in parts if (points := plan.lettered(p))}
    if request == "research":   # a student who checks a claim unprompted can be scored on the next turn
        next_points.setdefault(learner.AIL_VERIFY, plan.lettered(learner.AIL_VERIFY))

    focus = blocks.get("focus") or {}
    out = {
        "ok": True,
        "plan": public_steps(steps),
        "score_next": next_points,
        "reference": _plan_reference(turn, steps, config.blocks) if config.plan else _reference(blocks),
        "focus": [{"id": p["id"], "name": p["name"], "level": p["level"]} for p in focus.get("parts", [])],
    }
    if send_style:
        out["style"] = current_style
    if focus.get("candidates"):
        out["candidates"] = [{"id": c["id"], "name": c["name"]} for c in focus["candidates"]]
    if resolution["unknown"]:
        out["unknown_ids"] = resolution["unknown"]
    return fit_budget(out)


# --- progress ------------------------------------------------------------------


def _node_entry(student_id: str, node: dict, at: str) -> dict:
    p = learner.rollup(student_id, node["id"], at)
    return {"id": node["id"], "name": node["name"], "level": learner.level(p)}


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
                      "score": importance * (1 - p)})
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
    held = [m["wrong_idea"] for m in context_blocks.held_misconceptions(student_id, graph.parts_of(learner.AIL_HOW))]
    return {
        "ask": {"level": learner.level(learner.part_p(student_id, learner.AIL_ASK, at))},
        "verify": {"level": learner.level(learner.part_p(student_id, learner.AIL_VERIFY, at))},
        "how_ai_works": {"level": learner.level(learner.rollup(student_id, learner.AIL_HOW, at)), "held": held},
        "question_features": {f: _trend(share(f, recent), share(f, before)) for f in learner.QUESTION_FEATURES},
    }


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
    """Tree with levels, the biggest levers, weak links, reviews due, AI-literacy trends, AI-literacy skills (step
    05e) and study pattern. AI-literacy parts are left out of the tree, levers and reviews."""
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
        "ai_literacy": _ai_literacy(student_id, at),
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


def over_budget(tool: str, result_chars: int) -> bool:
    """A tutor_turn result over results.max_chars, after fit_budget dropped what it could."""
    return tool == "tutor_turn" and result_chars > _settings().results.max_chars


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
