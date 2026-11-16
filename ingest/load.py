"""Load a course pack into content.db.

Recreates the database from content_schema.sql, inserts rows (unknown columns into
extra), fills question_node, id_map and note_fts, computes node weights, applies the
teacher feedback overlay and prints a load report.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LoadReport:
    """Counts per table, warnings, flagged rows, low-confidence rows and feedback not applied."""

    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)
    low_confidence: list[str] = field(default_factory=list)
    feedback_not_applied: list[str] = field(default_factory=list)


def load_pack(pack_dir: Path, db_path: Path | None = None, feedback_dir: Path | None = None) -> LoadReport:
    """Validate and load a pack into a fresh content.db; return the report."""
    raise NotImplementedError


def create_database(db_path: Path) -> sqlite3.Connection:
    """Delete and recreate content.db from content_schema.sql."""
    raise NotImplementedError


def insert_rows(conn: sqlite3.Connection, pack_dir: Path) -> dict[str, int]:
    """Insert every file's rows, parsing ; lists; return counts per table."""
    raise NotImplementedError


def build_note_index(conn: sqlite3.Connection) -> None:
    """Fill note_fts from summary, key points and key wording."""
    raise NotImplementedError


def compute_weights(conn: sqlite3.Connection) -> None:
    """Fill node_weight with exam_weight, dependents and importance."""
    raise NotImplementedError


def apply_feedback(conn: sqlite3.Connection, feedback_csv: Path) -> list[str]:
    """Apply teacher feedback in ts order and record each action; return messages for those not applied."""
    raise NotImplementedError


def print_report(report: LoadReport) -> None:
    """Print the load report."""
    raise NotImplementedError
