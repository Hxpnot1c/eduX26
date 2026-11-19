"""Learner model: append-only events, scoring rules and state rebuilt from events.

part_state, student_misconception, approach_record and review_queue are derived:
rebuild_state replays a student's events (exchange_log and evidence_log) through the current rules in settings.toml.
Every rule runs at the event's own timestamp, so replaying gives the same state.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import os
import queue
import re
import secrets
import sqlite3
import threading
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from edux import db, graph
from ingest.registry import split_list as split
from edux.settings import (ContextConfig, Settings, load_context, load_settings, personal_learn_rate, protocol_label,
                           settings_hash)

SUPPORT_GIVEN = ("worked_example", "hint", "explain_back", "none")
CHOICE_TAKEN = ("try_first", "hint", "just_show_me", "skip_point", "quiz", "extend", "stop", "none")   # skip_point: "I know this" (step 05d); quiz, extend, stop: a pick from offer_choice
# What a student's answer can be to, as sent by the chatbot; each is also a key of [bkt.evidence].
# "mcq" is any server-built multiple-choice question (step 05d), scored from the letter picked.
ANSWER_TYPES = ("prequestion", "mcq", "explain_back", "review", "extend", "past_question", "ail_task", "ail_unprompted")
OPEN_ANSWERS = ("explain_back", "extend", "past_question", "link")   # answers the student writes, not picks
LITERACY_ANSWERS = ("ail_task", "ail_unprompted")   # a verify task's answer, or checking a claim unprompted (step 05e)
AIL_ASK, AIL_VERIFY = "ail_ask", "ail_verify"       # the AI-literacy skills Ask and Verify (ingest/ai_literacy/)
AIL_HOW = "ail_how_ai_works"                        # the concept holding the how-AI-works parts
REQUEST_TYPES = ("concept", "research", "homework", "other")   # step 05e
QUESTION_FEATURES = ("concept", "context", "asks_sources", "asks_reasoning")   # research questions only (step 05e)


class LostQuestion(ValueError):
    """An mcq answer arrived but the letter -> option map for that part is gone (a restart, a reset): nothing
    can be scored, so nothing is recorded and the question is asked again."""

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


def key_hash(key: str) -> str:
    """What is stored for a student's key: its SHA-256. The key is a random 128-bit secret, so a plain hash is enough;
    only the student's link holds the key."""
    return hashlib.sha256(key.encode()).hexdigest()


def add_student(display_name: str, course_id: str, profile: str | None = None, student_id: str | None = None,
                key: str | None = None) -> dict:
    """Create a student with a secret key and an empty profile; returns {"id", "key"}. The key is shown once, here:
    only its hash is stored. The id is opaque (s-<random>), never made from the name; student_id fixes it (demo
    students) and key fixes the key (a demo reset keeps keys, so connector URLs keep working). The display name, if
    given, is stored in the student row and nowhere else."""
    conn = _conn()
    if not conn.execute("SELECT 1 FROM content.course WHERE id = ?", (course_id,)).fetchone():
        raise ValueError(f"unknown course {course_id!r}; load its pack first")
    if profile is not None and profile not in _context().profiles:
        raise ValueError(f"unknown context profile {profile!r}")
    student_id, key = student_id or f"s-{secrets.token_hex(4)}", key or secrets.token_urlsafe(16)
    with conn:
        conn.execute("INSERT INTO student (id, key_hash, display_name, course_id, profile, created) VALUES (?, ?, ?, ?, ?, ?)",
                     (student_id, key_hash(key), display_name, course_id, profile, now_iso()))
        conn.execute("INSERT INTO student_profile (student_id) VALUES (?)", (student_id,))
    return {"id": student_id, "key": key}


def get_student(student_id: str) -> dict | None:
    row = _conn().execute("SELECT * FROM student WHERE id = ?", (student_id,)).fetchone()
    return {k: v for k, v in dict(row).items() if k not in ("key", "key_hash")} if row else None


# --- retention, export and deletion (step 05x) ---------------------------------------------------------------


def _student_tables(conn: sqlite3.Connection) -> list[str]:
    """Every table in learner.db that holds rows about a student (a student_id column), found rather than listed, so
    a table added later is covered by delete_student and export_student without anyone remembering to add it."""
    names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
                                       "AND name != 'student' ORDER BY name")]
    return [n for n in names if any(c["name"] == "student_id" for c in conn.execute(f"PRAGMA table_info({n})"))]


def delete_student(student_id: str) -> dict[str, int]:
    """Delete every row about the student, in every table, including the call log and the student row itself. Returns
    the rows deleted per table. Raises ValueError for an unknown student."""
    conn = _conn()
    if conn.execute("SELECT 1 FROM student WHERE id = ?", (student_id,)).fetchone() is None:
        raise ValueError(f"unknown student {student_id!r}")
    counts: dict[str, int] = {}
    with conn:
        for table in _student_tables(conn):
            counts[table] = conn.execute(f"DELETE FROM {table} WHERE student_id = ?", (student_id,)).rowcount
        counts["student"] = conn.execute("DELETE FROM student WHERE id = ?", (student_id,)).rowcount
    return counts


def export_student(student_id: str) -> dict:
    """Everything stored about the student, as plain data: the student row (never the key or its hash) and every row
    in every table that holds rows about a student. Raises ValueError for an unknown student."""
    conn = _conn()
    student = get_student(student_id)
    if student is None:
        raise ValueError(f"unknown student {student_id!r}")
    return {"student": student, "exported": now_iso(),
            "tables": {t: [dict(r) for r in conn.execute(f"SELECT * FROM {t} WHERE student_id = ? ORDER BY rowid", (student_id,))]
                       for t in _student_tables(conn)}}


def leave_student(student_id: str, on: str | None = None) -> None:
    """Mark the student as having left (today, or on a given date): all their data is deleted retention.after_leaving_days
    later by purge. Raises ValueError for an unknown student."""
    conn = _conn()
    with conn:
        if conn.execute("UPDATE student SET left_on = ? WHERE id = ?", ((on or now_iso())[:10], student_id)).rowcount == 0:
            raise ValueError(f"unknown student {student_id!r}")


def purge(now: str | datetime | None = None) -> dict:
    """Apply the retention settings: delete call-log rows older than retention.call_log_days, and every student who
    left more than retention.after_leaving_days ago. Returns {"call_log": rows deleted, "students": [ids deleted]}."""
    r, conn = _settings().retention, _conn()
    at = parse_ts(now) if now else parse_ts(now_iso())
    cutoff = (at - timedelta(days=r.call_log_days)).isoformat(timespec="seconds")
    with conn:
        removed = conn.execute("DELETE FROM call_log WHERE ts < ?", (cutoff,)).rowcount
    left_before = (at - timedelta(days=r.after_leaving_days)).date().isoformat()
    gone = [row["id"] for row in conn.execute("SELECT id FROM student WHERE left_on IS NOT NULL AND left_on < ? ORDER BY id", (left_before,))]
    for student_id in gone:
        delete_student(student_id)
    return {"call_log": removed, "students": gone}


def student_by_key(key: str) -> dict | None:
    """The student with this key, found by its hash. A student from before step 05x still has a plaintext key: it is
    matched once and replaced with its hash."""
    conn = _conn()
    row = conn.execute("SELECT * FROM student WHERE key_hash = ?", (key_hash(key),)).fetchone()
    if row is None:
        row = conn.execute("SELECT * FROM student WHERE key = ?", (key,)).fetchone()
        if row is not None:
            with conn:
                conn.execute("UPDATE student SET key_hash = ?, key = NULL WHERE id = ?", (key_hash(key), row["id"]))
    return {k: v for k, v in dict(row).items() if k not in ("key", "key_hash")} if row else None


def set_profile(student_id: str, profile: str | None) -> None:
    """Switch a student's context profile (None: back to the default in context.toml)."""
    if get_student(student_id) is None:
        raise ValueError(f"unknown student {student_id!r}")
    if profile is not None and profile not in _context().profiles:
        raise ValueError(f"unknown context profile {profile!r}; one of {', '.join(_context().profiles)}")
    conn = _conn()
    with conn:
        conn.execute("UPDATE student SET profile = ? WHERE id = ?", (profile, student_id))


def profile_of(student: dict) -> str:
    """The student's context profile, or the default from context.toml."""
    return student.get("profile") or _context().default_profile


# --- events ----------------------------------------------------------------


def _event_ts(ts: str | datetime | None) -> str:
    """An event timestamp: ISO, UTC, to the second (so stored timestamps compare correctly as text)."""
    return parse_ts(ts).astimezone(timezone.utc).isoformat(timespec="seconds") if ts else now_iso()


def _evidence_rows(evidence: list[dict]) -> list[tuple[str, str, float, list[str], str | None, int | None]]:
    """Validate evidence items and expand concept ids to their parts: (part_id, type, score, misconception_ids,
    point_id, n_options). point_id is the one point a multiple-choice question asked and n_options how many options
    it showed; both are kept only on a part's own item."""
    s = _settings()
    rows = []
    for item in evidence:
        node = graph.get_node(item.get("part_id") or "")
        if node is None:
            raise ValueError(f"evidence: unknown part {item.get('part_id')!r}")
        if item.get("type") not in s.bkt.evidence:
            raise ValueError(f"evidence type must be one of {', '.join(s.bkt.evidence)}")
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            raise ValueError(f"evidence score must be a number from 0 to 1, got {item.get('score')!r}") from None
        if not 0 <= score <= 1:
            raise ValueError(f"evidence score must be from 0 to 1, got {score}")
        parts = [node["id"]] if node["level"] == "part" else graph.parts_of(node["id"])
        if not parts:
            raise ValueError(f"evidence: {node['id']!r} has no parts")
        point_id = item.get("point_id") if node["level"] == "part" else None
        n_options = item.get("n_options") if node["level"] == "part" else None
        if n_options is not None and (isinstance(n_options, bool) or not isinstance(n_options, int) or n_options < 2):
            raise ValueError(f"evidence n_options must be a whole number of at least 2, got {n_options!r}")
        rows += [(part, item["type"], score, list(item.get("misconception_ids") or []), point_id, n_options)
                 for part in parts]
    return rows


