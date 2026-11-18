"""Learner model: append-only events, scoring rules and state rebuilt from events.

part_state, student_misconception, approach_record and review_queue are derived:
rebuild_state replays a student's events (exchange_log and evidence_log) through the current rules in settings.toml.
Every rule runs at the event's own timestamp, so replaying gives the same state.
"""

from __future__ import annotations

import functools
import math
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
CHOICE_TAKEN = ("try_first", "hint", "just_show_me", "skip_point", "none")   # skip_point: "I know this" (step 05d)
# What a student's answer can be to, as sent by the chatbot; each is also a key of [bkt.evidence].
# "mcq" is any server-built multiple-choice question (step 05d), scored from the letter picked.
ANSWER_TYPES = ("prequestion", "mcq", "explain_back", "review", "extend", "past_question", "ail_task", "ail_unprompted")
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


def add_student(display_name: str, course_id: str, profile: str | None = None, student_id: str | None = None) -> dict:
    """Create a student with a secret key and an empty profile; returns {"id", "key"}.
    student_id fixes the id (used for demo students); by default it is made from the name."""
    conn = _conn()
    if not conn.execute("SELECT 1 FROM content.course WHERE id = ?", (course_id,)).fetchone():
        raise ValueError(f"unknown course {course_id!r}; load its pack first")
    if profile is not None and profile not in _context().profiles:
        raise ValueError(f"unknown context profile {profile!r}")
    slug = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-") or "student"
    student_id, key = student_id or f"{slug}-{secrets.token_hex(2)}", secrets.token_urlsafe(16)
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


