"""Learner model: append-only events, scoring rules and state rebuilt from events.

part_state, student_misconception, approach_record and review_queue are derived:
rebuild_state replays a student's events (exchange_log and evidence_log) through the current rules in settings.toml.
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


def _event_ts(ts: str | datetime | None) -> str:
    """An event timestamp: ISO, UTC, to the second (so stored timestamps compare correctly as text)."""
    return parse_ts(ts).astimezone(timezone.utc).isoformat(timespec="seconds") if ts else now_iso()


def _evidence_rows(evidence: list[dict]) -> list[tuple[str, str, float, list[str]]]:
    """Validate evidence items and expand concept ids to their parts: (part_id, type, score, misconception_ids)."""
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
        rows += [(part, item["type"], score, list(item.get("misconception_ids") or [])) for part in parts]
    return rows


def _write_evidence(conn: sqlite3.Connection, student: dict, ts: str, rows: list, origin: str,
                    exchange_id: int | None = None, check_id: str | None = None) -> list[int]:
    s = _settings()
    ids = []
    for part_id, evidence_type, score, misconception_ids in rows:
        cur = conn.execute(
            """INSERT INTO evidence_log (student_id, ts, part_id, evidence_type, score, origin, exchange_id, check_id,
                 misconception_ids, protocol, settings_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student["id"], ts, part_id, evidence_type, score, origin, exchange_id, check_id, ";".join(misconception_ids),
             protocol_label(s, profile_of(student)), settings_hash()))
        ids.append(cur.lastrowid)
    return ids


def _dispatch(job: tuple[int | None, list[int]], apply: str) -> None:
    if apply == "now":
        apply_job(job)
    elif apply == "background":
        start_worker()
        _queue.put(job)


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
) -> int:
    """Write an exchange event, and any evidence that came with it, then apply them; return the exchange id.

    evidence is a list of {part_id, type, score, misconception_ids?}: what the student produced in this turn,
    scored 0–1. Concept ids expand to their parts with the score unchanged. All rows share the exchange's ts.
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
    evidence_rows = _evidence_rows(evidence or [])
    store_prompt = os.environ.get("STORE_PROMPTS", "0") == "1"
    ts = _event_ts(ts)
    conn = _conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO exchange_log (student_id, ts, client, node_ids, question_depth, engagement, offloading,
                 support_given, choice_taken, misconception_ids, conflict_flagged, protocol, settings_hash, prompt_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, ts, client, ";".join(node_ids), question_depth, engagement, int(offloading), support_given,
             choice_taken, ";".join(misconception_ids or []), int(conflict_flagged), protocol_label(s, profile_of(student)),
             settings_hash(), prompt_text if store_prompt else None),
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
) -> list[int]:
    """Write evidence with no exchange (demo seeding, checks), then apply it; return the evidence ids (one per part)."""
    student = get_student(student_id)
    if student is None:
        raise ValueError(f"unknown student {student_id!r}")
    if origin not in ("chat", "check"):
        raise ValueError("origin must be chat or check")
    rows = _evidence_rows([{"part_id": part_id, "type": evidence_type, "score": score, "misconception_ids": misconception_ids}])
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


def apply_evidence_event(event: dict) -> None:
    """Apply one evidence event: score -> correct, the immediate-recall discount for chat evidence,
    surprise against the model's expectation (stored in evidence_derived), misconception activation
    on wrong evidence, then the BKT update (_apply_evidence)."""
    s, conn = _settings(), _conn()
    student_id, ts = event["student_id"], event["ts"]
    node = graph.get_node(event["part_id"])
    if node is None or node["level"] != "part":
        return
    part_id = node["id"]
    correct = event["score"] >= s.bkt.correct_share
    evidence_type = event["evidence_type"]
    if event["origin"] == "chat" and _recently_taught(conn, student_id, part_id, ts):
        evidence_type = "immediate"
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)
    weight = 1.0
    surprise = weight * (event["score"] - p_before)
    conn.execute(
        """INSERT OR REPLACE INTO evidence_derived (evidence_id, student_id, session_id, p_before, surprise, weight, fatigued)
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (event["id"], student_id, session_start(conn, student_id, ts), p_before, surprise, weight))
    if not correct:
        _activate_misconceptions(conn, student_id, split(event.get("misconception_ids")), ts)
    _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts)


def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, evidence_type: str, correct: bool, ts: str) -> None:
    s = _settings()
    if evidence_type not in s.bkt.evidence:
        raise ValueError(f"evidence_type must be one of {', '.join(s.bkt.evidence)}")
    node = graph.get_node(part_id)
    if node is None or node["level"] != "part":
        raise ValueError(f"{part_id!r} is not a part")
    part_id, t = node["id"], parse_ts(ts)
    ts = t.isoformat(timespec="seconds")

    state = _load_state(conn, student_id, part_id, ts)
    before = _p_at(state, ts)
    slip, guess = s.bkt.evidence[evidence_type].slip, s.bkt.evidence[evidence_type].guess
    if state["offload_left"] > 0:
        guess = s.offloading.guess_after
        state["offload_left"] -= 1
    if correct:
        p = before * (1 - slip) / (before * (1 - slip) + (1 - before) * guess)
    else:
        p = before * slip / (before * slip + (1 - before) * (1 - guess))
    p += (1 - p) * s.bkt.learn_rate

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
    gap = max(s.scheduling.min_gap_days, review_gap_days(student_id, part_id, t))
    _queue_review(conn, student_id, part_id, t + timedelta(days=gap), "scheduled", replace=True)


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
    """Parts due for review by at (default now), most important first, then the most overdue."""
    at_dt = parse_ts(at or now_iso())
    due = []
    for row in _conn().execute("SELECT part_id, due, reason FROM review_queue WHERE student_id = ?", (student_id,)):
        node = graph.get_node(row["part_id"])
        if node and parse_ts(row["due"]) <= at_dt:
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


def misconception_link_signal(from_id: str, to_id: str) -> float:
    """Cross-student strength (0–1) of a link: how often a misconception about one end makes students fail the other.

    Combined with edge_weight.weight at read time using link_weight.w_misconception. Returns 0 until there is
    enough wrong evidence with misconception ids across students (see steps/later.md).
    """
    return 0.0


DERIVED_TABLES = ("part_state", "student_misconception", "approach_record", "review_queue", "evidence_derived")


def rebuild_state(student_id: str) -> int:
    """Delete the student's derived rows and replay their events with the current settings.

    exchange_log and evidence_log are merged in order of (ts, exchanges before evidence, id), the order in which
    they are applied live. Returns the number of events replayed. Old ids resolve through id_map as they replay.
    """
    conn = _conn()
    with conn:
        for table in DERIVED_TABLES:
            conn.execute(f"DELETE FROM {table} WHERE student_id = ?", (student_id,))
        events = conn.execute(
            """SELECT ts, 0 AS kind, id FROM exchange_log WHERE student_id = ?
               UNION ALL SELECT ts, 1 AS kind, id FROM evidence_log WHERE student_id = ?
               ORDER BY ts, kind, id""",
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