def score_answer(answer: dict, mcq: dict | None = None) -> dict:
    """Turn a chatbot's answer report into an evidence item {part_id, type, score, misconception_ids}.

    The chatbot ticks; the server scores. An mcq answer is scored from answer.choice against mcq, the letter ->
    option map stored with the last plan (step 05d): 1 for the correct option, else 0, with the picked
    misconception first in misconception_ids (a chatbot-written extra option activates nothing). Its evidence
    type is prequestion for an intuition question, ail_how for a how-AI-works check (step 05e), otherwise mcq_check, and the item also carries purpose,
    correct, picked, point_id and correct_option (its text). A prequestion scores 1 if correct, else 0, and its picked misconception goes
    into misconception_ids. Every other type scores len(points_met) / len(points), against graph.score_points
    for the part; points_met may be letters from score_next, full point ids or a mix, and the resolved point
    ids are returned as points_met. Raises LostQuestion when an mcq answer has no map for its part, and
    ValueError on an unknown part, type, letter, point or misconception.
    """
    node = graph.get_node(answer.get("part_id") or "")
    if node is None or node["level"] != "part":
        raise ValueError(f"answer.part_id: {answer.get('part_id')!r} is not a part")
    part_id, kind = node["id"], answer.get("type")
    if kind not in ANSWER_TYPES:
        raise ValueError(f"answer.type must be one of {', '.join(ANSWER_TYPES)}")
    known = {m["id"] for m in graph.misconceptions_for([part_id])}
    misconception_ids = [graph.canonical(m) for m in answer.get("misconception_ids") or []]
    for m in misconception_ids:
        if graph.get_misconception(m) is None:
            raise ValueError(f"answer.misconception_ids: unknown misconception {m!r}")
    if kind == "mcq":
        letter = str(answer.get("choice") or "").strip().upper()
        if not letter:
            raise ValueError("answer.choice (the letter picked, e.g. B) is required for an mcq answer")
        if not mcq or mcq.get("part_id") != part_id:
            raise LostQuestion(f"no multiple-choice question on {part_id} is waiting for an answer")
        option = mcq["options"].get(letter)
        if option is None:
            raise ValueError(f"answer.choice: {letter!r} is not an option; use one of {', '.join(sorted(mcq['options']))}")
        picked = option["id"]
        correct = picked == "correct"
        if not correct and picked != "extra":
            misconception_ids = [picked] + [m for m in misconception_ids if m != picked]
        kind = {"intuition": "prequestion", "how_ai_works": "ail_how"}.get(mcq["purpose"], "mcq_check")
        return {"part_id": part_id, "type": kind,
                "score": 1.0 if correct else 0.0, "misconception_ids": misconception_ids, "purpose": mcq["purpose"],
                "correct": correct, "picked": picked, "point_id": mcq.get("point_id"), "n_options": len(mcq["options"]),
                "correct_option": next((o["text"] for o in mcq["options"].values() if o["id"] == "correct"), "")}
    if kind in LITERACY_ANSWERS and part_id != AIL_VERIFY:
        raise ValueError(f"answer.type {kind} is for {AIL_VERIFY}, the verify ticks")
    if kind == "prequestion":
        if not isinstance(answer.get("correct"), bool):
            raise ValueError("answer.correct (true or false) is required for a prequestion")
        picked = answer.get("picked_misconception_id")
        if picked:
            picked = graph.canonical(picked)
            if picked not in known:
                raise ValueError(f"answer.picked_misconception_id: {picked!r} is not a misconception on {part_id}")
            misconception_ids = [picked] + [m for m in misconception_ids if m != picked]
        score = 1.0 if answer["correct"] else 0.0
    else:
        points = graph.score_points(part_id)
        if not points:
            raise ValueError(f"{part_id} has no mark points or note key points to score against")
        met, unknown = graph.resolve_points(part_id, answer.get("points_met") or [])
        if unknown:
            raise ValueError(f"answer.points_met: {', '.join(unknown)} is not a point on {part_id}; "
                             f"use the letters from score_next")
        score = len(met) / len(points)
        return {"part_id": part_id, "type": kind, "score": score, "misconception_ids": misconception_ids,
                "points_met": met}
    return {"part_id": part_id, "type": kind, "score": score, "misconception_ids": misconception_ids}


def research_turns(student_id: str, at: str | datetime | None = None) -> int:
    """How many research questions the student has asked up to at (default now), from exchange_log (step 05e)."""
    return _conn().execute("SELECT COUNT(*) FROM exchange_log WHERE student_id = ? AND request_type = 'research' AND ts <= ?",
                           (student_id, _event_ts(at))).fetchone()[0]


def verified_this_session(student_id: str, at: str | datetime | None = None) -> bool:
    """Whether the student has checked a claim (Verify evidence) in the current session."""
    state = session_state(student_id, at)
    if state is None:
        return False
    return _conn().execute("SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts >= ? AND ts <= ? LIMIT 1",
                           (student_id, AIL_VERIFY, state["session_id"], _event_ts(at))).fetchone() is not None


def question_evidence(features: list[str] | None, sources_credit: bool = False) -> dict:
    """Ask evidence for a research question (step 05e): ail_question on ail_ask, scored by the question features
    it shows out of the four. Asking for sources earns its feature only alongside checking them: without
    sources_credit (a Verify moment this session) asks_sources counts for nothing, because a chatbot asked for
    sources invites invented ones, and asking is not checking (step 05y)."""
    shown = {f for f in features or [] if f in QUESTION_FEATURES}
    if not sources_credit:
        shown.discard("asks_sources")
    return {"part_id": AIL_ASK, "type": "ail_question", "score": len(shown) / len(QUESTION_FEATURES), "misconception_ids": []}


def found_problem(kind: str = "ail_task", points_met: list[str] | None = None) -> dict:
    """Verify evidence for a reported dead or mismatched source (research fixes, 0003): finding the problem is a
    successful check, so it scores 1 whatever was ticked (a dead page has no publisher, date or figure to tick)."""
    return {"part_id": AIL_VERIFY, "type": kind, "score": 1.0, "misconception_ids": [], "points_met": list(points_met or [])}
# A report can't be told apart from a made-up one, so apply_evidence_event limits it: until the student has done one
# successful check of their own on Verify, reports reach developing at most (research fixes, 0009b).


def record_skip(student_id: str, part_id: str, ts: str | None = None) -> None:
    """An AI-literacy task or check left unanswered after its re-ask (research fixes, 0003): missing, not wrong, so
    no evidence is written; the skip is counted for the progress view."""
    conn = _conn()
    with conn:
        conn.execute("INSERT INTO literacy_skip (student_id, ts, part_id) VALUES (?, ?, ?)",
                     (student_id, _event_ts(ts), part_id))


def skips(student_id: str, part_ids: list[str], at: str | None = None) -> int:
    """How many literacy tasks or checks on part_ids the student skipped up to at (default now)."""
    marks = ", ".join("?" * len(part_ids))
    return _conn().execute(f"SELECT COUNT(*) FROM literacy_skip WHERE student_id = ? AND part_id IN ({marks}) AND ts <= ?",
                           (student_id, *part_ids, _event_ts(at))).fetchone()[0]


def _write_evidence(conn: sqlite3.Connection, student: dict, ts: str, rows: list, origin: str,
                    exchange_id: int | None = None, check_id: str | None = None) -> list[int]:
    s = _settings()
    ids = []
    for part_id, evidence_type, score, misconception_ids, point_id, n_options in rows:
        cur = conn.execute(
            """INSERT INTO evidence_log (student_id, ts, part_id, evidence_type, score, origin, exchange_id, check_id,
                 misconception_ids, point_id, n_options, protocol, settings_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student["id"], ts, part_id, evidence_type, score, origin, exchange_id, check_id, ";".join(misconception_ids),
             point_id, n_options, protocol_label(s, profile_of(student)), settings_hash()))
        ids.append(cur.lastrowid)
    return ids


def _dispatch(job: tuple[int | None, list[int]], apply: str) -> None:
    if apply == "now":
        apply_job(job)
    elif apply == "background":
        start_worker()
        _queue.put(job)


def _request_labels(request: dict) -> dict:
    """The step 05e labels as stored: features, web_access and asks_recent only on research questions."""
    kind = request.get("request_type")
    if kind is not None and kind not in REQUEST_TYPES:
        raise ValueError(f"request_type must be one of {', '.join(REQUEST_TYPES)}")
    features = list(dict.fromkeys(request.get("question_features") or []))
    unknown = [f for f in features if f not in QUESTION_FEATURES]
    if unknown:
        raise ValueError(f"question_features: {', '.join(unknown)} is not one of {', '.join(QUESTION_FEATURES)}")
    research = kind == "research"
    web = request.get("web_access")
    return {"request_type": kind, "question_features": ";".join(features) if research else "",
            "source_conflict": int(bool(request.get("source_conflict"))),
            "web_access": int(web) if research and web is not None else None,
            "asks_recent": int(research and bool(request.get("asks_recent"))),
            "pushback_changed": int(bool(request.get("pushback_changed")))}


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
    client: str | None = None,
    ts: str | None = None,
    evidence: list[dict] | None = None,
    apply: str = "background",
    request: dict | None = None,
    timing: dict | None = None,
) -> int:
    """Write an exchange event, and any evidence that came with it, then apply them; return the exchange id.

    evidence is a list of {part_id, type, score, misconception_ids?}: what the student produced in this turn,
    scored 0–1. Concept ids expand to their parts with the score unchanged. All rows share the exchange's ts.
    apply is "background" (queue for the worker thread), "now" (apply before returning) or "none".
    The student's message text is never stored. timing holds {latency_s, question_words, answer_words} (step 05s):
    seconds since their previous exchange, words in the question they are answering, and words in their message
    (a count only); the rapid-guess flag is worked out from these when the answer is applied. request holds the step 05e labels (request_type,
    question_features, source_conflict, web_access, asks_recent, pushback_changed); features, web_access and
    asks_recent are kept for research questions only, and source_conflict also sets conflict_flagged.
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
    req = _request_labels(request or {})
    conflict_flagged = conflict_flagged or bool(req["source_conflict"])
    evidence_rows = _evidence_rows(evidence or [])
    ts = _event_ts(ts)
    conn = _conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO exchange_log (student_id, ts, client, node_ids, question_depth, engagement, offloading,
                 support_given, choice_taken, misconception_ids, conflict_flagged, protocol, settings_hash,
                 request_type, question_features, source_conflict, web_access, asks_recent, pushback_changed,
                 latency_s, question_words, answer_words)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, ts, client, ";".join(node_ids), question_depth, engagement, int(offloading), support_given,
             choice_taken, ";".join(misconception_ids or []), int(conflict_flagged), protocol_label(s, profile_of(student)),
             settings_hash(), req["request_type"], req["question_features"],
             req["source_conflict"], req["web_access"], req["asks_recent"], req["pushback_changed"],
             (timing or {}).get("latency_s"), (timing or {}).get("question_words"), (timing or {}).get("answer_words")),
        )
        exchange_id = cur.lastrowid
        evidence_ids = _write_evidence(conn, student, ts, evidence_rows, "chat", exchange_id=exchange_id)
    _dispatch((exchange_id, evidence_ids), apply)
    return exchange_id


def record_evidence(
    student_id: str,
    part_id: str,
    evidence_type: str,
    score: float,
    misconception_ids: list[str] | None = None,
    ts: str | None = None,
    origin: str = "chat",
    check_id: str | None = None,
    apply: str = "background",
    point_id: str | None = None,
    n_options: int | None = None,
) -> list[int]:
    """Write evidence with no exchange (demo seeding, checks, an ignored task or check), then apply it; return the
    evidence ids (one per part). point_id is the one point a question asked, if it asked one, and n_options how
    many options a multiple-choice question showed."""
    student = get_student(student_id)
    if student is None:
        raise ValueError(f"unknown student {student_id!r}")
    if origin not in ("chat", "check"):
        raise ValueError("origin must be chat or check")
    rows = _evidence_rows([{"part_id": part_id, "type": evidence_type, "score": score, "misconception_ids": misconception_ids,
                            "point_id": point_id, "n_options": n_options}])
    conn = _conn()
    with conn:
        ids = _write_evidence(conn, student, _event_ts(ts), rows, origin, check_id=check_id)
    _dispatch((None, ids), apply)
    return ids


