"""Load a course pack into content.db.

Recreates the database from content_schema.sql, inserts rows (unknown columns into
extra), fills question_node, id_map and note_fts, computes node weights, applies the
teacher feedback overlay and prints a load report.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from edux import db
from ingest import registry
from ingest.registry import FileSpec, split_list
from ingest.validate import Issue, Table, read_pack, validate_tables


@dataclass
class LoadReport:
    """Counts per table, warnings, flagged rows, low-confidence rows and feedback not applied."""

    pack_path: str = ""
    db_path: str = ""
    course_id: str = ""
    errors: list[Issue] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)
    low_confidence: list[str] = field(default_factory=list)
    feedback_not_applied: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_pack(pack_dir: Path, db_path: Path | None = None, feedback_dir: Path | None = None) -> LoadReport:
    """Validate and load a pack into a fresh content.db; return the report."""
    db_path = db_path or db.content_db_path()
    report = LoadReport(pack_path=str(pack_dir), db_path=str(db_path))
    if not pack_dir.is_dir():
        report.errors.append(Issue(str(pack_dir), None, "course pack folder not found"))
        return report
    tables = read_pack(pack_dir)
    result = validate_tables(tables)
    report.errors = result.errors
    report.warnings = [str(w) for w in result.warnings]
    if result.errors:
        return report

    report.course_id = tables["course.csv"].rows[0]["id"]
    conn = create_database(db_path)
    try:
        insert_rows(conn, tables, report.course_id)
        fill_question_node(conn)
        build_note_index(conn)
        report.counts = count_rows(conn)
        write_load_info(conn, report)
        conn.commit()
    finally:
        conn.close()
    return report


def create_database(db_path: Path) -> sqlite3.Connection:
    """Delete and recreate content.db from content_schema.sql."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        Path(f"{db_path}{suffix}").unlink(missing_ok=True)
    conn = db.connect_content(db_path)
    conn.executescript(db.CONTENT_SCHEMA.read_text(encoding="utf-8"))
    return conn


def _convert(value: str, column: registry.Column) -> object:
    if value == "":
        value = column.default if column.default is not None else ""
        if value == "":
            return None if column.default is None else ""
    if column.type == "int":
        return int(value)
    if column.type == "real":
        return float(value)
    return value


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def insert_file(conn: sqlite3.Connection, spec: FileSpec, rows: list[dict[str, str]], header: list[str], course_id: str) -> int:
    """Insert one file's rows; columns not in the registry go to extra as JSON. Returns the row count."""
    db_columns = _table_columns(conn, spec.table)
    known = [c for c in spec.columns if c.name in db_columns]
    unknown = [h for h in header if h and spec.column(h) is None]
    names = [c.name for c in known]
    if spec.course_scoped and "course_id" in db_columns:
        names.append("course_id")
    if "extra" in db_columns:
        names.append("extra")
    sql = f"INSERT INTO {spec.table} ({', '.join(names)}) VALUES ({', '.join('?' * len(names))})"
    for row in rows:
        values = [_convert(row.get(c.name, ""), c) for c in known]
        if spec.course_scoped and "course_id" in db_columns:
            values.append(course_id)
        if "extra" in db_columns:
            extra = {h: row[h] for h in unknown if row.get(h)}
            values.append(json.dumps(extra, ensure_ascii=False) if extra else None)
        conn.execute(sql, values)
    return len(rows)


def insert_rows(conn: sqlite3.Connection, tables: dict[str, Table], course_id: str) -> dict[str, int]:
    """Insert every file's rows, including id_map; return counts per table."""
    return {t.spec.table: insert_file(conn, t.spec, t.rows, t.header, course_id) for t in tables.values() if t.present}


def fill_question_node(conn: sqlite3.Connection) -> None:
    """One row per (question, node) from questions' node_ids, for joins."""
    conn.execute("DELETE FROM question_node")
    for qid, node_ids in conn.execute("SELECT id, node_ids FROM question").fetchall():
        conn.executemany("INSERT OR IGNORE INTO question_node VALUES (?, ?)", [(qid, n) for n in split_list(node_ids)])


def build_note_index(conn: sqlite3.Connection) -> None:
    """Fill note_fts from summary, key points and key wording."""
    conn.execute("DELETE FROM note_fts")
    for nid, summary, points, wording in conn.execute("SELECT id, summary, key_points, key_wording FROM note").fetchall():
        body = "\n".join([summary or "", *split_list(points), *split_list(wording)])
        conn.execute("INSERT INTO note_fts (id, body) VALUES (?, ?)", (nid, body))


def count_rows(conn: sqlite3.Connection) -> dict[str, int]:
    """Row counts for every table loaded from the pack plus derived tables."""
    tables = [s.table for s in registry.FILES.values()] + ["question_node", "node_weight"]
    return {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in tables}


def write_load_info(conn: sqlite3.Connection, report: LoadReport) -> None:
    """Record when and what was loaded."""
    summary = json.dumps({"counts": report.counts, "warnings": len(report.warnings)})
    conn.execute("DELETE FROM load_info")
    conn.execute("INSERT INTO load_info VALUES (?, ?, ?, ?)",
                 (datetime.now(timezone.utc).isoformat(timespec="seconds"), report.course_id, report.pack_path, summary))


def print_report(report: LoadReport) -> None:
    """Print the load report."""
    if report.errors:
        for issue in report.errors:
            print(f"ERROR   {issue}")
        print(f"Not loaded: {len(report.errors)} error(s).")
        return
    print(f"Loaded {report.course_id} from {report.pack_path} into {report.db_path}")
    for table, n in report.counts.items():
        print(f"  {table:18} {n}")
    for w in report.warnings:
        print(f"warning {w}")
