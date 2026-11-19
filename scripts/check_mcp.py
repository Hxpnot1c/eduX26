"""Check a running Synapse server through the Python MCP client, without Node or MCP Inspector.

    python scripts/check_mcp.py [--student demo-secure] [--key <key>] [--url http://127.0.0.1:8000/mcp]

Run it from the repo root against a server started on the same data folder (EDUX_DATA_DIR), with the
example-mini pack loaded and the demo students seeded. It:
- resets the demo students (seed-demo --reset keeps their keys), so the run starts from the seeded state;
- lists the tools and prompts;
- runs the point-by-point loop on ped_formula as the student through tutor_turn (intuition MCQ answered wrongly, each point and its
  check, a wrong letter and its re-teach, the explain-back), then an explain-back missing a point and a question
  asked instead of an answer, and checks each plan, the letters scored from the stored map, the misconception
  state, that every reply in the loop ends in one question, every tutor_turn result and the levels-only get_my_progress within the budget (counted as sent), style, known terms,
  watch-for misconceptions, and that no p_now reaches the chatbot;
- checks "I know this", "just show me" (and no discount after it), a lost letter map, a wrong intuition answer
  followed by teaching (demo-weak), a prerequisite check and a
  due review as MCQs (demo-weak, demo-showme), a step back when the same point is missed again after its
  re-teach (demo-showme), and that options are shuffled differently per student;
- runs research questions (demo-weak): answer_with_sources and a literacy task, an ignored task re-asked once then
  counted as a skip with no evidence, Ask and Verify raised, no task on a course question; a task only every literacy.secure_every research
  questions at secure (demo-showme); and how-AI-works checks (demo-secure): cutoff only without web access, a bad
  link's fabrication check with 4 options, one per part per session, an ignored check re-asked then skipped, a
  self-correction's check, and the AI-literacy section of get_my_progress; and, with throwaway students that are
  removed after, no check or task for a fatigued student, and a literacy task taking the question slot after waiting;
- checks the server reports its name as Synapse, and the server instructions' length, that points_met scores the same as letters, full ids, a mix or with
  no saved plan, and that another part's point is refused;
- checks a bad answer is refused and records nothing, get_my_progress, update_my_profile, that a wrong or
  missing key is refused with 401, and that the minimal profile returns no plan;
- checks priorities (a mock beats an extend, no cramming, gaps, add/remove/rebuild, unmatched topics, considered);
- checks reply style (per-step length by mastery and fatigue, answer_length wins, diagram parts);
- checks the engagement rules (a passive streak and its picks, a repeated show, a coasting explain-back) with throwaway students;
- checks the personal learning rate (within bounds, earlier sessions only, never shown);
- checks rebuild gives identical state for every demo student and tutor_turn's median server time is under 100 ms;
- resets the demo students again, so the demo is left as seeded (--keep leaves the run's events).
Exits non-zero if any check fails. The key is read from the database when --key is not given.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import subprocess
import sys
import time
from datetime import timedelta

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from edux import demo, graph, learner, service
from edux.settings import load_settings

EXPECTED_TOOLS = {"tutor_turn", "get_my_progress", "update_my_profile", "plan_my_study"}
EXPECTED_PROMPTS = {"review_due", "check_me"}
PART = "ped_formula"
STATE_TABLES = ("part_state", "student_misconception", "review_queue", "approach_record", "evidence_derived")
INSTRUCTIONS_MAX_WORDS = load_settings().instructions.max_words
PLACEHOLDER = re.compile(r"\{[a-z_]+\}|`name`")
failures: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f": {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def cli(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "edux.cli", *args], check=True, capture_output=True)


def payload(result) -> dict:
    """The JSON a tool returned (structured content if present, else the first text item)."""
    if result.structuredContent is not None:
        return result.structuredContent.get("result", result.structuredContent)
    return json.loads(result.content[0].text) if result.content else {}


ASK_HOW_SURE = False  # the confidence run turns this on; every other run answers as if the chatbot did not ask


async def call(url: str, name: str, arguments: dict) -> dict:
    if name == "tutor_turn" and arguments.get("answer") and not ASK_HOW_SURE:
        arguments = {**arguments, "this_message": {"confidence": "none", **arguments.get("this_message", {})}}  # step 05z
    async with streamablehttp_client(url) as (read, write, _), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(name, arguments)
        if result.isError:
            raise RuntimeError(result.content[0].text if result.content else "tool error")
        return payload(result)


def moves(turn: dict) -> list[str]:
    return [step["move"] for step in turn.get("plan", [])]


def state(student: str) -> dict:
    """The student's derived rows, sorted, leaving out autoincrement ids (rebuild renumbers them)."""
    conn = learner._conn()
    out = {}
    for table in STATE_TABLES:
        columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})") if r["name"] != "id"]
        rows = conn.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE student_id = ?", (student,))
        out[table] = sorted(tuple(r) for r in rows)
    return out


def evidence(student: str, since_id: int) -> list[dict]:
    return [
        dict(r)
        for r in learner._conn().execute("SELECT * FROM evidence_log WHERE student_id = ? AND id > ? ORDER BY id", (student, since_id))
    ]


def max_evidence_id() -> int:
    return learner._conn().execute("SELECT COALESCE(MAX(id), 0) FROM evidence_log").fetchone()[0]


def plan_json(student: str) -> dict:
    row = learner._conn().execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (student,)).fetchone()
    return json.loads(row[0]) if row else {}


def letter(student: str, right: bool) -> tuple[str, str]:
    """(letter, option id) of the correct option, or of a misconception option, in the stored map."""
    options = plan_json(student)["mcq"]["options"]
    return next((k, o["id"]) for k, o in sorted(options.items()) if (o["id"] == "correct") == right and o["id"] != "extra")


def ends_in_one_question(turn: dict) -> bool:
    steps = turn.get("plan", [])
    asking = [s for s in steps if "answer_type" in s["data"]]
    return bool(steps) and len(asking) == 1 and asking[0] is steps[-1]


async def conversation(keyed: str, student: str) -> None:
    """The point-by-point run from the step 05d done-when list on PART: intuition MCQ answered wrongly, point 1 and
    its check, a right letter, point 2, a wrong letter (named and active), one re-teach with no step back (a wrong
    guess and one missed check are not stuck), a right letter, the explain-back; then
    an explain-back missing a point and a question asked instead of an answer (step 05c), with result sizes,
    style, terms and watch-for checks."""
    start = max_evidence_id()
    turns = []
    labels = {"question_depth": "mechanism", "engagement": "active"}

    async def turn(arguments: dict) -> dict:
        if turns:
            time.sleep(1.1)  # event timestamps are to the second; keep the turns in separate seconds
        got = await call(keyed, "tutor_turn", {"client": "check_mcp", **arguments})
        turns.append(got)
        return got

    async def pick(right: bool) -> tuple[dict, str]:
        chosen, option = letter(student, right)
        got = await turn({"message": chosen, "this_message": labels, "answer": {"part_id": PART, "type": "mcq", "choice": chosen}})
        return got, option

    def purposes(t: dict) -> list[str]:
        return [s["move"] + (f":{s['data']['purpose']}" if s["move"] == "ask_mcq" else "") for s in t.get("plan", [])]

    points = graph.score_points(PART)
    first = await turn({"message": "How do I calculate PED?", "this_message": labels})
    data = (first.get("plan") or [{}])[0].get("data") or {}
    check(
        purposes(first) == ["ask_mcq:intuition"] and first["plan"][0]["part_id"] == PART and not first.get("score_next", {}).get(PART),
        "1. an untaught part gets one intuition MCQ, answered by letter",
        ", ".join(purposes(first)) or first.get("error", ""),
    )
    named = [r[0] for r in graph._conn().execute("SELECT id FROM node WHERE name = ?", (data.get("via") or "",))]
    via_known = not data.get("via") or any(learner.level(learner.rollup(student, i)) != "new" for i in named)
    check(
        bool(data.get("note")) and via_known,
        "1. the intuition leads in from a known link or the part's intuition line",
        json.dumps({k: data.get(k) for k in ("note", "via")}),
    )

    second, _ = await pick(False)
    step = (second.get("plan") or [{}, {}])[1:2] or [{}]
    check(
        purposes(second) == ["feedback", "teach_point", "ask_mcq:check"] and step[0].get("data", {}).get("index") == 1,
        "2. a wrong intuition answer gets feedback, then point 1 and its check",
        ", ".join(purposes(second)) or second.get("error", ""),
    )
    third, _ = await pick(True)
    check(
        purposes(third) == ["feedback", "teach_point", "ask_mcq:check"] and third["plan"][1]["data"]["index"] == 2,
        "3. a right letter moves to point 2",
        ", ".join(purposes(third)) or third.get("error", ""),
    )
    fourth, picked = await pick(False)
    named = ((fourth.get("plan") or [{}])[0].get("data") or {}).get("misconceptions") or [{}]
    check(
        purposes(fourth) == ["feedback", "reteach", "ask_mcq:check"] and named[0].get("id") == picked,
        "4. a wrong letter gets feedback naming it, one re-teach of the point and the check again (no step back)",
        ", ".join(purposes(fourth)) or fourth.get("error", ""),
    )
    held = (
        learner._conn()
        .execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?", (student, picked))
        .fetchone()
    )
    check(bool(held and held["active"]), f"4. {picked} is active")
    fifth, _ = await pick(True)
    check(
        purposes(fifth) == ["feedback", "explain_back"] and len(points) == 2,
        "5. after the last point comes the explain-back of the whole part",
        ", ".join(purposes(fifth)) or fifth.get("error", ""),
    )
    recorded = [(e["evidence_type"], e["score"]) for e in evidence(student, start)]
    check(
        recorded == [("prequestion", 0.0), ("mcq_check", 1.0), ("mcq_check", 0.0), ("mcq_check", 1.0)],
        "the server scored every letter from its stored map",
        json.dumps(recorded),
    )
    loop = [first, second, third, fourth, fifth]
    check(
        all(ends_in_one_question(t) for t in loop),
        "every reply in the loop ends in exactly one question",
        "; ".join(", ".join(purposes(t)) for t in loop if not ends_in_one_question(t)),
    )
    words = [s["data"].get("max_words") for t in loop for s in t["plan"] if s["move"] == "teach_point"]
    check(
        bool(words) and all(w == load_settings().points.max_words <= 80 for w in words),
        "every teach_point asks for at most 80 words of explanation",
        json.dumps(words),
    )

    sixth = await turn(
        {
            "message": "You divide the change by the original value and times by 100 for each percentage.",
            "this_message": {"question_depth": "mechanism", "engagement": "constructive"},
            "answer": {"part_id": PART, "type": "explain_back", "points_met": ["a"]},
        }
    )
    missing = ((sixth.get("plan") or [{}, {}])[-1].get("data") or {}).get("missing")
    check(
        purposes(sixth) == ["feedback", "reteach"] and missing == [p["point"] for p in points[1:]],
        "6. an explanation missing a point gets feedback, then reteach with only that point",
        f"{', '.join(purposes(sixth)) or sixth.get('error', '')}; missing {missing}",
    )

    before = max_evidence_id()
    seventh = await turn(
        {"message": "Wait, why do you use the original value and not the new one?", "node_ids": [PART], "this_message": labels}
    )  # a self-correction here would add a how-AI-works check (05e)
    asked = (seventh.get("plan") or [{}, {}])[-1].get("data") or {}
    check(
        purposes(seventh) == ["answer_brief", "reask"]
        and asked.get("asked") == "reteach"
        and asked.get("missing") == missing
        and seventh.get("score_next") == sixth.get("score_next")
        and max_evidence_id() == before,
        "7. a question instead of an answer gets answer_brief, then the same question again, and scores nothing",
        ", ".join(purposes(seventh)) or seventh.get("error", ""),
    )

    untermed = []
    for t in turns:
        on_part = [s for s in t.get("plan", []) if s.get("part_id")]
        if on_part and (on_part[0]["data"].get("terms") or [None])[0] != graph.get_node(on_part[0]["part_id"])["name"]:
            untermed.append(on_part[0]["move"])
    check(not untermed, "each plan lists the known terms once, its first part first", ", ".join(untermed))

    shapes = {tuple(sorted(step)) for t in turns for step in t.get("plan", [])}
    check(shapes == {("cue", "data", "move", "part_id")}, "each step carries only move, part_id, cue and data", json.dumps(sorted(shapes)))
    filled = [step["cue"] for t in turns for step in t.get("plan", []) if PLACEHOLDER.search(json.dumps(step))]
    check(not filled, "no placeholder in any step", "; ".join(filled[:2]))
    bare = [
        i
        for i, t in enumerate(turns, 1)
        if any("answer_type" in s["data"] for s in t.get("plan", []))
        and not ((t.get("reference") or {}).get("misconceptions") or {}).get("watch_for")
    ]
    shapes = {tuple(sorted(w)) for t in turns for w in ((t.get("reference") or {}).get("misconceptions") or {}).get("watch_for") or []}
    check(
        not bare and shapes == {("id", "wrong_idea")},
        "every plan that asks something carries watch-for misconceptions as id and wrong_idea only",
        f"none in turn(s) {bare}" if bare else json.dumps(sorted(shapes)),
    )
    check(
        "style" in turns[0] and not any("style" in t for t in turns[1:]),
        "style comes with the first call of a session only",
        ", ".join(str("style" in t) for t in turns),
    )
    for i, t in enumerate(turns, 1):
        print(f"     turn {i}: {service.result_size(t)} chars")
    sizes = [service.result_size(t) for t in turns]
    limit = load_settings().results.max_chars
    over = (
        learner._conn()
        .execute("SELECT COALESCE(SUM(over_budget), 0) FROM call_log WHERE student_id = ? AND tool = 'tutor_turn'", (student,))
        .fetchone()[0]
    )
    check(
        max(sizes) <= limit and over == 0,
        f"no tutor_turn result is over {limit} characters, none over budget",
        f"median {statistics.median(sizes):.0f}, largest {max(sizes)}, {over} over budget",
    )
    leaked = [i + 1 for i, t in enumerate(turns) if "p_now" in json.dumps(t)]
    check(not leaked, "no p_now in tutor_turn output", f"found in turn(s) {leaked}" if leaked else "")