def question_evidence(features: list[str] | None) -> dict:
    """Ask evidence for a research question (step 05e): ail_question on ail_ask, scored by the question features
    it shows out of the four."""
    shown = {f for f in features or [] if f in QUESTION_FEATURES}
    return {"part_id": AIL_ASK, "type": "ail_question", "score": len(shown) / len(QUESTION_FEATURES), "misconception_ids": []}


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
    prompt_text: str | None = None,
    client: str | None = None,
    ts: str | None = None,
    evidence: list[dict] | None = None,
    apply: str = "background",
    request: dict | None = None,
) -> int:
    """Write an exchange event, and any evidence that came with it, then apply them; return the exchange id.

    evidence is a list of {part_id, type, score, misconception_ids?}: what the student produced in this turn,
    scored 0–1. Concept ids expand to their parts with the score unchanged. All rows share the exchange's ts.
    apply is "background" (queue for the worker thread), "now" (apply before returning) or "none".
    prompt_text is stored only when STORE_PROMPTS=1. request holds the step 05e labels (request_type,
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
    store_prompt = os.environ.get("STORE_PROMPTS", "0") == "1"
    ts = _event_ts(ts)
    conn = _conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO exchange_log (student_id, ts, client, node_ids, question_depth, engagement, offloading,
                 support_given, choice_taken, misconception_ids, conflict_flagged, protocol, settings_hash, prompt_text,
                 request_type, question_features, source_conflict, web_access, asks_recent, pushback_changed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, ts, client, ";".join(node_ids), question_depth, engagement, int(offloading), support_given,
             choice_taken, ";".join(misconception_ids or []), int(conflict_flagged), protocol_label(s, profile_of(student)),
             settings_hash(), prompt_text if store_prompt else None, req["request_type"], req["question_features"],
             req["source_conflict"], req["web_access"], req["asks_recent"], req["pushback_changed"]),
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
    """Apply one exchange event: nudges, the "just show me" review, misconception activation, untested reviews,
    last_seen.

    An exchange is not evidence: it nudges p_known a little by its labels and moves the forgetting
    clock only decay.seen_refresh of the way to now. Being shown doesn't change understanding (step 05d): a
    "just show me" exchange gets no nudge and doesn't discount later evidence (the immediate-recall rule
    already lowers credit straight after being shown); it still queues a review. Old ids are resolved through id_map.
    """
    s, conn = _settings(), _conn()
    student_id, ts = event["student_id"], event["ts"]
    t = parse_ts(ts)
    multiplier = s.nudges.depth[event["question_depth"]] * s.nudges.engagement[event["engagement"]]
    offloaded = bool(event["offloading"]) or event.get("choice_taken") == "just_show_me"
    support = event.get("support_given")

    for part, strength in _tagged_parts(split(event["node_ids"])).items():
        state = _load_state(conn, student_id, part, ts)
        if not offloaded:
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


def days_to_exam(student_id: str, part_id: str, at: datetime) -> float | None:
    """Days from at to the student's next exam on this part: their exam_date_override if set and ahead,
    otherwise the soonest exam paper covering the part. None if there is no exam ahead."""
    row = _conn().execute("SELECT exam_date_override FROM student_profile WHERE student_id = ?", (student_id,)).fetchone()
    dates = [row["exam_date_override"]] if row and row["exam_date_override"] else []
    if not dates or parse_ts(dates[0]) <= at:
        dates = [paper["date"] for paper in graph.exam_papers_for(part_id) if paper["date"]]
    ahead = [(parse_ts(d) - at).total_seconds() / 86400 for d in dates]
    ahead = [d for d in ahead if d > 0]
    return min(ahead) if ahead else None


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


def _fatigued(conn: sqlite3.Connection, event: dict, part_id: str, session_id: str, surprise: float, weight: float) -> bool:
    """Whether this piece of evidence falls in the session's fatigued state.

    Once fatigued, a session stays fatigued. Otherwise fatigue starts here when the session is at least
    session.fatigue_min_minutes old, the last session.fatigue_window weighted pieces of evidence (this one
    included) have a mean surprise at or below session.fatigue_threshold, and they span at least
    session.fatigue_min_parts parts. Untaught pre-questions (weight 0) never start it.
    """
    s = _settings().session
    student_id, ts = event["student_id"], event["ts"]
    if conn.execute("SELECT 1 FROM evidence_derived WHERE student_id = ? AND session_id = ? AND fatigued = 1",
                    (student_id, session_id)).fetchone():
        return True
    if weight == 0 or (parse_ts(ts) - parse_ts(session_id)).total_seconds() / 60 < s.fatigue_min_minutes:
        return False
    earlier = conn.execute(
        """SELECT l.part_id, d.surprise FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id
           WHERE d.student_id = ? AND d.session_id = ? AND d.weight > 0 AND l.id != ? AND l.ts <= ?
           ORDER BY l.ts DESC, l.id DESC LIMIT ?""",
        (student_id, session_id, event["id"], ts, s.fatigue_window - 1)).fetchall()
    window = [(part_id, surprise)] + [(r["part_id"], r["surprise"]) for r in earlier]
    if len(window) < s.fatigue_window:
        return False
    mean = sum(x for _, x in window) / len(window)
    return mean <= s.fatigue_threshold and len({p for p, _ in window}) >= s.fatigue_min_parts


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
    slip, guess = slip_guess(evidence_type, event.get("n_options"), immediate)
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)
    expected = p_before * (1 - slip) + (1 - p_before) * guess   # chance of a correct answer under this type's slip and guess
    surprise = weight * (event["score"] - expected)
    session_id = session_start(conn, student_id, ts)
    fatigued = _fatigued(conn, event, part_id, session_id, surprise, weight)
    conn.execute(
        """INSERT OR REPLACE INTO evidence_derived (evidence_id, student_id, session_id, p_before, surprise, weight, fatigued)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (event["id"], student_id, session_id, p_before, surprise, weight, int(fatigued)))
    if not correct:
        _activate_misconceptions(conn, student_id, split(event.get("misconception_ids")), ts)
    if weight > 0:  # an untaught pre-question is diagnostic only
        slip_add = _settings().session.fatigue_slip_add if fatigued else 0.0
        _apply_evidence(conn, student_id, part_id, slip, guess, correct, ts, weight=weight, slip_add=slip_add)


