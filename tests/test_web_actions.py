"""What a teacher can change from the page: set or remove a test, mark sections as taught. Each is authorised per class,
validated like the command line, recorded in the audit trail, and shown to the class's students the way the command line
would show it."""

from datetime import date, timedelta

import pytest
from starlette.testclient import TestClient

from edux import graph, learner, server, teachers
from edux.web import views


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


@pytest.fixture()
def owned(course):
    """A teacher, their class of six, and one student in it."""
    teacher = teachers.add_teacher("Ms Owner")
    class_id = learner.add_class("Y12", None)
    ids = []
    for i in range(6):
        s = learner.add_student(f"Pupil {i}", course)
        learner.add_students_to_class(class_id, [s["id"]])
        ids.append(s["id"])
    teachers.assign_class(teacher["id"], class_id)
    return {"teacher": teacher, "class": class_id, "students": ids, "key": teacher["key"]}


def _post(client, owned, path, body, key=None, cls=None):
    return client.post(
        f"/api/teacher/class/{cls or owned['class']}/{path}", json=body, headers={"Authorization": f"Bearer {key or owned['key']}"}
    )


def _future(days=9):
    return (date.today() + timedelta(days=days)).isoformat()


def _topic():
    return graph.topics()[0]


# --- who may change what ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["assessments", "assessments/remove", "coverage"])
def test_nobody_without_the_right_key_can_change_a_class(client, owned, student, path):
    body = {"name": "x", "kind": "mock", "date": _future(), "topics": [_topic()["name"]], "sections": [_topic()["name"]], "id": 1}
    assert client.post(f"/api/teacher/class/{owned['class']}/{path}", json=body).status_code == 401
    assert _post(client, owned, path, body, key="wrong").status_code == 401
    assert _post(client, owned, path, body, key=student["key"]).status_code == 403
    other = teachers.add_teacher("Ms Other")
    assert _post(client, owned, path, body, key=other["key"]).status_code == 404  # not theirs
    assert (
        client.post(
            f"/api/teacher/class/{owned['class']}/{path}?key={owned['key']}", json=body, headers={"Authorization": f"Bearer {owned['key']}"}
        ).status_code
        == 400
    )
    assert learner._conn().execute("SELECT COUNT(*) FROM teacher_action").fetchone()[0] == 0  # nothing was changed or logged


def test_a_teacher_who_has_left_cannot_change_anything(client, owned):
    teachers.leave_teacher(owned["teacher"]["id"])
    assert _post(client, owned, "coverage", {"sections": [_topic()["name"]]}).status_code == 401


# --- tests and assignments ---------------------------------------------------------------------------------------


def test_setting_a_test_is_recorded_shown_and_reaches_every_student(client, owned):
    res = _post(client, owned, "assessments", {"name": "Unit test", "kind": "class_test", "date": _future(), "topics": [_topic()["name"]]})
    assert res.status_code == 200
    body = res.json()
    assert [a["name"] for a in body["assessments"]] == ["Unit test"] and body["assessments"][0]["id"]
    assert body["recent_changes"][0]["who"] == "Ms Owner" and "added a test" in body["recent_changes"][0]["action"]
    for sid in owned["students"]:
        assert [a["name"] for a in learner.upcoming(sid, days=30)] == ["Unit test"]


@pytest.mark.parametrize(
    ("change", "needle"),
    [
        ({"kind": "quiz"}, "kind"),
        ({"name": "  "}, "name"),
        ({"date": "soon"}, "date"),
        ({"date": "2001-01-01"}, "future"),
        ({"topics": ["zzz nothing"]}, "no topic matched"),
        ({"topics": []}, "no topic matched"),
    ],
)
def test_a_bad_test_is_refused_with_a_reason_and_changes_nothing(client, owned, change, needle):
    body = {"name": "Unit test", "kind": "class_test", "date": _future(), "topics": [_topic()["name"]], **change}
    res = _post(client, owned, "assessments", body)
    assert res.status_code == 400 and needle in res.json()["error"].lower()
    assert views.class_summary(owned["class"])["assessments"] == [] and teachers.recent_actions(owned["class"]) == []


