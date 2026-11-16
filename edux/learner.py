"""Learner model: append-only events, scoring rules and state rebuilt from events.

part_state, student_misconception, approach_record and review_queue are derived:
rebuild_state replays a student's events through the current rules in settings.toml.
Every rule runs at the event's own timestamp, so replaying gives the same state.
"""

from __future__ import annotations

import functools
import os
import queue
import re
import secrets
import sqlite3
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from edux import db, graph
from edux.settings import ContextConfig, Settings, load_context, load_settings, protocol_label, settings_hash

SUPPORT_GIVEN = ("worked_example", "hint", "explain_back", "none")
CHOICE_TAKEN = ("try_first", "hint", "just_show_me", "none")

_local = threading.local()
_paths: dict[str, Path | None] = {"learner": None, "content": None}


# --- setup -----------------------------------------------------------------


@functools.cache
def _settings() -> Settings:
    return load_settings()


@functools.cache
def _context() -> ContextConfig:
    return load_context()


def use_database(learner_path: Path | None, content_path: Path | None = None) -> None:
    """Point the learner model (and graph lookups) at specific databases; None means the defaults."""
    _paths["learner"], _paths["content"] = learner_path, content_path
    _local.__dict__.clear()
    graph.use_database(content_path)


def _conn() -> sqlite3.Connection:
    """This thread's connection to learner.db, with content.db attached."""
    key = (_paths["learner"], _paths["content"])
    if getattr(_local, "key", None) != key:
        _local.conn = db.connect_learner(_paths["learner"], content_path=_paths["content"])
        _local.key = key
    return _local.conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_ts(ts: str | datetime) -> datetime:
    """An aware datetime from an ISO string or datetime (naive values are taken as UTC)."""
    value = ts if isinstance(ts, datetime) else datetime.fromisoformat(ts)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


# --- students --------------------------------------------------------------


def add_student(display_name: str, course_id: str, profile: str | None = None) -> dict:
    """Create a student with a secret key and an empty profile; returns {"id", "key"}."""
    conn = _conn()
    if not conn.execute("SELECT 1 FROM content.course WHERE id = ?", (course_id,)).fetchone():
        raise ValueError(f"unknown course {course_id!r}; load its pack first")
    if profile is not None and profile not in _context().profiles:
        raise ValueError(f"unknown context profile {profile!r}")
    slug = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-") or "student"
    student_id, key = f"{slug}-{secrets.token_hex(2)}", secrets.token_urlsafe(16)
    with conn:
        conn.execute("INSERT INTO student (id, key, display_name, course_id, profile, created) VALUES (?, ?, ?, ?, ?, ?)",
                     (student_id, key, display_name, course_id, profile, now_iso()))
        conn.execute("INSERT INTO student_profile (student_id) VALUES (?)", (student_id,))
    return {"id": student_id, "key": key}


def get_student(student_id: str) -> dict | None:
    row = _conn().execute("SELECT * FROM student WHERE id = ?", (student_id,)).fetchone()
    return dict(row) if row else None


def student_by_key(key: str) -> dict | None:
    row = _conn().execute("SELECT * FROM student WHERE key = ?", (key,)).fetchone()
    return dict(row) if row else None


def profile_of(student: dict) -> str:
    """The student's context profile, or the default from context.toml."""
    return student.get("profile") or _context().default_profile


# --- events ----------------------------------------------------------------