def get_event(event_id: int) -> dict:
    row = _conn().execute("SELECT * FROM exchange_log WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise ValueError(f"no exchange event {event_id}")
    return dict(row)


def get_evidence(evidence_id: int) -> dict:
    row = _conn().execute("SELECT * FROM evidence_log WHERE id = ?", (evidence_id,)).fetchone()
    if row is None:
        raise ValueError(f"no evidence event {evidence_id}")
    return dict(row)


def apply_job(job: tuple[int | None, list[int]]) -> None:
    """Apply an exchange (if any) and then its evidence, in one transaction."""
    exchange_id, evidence_ids = job
    conn = _conn()
    with conn:
        if exchange_id is not None:
            apply_exchange(get_event(exchange_id))
        for evidence_id in evidence_ids:
            apply_evidence_event(get_evidence(evidence_id))


# --- state -----------------------------------------------------------------


def difficulty_signal(part_id: str) -> float | None:
    """Cross-student difficulty (0–1) of a part, e.g. from first-attempt failure rates in evidence_log.
    None until there is enough evidence across students."""
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
    """The normal starting (p_known, half_life_days) for a part: bkt.prior shifted by its difficulty. It knows nothing
    about the student; starting_point adds their coverage, starting adjustment and prerequisites."""
    s = _settings()
    shift = max(-1.0, min(1.0, (difficulty(part_id) - s.difficulty.default) / 0.5))
    prior = min(0.99, max(0.01, s.bkt.prior - s.difficulty.prior_shift * shift))
    half_life = max(s.decay.min_half_life_days, s.decay.base_half_life_days * (1 - s.difficulty.half_life_shift * shift))
    return prior, half_life


# --- coverage and starting points (step 05q) -------------------------------------------------------------------


def _logit(p: float) -> float:
    p = min(0.999, max(0.001, p))
    return math.log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _day(at: str | datetime | None) -> str:
    return parse_ts(_event_ts(at)).date().isoformat()


def add_class(name: str, course_pack: str | None = None, class_id: str | None = None) -> str:
    """Create a class and return its id (c-<random> unless fixed)."""
    class_id = class_id or f"c-{secrets.token_hex(3)}"
    conn = _conn()
    with conn:
        conn.execute("INSERT INTO class (id, name, course_pack, created) VALUES (?, ?, ?, ?)", (class_id, name, course_pack, now_iso()))
    return class_id


def add_students_to_class(class_id: str, student_ids: list[str]) -> None:
    """Put students in a class (one class per student row). Raises ValueError for an unknown class or student."""
    conn = _conn()
    if conn.execute("SELECT 1 FROM class WHERE id = ?", (class_id,)).fetchone() is None:
        raise ValueError(f"unknown class {class_id!r}")
    unknown = [s for s in student_ids if conn.execute("SELECT 1 FROM student WHERE id = ?", (s,)).fetchone() is None]
    if unknown:
        raise ValueError(f"unknown student(s): {', '.join(unknown)}")
    with conn:
        for student_id in student_ids:
            conn.execute("UPDATE student SET class_id = ? WHERE id = ?", (class_id, student_id))
            conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ?", (student_id,))


def set_class_coverage(class_id: str, node_ids: list[str], taught_on: str, set_by: str = "cli") -> None:
    """Record that a class was taught these nodes (a node marks all its parts) on a date (YYYY-MM-DD)."""
    date.fromisoformat(taught_on)          # ValueError for a bad date
    conn = _conn()
    if conn.execute("SELECT 1 FROM class WHERE id = ?", (class_id,)).fetchone() is None:
        raise ValueError(f"unknown class {class_id!r}")
    with conn:
        for node_id in node_ids:
            conn.execute("INSERT OR REPLACE INTO class_coverage (class_id, node_id, taught_on, set_by) VALUES (?, ?, ?, ?)",
                         (class_id, node_id, taught_on, set_by))
        conn.execute("DELETE FROM learner_offset_cache WHERE student_id IN (SELECT id FROM student WHERE class_id = ?)", (class_id,))


def class_coverage(class_id: str) -> list[dict]:
    """A class's coverage rows, by taught date: {node_id, name, spec_ref, taught_on, set_by, parts}."""
    out = []
    for r in _conn().execute("SELECT * FROM class_coverage WHERE class_id = ? ORDER BY taught_on, node_id", (class_id,)):
        node = graph.get_node(r["node_id"]) or {}
        out.append({"node_id": r["node_id"], "name": node.get("name"), "spec_ref": node.get("spec_ref"),
                    "taught_on": r["taught_on"], "set_by": r["set_by"], "parts": len(graph.parts_of(r["node_id"]))})
    return out


def student_class(student_id: str) -> str | None:
    row = _conn().execute("SELECT class_id FROM student WHERE id = ?", (student_id,)).fetchone()
    return row["class_id"] if row else None


def covered_since(student_id: str, part_id: str, at: str | datetime | None = None) -> str | None:
    """The date the part was taught (YYYY-MM-DD) as of at, or None: the earliest coverage row on or before that date
    that covers the part, set by the student or for their class, on the part or any node above it. Coverage is
    profile, not events: a row counts only from its taught_on date, so a rebuild gives the same state. AI-literacy
    parts have no coverage."""
    if graph.is_literacy(part_id):
        return None
    nodes = [part_id] + [n["id"] for n in graph.ancestors(part_id)]
    marks = ",".join("?" * len(nodes))
    day, conn, class_id = _day(at), _conn(), student_class(student_id)
    found = [r[0] for r in conn.execute(
        f"SELECT taught_on FROM student_coverage WHERE student_id = ? AND node_id IN ({marks}) AND taught_on <= ?",
        (student_id, *nodes, day))]
    if class_id:
        found += [r[0] for r in conn.execute(
            f"SELECT taught_on FROM class_coverage WHERE class_id = ? AND node_id IN ({marks}) AND taught_on <= ?",
            (class_id, *nodes, day))]
    return min(found) if found else None


def covered_parts(student_id: str, at: str | datetime | None = None) -> dict[str, str]:
    """Every part the student's coverage record covers as of at, with its taught_on date (the earliest)."""
    conn, day, class_id = _conn(), _day(at), student_class(student_id)
    rows = list(conn.execute("SELECT node_id, taught_on FROM student_coverage WHERE student_id = ? AND taught_on <= ?",
                             (student_id, day)))
    if class_id:
        rows += list(conn.execute("SELECT node_id, taught_on FROM class_coverage WHERE class_id = ? AND taught_on <= ?",
                                  (class_id, day)))
    out: dict[str, str] = {}
    for row in rows:
        for part in graph.parts_of(row["node_id"]):
            if not graph.is_literacy(part):
                out[part] = min(row["taught_on"], out.get(part, row["taught_on"]))
    return out


def _expected(p: float, evidence_type: str, n_options: int | None) -> float:
    slip, guess = slip_guess(evidence_type, n_options)
    return p * (1 - slip) + (1 - p) * guess


def _taught_before(conn: sqlite3.Connection, student_id: str, part_id: str, ts: str) -> bool:
    """Whether the student was taught the part by ts: an exchange on it (at or before ts) that gave a worked example or a
    hint, or was "just show me"."""
    for row in conn.execute("""SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts <= ?
                               AND (support_given IN ('worked_example', 'hint') OR choice_taken = 'just_show_me')""",
                            (student_id, ts)):
        if part_id in _tagged_parts(split(row["node_ids"])):
            return True
    return False


def _pre_teaching_answers(conn: sqlite3.Connection, student_id: str, before: str) -> list[sqlite3.Row]:
    """The student's first answer on each part, from sessions before `before`, when it came before any teaching of the
    part: a pre-question, an "I know this" check, or an explain-back. AI-literacy parts are left out."""
    rows = conn.execute(
        """SELECT l.id, l.ts, l.part_id, l.evidence_type, l.score, l.n_options, x.choice_taken FROM evidence_log l
           LEFT JOIN exchange_log x ON x.id = l.exchange_id
           WHERE l.student_id = ? AND l.ts < ? AND l.id IN (SELECT MIN(id) FROM evidence_log WHERE student_id = ? GROUP BY part_id)
           ORDER BY l.ts, l.id""", (student_id, before, student_id)).fetchall()
    keep = []
    for r in rows:
        if graph.is_literacy(r["part_id"]):
            continue
        if not (r["evidence_type"] in ("prequestion", "explain_back") or r["choice_taken"] == "skip_point"):
            continue
        if not _taught_before(conn, student_id, r["part_id"], r["ts"]):
            keep.append(r)
    return keep


def starting_offsets(student_id: str, before: str | datetime | None = None) -> dict:
    """The student's personal starting adjustment, in log-odds, in two sectors that never mix: parts the class had
    covered when they answered, and parts it had not. Built from their pre-teaching first answers in sessions before
    `before` (default now), so it is stable within a session. Each sector: n / (n + starting.k) x (logit of the
    smoothed score minus logit of the smoothed expected success under the part's starting point), both smoothed
    ((sum + 0.5) / (n + 1)) so an all-right or all-wrong start cannot give an infinite offset, within
    +-starting.bound_logits. Returns {covered, not_covered, n_covered, n_not_covered}."""
    st, conn = _settings().starting, _conn()
    cutoff = session_start(conn, student_id, _event_ts(before))
    cacheable = not _settings().coverage.class_estimate_enabled       # a class estimate depends on other students: not cached
    shash = settings_hash()
    if cacheable:
        row = conn.execute("""SELECT covered_offset, covered_n, uncovered_offset, uncovered_n FROM learner_offset_cache
                              WHERE student_id = ? AND session_id = ? AND settings_hash = ? AND covered_offset IS NOT NULL""",
                           (student_id, cutoff, shash)).fetchone()
        if row:
            return {"covered": row["covered_offset"], "not_covered": row["uncovered_offset"],
                    "n_covered": row["covered_n"], "n_not_covered": row["uncovered_n"]}
    sums = {True: [0, 0.0, 0.0], False: [0, 0.0, 0.0]}      # sector -> [n, sum score, sum expected]
    for r in _pre_teaching_answers(conn, student_id, cutoff):
        sector = covered_since(student_id, r["part_id"], r["ts"]) is not None
        p0 = base_start(student_id, r["part_id"], r["ts"])["p"]
        n_sum = sums[sector]
        n_sum[0] += 1
        n_sum[1] += r["score"]
        n_sum[2] += _expected(p0, r["evidence_type"], r["n_options"])

    def offset(n: int, score: float, expected: float) -> float:
        if n == 0:
            return 0.0
        raw = n / (n + st.k) * (_logit((score + 0.5) / (n + 1)) - _logit((expected + 0.5) / (n + 1)))
        return max(-st.bound_logits, min(st.bound_logits, raw))

    out = {"covered": offset(*sums[True]), "not_covered": offset(*sums[False]),
           "n_covered": sums[True][0], "n_not_covered": sums[False][0]}
    if cacheable:
        with conn:
            conn.execute(
                """INSERT INTO learner_offset_cache (student_id, session_id, settings_hash, covered_offset, covered_n,
                     uncovered_offset, uncovered_n) VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (student_id, session_id) DO UPDATE SET settings_hash = excluded.settings_hash,
                     covered_offset = excluded.covered_offset, covered_n = excluded.covered_n,
                     uncovered_offset = excluded.uncovered_offset, uncovered_n = excluded.uncovered_n""",
                (student_id, cutoff, shash, out["covered"], out["n_covered"], out["not_covered"], out["n_not_covered"]))
    return out


def class_shift(class_id: str, at: str | datetime | None = None) -> float | None:
    """The class's own shift of its covered starting point, in log-odds, or None. Only when the school has turned the
    class estimate on (coverage.class_estimate_enabled) and at least coverage.class_min_students members have a first
    answer on a covered part before `at`. It reads one class's raw first answers only, against the boosted default, so
    there is no circularity and a rebuild gives the same state. Shrunk with k = coverage.class_k like the personal
    adjustment."""
    c = _settings().coverage
    if not c.class_estimate_enabled:
        return None
    conn, at_ts = _conn(), _event_ts(at)
    n, total, expected, who = 0, 0.0, 0.0, set()
    for member in (r["id"] for r in conn.execute("SELECT id FROM student WHERE class_id = ?", (class_id,))):
        for r in _pre_teaching_answers(conn, member, at_ts):
            if covered_since(member, r["part_id"], r["ts"]) is None:
                continue
            p0, _ = initial_state(r["part_id"])
            boosted = _sigmoid(_logit(p0) + c.boost_logit)
            n, total, expected = n + 1, total + r["score"], expected + _expected(boosted, r["evidence_type"], r["n_options"])
            who.add(member)
    if len(who) < c.class_min_students:
        return None
    return n / (n + c.class_k) * (_logit((total + 0.5) / (n + 1)) - _logit((expected + 0.5) / (n + 1)))


def base_start(student_id: str, part_id: str, at: str | datetime | None = None) -> dict:
    """A part's starting point before the student's own adjustment and prerequisites: {p, half_life, taught_on}. A
    covered part starts coverage.boost_logit up in log-odds from its normal start (Vishnu's change of 18 November,
    replacing a fixed covered prior); with the class estimate on, the class's own shift replaces the boost's size, but
    never starts the part more than coverage.class_max_down below the boosted start."""
    p0, half_life = initial_state(part_id)
    taught = covered_since(student_id, part_id, at)
    if taught is None:
        return {"p": p0, "half_life": half_life, "taught_on": None}
    c = _settings().coverage
    boosted = _sigmoid(_logit(p0) + c.boost_logit)
    cid = student_class(student_id)
    shift = class_shift(cid, at) if cid else None
    p = boosted if shift is None else max(_sigmoid(_logit(boosted) + shift), boosted - c.class_max_down)
    return {"p": p, "half_life": half_life, "taught_on": taught}


def has_evidence(student_id: str, part_id: str, at: str | datetime | None = None) -> bool:
    return _conn().execute("SELECT 1 FROM evidence_log WHERE student_id = ? AND part_id = ? AND ts <= ? LIMIT 1",
                           (student_id, graph.canonical(part_id), _event_ts(at))).fetchone() is not None


def _own_start(student_id: str, part_id: str, at: str | datetime | None) -> dict:
    """base_start plus the student's sector offset, before the prerequisite shift and the cap."""
    base = base_start(student_id, part_id, at)
    if graph.is_literacy(part_id):
        return base
    offsets = starting_offsets(student_id, at)
    sector = offsets["covered"] if base["taught_on"] else offsets["not_covered"]
    return {**base, "logit": _logit(base["p"]) + sector}


def _now_without_forward(student_id: str, part_id: str, at: str | datetime | None) -> float:
    """A part's p_now where its own prerequisites' shift is left out (so the feed-forward is one hop, never recursive)."""
    row = _conn().execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    if row is not None:
        return p_now(row["p_known"], row["half_life_days"], row["clock_start"], at)
    own = _own_start(student_id, part_id, at)
    clock = own["taught_on"]
    return p_now(_sigmoid(own.get("logit", _logit(own["p"]))), own["half_life"], clock, at)


def forward_shift(student_id: str, part_id: str, at: str | datetime | None = None) -> float:
    """How far a part's starting point moves because of its direct prerequisites: propagation.forward_weight x the mean,
    over them, of logit p_now minus logit of their starting point. Only a prerequisite the student has answered on
    moves it; one with no answers contributes 0 (its forgetting is not fed forward, because a covered dependent
    decays from its own taught date and counting both would penalise it twice). Course-pack edges, one hop, never
    recursive. It stops mattering once the part has its own evidence (it has a state then)."""
    if graph.is_literacy(part_id):
        return 0.0
    prereqs = [pp for edge in graph.prerequisites(part_id, 1) for pp in graph.parts_of(edge["other"])]
    deltas = []
    for pp in dict.fromkeys(prereqs):
        if not has_evidence(student_id, pp, at):
            deltas.append(0.0)
            continue
        start = _own_start(student_id, pp, at)
        now = _now_without_forward(student_id, pp, at)
        deltas.append(_logit(now) - start.get("logit", _logit(start["p"])))
    return _settings().propagation.forward_weight * sum(deltas) / len(deltas) if deltas else 0.0


def starting_point(student_id: str, part_id: str, at: str | datetime | None = None) -> dict:
    """Where a part the student has no evidence on starts, as {p, half_life, clock_start, taught_on}. In order:
    logit of the base start (the normal start, or the covered boost or class estimate), plus the student's sector
    offset, plus the prerequisite shift; back to a probability, within [0.01, starting.cap] (answers can take a
    part anywhere). The forgetting clock starts at taught_on for a covered part. AI-literacy parts are the plain prior."""
    st = _settings().starting
    own = _own_start(student_id, part_id, at)
    if graph.is_literacy(part_id):
        return {"p": own["p"], "half_life": own["half_life"], "clock_start": None, "taught_on": None}
    x = own["logit"] + forward_shift(student_id, part_id, at)
    return {"p": min(st.cap, max(0.01, _sigmoid(x))), "half_life": own["half_life"],
            "clock_start": own["taught_on"], "taught_on": own["taught_on"]}


def shown_level(student_id: str, part_id: str, at: str | datetime | None = None) -> str:
    """The level to show a student for a part: new, developing or secure once they have an answer on it; before that
    never developing or secure, whatever the starting number: "taught_in_class" if their class covered it ("taught in
    class, not yet checked"), else new. The planner still uses the number."""
    if graph.is_literacy(part_id) or has_evidence(student_id, part_id, at):
        return level(part_p(student_id, part_id, at))
    return "taught_in_class" if covered_since(student_id, part_id, at) else "new"


def shown_rollup(student_id: str, node_id: str, at: str | datetime | None = None) -> str:
    """shown_level for a concept or topic: with no answer on any part under it, taught_in_class if any part is
    covered, else new; otherwise the rollup's level."""
    parts = [p for p in graph.parts_of(node_id)]
    if parts and not any(has_evidence(student_id, p, at) for p in parts):
        return "taught_in_class" if any(covered_since(student_id, p, at) for p in parts) else "new"
    return level(rollup(student_id, node_id, at))


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
    start = starting_point(student_id, part_id, ts)
    return {"student_id": student_id, "part_id": part_id, "p_known": start["p"], "half_life_days": start["half_life"],
            "last_seen": ts, "n_evidence": 0, "offload_left": 0, "was_secure": 0,
            "clock_start": start["clock_start"], "last_correct": None, "exchanges_since_evidence": 0}


def _clamp(p: float) -> float:
    """p_known kept inside [0.001, 0.999]: BKT can round to exactly 1.0 after a long run of right answers, and the
    exchange nudge works in odds, p / (1 - p)."""
    return min(0.999, max(0.001, p))


def _save_state(conn: sqlite3.Connection, state: dict) -> None:
    state["p_known"] = _clamp(state["p_known"])
    state["was_secure"] = int(state["was_secure"] or _p_at(state, state["last_seen"]) >= _settings().levels.secure)
    columns = list(state)
    conn.execute(f"INSERT OR REPLACE INTO part_state ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})",
                 [state[c] for c in columns])


def _floored(p: float, part_id: str, has_answers: bool, clock_start: str | None) -> float:
    """A part taught in class and never answered here forgets only as far as where it would have started untaught: a
    covered part must not look weaker than an untaught one. (A minimal decay-to-prior, for parts with no answers; the
    full change for answered parts is held.)"""
    if has_answers or not clock_start:
        return p
    return max(p, initial_state(part_id)[0])


def _p_at(state: dict, ts: str) -> float:
    p = p_now(state["p_known"], state["half_life_days"], state["clock_start"], ts)
    return _floored(p, state["part_id"], state["n_evidence"] > 0, state["clock_start"])


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
    """Apply one exchange event: nudges, the "just show me" review, misconception activation, untested reviews,
    last_seen.

    An exchange is not evidence: it nudges p_known a little by its labels, only up to nudges.ceiling, and moves
    the forgetting clock only decay.seen_refresh of the way to now. Being shown doesn't change understanding (step 05d): a
    "just show me" exchange gets no nudge and doesn't discount later evidence (the immediate-recall rule
    already lowers credit straight after being shown); it still queues a review. Old ids are resolved through id_map.
    """
    s, conn = _settings(), _conn()
    student_id, ts = event["student_id"], event["ts"]
    t = parse_ts(ts)
    # an exchange earlier than cached sessions changes what counts as teaching there: drop their cached offsets
    conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ? AND session_id > ?",
                 (student_id, session_start(conn, student_id, ts)))
    multiplier = s.nudges.depth[event["question_depth"]] * s.nudges.engagement[event["engagement"]]
    offloaded = bool(event["offloading"]) or event.get("choice_taken") == "just_show_me"
    support = event.get("support_given")

    for part, strength in _tagged_parts(split(event["node_ids"])).items():
        state = _load_state(conn, student_id, part, ts)
        if not offloaded:
            odds = _clamp(state["p_known"]) / (1 - _clamp(state["p_known"]))   # also a 1.0 saved before the clamp
            odds *= 1 + (multiplier - 1) * strength
            nudged = odds / (1 + odds)
            # Talk is not evidence (nudges.ceiling): it can raise a part towards the ceiling, never past it, and
            # never lowers a part that evidence has already lifted above it.
            state["p_known"] = max(state["p_known"], min(nudged, s.nudges.ceiling))
        if state["clock_start"]:
            clock = parse_ts(state["clock_start"])
            clock += (t - clock) * s.decay.seen_refresh * strength
            state["clock_start"] = clock.isoformat(timespec="seconds")
        state["last_seen"] = ts
        state["exchanges_since_evidence"] += 1
        if offloaded:
            _queue_review(conn, student_id, part, t + timedelta(days=s.scheduling.just_show_me_gap_days), "just_show_me")
        if support and support != "none":
            conn.execute("INSERT INTO approach_record (student_id, part_id, approach, ts) VALUES (?, ?, ?, ?)",
                         (student_id, part, support, ts))
        if state["exchanges_since_evidence"] >= s.scheduling.untested_after and _p_at(state, ts) < s.scheduling.untested_below:
            _queue_review(conn, student_id, part, t, "untested")
        _save_state(conn, state)

    _activate_misconceptions(conn, student_id, split(event.get("misconception_ids")), ts)


