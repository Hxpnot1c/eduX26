"""MCP server over Streamable HTTP at /mcp.

Each tool resolves the student from the ?key= in the request, calls one function in
service.py and returns its result. Descriptions and instructions come from text/.
Requests without a known key are refused with 401 before they reach MCP.
"""

from __future__ import annotations

import functools
import json
import os
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import parse_qs

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from edux import learner, service
from edux.settings import load_settings, read_text

QuestionDepth = Literal["surface", "mechanism", "transfer"]
Engagement = Literal["passive", "active", "constructive"]
SupportGiven = Literal["worked_example", "hint", "explain_back", "none"]
ChoiceTaken = Literal["try_first", "hint", "just_show_me", "none"]
# Evidence types the chatbot may send: the keys of [bkt.evidence], except "immediate", which the server assigns.
EvidenceType = Literal[tuple(t for t in load_settings().bkt.evidence if t != "immediate")]  # type: ignore[valid-type]


class EvidenceItem(BaseModel):
    """What the student produced this turn on one part, scored against the notes and mark points."""

    part_id: str = Field(description="part (or concept) id the answer was about")
    type: EvidenceType = Field(description="what kind of answer it was, e.g. explain_back or prequestion")
    score: float = Field(ge=0, le=1, description="0-1 against the mark points and key wording")
    misconception_ids: list[str] = Field(default_factory=list, description="misconceptions the answer showed")


def _key_from_scope(scope: Scope) -> str | None:
    values = parse_qs(scope.get("query_string", b"").decode()).get("key")
    return values[0] if values else None


class RequireKey:
    """ASGI middleware: refuse HTTP requests whose ?key= doesn't belong to a student, before the MCP handshake."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and service.resolve_student(_key_from_scope(scope)) is None:
            response = JSONResponse({"error": "unknown or missing key; use the connector URL you were given"},
                                    status_code=401)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _security() -> TransportSecuritySettings:
    """Host and Origin checks from ALLOWED_HOSTS (comma-separated), so a tunnel host works; any port is allowed."""
    hosts = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[v for h in hosts for v in (h, f"{h}:*")],
        allowed_origins=[v for h in hosts for scheme in ("http", "https") for v in (f"{scheme}://{h}", f"{scheme}://{h}:*")],
    )


def student_from_request(ctx: Context) -> dict:
    """Read the key from the request query string and return its student; reject unknown keys."""
    request = ctx.request_context.request
    key = request.query_params.get("key") if request is not None else None
    student = service.resolve_student(key)
    if student is None:
        raise ToolError("unknown or missing key; use the connector URL you were given")
    return student


def get_learning_context(ctx: Context, message: str, node_ids: list[str] | None = None, client: str | None = None) -> dict:
    """Tool adapter for service.learning_context."""
    return service.learning_context(student_from_request(ctx), message, node_ids, client)


def log_exchange(
    ctx: Context,
    node_ids: list[str],
    question_depth: QuestionDepth,
    engagement: Engagement,
    offloading: bool,
    support_given: SupportGiven | None = None,
    choice_taken: ChoiceTaken | None = None,
    misconception_ids: list[str] | None = None,
    conflict_flagged: bool = False,
    prompt_text: str | None = None,
    evidence: list[EvidenceItem] | None = None,
    client: str | None = None,
) -> dict:
    """Tool adapter for service.log_exchange."""
    return service.log_exchange(student_from_request(ctx), node_ids, question_depth, engagement, offloading,
                                support_given, choice_taken, misconception_ids, conflict_flagged, prompt_text,
                                [e.model_dump() for e in evidence or []], client)


def get_my_progress(ctx: Context, include_parts: bool = False) -> dict:
    """Tool adapter for service.my_progress."""
    return service.my_progress(student_from_request(ctx), include_parts)


def update_my_profile(
    ctx: Context,
    interests: str | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
) -> dict:
    """Tool adapter for service.update_profile."""
    return service.update_profile(student_from_request(ctx), interests, exam_date_override, answer_length)


def review_due() -> str:
    """Prompt: "Quiz me on what's due." """
    return read_text("prompts/review_due.md").strip()


def check_me(topic: str) -> str:
    """Prompt: "Check my understanding of ___." """
    return read_text("prompts/check_me.md").strip().format(topic=topic.strip())


def _student_id(ctx: Context | None) -> str | None:
    """The student id for the request, for the call log; None if the key doesn't resolve."""
    try:
        return student_from_request(ctx)["id"] if ctx is not None else None
    except (ToolError, AttributeError, ValueError):
        return None


def timed(name: str, fn: Callable[..., dict]) -> Callable[..., dict]:
    """Wrap a tool adapter: time it, write a call_log row and print one console line such as
    "tutor_turn demo-weak 18ms 3.1k chars ok". The key is never printed or stored."""

    @functools.wraps(fn)
    def wrapper(*args: object, **kwargs: object) -> dict:
        started, t0 = datetime.now(timezone.utc), time.perf_counter()
        result, error = None, None
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e) or type(e).__name__
            raise
        finally:
            ms = (time.perf_counter() - t0) * 1000
            if error is None and isinstance(result, dict) and result.get("ok") is False:
                error = str(result.get("error") or "ok: false")
            chars = len(json.dumps(result, default=str)) if result is not None else 0
            ctx = kwargs.get("ctx") or next((a for a in args if isinstance(a, Context)), None)
            student_id = _student_id(ctx)
            service.log_call(student_id, name, started, ms, chars, error is None, error)
            print(f"{name} {student_id or '-'} {ms:.0f}ms {chars / 1000:.1f}k chars "
                  f"{'ok' if error is None else 'error: ' + error}", flush=True)

    return wrapper


TOOLS = {
    "get_learning_context": get_learning_context,
    "log_exchange": log_exchange,
    "get_my_progress": get_my_progress,
    "update_my_profile": update_my_profile,
}


def build_server() -> FastMCP:
    """Create the FastMCP server with instructions, tools, prompts and transport security from ALLOWED_HOSTS."""
    mcp = FastMCP(
        name="eduX",
        instructions=read_text("server_instructions.md"),
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=_security(),
    )
    for name, fn in TOOLS.items():
        mcp.add_tool(timed(name, fn), name=name, description=read_text(f"tools/{name}.md"))
    mcp.prompt(name="review_due", description="Quiz me on what's due.")(review_due)
    mcp.prompt(name="check_me", description="Check my understanding of a topic.")(check_me)
    return mcp


def http_app() -> ASGIApp:
    """The ASGI app: the MCP endpoint at /mcp behind the key check."""
    return RequireKey(build_server().streamable_http_app())


def serve(host: str, port: int) -> None:
    """Run the server with uvicorn. The access log is off: request URLs carry student keys."""
    import uvicorn

    learner.start_worker()
    uvicorn.run(http_app(), host=host, port=port, access_log=False)
