"""What each tool does. server.py adapts arguments; the logic lives here."""

from __future__ import annotations


def resolve_student(key: str) -> dict | None:
    """Look up the student for a connector key."""
    raise NotImplementedError


def learning_context(student: dict, message: str, node_ids: list[str] | None = None, client: str | None = None) -> dict:
    """Resolve focus parts and assemble the student's context blocks."""
    raise NotImplementedError


def log_exchange(
    student: dict,
    node_ids: list[str],
    question_depth: str,
    engagement: str,
    offloading: bool,
    support_given: str | None = None,
    choice_taken: str | None = None,
    misconception_ids: list[str] | None = None,
    conflict_flagged: bool = False,
    prompt_text: str | None = None,
    client: str | None = None,
) -> dict:
    """Record the exchange event and return {"ok": True}; the update is applied in the background."""
    raise NotImplementedError


def my_progress(student: dict) -> dict:
    """Tree with levels, biggest levers, weak links, reviews due and AI-literacy trends."""
    raise NotImplementedError


def update_profile(
    student: dict,
    interests: str | None = None,
    exam_date_override: str | None = None,
    answer_length: int | None = None,
) -> dict:
    """Update student_profile and return it."""
    raise NotImplementedError