def slip_guess(evidence_type: str, n_options: int | None = None, immediate: bool = False) -> tuple[float, float]:
    """Slip and guess for a piece of evidence. With bkt.mcq_guess_from_options, a multiple-choice question that
    recorded how many options it showed guesses 1 / n_options (older rows keep the type's guess). Immediate
    evidence (straight after a worked example or hint) takes immediate's slip and the larger of immediate's guess
    and the type's own, so a question with few options is never discounted less."""
    s = _settings()
    if evidence_type not in s.bkt.evidence:
        raise ValueError(f"evidence_type must be one of {', '.join(s.bkt.evidence)}")
    slip, guess = s.bkt.evidence[evidence_type].slip, s.bkt.evidence[evidence_type].guess
    if s.bkt.mcq_guess_from_options and n_options:
        guess = 1 / n_options
    if immediate:
        slip, guess = s.bkt.evidence["immediate"].slip, max(s.bkt.evidence["immediate"].guess, guess)
    return slip, guess


def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, slip: float, guess: float, correct: bool,
                    ts: str, weight: float = 1.0, slip_add: float = 0.0) -> None:
    """The BKT update on one part with the evidence's slip and guess (slip_guess); weight (0–1) scales how far
    p_known moves towards the BKT result. slip_add raises slip (capped at session.slip_cap) while the session is
    fatigued."""
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
    p += (1 - p) * s.bkt.learn_rate
    p = before + weight * (p - before)

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
                other["p_known"] = min(0.99, _p_at(other, ts) + s.propagation.prereq_boost * gain)
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
    if row is None:
        return initial_state(part_id)[0]
    return p_now(row["p_known"], row["half_life_days"], row["clock_start"], at)


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
        """SELECT l.id, l.ts, l.part_id, l.evidence_type, l.point_id, l.score, d.surprise, d.weight, d.fatigued
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
    session.gap_minutes ago. Fatigue and surprise come from evidence_derived; stuck parts and the supporting
    signals ("just show me" and surface shares over the last session.signal_window exchanges) are read here."""
    s, conn = _settings().session, _conn()
    at_ts = _event_ts(at)
    times = _event_times(conn, student_id, at_ts)
    if not times or (parse_ts(at_ts) - parse_ts(times[0])).total_seconds() / 60 > s.gap_minutes:
        return None
    start = session_start(conn, student_id, times[0])
    rows = _session_evidence(conn, student_id, start, at_ts)
    weighted = [r for r in rows if r["weight"] > 0][-s.fatigue_window:]
    onset = next((r for r in rows if r["fatigued"]), None)
    exchanges = conn.execute(
        """SELECT question_depth, offloading, choice_taken FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
           ORDER BY ts DESC, id DESC LIMIT ?""", (student_id, start, at_ts, s.signal_window)).fetchall()

    def minutes(ts: str) -> float:
        return (parse_ts(ts) - parse_ts(start)).total_seconds() / 60

    return {
        "session_id": start,
        "minutes": minutes(at_ts),
        "n_evidence": len(rows),
        "rolling_surprise": sum(r["surprise"] for r in weighted) / len(weighted) if weighted else None,
        "fatigued": onset is not None,
        "fatigued_since_minute": minutes(onset["ts"]) if onset else None,
        "stuck_parts": stuck_parts(rows),
        "just_show_me_share": (sum(1 for e in exchanges if e["offloading"] or e["choice_taken"] == "just_show_me")
                               / len(exchanges)) if exchanges else None,
        "surface_share": sum(1 for e in exchanges if e["question_depth"] == "surface") / len(exchanges) if exchanges else None,
    }


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


DERIVED_TABLES = ("part_state", "student_misconception", "approach_record", "review_queue", "evidence_derived")


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
