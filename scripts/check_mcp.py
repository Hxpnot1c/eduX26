"""Check a running eduX server through the Python MCP client, without Node or MCP Inspector.

    python scripts/check_mcp.py [--student demo-secure] [--key <key>] [--url http://127.0.0.1:8000/mcp]

Run it from the repo root against a server started on the same data folder (EDUX_DATA_DIR), with the
example-mini pack loaded and the demo students seeded. It:
- resets the demo students (seed-demo --reset keeps their keys), so the run starts from the seeded state;
- lists the tools and prompts;
- runs the point-by-point loop on ped_formula as the student through tutor_turn (intuition MCQ answered wrongly, each point and its
  check, a wrong letter and its re-teach, the explain-back), then an explain-back missing a point and a question
  asked instead of an answer, and checks each plan, the letters scored from the stored map, the misconception
  state, that every reply in the loop ends in one question, result sizes against the budget, style, known terms,
  watch-for misconceptions, and that no p_now reaches the chatbot;
- checks "I know this", "just show me" (and no discount after it), a lost letter map, a wrong intuition answer
  followed by teaching (demo-weak), a prerequisite check and a
  due review as MCQs (demo-weak, demo-showme), a step back when the same point is missed again after its
  re-teach (demo-showme), and that options are shuffled differently per student;
- runs research questions (demo-weak): answer_with_sources and a literacy task, an ignored task re-asked once then
  scored 0, Ask and Verify raised, no task on a course question; a task only every literacy.secure_every research
  questions at secure (demo-showme); and how-AI-works checks (demo-secure): cutoff only without web access, a bad
  link's fabrication check with 4 options, one per part per session, an ignored check re-asked then scored 0, a
  self-correction's check, and the AI-literacy section of get_my_progress;
- checks the server instructions' length, that points_met scores the same as letters, full ids, a mix or with
  no saved plan, and that another part's point is refused;
- checks a bad answer is refused and records nothing, get_my_progress, update_my_profile, that a wrong or
  missing key is refused with 401, and that the minimal profile returns no plan;
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

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from edux import graph, learner
from edux.settings import load_settings

EXPECTED_TOOLS = {"tutor_turn", "get_my_progress", "update_my_profile"}
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


async def call(url: str, name: str, arguments: dict) -> dict:
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
    return [dict(r) for r in learner._conn().execute(
        "SELECT * FROM evidence_log WHERE student_id = ? AND id > ? ORDER BY id", (student, since_id))]


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
            time.sleep(1.1)   # event timestamps are to the second; keep the turns in separate seconds
        got = await call(keyed, "tutor_turn", {"client": "check_mcp", **arguments})
        turns.append(got)
        return got

    async def pick(right: bool) -> tuple[dict, str]:
        chosen, option = letter(student, right)
        got = await turn({"message": chosen, "this_message": labels,
                          "answer": {"part_id": PART, "type": "mcq", "choice": chosen}})
        return got, option

    def purposes(t: dict) -> list[str]:
        return [s["move"] + (f":{s['data']['purpose']}" if s["move"] == "ask_mcq" else "") for s in t.get("plan", [])]

    points = graph.score_points(PART)
    first = await turn({"message": "How do I calculate PED?", "this_message": labels})
    data = (first.get("plan") or [{}])[0].get("data") or {}
    check(purposes(first) == ["ask_mcq:intuition"] and first["plan"][0]["part_id"] == PART
          and not first.get("score_next", {}).get(PART),
          "1. an untaught part gets one intuition MCQ, answered by letter", ", ".join(purposes(first)) or first.get("error", ""))
    named = [r[0] for r in graph._conn().execute("SELECT id FROM node WHERE name = ?", (data.get("via") or "",))]
    via_known = not data.get("via") or any(learner.level(learner.rollup(student, i)) != "new" for i in named)
    check(bool(data.get("note")) and via_known, "1. the intuition leads in from a known link or the part's intuition line",
          json.dumps({k: data.get(k) for k in ("note", "via")}))

    second, _ = await pick(False)
    step = (second.get("plan") or [{}, {}])[1:2] or [{}]
    check(purposes(second) == ["feedback", "teach_point", "ask_mcq:check"] and step[0].get("data", {}).get("index") == 1,
          "2. a wrong intuition answer gets feedback, then point 1 and its check", ", ".join(purposes(second)) or second.get("error", ""))
    third, _ = await pick(True)
    check(purposes(third) == ["feedback", "teach_point", "ask_mcq:check"] and third["plan"][1]["data"]["index"] == 2,
          "3. a right letter moves to point 2", ", ".join(purposes(third)) or third.get("error", ""))
    fourth, picked = await pick(False)
    named = ((fourth.get("plan") or [{}])[0].get("data") or {}).get("misconceptions") or [{}]
    check(purposes(fourth) == ["feedback", "reteach", "ask_mcq:check"] and named[0].get("id") == picked,
          "4. a wrong letter gets feedback naming it, one re-teach of the point and the check again (no step back)",
          ", ".join(purposes(fourth)) or fourth.get("error", ""))
    held = learner._conn().execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?",
                                   (student, picked)).fetchone()
    check(bool(held and held["active"]), f"4. {picked} is active")
    fifth, _ = await pick(True)
    check(purposes(fifth) == ["feedback", "explain_back"] and len(points) == 2,
          "5. after the last point comes the explain-back of the whole part", ", ".join(purposes(fifth)) or fifth.get("error", ""))
    recorded = [(e["evidence_type"], e["score"]) for e in evidence(student, start)]
    check(recorded == [("prequestion", 0.0), ("mcq_check", 1.0), ("mcq_check", 0.0), ("mcq_check", 1.0)],
          "the server scored every letter from its stored map", json.dumps(recorded))
    loop = [first, second, third, fourth, fifth]
    check(all(ends_in_one_question(t) for t in loop), "every reply in the loop ends in exactly one question",
          "; ".join(", ".join(purposes(t)) for t in loop if not ends_in_one_question(t)))
    words = [s["data"].get("max_words") for t in loop for s in t["plan"] if s["move"] == "teach_point"]
    check(bool(words) and all(w == load_settings().points.max_words <= 80 for w in words),
          "every teach_point asks for at most 80 words of explanation", json.dumps(words))

    sixth = await turn({"message": "You divide the change by the original value and times by 100 for each percentage.",
                        "this_message": {"question_depth": "mechanism", "engagement": "constructive"},
                        "answer": {"part_id": PART, "type": "explain_back", "points_met": ["a"]}})
    missing = ((sixth.get("plan") or [{}, {}])[-1].get("data") or {}).get("missing")
    check(purposes(sixth) == ["feedback", "reteach"] and missing == [p["point"] for p in points[1:]],
          "6. an explanation missing a point gets feedback, then reteach with only that point",
          f"{', '.join(purposes(sixth)) or sixth.get('error', '')}; missing {missing}")

    before = max_evidence_id()
    seventh = await turn({"message": "Wait, why do you use the original value and not the new one?", "node_ids": [PART],
                          "this_message": labels})   # a self-correction here would add a how-AI-works check (05e)
    asked = ((seventh.get("plan") or [{}, {}])[-1].get("data") or {})
    check(purposes(seventh) == ["answer_brief", "reask"] and asked.get("asked") == "reteach"
          and asked.get("missing") == missing and seventh.get("score_next") == sixth.get("score_next")
          and max_evidence_id() == before,
          "7. a question instead of an answer gets answer_brief, then the same question again, and scores nothing",
          ", ".join(purposes(seventh)) or seventh.get("error", ""))

    untermed = []
    for t in turns:
        on_part = [s for s in t.get("plan", []) if s.get("part_id")]
        if on_part and (on_part[0]["data"].get("terms") or [None])[0] != graph.get_node(on_part[0]["part_id"])["name"]:
            untermed.append(on_part[0]["move"])
    check(not untermed, "each plan lists the known terms once, its first part first", ", ".join(untermed))

    shapes = {tuple(sorted(step)) for t in turns for step in t.get("plan", [])}
    check(shapes == {("cue", "data", "move", "part_id")}, "each step carries only move, part_id, cue and data",
          json.dumps(sorted(shapes)))
    filled = [step["cue"] for t in turns for step in t.get("plan", []) if PLACEHOLDER.search(json.dumps(step))]
    check(not filled, "no placeholder in any step", "; ".join(filled[:2]))
    bare = [i for i, t in enumerate(turns, 1) if any("answer_type" in s["data"] for s in t.get("plan", []))
            and not ((t.get("reference") or {}).get("misconceptions") or {}).get("watch_for")]
    shapes = {tuple(sorted(w)) for t in turns
              for w in ((t.get("reference") or {}).get("misconceptions") or {}).get("watch_for") or []}
    check(not bare and shapes == {("id", "wrong_idea")},
          "every plan that asks something carries watch-for misconceptions as id and wrong_idea only",
          f"none in turn(s) {bare}" if bare else json.dumps(sorted(shapes)))
    check("style" in turns[0] and not any("style" in t for t in turns[1:]),
          "style comes with the first call of a session only", ", ".join(str("style" in t) for t in turns))
    for i, t in enumerate(turns, 1):
        print(f"     turn {i}: {len(json.dumps(t))} chars")
    sizes = [len(json.dumps(t)) for t in turns]
    limit = load_settings().results.max_chars
    over = learner._conn().execute("SELECT COALESCE(SUM(over_budget), 0) FROM call_log WHERE student_id = ? AND tool = 'tutor_turn'",
                                   (student,)).fetchone()[0]
    check(statistics.median(sizes) <= limit and over == 0, f"the median result is at most {limit} characters, none over budget",
          f"median {statistics.median(sizes):.0f}, largest {max(sizes)}, {over} over budget")
    leaked = [i + 1 for i, t in enumerate(turns) if "p_now" in json.dumps(t)]
    check(not leaked, "no p_now in tutor_turn output", f"found in turn(s) {leaked}" if leaked else "")


async def choices(keyed: str, student: str) -> None:
    """"I know this" goes straight to the check; "just show me" shows the point and ends with its check, with no
    discount on the next answer; a lost letter map records nothing and asks the same question with new letters."""
    other = "pes_definition"
    labels = {"question_depth": "surface", "engagement": "active"}
    time.sleep(1.1)
    skip = await call(keyed, "tutor_turn", {"message": "I know this", "node_ids": [other],
                                            "this_message": {**labels, "choice": "skip_point"}})
    check([s["move"] for s in skip.get("plan", [])] == ["ask_mcq"] and skip["plan"][0]["data"].get("purpose") == "check",
          '"I know this" goes straight to the check', json.dumps([s["move"] for s in skip.get("plan", [])]))

    shown_before = [o["text"] for o in skip["plan"][0]["data"]["options"]] if skip.get("plan") else []
    row = plan_json(student)
    row["mcq"] = None
    with learner._conn() as conn:
        conn.execute("UPDATE issued_plan SET plan_json = ? WHERE student_id = ?", (json.dumps(row), student))
    time.sleep(1.1)
    before, exchanges = max_evidence_id(), learner._conn().execute("SELECT COUNT(*) FROM exchange_log").fetchone()[0]
    again = await call(keyed, "tutor_turn", {"message": "A", "this_message": labels,
                                             "answer": {"part_id": other, "type": "mcq", "choice": "A"}})
    shown_after = [o["text"] for o in again["plan"][0]["data"]["options"]] if again.get("plan") else []
    check(max_evidence_id() == before and learner._conn().execute("SELECT COUNT(*) FROM exchange_log").fetchone()[0] == exchanges
          and sorted(shown_after) == sorted(shown_before) and shown_after != shown_before,
          "with the map deleted, an answer records nothing and the same question comes back with new letters",
          json.dumps(shown_after))

    time.sleep(1.1)
    show = await call(keyed, "tutor_turn", {"message": "just show me", "node_ids": ["yed_definition"],
                                            "this_message": {**labels, "choice": "just_show_me"}})
    check([s["move"] for s in show.get("plan", [])] == ["show", "ask_mcq"],
          '"just show me" shows the point and ends with its check', json.dumps([s["move"] for s in show.get("plan", [])]))
    chosen, _ = letter(student, True)
    time.sleep(1.1)
    await call(keyed, "tutor_turn", {"message": chosen, "this_message": labels,
                                     "answer": {"part_id": "yed_definition", "type": "mcq", "choice": chosen}})
    left = learner._conn().execute("SELECT COALESCE(MAX(offload_left), 0) FROM part_state WHERE student_id = ?",
                                   (student,)).fetchone()[0]
    check(left == 0, 'after "just show me", the next answer is not discounted (offload_left stays 0)', str(left))


async def wrong_intuition(url: str) -> None:
    """A wrong intuition answer is followed by teaching, never by another intuition question (demo-weak)."""
    student, part = "demo-weak", "pes_formula"
    keyed = f"{url}?key={learner.get_student(student)['key']}"
    labels = {"question_depth": "surface", "engagement": "active"}
    got = await call(keyed, "tutor_turn", {"message": "How do I work out PES?", "node_ids": [part], "client": "check_mcp",
                                           "this_message": labels})
    if [s["data"].get("purpose") for s in got.get("plan", [])] != ["intuition"]:
        check(False, "a wrong intuition answer is followed by teaching", "no intuition question to answer")
        return
    chosen, picked = letter(student, False)
    time.sleep(1.1)
    got = await call(keyed, "tutor_turn", {"message": chosen, "client": "check_mcp", "this_message": labels,
                                           "answer": {"part_id": part, "type": "mcq", "choice": chosen}})
    moves_ = [s["move"] + (f":{s['data']['purpose']}" if s["move"] == "ask_mcq" else "") for s in got.get("plan", [])]
    named = (got.get("plan") or [{}])[0].get("data", {}).get("misconceptions") or [{}]
    check(moves_ == ["feedback", "teach_point", "ask_mcq:check"] and named[0].get("id") == picked,
          "a wrong intuition answer gets feedback naming it, then teaching, not another intuition question",
          ", ".join(moves_) or got.get("error", ""))


async def prerequisite_and_review(url: str) -> None:
    """A prerequisite check (demo-weak) and a due review (demo-showme) come as ask_mcq and are scored from the letter."""
    for student, message, purpose in (("demo-weak", "How do I calculate PED?", "prereq"),
                                      ("demo-showme", "quiz me on what's due", "review")):
        keyed = f"{url}?key={learner.get_student(student)['key']}"
        got = await call(keyed, "tutor_turn", {"message": message, "client": "check_mcp",
                                               "this_message": {"question_depth": "surface", "engagement": "active"}})
        step = (got.get("plan") or [{}])[-1]
        check(step.get("move") == "ask_mcq" and step.get("data", {}).get("purpose") == purpose,
              f"{student}: a {purpose} question comes as ask_mcq", json.dumps([s["move"] for s in got.get("plan", [])]))
        if step.get("move") != "ask_mcq":
            continue
        chosen, _ = letter(student, True)
        before = max_evidence_id()
        time.sleep(1.1)
        await call(keyed, "tutor_turn", {"message": chosen, "client": "check_mcp",
                                         "this_message": {"question_depth": "surface", "engagement": "active"},
                                         "answer": {"part_id": step["part_id"], "type": "mcq", "choice": chosen}})
        scored = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
        check(scored == [(step["part_id"], "mcq_check", 1.0)], f"{student}: the {purpose} letter is scored", json.dumps(scored))


async def stuck_on_point(url: str) -> None:
    """The same point missed on its check and again on the re-check after its reteach makes the part stuck: the
    next plan steps back (demo-showme on PART, intuition answered right). The plan left by the review run is
    cleared first, so the question here isn't taken as a detour from a pending one."""
    student = "demo-showme"
    keyed = f"{url}?key={learner.get_student(student)['key']}"
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
    labels = {"question_depth": "surface", "engagement": "active"}
    before = max_evidence_id()
    got = await call(keyed, "tutor_turn", {"message": "How do I calculate PED?", "node_ids": [PART], "client": "check_mcp",
                                           "this_message": labels})
    for right in (True, False, False):
        if (got.get("plan") or [{}])[-1].get("move") != "ask_mcq":
            break
        chosen, _ = letter(student, right)
        time.sleep(1.1)
        got = await call(keyed, "tutor_turn", {"message": chosen, "client": "check_mcp", "this_message": labels,
                                               "answer": {"part_id": PART, "type": "mcq", "choice": chosen}})
    steps = got.get("plan") or []
    stepped_back = any(s["data"].get("stuck") or (s["move"] == "reteach" and s["data"].get("answer_type") == "explain_back")
                       for s in steps)
    missed = {e["point_id"] for e in evidence(student, before) if e["evidence_type"] == "mcq_check" and e["score"] == 0}
    check(stepped_back and len(missed) == 1,
          "the same point missed again after its reteach is stuck: the plan steps back",
          ", ".join(s["move"] + (":stuck" if s["data"].get("stuck") else "") for s in steps) or got.get("error", ""))


