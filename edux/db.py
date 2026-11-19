"""SQLite connections: content.db (rebuilt on every load) and learner.db (migrated).

Both use WAL mode and each thread opens its own connection. The learner connection
attaches content.db as "content" so queries can join across both.
"""

from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "migrations"
CONTENT_SCHEMA = Path(__file__).resolve().parent / "content_schema.sql"


def data_dir() -> Path:
    """Folder holding both databases, from EDUX_DATA_DIR (default ./data); created if missing."""
    path = Path(os.environ.get("EDUX_DATA_DIR") or ROOT / "data")
    path.mkdir(parents=True, exist_ok=True)
    return path


def content_db_path() -> Path:
    """Path to content.db inside the data folder."""
    return data_dir() / "content.db"


def learner_db_path() -> Path:
    """Path to learner.db inside the data folder."""
    return data_dir() / "learner.db"


def connect_content(path: Path | None = None) -> sqlite3.Connection:
    """Open content.db in WAL mode with row access by column name."""
    conn = sqlite3.connect(path or content_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def connect_learner(path: Path | None = None, attach_content: bool = True, content_path: Path | None = None) -> sqlite3.Connection:
    """Open learner.db in WAL mode, run pending migrations and attach content.db AS content."""
    conn = sqlite3.connect(path or learner_db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    run_migrations(conn)
    if attach_content:
        conn.execute("ATTACH DATABASE ? AS content", (str(content_path or content_db_path()),))
    return conn


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path = MIGRATIONS_DIR) -> list[int]:
    """Apply migrations/NNN_*.sql not yet in schema_version, in order; return the versions applied.

    Each migration and its schema_version row run in one transaction.
    """
    has_table = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'").fetchone()
    done = {r[0] for r in conn.execute("SELECT version FROM schema_version")} if has_table else set()
    applied = []
    for path in sorted(migrations_dir.glob("[0-9][0-9][0-9]_*.sql")):
        match = re.match(r"\d+", path.name)
        assert match is not None  # the glob above only yields names that start with three digits
        version = int(match.group())
        if version in done:
            continue
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        conn.executescript(
            f"BEGIN;\n{path.read_text(encoding='utf-8')}\n"
            f"INSERT INTO schema_version (version, applied_at) VALUES ({version}, '{now}');\nCOMMIT;"
        )
        applied.append(version)
    return applied
