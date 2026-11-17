"""Check a running eduX server through the Python MCP client, without Node or MCP Inspector.

    python scripts/check_mcp.py --key <student key> [--url http://127.0.0.1:8000/mcp] [--student <id>]

Lists the tools and prompts, calls each tool once, checks that a wrong key is refused with 401 and,
with --student, switches the student's profile to minimal and back to show the context changes.
Exits non-zero if any check fails. Logs one real exchange for the student.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

EXPECTED_TOOLS = {"get_learning_context", "log_exchange", "get_my_progress", "update_my_profile"}
EXPECTED_PROMPTS = {"review_due", "check_me"}
failures: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f": {detail}" if detail else ""))
    if not ok:
        failures.append(label)


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


async def main(url: str, key: str, student: str | None, message: str) -> None:
    keyed = f"{url}?key={key}"
    async with streamablehttp_client(keyed) as (read, write, _), ClientSession(read, write) as session:
        await session.initialize()
        tools = {t.name for t in (await session.list_tools()).tools}
        check(EXPECTED_TOOLS <= tools, "lists the tools", ", ".join(sorted(tools)))
        prompts = {p.name for p in (await session.list_prompts()).prompts}
        check(EXPECTED_PROMPTS <= prompts, "lists the prompts", ", ".join(sorted(prompts)))
        for name in sorted(EXPECTED_PROMPTS & prompts):
            args = {"topic": "price elasticity of demand"} if name == "check_me" else {}
            got = await session.get_prompt(name, args)
            check(bool(got.messages), f"prompt {name}")

    context = await call(keyed, "get_learning_context", {"message": message})
    check(bool(context.get("blocks")), "get_learning_context returns blocks",
          f"profile {context.get('profile')}: {', '.join(context.get('blocks', {}))}")
    focus = context.get("blocks", {}).get("focus", {})
    parts = [p["id"] for p in focus.get("parts", [])] or [c["id"] for c in focus.get("candidates", [])][:1]
    if parts:
        logged = await call(keyed, "log_exchange", {"node_ids": parts[:1], "question_depth": "mechanism",
                                                    "engagement": "active", "offloading": False,
                                                    "support_given": "worked_example", "client": "check_mcp"})
        check(logged == {"ok": True}, "log_exchange returns ok", json.dumps(logged))
    else:
        check(False, "log_exchange returns ok", "no focus part to log against")
    bad = await call(keyed, "log_exchange", {"node_ids": ["no_such_part"], "question_depth": "surface",
                                             "engagement": "passive", "offloading": False,
                                             "evidence": [{"part_id": "no_such_part", "type": "explain_back", "score": 1}]})
    check(bad.get("ok") is False, "log_exchange rejects an unknown part", bad.get("error", ""))
    progress = await call(keyed, "get_my_progress", {})
    check({"tree", "levers", "reviews_due", "trends"} <= set(progress), "get_my_progress",
          f"{len(progress.get('levers', []))} levers")
    profile = await call(keyed, "update_my_profile", {"interests": "football"})
    check(profile.get("ok") is True, "update_my_profile", json.dumps(profile.get("profile")))

    for label, target in (("wrong key", f"{url}?key=not-a-real-key"), ("missing key", url)):
        response = httpx.post(target, json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                              headers={"Accept": "application/json, text/event-stream"})
        check(response.status_code == 401, f"{label} is refused", f"HTTP {response.status_code}")

    if student:
        def set_profile(profile: str) -> None:
            subprocess.run([sys.executable, "-m", "edux.cli", "set-profile", "--student", student, "--profile", profile],
                           check=True, capture_output=True)

        set_profile("minimal")
        try:
            minimal = await call(keyed, "get_learning_context", {"message": message})
        finally:
            set_profile("default")
        check(minimal.get("profile") == "minimal" and set(minimal["blocks"]) != set(context["blocks"]),
              "switching to minimal changes the output", ", ".join(minimal.get("blocks", {})))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--key", required=True)
    parser.add_argument("--student", help="student id; enables the profile switch check (runs edux.cli set-profile)")
    parser.add_argument("--message", default="how do I calculate PED?")
    args = parser.parse_args()
    asyncio.run(main(args.url, args.key, args.student, args.message))
    print(f"\n{'all checks passed' if not failures else f'{len(failures)} check(s) failed'}")
    sys.exit(1 if failures else 0)