async def research_questions(url: str) -> None:
    """Research questions and the literacy task (step 05e, demo-weak): answer_with_sources then literacy_task, an
    ignored task re-asked once then scored 0, Ask and Verify raised by a well-phrased question and an answered
    verify task, and no literacy task on a course question."""
    student = "demo-weak"
    keyed = f"{url}?key={learner.get_student(student)['key']}"
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
    check(moves(got) == ["answer_with_sources", "literacy_task"] and task.get("data", {}).get("skill") == "ask"
          and task["data"].get("task") is True and bool(task["data"].get("pattern"))
          and "ail_verify" in got.get("score_next", {}),
          "a research question gets answer_with_sources, then a literacy task with a feedback pattern and a task",
          json.dumps([(s["move"], s["data"].get("skill"), s["data"].get("task")) for s in got.get("plan", [])]))
    asked = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
    check(asked == [("ail_ask", "ail_question", 0.25)], "the question is Ask evidence: features present / 4", json.dumps(asked))

    got = await turn("ok thanks", {"request_type": "other"})
    check(moves(got) == ["reask"] and got["plan"][0]["data"].get("asked") == "literacy_task",
          "an ignored literacy task is re-asked once", json.dumps(moves(got)))
    before = max_evidence_id()
    got = await turn("nice", {"request_type": "other"})
    zero = [(e["part_id"], e["evidence_type"], e["score"]) for e in evidence(student, before)]
    check(moves(got) == [] and zero == [("ail_ask", "ail_task", 0.0)] and plan_json(student).get("literacy") is None,
          "still ignored, it is recorded as ail_task 0 and dropped", f"{moves(got)} {json.dumps(zero)}")

    ask_before = p("ail_ask")
    sharp = {"request_type": "research", "question_features": ["concept", "context", "asks_sources", "asks_reasoning"],
             "web_access": True}
    got = await turn("How did UK petrol prices change in 2025, and why? Give sources.", sharp)
    task = (got.get("plan") or [{}])[-1]
    check(p("ail_ask") > ask_before and task.get("data", {}).get("skill") == "verify"
          and task["data"].get("answer_type") == "ail_task",
          "a well-phrased question raises ail_ask and gets a verify task", f"{ask_before:.2f} -> {p('ail_ask'):.2f}")
    verify_before = p("ail_verify")
    got = await turn("I opened the ONS page: March 2025, and the figure matched.", {"request_type": "other"},
                     {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "b", "c", "d"]})
    check(p("ail_verify") > verify_before and plan_json(student).get("literacy") is None,
          "answering the verify task raises ail_verify and clears it", f"{verify_before:.2f} -> {p('ail_verify'):.2f}")

    got = await turn("How do I calculate PED?", {"request_type": "concept"})
    check(not {"literacy_task", "answer_with_sources"} & set(moves(got)),
          "a course question never gets a literacy task", json.dumps(moves(got)))


