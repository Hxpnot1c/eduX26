"""Context blocks returned by get_learning_context.

Each block is one function taking (student, parts, settings) and returning a small
dict, or None to leave it out. context.toml chooses the blocks, order and limits per profile.
"""

from __future__ import annotations

from collections.abc import Callable

from edux.settings import ContextConfig, Settings


def focus(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Resolved parts with name, level and type, or candidates when ambiguous."""
    raise NotImplementedError


def support(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Support level and its text."""
    raise NotImplementedError


def weak_prerequisites(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Prerequisites below secure."""
    raise NotImplementedError


def anchor(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """A secure analogous part with the edge note."""
    raise NotImplementedError


def confusables(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Parts to contrast."""
    raise NotImplementedError


def active_misconceptions(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Active wrong ideas and their corrections."""
    raise NotImplementedError


def notes(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Summaries, key points and key wording in source-authority order, with source titles."""
    raise NotImplementedError


def exam_relevance(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Papers and marks that test these parts."""
    raise NotImplementedError


def reviews_due(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Up to N due parts."""
    raise NotImplementedError


def teaching_note(student: dict, parts: list[str], settings: Settings) -> dict | None:
    """Short paragraph filled from text/teaching_note.md."""
    raise NotImplementedError


Block = Callable[[dict, list[str], Settings], dict | None]

BLOCKS: dict[str, Block] = {
    "focus": focus,
    "support": support,
    "weak_prerequisites": weak_prerequisites,
    "anchor": anchor,
    "confusables": confusables,
    "active_misconceptions": active_misconceptions,
    "notes": notes,
    "exam_relevance": exam_relevance,
    "reviews_due": reviews_due,
    "teaching_note": teaching_note,
}


def assemble(profile: str, student: dict, parts: list[str], settings: Settings, context: ContextConfig) -> list[dict]:
    """Run the profile's blocks in order with their limits; skip unknown blocks with a warning."""
    raise NotImplementedError
