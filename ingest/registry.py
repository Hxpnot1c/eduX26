"""Every course-pack file and column, defined once.

Validation, loading, the empty CSV templates and coursepacks/README.md are generated
from these definitions. Adding a column is one line here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Column:
    """One CSV column: type, required flag, allowed values and default."""

    name: str
    type: str = "text"
    required: bool = False
    enum: tuple[str, ...] = ()
    default: str | None = None
    is_list: bool = False


@dataclass(frozen=True)
class FileSpec:
    """One course-pack CSV file and the content.db table it loads into."""

    name: str
    table: str
    columns: tuple[Column, ...] = field(default_factory=tuple)
    content_row: bool = False


FILES: dict[str, FileSpec] = {}


def get(file_name: str) -> FileSpec:
    """The spec for a course-pack file, e.g. "nodes.csv"."""
    raise NotImplementedError


def write_templates(out_dir: Path) -> list[Path]:
    """Write a header-only CSV for every file; return the paths written."""
    raise NotImplementedError


def render_readme() -> str:
    """Markdown description of every file and column, for coursepacks/README.md."""
    raise NotImplementedError
