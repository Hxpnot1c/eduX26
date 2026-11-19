"""Teachers: who may open the teacher page, and which classes they may see (step 09, decision 0023).

A teacher has a key, shown once and stored only as its SHA-256 (the same scheme as a student's). A key opens the web
API as a teacher and never the MCP endpoint, and a student key never opens the teacher API. A teacher sees only the
classes assigned to them; every teacher query is scoped by `classes_of`."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from edux import learner

PREFIX = "t"  # teacher ids start with t-, student ids with s-


def _conn():
    return learner._conn()


def add_teacher(name: str) -> dict:
    """Create a teacher; returns {"id", "key"}. The key is shown once, here: only its hash is stored."""
    name = name.strip()
    if not name:
        raise ValueError("a teacher needs a name")
    teacher_id, key = f"{PREFIX}-{secrets.token_hex(4)}", secrets.token_urlsafe(16)
    conn = _conn()
    with conn:
        conn.execute(
            "INSERT INTO teacher (id, name, key_hash, created_on) VALUES (?, ?, ?, ?)",
            (teacher_id, name, learner.key_hash(key), learner.now_iso()[:10]),
        )
    return {"id": teacher_id, "key": key}


def teacher_by_key(key: str | None) -> dict | None:
    """The teacher with this key who has not left, or None."""
    if not key:
        return None
    row = (
        _conn()
        .execute("SELECT id, name, created_on FROM teacher WHERE key_hash = ? AND left_on IS NULL", (learner.key_hash(key),))
        .fetchone()
    )
    return dict(row) if row else None


def get_teacher(teacher_id: str) -> dict | None:
    row = _conn().execute("SELECT id, name, created_on, left_on FROM teacher WHERE id = ?", (teacher_id,)).fetchone()
    return dict(row) if row else None


def assign_class(teacher_id: str, class_id: str) -> None:
    """Let the teacher see the class. Raises ValueError for an unknown teacher or class."""
    conn = _conn()
    if get_teacher(teacher_id) is None:
        raise ValueError(f"unknown teacher {teacher_id!r}")
    if conn.execute("SELECT 1 FROM class WHERE id = ?", (class_id,)).fetchone() is None:
        raise ValueError(f"unknown class {class_id!r}")
    with conn:
        conn.execute("INSERT OR IGNORE INTO teacher_class (teacher_id, class_id) VALUES (?, ?)", (teacher_id, class_id))


def classes_of(teacher_id: str) -> list[dict]:
    """The classes this teacher may see: {id, name}, in name order."""
    rows = _conn().execute(
        "SELECT c.id, c.name FROM teacher_class t JOIN class c ON c.id = t.class_id WHERE t.teacher_id = ? ORDER BY c.name, c.id",
        (teacher_id,),
    )
    return [dict(r) for r in rows]


def may_see(teacher_id: str, class_id: str) -> bool:
    return (
        _conn().execute("SELECT 1 FROM teacher_class WHERE teacher_id = ? AND class_id = ?", (teacher_id, class_id)).fetchone() is not None
    )


def leave_teacher(teacher_id: str, on: str | None = None) -> None:
    """Mark the teacher as having left: the key stops working now. Raises ValueError for an unknown teacher."""
    conn = _conn()
    with conn:
        if conn.execute("UPDATE teacher SET left_on = ? WHERE id = ?", ((on or learner.now_iso())[:10], teacher_id)).rowcount == 0:
            raise ValueError(f"unknown teacher {teacher_id!r}")


def delete_teacher(teacher_id: str) -> None:
    """Delete the teacher and their class assignments. Raises ValueError for an unknown teacher."""
    conn = _conn()
    if get_teacher(teacher_id) is None:
        raise ValueError(f"unknown teacher {teacher_id!r}")
    with conn:
        conn.execute("DELETE FROM teacher_class WHERE teacher_id = ?", (teacher_id,))
        conn.execute("DELETE FROM teacher WHERE id = ?", (teacher_id,))


def purge_left_teachers(today: datetime | None = None) -> int:
    """Delete teachers who left more than retention.after_leaving_days ago. Returns how many."""
    days = learner._settings().retention.after_leaving_days
    cutoff = ((today or datetime.now(timezone.utc)) - timedelta(days=days)).date().isoformat()
    ids = [r["id"] for r in _conn().execute("SELECT id FROM teacher WHERE left_on IS NOT NULL AND left_on < ?", (cutoff,))]
    for teacher_id in ids:
        delete_teacher(teacher_id)
    return len(ids)
