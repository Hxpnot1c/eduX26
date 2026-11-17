"""Demo students, built by replaying scripted events against whichever course pack is loaded.

Parts are picked by role (target, prereq, misconception, anchor, confusable, review_parts, showme_parts) with
deterministic rules, so the same script works on example-mini and on a real pack. Every event goes through
learner.record_exchange / record_evidence, timestamped back from now, so state is derived exactly as in use.
These are demo fixtures, not teaching rules: the numbers here only shape the demo histories.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from edux import graph, learner

STUDENTS = {"demo-secure": "Demo: mostly secure", "demo-weak": "Demo: weak prerequisite", "demo-showme": "Demo: just show me"}
EXAM_IN_DAYS = 150
ROLES = ("target", "prereq", "misconception", "anchor", "confusable", "review_parts", "showme_parts")


class DemoError(ValueError):
    """The demo can't be seeded (no parts, a bad --parts override, students already exist)."""


# --- picking parts by role ---------------------------------------------------


def _ranked(parts: list[str]) -> list[str]:
    """Most important first; ties keep pack order."""
    order = {p: i for i, p in enumerate(learner.all_parts())}
    return sorted(parts, key=lambda p: (-graph.weight(p)["importance"], order.get(p, 0)))


def _linked_parts(part: str, lookup: Callable[[str], list[dict]], same_type: bool = False) -> list[str]:
    """Parts at the far end of the part's edges, strongest link first (then the same part type, if asked)."""
    order = {p: i for i, p in enumerate(learner.all_parts())}
    part_type = graph.get_node(part)["part_type"]
    found: dict[str, tuple] = {}
    for edge in lookup(part):
        for other in graph.parts_of(edge["other"]):
            if other == part:
                continue
            key = (-(edge["weight"] or 0.0), not (same_type and graph.get_node(other)["part_type"] == part_type), order.get(other, 0))
            found[other] = min(found.get(other, key), key)
    return sorted(found, key=lambda p: found[p])


def near_target(target: str) -> set[str]:
    """The target and the parts that depend on it. Evidence on a dependent passes a prerequisite boost to the
    target, so students meant to leave the target untouched get no evidence on any of these."""
    return {target} | {p for edge in graph.dependents(target, 1) for p in graph.parts_of(edge["other"])}


def _prereq_parts(part: str) -> list[str]:
    return _linked_parts(part, lambda p: graph.prerequisites(p, 1))


def _parse_overrides(text: str | None) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for item in (text or "").split(","):
        if not item.strip():
            continue
        role, _, value = item.partition("=")
        role, value = role.strip(), value.strip()
        if role not in ROLES:
            raise DemoError(f"unknown role {role!r}; one of {', '.join(ROLES)}")
        if not value:
            raise DemoError(f"--parts {role}= needs an id")
        overrides[role] = value
    return overrides


def _check_part(role: str, value: str) -> str:
    node = graph.get_node(graph.canonical(value))
    if node is None or node["level"] != "part":
        raise DemoError(f"--parts {role}={value}: not a part in the loaded pack")
    return node["id"]


