"""MCP server over Streamable HTTP at /mcp.

Each tool resolves the student from the ?key= in the request, calls one function in
service.py and returns its result. Descriptions and instructions come from text/.
Requests without a known key are refused with 401 before they reach MCP.
"""

from __future__ import annotations

import functools
import inspect
import os
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Annotated, Any, Literal
from urllib.parse import parse_qs

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from edux import learner, plan, service
from edux.settings import load_settings, read_text

# Input limits (judgement call, starting values): far above anything a student writes, far below what could fill the database.
MAX_MESSAGE = 8000  # characters in a student's message
MAX_INTERESTS = 300  # characters in the interests line
MAX_ID = 120  # characters in an id, name, letter or client label
MAX_LIST = 40  # items in any list the chatbot sends

QuestionDepth = Literal["surface", "mechanism", "transfer"]
Engagement = Literal["passive", "active", "constructive"]
Choice = Literal[learner.CHOICE_TAKEN]  # type: ignore[valid-type]
RequestType = Literal[learner.REQUEST_TYPES]  # type: ignore[valid-type]
QuestionFeature = Literal[learner.QUESTION_FEATURES]  # type: ignore[valid-type]
AnswerType = Literal[learner.ANSWER_TYPES]  # type: ignore[valid-type]


class ThisMessage(BaseModel):
    """Labels for the student's message in this turn."""

    question_depth: QuestionDepth = Field(description="surface (what is it), mechanism (how or why), transfer (applying it somewhere new)")
    engagement: Engagement = Field(description="passive (just reading), active (asking or answering), constructive (their own reasoning)")
    choice: Choice = Field(
        "none",
        description='what they chose: try_first, hint, just_show_me, skip_point ("I know this"), quiz, extend or stop (a pick from offer_choice), or none',
    )
    conflict_flagged: bool = Field(False, description="true when your reply corrects a mistake you made earlier")
    request_type: RequestType = Field(
        "concept", description="concept (about the course), research (a factual or current question about the world), homework, or other"
    )
    question_features: list[QuestionFeature] = Field(
        default_factory=list,
        description="research only: what the question shows: concept (names the idea), context (a place and time), asks_sources, asks_reasoning",
    )
    source_conflict: bool = Field(False, description="true when the student says a link failed or didn't say what was claimed")
    web_access: bool | None = Field(None, description="research only: can you search the web in this chat")
    asks_recent: bool = Field(False, description="research only: the question is about recent data or events")
    pushback_changed: bool = Field(False, description="true when the student challenged your last answer and you are changing it")
    confidence: Literal["guess", "fairly_sure", "certain", "none"] | None = Field(
        None,
        description="their reply to 'how sure are you?' (asked only after quick guesses): guess, fairly_sure or certain; none if they skipped or ignored it. Send it only when you asked",
    )
    words: int | None = Field(
        None,
        ge=0,
        description="the number of words in the student's message (a count only; used to tell a quick guess from a considered answer)",
    )
    asks_for_reviews: bool = Field(
        False,
        description="true when they ask to be quizzed or to revise without naming a topic: quiz me, what should I revise, do my reviews",
    )


class Answer(BaseModel):
    """The student's answer to what you asked last turn. The server works out the score."""

    part_id: str = Field(description="the part the question was on (the step's part_id)")
    type: AnswerType = Field(description="the asking step's data.answer_type: mcq, explain_back, review, extend, ...")
    choice: str | None = Field(
        None, description="mcq: the letter they picked, e.g. B. find_error: the number of the sentence they named, e.g. 2"
    )
    correct: bool | None = Field(None, description="prequestion only: did they pick the correct option")
    picked_misconception_id: str | None = Field(None, description="prequestion only: the option id they picked, if it was a misconception")
    points_met: list[Annotated[str, Field(max_length=MAX_ID)]] = Field(
        default_factory=list,
        max_length=MAX_LIST,
        description="the letters from score_next (a, b, ...) of the points the student actually produced",
    )
    misconception_ids: list[Annotated[str, Field(max_length=MAX_ID)]] = Field(
        default_factory=list, max_length=MAX_LIST, description="other misconceptions the answer showed"
    )


def _key_from_scope(scope: Scope) -> str | None:
    values = parse_qs(scope.get("query_string", b"").decode()).get("key")
    return values[0] if values else None


class RequireKey:
    """ASGI middleware: refuse HTTP requests whose ?key= doesn't belong to a student, before the MCP handshake."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and service.resolve_student(_key_from_scope(scope)) is None:
            response = JSONResponse({"error": "unknown or missing key; use the connector URL you were given"}, status_code=401)
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


def tutor_turn(
    ctx: Context,
    message: Annotated[str, Field(max_length=MAX_MESSAGE)],
    this_message: ThisMessage,
    node_ids: Annotated[list[Annotated[str, Field(max_length=MAX_ID)]], Field(max_length=MAX_LIST)] | None = None,
    answer: Answer | None = None,
    client: Annotated[str, Field(max_length=MAX_ID)] | None = None,
) -> dict:
    """Tool adapter for service.tutor_turn."""
    return service.tutor_turn(
        student_from_request(ctx), message, this_message.model_dump(), node_ids, answer.model_dump() if answer else None, client
    )


def get_my_progress(ctx: Context, include_parts: bool = False) -> dict:
    """Tool adapter for service.my_progress."""
    return service.my_progress(student_from_request(ctx), include_parts)


class AddAssessment(BaseModel):
    """An upcoming test of the student's own."""

    name: str = Field(max_length=MAX_ID, description="what they call it, e.g. Year 12 mock")
    kind: Literal[learner.ASSESSMENT_KINDS] = Field(description="homework, class_test, mock or written_assignment")  # type: ignore[valid-type]
    date: str = Field(description="YYYY-MM-DD, in the future")
    topics: list[Annotated[str, Field(max_length=MAX_ID)]] = Field(
        max_length=MAX_LIST, description="the topics it covers, as the student names them (topic names or spec codes)"
    )


