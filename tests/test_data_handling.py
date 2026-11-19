"""Step 05x: opaque ids, hashed keys, export, deletion and retention."""

import json
import re
from datetime import datetime, timedelta, timezone

import pytest

from edux import db, learner, service


def _count_rows_about(student_id):
    conn = learner._conn()
    total = {}
    for table in learner._student_tables(conn):
        n = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE student_id = ?", (student_id,)).fetchone()[0]
        if n:
            total[table] = n
    total_student = conn.execute("SELECT COUNT(*) FROM student WHERE id = ?", (student_id,)).fetchone()[0]
    if total_student:
        total["student"] = total_student
    return total


def _use(student, part):
    """Give a student rows in as many tables as the model writes."""
    sid = student["id"]
    learner.record_exchange(sid, [part], "transfer", "constructive", apply="now")
    learner.record_evidence(sid, part, "explain_back", 1.0, apply="now")
    service.update_profile(learner.get_student(sid), interests="football")
    service.log_call(sid, "tutor_turn", datetime.now(timezone.utc), 12.0, 800, True)
    conn = learner._conn()
    with conn:
        conn.execute("INSERT INTO issued_plan (student_id, ts, plan_json) VALUES (?, ?, '{}')", (sid, learner.now_iso()))
    learner.record_skip(sid, "ail_verify")


def test_a_new_students_id_is_opaque_and_holds_no_part_of_their_name(course):
    made = learner.add_student("Priya Patel", course)
    assert re.fullmatch(r"s-[0-9a-f]{8}", made["id"])
    assert "priya" not in made["id"].lower() and "patel" not in made["id"].lower()


def test_the_key_is_stored_only_as_a_hash(student):
    row = learner._conn().execute("SELECT key, key_hash FROM student WHERE id = ?", (student["id"],)).fetchone()
    assert row["key"] is None
    assert row["key_hash"] == learner.key_hash(student["key"]) != student["key"]
    assert learner.student_by_key(student["key"])["id"] == student["id"]
    assert learner.student_by_key("not-a-key") is None


def test_a_students_dict_never_carries_the_key_or_its_hash(student):
    for found in (learner.get_student(student["id"]), learner.student_by_key(student["key"])):
        assert "key" not in found and "key_hash" not in found


def test_a_legacy_plaintext_key_still_works_once_and_is_then_hashed(student):
    conn = learner._conn()
    with conn:
        conn.execute("UPDATE student SET key = ?, key_hash = NULL WHERE id = ?", ("legacy-key", student["id"]))
    assert learner.student_by_key("legacy-key")["id"] == student["id"]
    row = conn.execute("SELECT key, key_hash FROM student WHERE id = ?", (student["id"],)).fetchone()
    assert row["key"] is None and row["key_hash"] == learner.key_hash("legacy-key")
    assert learner.student_by_key("legacy-key")["id"] == student["id"]


def test_delete_student_leaves_no_row_about_them_in_any_table(student, part):
    _use(student, part)
    assert len(_count_rows_about(student["id"])) >= 5  # the student really has rows in many tables
    counts = learner.delete_student(student["id"])
    assert counts["student"] == 1
    assert _count_rows_about(student["id"]) == {}
    assert learner.get_student(student["id"]) is None


def test_delete_student_leaves_other_students_untouched_and_rebuild_identical(course, part):
    a, b = learner.add_student("A", course), learner.add_student("B", course)
    for s in (a, b):
        _use(s, part)
    before = [dict(r) for r in learner._conn().execute("SELECT * FROM part_state WHERE student_id = ?", (b["id"],))]
    learner.delete_student(a["id"])
    assert _count_rows_about(b["id"]) != {}
    learner.rebuild_state(b["id"])
    after = [dict(r) for r in learner._conn().execute("SELECT * FROM part_state WHERE student_id = ?", (b["id"],))]
    assert after == before


