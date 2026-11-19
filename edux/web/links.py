"""Map links from get_my_progress (decision 0026): a way into the student's own pages that never puts their key in a chat.

The chatbot provider keeps chats, so a tool result must not carry the student's key. Instead get_my_progress issues a
link token: 32 random bytes, stored only as its SHA-256 with the student and an expiry (web.link_minutes). The page
swaps it, once, for a session token (web.session_minutes) that it sends as its bearer. A session opens the same student
API a key does, which is read-only, and never the MCP endpoint or the teacher API. A link that has been used (a chat
app's preview may load it first) or has expired is refused, and the page asks the student to get a new one."""

from __future__ import annotations

import os
import secrets
from datetime import timedelta

from edux import learner

TOKEN_BYTES = 32


def public_base_url() -> str:
    """EDUX_PUBLIC_BASE_URL if set and not empty, else web.public_base_url; without a trailing slash. "" means none."""
    value = os.environ.get("EDUX_PUBLIC_BASE_URL", "").strip() or learner._settings().web.public_base_url
    return value.strip().rstrip("/")


def _later(minutes: int) -> str:
    return (learner.parse_ts(learner.now_iso()) + timedelta(minutes=minutes)).isoformat(timespec="seconds")


def _store(student_id: str, kind: str, minutes: int) -> str:
    """A new token of this kind for the student; only its hash is stored. Expired rows are cleared on the way."""
    token = secrets.token_urlsafe(TOKEN_BYTES)
    conn = learner._conn()
    with conn:
        conn.execute("DELETE FROM web_link WHERE expires_at <= ?", (learner.now_iso(),))
        conn.execute(
            "INSERT INTO web_link (token_hash, student_id, kind, expires_at) VALUES (?, ?, ?, ?)",
            (learner.key_hash(token), student_id, kind, _later(minutes)),
        )
    return token


def issue_link(student_id: str) -> str:
    """A single-use link token for the student, valid for web.link_minutes."""
    return _store(student_id, "link", learner._settings().web.link_minutes)


def map_url(student_id: str) -> str | None:
    """{public_base_url}/me#link=<token>, or None when no base URL is set (then no token is issued)."""
    base = public_base_url()
    return f"{base}/me#link={issue_link(student_id)}" if base else None


def exchange(token: str | None) -> dict | None:
    """Swap a link token for a session: {"session", "expires_in"} (seconds), or None if the token is unknown, used or
    expired. The token is marked used in the same statement that checks it, so it can be swapped only once."""
    if not token:
        return None
    conn = learner._conn()
    with conn:
        row = conn.execute(
            "UPDATE web_link SET used_at = ? WHERE token_hash = ? AND kind = 'link' AND used_at IS NULL AND expires_at > ? "
            "RETURNING student_id",
            (learner.now_iso(), learner.key_hash(token), learner.now_iso()),
        ).fetchone()
    if row is None:
        return None
    minutes = learner._settings().web.session_minutes
    return {"session": _store(row["student_id"], "session", minutes), "expires_in": minutes * 60}


def student_by_session(token: str | None) -> dict | None:
    """The student a live session token belongs to, or None."""
    if not token:
        return None
    row = (
        learner._conn()
        .execute(
            "SELECT student_id FROM web_link WHERE token_hash = ? AND kind = 'session' AND expires_at > ?",
            (learner.key_hash(token), learner.now_iso()),
        )
        .fetchone()
    )
    return learner.get_student(row["student_id"]) if row else None


def demo_teacher_on() -> bool:
    """web.demo_teacher (off by default), unless EDUX_DEMO_TEACHER is set: 1 turns it on, 0 off (decision 0030)."""
    switch = os.environ.get("EDUX_DEMO_TEACHER", "").strip()
    return switch == "1" if switch in ("0", "1") else learner._settings().web.demo_teacher


def teacher_session(teacher_id: str) -> dict:
    """A short read-only session for a teacher (the demo teacher's sign-in): {"session", "expires_in"}. It is stored like
    a map-link session, hashed, in the same table; the teacher id (t-...) can never match a student id."""
    minutes = learner._settings().web.session_minutes
    return {"session": _store(teacher_id, "session", minutes), "expires_in": minutes * 60}


def teacher_by_session(token: str | None) -> dict | None:
    """The teacher a live session token belongs to, marked read_only, or None."""
    from edux import teachers

    if not token:
        return None
    row = (
        learner._conn()
        .execute(
            "SELECT student_id FROM web_link WHERE token_hash = ? AND kind = 'session' AND expires_at > ?",
            (learner.key_hash(token), learner.now_iso()),
        )
        .fetchone()
    )
    found = teachers.get_teacher(row["student_id"]) if row else None
    return found | {"read_only": True} if found and not found.get("left_on") else None