def record_exchange(
    student_id: str,
    node_ids: list[str],
    question_depth: str,
    engagement: str,
    offloading: bool = False,
    support_given: str | None = None,
    choice_taken: str | None = None,
    misconception_ids: list[str] | None = None,
    conflict_flagged: bool = False,
    prompt_text: str | None = None,
    client: str | None = None,
    ts: str | None = None,
    apply: str = "background",
) -> int:
    """Write an exchange event with protocol and settings_hash, then apply it; return the event id.

    apply is "background" (queue for the worker thread), "now" (apply before returning) or "none".
    prompt_text is stored only when STORE_PROMPTS=1.
    """
    s = _settings()
    student = get_student(student_id)
    if student is None:
        raise ValueError(f"unknown student {student_id!r}")
    if not node_ids:
        raise ValueError("node_ids is empty")
    if question_depth not in s.nudges.depth:
        raise ValueError(f"question_depth must be one of {', '.join(s.nudges.depth)}")
    if engagement not in s.nudges.engagement:
        raise ValueError(f"engagement must be one of {', '.join(s.nudges.engagement)}")
    if support_given is not None and support_given not in SUPPORT_GIVEN:
        raise ValueError(f"support_given must be one of {', '.join(SUPPORT_GIVEN)}")
    if choice_taken is not None and choice_taken not in CHOICE_TAKEN:
        raise ValueError(f"choice_taken must be one of {', '.join(CHOICE_TAKEN)}")
    store_prompt = os.environ.get("STORE_PROMPTS", "0") == "1"
    conn = _conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO exchange_log (student_id, ts, client, node_ids, question_depth, engagement, offloading,
                 support_given, choice_taken, misconception_ids, conflict_flagged, protocol, settings_hash, prompt_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, parse_ts(ts).isoformat(timespec="seconds") if ts else now_iso(), client, ";".join(node_ids),
             question_depth, engagement, int(offloading), support_given, choice_taken, ";".join(misconception_ids or []),
             int(conflict_flagged), protocol_label(s, profile_of(student)), settings_hash(),
             prompt_text if store_prompt else None),
        )
    event_id = cur.lastrowid
    if apply == "now":
        apply_event(event_id)
    elif apply == "background":
        start_worker()
        _queue.put(event_id)
    return event_id


def get_event(event_id: int) -> dict:
    row = _conn().execute("SELECT * FROM exchange_log WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise ValueError(f"no exchange event {event_id}")
    return dict(row)


def apply_event(event_id: int) -> None:
    """Apply one stored exchange event to the derived state, in its own transaction."""
    conn = _conn()
    with conn:
        apply_exchange(get_event(event_id))


def apply_exchange(event: dict) -> None:
    """Apply one exchange event: nudges, offloading, misconception activation, untested reviews, last_seen."""
    raise NotImplementedError


def apply_evidence(student_id: str, part_id: str, evidence_type: str, correct: bool, ts: datetime | None = None) -> None:
    """BKT update, half-life change, prerequisite propagation, misconception clearing and review scheduling."""
    raise NotImplementedError


def p_now(p_known: float, half_life_days: float, last_seen: datetime, now: datetime | None = None) -> float:
    """Decayed p_known at read time."""
    raise NotImplementedError


def level(p: float) -> str:
    """new, developing or secure from the thresholds in settings.toml."""
    raise NotImplementedError


def rollup(student_id: str, node_id: str) -> float:
    """Importance-weighted mean p_now of the parts under a node."""
    raise NotImplementedError


def due_reviews(student_id: str, limit: int) -> list[dict]:
    """Parts due for review, ordered by importance."""
    raise NotImplementedError


def candidates(student_id: str, limit: int) -> list[dict]:
    """Parts to teach next: p_now in the queue band and prerequisites at least developing."""
    raise NotImplementedError


def support_level(p: float) -> str:
    """worked_example, hint or explain_back from p_now."""
    raise NotImplementedError


def anchor(student_id: str, part_id: str) -> dict | None:
    """A secure analogous part with its edge note."""
    raise NotImplementedError


def approaches(student_id: str, part_id: str) -> list[dict]:
    """Past support approaches on the part and whether the next check went well."""
    raise NotImplementedError


def misconception_link_signal(from_id: str, to_id: str) -> float:
    """Cross-student strength (0–1) of a link: how often a misconception about one end makes students fail the other.

    Combined with edge_weight.weight at read time using link_weight.w_misconception. Returns 0 until
    checks record failures with misconception ids (see steps/later.md).
    """
    return 0.0


def rebuild_state(student_id: str) -> None:
    """Delete the student's derived rows and replay their events in ts order."""
    raise NotImplementedError


def rebuild_all() -> None:
    """rebuild_state for every student."""
    raise NotImplementedError


# --- background worker -----------------------------------------------------

_queue: queue.Queue[int] = queue.Queue()
_worker: threading.Thread | None = None
_worker_lock = threading.Lock()


def _work() -> None:
    while True:
        event_id = _queue.get()
        try:
            apply_event(event_id)
        except Exception:
            traceback.print_exc()
        finally:
            _queue.task_done()


def start_worker() -> None:
    """Start the background thread that applies queued events (once per process)."""
    global _worker
    with _worker_lock:
        if _worker is None or not _worker.is_alive():
            _worker = threading.Thread(target=_work, name="learner-worker", daemon=True)
            _worker.start()


def wait_for_worker() -> None:
    """Block until every queued event has been applied."""
    _queue.join()
