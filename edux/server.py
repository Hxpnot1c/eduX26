"""MCP server over Streamable HTTP at /mcp.

Each tool resolves the student from the ?key= in the request, calls one function in
service.py and returns its result. Descriptions and instructions come from text/.
"""

from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import Context, FastMCP

QuestionDepth = Literal["surface", "mechanism", "transfer"]
Engagement = Literal["passive", "active", "constructive"]
SupportGiven = Literal["worked_example", "hint", "explain_back", "none"]
ChoiceTaken = Literal["try_first", "hint", "just_show_me", "none"]


def build_server() -> FastMCP:
    """Create the FastMCP server with instructions, tools, prompts and transport security from ALLOWED_HOSTS."""
    raise NotImplementedError


def student_from_request(ctx: Context) -> dict:
    """Read the key from the request query string and return its student; reject unknown keys."""
    raise NotImplementedError


def get_learning_context(ctx: Context, message: str, node_ids: list[str] | None = None, client: str | None = None) -> dict:
    """Tool adapter for service.learning_context."""
    raise NotImplementedError


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
) -> dict:
    """Tool adapter for service.log_exchange."""
    raise NotImplementedError


def get_my_progress(ctx: Context) -> dict:
    """Tool adapter for service.my_progress."""
    raise NotImplementedError


def update_my_profile(
    ctx: Context,
    interests: str | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
) -> dict:
    """Tool adapter for service.update_profile."""
    raise NotImplementedError


def review_due() -> str:
    """Prompt: "Quiz me on what's due." """
    raise NotImplementedError


def check_me(topic: str) -> str:
    """Prompt: "Check my understanding of ___." """
    raise NotImplementedError


def serve(host: str, port: int) -> None:
    """Run the server with uvicorn."""
    raise NotImplementedError