async def choices(keyed: str, student: str) -> None:
    """ "I know this" goes straight to the check; "just show me" shows the point and ends with its check, with no
    discount on the next answer; a lost letter map records nothing and asks the same question with new letters."""
    other = "pes_definition"
    labels = {"question_depth": "surface", "engagement": "active"}
    time.sleep(1.1)
    skip = await call(
        keyed, "tutor_turn", {"message": "I know this", "node_ids": [other], "this_message": {**labels, "choice": "skip_point"}}
    )
    check(
        [s["move"] for s in skip.get("plan", [])] == ["ask_mcq"] and skip["plan"][0]["data"].get("purpose") == "check",
        '"I know this" goes straight to the check',
        json.dumps([s["move"] for s in skip.get("plan", [])]),
    )

    shown_before = [o["text"] for o in skip["plan"][0]["data"]["options"]] if skip.get("plan") else []
    row = plan_json(student)
    row["mcq"] = None
    with learner._conn() as conn:
        conn.execute("UPDATE issued_plan SET plan_json = ? WHERE student_id = ?", (json.dumps(row), student))
    time.sleep(1.1)
    before, exchanges = max_evidence_id(), learner._conn().execute("SELECT COUNT(*) FROM exchange_log").fetchone()[0]
    again = await call(
        keyed, "tutor_turn", {"message": "A", "this_message": labels, "answer": {"part_id": other, "type": "mcq", "choice": "A"}}
    )
    shown_after = [o["text"] for o in again["plan"][0]["data"]["options"]] if again.get("plan") else []
    check(
        max_evidence_id() == before
        and learner._conn().execute("SELECT COUNT(*) FROM exchange_log").fetchone()[0] == exchanges
        and sorted(shown_after) == sorted(shown_before)
        and shown_after != shown_before,
        "with the map deleted, an answer records nothing and the same question comes back with new letters",
        json.dumps(shown_after),
    )

    time.sleep(1.1)
    show = await call(
        keyed,
        "tutor_turn",
        {"message": "just show me", "node_ids": ["yed_definition"], "this_message": {**labels, "choice": "just_show_me"}},
    )
    check(
        [s["move"] for s in show.get("plan", [])] == ["show", "ask_mcq"],
        '"just show me" shows the point and ends with its check',
        json.dumps([s["move"] for s in show.get("plan", [])]),
    )
    chosen, _ = letter(student, True)
    time.sleep(1.1)
    await call(
        keyed,
        "tutor_turn",
        {"message": chosen, "this_message": labels, "answer": {"part_id": "yed_definition", "type": "mcq", "choice": chosen}},
    )
    left = learner._conn().execute("SELECT COALESCE(MAX(offload_left), 0) FROM part_state WHERE student_id = ?", (student,)).fetchone()[0]
    check(left == 0, 'after "just show me", the next answer is not discounted (offload_left stays 0)', str(left))


async def wrong_intuition(url: str) -> None:
    """A wrong intuition answer is followed by teaching, never by another intuition question (demo-weak)."""
    student, part = "demo-weak", "pes_formula"
    keyed = f"{url}?key={demo.demo_keys()[student]}"
    labels = {"question_depth": "surface", "engagement": "active"}
    got = await call(
        keyed, "tutor_turn", {"message": "How do I work out PES?", "node_ids": [part], "client": "check_mcp", "this_message": labels}
    )
    if [s["data"].get("purpose") for s in got.get("plan", [])] != ["intuition"]:
        check(False, "a wrong intuition answer is followed by teaching", "no intuition question to answer")
        return
    chosen, picked = letter(student, False)
    time.sleep(1.1)
    got = await call(
        keyed,
        "tutor_turn",
        {"message": chosen, "client": "check_mcp", "this_message": labels, "answer": {"part_id": part, "type": "mcq", "choice": chosen}},
    )
    moves_ = [s["move"] + (f":{s['data']['purpose']}" if s["move"] == "ask_mcq" else "") for s in got.get("plan", [])]
    named = (got.get("plan") or [{}])[0].get("data", {}).get("misconceptions") or [{}]
    check(
        moves_ == ["feedback", "teach_point", "ask_mcq:check"] and named[0].get("id") == picked,
        "a wrong intuition answer gets feedback naming it, then teaching, not another intuition question",
        ", ".join(moves_) or got.get("error", ""),
    )


async def prerequisite_and_review(url: str) -> None:
    """A prerequisite check (demo-weak) and a due review (demo-showme) come as ask_mcq and are scored from the letter."""
    for student, message, purpose in (
        ("demo-weak", "How do I calculate PED?", "prereq"),
        ("demo-showme", "quiz me on what's due", "review"),
    ):
        keyed = f"{url}?key={demo.demo_keys()[student]}"
        got = await call(
            keyed,
            "tutor_turn",
            {"message": message, "client": "check_mcp", "this_message": {"question_depth": "surface", "engagement": "active"}},
        )
        step = (got.get("plan") or [{}])[-1]
        check(
            step.get("move") == "ask_mcq" and step.get("data", {}).get("purpose") == purpose,
            f"{student}: a {purpose} question comes as ask_mcq",
            json.dumps([s["move"] for s in got.get("plan", [])]),
        )
        if step.get("move") != "ask_mcq":
            continue
        chosen, _ = letter(student, True)
        before = max_evidence_id()
        time.sleep(1.1)
        await call(
            keyed,
            "tutor_turn",
            {
                "message": chosen,
                "client": "check_mcp",
                "this_message": {"question_depth": "surface", "engagement": "active"},
                "answer": {"part_id": step["part_id"], "type": "mcq", "choice": chosen},
            },
        )
        scored = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
        check(scored == [(step["part_id"], "mcq_check", 1.0)], f"{student}: the {purpose} letter is scored", json.dumps(scored))