def _activate_misconceptions(conn: sqlite3.Connection, student_id: str, misconception_ids: list[str], ts: str) -> None:
    """Mark known, non-rejected misconceptions active for the student (old ids resolve through id_map)."""
    for misconception_id in misconception_ids:
        misconception_id = graph.canonical(misconception_id)
        if conn.execute("SELECT 1 FROM content.misconception WHERE id = ? AND status != 'rejected'", (misconception_id,)).fetchone():
            conn.execute("INSERT OR REPLACE INTO student_misconception (student_id, misconception_id, active, last_seen) "
                         "VALUES (?, ?, 1, ?)", (student_id, misconception_id, ts))


ASSESSMENT_KINDS = ("homework", "class_test", "mock")   # a student's own upcoming tests (priorities)


def assessments(student_id: str, at: datetime | str | None = None) -> list[dict]:
    """The student's upcoming assessments (dated after at, default now), soonest first: {id, name, kind, date,
    part_ids}. Profile data, like exam_date_override: a rebuild uses them as they are now."""
    day = parse_ts(at or now_iso()).date().isoformat()
    rows = _conn().execute("SELECT id, name, kind, date, part_ids FROM student_assessment WHERE student_id = ? "
                           "AND date > ? ORDER BY date, id", (student_id, day)).fetchall()
    return [{**dict(r), "part_ids": json.loads(r["part_ids"])} for r in rows]


