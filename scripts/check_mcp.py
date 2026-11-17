"""Check a running eduX server through the Python MCP client, without Node or MCP Inspector.

    python scripts/check_mcp.py [--student demo-secure] [--key <key>] [--url http://127.0.0.1:8000/mcp]

Run it from the repo root against a server started on the same data folder (EDUX_DATA_DIR), with the
example-mini pack loaded and the demo students seeded. It:
- resets the demo students (seed-demo --reset keeps their keys), so the run starts from the seeded state;
- lists the tools and prompts;
- runs a three-message conversation as the student through tutor_turn and checks each plan, the recorded
  evidence and the misconception state, and that no p_now reaches the chatbot;
- checks a bad answer is refused and records nothing, get_my_progress, update_my_profile, that a wrong or
  missing key is refused with 401, and that the minimal profile returns no plan;
- checks rebuild gives identical state and tutor_turn's median server time is under 100 ms;
- resets the demo students again, so the demo is left as seeded (--keep leaves the run's events).
Exits non-zero if any check fails. The key is read from the database when --key is not given.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import subprocess
import sys
import time

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from edux import graph, learner

EXPECTED_TOOLS = {"tutor_turn", "get_my_progress", "update_my_profile"}
EXPECTED_PROMPTS = {"review_due", "check_me"}
PART, MISCONCEPTION = "ped_formula", "ped_formula_m1"
STATE_TABLES = ("part_state", "student_misconception", "review_queue", "approach_record", "evidence_derived")
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


async def conversation(keyed: str, student: str) -> None:
    """The three-message run from the step 05b done-when list."""
    start = max_evidence_id()
    turns = []

    async def turn(arguments: dict) -> dict:
        if turns:
            time.sleep(1.1)   # event timestamps are to the second; keep the three turns in separate seconds
        got = await call(keyed, "tutor_turn", {"client": "check_mcp", **arguments})
        turns.append(got)
        return got

    first = await turn({"message": "How do I calculate PED?",
                        "this_message": {"question_depth": "mechanism", "engagement": "active"}})
    check(moves(first) == ["prequestion"] and first["plan"][0]["part_id"] == PART,
          "1. a question on an untaught part gets a single pre-question", ", ".join(moves(first)) or first.get("error", ""))

    second = await turn({"message": "Is it the change in price divided by the change in quantity?",
                         "this_message": {"question_depth": "surface", "engagement": "active"},
                         "answer": {"part_id": PART, "type": "prequestion", "correct": False,
                                    "picked_misconception_id": MISCONCEPTION}})
    named = ((second.get("plan") or [{}])[0].get("data") or {}).get("misconceptions") or [{}]
    check(moves(second) == ["feedback", "teach"] and named[0].get("id") == MISCONCEPTION,
          "2. a wrong pre-question answer gets feedback naming it, then teach", ", ".join(moves(second)) or second.get("error", ""))
    held = learner._conn().execute("SELECT active FROM student_misconception WHERE student_id = ? AND misconception_id = ?",
                                   (student, MISCONCEPTION)).fetchone()
    check(bool(held and held["active"]), f"2. {MISCONCEPTION} is active")
    recorded = evidence(student, start)
    check([(e["evidence_type"], e["score"]) for e in recorded] == [("prequestion", 0.0)],
          "2. the pre-question evidence is recorded", json.dumps([(e["evidence_type"], e["score"]) for e in recorded]))

    points = graph.score_points(PART)
    third = await turn({"message": "You divide the change by the original value and times by 100 for each percentage.",
                        "this_message": {"question_depth": "mechanism", "engagement": "constructive"},
                        "answer": {"part_id": PART, "type": "explain_back", "points_met": [points[0]["id"]]}})
    missing = ((third.get("plan") or [{}, {}])[-1].get("data") or {}).get("missing")
    check(moves(third) == ["feedback", "reteach"] and missing == [p["point"] for p in points[1:]],
          "3. an explanation missing a point gets feedback, then reteach with only that point",
          f"{', '.join(moves(third)) or third.get('error', '')}; missing {missing}")
    recorded = evidence(student, start)
    check(len(recorded) == 2 and recorded[-1]["score"] == 1 / len(points),
          f"3. the recorded score is {1 / len(points)}", json.dumps([e["score"] for e in recorded]))

    leaked = [i + 1 for i, t in enumerate(turns) if "p_now" in json.dumps(t)]
    check(not leaked, "no p_now in tutor_turn output", f"found in turn(s) {leaked}" if leaked else "")


async def main(url: str, key: str, student: str) -> None:
    keyed = f"{url}?key={key}"
    async with streamablehttp_client(keyed) as (read, write, _), ClientSession(read, write) as session:
        await session.initialize()
        tools = {t.name for t in (await session.list_tools()).tools}
        check(tools == EXPECTED_TOOLS, "lists the tools", ", ".join(sorted(tools)))
        prompts = {p.name for p in (await session.list_prompts()).prompts}
        check(EXPECTED_PROMPTS <= prompts, "lists the prompts", ", ".join(sorted(prompts)))
        for name in sorted(EXPECTED_PROMPTS & prompts):
            args = {"topic": "price elasticity of demand"} if name == "check_me" else {}
            got = await session.get_prompt(name, args)
            check(bool(got.messages), f"prompt {name}")

    await conversation(keyed, student)

    before = max_evidence_id()
    bad = await call(keyed, "tutor_turn", {"message": "it's the minus sign", "node_ids": [PART],
                                           "this_message": {"question_depth": "surface", "engagement": "active"},
                                           "answer": {"part_id": PART, "type": "explain_back", "points_met": ["no_such_point"]}})
    check(bad.get("ok") is False and max_evidence_id() == before, "an unknown point id is refused and records nothing",
          bad.get("error", ""))

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
    check(minimal.get("plan") == [] and set(minimal.get("reference", {})) == {"notes"},
          "the minimal profile returns notes only and no plan", ", ".join(minimal.get("reference", {})))

    before_rebuild = state(student)
    cli("rebuild", "--student", student)
    after_rebuild = state(student)
    changed = [t for t in STATE_TABLES if after_rebuild[t] != before_rebuild[t]]
    check(not changed, "rebuild gives identical state", f"differs in {', '.join(changed)}" if changed else "")
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