def test_delete_student_refuses_an_unknown_student(course):
    with pytest.raises(ValueError):
        learner.delete_student("nobody")


def test_export_holds_every_table_with_rows_and_never_the_key(student, part):
    _use(student, part)
    data = learner.export_student(student["id"])
    assert set(data["tables"]) >= {t for t in _count_rows_about(student["id"]) if t != "student"}
    text = json.dumps(data)
    assert student["key"] not in text and learner.key_hash(student["key"]) not in text
    assert data["student"]["id"] == student["id"]


def test_purge_deletes_old_call_log_rows_and_keeps_recent_ones(student):
    now = datetime(2026, 11, 18, tzinfo=timezone.utc)
    days = learner._settings().retention.call_log_days
    service.log_call(student["id"], "tutor_turn", now - timedelta(days=days + 1), 10.0, 100, True)
    service.log_call(student["id"], "tutor_turn", now - timedelta(days=1), 10.0, 100, True)
    done = learner.purge(now)
    assert done["call_log"] == 1
    assert learner._conn().execute("SELECT COUNT(*) FROM call_log WHERE student_id = ?", (student["id"],)).fetchone()[0] == 1


def test_purge_deletes_a_student_only_after_the_leaving_period(course, part):
    stayed, gone = learner.add_student("Stayed", course), learner.add_student("Gone", course)
    for s in (stayed, gone):
        _use(s, part)
    now = datetime(2026, 11, 18, tzinfo=timezone.utc)
    days = learner._settings().retention.after_leaving_days
    learner.leave_student(stayed["id"], (now - timedelta(days=days - 1)).date().isoformat())
    learner.leave_student(gone["id"], (now - timedelta(days=days + 1)).date().isoformat())
    done = learner.purge(now)
    assert done["students"] == [gone["id"]]
    assert _count_rows_about(gone["id"]) == {}
    assert _count_rows_about(stayed["id"]) != {}


def test_a_student_who_has_not_left_is_never_purged(student, part):
    _use(student, part)
    learner.purge(datetime(2099, 1, 1, tzinfo=timezone.utc))
    assert learner.get_student(student["id"]) is not None


def test_no_message_text_column_is_stored(course):
    columns = [c["name"] for c in learner._conn().execute("PRAGMA table_info(exchange_log)")]
    assert "prompt_text" not in columns


def test_the_migration_keeps_an_existing_students_key_working(tmp_path, monkeypatch):
    """A database from before step 05x: migrate up to 013, add a student with a plaintext key, then apply 014."""
    import shutil
    import sqlite3

    from edux import db

    old = tmp_path / "migrations_old"
    old.mkdir()
    for path in sorted(db.MIGRATIONS_DIR.glob("*.sql")):
        if int(path.name[:3]) <= 13:
            shutil.copy(path, old / path.name)
    conn = sqlite3.connect(tmp_path / "old.db")
    conn.row_factory = sqlite3.Row
    db.run_migrations(conn, old)
    conn.execute("INSERT INTO student (id, key, display_name, course_id, created) VALUES ('old-1', 'plain-key', 'Old', 'c', '2026-01-01')")
    conn.commit()
    assert db.run_migrations(conn)[0] == 14  # 014 first (then any later migration)
    row = conn.execute("SELECT key, key_hash, left_on FROM student WHERE id = 'old-1'").fetchone()
    assert (row["key"], row["key_hash"], row["left_on"]) == ("plain-key", None, None)
    assert "prompt_text" not in [c["name"] for c in conn.execute("PRAGMA table_info(exchange_log)")]


def test_tests_never_use_the_real_data_folder(tmp_path):
    """The autouse fixture in conftest.py gives every test its own folder, so logging a call can't write to ./data."""
    assert db.data_dir() == tmp_path != db.ROOT / "data"
    service.log_call(None, "get_my_progress", learner.parse_ts(learner.now_iso()), 1.0, 10, True)
    assert (tmp_path / "learner.db").exists()