async def stuck_on_point(url: str) -> None:
    """The same point missed on its check and again on the re-check after its reteach makes the part stuck: the
    next plan steps back (demo-showme on PART, intuition answered right). The plan left by the review run is
    cleared first, so the question here isn't taken as a detour from a pending one."""
    student = "demo-showme"
    keyed = f"{url}?key={demo.demo_keys()[student]}"
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
    labels = {"question_depth": "surface", "engagement": "active"}
    before = max_evidence_id()
    got = await call(
        keyed, "tutor_turn", {"message": "How do I calculate PED?", "node_ids": [PART], "client": "check_mcp", "this_message": labels}
    )
    for right in (True, False, False):
        if (got.get("plan") or [{}])[-1].get("move") != "ask_mcq":
            break
        chosen, _ = letter(student, right)
        time.sleep(1.1)
        got = await call(
            keyed,
            "tutor_turn",
            {
                "message": chosen,
                "client": "check_mcp",
                "this_message": labels,
                "answer": {"part_id": PART, "type": "mcq", "choice": chosen},
            },
        )
    steps = got.get("plan") or []
    stepped_back = any(s["data"].get("stuck") or (s["move"] == "reteach" and s["data"].get("answer_type") == "explain_back") for s in steps)
    missed = {e["point_id"] for e in evidence(student, before) if e["evidence_type"] == "mcq_check" and e["score"] == 0}
    check(
        stepped_back and len(missed) == 1,
        "the same point missed again after its reteach is stuck: the plan steps back",
        ", ".join(s["move"] + (":stuck" if s["data"].get("stuck") else "") for s in steps) or got.get("error", ""),
    )


async def research_questions(url: str) -> None:
    """Research questions and the literacy task (step 05e, demo-weak): answer_with_sources then literacy_task, an
    ignored task re-asked once then counted as a skip (missing, not 0), Ask and Verify raised by a well-phrased question and an answered
    verify task, and no literacy task on a course question."""
    student = "demo-weak"
    keyed = f"{url}?key={demo.demo_keys()[student]}"
    labels = {"question_depth": "surface", "engagement": "active"}
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))

    async def turn(message: str, extra: dict, answer: dict | None = None) -> dict:
        time.sleep(1.1)
        args = {"message": message, "client": "check_mcp", "this_message": {**labels, **extra}}
        if answer:
            args["answer"] = answer
        return await call(keyed, "tutor_turn", args)

    def p(part: str) -> float:
        return learner.part_p(student, part)

    vague = {"request_type": "research", "question_features": ["concept"], "web_access": True}
    before = max_evidence_id()
    got = await turn("how much does petrol cost?", vague)
    task = (got.get("plan") or [{}, {}])[-1]
    check(
        moves(got) == ["answer_with_sources", "literacy_task"]
        and task.get("data", {}).get("skill") == "ask"
        and task["data"].get("task") is True
        and bool(task["data"].get("pattern"))
        and "ail_verify" in got.get("score_next", {}),
        "a research question gets answer_with_sources, then a literacy task with a feedback pattern and a task",
        json.dumps([(s["move"], s["data"].get("skill"), s["data"].get("task")) for s in got.get("plan", [])]),
    )
    asked = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
    check(asked == [("ail_ask", "ail_question", 0.25)], "the question is Ask evidence: features present / 4", json.dumps(asked))

    got = await turn("ok thanks", {"request_type": "other"})
    check(
        moves(got) == ["reask"] and got["plan"][0]["data"].get("asked") == "literacy_task",
        "an ignored literacy task is re-asked once",
        json.dumps(moves(got)),
    )
    before, skipped = max_evidence_id(), learner.skips(student, ["ail_ask"])
    got = await turn("nice", {"request_type": "other"})
    zero = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
    check(
        moves(got) == []
        and zero == []
        and learner.skips(student, ["ail_ask"]) == skipped + 1
        and plan_json(student).get("literacy") is None,
        "still ignored, it is counted as a skip (no evidence) and dropped",
        f"{moves(got)} {json.dumps(zero)}",
    )

    ask_before = p("ail_ask")
    sharp = {"request_type": "research", "question_features": ["concept", "context", "asks_sources", "asks_reasoning"], "web_access": True}
    got = await turn("How did UK petrol prices change in 2025, and why? Give sources.", sharp)
    task = (got.get("plan") or [{}])[-1]
    check(
        p("ail_ask") > ask_before and task.get("data", {}).get("skill") == "verify" and task["data"].get("answer_type") == "ail_task",
        "a well-phrased question raises ail_ask and gets a verify task",
        f"{ask_before:.2f} -> {p('ail_ask'):.2f}",
    )
    verify_before = p("ail_verify")
    got = await turn(
        "I opened the ONS page: March 2025, and the figure matched.",
        {"request_type": "other"},
        {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "b", "c", "d"]},
    )
    check(
        p("ail_verify") > verify_before and plan_json(student).get("literacy") is None,
        "answering the verify task raises ail_verify and clears it",
        f"{verify_before:.2f} -> {p('ail_verify'):.2f}",
    )

    got = await turn("How do I calculate PED?", {"request_type": "concept"})
    check(
        not {"literacy_task", "answer_with_sources"} & set(moves(got)),
        "a course question never gets a literacy task",
        json.dumps(moves(got)),
    )


async def secure_every(url: str) -> None:
    """At secure, the literacy task comes only every literacy.secure_every research questions (demo-showme)."""
    student = "demo-showme"
    keyed = f"{url}?key={demo.demo_keys()[student]}"
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
    for _ in range(8):  # unprompted checks until Verify is secure
        if learner.level(learner.part_p(student, "ail_verify")) == "secure":
            break
        learner.record_evidence(student, "ail_verify", "ail_unprompted", 1.0, apply="now")
    every = load_settings().literacy.secure_every
    tasks = []
    for _ in range(every):
        time.sleep(1.1)
        got = await call(
            keyed,
            "tutor_turn",
            {
                "message": "What was UK inflation last year, and why? Sources please.",
                "client": "check_mcp",
                "this_message": {
                    "question_depth": "mechanism",
                    "engagement": "active",
                    "request_type": "research",
                    "question_features": ["concept", "context", "asks_sources"],
                    "web_access": True,
                },
            },
        )
        step = next((s for s in got.get("plan", []) if s["move"] == "literacy_task"), {})
        tasks.append(bool(step.get("data", {}).get("task")))
    check(
        learner.level(learner.part_p(student, "ail_verify")) == "secure" and tasks.count(True) == 1,
        f"at secure, a task comes once in {every} research questions (the rest get the feedback line only)",
        json.dumps(tasks),
    )


