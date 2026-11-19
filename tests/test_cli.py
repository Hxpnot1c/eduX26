"""The command line, run in-process through main(): every command, with its success and its error paths."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from edux import cli, graph, learner
from tests.conftest import PACK


@pytest.fixture()
def run(capsys):
    def _run(*argv):
        with pytest.raises(SystemExit) as stop:
            cli.main(list(argv))
        captured = capsys.readouterr()
        return stop.value.code, captured.out, captured.err

    return _run


@pytest.fixture()
def topic():
    return graph.topics()[0]


def _ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")


def test_load_reports_the_pack(tmp_path, monkeypatch, run):
    monkeypatch.setenv("EDUX_DATA_DIR", str(tmp_path))
    code, out, _ = run("load", str(PACK))
    assert code == 0 and out.strip()


def test_add_student_prints_an_id_and_a_key_once(course, run):
    code, out, _ = run("add-student", "--name", "Sam", "--course", course)
    assert code == 0 and "student: s-" in out and "key:" in out
    code, _, err = run("add-student", "--name", "Sam", "--course", "no-such-course")
    assert code == 1 and err.strip()


def test_set_profile_and_its_errors(student, run):
    assert run("set-profile", "--student", student["id"], "--profile", "minimal")[0] == 0
    assert run("set-profile", "--student", student["id"], "--profile", "nonsense")[0] == 1
    assert run("set-profile", "--student", "nobody", "--profile", "minimal")[0] == 1


def test_log_and_evidence_record_events(student, part, run):
    code, out, _ = run(
        "log",
        "--student",
        student["id"],
        "--nodes",
        part,
        "--depth",
        "mechanism",
        "--engagement",
        "active",
        "--support",
        "hint",
        "--choice",
        "try_first",
        "--misconceptions",
        "",
        "--ts",
        _ago(1),
        "--evidence",
        f"{part}:explain_back:1.0",
    )
    assert code == 0 and "logged exchange" in out and "1 evidence" in out
    assert run("evidence", "--student", student["id"], "--part", part, "--type", "mcq_check", "--score", "0.0", "--ts", _ago(1))[0] == 0
    assert run("log", "--student", "nobody", "--nodes", part, "--depth", "surface", "--engagement", "passive")[0] == 1
    assert run("evidence", "--student", student["id"], "--part", part, "--type", "made_up", "--score", "1")[0] == 1


def test_bad_evidence_option_is_refused(student, part, capsys):
    with pytest.raises(SystemExit):
        cli.main(["log", "--student", student["id"], "--nodes", part, "--depth", "surface", "--engagement", "passive", "--evidence", "bad"])
    assert capsys.readouterr().err


def test_state_sessions_context_and_calls(student, part, run):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now", ts=_ago(1))
    code, out, _ = run("state", "--student", student["id"])
    assert code == 0 and part in out and "learning rate" in out
    assert run("state", "--student", student["id"], "--node", part, "--at", _ago(0))[0] == 0
    assert run("state", "--student", "nobody")[0] == 1
    assert run("state", "--student", student["id"], "--node", "no-such-node")[0] == 1
    assert run("sessions", "--student", student["id"])[0] == 0
    assert run("sessions", "--student", "nobody")[0] == 1
    code, out, _ = run("context", "--student", student["id"], "--message", "what is elasticity?", "--nodes", part)
    assert code == 0 and out.strip()
    assert run("context", "--student", "nobody", "--message", "hi")[0] == 1
    assert run("calls")[0] == 0
    assert run("calls", "--student", student["id"], "--last", "5")[0] == 0


def test_rebuild_one_or_all(student, part, run):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    code, out, _ = run("rebuild", "--student", student["id"])
    assert code == 0 and "replayed" in out
    assert run("rebuild", "--student", "nobody")[0] == 1
    code, out, _ = run("rebuild")
    assert code == 0 and "rebuilt 1 student" in out


def test_export_and_delete_a_student(student, part, run, tmp_path):
    learner.record_evidence(student["id"], part, "explain_back", 1.0, apply="now")
    code, out, _ = run("export-student", "--student", student["id"])
    assert code == 0 and json.loads(out)["student"]["id"] == student["id"]
    target = tmp_path / "out.json"
    assert run("export-student", "--student", student["id"], "--out", str(target))[0] == 0 and target.exists()
    assert run("export-student", "--student", "nobody")[0] == 1
    code, _, err = run("delete-student", "--student", student["id"])
    assert code == 1 and "--yes" in err and learner.get_student(student["id"]) is not None
    code, out, _ = run("delete-student", "--student", student["id"], "--yes")
    assert code == 0 and learner.get_student(student["id"]) is None
    assert run("delete-student", "--student", student["id"], "--yes")[0] == 1


def test_leave_and_purge(student, run):
    assert (
        run("leave-student", "--student", student["id"], "--on", (datetime.now(timezone.utc) - timedelta(days=400)).date().isoformat())[0]
        == 0
    )
    assert run("leave-student", "--student", "nobody")[0] == 1
    code, out, _ = run("purge")
    assert code == 0 and learner.get_student(student["id"]) is None
    assert run("leave-student", "--student", "nobody", "--on", "2026-01-01")[0] == 1


def test_classes_coverage_and_assessments(student, topic, run, tmp_path):
    code, out, _ = run("class", "add", "--name", "Year 12", "--pack", "ped")
    assert code == 0 and out.startswith("class: ")
    class_id = out.split(": ")[1].strip()
    assert run("class", "add-students", "--class", class_id, "--students", student["id"])[0] == 0
    assert run("class", "add-students", "--class", "nope", "--students", student["id"])[0] == 1
    assert run("coverage", "set", "--class", class_id, "--sections", topic["name"], "--taught-on", "2026-10-01")[0] == 0
    assert run("coverage", "set", "--class", class_id, "--sections", "no such section")[0] == 1
    assert run("coverage", "set", "--class", "nope", "--sections", topic["name"])[0] == 1
    csv_path = tmp_path / "cov.csv"
    csv_path.write_text(f"section,taught_on\n{topic['name']},2026-10-02\n", encoding="utf-8")
    assert run("coverage", "import", "--class", class_id, str(csv_path))[0] == 0
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n", encoding="utf-8")
    assert run("coverage", "import", "--class", class_id, str(bad))[0] == 1
    assert run("coverage", "import", "--class", class_id, str(tmp_path / "missing.csv"))[0] == 1
    unmatched = tmp_path / "unmatched.csv"
    unmatched.write_text("section,taught_on\nnothing here,2026-10-02\n", encoding="utf-8")
    assert run("coverage", "import", "--class", class_id, str(unmatched))[0] == 1
    badday = tmp_path / "badday.csv"
    badday.write_text(f"section,taught_on\n{topic['name']},yesterday\n", encoding="utf-8")
    assert run("coverage", "import", "--class", class_id, str(badday))[0] == 1
    code, out, _ = run("coverage", "export", "--class", class_id)
    assert code == 0 and topic["name"] in out
    code, out, _ = run("coverage", "export", "--class", class_id, "--json")
    assert code == 0 and json.loads(out)["class"] == class_id
    future = (datetime.now(timezone.utc) + timedelta(days=9)).date().isoformat()
    assert (
        run("assessment", "add", "--class", class_id, "--name", "Mock", "--kind", "mock", "--date", future, "--topics", topic["name"])[0]
        == 0
    )
    assert (
        run("assessment", "add", "--class", class_id, "--name", "Mock", "--kind", "mock", "--date", future, "--topics", "nothing")[0] == 1
    )
    assert (
        run("assessment", "add", "--class", "nope", "--name", "Mock", "--kind", "mock", "--date", future, "--topics", topic["name"])[0] == 1
    )


def test_seed_demo_and_reset(course, run):
    code, out, _ = run("seed-demo")
    assert code == 0 and "demo-secure" in out
    assert run("seed-demo")[0] == 1  # already there
    assert run("seed-demo", "--reset")[0] == 0
    assert run("seed-demo", "--reset", "--parts", "target=no_such_part")[0] == 1
    code, out, _ = run("state", "--student", "demo-weak")
    assert code == 0 and "assessment" in out


def test_serve_passes_host_and_port_through(course, run, monkeypatch):
    seen = {}
    monkeypatch.setattr("edux.server.serve", lambda host=None, port=None: seen.update(host=host, port=port), raising=False)
    monkeypatch.setattr("edux.cli.cmd_serve", lambda host=None, port=None: seen.update(host=host, port=port) or 0)
    assert run("serve", "--host", "127.0.0.1", "--port", "9999")[0] == 0 and seen == {"host": "127.0.0.1", "port": 9999}


def test_the_list_and_evidence_parsers():
    assert cli._list("a, b,,c") == ["a", "b", "c"]
    assert cli._evidence("p:explain_back:0.5") == {"part_id": "p", "type": "explain_back", "score": 0.5}
    with pytest.raises(Exception):
        cli._evidence("only:two")