async def secure_every(url: str) -> None:
    """At secure, the literacy task comes only every literacy.secure_every research questions (demo-showme)."""
    student = "demo-showme"
    keyed = f"{url}?key={learner.get_student(student)['key']}"
    with learner._conn() as conn:
        conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
    for _ in range(8):   # unprompted checks until Verify is secure
        if learner.level(learner.part_p(student, "ail_verify")) == "secure":
            break
        learner.record_evidence(student, "ail_verify", "ail_unprompted", 1.0, apply="now")
    every = load_settings().literacy.secure_every
    tasks = []
    for _ in range(every):
        time.sleep(1.1)
        got = await call(keyed, "tutor_turn", {
            "message": "What was UK inflation last year, and why? Sources please.", "client": "check_mcp",
            "this_message": {"question_depth": "mechanism", "engagement": "active", "request_type": "research",
                             "question_features": ["concept", "context", "asks_sources"], "web_access": True}})
        step = next((s for s in got.get("plan", []) if s["move"] == "literacy_task"), {})
        tasks.append(bool(step.get("data", {}).get("task")))
    check(learner.level(learner.part_p(student, "ail_verify")) == "secure" and tasks.count(True) == 1,
          f"at secure, a task comes once in {every} research questions (the rest get the feedback line only)",
          json.dumps(tasks))