class CoveredInClass(BaseModel):
    """Topics the student says their class has been taught."""

    topics: list[Annotated[str, Field(max_length=MAX_ID)]] = Field(
        max_length=MAX_LIST, description="the topics or sections covered (topic names or spec codes)"
    )
    when: str | None = Field(None, description="YYYY-MM-DD, about when they were taught (default today)")


class RemoveAssessment(BaseModel):
    """An assessment to remove."""

    id: int = Field(description="its id, from the profile's assessments")


def update_my_profile(
    ctx: Context,
    interests: Annotated[str, Field(max_length=MAX_INTERESTS)] | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
    add_assessment: AddAssessment | None = None,
    remove_assessment: RemoveAssessment | None = None,
    covered_in_class: CoveredInClass | None = None,
    reminders: bool | None = None,
) -> dict:
    """Tool adapter for service.update_profile."""
    return service.update_profile(
        student_from_request(ctx),
        interests,
        exam_date_override,
        answer_length,
        add_assessment.model_dump() if add_assessment else None,
        remove_assessment.id if remove_assessment else None,
        covered_in_class.model_dump() if covered_in_class else None,
        reminders,
    )


def plan_my_study(ctx: Context, assessment_id: int | None = None, sessions_per_week: int | None = None) -> dict:
    """Tool adapter for service.plan_study."""
    return service.plan_study(student_from_request(ctx), assessment_id, sessions_per_week)


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


ERROR_CHARS = 200  # stored and printed error text is cut to this (a validation message can echo the input)


def timed(name: str, fn: Callable[..., Any]) -> Callable[..., CallToolResult]:
    """Wrap a tool adapter: time it, write a call_log row, print one console line such as
    "tutor_turn demo-weak 18ms 3.1k chars ok", ending in OVER BUDGET when a tutor_turn result is still over
    results.max_chars, and send the result as compact JSON, the same text the size is counted from. The key is
    never printed or stored. A failure to log is reported on stderr and never replaces the tool's result."""

    @functools.wraps(fn)
    def wrapper(*args: object, **kwargs: object) -> CallToolResult:
        started, t0 = datetime.now(timezone.utc), time.perf_counter()
        result, error = None, None
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            error = (str(e) or type(e).__name__)[:ERROR_CHARS]
            raise
        finally:
            try:
                ms = (time.perf_counter() - t0) * 1000
                if error is None and isinstance(result, dict) and result.get("ok") is False:
                    error = str(result.get("error") or "ok: false")[:ERROR_CHARS]
                chars = service.result_size(result) if result is not None else 0
                ctx: Any = kwargs.get("ctx") or next((a for a in args if isinstance(a, Context)), None)
                student_id = _student_id(ctx)
                over = service.over_budget(name, chars, bool(kwargs.get("include_parts")))
                service.log_call(student_id, name, started, ms, chars, error is None, error, over)
                print(
                    f"{name} {student_id or '-'} {ms:.0f}ms {chars / 1000:.1f}k chars "
                    f"{'ok' if error is None else 'error: ' + error}{' OVER BUDGET' if over else ''}",
                    flush=True,
                )
            except Exception as log_error:  # logging is not the tool's job: keep the result
                print(f"call log failed for {name}: {type(log_error).__name__}", file=sys.stderr, flush=True)
        return CallToolResult(content=[TextContent(type="text", text=service.compact_json(result))])

    # FastMCP reads the return type from the signature: CallToolResult is sent as it is, with no schema check.
    wrapper.__signature__ = inspect.signature(fn, eval_str=True).replace(return_annotation=CallToolResult)  # type: ignore[attr-defined]
    return wrapper


TOOLS: dict[str, Callable[..., Any]] = {
    "tutor_turn": tutor_turn,
    "get_my_progress": get_my_progress,
    "update_my_profile": update_my_profile,
    "plan_my_study": plan_my_study,
}


def build_server() -> FastMCP:
    """Create the FastMCP server with instructions, tools, prompts and transport security from ALLOWED_HOSTS.
    The instructions include every move's section; a bad move text or going over instructions.max_words stops
    the server starting."""
    mcp = FastMCP(
        name="Synapse",
        instructions=plan.server_instructions(load_settings()),
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
    """The ASGI app: the MCP endpoint at /mcp behind the key check, with the web pages and their API beside it."""
    from edux.web.app import WebLayer

    return WebLayer(RequireKey(build_server().streamable_http_app()))


def serve(host: str, port: int) -> None:
    """Run the server with uvicorn. The access log is off: request URLs carry student keys."""
    import uvicorn

    uvicorn.run(http_app(), host=host, port=port, access_log=False)
