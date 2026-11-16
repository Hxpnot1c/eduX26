"""Command line: python -m ingest.cli validate | load | templates | readme."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ingest import registry

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "coursepacks" / "README.md"


def cmd_validate(pack: Path) -> int:
    """Validate a pack; return a non-zero exit code on errors."""
    raise NotImplementedError


def cmd_load(pack: Path, db: Path | None = None, feedback_dir: Path | None = None) -> int:
    """Load a pack into content.db."""
    raise NotImplementedError


def cmd_templates(out_dir: Path) -> int:
    """Write header-only CSV templates from the registry."""
    for path in registry.write_templates(out_dir):
        print(path)
    return 0


def cmd_readme(out: Path = README_PATH) -> int:
    """Regenerate coursepacks/README.md from the registry."""
    out.write_text(registry.render_readme(), encoding="utf-8")
    print(out)
    return 0


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run a command."""
    parser = argparse.ArgumentParser(prog="python -m ingest.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate", help="check a course pack")
    p.add_argument("pack", type=Path)
    p = sub.add_parser("load", help="load a course pack into content.db")
    p.add_argument("pack", type=Path)
    p.add_argument("--db", type=Path, help="content.db path (default: $EDUX_DATA_DIR/content.db)")
    p.add_argument("--feedback-dir", type=Path, help="teacher feedback folder (default: teacher_feedback/)")
    p = sub.add_parser("templates", help="write empty CSV templates")
    p.add_argument("out_dir", type=Path)
    p = sub.add_parser("readme", help="regenerate coursepacks/README.md")
    p.add_argument("--out", type=Path, default=README_PATH)
    args = parser.parse_args(argv)

    if args.command == "validate":
        code = cmd_validate(args.pack)
    elif args.command == "load":
        code = cmd_load(args.pack, args.db, args.feedback_dir)
    elif args.command == "templates":
        code = cmd_templates(args.out_dir)
    else:
        code = cmd_readme(args.out)
    sys.exit(code)


if __name__ == "__main__":
    main()