async def how_ai_works(url: str) -> None:
    """How-AI-works checks (step 05e, demo-secure): cutoff only with asks_recent and no web access; a bad link
    gets the correction then a 4-option check on fabrication (a right letter raises it, a wrong one activates the
    misconception); one check per part per session; an ignored check re-asked once then scored 0; a
    self-correction gets a check on confidence and is stored."""
    student = "demo-secure"
    keyed = f"{url}?key={learner.get_student(student)['key']}"
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
    check(step.get("part_id") == "ail_how_cutoff" and moves(got)[-1] == "ask_mcq" and "literacy_task" not in moves(got),
          "cutoff: asks_recent with no web access gets a check, which wins over the literacy task", json.dumps(moves(got)))
    if step:
        chosen, _ = letter(student, True)
        before = learner.part_p(student, "ail_how_cutoff")
        await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_cutoff", "type": "mcq", "choice": chosen})
        check(learner.part_p(student, "ail_how_cutoff") > before, "a right letter raises the how-AI-works part")

    got = await turn("That ONS link you gave me doesn't work.", {"request_type": "research", "source_conflict": True,
                                                                   "question_features": ["context"]})
    step = how(got)
    check(moves(got)[0] == "source_conflict" and step.get("part_id") == "ail_how_fabrication"
          and len(step["data"].get("options", [])) == 4,
          "a bad link gets source_conflict first, then a 4-option check on fabrication", json.dumps(moves(got)))
    if step:
        chosen, picked = letter(student, False)
        got = await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_fabrication", "type": "mcq", "choice": chosen})
        held = learner._conn().execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?",
                                       (student, picked)).fetchone()
        data = (got.get("plan") or [{}])[0].get("data", {})
        check(bool(held and held["active"]) and bool(data.get("intuition")),
              "a wrong letter activates the picked misconception; the feedback carries the intuition line", picked)
    got = await turn("Another link is dead too.", {"request_type": "research", "source_conflict": True,
                                                   "question_features": ["context"]})
    check(not how(got), "a second failure of the same type in a session gets no second check", json.dumps(moves(got)))

    got = await turn("No, I think you were right the first time.", {"request_type": "concept", "pushback_changed": True})
    check(how(got).get("part_id") == "ail_how_agreement", "a changed answer after pushback gets a check on agreement",
          json.dumps(moves(got)))
    got = await turn("ok", {"request_type": "other"})
    check(moves(got) == ["reask"], "an ignored check is re-asked once", json.dumps(moves(got)))
    before = max_evidence_id()
    await turn("fine", {"request_type": "other"})
    zero = [(e["part_id"], e["evidence_type"], e["score"], e["point_id"]) for e in evidence(student, before)]
    check(zero == [("ail_how_agreement", "ail_how", 0.0, "ail_how_agreement_p1")],
          "still not answered, it is recorded as ail_how 0", json.dumps(zero))

    got = await turn("Sorry, which formula was it?", {"request_type": "concept", "conflict_flagged": True})
    flagged = learner._conn().execute("SELECT conflict_flagged FROM exchange_log WHERE student_id = ? ORDER BY id DESC LIMIT 1",
                                      (student,)).fetchone()
    check(how(got).get("part_id") == "ail_how_confidence" and bool(flagged and flagged[0] == 1),
          "a self-correction is stored and gets a check on confidence", json.dumps(moves(got)))
    if how(got):   # answer it, so the checks after this one start with nothing pending
        chosen, _ = letter(student, True)
        await turn(chosen, {"request_type": "other"}, {"part_id": "ail_how_confidence", "type": "mcq", "choice": chosen})
    progress = await call(keyed, "get_my_progress", {})
    lit = progress.get("ai_literacy") or {}
    check({"ask", "verify", "how_ai_works", "question_features"} <= set(lit) and bool(lit["how_ai_works"].get("held")),
          "get_my_progress shows AI-literacy skills, with the wrong ideas about AI still held",
          json.dumps(lit.get("how_ai_works")))


