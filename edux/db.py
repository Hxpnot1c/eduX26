"""SQLite connections: content.db (rebuilt on every load) and learner.db (migrated).

Both use WAL mode and each thread opens its own connection. The learner connection
attaches content.db as "content" so queries can join across both.
"""

from __future__ import annotations

import os
import sqlite3
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


def connect_learner(path: Path | None = None, attach_content: bool = True) -> sqlite3.Connection:
    """Open learner.db in WAL mode, run pending migrations and attach content.db AS content."""
    raise NotImplementedError


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path = MIGRATIONS_DIR) -> list[int]:
    """Apply migrations/NNN_*.sql not yet in schema_version, in order; return the versions applied."""
    raise NotImplementedError