def _days_until(date_text: str, at: datetime) -> float:
    return (parse_ts(date_text) - at).total_seconds() / 86400


def final_exam_days(student_id: str, part_id: str, at: datetime) -> float | None:
    """Days from at to the student's final exam on this part: their exam_date_override if set and ahead,
    otherwise the soonest exam paper covering the part. None if there is no exam ahead."""
    row = _conn().execute("SELECT exam_date_override FROM student_profile WHERE student_id = ?", (student_id,)).fetchone()
    dates = [row["exam_date_override"]] if row and row["exam_date_override"] else []
    if not dates or parse_ts(dates[0]) <= at:
        dates = [paper["date"] for paper in graph.exam_papers_for(part_id) if paper["date"]]
    ahead = [(parse_ts(d) - at).total_seconds() / 86400 for d in dates]
    ahead = [d for d in ahead if d > 0]
    return min(ahead) if ahead else None


def days_to_exam(student_id: str, part_id: str, at: datetime) -> float | None:
    """Days from at to the student's next test on this part: the final exam (final_exam_days) or the soonest of
    their own upcoming assessments covering it (priorities). None if there is none ahead."""
    ahead = [_days_until(a["date"], at) for a in assessments(student_id, at) if part_id in a["part_ids"]]
    final = final_exam_days(student_id, part_id, at)
    ahead = [d for d in ahead + ([final] if final is not None else []) if d > 0]
    return min(ahead) if ahead else None


KIND_LABELS = {"homework": "homework", "class_test": "class test", "mock": "mock", "final": "final exam"}


def p_on(student_id: str, part_id: str, when: datetime | str) -> float:
    """The part's predicted p on a date: p_now with decay run forward to when (priorities)."""
    return part_p(student_id, part_id, when)


def step_value(student_id: str, part_id: str, at: datetime | str | None = None) -> dict:
    """How much a step on a part is worth (priorities): the sum, over the final exam and the student's upcoming
    assessments covering the part, of weight(kind) x urgency(days to it) x (1 - p on its date). There is no
    learning-chance factor: with one learn rate for every evidence type it would scale every value equally and
    never change a choice (step 05n).
    urgency = clamp(horizon_days / max(days, 1), urgency_floor, 1). With no final exam date ahead, the final
    counts at urgency_floor with today's p. Returns {value, reason}: reason is the assessment (not the final) that
    adds the most, or None."""
    s, at_dt = _settings().priorities, parse_ts(at or now_iso())
    weights = {"homework": s.weight_homework, "class_test": s.weight_class_test, "mock": s.weight_mock}

    def urgency(days: float | None) -> float:
        return s.urgency_floor if days is None else min(1.0, max(s.urgency_floor, s.horizon_days / max(days, 1.0)))

    final = final_exam_days(student_id, part_id, at_dt)
    when = at_dt + timedelta(days=final) if final is not None else at_dt
    total = s.weight_final * urgency(final) * (1 - p_on(student_id, part_id, when))
    reason, best = None, 0.0
    for a in assessments(student_id, at_dt):
        if part_id not in a["part_ids"]:
            continue
        days = _days_until(a["date"], at_dt)
        term = weights[a["kind"]] * urgency(days) * (1 - p_on(student_id, part_id, a["date"]))
        total += term
        if term > best:
            reason, best = {**a, "days": days}, term
    return {"value": total, "reason": reason}


def reason_text(assessment: dict, at: datetime | str | None = None) -> str:
    """A few words on why a review was picked: "on your mock on Tuesday" (the day within a week, else the date)."""
    day = parse_ts(assessment["date"]).date()
    when = day.strftime("%A") if assessment["days"] <= 7 else f"{day.day} {day.strftime('%b')}"
    return f"on your {KIND_LABELS[assessment['kind']]} on {when}"


def review_gap_days(student_id: str, part_id: str, at: datetime) -> float:
    """Days until the next review after evidence: a share of the days left to the exam (Cepeda et al., 2008),
    a smaller share as the exam gets closer. With no exam ahead, decay.base_half_life_days."""
    s = _settings().scheduling
    days = days_to_exam(student_id, part_id, at)
    if days is None:
        return _settings().decay.base_half_life_days
    share = s.share_far if days > 60 else s.share_mid if days >= 14 else s.share_near
    return share * days


def _recently_taught(conn: sqlite3.Connection, student_id: str, part_id: str, ts: str) -> bool:
    """True if an exchange on the part with a worked example or hint happened within
    evidence.immediate_window_minutes before ts (inclusive; a tag on a concept counts for its parts)."""
    since = _event_ts(parse_ts(ts) - timedelta(minutes=_settings().evidence.immediate_window_minutes))
    rows = conn.execute(
        """SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
           AND support_given IN ('worked_example', 'hint')""",
        (student_id, since, ts))
    return any(part_id in _tagged_parts(split(r["node_ids"])) for r in rows)


# --- sessions ----------------------------------------------------------------


def _event_times(conn: sqlite3.Connection, student_id: str, until: str) -> list[str]:
    """Timestamps of the student's exchanges and evidence up to until, newest first."""
    rows = conn.execute(
        """SELECT ts FROM exchange_log WHERE student_id = ? AND ts <= ?
           UNION ALL SELECT ts FROM evidence_log WHERE student_id = ? AND ts <= ? ORDER BY ts DESC""",
        (student_id, until, student_id, until))
    return [r["ts"] for r in rows]


def session_start(conn: sqlite3.Connection, student_id: str, ts: str) -> str:
    """The start of the session containing ts: walk back through both logs until a gap longer than session.gap_minutes."""
    gap = timedelta(minutes=_settings().session.gap_minutes)
    start = previous = parse_ts(ts)
    for earlier in _event_times(conn, student_id, ts):
        t = parse_ts(earlier)
        if previous - t > gap:
            break
        start = previous = t
    return _event_ts(start)


def prequestion_weight(conn: sqlite3.Connection, student_id: str, part_id: str, ts: str) -> float:
    """How much a pre-question answer counts, 0–1, from how much the part has been covered so far:
    min(1, (exchanges on it × exchange_weight + n_evidence) / full_weight_at). 0 means never taught."""
    s = _settings().prequestion
    exchanges = sum(1 for r in conn.execute("SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts <= ?",
                                            (student_id, ts)) if part_id in _tagged_parts(split(r["node_ids"])))
    state = _load_state(conn, student_id, part_id, ts)
    return min(1.0, (exchanges * s.exchange_weight + state["n_evidence"]) / s.full_weight_at)


def extra_slip(minutes: float) -> float:
    """The extra slip from time on task: 0 before fatigue.slip_start_minutes, then fatigue.slip_per_minute per minute,
    up to fatigue.extra_slip_cap (Randles, Harlow & Inzlicht, 2017; end-of-test declines in TIMSS). Pacing, not a
    state: it is added to an answer's slip whoever the student is."""
    f = _settings().fatigue
    return min(f.extra_slip_cap, max(0.0, (minutes - f.slip_start_minutes) * f.slip_per_minute))


def rapid_guess(latency_s: float | None, question_words: int | None, answer_words: int | None) -> bool:
    """Whether an answer came faster than the question could be read at fatigue.reading_wpm plus the answer typed at
    fatigue.typing_wpm (Wise & Kong, 2005, effort-moderated scoring). The latency is the time since the student's
    previous exchange, which includes the chatbot's writing time, so a flag is less likely: the safe direction. False
    when any of the three is unknown: a chatbot that doesn't send the word count is never flagged."""
    if latency_s is None or not question_words or answer_words is None:
        return False
    f = _settings().fatigue
    return latency_s < question_words * 60 / f.reading_wpm + answer_words * 60 / f.typing_wpm


def _rapid_for_evidence(conn: sqlite3.Connection, event: dict) -> bool:
    """Whether a chat answer was a rapid guess, from the timing stored on the exchange it came with."""
    if not event.get("exchange_id"):
        return False
    row = conn.execute("SELECT latency_s, question_words, answer_words FROM exchange_log WHERE id = ?",
                       (event["exchange_id"],)).fetchone()
    return bool(row) and rapid_guess(row["latency_s"], row["question_words"], row["answer_words"])


def _fatigued(conn: sqlite3.Connection, event: dict, session_id: str, rapid: bool) -> bool:
    """Whether this piece of evidence falls in long-session or rushing mode (the "fatigued" state).

    Once in the mode, the session stays in it. Otherwise it starts here when the session is fatigue.mode_minutes old,
    or this is the fatigue.rapid_guesses-th rapid guess in the session. The mode follows time on task and answers
    faster than the question can be read; it never infers an emotion or a tired state from how well they answer."""
    f, student_id, ts = _settings().fatigue, event["student_id"], event["ts"]
    if conn.execute("SELECT 1 FROM evidence_derived WHERE student_id = ? AND session_id = ? AND fatigued = 1",
                    (student_id, session_id)).fetchone():
        return True
    if (parse_ts(ts) - parse_ts(session_id)).total_seconds() / 60 >= f.mode_minutes:
        return True
    earlier = conn.execute("SELECT COUNT(*) FROM evidence_derived WHERE student_id = ? AND session_id = ? AND rapid = 1",
                           (student_id, session_id)).fetchone()[0]
    return rapid and earlier + 1 >= f.rapid_guesses


def personalisation_on() -> bool:
    """personalisation.enabled (off by default), unless the environment sets EDUX_PERSONALISATION: 1 turns the
    learning-rate offset on, 0 turns it off."""
    switch = os.environ.get("EDUX_PERSONALISATION")
    return _settings().personalisation.enabled if switch is None else switch == "1"


def _clear_offset_cache(student_id: str, after_session: str | None = None) -> None:
    """Drop the student's cached offsets (all of them, or those for sessions after after_session). The cache holds
    nothing that cannot be recomputed from the event logs, so dropping it is always safe."""
    conn = _conn()
    with conn:
        if after_session is None:
            conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ?", (student_id,))
        else:
            conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ? AND session_id > ?", (student_id, after_session))