def shuffles() -> None:
    """MCQ options are shuffled differently for different students."""
    from edux import plan
    from edux.context_blocks import Turn
    settings = load_settings()
    orders = set()
    for student in ("demo-secure", "demo-weak", "demo-showme"):
        turn = Turn(student=learner.get_student(student), parts=[PART], message="", at=learner.now_iso(), limits={},
                    resolution={})
        step = plan.ask_mcq(turn, plan.question(PART, "check", graph.score_points(PART)[0]["point"], settings))
        orders.add(tuple(o["text"] for o in step["data"]["options"]))
    check(len(orders) > 1, "MCQ options are shuffled differently for different students", f"{len(orders)} orders for 3 students")


async def point_ids(keyed: str, student: str) -> None:
    """points_met scores the same as letters, full ids, a mix, or with no saved plan; another part's id is refused."""
    points = graph.score_points(PART)
    labels = {"question_depth": "mechanism", "engagement": "constructive"}
    cases = [("letters", ["a"], 1 / len(points)), ("full ids", [points[0]["id"]], 1 / len(points)),
             ("a mix", ["a", points[1]["id"]], 1.0), ("no saved plan", ["a"], 1 / len(points))]
    for label, met, expected in cases:
        if label == "no saved plan":
            with learner._conn() as conn:
                conn.execute("DELETE FROM issued_plan WHERE student_id = ?", (student,))
        time.sleep(1.1)
        before = max_evidence_id()
        got = await call(keyed, "tutor_turn", {"message": "my answer", "client": "check_mcp", "this_message": labels,
                                               "answer": {"part_id": PART, "type": "explain_back", "points_met": met}})
        scores = [e["score"] for e in evidence(student, before)]
        check(got.get("ok") is True and scores == [expected], f"points_met as {label} scores {expected}",
              got.get("error") or json.dumps(scores))
    other = graph.score_points("ped_definition")[0]["id"]
    before = max_evidence_id()
    got = await call(keyed, "tutor_turn", {"message": "my answer", "this_message": labels,
                                           "answer": {"part_id": PART, "type": "explain_back", "points_met": [other]}})
    check(got.get("ok") is False and max_evidence_id() == before, "a point id from another part is refused",
          got.get("error", ""))


