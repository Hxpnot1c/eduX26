"""The course-pack ingest: validation of a good pack and of deliberately broken copies, the loader, the teacher feedback
overlay, the CSV templates and the generated README, and the ingest command line."""

import csv
import shutil
import sqlite3

import pytest

from ingest import cli as ingest_cli
from ingest import load, registry, validate
from tests.conftest import PACK


@pytest.fixture()
def pack(tmp_path):
    """A writable copy of the example pack."""
    target = tmp_path / "pack"
    shutil.copytree(PACK, target)
    return target


def _rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def _write(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _edit(pack, name, change):
    rows, fields = _rows(pack / name)
    change(rows)
    _write(pack / name, rows, fields)


def _problems(pack):
    result = validate.validate_pack(pack)
    return result, [str(m) for m in (*result.errors, *result.warnings)]


def test_the_example_pack_is_valid():
    result = validate.validate_pack(PACK)
    assert result.ok and not result.errors


@pytest.mark.parametrize(
    ("name", "change", "needle"),
    [
        ("nodes.csv", lambda rows: rows[0].update(level="galaxy"), "level"),
        ("nodes.csv", lambda rows: rows[1].update(parent_id="no_such_parent"), "parent"),
        ("nodes.csv", lambda rows: rows.append(dict(rows[0])), "duplicate"),
        ("nodes.csv", lambda rows: rows[1].update(extraction_confidence="high"), "number"),
        ("edges.csv", lambda rows: rows[0].update(to_id="no_such_node"), "no_such_node"),
        ("edges.csv", lambda rows: rows[0].update(type="friendship"), "type"),
        ("edges.csv", lambda rows: rows[0].update(confidence="7"), "confidence"),
        ("misconceptions.csv", lambda rows: rows[0].update(node_id="no_such_node"), "no_such_node"),
        ("mark_points.csv", lambda rows: rows[0].update(node_id="no_such_node"), "no_such_node"),
        ("questions.csv", lambda rows: rows[0].update(marks="lots"), "integer"),
    ],
)
def test_a_broken_pack_is_reported(pack, name, change, needle):
    _edit(pack, name, change)
    result, messages = _problems(pack)
    assert not result.ok or messages
    assert any(needle.lower() in m.lower() for m in messages), messages


def test_a_missing_file_and_a_missing_column_are_reported(pack):
    (pack / "edges.csv").unlink()
    result, messages = _problems(pack)
    assert not result.ok and messages
    pack2 = pack.parent / "pack2"
    shutil.copytree(PACK, pack2)
    rows, fields = _rows(pack2 / "nodes.csv")
    _write(pack2 / "nodes.csv", [{k: v for k, v in r.items() if k != "name"} for r in rows], [f for f in fields if f != "name"])
    result, messages = _problems(pack2)
    assert not result.ok and any("name" in m for m in messages)


def test_a_cycle_in_prerequisites_is_reported(pack):
    _edit(pack, "edges.csv", lambda rows: rows.append({**rows[0], "from_id": rows[0]["to_id"], "to_id": rows[0]["from_id"]}))
    result, messages = _problems(pack)
    assert any("cycle" in m.lower() or "circular" in m.lower() for m in messages), messages


def test_print_result_prints_errors_and_warnings(pack, capsys):
    _edit(pack, "nodes.csv", lambda rows: rows[0].update(level="galaxy"))
    validate.print_result(validate.validate_pack(pack))
    assert capsys.readouterr().out.strip()
    validate.print_result(validate.validate_pack(PACK))


def test_load_and_reload_is_idempotent(tmp_path):
    db = tmp_path / "content.db"
    first = load.load_pack(PACK, db_path=db)
    assert first.ok and first.course_id
    second = load.load_pack(PACK, db_path=db)
    assert second.ok
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM node").fetchone()[0] > 0


def test_a_bad_pack_is_not_loaded(pack, tmp_path):
    _edit(pack, "nodes.csv", lambda rows: rows[0].update(level="galaxy"))
    report = load.load_pack(pack, db_path=tmp_path / "bad.db")
    assert not report.ok


def _feedback(tmp_path, *rows):
    path = tmp_path / "feedback.csv"
    fields = ["ts", "teacher", "table", "target_id", "action", "field", "value", "note"]
    _write(path, [{**dict.fromkeys(fields, ""), "teacher": "Ms T", **r} for r in rows], fields)
    return path


def test_teacher_feedback_approves_edits_adds_and_reports_problems(tmp_path):
    db = tmp_path / "content.db"
    load.load_pack(PACK, db_path=db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    node_id = conn.execute("SELECT id FROM node WHERE level = 'part' LIMIT 1").fetchone()[0]
    edge = conn.execute("SELECT from_id, to_id, type FROM edge LIMIT 1").fetchone()
    edge_id = f"{edge['from_id']}|{edge['to_id']}|{edge['type']}"
    course = conn.execute("SELECT id FROM course").fetchone()[0]
    path = _feedback(
        tmp_path,
        {"ts": "2026-01-01T10:00:00", "table": "nodes", "target_id": node_id, "action": "approve"},
        {"ts": "2026-01-01T10:01:00", "table": "nodes", "target_id": node_id, "action": "reject"},
        {"ts": "2026-01-01T10:02:00", "table": "nodes", "target_id": node_id, "action": "edit", "field": "name", "value": "Renamed"},
        {"ts": "2026-01-01T10:03:00", "table": "edges", "target_id": edge_id, "action": "edit", "field": "weight", "value": "0.4"},
        {"ts": "2026-01-01T10:04:00", "table": "edges", "target_id": edge_id, "action": "edit", "field": "weight", "value": "9"},
        {"ts": "2026-01-01T10:05:00", "table": "edges", "target_id": edge_id, "action": "edit", "field": "weight", "value": "x"},
        {"ts": "2026-01-01T10:06:00", "table": "nodes", "target_id": "missing", "action": "approve"},
        {"ts": "2026-01-01T10:07:00", "table": "nodes", "target_id": node_id, "action": "edit", "field": "id", "value": "z"},
        {"ts": "2026-01-01T10:08:00", "table": "nodes", "target_id": node_id, "action": "edit", "field": "level", "value": "galaxy"},
        {"ts": "2026-01-01T10:09:00", "table": "nodes", "target_id": "a|b", "action": "approve"},
        {
            "ts": "2026-01-01T10:10:00",
            "table": "nodes",
            "target_id": "new_node",
            "action": "add",
            "value": "parent_id=;level=topic;name=Fresh;bad",
        },
        {
            "ts": "2026-01-01T10:11:00",
            "table": "nodes",
            "target_id": "new_node2",
            "action": "add",
            "value": "level=topic;name=Fresh;part_type=",
        },
        {"ts": "2026-01-01T10:12:00", "table": "nodes", "target_id": node_id, "action": "add", "value": "level=part;name=Dup"},
        {"ts": "", "table": "nodes", "target_id": node_id, "action": "approve"},
    )
    not_applied = load.apply_feedback(conn, path, course)
    assert len(not_applied) >= 6 and any("not found" in m for m in not_applied)
    assert conn.execute("SELECT COUNT(*) FROM teacher_feedback").fetchone()[0] == 14
    assert conn.execute("SELECT name FROM node WHERE id = ?", (node_id,)).fetchone()[0] == "Renamed"
    assert load.apply_feedback(conn, tmp_path / "nothing.csv") == []


def test_templates_and_readme_are_generated(tmp_path):
    written = registry.write_templates(tmp_path / "templates")
    assert written and all(p.exists() for p in written)
    text = registry.render_readme()
    assert "nodes.csv" in text and "Teacher feedback" in text


def test_the_ingest_command_line(pack, tmp_path, capsys):
    def run(*argv):
        with pytest.raises(SystemExit) as stop:
            ingest_cli.main(list(argv))
        return stop.value.code, capsys.readouterr().out

    assert run("validate", str(PACK))[0] == 0
    assert run("load", str(PACK), "--db", str(tmp_path / "c.db"), "--feedback-dir", str(tmp_path))[0] == 0
    code, out = run("templates", str(tmp_path / "t"))
    assert code == 0 and out.strip()
    target = tmp_path / "README.md"
    assert run("readme", "--out", str(target))[0] == 0 and target.read_text(encoding="utf-8").startswith("#")
    _edit(pack, "nodes.csv", lambda rows: rows[0].update(level="galaxy"))
    assert run("validate", str(pack))[0] == 1
    assert run("load", str(pack), "--db", str(tmp_path / "d.db"))[0] == 1
