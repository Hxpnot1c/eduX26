"""SQLite connections: content.db (rebuilt on every load) and learner.db (migrated).

Both use WAL mode and each thread opens its own connection. The learner connection
attaches content.db as "content" so queries can join across both.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "migrations"
CONTENT_SCHEMA = Path(__file__).resolve().parent / "content_schema.sql"


def data_dir() -> Path:
    """Folder holding both databases, from EDUX_DATA_DIR."""
    raise NotImplementedError


def content_db_path() -> Path:
    """Path to content.db inside the data folder."""
    raise NotImplementedError


def learner_db_path() -> Path:
    """Path to learner.db inside the data folder."""
    raise NotImplementedError


def connect_content(path: Path | None = None) -> sqlite3.Connection:
    """Open content.db in WAL mode with row access by column name."""
    raise NotImplementedError


def connect_learner(path: Path | None = None, attach_content: bool = True) -> sqlite3.Connection:
    """Open learner.db in WAL mode, run pending migrations and attach content.db AS content."""
    raise NotImplementedError


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path = MIGRATIONS_DIR) -> list[int]:
    """Apply migrations/NNN_*.sql not yet in schema_version, in order; return the versions applied."""
    raise NotImplementedError
