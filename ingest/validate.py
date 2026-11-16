"""Validate a course pack against the registry and the format rules.

All errors and warnings are collected rather than stopping at the first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Issue:
    """One error or warning, with where it was found."""

    file: str
    row: int | None
    message: str


@dataclass
class ValidationResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_pack(pack_dir: Path) -> ValidationResult:
    """Run every check in the course-pack format reference."""
    raise NotImplementedError
