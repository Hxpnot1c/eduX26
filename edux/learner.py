"""Learner model: append-only events, scoring rules and state rebuilt from events.

part_state, student_misconception, approach_record and review_queue are derived:
rebuild_state replays a student's events through the current rules in settings.toml.
"""

from __future__ import annotations

from datetime import datetime


def record_exchange(
    student_id: str,
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
) -> int:
    """Write an exchange event with protocol and settings_hash, queue apply_exchange, return the event id."""
    raise NotImplementedError


def apply_exchange(event: dict) -> None:
    """Apply one exchange event: nudges, offloading, misconception activation, overconfidence, last_seen."""
    raise NotImplementedError


def apply_evidence(student_id: str, part_id: str, evidence_type: str, correct: bool, ts: datetime | None = None) -> None:
    """BKT update, half-life change, prerequisite propagation, misconception clearing and review scheduling."""
    raise NotImplementedError


def p_now(p_known: float, half_life_days: float, last_seen: datetime, now: datetime | None = None) -> float:
    """Decayed p_known at read time."""
    raise NotImplementedError


def level(p: float) -> str:
    """new, developing or secure from the thresholds in settings.toml."""
    raise NotImplementedError


def rollup(student_id: str, node_id: str) -> float:
    """Importance-weighted mean p_now of the parts under a node."""
    raise NotImplementedError


def due_reviews(student_id: str, limit: int) -> list[dict]:
    """Parts due for review, ordered by importance."""
    raise NotImplementedError


def candidates(student_id: str, limit: int) -> list[dict]:
    """Parts to teach next: p_now in the queue band and prerequisites at least developing."""
    raise NotImplementedError


def support_level(p: float) -> str:
    """worked_example, hint or explain_back from p_now."""
    raise NotImplementedError


def anchor(student_id: str, part_id: str) -> dict | None:
    """A secure analogous part with its edge note."""
    raise NotImplementedError


def approaches(student_id: str, part_id: str) -> list[dict]:
    """Past support approaches on the part and whether the next check went well."""
    raise NotImplementedError


def rebuild_state(student_id: str) -> None:
    """Delete the student's derived rows and replay their events in ts order."""
    raise NotImplementedError


def rebuild_all() -> None:
    """rebuild_state for every student."""
    raise NotImplementedError


def start_worker() -> None:
    """Start the background thread that applies queued events."""
    raise NotImplementedError