async def how_ai_works(url: str) -> None:
    """How-AI-works checks (step 05e, demo-secure): cutoff only with asks_recent and no web access; a bad link
    gets the correction then a 4-option check on fabrication (a right letter raises it, a wrong one activates the
    misconception); one check per part per session; an ignored check re-asked once then skipped (no evidence); a
    self-correction gets a check on confidence and is stored."""
    student = "demo-secure"
    keyed = f"{url}?key={demo.demo_keys()[student]}"
    labels = {"question_depth": "surface", "engagement": "active"}
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))

    async def turn(message: str, extra: dict, answer: dict | None = None) -> dict:
        time.sleep(1.1)
        args = {"message": message, "client": "check_mcp", "this_message": {**labels, **extra}}
        if answer:
            args["answer"] = answer
        return await call(keyed, "tutor_turn", args)

    def how(got: dict) -> dict:
        return next((s for s in got.get("plan", []) if s["data"].get("purpose") == "how_ai_works"), {})

    recent = {"request_type": "research", "question_features": ["concept", "context"], "asks_recent": True}
    got = await turn("What did the Bank of England do with rates last week?", {**recent, "web_access": True})
    check(not how(got), "cutoff: no check when the chatbot can search the web", json.dumps(moves(got)))
    got = await turn("What is a price index?", {**recent, "asks_recent": False, "web_access": False})
    check(not how(got), "cutoff: no check when the question isn't about recent events", json.dumps(moves(got)))
    got = await turn("What did the Bank of England do with rates last week?", {**recent, "web_access": False})
    step = how(got)
    check(
        step.get("part_id") == "ail_how_cutoff" and moves(got)[-1] == "ask_mcq" and "literacy_task" not in moves(got),
        "cutoff: asks_recent with no web access gets a check, which wins over the literacy task",
        json.dumps(moves(got)),
    )
    if step:
        chosen, _ = letter(student, True)
        before = learner.part_p(student, "ail_how_cutoff")
        await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_cutoff", "type": "mcq", "choice": chosen})
        check(learner.part_p(student, "ail_how_cutoff") > before, "a right letter raises the how-AI-works part")

    got = await turn(
        "That ONS link you gave me doesn't work.", {"request_type": "research", "source_conflict": True, "question_features": ["context"]}
    )
    step = how(got)
    check(
        moves(got)[0] == "source_conflict" and step.get("part_id") == "ail_how_fabrication" and len(step["data"].get("options", [])) == 4,
        "a bad link gets source_conflict first, then a 4-option check on fabrication",
        json.dumps(moves(got)),
    )
    if step:
        chosen, picked = letter(student, False)
        got = await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_fabrication", "type": "mcq", "choice": chosen})
        held = (
            learner._conn()
            .execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?", (student, picked))
            .fetchone()
        )
        data = (got.get("plan") or [{}])[0].get("data", {})
        check(
            bool(held and held["active"]) and bool(data.get("intuition")),
            "a wrong letter activates the picked misconception; the feedback carries the intuition line",
            picked,
        )
    got = await turn("Another link is dead too.", {"request_type": "research", "source_conflict": True, "question_features": ["context"]})
    check(not how(got), "a second failure of the same type in a session gets no second check", json.dumps(moves(got)))

    got = await turn("No, I think you were right the first time.", {"request_type": "concept", "pushback_changed": True})
    check(
        how(got).get("part_id") == "ail_how_agreement", "a changed answer after pushback gets a check on agreement", json.dumps(moves(got))
    )
    got = await turn("ok", {"request_type": "other"})
    check(moves(got) == ["reask"], "an ignored check is re-asked once", json.dumps(moves(got)))
    before, skipped = max_evidence_id(), learner.skips(student, ["ail_how_agreement"])
    await turn("fine", {"request_type": "other"})
    zero = [(e["part_id"], e["evidence_type"], e["score"], e["point_id"]) for e in evidence(student, before)]
    check(
        zero == [] and learner.skips(student, ["ail_how_agreement"]) == skipped + 1,
        "still not answered, it is counted as a skip, with no evidence",
        json.dumps(zero),
    )

    got = await turn("Sorry, which formula was it?", {"request_type": "concept", "conflict_flagged": True})
    flagged = (
        learner._conn()
        .execute("SELECT conflict_flagged FROM exchange_log WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student,))
        .fetchone()
    )
    check(
        how(got).get("part_id") == "ail_how_confidence" and bool(flagged and flagged[0] == 1),
        "a self-correction is stored and gets a check on confidence",
        json.dumps(moves(got)),
    )
    if how(got):  # answer it, so the checks after this one start with nothing pending
        chosen, _ = letter(student, True)
        await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_confidence", "type": "mcq", "choice": chosen})
    progress = await call(keyed, "get_my_progress", {})
    lit = progress.get("ai_literacy") or {}
    check(
        {"ask", "verify", "how_ai_works", "question_features"} <= set(lit) and bool(lit["how_ai_works"].get("held")),
        "get_my_progress shows AI-literacy skills, with the wrong ideas about AI still held",
        json.dumps(lit.get("how_ai_works")),
    )


THROWAWAY_TABLES = (
    "student_profile",
    "student_assessment",
    "exchange_log",
    "part_state",
    "student_misconception",
    "approach_record",
    "review_queue",
    "evidence_derived",
    "evidence_log",
    "call_log",
    "issued_plan",
    "literacy_skip",
)


def drop_student(student: str) -> None:
    """Remove a throwaway check student and every row about them (learner.delete_student finds every table)."""
    if learner.get_student(student) is not None:
        learner.delete_student(student)


def new_student(student: str) -> str:
    """A fresh throwaway student for one run; returns their keyed URL suffix (the key)."""
    drop_student(student)
    course = learner._conn().execute("SELECT id FROM content.course").fetchone()[0]
    return learner.add_student(student, course, student_id=student)["key"]


async def find_error_run(url: str) -> None:
    """Find-the-error practice (decision 0012). Off by default: a finished part ends as before, with no practice item.
    Switched on (EDUX_FIND_ERROR=1 for the server and this check): the item is labelled as practice and shows no answer,
    its answer is scored on the server against the item it kept, recorded on the part and on Verify as its own type, and
    the correct statement is always given afterwards."""
    student = "check-error"
    keyed = f"{url}?key={new_student(student)}"
    labels = {"question_depth": "mechanism", "engagement": "constructive"}
    try:
        now = learner.parse_ts(learner.now_iso())
        for part in ("ped_definition", "ped_formula"):
            for i in range(3):
                learner.record_evidence(
                    student, part, "explain_back", 1.0, apply="now", ts=learner._event_ts(now - timedelta(days=3, minutes=10 * (3 - i)))
                )
        got = await call(
            keyed,
            "tutor_turn",
            {"message": "Let's go back over the PED formula", "client": "check_mcp", "node_ids": ["ped_formula"], "this_message": labels},
        )
        letters = [p["id"] for p in got.get("score_next", {}).get("ped_formula", [])]
        done = await call(
            keyed,
            "tutor_turn",
            {
                "message": "my explanation",
                "client": "check_mcp",
                "node_ids": ["ped_formula"],
                "this_message": labels,
                "answer": {"part_id": "ped_formula", "type": "explain_back", "points_met": letters},
            },
        )
        step = next(
            (s for s in done.get("plan", []) if s["move"] == "say_line" and "Practice, not a real answer" in s["data"].get("line", "")),
            None,
        )
        if not learner.find_error_on():
            check(step is None, "find-the-error practice is off by default: a finished part never offers an item", json.dumps(moves(done)))
            return
        check(
            step is not None
            and step["data"]["answer_type"] == "find_error"
            and "one mistake, or none" in step["data"]["line"]
            and "item" not in json.dumps(step).lower()
            and "misconception" not in json.dumps(step).lower(),
            "a finished part offers a find-the-error item, labelled as practice, with nothing that gives the answer away",
            json.dumps(moves(done)),
        )
        if step is None:
            return
        item = next(s for s in plan_json(student)["plan"] if s.get("key") == "say_line_find_error")["item"]
        ticked = ["a", "b", "c"] if item["kind"] == "error" else ["d"]
        scored = [p["id"] for p in done["score_next"].get("ped_formula", [])]
        check(scored == ["a", "b", "c", "d"], "the four answer letters are the same for every item", json.dumps(scored))
        after = await call(
            keyed,
            "tutor_turn",
            {
                "message": "my answer",
                "client": "check_mcp",
                "node_ids": ["ped_formula"],
                "this_message": labels,
                "answer": {"part_id": "ped_formula", "type": "find_error", "points_met": ticked},
            },
        )
        fb = next((s for s in after.get("plan", []) if s["move"] == "feedback"), {})
        rows = (
            learner._conn()
            .execute(
                "SELECT part_id, evidence_type, score FROM evidence_log WHERE student_id = ? AND evidence_type "
                "IN ('find_error', 'ail_find_error') ORDER BY id",
                (student,),
            )
            .fetchall()
        )
        check(
            fb.get("data", {}).get("correct") is True
            and bool(fb["data"].get("correct_option"))
            and [(r["part_id"], r["evidence_type"], r["score"]) for r in rows]
            == [("ped_formula", "find_error", 1.0), ("ail_verify", "ail_find_error", 1.0)],
            "the answer is scored on the server, recorded on the part and on Verify as its own type, and the correct statement is given",
            f"{json.dumps(moves(after))} {[(r['part_id'], r['evidence_type']) for r in rows]}",
        )
    finally:
        drop_student(student)


async def calibration(url: str) -> None:
    """ "How sure are you?" (step 05z, decision 0027): asked only on the second rapid-guess check answer in a row (here two
    one-word answers sent at once, faster than the question can be read), keeping the feedback back one turn; the reply
    stores the rating, and the rating never changes what the model thinks they know. The answers on the way send no
    word count, so they are never rapid guesses."""
    global ASK_HOW_SURE
    student = "check-sure"
    keyed = f"{url}?key={new_student(student)}"
    labels = {"question_depth": "mechanism", "engagement": "active"}
    ASK_HOW_SURE = True
    try:
        out = await call(
            keyed, "tutor_turn", {"message": "Teach me the PED formula", "client": "check_mcp", "node_ids": [PART], "this_message": labels}
        )
        for _ in range(4):  # answer any pre-question until the first check
            step = next((s for s in out["plan"] if s["move"] == "ask_mcq"), None)
            if step is None or step["data"].get("purpose") == "check":
                break
            chosen, _ = letter(student, True)
            out = await call(
                keyed,
                "tutor_turn",
                {
                    "message": chosen,
                    "client": "check_mcp",
                    "node_ids": [PART],
                    "this_message": labels,
                    "answer": {"part_id": step["part_id"], "type": step["data"]["answer_type"], "choice": chosen},
                },
            )
        step = next((s for s in out["plan"] if s["move"] == "ask_mcq" and s["data"].get("purpose") == "check"), None)
        check(step is not None, "the loop reaches a check question", json.dumps(moves(out)))
        if step is None:
            return

        async def rapid_answer(step: dict) -> dict:
            chosen, _ = letter(student, True)
            return await call(
                keyed,
                "tutor_turn",
                {
                    "message": chosen,
                    "client": "check_mcp",
                    "node_ids": [PART],
                    "this_message": {**labels, "words": 1},
                    "answer": {"part_id": step["part_id"], "type": "mcq", "choice": chosen},
                },
            )

        first = await rapid_answer(step)
        check(
            "say_line" not in moves(first),
            "one rapid-guess check answer is not enough: the feedback comes at once",
            json.dumps(moves(first)),
        )
        step = next((s for s in first["plan"] if s["move"] == "ask_mcq" and s["data"].get("purpose") == "check"), None)
        check(step is not None, "a second check follows the first", json.dumps(moves(first)))
        if step is None:
            return
        asked = await rapid_answer(step)
        if not learner.confidence_on():  # switched off (EDUX_CONFIDENCE=0, as for filming): nothing is asked and nothing is held back
            check(
                moves(asked)[:1] == ["feedback"] and "how sure" not in json.dumps(asked).lower(),
                "with the question switched off (EDUX_CONFIDENCE=0) a check answer gets its feedback at once and nothing is asked",
                json.dumps(moves(asked)),
            )
            return
        check(
            moves(asked) == ["say_line"] and asked["score_next"] == {} and "how sure" in asked["plan"][0]["data"]["line"].lower(),
            "after a second rapid-guess check in a row the reply asks how sure they are and keeps the feedback back",
            json.dumps(moves(asked)),
        )
        before = {
            r["part_id"]: round(r["p_known"], 9)
            for r in learner._conn().execute("SELECT part_id, p_known FROM part_state WHERE student_id = ?", (student,))
        }
        time.sleep(1.1)
        given = await call(
            keyed,
            "tutor_turn",
            {"message": "fairly sure", "client": "check_mcp", "node_ids": [PART], "this_message": {**labels, "confidence": "fairly_sure"}},
        )
        rating = learner._conn().execute("SELECT level FROM confidence_log WHERE student_id = ?", (student,)).fetchone()
        check(
            moves(given)[:1] == ["feedback"] and rating and rating["level"] == "fairly_sure",
            "the reply to 'how sure' delivers the held feedback and stores the rating",
            f"{json.dumps(moves(given))} {rating and rating['level']}",
        )
        after = {
            r["part_id"]: round(r["p_known"], 9)
            for r in learner._conn().execute("SELECT part_id, p_known FROM part_state WHERE student_id = ?", (student,))
        }
        check(
            all(after.get(p) is not None and abs(after[p] - v) < 1e-9 for p, v in before.items() if p == step["part_id"]),
            "the rating does not change what the model thinks they know",
            json.dumps(after),
        )
    finally:
        ASK_HOW_SURE = False
        drop_student(student)


async def class_assessments(url: str) -> None:
    """Class assessments, reminders and study plans (step 05u): a teacher-set test reaches a member, the first call of a
    session mentions what is due this week (once, and not a test 16 days away), plan_my_study gives a day-by-day plan
    within the budget, and a written assignment gets stages that say what to do, never what to write."""
    student = "check-class"
    keyed = f"{url}?key={new_student(student)}"
    class_id = learner.add_class("Check class")
    try:
        learner.add_students_to_class(class_id, [student])
        today = learner.parse_ts(learner.now_iso()).date()
        parts = graph.parts_of("elasticities")
        learner.add_class_assessment(class_id, "Class test", "class_test", (today + timedelta(days=3)).isoformat(), parts)
        essay = learner.add_class_assessment(class_id, "Essay", "written_assignment", (today + timedelta(days=16)).isoformat(), parts)
        labels = {"question_depth": "surface", "engagement": "active"}
        first = await call(
            keyed, "tutor_turn", {"message": "How do I calculate PED?", "client": "check_mcp", "node_ids": [PART], "this_message": labels}
        )
        time.sleep(1.1)
        second = await call(
            keyed,
            "tutor_turn",
            {"message": "And what does a value of 2 mean?", "client": "check_mcp", "node_ids": [PART], "this_message": labels},
        )
        names = [i["name"] for i in (first.get("upcoming") or {}).get("items", [])]
        check(
            names == ["Class test"] and "upcoming" not in second,
            "the first call of a session mentions a test due this week, once, and not one 16 days away",
            f"{names} then {'upcoming' in second}",
        )
        plan_out = await call(keyed, "plan_my_study", {})
        check(
            plan_out.get("ok")
            and plan_out["assessment"]["name"] == "Class test"
            and plan_out["sessions"][-1]["kind"] == "mixed practice"
            and service.result_size(plan_out) <= load_settings().results.max_chars,
            "plan_my_study gives a dated plan for the soonest test, ending with mixed practice, within the budget",
            f"{len(plan_out.get('sessions', []))} sessions, {service.result_size(plan_out)} characters",
        )
        written = await call(keyed, "plan_my_study", {"assessment_id": essay})
        check(
            written.get("ok")
            and [x["stage"] for x in written["stages"]] == ["knowledge", "application", "analysis", "evaluation"]
            and "sessions" not in written,
            "a written assignment gets four dated stages and no sessions",
            json.dumps([x["stage"] for x in written.get("stages", [])]),
        )
        removed = await call(keyed, "update_my_profile", {"remove_assessment": {"id": essay}})
        check(
            removed.get("ok") is False and "teacher" in removed.get("error", ""),
            "a student cannot remove an assessment their teacher set",
            json.dumps(removed)[:100],
        )
    finally:
        with learner._conn() as conn:
            conn.execute("DELETE FROM student_assessment WHERE class_id = ?", (class_id,))
            conn.execute("UPDATE student SET class_id = NULL WHERE class_id = ?", (class_id,))
            conn.execute("DELETE FROM class WHERE id = ?", (class_id,))
        drop_student(student)


async def bridge(url: str) -> None:
    """The reply's ending (step 05t): when a part is finished, the ending is a bridge question towards the next topic
    (the pre-question move, with data.link); after its answer the first teach step says they can stop or switch, and
    stop gives the session summary; neither forces the target part."""
    student = "check-bridge"
    keyed = f"{url}?key={new_student(student)}"
    labels = {"question_depth": "mechanism", "engagement": "constructive"}
    try:
        now = learner.parse_ts(learner.now_iso())
        for part in ("ped_definition", "ped_formula"):
            for i in range(3):
                learner.record_evidence(
                    student, part, "explain_back", 1.0, apply="now", ts=learner._event_ts(now - timedelta(days=3, minutes=10 * (3 - i)))
                )
        got = await call(
            keyed,
            "tutor_turn",
            {"message": "Let's go back over the PED formula", "client": "check_mcp", "node_ids": ["ped_formula"], "this_message": labels},
        )
        letters = [p["id"] for p in got.get("score_next", {}).get("ped_formula", [])]
        done = await call(
            keyed,
            "tutor_turn",
            {
                "message": "my explanation",
                "client": "check_mcp",
                "node_ids": ["ped_formula"],
                "this_message": labels,
                "answer": {"part_id": "ped_formula", "type": "explain_back", "points_met": letters},
            },
        )
        if learner.find_error_on():  # find-the-error practice takes the ending when switched on; checked in find_error_run
            return
        step = next((s for s in done.get("plan", []) if s["move"] == "ask_mcq" and s["data"].get("bridge")), None)
        link = (step or {}).get("data", {}).get("link", {})
        check(
            step is not None and link.get("from") == "ped_formula" and link.get("to") == step["part_id"] != "ped_formula",
            "a finished part ends with a bridge question towards the next topic, carrying data.link",
            json.dumps(moves(done)) + " " + json.dumps(link),
        )
        if step is None:
            return
        chosen, _ = letter(student, True)
        after = await call(
            keyed,
            "tutor_turn",
            {
                "message": chosen,
                "client": "check_mcp",
                "this_message": labels,
                "answer": {"part_id": step["part_id"], "type": step["data"]["answer_type"], "choice": chosen},
            },
        )
        teach_step = next((s for s in after.get("plan", []) if s["move"] == "teach_point"), {})
        check(
            moves(after)[:1] == ["feedback"]
            and teach_step.get("part_id") == step["part_id"]
            and "stop or switch" in teach_step.get("cue", ""),
            "after the bridge answer: feedback, then the first teach step on the target, which says they can stop or switch",
            json.dumps(moves(after)) + " " + teach_step.get("cue", "")[:80],
        )
        stop = await call(
            keyed, "tutor_turn", {"message": "that's enough for today", "client": "check_mcp", "this_message": {**labels, "choice": "stop"}}
        )
        check(
            moves(stop) == ["session_summary"],
            "stop after a bridge gives the session summary and does not force the target part",
            json.dumps(moves(stop)),
        )
    finally:
        drop_student(student)


async def coverage(url: str) -> None:
    """What a student says their class covered (step 05q): matched and unmatched topics come back, and the progress view
    shows the covered, untouched topic as "taught in class, not yet checked", never developing or secure."""
    student = "check-covered"
    keyed = f"{url}?key={new_student(student)}"
    try:
        bad = await call(keyed, "update_my_profile", {"covered_in_class": {"topics": ["not a topic"]}})
        check(
            bad.get("ok") is False and bad.get("topics"),
            "covered_in_class with no match returns the pack's topics to pick from",
            json.dumps(bad)[:120],
        )
        got = await call(keyed, "update_my_profile", {"covered_in_class": {"topics": ["PED", "nonsense"], "when": "2026-10-01"}})
        check(
            got.get("ok") is True and got["covered"]["unmatched"] == ["nonsense"] and got["covered"]["taught_on"] == "2026-10-01",
            "covered_in_class matches topics and returns the unmatched ones",
            json.dumps(got.get("covered")),
        )
        progress = await call(keyed, "get_my_progress", {"include_parts": True})
        levels = {}

        def walk(nodes):
            for n in nodes:
                levels[n["id"]] = n["level"]
                walk(n.get("children", []))

        walk(progress["tree"])
        check(
            levels.get("ped") == "taught_in_class"
            and levels.get("ped_definition") == "taught_in_class"
            and not {"developing", "secure"} & {levels[k] for k in ("ped", "ped_definition", "ped_formula", "pes")},
            "a covered part with no answer shows 'taught in class', and an uncovered one shows new, never developing or secure",
            json.dumps({k: levels.get(k) for k in ("ped", "ped_definition", "pes")}),
        )
    finally:
        drop_student(student)


async def rushing_student(url: str) -> None:
    """Two answers faster than the question can be read (step 05s) start rushing mode: the plan offers a change in
    plain words (data.line), not a comment on tiredness. Answers sent without a word count are never flagged."""
    student = "check-rushing"
    keyed = f"{url}?key={new_student(student)}"
    try:
        labels = {"question_depth": "surface", "engagement": "active", "words": 1}
        await call(
            keyed,
            "tutor_turn",
            {"message": "Teach me PED", "client": "check_mcp", "node_ids": [PART], "this_message": {**labels, "words": 4}},
        )
        got = None
        for _ in range(4):  # answer each question at once, with a word count, until the offer comes
            time.sleep(1.1)
            pending = plan_json(student).get("pending") or {}
            if not plan_json(student).get("mcq") or not pending.get("part_id"):
                break
            chosen, _ = letter(student, True)
            got = await call(
                keyed,
                "tutor_turn",
                {
                    "message": chosen,
                    "client": "check_mcp",
                    "this_message": labels,
                    "answer": {"part_id": pending["part_id"], "type": "mcq", "choice": chosen},
                },
            )
            if "offer_choice" in moves(got):
                break
        state_now = learner.session_state(student) or {}
        offer = next((s for s in (got or {}).get("plan", []) if s["move"] == "offer_choice"), {})
        check(
            state_now.get("fatigue_reason") == "rushing"
            and state_now.get("rapid_guesses", 0) >= 2
            and "rushing" in (offer.get("data") or {}).get("line", "")
            and not {"tired", "tiredness", "fatigue", "fatigued"} & set((offer.get("data") or {}).get("line", "").lower().split()),
            "two answers faster than the question can be read start rushing mode, offered as pacing (no tiredness wording)",
            f"{json.dumps(moves(got or {}))} rapid={state_now.get('rapid_guesses')} reason={state_now.get('fatigue_reason')}",
        )
    finally:
        drop_student(student)


async def fatigued_student(url: str) -> None:
    """A student in long-session mode whose link failed gets the correction, but no how-AI-works check and no literacy
    task (step 05e). The mode comes from time on task (step 05s): right answers every few minutes for 55 minutes."""
    student = "check-fatigued"
    keyed = f"{url}?key={new_student(student)}"
    try:
        now = learner.parse_ts(learner.now_iso())
        for minutes, part, score in (
            (-55, "ped_formula", 1),
            (-48, "yed_definition", 1),
            (-41, "ped_formula", 1),
            (-34, "yed_definition", 1),
            (-27, "ped_formula", 1),
            (-20, "yed_definition", 1),
            (-13, "ped_formula", 1),
            (-6, "yed_definition", 1),
        ):
            learner.record_evidence(
                student, part, "explain_back", float(score), ts=learner._event_ts(now + timedelta(minutes=minutes)), apply="now"
            )
        tired = bool((learner.session_state(student) or {}).get("fatigued"))
        got = await call(
            keyed,
            "tutor_turn",
            {
                "message": "That link you gave me doesn't work.",
                "client": "check_mcp",
                "this_message": {
                    "question_depth": "surface",
                    "engagement": "active",
                    "request_type": "research",
                    "source_conflict": True,
                    "question_features": ["context"],
                },
            },
        )
        check(
            tired and moves(got)[:1] == ["source_conflict"] and "ask_mcq" not in moves(got) and "literacy_task" not in moves(got),
            "a fatigued student gets the correction, with no how-AI-works check and no literacy task",
            f"fatigued={tired} {json.dumps(moves(got))}",
        )
    finally:
        drop_student(student)


async def waiting_task(url: str) -> None:
    """A literacy task behind course questions waits two replies, then takes the next reply's question slot; the
    course check it displaced comes alone in the reply after, and the ignored re-ask is a skip (step 05e)."""
    student = "check-waiting"
    keyed = f"{url}?key={new_student(student)}"
    labels = {"question_depth": "surface", "engagement": "active", "request_type": "concept"}

    async def turn(message: str, extra: dict | None = None, **more) -> dict:
        time.sleep(1.1)
        return await call(
            keyed, "tutor_turn", {"message": message, "client": "check_mcp", "this_message": {**labels, **(extra or {})}, **more}
        )

    async def right() -> dict:
        chosen, _ = letter(student, True)
        return await turn(chosen, answer={"part_id": PART, "type": "mcq", "choice": chosen})

    def purposes(t: dict) -> list[str]:
        return [
            s["move"] + (f":{s['data'].get('purpose') or s['data'].get('asked')}" if s["move"] in ("ask_mcq", "reask") else "")
            for s in t.get("plan", [])
        ]

    try:
        await turn(
            "What was UK inflation in 2024, and why? Sources please.",
            {"request_type": "research", "question_features": ["concept", "context", "asks_sources"]},
        )
        first = await turn("How do I calculate PED?", node_ids=[PART])  # waits: 1
        second = await right()  # waits: 2
        third = await right()  # takes the question slot
        fourth = await turn("Sorry, can we carry on?")  # the displaced check, alone
        skipped = learner.skips(student, ["ail_ask", "ail_verify"])
        check(
            purposes(first)[-1].startswith("ask_mcq")
            and purposes(second)[-1] == "ask_mcq:check"
            and purposes(third)[-1] == "reask:literacy_task"
            and purposes(fourth) == ["ask_mcq:check"]
            and skipped == 1,
            "a waiting literacy task takes the question slot after 2 replies; the skipped check comes next, alone",
            " | ".join(", ".join(purposes(t)) for t in (first, second, third, fourth)),
        )
    finally:
        drop_student(student)


async def engagement_rules(url: str) -> None:
    """In-session engagement rules (engagement-rules): a passive streak gets offer_choice once a session, and each
    pick is planned; a third "just show me" on a part first gets a 2-option check; a coasting student's
    explain-back asks for their weakest point only and is scored on it."""
    labels = {"question_depth": "surface", "engagement": "passive"}

    def turner(student: str, keyed: str):
        async def turn(message: str, extra: dict | None = None, **more) -> dict:
            time.sleep(1.1)
            return await call(
                keyed,
                "tutor_turn",
                {"message": message, "client": "check_mcp", "node_ids": [PART], "this_message": {**labels, **(extra or {})}, **more},
            )

        return turn

    student = "check-passive"
    turn = turner(student, f"{url}?key={new_student(student)}")
    try:
        streak = [await turn("ok") for _ in range(4)]
        offer = streak[-1].get("plan") or [{}]
        again = await turn("ok")
        quiz = await turn("a quick question please", {"choice": "quiz"})
        extend = await turn("a harder one", {"choice": "extend", "engagement": "active"})
        stop = await turn("let's stop there", {"choice": "stop", "engagement": "active"})
        check(
            offer[0].get("move") == "offer_choice"
            and offer[0]["data"].get("reason") == "passive"
            and offer[0]["data"].get("options") == ["quiz", "stop"]
            and "offer_choice" not in moves(again)
            and moves(quiz) == ["ask_mcq"]
            and moves(extend) == ["extend"]
            and moves(stop) == ["session_summary"]
            and "covered" in stop["plan"][0]["data"],
            "a passive streak is offered quiz and stop (extend only when earned) once a session, and each pick is planned; stop returns a session summary",
            " | ".join(json.dumps(moves(t)) for t in (*streak, again, quiz, extend, stop)),
        )
    finally:
        drop_student(student)

    student = "check-shows"
    turn = turner(student, f"{url}?key={new_student(student)}")
    try:
        shows = [await turn("just show me", {"choice": "just_show_me"}) for _ in range(3)]
        third = (shows[-1].get("plan") or [{}])[0]
        chosen, _ = letter(student, True)
        before = max_evidence_id()
        answered = await turn(chosen, {"engagement": "active"}, answer={"part_id": PART, "type": "mcq", "choice": chosen})
        rows = evidence(student, before)
        check(
            moves(answered) == ["feedback", "show", "ask_mcq"] and third["data"].get("then_show") is True,
            "the repeated show's 2-option question comes first; its answer gets feedback, then the full show and its check",
            json.dumps(moves(answered)),
        )
        check(
            [moves(t) for t in shows[:2]] == [["show", "ask_mcq"]] * 2
            and moves(shows[-1]) == ["ask_mcq"]
            and len(third["data"].get("options", [])) + bool(third["data"].get("extra_option")) == 2
            and [(r["evidence_type"], r["n_options"]) for r in rows] == [("mcq_check", 2)],
            f"after {load_settings().show.max_per_part_session} shows of a part, the next first gets a 2-option check (guess 1/2)",
            " | ".join(json.dumps(moves(t)) for t in shows) + f" {[(r['evidence_type'], r['n_options']) for r in rows]}",
        )
    finally:
        drop_student(student)

    student = "check-coasting"
    turn = turner(student, f"{url}?key={new_student(student)}")
    try:
        now = learner.parse_ts(learner.now_iso())
        prereqs = [p for e in graph.prerequisites(PART, 1) for p in graph.parts_of(e["other"])]
        for i, part in enumerate([*prereqs, PART] * 3):  # known well, two days ago, so no prequestion or prereq check
            learner.record_evidence(
                student, part, "explain_back", 1.0, apply="now", ts=learner._event_ts(now - timedelta(days=2, minutes=60 - i))
            )
        # coasting needs at least engagement.coasting_min_messages messages: one passive message came just before
        learner.record_exchange(student, [PART], "surface", "passive", ts=learner._event_ts(now - timedelta(minutes=2)), apply="now")
        got = await turn("ok")
        step = next((s for s in got.get("plan", []) if s["move"] == "explain_back"), {})
        ids = [p["id"] for p in graph.score_points(PART)]
        point_id = step.get("data", {}).get("point_id")
        letters = [p["id"] for p in got.get("score_next", {}).get(PART, [])]
        before = max_evidence_id()
        mine = graph.point_letter(ids.index(point_id)) if point_id in ids else "a"
        await turn("my answer", {"engagement": "constructive"}, answer={"part_id": PART, "type": "explain_back", "points_met": [mine]})
        rows = evidence(student, before)
        check(
            point_id in ids and letters == [mine] and [(r["score"], r["point_id"]) for r in rows] == [(1.0, point_id)],
            "a coasting student's explain-back asks for their weakest point only, and is scored on it",
            f"{json.dumps(moves(got))} point {point_id} letters {letters} {[(r['score'], r['point_id']) for r in rows]}",
        )
    finally:
        drop_student(student)


async def priorities(url: str) -> None:
    """Add-on steps by expected marks (priorities): a due review covered by a mock in 3 days beats an earned extend
    on a part with only the final ahead, and loses to it without the mock; a part not yet due is never reviewed; a
    mock shortens the review gap until it has passed; adding then removing a test and rebuilding changes nothing;
    an unmatched topic adds nothing and returns the topics; considered is stored and never sent."""
    from edux import context_blocks, plan, service

    settings = load_settings()
    student = "check-priorities"
    keyed = f"{url}?key={new_student(student)}"
    extend_part, review_part, later_part = "ped_definition", "tax_supply_shift", "externality_tax_eval"
    topic = next(t["name"] for t in graph.topics() if review_part in graph.parts_of(t["id"]))
    now = learner.parse_ts(learner.now_iso())

    def iso(days: float) -> str:
        return learner._event_ts(now + timedelta(days=days))

    def assess(days: int) -> dict:
        return service.update_profile(
            learner.get_student(student),
            add_assessment={"name": "Mock", "kind": "mock", "date": (now + timedelta(days=days)).date().isoformat(), "topics": [topic]},
        )

    def clear() -> None:
        for a in learner.assessments(student):
            service.update_profile(learner.get_student(student), remove_assessment=a["id"])

    def addon() -> tuple[dict | None, dict]:
        turn = context_blocks.Turn(
            student=learner.get_student(student),
            parts=[extend_part],
            message="",
            at=learner.now_iso(),
            limits={"reviews_due": 3},
            resolution={},
        )
        blocks = {"support": {"part_id": extend_part, "extend": True}, "reviews_due": context_blocks.reviews_due(turn, settings)}
        return plan._second_step(turn, blocks, settings), blocks

    def picked(step: dict | None) -> str:
        return "-" if step is None else f"{step['move']}:{step['part_id']}"

    try:
        with learner._conn() as conn:  # hand-set state: the extend part fades by the final, the review part holds
            for part, p_known, half_life in ((extend_part, 0.6, 1.0), (review_part, 0.6, 400.0), (later_part, 0.6, 400.0)):
                conn.execute(
                    "INSERT INTO part_state (student_id, part_id, p_known, half_life_days, last_seen, n_evidence, "
                    "clock_start, last_correct) VALUES (?, ?, ?, ?, ?, 3, ?, ?)",
                    (student, part, p_known, half_life, iso(-1), iso(-1), iso(-1)),
                )
            conn.execute(
                "INSERT INTO review_queue (student_id, part_id, due, reason) VALUES (?, ?, ?, 'scheduled')",
                (student, review_part, iso(-0.1)),
            )
            conn.execute(
                "INSERT INTO review_queue (student_id, part_id, due, reason) VALUES (?, ?, ?, 'scheduled')", (student, later_part, iso(5))
            )
        without, _ = addon()
        added = assess(3)
        with_mock, blocks = addon()
        due_parts = [r["part_id"] for r in blocks["reviews_due"]["items"]]
        bridged = (
            without is not None and without["move"] == "ask_mcq" and without["data"].get("bridge")
        )  # step 05t: a bridge beats an earned extend
        check(
            (picked(without) == f"extend:{extend_part}" or bridged)
            and picked(with_mock) == f"ask_mcq:{review_part}"
            and "mock" in with_mock["data"].get("reason", "")
            and with_mock.get("considered"),
            "a due review covered by a mock in 3 days beats an earned extend and a bridge; with no mock it loses to them",
            f"without: {picked(without)}, with: {picked(with_mock)} {json.dumps((with_mock or {}).get('data', {}).get('reason'))}",
        )
        check(
            later_part not in due_parts and picked(with_mock) != f"ask_mcq:{later_part}",
            "a part not yet due is never reviewed, whatever tests are coming",
            json.dumps(due_parts),
        )
        clear()
        assess(5)
        before_mock = learner.review_gap_days(student, review_part, now)
        after_mock = learner.review_gap_days(student, review_part, now + timedelta(days=6))
        clear()
        plain_now = learner.review_gap_days(student, review_part, now)
        plain_after = learner.review_gap_days(student, review_part, now + timedelta(days=6))
        check(
            before_mock < plain_now and abs(after_mock - plain_after) < 1e-9,
            "a mock in 5 days shortens the review gap; after it, the gap is the final-exam one again",
            f"with mock {before_mock:.2f} vs {plain_now:.2f} days; after it {after_mock:.2f} vs {plain_after:.2f}",
        )

        drop_student(student)  # with events this time: add, remove, rebuild = never added
        keyed = f"{url}?key={new_student(student)}"
        for i, part in enumerate([review_part, extend_part, review_part]):
            learner.record_evidence(student, part, "explain_back", 1.0, ts=iso(-3 + i), apply="now")
        cli("rebuild", "--student", student)
        untouched = state(student)
        assess(5)
        cli("rebuild", "--student", student)
        clear()
        cli("rebuild", "--student", student)
        check(state(student) == untouched, "adding then removing an assessment and rebuilding gives the same state")

        rows = lambda: learner._conn().execute("SELECT COUNT(*) FROM student_assessment WHERE student_id = ?", (student,)).fetchone()[0]
        got = await call(
            keyed,
            "update_my_profile",
            {
                "add_assessment": {
                    "name": "Mock",
                    "kind": "mock",
                    "date": (now + timedelta(days=9)).date().isoformat(),
                    "topics": ["astrophysics"],
                }
            },
        )
        check(
            got.get("ok") is False and {t["name"] for t in got.get("topics", [])} == {t["name"] for t in graph.topics()} and rows() == 0,
            "an unmatched topic returns the pack's topics and adds nothing",
            json.dumps(got)[:200],
        )
        check(
            added.get("ok") is True
            and added["added"]["parts"] == len(graph.parts_of(next(t["id"] for t in graph.topics() if t["name"] == topic))),
            "a matched topic is confirmed with its part count",
            json.dumps(added.get("added")),
        )
    finally:
        drop_student(student)

    key = demo.demo_keys()["demo-secure"]
    got = await call(
        f"{url}?key={key}",
        "tutor_turn",
        {"message": "Quiz me on what's due", "client": "check_mcp", "this_message": {"question_depth": "surface", "engagement": "active"}},
    )
    stored = plan_json("demo-secure").get("considered")
    check(
        bool(stored) and "considered" not in json.dumps(got) and all("value" in c for c in stored),
        "considered add-on candidates are stored with their values and never sent",
        json.dumps(stored)[:200],
    )


async def reply_style(url: str) -> None:
    """Per-step reply length follows mastery and fatigue, a student's own answer_length always wins, and steps on
    a diagram part carry diagram: true (reply-style)."""
    from edux import context_blocks, plan, service

    settings = load_settings()
    ceiling = settings.style.max_words

    def turn_for(student: str) -> context_blocks.Turn:
        return context_blocks.Turn(
            student=learner.get_student(student), parts=[], message="", at=learner.now_iso(), limits={}, resolution={}
        )

    def review(part: str) -> dict:
        return plan._step(
            "ask_mcq",
            part,
            {"purpose": "review", "name": graph.get_node(part)["name"], "mode": "transfer", "options": [], "answer_type": "mcq"},
            key="ask_mcq_review",
        )

    def teach(part: str) -> dict:
        return plan._step(
            "teach_point",
            part,
            {"index": 1, "total": 2, "point": "p", "exemplar": "", "level": "hint", "max_words": settings.points.max_words},
        )

    secure = next(p for p in learner.all_parts() if learner.level(learner.part_p("demo-secure", p)) == "secure")
    known = service.reply_style([review(secure)], learner.get_student("demo-secure"), turn_for("demo-secure"), {})
    tired = service.reply_style(
        [review(secure), teach(secure)], learner.get_student("demo-secure"), turn_for("demo-secure"), {"session": {"state": "fatigued"}}
    )
    check(
        known[0]["data"].get("max_words") == round(ceiling * settings.style.length_known_share)
        and all(s["data"].get("max_words") == round(ceiling * settings.style.length_fatigued_share) for s in tired),
        "a review on a secure part gets about half the words; a fatigued turn gets the fatigued share",
        f"known {known[0]['data'].get('max_words')}, fatigued {[s['data'].get('max_words') for s in tired]} of {ceiling}",
    )

    student = "check-style"
    keyed = f"{url}?key={new_student(student)}"
    try:
        service.update_profile(learner.get_student(student), answer_length=200)
        for part in ("ped_definition", "tax_supply_shift"):
            learner.record_evidence(
                student,
                part,
                "explain_back",
                1.0,
                apply="now",
                ts=learner._event_ts(learner.parse_ts(learner.now_iso()) - timedelta(days=3)),
            )
        own = service.reply_style(
            [review("ped_definition"), teach("ped_definition")],
            learner.get_student(student),
            turn_for(student),
            {"session": {"state": "fatigued"}},
        )
        cap = load_settings().points.max_words_requested
        check(
            all((s["data"].get("max_words") or 200) >= 200 for s in own if s["move"] != "teach_point")
            and all(s["data"].get("max_words") == min(200, cap) for s in own if s["move"] == "teach_point"),
            f"with answer_length 200, no step carries a smaller max_words, and teach_point carries {cap} (one point per message)",
            json.dumps([s["data"].get("max_words") for s in own]),
        )
        service.update_profile(learner.get_student(student), answer_length=50)
        short = service.reply_style([teach("ped_definition")], learner.get_student(student), turn_for(student), {})
        check(
            short[0]["data"].get("max_words") == 50,
            "with answer_length 50, teach_point carries 50",
            json.dumps([s["data"].get("max_words") for s in short]),
        )
        service.update_profile(learner.get_student(student), answer_length=200)
        got = await call(
            keyed,
            "tutor_turn",
            {
                "message": "How does a tax shift supply?",
                "client": "check_mcp",
                "node_ids": ["tax_supply_shift"],
                "this_message": {"question_depth": "mechanism", "engagement": "active"},
            },
        )
        other = await call(
            keyed,
            "tutor_turn",
            {
                "message": "And how do I calculate PED?",
                "client": "check_mcp",
                "node_ids": ["ped_formula"],
                "this_message": {"question_depth": "mechanism", "engagement": "active"},
            },
        )
        on = [s for s in got.get("plan", []) if s["part_id"] == "tax_supply_shift"]
        off = [s for s in other.get("plan", []) if s["part_id"] == "ped_formula"]
        check(
            on
            and all(s["data"].get("diagram") is True for s in on)
            and "sketch" in on[0]["cue"]
            and off
            and not any(s["data"].get("diagram") for s in off),
            "steps on a diagram part carry diagram: true (and the cue line); steps on another part don't",
            f"{[(s['move'], s['data'].get('diagram')) for s in on]} | {[(s['move'], s['data'].get('diagram')) for s in off]}",
        )
    finally:
        drop_student(student)


def shuffles() -> None:
    """MCQ options are shuffled differently for different students."""
    from edux import plan
    from edux.context_blocks import Turn

    settings = load_settings()
    orders = set()
    for student in ("demo-secure", "demo-weak", "demo-showme"):
        turn = Turn(student=learner.get_student(student), parts=[PART], message="", at=learner.now_iso(), limits={}, resolution={})
        step = plan.ask_mcq(turn, plan.question(PART, "check", graph.score_points(PART)[0]["point"], settings))
        orders.add(tuple(o["text"] for o in step["data"]["options"]))
    check(len(orders) > 1, "MCQ options are shuffled differently for different students", f"{len(orders)} orders for 3 students")


async def point_ids(keyed: str, student: str) -> None:
    """points_met scores the same as letters, full ids, a mix, or with no saved plan; another part's id is refused."""
    points = graph.score_points(PART)
    labels = {"question_depth": "mechanism", "engagement": "constructive"}
    cases = [
        ("letters", ["a"], 1 / len(points)),
        ("full ids", [points[0]["id"]], 1 / len(points)),
        ("a mix", ["a", points[1]["id"]], 1.0),
        ("no saved plan", ["a"], 1 / len(points)),
    ]
    for label, met, expected in cases:
        if label == "no saved plan":
            with learner._conn() as conn:
                conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
        time.sleep(1.1)
        before = max_evidence_id()
        got = await call(
            keyed,
            "tutor_turn",
            {
                "message": "my answer",
                "client": "check_mcp",
                "this_message": labels,
                "answer": {"part_id": PART, "type": "explain_back", "points_met": met},
            },
        )
        scores = [e["score"] for e in evidence(student, before)]
        check(
            got.get("ok") is True and scores == [expected],
            f"points_met as {label} scores {expected}",
            got.get("error") or json.dumps(scores),
        )
    other = graph.score_points("ped_definition")[0]["id"]
    before = max_evidence_id()
    got = await call(
        keyed,
        "tutor_turn",
        {"message": "my answer", "this_message": labels, "answer": {"part_id": PART, "type": "explain_back", "points_met": [other]}},
    )
    check(got.get("ok") is False and max_evidence_id() == before, "a point id from another part is refused", got.get("error", ""))


async def main(url: str, key: str, student: str) -> None:
    keyed = f"{url}?key={key}"
    async with streamablehttp_client(keyed) as (read, write, _), ClientSession(read, write) as session:
        init = await session.initialize()
        check(init.serverInfo.name == "Synapse", "the server reports its name as Synapse", init.serverInfo.name)
        instructions = init.instructions or ""
        words = len(instructions.split())
        sections = instructions.count(chr(10) + "## ")
        from edux import plan

        expected = len(plan.move_keys())
        check(
            0 < words <= INSTRUCTIONS_MAX_WORDS and sections == expected,
            f"the server instructions have one section per move ({expected}) and are at most {INSTRUCTIONS_MAX_WORDS} words",
            f"{words} words, {sections} move sections",
        )
        check(
            not PLACEHOLDER.search(instructions),
            "no placeholder in the server instructions",
            ", ".join(PLACEHOLDER.findall(instructions)[:3]),
        )
        tools = {t.name for t in (await session.list_tools()).tools}
        check(tools == EXPECTED_TOOLS, "lists the tools", ", ".join(sorted(tools)))
        prompts = {p.name for p in (await session.list_prompts()).prompts}
        check(EXPECTED_PROMPTS <= prompts, "lists the prompts", ", ".join(sorted(prompts)))
        for name in sorted(EXPECTED_PROMPTS & prompts):
            args = {"topic": "price elasticity of demand"} if name == "check_me" else {}
            got = await session.get_prompt(name, args)
            check(bool(got.messages), f"prompt {name}")

    await conversation(keyed, student)
    await choices(keyed, student)
    await wrong_intuition(url)
    await prerequisite_and_review(url)
    await stuck_on_point(url)
    await research_questions(url)
    await secure_every(url)
    await how_ai_works(url)
    await fatigued_student(url)
    await rushing_student(url)
    await coverage(url)
    await bridge(url)
    await class_assessments(url)
    await calibration(url)
    await find_error_run(url)
    await waiting_task(url)
    await engagement_rules(url)
    await priorities(url)
    await reply_style(url)
    shuffles()

    before = max_evidence_id()
    bad = await call(
        keyed,
        "tutor_turn",
        {
            "message": "it's the minus sign",
            "node_ids": [PART],
            "this_message": {"question_depth": "surface", "engagement": "active"},
            "answer": {"part_id": PART, "type": "explain_back", "points_met": ["no_such_point"]},
        },
    )
    check(
        bad.get("ok") is False and max_evidence_id() == before, "an unknown point id is refused and records nothing", bad.get("error", "")
    )

    await point_ids(keyed, student)

    progress = await call(keyed, "get_my_progress", {})
    check(
        {"tree", "levers", "reviews_due", "trends"} <= set(progress) and "p_now" not in json.dumps(progress),
        "get_my_progress (levels only)",
        f"{len(progress.get('levers', []))} levers",
    )
    full = await call(keyed, "get_my_progress", {"include_parts": True})
    check(
        service.result_size(full) <= load_settings().results.max_chars_full_progress,
        f"get_my_progress with include_parts is at most {load_settings().results.max_chars_full_progress} characters",
        f"{service.result_size(full)} characters",
    )
    check(
        service.result_size(progress) <= load_settings().results.max_chars,
        f"get_my_progress (levels only) is at most {load_settings().results.max_chars} characters",
        f"{service.result_size(progress)} characters",
    )
    profile = await call(keyed, "update_my_profile", {"interests": "football"})
    check(profile.get("ok") is True, "update_my_profile", json.dumps(profile.get("profile")))

    for label, target in (("wrong key", f"{url}?key=not-a-real-key"), ("missing key", url)):
        response = httpx.post(
            target,
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            headers={"Accept": "application/json, text/event-stream"},
        )
        check(response.status_code == 401, f"{label} is refused", f"HTTP {response.status_code}")

    cli("set-profile", "--student", student, "--profile", "minimal")
    try:
        minimal = await call(
            keyed,
            "tutor_turn",
            {"message": "How do I calculate PED?", "this_message": {"question_depth": "surface", "engagement": "passive"}},
        )
    finally:
        cli("set-profile", "--student", student, "--profile", "default")
    check(
        (minimal.get("style") or {}).get("interests") == "football",
        "style is sent again after the interests change",
        json.dumps(minimal.get("style", {}).get("interests")),
    )
    check(
        minimal.get("plan") == [] and set(minimal.get("reference", {})) == {"notes"},
        "the minimal profile returns notes only and no plan",
        ", ".join(minimal.get("reference", {})),
    )

    rows = (
        learner._conn()
        .execute(
            """SELECT evidence_type, n_options FROM evidence_log WHERE student_id IN (?, 'demo-secure', 'demo-showme')
           AND origin = 'chat' AND evidence_type IN ('mcq_check', 'ail_how')""",
            (student,),
        )
        .fetchall()
    )
    kinds = {r["evidence_type"] for r in rows}
    check(
        kinds == {"mcq_check", "ail_how"} and all((r["n_options"] or 0) >= 2 for r in rows),
        "multiple-choice answers from chat store how many options they showed",
        f"{len(rows)} rows, types {sorted(kinds)}, n_options {sorted({r['n_options'] for r in rows}, key=str)}",
    )

    personal = load_settings().personalisation
    found = learner.learning_offset("demo-secure")
    low, high = personal.learn_rate_weight_bounds
    progress = await call(keyed, "get_my_progress", {})
    shown = json.dumps(progress) + json.dumps(
        await call(
            keyed,
            "tutor_turn",
            {
                "message": "How do I calculate PED?",
                "client": "check_mcp",
                "this_message": {"question_depth": "surface", "engagement": "active"},
            },
        )
    )
    # off (the default): no offset at all. On: inside its bounds, and nonzero only once enough later answers
    # (each part's first answer is left out) have built up
    enough = found["n"] >= personal.min_observations
    check(
        (found["offset"] == 0.0 and found["weight"] == 1.0)
        if not learner.personalisation_on()
        else (low <= found["weight"] <= high and (found["offset"] != 0) == enough),
        "the personal learning rate is off by default; when on, it is within its bounds and moves only with enough earlier evidence",
        json.dumps(found),
    )
    check(
        "offset" not in shown and "learning_rate" not in shown, "the learning-rate offset is never shown in tutor_turn or get_my_progress"
    )
    lone = "check-lone"
    new_student(lone)
    try:  # one session's evidence only: nothing earlier, so no offset yet
        now = learner.parse_ts(learner.now_iso())
        for i in range(12):
            learner.record_evidence(
                lone,
                ["ped_definition", "ped_formula", "yed_definition"][i % 3],
                "explain_back",
                1.0,
                ts=learner._event_ts(now - timedelta(minutes=24 - 2 * i)),
                apply="now",
            )
        current = learner.learning_offset(lone, learner.session_state(lone)["session_id"])
        derived = (
            learner._conn().execute("SELECT COUNT(DISTINCT session_id) FROM evidence_derived WHERE student_id = ?", (lone,)).fetchone()[0]
        )
        check(
            derived == 1 and current["offset"] == 0.0,
            "evidence from the current session alone gives no offset (only earlier sessions count)",
            f"{derived} session(s) {json.dumps(current)}",
        )
    finally:
        drop_student(lone)

    for who in ("demo-secure", "demo-weak", "demo-showme"):  # step 05r: cached offsets equal the ones computed from scratch
        cached = (learner.learning_offset(who), learner.starting_offsets(who))
        learner._clear_offset_cache(who)
        fresh = (learner.learning_offset(who), learner.starting_offsets(who))
        check(cached == fresh, f"cached and uncached learner offsets match ({who})", json.dumps(fresh)[:120])

    for who in sorted({student, "demo-secure", "demo-weak", "demo-showme"}):  # every student the run wrote events for
        before_rebuild = state(who)
        cli("rebuild", "--student", who)
        after_rebuild = state(who)
        changed = [t for t in STATE_TABLES if after_rebuild[t] != before_rebuild[t]]
        check(not changed, f"rebuild gives identical state ({who})", f"differs in {', '.join(changed)}" if changed else "")
        for t in changed:
            print("     before only:", sorted(set(before_rebuild[t]) - set(after_rebuild[t]))[:3])
            print("     after only: ", sorted(set(after_rebuild[t]) - set(before_rebuild[t]))[:3])

    ms = [
        r["ms"]
        for r in learner._conn().execute(
            "SELECT ms FROM call_log WHERE student_id = ? AND tool = 'tutor_turn' ORDER BY id DESC LIMIT 6", (student,)
        )
    ]
    check(
        bool(ms) and statistics.median(ms) < 100,
        "tutor_turn server time under 100 ms",
        f"median {statistics.median(ms):.0f} ms over {len(ms)} calls" if ms else "no calls logged",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--student", default="demo-secure", help="a demo student (default demo-secure)")
    parser.add_argument("--key", help="the student's key (default: read from demo-keys.json in the data folder)")
    parser.add_argument("--keep", action="store_true", help="don't reset the demo students after the run")
    args = parser.parse_args()
    cli("seed-demo", "--reset")
    found = learner.get_student(args.student)
    if found is None:
        sys.exit(f"unknown student {args.student!r}; run python -m edux.cli seed-demo first")
    try:
        asyncio.run(main(args.url, args.key or demo.demo_keys()[args.student], args.student))
    finally:
        if not args.keep:
            cli("seed-demo", "--reset")
    print(f"\n{'all checks passed' if not failures else f'{len(failures)} check(s) failed'}")
    sys.exit(1 if failures else 0)