def pick_roles(overrides: str | None = None) -> tuple[dict, list[str]]:
    """Choose the parts for each role from the loaded pack. Returns (roles, warnings).

    review_parts and showme_parts take ;-separated ids in --parts. The misconception override is a misconception id.
    """
    parts = learner.all_parts()
    if not parts:
        raise DemoError("the loaded pack has no parts; load a pack first")
    given = _parse_overrides(overrides)
    min_distractors = learner._settings().prequestion.min_distractors
    warnings: list[str] = []
    roles: dict = {}

    def misconceptions(part: str) -> list[dict]:
        return graph.misconceptions_for([part])

    # target
    if "target" in given:
        roles["target"] = _check_part("target", given["target"])
    else:
        with_prereq = [p for p in _ranked(parts) if _prereq_parts(p)]
        best = [p for p in with_prereq if len(misconceptions(p)) >= min_distractors]
        if best:
            roles["target"] = best[0]
        elif [p for p in with_prereq if misconceptions(p)]:
            roles["target"] = [p for p in with_prereq if misconceptions(p)][0]
            warnings.append(f"no part with a prerequisite has {min_distractors}+ misconceptions: no pre-question for the target")
        elif with_prereq:
            roles["target"] = with_prereq[0]
            warnings.append("no part with a prerequisite has a misconception: no pre-question or misconception correction")
        else:
            roles["target"] = _ranked(parts)[0]
            warnings.append("no part has a prerequisite: demo-weak shows no weak prerequisite")
    target = roles["target"]
    if len(misconceptions(target)) < min_distractors and "target" in given:
        warnings.append(f"{target} has fewer than {min_distractors} misconceptions: no pre-question")

    # prereq
    if "prereq" in given:
        roles["prereq"] = _check_part("prereq", given["prereq"])
    else:
        found = _prereq_parts(target)
        roles["prereq"] = found[0] if found else None
        if not found and not any("prerequisite" in w for w in warnings):
            warnings.append(f"{target} has no prerequisite part: demo-weak shows no weak prerequisite")

    # misconception: examiner-report source first, otherwise the first
    target_misconceptions = misconceptions(target)
    if "misconception" in given:
        wanted = graph.canonical(given["misconception"])
        if wanted not in {m["id"] for m in target_misconceptions}:
            raise DemoError(f"--parts misconception={given['misconception']}: not a misconception on {target}")
        roles["misconception"] = wanted
    elif target_misconceptions:
        target_misconceptions.sort(key=lambda m: "examiner_report" not in graph.source_types(m["source_ids"]))
        roles["misconception"] = target_misconceptions[0]["id"]
    else:
        roles["misconception"] = None

    # anchor and confusable
    for role, lookup, same_type in (("anchor", graph.analogous, True), ("confusable", graph.confusables, False)):
        if role in given:
            roles[role] = _check_part(role, given[role])
        else:
            found = _linked_parts(target, lookup, same_type)
            roles[role] = found[0] if found else None
            if not found:
                warnings.append(f"{target} has no {'analogous' if role == 'anchor' else 'confusable'} part: no {role} in the demo")

    # review_parts and showme_parts
    near = near_target(target)
    for role, exclude, n in (("review_parts", near | {roles["prereq"], roles["anchor"]}, 3), ("showme_parts", {target}, 2)):
        if role in given:
            roles[role] = [_check_part(role, v) for v in given[role].split(";") if v.strip()]
        else:
            roles[role] = [p for p in _ranked(parts) if p not in exclude][:n]
            if len(roles[role]) < n:
                warnings.append(f"only {len(roles[role])} part(s) available for {role} (wanted {n})")
    return roles, warnings


# --- scripted histories --------------------------------------------------------


class _Clock:
    """Timestamps counted back from one fixed 'now', so a whole seed run shares the same reference."""

    def __init__(self) -> None:
        self.now = datetime.now(timezone.utc).replace(microsecond=0)

    def ago(self, days: float = 0, minutes: float = 0) -> str:
        return (self.now - timedelta(days=days, minutes=minutes)).isoformat()

    def session(self, days_ago: float, minute: float) -> str:
        """A time within a session that started days_ago days ago at 16:00 UTC."""
        start = (self.now - timedelta(days=days_ago)).replace(hour=16, minute=0, second=0)
        return (start + timedelta(minutes=minute)).isoformat()


_pending: list[tuple[str, int, int, Callable[[], object]]] = []


def _exchange(sid: str, nodes: list[str], ts: str, depth: str = "mechanism", engagement: str = "active",
              support: str | None = None, choice: str | None = None, offloading: bool = False,
              misconceptions: list[str] | None = None) -> None:
    _pending.append((ts, 0, len(_pending), lambda: learner.record_exchange(
        sid, nodes, depth, engagement, offloading, support, choice, misconceptions, client="demo", ts=ts, apply="now")))


def _evidence(sid: str, part: str, kind: str, score: float, ts: str, misconceptions: list[str] | None = None) -> None:
    _pending.append((ts, 1, len(_pending), lambda: learner.record_evidence(
        sid, part, kind, score, misconceptions, ts=ts, apply="now")))


def _flush() -> None:
    """Record the queued events in time order (exchanges before evidence at the same moment), the order a
    rebuild replays them in, so seeding and rebuilding give the same state."""
    for *_, record in sorted(_pending, key=lambda e: e[:3]):
        record()
    _pending.clear()


def _seed_secure(sid: str, roles: dict, clock: _Clock) -> None:
    """Spaced correct answers on every part except the target: most parts secure now (prereq and anchor
    included), with the review parts last answered long enough ago to be due: the first one only once (weak,
    recall), the others several times (developing, transfer)."""
    review = roles["review_parts"]
    secure = [p for p in learner.all_parts() if p not in near_target(roles["target"]) and p not in review]
    for part in secure:
        for days in (40, 30, 20, 10, 3):
            _exchange(sid, [part], clock.ago(days=days, minutes=10), support="hint", choice="try_first")
            _evidence(sid, part, "past_question", 1.0, clock.ago(days=days))
    for i, part in enumerate(review):
        history = (60,) if i == 0 else (110, 95, 82, 70, 60)
        for days in history:
            _exchange(sid, [part], clock.ago(days=days, minutes=10), choice="try_first")
            _evidence(sid, part, "explain_back", 1.0, clock.ago(days=days))