def _learn_eligible(conn: sqlite3.Connection, student_id: str, since: str | None, before: str) -> list[sqlite3.Row]:
    """The evidence the learning-rate offset counts, from session `since` (inclusive) to before `before`, in order:
    not fatigued, immediate or weightless, not on an AI-literacy part, and not a part's first answer (that belongs
    to the starting-point adjustment)."""
    rows = conn.execute(
        """SELECT d.evidence_id, d.session_id, l.part_id, d.surprise FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id
           WHERE d.student_id = ? AND d.session_id >= ? AND d.session_id < ? AND d.fatigued = 0 AND d.immediate = 0 AND d.weight > 0
           ORDER BY l.ts, l.id""", (student_id, since or "", before)).fetchall()
    firsts = {r[0] for r in conn.execute("SELECT MIN(id) FROM evidence_log WHERE student_id = ? GROUP BY part_id", (student_id,))}
    return [r for r in rows if not graph.is_literacy(r["part_id"]) and r["evidence_id"] not in firsts]


def _learn_step(state: dict, p) -> float:
    """One step of the offset at a session boundary, from the running statistics of the evidence before it."""
    low, high = (math.log(b) for b in p.learn_rate_weight_bounds)
    n, target = state["n"], 0.0
    if n >= p.min_observations and len(state["parts"]) >= p.min_parts and state["w"] > 0:
        target = min(high, max(low, n / (n + p.learn_rate_k) * (state["sx"] / state["w"]) * p.surprise_scale))
    step = p.max_change_per_session
    return state["offset"] + min(step, max(-step * p.down_change_factor, target - state["offset"]))


def learning_offset(student_id: str, before: str | datetime | None = None) -> dict:
    """The student's learning-rate offset (log-odds on bkt.learn_rate) for a session starting at before (default now),
    a pure function of evidence in earlier sessions, so rebuild gives the same values (personal-learning-rate).

    Evidence counts unless it was fatigued, immediate recall, an untaught pre-question (weight 0), on an AI-literacy
    part, or the student's first piece of evidence on its part (that belongs to the starting-point adjustment, step
    05q, and counting it here would count "already knew it" twice). The offset steps once per session, in order: target
    = n / (n + learn_rate_k) x the mean surprise of the evidence before that session, weighted by recency (half each
    recency_half_life pieces back), x surprise_scale, within log(learn_rate_weight_bounds); 0 until min_observations
    pieces across min_parts parts. Each step rises at most max_change_per_session, and falls at most
    down_change_factor times that. Returns {offset, n, weight}: the offset, the pieces of evidence it rests on, and
    the odds weight exp(offset). Off: offset 0.

    Step 05r: the running statistics (count, recency-weighted sums, parts seen, offset) are cached per session in
    learner_offset_cache, so a call reads only the sessions since the last cached boundary instead of the whole
    history; the weighted mean is updated one piece at a time (S = S x r + x, W = W x r + 1 with r = 0.5 ^ (1 /
    recency_half_life)), which equals the direct sum, and live and rebuild use the same updates in the same order, so
    rebuild gives identical state."""
    p, conn = _settings().personalisation, _conn()
    if not personalisation_on():
        return {"offset": 0.0, "n": 0, "weight": 1.0}
    before_ts, shash = _event_ts(before), settings_hash()
    cached = conn.execute(
        """SELECT session_id, learn_state FROM learner_offset_cache WHERE student_id = ? AND settings_hash = ?
           AND learn_state IS NOT NULL AND session_id < ? ORDER BY session_id DESC LIMIT 1""",
        (student_id, shash, before_ts)).fetchone()
    rows = _learn_eligible(conn, student_id, cached["session_id"] if cached else None, before_ts)
    if cached and (not rows or rows[0]["session_id"] != cached["session_id"]):
        _clear_offset_cache(student_id)        # the cached boundary no longer matches the evidence: start again
        cached, rows = None, _learn_eligible(conn, student_id, None, before_ts)
    state = json.loads(cached["learn_state"]) if cached else {"n": 0, "sx": 0.0, "w": 0.0, "parts": [], "offset": 0.0, "groups": 0}
    state["parts"] = set(state["parts"])
    decay, current, fresh = 0.5 ** (1 / p.recency_half_life), None, []
    for r in rows:
        if r["session_id"] != current:
            resumed = current is None and cached is not None       # this group's boundary is already in the state
            if state["groups"] > 0 and not resumed:                # every group but the first has a boundary step
                state["offset"] = _learn_step(state, p)
                fresh.append((r["session_id"], {**state, "parts": sorted(state["parts"])}))
            state["groups"] += 1
            current = r["session_id"]
        state["n"] += 1
        state["sx"] = state["sx"] * decay + r["surprise"]
        state["w"] = state["w"] * decay + 1.0
        state["parts"].add(r["part_id"])
    offset = _learn_step(state, p)
    if fresh:
        with conn:
            for session_id, snap in fresh:
                conn.execute(
                    """INSERT INTO learner_offset_cache (student_id, session_id, settings_hash, learn_state, learn_offset, learn_n)
                       VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (student_id, session_id) DO UPDATE SET
                       settings_hash = excluded.settings_hash, learn_state = excluded.learn_state,
                       learn_offset = excluded.learn_offset, learn_n = excluded.learn_n""",
                    (student_id, session_id, shash, json.dumps(snap), snap["offset"], snap["n"]))
    return {"offset": offset, "n": state["n"], "weight": math.exp(offset)}


def _reported(conn: sqlite3.Connection, event: dict) -> bool:
    """The evidence came with an exchange labelled source_conflict (a dead or mismatched source reported)."""
    row = conn.execute("SELECT source_conflict FROM exchange_log WHERE id = ?", (event.get("exchange_id"),)).fetchone()
    return bool(row and row["source_conflict"])


def _checked_before(conn: sqlite3.Connection, event: dict) -> bool:
    """The student has done one successful check of their own on Verify: a correct Verify answer that was not a
    report."""
    return conn.execute(
        """SELECT 1 FROM evidence_log e LEFT JOIN exchange_log x ON x.id = e.exchange_id WHERE e.student_id = ?
           AND e.part_id = ? AND e.id < ? AND e.score >= ? AND COALESCE(x.source_conflict, 0) = 0 LIMIT 1""",
        (event["student_id"], AIL_VERIFY, event["id"], _settings().bkt.correct_share)).fetchone() is not None