async def main(url: str, key: str, student: str) -> None:
    keyed = f"{url}?key={key}"
    async with streamablehttp_client(keyed) as (read, write, _), ClientSession(read, write) as session:
        init = await session.initialize()
        instructions = init.instructions or ""
        words = len(instructions.split())
        sections = instructions.count(chr(10) + "## ")
        from edux import plan
        expected = len(plan.move_keys())
        check(0 < words <= INSTRUCTIONS_MAX_WORDS and sections == expected,
              f"the server instructions have one section per move ({expected}) and are at most {INSTRUCTIONS_MAX_WORDS} words",
              f"{words} words, {sections} move sections")
        check(not PLACEHOLDER.search(instructions), "no placeholder in the server instructions",
              ", ".join(PLACEHOLDER.findall(instructions)[:3]))
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
    shuffles()

    before = max_evidence_id()
    bad = await call(keyed, "tutor_turn", {"message": "it's the minus sign", "node_ids": [PART],
                                           "this_message": {"question_depth": "surface", "engagement": "active"},
                                           "answer": {"part_id": PART, "type": "explain_back", "points_met": ["no_such_point"]}})
    check(bad.get("ok") is False and max_evidence_id() == before, "an unknown point id is refused and records nothing",
          bad.get("error", ""))

    await point_ids(keyed, student)

    progress = await call(keyed, "get_my_progress", {})
    check({"tree", "levers", "reviews_due", "trends"} <= set(progress) and "p_now" not in json.dumps(progress),
          "get_my_progress (levels only)", f"{len(progress.get('levers', []))} levers")
    profile = await call(keyed, "update_my_profile", {"interests": "football"})
    check(profile.get("ok") is True, "update_my_profile", json.dumps(profile.get("profile")))

    for label, target in (("wrong key", f"{url}?key=not-a-real-key"), ("missing key", url)):
        response = httpx.post(target, json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                              headers={"Accept": "application/json, text/event-stream"})
        check(response.status_code == 401, f"{label} is refused", f"HTTP {response.status_code}")

    cli("set-profile", "--student", student, "--profile", "minimal")
    try:
        minimal = await call(keyed, "tutor_turn", {"message": "How do I calculate PED?",
                                                   "this_message": {"question_depth": "surface", "engagement": "passive"}})
    finally:
        cli("set-profile", "--student", student, "--profile", "default")
    check((minimal.get("style") or {}).get("interests") == "football",
          "style is sent again after the interests change", json.dumps(minimal.get("style", {}).get("interests")))
    check(minimal.get("plan") == [] and set(minimal.get("reference", {})) == {"notes"},
          "the minimal profile returns notes only and no plan", ", ".join(minimal.get("reference", {})))

    for who in sorted({student, "demo-secure", "demo-weak", "demo-showme"}):   # every student the run wrote events for
        before_rebuild = state(who)
        cli("rebuild", "--student", who)
        after_rebuild = state(who)
        changed = [t for t in STATE_TABLES if after_rebuild[t] != before_rebuild[t]]
        check(not changed, f"rebuild gives identical state ({who})", f"differs in {', '.join(changed)}" if changed else "")
        for t in changed:
            print("     before only:", sorted(set(before_rebuild[t]) - set(after_rebuild[t]))[:3])
            print("     after only: ", sorted(set(after_rebuild[t]) - set(before_rebuild[t]))[:3])

    ms = [r["ms"] for r in learner._conn().execute(
        "SELECT ms FROM call_log WHERE student_id = ? AND tool = 'tutor_turn' ORDER BY id DESC LIMIT 6", (student,))]
    check(bool(ms) and statistics.median(ms) < 100, "tutor_turn server time under 100 ms",
          f"median {statistics.median(ms):.0f} ms over {len(ms)} calls" if ms else "no calls logged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--student", default="demo-secure", help="a demo student (default demo-secure)")
    parser.add_argument("--key", help="the student's key (default: read from the database)")
    parser.add_argument("--keep", action="store_true", help="don't reset the demo students after the run")
    args = parser.parse_args()
    cli("seed-demo", "--reset")
    found = learner.get_student(args.student)
    if found is None:
        sys.exit(f"unknown student {args.student!r}; run python -m edux.cli seed-demo first")
    try:
        asyncio.run(main(args.url, args.key or found["key"], args.student))
    finally:
        if not args.keep:
            cli("seed-demo", "--reset")
    print(f"\n{'all checks passed' if not failures else f'{len(failures)} check(s) failed'}")
    sys.exit(1 if failures else 0)
