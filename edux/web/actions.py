"""What a teacher can change from the web page: set a test or assignment for their class, mark what has been taught, and
remove a test they set. The same operations as the command line (`assessment add`, `coverage set`), with the same
validation, plus a line in the audit trail. Every function returns (ok, message) or (ok, None) and never raises for bad
input: the page shows the message."""

from __future__ import annotations

from datetime import date

from edux import graph, learner, service, teachers


def set_assessment(teacher_id: str, class_id: str, payload: dict) -> tuple[bool, str | None]:
    """Add a test or assignment for the whole class. payload: name, kind, date (YYYY-MM-DD, in the future), topics."""
    checked = service._check_assessment(
        {"name": payload.get("name"), "kind": payload.get("kind"), "date": payload.get("date"), "topics": payload.get("topics") or []}
    )
    if not checked["ok"]:
        return False, checked["error"]
    learner.add_class_assessment(class_id, checked["name"], checked["kind"], checked["date"], checked["part_ids"])
    teachers.log_action(
        teacher_id, class_id, "added a test", f"{checked['name']} ({checked['kind'].replace('_', ' ')}) on {checked['date']}"
    )
    return True, None


def remove_assessment(teacher_id: str, class_id: str, assessment_id: object) -> tuple[bool, str | None]:
    if not isinstance(assessment_id, int) or isinstance(assessment_id, bool):
        return False, "assessment id must be a number"
    row = learner._conn().execute("SELECT name FROM student_assessment WHERE id = ? AND class_id = ?", (assessment_id, class_id)).fetchone()
    if row is None or not learner.remove_class_assessment(class_id, assessment_id):
        return False, "no such test for this class"
    teachers.log_action(teacher_id, class_id, "removed a test", row["name"])
    return True, None


def set_coverage(teacher_id: str, class_id: str, payload: dict) -> tuple[bool, str | None]:
    """Mark sections as taught. payload: sections (ids, spec codes or names), taught_on (YYYY-MM-DD, today or earlier)."""
    keys = [str(k) for k in payload.get("sections") or [] if str(k).strip()]
    matched, unmatched = graph.match_sections(keys)
    if unmatched or not matched:
        return False, "no match for: " + ", ".join(unmatched or keys or ["nothing chosen"])
    today = learner.parse_ts(learner.now_iso()).date()
    try:
        day = date.fromisoformat(str(payload.get("taught_on") or today.isoformat()).strip())
    except ValueError:
        return False, "taught_on must be a date like 2026-11-19"
    if day > today:
        return False, "a section cannot have been taught in the future"
    learner.set_class_coverage(class_id, [n["id"] for n in matched], day.isoformat(), "web")
    teachers.log_action(teacher_id, class_id, "marked as taught", ", ".join(n["name"] for n in matched) + f" on {day.isoformat()}")
    return True, None