def apply_evidence_event(event: dict) -> None:
    """Apply one evidence event: score -> correct, the immediate-recall discount for chat evidence,
    surprise against the expected success p(1 - slip) + (1 - p) guess (stored in evidence_derived), misconception activation
    on wrong evidence, then the BKT update (_apply_evidence)."""
    s, conn = _settings(), _conn()
    student_id, ts = event["student_id"], event["ts"]
    node = graph.get_node(event["part_id"])
    if node is None or node["level"] != "part":
        return
    part_id = node["id"]
    correct = event["score"] >= s.bkt.correct_share
    evidence_type = event["evidence_type"]
    immediate = False
    if evidence_type == "prequestion":
        weight = prequestion_weight(conn, student_id, part_id, ts)
    else:
        weight = 1.0
        immediate = event["origin"] == "chat" and _recently_taught(conn, student_id, part_id, ts)
    n_points = None
    if evidence_type == "explain_back":
        n_points = 1 if event.get("point_id") else len(graph.score_points(part_id))
    slip, guess = slip_guess(evidence_type, event.get("n_options"), immediate, n_points)
    cap = None
    if immediate and event["evidence_type"] not in OPEN_ANSWERS:
        # a pick straight after being shown or hinted (the option repeats the point just shown) can't make a part
        # secure; an answer they write themselves (explain-back, extend) still can (research fixes, 0010b)
        cap = s.levels.secure - 0.01
    if part_id == AIL_VERIFY and _reported(conn, event) and not _checked_before(conn, event):
        # a reported dead or mismatched source counts as a check (a dead page has nothing else to tick), but it can't
        # be told apart from a made-up one: until the student has done one successful check of their own on Verify,
        # reports can't make Verify secure
        cap = s.levels.secure - 0.01
    session_id = session_start(conn, student_id, ts)
    conn.execute("DELETE FROM learner_offset_cache WHERE student_id = ? AND session_id > ?", (student_id, session_id))   # out of order
    rapid = event["origin"] == "chat" and _rapid_for_evidence(conn, event)
    if rapid:
        weight = 0.0    # a rapid guess says nothing about knowledge (effort-moderated scoring: Wise & DeMars, 2006)
    slip_add = extra_slip((parse_ts(ts) - parse_ts(session_id)).total_seconds() / 60)   # time on task raises slip
    slip = min(s.session.slip_cap, slip + slip_add)
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)
    expected = p_before * (1 - slip) + (1 - p_before) * guess   # chance of a correct answer under this type's slip and guess
    surprise = weight * (event["score"] - expected)
    fatigued = _fatigued(conn, event, session_id, rapid)
    conn.execute(
        """INSERT OR REPLACE INTO evidence_derived (evidence_id, student_id, session_id, p_before, surprise, weight, fatigued,
             immediate, rapid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (event["id"], student_id, session_id, p_before, surprise, weight, int(fatigued), int(immediate), int(rapid)))
    if not correct:
        _activate_misconceptions(conn, student_id, split(event.get("misconception_ids")), ts)
    if weight > 0:  # an untaught pre-question or a rapid guess is not applied to what the student knows
        if part_id == AIL_VERIFY and correct:   # Verify is graded: 3 of 4 ticks moves it 3/4 as far as 4 of 4
            weight *= event["score"]
        # AI literacy is a different skill, measured differently: its parts use the population learn rate
        offset = 0.0 if graph.is_literacy(part_id) else learning_offset(student_id, session_id)["offset"]
        learn_rate = personal_learn_rate(s.bkt.learn_rate, offset)
        _apply_evidence(conn, student_id, part_id, slip, guess, correct, ts, weight=weight, slip_add=0.0,
                        learn_rate=learn_rate, cap=cap)


def slip_guess(evidence_type: str, n_options: int | None = None, immediate: bool = False,
               n_points: int | None = None) -> tuple[float, float]:
    """Slip and guess for a piece of evidence. With bkt.mcq_guess_from_options, a multiple-choice question that
    recorded how many options it showed guesses 1 / n_options (older rows keep the type's guess). Immediate
    evidence (straight after a worked example or hint) takes immediate's slip and the larger of immediate's guess
    and the type's own, so a question with few options is never discounted less. An explain-back that needs
    n_points mark points guesses less as they rise (bkt.explain_back_guess: a complete multi-point answer is far
    harder to produce by luck); n_points is 1 for a narrowed explain-back, else the part's point count."""
    s = _settings()
    if evidence_type not in s.bkt.evidence:
        raise ValueError(f"evidence_type must be one of {', '.join(s.bkt.evidence)}")
    slip, guess = s.bkt.evidence[evidence_type].slip, s.bkt.evidence[evidence_type].guess
    if s.bkt.mcq_guess_from_options and n_options:
        guess = 1 / n_options
    if evidence_type == "explain_back" and n_points is not None:
        g = s.bkt.explain_back_guess
        guess = g.up_to_2 if n_points <= 2 else g.three if n_points == 3 else g.four_plus
    if immediate:
        slip, guess = s.bkt.evidence["immediate"].slip, max(s.bkt.evidence["immediate"].guess, guess)
    return slip, guess


def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, slip: float, guess: float, correct: bool,
                    ts: str, weight: float = 1.0, slip_add: float = 0.0, learn_rate: float | None = None,
                    cap: float | None = None) -> None:
    """The BKT update on one part with the evidence's slip and guess (slip_guess); weight (0–1) scales how far
    p_known moves towards the BKT result. slip_add raises slip (capped at session.slip_cap) while the session is
    fatigued. learn_rate is the student's own (learning_offset), else bkt.learn_rate."""
    s = _settings()
    node = graph.get_node(part_id)
    if node is None or node["level"] != "part":
        raise ValueError(f"{part_id!r} is not a part")
    part_id, t = node["id"], parse_ts(ts)
    ts = t.isoformat(timespec="seconds")

    state = _load_state(conn, student_id, part_id, ts)
    before = _p_at(state, ts)
    if slip_add:
        slip = max(slip, min(s.session.slip_cap, slip + slip_add))
    if correct:
        p = before * (1 - slip) / (before * (1 - slip) + (1 - before) * guess)
    else:
        p = before * slip / (before * slip + (1 - before) * (1 - guess))
    p += (1 - p) * (s.bkt.learn_rate if learn_rate is None else learn_rate)
    p = before + weight * (p - before)
    if cap is not None and p > cap:   # cap: p_known rises no higher than this (or than where it was)
        p = max(before, cap)

    factor = s.decay.on_success if correct else s.decay.on_failure
    state["half_life_days"] = max(s.decay.min_half_life_days, state["half_life_days"] * factor)
    state["p_known"] = p
    if correct:
        state["clock_start"] = state["last_correct"] = ts
    elif state["clock_start"]:
        state["clock_start"] = ts  # decay continues from the new, lower estimate
    state["n_evidence"] += 1
    state["exchanges_since_evidence"] = 0
    state["last_seen"] = ts
    _save_state(conn, state)

    gain = p - before
    if gain > 0:
        for edge in graph.prerequisites(part_id, 1):
            for prereq in graph.parts_of(edge["other"]):
                other = _load_state(conn, student_id, prereq, ts)
                was = _p_at(other, ts)
                # a boost from a dependent part is indirect evidence: it never makes a prerequisite secure on its own
                other["p_known"] = min(0.99, was + s.propagation.prereq_boost * gain, max(was, s.levels.secure - 0.01))
                if other["clock_start"]:
                    other["clock_start"] = ts
                _save_state(conn, other)

    if correct:
        conn.execute(
            """UPDATE student_misconception SET active = 0, last_seen = ? WHERE student_id = ? AND active = 1
               AND misconception_id IN (SELECT id FROM content.misconception WHERE node_id = ?)""",
            (ts, student_id, part_id))
    conn.execute(
        """UPDATE approach_record SET next_check_correct = ? WHERE id = (SELECT id FROM approach_record
           WHERE student_id = ? AND part_id = ? AND next_check_correct IS NULL ORDER BY ts DESC, id DESC LIMIT 1)""",
        (int(correct), student_id, part_id))
    gap, reason = review_gap_days(student_id, part_id, t), "scheduled"
    below = days_until_below(state, s.scheduling.review_when_below)
    if below is not None and below < gap:
        gap, reason = below, "recall_below"
    gap = max(s.scheduling.min_gap_days, gap)
    _queue_review(conn, student_id, part_id, t + timedelta(days=gap), reason, replace=True)


def answer_p_before(student_id: str, part_id: str, ts: str) -> float | None:
    """The student's p_now on the part just before the answer recorded at ts was applied (stored in
    evidence_derived), or None when no evidence was recorded then. Feedback reads this, not the level after the
    answer: the answer that tips a part to secure may be a lucky guess and still deserves its why."""
    row = _conn().execute(
        """SELECT d.p_before FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id
           WHERE l.student_id = ? AND l.part_id = ? AND l.ts = ? ORDER BY l.id DESC LIMIT 1""",
        (student_id, graph.canonical(part_id), ts)).fetchone()
    return row["p_before"] if row else None


def days_until_below(state: dict, threshold: float) -> float | None:
    """Days from the clock's start until p_now decays below threshold, or None when it never crosses it: no clock
    yet (nothing learnt, nothing to forget) or p_known already at or below it."""
    if not state["clock_start"] or state["p_known"] <= threshold:
        return None
    return state["half_life_days"] * math.log2(state["p_known"] / threshold)


# --- reading state ---------------------------------------------------------


def part_p(student_id: str, part_id: str, at: datetime | str | None = None) -> float:
    """The student's current p_now on a part; a part they haven't met is at its starting estimate."""
    part_id = graph.canonical(part_id)
    row = _conn().execute("SELECT * FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    if row is None:    # a part they haven't met: its starting point, decaying from the date the class was taught it
        start = starting_point(student_id, part_id, at)
        return _floored(p_now(start["p"], start["half_life"], start["clock_start"], at), part_id, False, start["clock_start"])
    return _floored(p_now(row["p_known"], row["half_life_days"], row["clock_start"], at), part_id,
                    row["n_evidence"] > 0, row["clock_start"])


def level(p: float) -> str:
    """new, developing or secure from the thresholds in settings.toml."""
    levels = _settings().levels
    return "new" if p < levels.new else "secure" if p >= levels.secure else "developing"


def rollup(student_id: str, node_id: str, at: datetime | str | None = None) -> float:
    """Importance-weighted mean p_now of the parts under a node (a plain mean if no part has importance)."""
    parts = graph.parts_of(node_id)
    if not parts:
        return 0.0
    weights = [graph.weight(p)["importance"] for p in parts]
    values = [part_p(student_id, p, at) for p in parts]
    if sum(weights) <= 0:
        return sum(values) / len(values)
    return sum(w * v for w, v in zip(weights, values)) / sum(weights)


def due_reviews(student_id: str, limit: int, at: datetime | str | None = None) -> list[dict]:
    """Course parts due for review by at (default now), most important first, then the most overdue. AI-literacy
    parts are practised through their tasks and checks (step 05e), never as course reviews."""
    at_dt = parse_ts(at or now_iso())
    due = []
    for row in _conn().execute("SELECT part_id, due, reason FROM review_queue WHERE student_id = ?", (student_id,)):
        node = graph.get_node(row["part_id"])
        if node and parse_ts(row["due"]) <= at_dt and not graph.is_literacy(node["id"]):
            due.append({"part_id": node["id"], "name": node["name"], "due": row["due"], "reason": row["reason"],
                        "p_now": part_p(student_id, node["id"], at), "importance": graph.weight(node["id"])["importance"]})
    queued = {row["part_id"] for row in _conn().execute("SELECT part_id FROM review_queue WHERE student_id = ?", (student_id,))}
    course_parts = set(all_parts())
    for part, taught in covered_parts(student_id, at_dt).items():   # taught in class, never practised here: reviewed too
        if part in queued or has_evidence(student_id, part, at_dt) or part not in course_parts:
            continue
        t = parse_ts(taught)
        when = t + timedelta(days=max(_settings().scheduling.min_gap_days, review_gap_days(student_id, part, t)))
        if when <= at_dt:
            due.append({"part_id": part, "name": graph.get_node(part)["name"], "due": when.isoformat(timespec="seconds"),
                        "reason": "taught_in_class", "p_now": part_p(student_id, part, at_dt),
                        "importance": graph.weight(part)["importance"]})
    due.sort(key=lambda r: (-r["importance"], r["due"]))
    return due[:limit]


def all_parts() -> list[str]:
    return [part for topic in graph.topics() for part in graph.parts_of(topic["id"])]


def candidates(student_id: str, limit: int, at: datetime | str | None = None) -> list[dict]:
    """Parts to teach next: p_now inside propagation.queue_band with every prerequisite at least developing,
    ordered by importance x (1 - p_now)."""
    low, high = _settings().propagation.queue_band
    found = []
    for part in all_parts():
        p = part_p(student_id, part, at)
        if not low <= p <= high:
            continue
        prereqs = [pp for edge in graph.prerequisites(part, 1) for pp in graph.parts_of(edge["other"])]
        if any(level(part_p(student_id, pp, at)) == "new" for pp in prereqs):
            continue
        importance = graph.weight(part)["importance"]
        found.append({"part_id": part, "name": graph.get_node(part)["name"], "p_now": p, "importance": importance,
                      "score": importance * (1 - p)})
    found.sort(key=lambda c: -c["score"])
    return found[:limit]


def support_level(p: float) -> str:
    """worked_example, hint or explain_back from p_now."""
    support = _settings().support
    return "worked_example" if p < support.worked_example_below else "hint" if p < support.hint_below else "explain_back"


def anchor(student_id: str, part_id: str, at: datetime | str | None = None) -> dict | None:
    """The best secure analogous part to teach through, with the edge note: highest link weight, then the
    same part type (a calculation anchors a calculation), then the highest p_now."""
    target = graph.get_node(part_id)
    best, best_key = None, None
    for edge in graph.analogous(part_id):
        for other in graph.parts_of(edge["other"]):
            p = part_p(student_id, other, at)
            if level(p) != "secure":
                continue
            node = graph.get_node(other)
            key = (edge["weight"] or 0, bool(target) and node["part_type"] == target["part_type"], p)
            if best_key is None or key > best_key:
                best_key = key
                best = {"part_id": other, "name": node["name"], "p_now": p, "note": edge["note"],
                        "weight": edge["weight"], "via": edge["other"] if other != edge["other"] else None}
    return best


def approaches(student_id: str, part_id: str) -> list[dict]:
    """Past support approaches on the part, newest first, and whether the next check went well (None: no check yet)."""
    rows = _conn().execute("SELECT approach, ts, next_check_correct FROM approach_record WHERE student_id = ? AND part_id = ? "
                           "ORDER BY ts DESC, id DESC", (student_id, graph.canonical(part_id)))
    return [dict(r) for r in rows]


# --- reading sessions ------------------------------------------------------


def _session_evidence(conn: sqlite3.Connection, student_id: str, start: str, until: str) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT l.id, l.ts, l.part_id, l.evidence_type, l.point_id, l.score, d.surprise, d.weight, d.fatigued, d.rapid
           FROM evidence_log l
           JOIN evidence_derived d ON d.evidence_id = l.id
           WHERE l.student_id = ? AND l.ts >= ? AND l.ts <= ? ORDER BY l.ts, l.id""",
        (student_id, start, until)).fetchall()


def stuck_parts(rows: list) -> list[dict]:
    """Parts the student keeps failing in the session: repeated failure, not tiredness. Intuition and other
    prequestion evidence never count. On 0/1 MCQ checks (mcq_check, ail_how), a part is stuck when the same point is
    missed on its check and again on the re-check after its reteach (a part with no score points has one point:
    itself). On open answers, it is stuck after at least session.stuck_attempts of them, with a mean score below
    session.stuck_below and a latest score no better than the first."""
    s = _settings()
    correct_share = s.bkt.correct_share
    open_scores: dict[str, list[float]] = {}
    last_on_point: dict[tuple[str, str], float] = {}
    missed_twice: dict[str, list[float]] = {}
    order: list[str] = []
    for r in rows:
        if r["evidence_type"] == "prequestion" or r["weight"] <= 0:
            continue
        part = r["part_id"]
        if r["evidence_type"] in ("mcq_check", "ail_how"):
            key = (part, r["point_id"] or part)
            if key in last_on_point and last_on_point[key] < correct_share and r["score"] < correct_share:
                missed_twice.setdefault(part, [last_on_point[key], r["score"]])
            last_on_point[key] = r["score"]
        else:
            open_scores.setdefault(part, []).append(r["score"])
        if part not in order:
            order.append(part)
    stuck = []
    for part in order:
        scores = missed_twice.get(part)
        if scores is None:
            opened = open_scores.get(part, [])
            if (len(opened) >= s.session.stuck_attempts and sum(opened) / len(opened) < s.session.stuck_below
                    and opened[-1] <= opened[0]):
                scores = opened
        if scores:
            node = graph.get_node(part)
            stuck.append({"part_id": part, "name": node["name"] if node else part, "attempts": len(scores),
                          "mean_score": sum(scores) / len(scores)})
    return stuck


def session_state(student_id: str, at: str | datetime | None = None) -> dict | None:
    """The student's current session as of at (default now), or None if the last event is more than
    session.gap_minutes ago. Long-session or rushing mode ("fatigued") starts at fatigue.mode_minutes into the session
    or at its fatigue.rapid_guesses-th rapid guess, whichever comes first (time on task and answer speed, never how
    well they answer); stuck parts and the supporting signals ("just show me" and surface shares over the last
    session.signal_window exchanges) are read here."""
    s, conn = _settings().session, _conn()
    at_ts = _event_ts(at)
    times = _event_times(conn, student_id, at_ts)
    if not times or (parse_ts(at_ts) - parse_ts(times[0])).total_seconds() / 60 > s.gap_minutes:
        return None
    start = session_start(conn, student_id, times[0])
    rows = _session_evidence(conn, student_id, start, at_ts)
    exchanges = conn.execute(
        """SELECT question_depth, offloading, choice_taken FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
           ORDER BY ts DESC, id DESC LIMIT ?""", (student_id, start, at_ts, s.signal_window)).fetchall()

    def minutes(ts: str) -> float:
        return (parse_ts(ts) - parse_ts(start)).total_seconds() / 60

    f = _settings().fatigue
    rapid_at = [minutes(r["ts"]) for r in rows if r["rapid"]]
    by_rapid = rapid_at[f.rapid_guesses - 1] if len(rapid_at) >= f.rapid_guesses else None
    by_time = f.mode_minutes if minutes(at_ts) >= f.mode_minutes else None
    since = min((m for m in (by_time, by_rapid) if m is not None), default=None)
    return {
        "session_id": start,
        "minutes": minutes(at_ts),
        "n_evidence": len(rows),
        "rapid_guesses": len(rapid_at),
        "fatigued": since is not None,
        "fatigued_since_minute": since,
        "fatigue_reason": None if since is None else ("rushing" if by_rapid is not None and by_rapid <= (by_time or by_rapid) else "long_session"),
        "stuck_parts": stuck_parts(rows),
        "just_show_me_share": (sum(1 for e in exchanges if e["offloading"] or e["choice_taken"] == "just_show_me")
                               / len(exchanges)) if exchanges else None,
        "surface_share": sum(1 for e in exchanges if e["question_depth"] == "surface") / len(exchanges) if exchanges else None,
    }


def session_parts(student_id: str, at: str | datetime | None = None) -> list[str]:
    """The course parts the student worked on this session (answered, or asked about), in the order they first
    came up. AI-literacy parts are left out. Empty with no session. For the summary when they stop."""
    conn, at_ts = _conn(), _event_ts(at)
    state = session_state(student_id, at_ts)
    if state is None:
        return []
    start = state["session_id"]
    found: dict[str, None] = {}
    rows = conn.execute("""SELECT ts, node_ids AS ids FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
                           UNION ALL SELECT ts, part_id FROM evidence_log WHERE student_id = ? AND ts >= ? AND ts <= ?
                           ORDER BY ts""", (student_id, start, at_ts, student_id, start, at_ts)).fetchall()
    for row in rows:
        for node in split(row["ids"]):
            node = graph.canonical(node)
            if not graph.is_literacy(node) and (graph.get_node(node) or {}).get("level") == "part":
                found.setdefault(node)
    return list(found)


def next_review(student_id: str) -> dict | None:
    """The student's next review, {part_id, due} (due may be in the past), or None. AI-literacy parts are left out."""
    for row in _conn().execute("SELECT part_id, due FROM review_queue WHERE student_id = ? ORDER BY due", (student_id,)):
        if not graph.is_literacy(row["part_id"]):
            return {"part_id": row["part_id"], "due": row["due"]}
    return None


def passive_streak(student_id: str, at: str | datetime | None = None) -> int:
    """How many of the student's latest messages in the current session were labelled passive, in a row, up to
    engagement.passive_run (engagement-rules). Read from exchange_log, never stored."""
    limit, conn, at_ts = _settings().engagement.passive_run, _conn(), _event_ts(at)
    start = session_start(conn, student_id, at_ts)
    rows = conn.execute("""SELECT engagement FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
                           ORDER BY ts DESC, id DESC LIMIT ?""", (student_id, start, at_ts, limit)).fetchall()
    run = 0
    for row in rows:
        if row["engagement"] != "passive":
            break
        run += 1
    return run


def coasting_share(student_id: str, at: str | datetime | None = None) -> float | None:
    """The share of the student's last session.signal_window messages this session that were passive or asked to
    be shown ("just show me", or labelled offloading), or None with fewer than engagement.coasting_min_messages
    messages, so one passive first message is not coasting (engagement-rules)."""
    conn, at_ts = _conn(), _event_ts(at)
    start = session_start(conn, student_id, at_ts)
    rows = conn.execute("""SELECT engagement, offloading, choice_taken FROM exchange_log WHERE student_id = ? AND ts >= ?
                           AND ts <= ? ORDER BY ts DESC, id DESC LIMIT ?""",
                        (student_id, start, at_ts, _settings().session.signal_window)).fetchall()
    if len(rows) < _settings().engagement.coasting_min_messages:
        return None
    return sum(1 for r in rows if r["engagement"] == "passive" or r["offloading"] or r["choice_taken"] == "just_show_me") / len(rows)


def weakest_point(student_id: str, part_id: str, point_ids: list[str]) -> str:
    """The point the student has done worst on: the lowest mean score of each point's last engagement.weakest_last_n
    pieces of evidence (point_id), so early misses that were later put right don't count; a point never asked
    counts as 0.5; the earlier point on a tie."""
    last_n = _settings().engagement.weakest_last_n
    rows = _conn().execute("SELECT point_id, score FROM evidence_log WHERE student_id = ? AND part_id = ? "
                           "AND point_id IS NOT NULL ORDER BY ts DESC, id DESC",
                           (student_id, graph.canonical(part_id))).fetchall()
    recent: dict[str, list[float]] = {}
    for r in rows:   # newest first: keep each point's last weakest_last_n scores
        if len(recent.setdefault(r["point_id"], [])) < last_n:
            recent[r["point_id"]].append(r["score"])
    means = {p: sum(v) / len(v) for p, v in recent.items()}
    return min(point_ids, key=lambda p: (means.get(p, 0.5), point_ids.index(p)))


def shows_this_session(student_id: str, part_id: str, at: str | datetime | None = None) -> int:
    """How many messages this session asked to be shown the part ("just show me", or labelled offloading),
    including one at at itself (engagement-rules)."""
    conn, at_ts = _conn(), _event_ts(at)
    start = session_start(conn, student_id, at_ts)
    rows = conn.execute("""SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
                           AND (offloading = 1 OR choice_taken = 'just_show_me')""", (student_id, start, at_ts))
    return sum(1 for r in rows if part_id in _tagged_parts(split(r["node_ids"])))


def sessions(student_id: str) -> list[dict]:
    """The student's sessions, oldest first: start, minutes, exchange and evidence counts, and the minute fatigue began."""
    s, conn = _settings().session, _conn()
    events = conn.execute(
        """SELECT ts, 0 AS kind FROM exchange_log WHERE student_id = ?
           UNION ALL SELECT ts, 1 AS kind FROM evidence_log WHERE student_id = ? ORDER BY ts, kind""",
        (student_id, student_id)).fetchall()
    found: list[dict] = []
    for e in events:
        t = parse_ts(e["ts"])
        if not found or (t - parse_ts(found[-1]["end"])).total_seconds() / 60 > s.gap_minutes:
            found.append({"session_id": e["ts"], "end": e["ts"], "n_exchanges": 0, "n_evidence": 0})
        found[-1]["end"] = e["ts"]
        found[-1]["n_exchanges" if e["kind"] == 0 else "n_evidence"] += 1
    for session in found:
        start = parse_ts(session["session_id"])
        session["minutes"] = (parse_ts(session["end"]) - start).total_seconds() / 60
        onset = conn.execute(
            """SELECT min(l.ts) FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id
               WHERE d.student_id = ? AND d.session_id = ? AND d.fatigued = 1""",
            (student_id, session["session_id"])).fetchone()[0]
        session["fatigue_onset_minute"] = (parse_ts(onset) - start).total_seconds() / 60 if onset else None
    return found


def misconception_link_signal(from_id: str, to_id: str) -> float:
    """Cross-student strength (0–1) of a link: how often a misconception about one end makes students fail the other.

    Combined with edge_weight.weight at read time using link_weight.w_misconception. Returns 0 until there is
    enough wrong evidence with misconception ids across students (see steps/later.md).
    """
    return 0.0


DERIVED_TABLES = ("part_state", "student_misconception", "approach_record", "review_queue", "evidence_derived",
                  "learner_offset_cache")


def rebuild_state(student_id: str) -> int:
    """Delete the student's derived rows and replay their events with the current settings.

    exchange_log and evidence_log are merged in the order they are applied live: by ts, then each exchange
    followed straight away by the evidence that came with it (so two exchanges in the same second replay in
    turn), then evidence with no exchange. Returns the number of events replayed. Old ids resolve through
    id_map as they replay.
    """
    conn = _conn()
    with conn:
        for table in DERIVED_TABLES:
            conn.execute(f"DELETE FROM {table} WHERE student_id = ?", (student_id,))
        events = conn.execute(
            """SELECT ts, id AS grp, 0 AS kind, id FROM exchange_log WHERE student_id = ?
               UNION ALL SELECT ts, COALESCE(exchange_id, 9223372036854775807) AS grp, 1 AS kind, id
                 FROM evidence_log WHERE student_id = ?
               ORDER BY ts, grp, kind, id""",
            (student_id, student_id)).fetchall()
        for event in events:
            if event["kind"] == 0:
                apply_exchange(get_event(event["id"]))
            else:
                apply_evidence_event(get_evidence(event["id"]))
    return len(events)


def rebuild_all() -> dict[str, int]:
    """rebuild_state for every student; returns events replayed per student."""
    return {r["id"]: rebuild_state(r["id"]) for r in _conn().execute("SELECT id FROM student ORDER BY id").fetchall()}


# --- background worker -----------------------------------------------------

_queue: queue.Queue[tuple[int | None, list[int]]] = queue.Queue()
_worker: threading.Thread | None = None
_worker_lock = threading.Lock()


def _work() -> None:
    while True:
        job = _queue.get()
        try:
            apply_job(job)
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
    """Block until every queued job has been applied."""
    _queue.join()
