"""Command line: python -m edux.cli load | rebuild | add-student | state | serve | seed-demo."""

from __future__ import annotations

from pathlib import Path


def cmd_load(pack: Path) -> None:
    """Load a course pack into content.db (delegates to ingest)."""
    raise NotImplementedError


def cmd_rebuild(student: str | None = None) -> None:
    """Rebuild derived state for one student, or all."""
    raise NotImplementedError


def cmd_add_student(name: str, course: str) -> None:
    """Create a student and print their key."""
    raise NotImplementedError


def cmd_state(student: str, node: str | None = None) -> None:
    """Print parts with p_now, level and due date."""
    raise NotImplementedError


def cmd_serve(host: str | None = None, port: int | None = None) -> None:
    """Start the MCP server."""
    raise NotImplementedError


def cmd_seed_demo() -> None:
    """Create the demo students by replaying scripted events."""
    raise NotImplementedError


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run a command."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
