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
from datetime import datetime, timedelta, timezone
from pathlib import Path

from edux import db, graph
from ingest.registry import split_list as split
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


# --- state -----------------------------------------------------------------


def difficulty_signal(part_id: str) -> float | None:
    """Cross-student difficulty (0–1) of a part, e.g. from first-attempt failure rates. None until checks exist."""
    return None


def difficulty(part_id: str) -> float:
    """A part's difficulty: the teacher's value (inherited from its concept or topic) or the default,
    blended with the cross-student estimate at share difficulty.w_cross once there is one."""
    d = _settings().difficulty
    base = graph.difficulty(part_id)
    base = d.default if base is None else base
    cross = difficulty_signal(part_id)
    return base if cross is None else (1 - d.w_cross) * base + d.w_cross * cross


def initial_state(part_id: str) -> tuple[float, float]:
    """Starting (p_known, half_life_days) for a part the student hasn't met, shifted by its difficulty."""
    s = _settings()
    shift = max(-1.0, min(1.0, (difficulty(part_id) - s.difficulty.default) / 0.5))
    prior = min(0.99, max(0.01, s.bkt.prior - s.difficulty.prior_shift * shift))
    half_life = max(s.decay.min_half_life_days, s.decay.base_half_life_days * (1 - s.difficulty.half_life_shift * shift))
    return prior, half_life


def p_now(p_known: float, half_life_days: float, since: datetime | str | None, now: datetime | str | None = None) -> float:
    """p_known decayed by the time from since (the forgetting clock's start) to now.

    since is None until the student first gets the part right: with nothing learnt yet there is nothing to forget.
    """
    if since is None:
        return p_known
    days = max(0.0, (parse_ts(now or now_iso()) - parse_ts(since)).total_seconds() / 86400)
    return p_known * 0.5 ** (days / half_life_days)


def _load_state(conn: sqlite3.Connection, student_id: str, part_id: str, ts: str) -> dict:
    row = conn.execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    if row:
        return dict(row)
    prior, half_life = initial_state(part_id)
    return {"student_id": student_id, "part_id": part_id, "p_known": prior, "half_life_days": half_life,
            "last_seen": ts, "n_evidence": 0, "offload_left": 0, "was_secure": 0,
            "clock_start": None, "last_correct": None, "exchanges_since_evidence": 0}


def _save_state(conn: sqlite3.Connection, state: dict) -> None:
    state["was_secure"] = int(state["was_secure"] or _p_at(state, state["last_seen"]) >= _settings().levels.secure)
    columns = list(state)
    conn.execute(f"INSERT OR REPLACE INTO part_state ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})",
                 [state[c] for c in columns])


def _p_at(state: dict, ts: str) -> float:
    return p_now(state["p_known"], state["half_life_days"], state["clock_start"], ts)


def _queue_review(conn: sqlite3.Connection, student_id: str, part_id: str, due: datetime, reason: str,
                  replace: bool = False) -> None:
    """Queue a review; unless replace, an existing earlier due date is kept."""
    due_iso = due.isoformat(timespec="seconds")
    row = conn.execute("SELECT due FROM review_queue WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    if row and not replace and parse_ts(row["due"]) <= due:
        return
    conn.execute("INSERT OR REPLACE INTO review_queue (student_id, part_id, due, reason) VALUES (?, ?, ?, ?)",
                 (student_id, part_id, due_iso, reason))


def _tagged_parts(node_ids: list[str]) -> dict[str, float]:
    """Parts an event is about, each with its strength: 1 for a part, concept_tag_strength for a concept or topic tag."""
    strength = _settings().nudges.concept_tag_strength
    parts: dict[str, float] = {}
    for node_id in node_ids:
        node = graph.get_node(node_id)
        if node is None:
            continue
        if node["level"] == "part":
            parts[node["id"]] = 1.0
        else:
            for part in graph.parts_of(node["id"]):
                parts[part] = max(parts.get(part, 0.0), strength)
    return parts


def apply_exchange(event: dict) -> None:
    """Apply one exchange event: nudges, offloading, misconception activation, untested reviews, last_seen.

    An exchange is not evidence: it nudges p_known a little by its labels and moves the forgetting
    clock only decay.seen_refresh of the way to now. Old ids are resolved through id_map.
    """
    s, conn = _settings(), _conn()
    student_id, ts = event["student_id"], event["ts"]
    t = parse_ts(ts)
    multiplier = s.nudges.depth[event["question_depth"]] * s.nudges.engagement[event["engagement"]]
    offloaded = bool(event["offloading"]) or event.get("choice_taken") == "just_show_me"
    support = event.get("support_given")

    for part, strength in _tagged_parts(split(event["node_ids"])).items():
        state = _load_state(conn, student_id, part, ts)
        odds = state["p_known"] / (1 - state["p_known"])
        odds *= 1 + (multiplier - 1) * strength
        state["p_known"] = odds / (1 + odds)
        if state["clock_start"]:
            clock = parse_ts(state["clock_start"])
            clock += (t - clock) * s.decay.seen_refresh * strength
            state["clock_start"] = clock.isoformat(timespec="seconds")
        state["last_seen"] = ts
        state["exchanges_since_evidence"] += 1
        if offloaded:
            state["offload_left"] = s.offloading.checks_discounted
            _queue_review(conn, student_id, part, t + timedelta(days=s.scheduling.just_show_me_gap_days), "just_show_me")
        if support and support != "none":
            conn.execute("INSERT INTO approach_record (student_id, part_id, approach, ts) VALUES (?, ?, ?, ?)",
                         (student_id, part, support, ts))
        if state["exchanges_since_evidence"] >= s.scheduling.untested_after and _p_at(state, ts) < s.scheduling.untested_below:
            _queue_review(conn, student_id, part, t, "untested")
        _save_state(conn, state)

    for misconception_id in split(event.get("misconception_ids")):
        misconception_id = graph.canonical(misconception_id)
        if conn.execute("SELECT 1 FROM content.misconception WHERE id = ? AND status != 'rejected'", (misconception_id,)).fetchone():
            conn.execute("INSERT OR REPLACE INTO student_misconception (student_id, misconception_id, active, last_seen) "
                         "VALUES (?, ?, 1, ?)", (student_id, misconception_id, ts))


def apply_evidence(student_id: str, part_id: str, evidence_type: str, correct: bool, ts: datetime | None = None) -> None:
    """BKT update, half-life change, prerequisite propagation, misconception clearing and review scheduling."""
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
