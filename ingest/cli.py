"""Command line: python -m ingest.cli validate | load | templates."""

from __future__ import annotations

from pathlib import Path


def cmd_validate(pack: Path) -> int:
    """Validate a pack; return a non-zero exit code on errors."""
    raise NotImplementedError


def cmd_load(pack: Path) -> int:
    """Load a pack into content.db."""
    raise NotImplementedError


def cmd_templates(out_dir: Path) -> int:
    """Write header-only CSV templates from the registry."""
    raise NotImplementedError


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run a command."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