def _seed_weak(sid: str, roles: dict, clock: _Clock) -> None:
    """Two days ago: taught the prerequisite and got it wrong, then got the target wrong with its misconception."""
    target, prereq, misconception = roles["target"], roles["prereq"], roles["misconception"]
    misconceptions = [misconception] if misconception else None
    if prereq:
        _exchange(sid, [prereq], clock.ago(days=2, minutes=120), depth="surface", support="worked_example", choice="try_first")
        _evidence(sid, prereq, "explain_back", 0.2, clock.ago(days=2, minutes=80))
    _exchange(sid, [target], clock.ago(days=2, minutes=60), support="hint", choice="try_first", misconceptions=misconceptions)
    _evidence(sid, target, "explain_back", 0.25, clock.ago(days=2, minutes=20), misconceptions)


def _seed_showme(sid: str, roles: dict, clock: _Clock) -> None:
    """Earlier sessions with their own reasoning; then three ~50-minute sessions (9, 6 and 3 days ago) with
    frequent "just show me", where answers start well and drop on previously correct parts from about minute 35."""
    showme = roles["showme_parts"]
    near = near_target(roles["target"])
    known = [p for p in _ranked(learner.all_parts()) if p not in near and p not in showme][:3]
    known = known or [p for p in _ranked(learner.all_parts()) if p not in near][:3]
    for days in (25, 20):
        for part in known:
            _exchange(sid, [part], clock.session(days, 5), depth="mechanism", engagement="constructive", choice="try_first")
            _evidence(sid, part, "past_question", 1.0, clock.session(days, 15))
    for days in (9, 6, 3):
        for minute, part in ((2, showme[0]), (24, showme[-1]), (47, showme[0])):
            _exchange(sid, [part], clock.session(days, minute), depth="surface", engagement="passive",
                      support="worked_example", choice="just_show_me", offloading=True)
        early = [known[i % len(known)] for i in range(4)]
        for minute, part in zip((5, 10, 15, 20), early):
            _evidence(sid, part, "past_question", 1.0, clock.session(days, minute))
        late = [known[i % len(known)] for i in range(1, 5)]
        for minute, part in zip((29, 33, 37, 41), late):
            _evidence(sid, part, "past_question", 0.0, clock.session(days, minute))


SEEDS = {"demo-secure": _seed_secure, "demo-weak": _seed_weak, "demo-showme": _seed_showme}


# --- seeding -------------------------------------------------------------------


def _course(course: str | None) -> str:
    rows = [r["id"] for r in learner._conn().execute("SELECT id FROM content.course ORDER BY id")]
    if course:
        if course not in rows:
            raise DemoError(f"unknown course {course!r}; loaded: {', '.join(rows) or 'none'}")
        return course
    if len(rows) != 1:
        raise DemoError(f"pass --course; loaded courses: {', '.join(rows) or 'none'}")
    return rows[0]


def remove_students() -> dict[str, str]:
    """Delete the demo students, their events and derived state. Returns the keys they had, by id."""
    conn = learner._conn()
    keys = {sid: s["key"] for sid in STUDENTS if (s := learner.get_student(sid))}
    ids = list(keys)
    with conn:
        for sid in ids:
            for table in ("exchange_log", "evidence_log", "student_profile", *learner.DERIVED_TABLES):
                conn.execute(f"DELETE FROM {table} WHERE student_id = ?", (sid,))
            conn.execute("DELETE FROM student WHERE id = ?", (sid,))
    return keys


def seed(course: str | None = None, reset: bool = False, overrides: str | None = None) -> dict:
    """Create the three demo students. Returns {"course", "roles", "warnings", "students": {id: key}}.
    With reset, existing demo students are removed and recreated with the same keys."""
    from edux import service

    course_id = _course(course)
    roles, warnings = pick_roles(overrides)
    existing = [sid for sid in STUDENTS if learner.get_student(sid)]
    if existing and not reset:
        raise DemoError(f"demo students already exist ({', '.join(existing)}); use --reset to recreate them")
    old_keys = remove_students() if reset else {}
    clock = _Clock()
    exam = (clock.now + timedelta(days=EXAM_IN_DAYS)).date().isoformat()
    keys = {}
    for sid, name in STUDENTS.items():
        keys[sid] = learner.add_student(name, course_id, student_id=sid)["key"]
        if sid in old_keys:   # --reset keeps each demo student's key, so connector URLs keep working
            with learner._conn() as conn:
                conn.execute("UPDATE student SET key = ? WHERE id = ?", (old_keys[sid], sid))
            keys[sid] = old_keys[sid]
        service.update_profile(learner.get_student(sid), exam_date_override=exam)
        SEEDS[sid](sid, roles, clock)
        _flush()
    return {"course": course_id, "roles": roles, "warnings": warnings, "students": keys}