def test_a_test_can_be_removed_only_from_its_own_class(client, owned):
    _post(client, owned, "assessments", {"name": "Unit test", "kind": "mock", "date": _future(), "topics": [_topic()["name"]]})
    aid = views.class_summary(owned["class"])["assessments"][0]["id"]
    other_class = learner.add_class("Y13", None)
    teachers.assign_class(owned["teacher"]["id"], other_class)
    assert _post(client, owned, "assessments/remove", {"id": aid}, cls=other_class).status_code == 400  # that test is not that class's
    assert _post(client, owned, "assessments/remove", {"id": "1"}).status_code == 400
    assert _post(client, owned, "assessments/remove", {"id": True}).status_code == 400
    res = _post(client, owned, "assessments/remove", {"id": aid})
    assert res.status_code == 200 and res.json()["assessments"] == [] and "removed a test" in res.json()["recent_changes"][0]["action"]


# --- coverage ----------------------------------------------------------------------------------------------------


def test_marking_a_section_taught_changes_what_students_are_shown(client, owned):
    sid = owned["students"][0]
    part = graph.parts_of(_topic()["id"])[0]
    assert learner.shown_level(sid, part) == "new"
    taught = (date.today() - timedelta(days=4)).isoformat()
    res = _post(client, owned, "coverage", {"sections": [_topic()["name"]], "taught_on": taught})
    assert res.status_code == 200 and res.json()["coverage"]["taught"][0]["taught_on"] == taught
    assert learner.shown_level(sid, part) == "taught_in_class"
    assert learner._conn().execute("SELECT set_by FROM class_coverage WHERE class_id = ?", (owned["class"],)).fetchone()[0] == "web"


@pytest.mark.parametrize(
    ("body", "needle"),
    [
        ({"sections": []}, "no match"),
        ({"sections": ["zzz nothing"]}, "no match"),
        ({"sections": ["zzz nothing", "ped"]}, "zzz nothing"),
        ({"sections": ["ped"], "taught_on": "yesterday"}, "date"),
        ({"sections": ["ped"], "taught_on": (date.today() + timedelta(days=2)).isoformat()}, "future"),
    ],
)
def test_bad_coverage_is_refused_with_a_reason(client, owned, body, needle):
    res = _post(client, owned, "coverage", body)
    assert res.status_code == 400 and needle in res.json()["error"].lower()
    assert views.class_summary(owned["class"])["coverage"]["taught"] == []


def test_coverage_defaults_to_today(client, owned):
    res = _post(client, owned, "coverage", {"sections": [_topic()["name"]]})
    assert (
        res.status_code == 200
        and res.json()["coverage"]["taught"][0]["taught_on"] == learner.parse_ts(learner.now_iso()).date().isoformat()
    )


# --- the request itself --------------------------------------------------------------------------------------------


def test_a_huge_or_malformed_body_is_refused(client, owned):
    headers = {"Authorization": f"Bearer {owned['key']}", "Content-Type": "application/json"}
    url = f"/api/teacher/class/{owned['class']}/coverage"
    assert client.post(url, content=b"x" * 20_000, headers=headers).status_code == 413
    assert client.post(url, content=b"not json", headers=headers).status_code == 400
    assert client.post(url, content=b"[1, 2]", headers=headers).status_code == 400


# --- the audit trail -------------------------------------------------------------------------------------------------


def test_the_trail_names_the_teacher_while_they_are_here_and_not_after(client, owned):
    _post(client, owned, "coverage", {"sections": [_topic()["name"]]})
    assert teachers.recent_actions(owned["class"])[0]["who"] == "Ms Owner"
    teachers.delete_teacher(owned["teacher"]["id"])
    kept = teachers.recent_actions(owned["class"])
    assert kept and kept[0]["who"] == teachers.FORMER and "Ms Owner" not in str(kept)


def test_the_trail_is_newest_first_and_limited(client, owned):
    for n in range(8):
        teachers.log_action(owned["teacher"]["id"], owned["class"], "marked as taught", f"item {n}")
    shown = teachers.recent_actions(owned["class"], 6)
    assert len(shown) == 6 and shown[0]["detail"] == "item 7"
