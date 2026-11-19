"""The teacher's class view: who may ask, and the privacy rules the view keeps for itself. A class cell under the
minimum is withheld, a small class shows no student data at all, parts are banded so a small group cannot be found by
subtraction, and no student identifier, confidence or fatigue figure appears anywhere in the JSON."""

import json
from datetime import date, timedelta

import pytest
from starlette.testclient import TestClient

from edux import demo, graph, learner, server, teachers
from edux.web import views

MIN = 5
FORBIDDEN = {
    "student_id",
    "students_list",
    "confidence",
    "calibration",
    "fatigue",
    "rapid",
    "learn_rate",
    "p_now",
    "p_known",
    "p",
    "score",
    "rank",
}


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


def _auth(key):
    return {"Authorization": f"Bearer {key}"}


def _walk_keys(value, found=None):
    found = set() if found is None else found
    if isinstance(value, dict):
        for k, v in value.items():
            found.add(k)
            _walk_keys(v, found)
    elif isinstance(value, list):
        for v in value:
            _walk_keys(v, found)
    return found


def _class(course, n, name="Y12"):
    class_id = learner.add_class(name, None)
    ids = []
    for i in range(n):
        s = learner.add_student(f"Real Name {i}", course)
        learner.add_students_to_class(class_id, [s["id"]])
        ids.append(s["id"])
    return class_id, ids


def _practise(student_id, part, times=3, score=1.0):
    for k in range(times):
        learner.record_evidence(
            student_id,
            part,
            "explain_back",
            score,
            apply="now",
            ts=learner._event_ts(learner.parse_ts(learner.now_iso()) - timedelta(days=3, minutes=k)),
        )


def _developing(student_id, part):
    _practise(student_id, part, 3, 1.0)
    assert learner.shown_level(student_id, part) in ("developing", "secure")


def _new(student_id, part):
    learner.record_evidence(student_id, part, "explain_back", 0.0, apply="now")
    assert learner.shown_level(student_id, part) == "new"


# --- a small class -----------------------------------------------------------------------------------------------


def test_a_class_under_the_minimum_shows_no_student_data(course):
    class_id, ids = _class(course, MIN - 1)
    part = learner.all_parts()[0]
    for sid in ids:
        _developing(sid, part)
    data = views.class_summary(class_id)
    assert data["enough"] is False and data["overlay"] == {} and data["wrong_ideas"] == [] and data["help_seeking"] is None
    assert data["class"]["size"] == MIN - 1 and "coverage" in data and "assessments" in data


# --- the cell minimum and the bands -------------------------------------------------------------------------------


def test_a_part_with_fewer_than_five_students_answering_is_withheld(course):
    class_id, ids = _class(course, 8)
    part = learner.all_parts()[0]
    for sid in ids[: MIN - 1]:
        _developing(sid, part)
    cell = views.class_summary(class_id)["overlay"][part]
    assert cell["level"] == "none" and "not enough" in cell["label"] and set(cell) == {"level", "label", "note", "fade"}


@pytest.mark.parametrize(
    ("developing", "new", "band"),
    [(0, 6, "few"), (1, 5, "few"), (2, 4, "mixed"), (3, 3, "mixed"), (4, 2, "mixed"), (5, 1, "most"), (6, 0, "most")],
)
def test_a_part_is_a_band_not_a_count_at_each_level(course, developing, new, band):
    class_id, ids = _class(course, 6)
    part = learner.all_parts()[0]
    for sid in ids[:developing]:
        _developing(sid, part)
    for sid in ids[developing:]:
        _new(sid, part)
    cell = views.class_summary(class_id)["overlay"][part]
    assert cell["band"] == band and cell["level"] == views.BAND_LEVEL[band]
    assert set(cell) == {"level", "band", "label", "note", "fade"}  # no per-level counts to subtract
    assert "6 students have answered" in cell["note"]


def test_a_cell_resting_on_few_students_is_called_thin_and_drawn_lighter(course):
    class_id, ids = _class(course, MIN)
    part = learner.all_parts()[0]
    for sid in ids:
        _developing(sid, part)
    cell = views.class_summary(class_id)["overlay"][part]
    assert "Thin" in cell["note"] and cell["fade"] < 1.0
    big_id, big = _class(course, views.THIN, "Y13")
    for sid in big:
        _developing(sid, part)
    assert views.class_summary(big_id)["overlay"][part]["fade"] == 1.0


# --- wrong ideas and help-seeking ----------------------------------------------------------------------------------


def test_a_wrong_idea_is_listed_only_when_five_or_more_students_hold_it(course):
    class_id, ids = _class(course, 7)
    part = learner.all_parts()[0]
    wrong = graph.misconceptions_for([part])[0]["id"]
    for sid in ids[: MIN - 1]:
        learner.record_evidence(sid, part, "mcq_check", 0.0, [wrong], apply="now")
    assert views.class_summary(class_id)["wrong_ideas"] == []
    learner.record_evidence(ids[MIN - 1], part, "mcq_check", 0.0, [wrong], apply="now")
    ideas = views.class_summary(class_id)["wrong_ideas"]
    assert [(i["id"], i["students"]) for i in ideas] == [(wrong, MIN)]


def _exchanges(ids, days_ago, asked):
    part = learner.all_parts()[0]
    for n, sid in enumerate(ids):
        ts = learner._event_ts(learner.parse_ts(learner.now_iso()) - timedelta(days=days_ago, minutes=n))
        learner.record_exchange(sid, [part], "mechanism", "active", choice_taken="just_show_me" if n in asked else None, ts=ts, apply="now")


def test_the_help_seeking_pattern_needs_five_students_in_each_window(course):
    class_id, ids = _class(course, 6)
    assert views.class_summary(class_id)["help_seeking"] is None
    _exchanges(ids[:4], 3, {0})
    _exchanges(ids, 30, set())
    assert views.class_summary(class_id)["help_seeking"] is None  # only four students wrote in the recent window
    _exchanges(ids[4:], 3, {0})
    pattern = views.class_summary(class_id)["help_seeking"]
    assert (
        pattern["direction"] == "up" and pattern["recent"] > pattern["before"] and set(pattern) == {"recent", "before", "direction", "days"}
    )


# --- what is never in the JSON ---------------------------------------------------------------------------------------


def test_no_student_identifier_name_key_or_personal_trait_is_in_the_summary(course):
    class_id, ids = _class(course, 9)
    part = learner.all_parts()[0]
    for sid in ids:
        _developing(sid, part)
        learner.record_evidence(sid, part, "mcq_check", 0.0, [graph.misconceptions_for([part])[0]["id"]], apply="now")
    _exchanges(ids, 3, {0, 1})
    _exchanges(ids, 30, set())
    text = json.dumps(views.class_summary(class_id))
    for sid in ids:
        assert sid not in text
    assert "Real Name" not in text and not (_walk_keys(json.loads(text)) & FORBIDDEN)


def test_the_synthetic_class_is_named_as_such_and_flagged(course):
    demo.seed(pupils=8)
    data = views.class_summary(demo.CLASS_ID)
    assert data["seeded"] is True and data["enough"] is True and data["class"]["size"] == 11
    names = [r["display_name"] for r in learner._conn().execute("SELECT display_name FROM student WHERE id LIKE 'demo-pupil-%'")]
    assert len(names) == 8 and all(n.startswith("Synthetic pupil") for n in names)
    demo.seed(reset=True)
    assert learner._conn().execute("SELECT COUNT(*) FROM student WHERE id LIKE 'demo-pupil-%'").fetchone()[0] == 0


def test_coverage_and_what_is_not_yet_covered(course):
    class_id, _ = _class(course, 6)
    topic = graph.topics()[0]
    concept = next(c for c in graph.children(topic["id"]) if c["level"] == "concept")
    learner.set_class_coverage(class_id, [concept["id"]], (date.today() - timedelta(days=5)).isoformat(), "cli")
    coverage = views.class_summary(class_id)["coverage"]
    assert [c["name"] for c in coverage["taught"]] == [concept["name"]]
    assert concept["name"] not in [c["name"] for c in coverage["not_yet"]] and coverage["not_yet"]


def test_a_class_assessment_is_listed_once_not_once_per_student(course):
    class_id, _ = _class(course, 6)
    parts = graph.parts_of(graph.topics()[0]["id"])
    learner.add_class_assessment(class_id, "Class test", "class_test", (date.today() + timedelta(days=6)).isoformat(), parts)
    assert [a["name"] for a in views.class_summary(class_id)["assessments"]] == ["Class test"]


def test_an_unknown_class_has_no_summary(course):
    assert views.class_summary("nope") is None


# --- the route -------------------------------------------------------------------------------------------------------


def test_only_the_teacher_who_owns_a_class_can_read_it(client, course):
    class_id, _ = _class(course, 6)
    mine, other = teachers.add_teacher("Mine"), teachers.add_teacher("Other")
    teachers.assign_class(mine["id"], class_id)
    url = f"/api/teacher/class/{class_id}"
    assert client.get(url).status_code == 401
    assert client.get(url, headers=_auth("wrong")).status_code == 401
    assert client.get(url, headers=_auth(mine["key"])).status_code == 200
    assert client.get(url, headers=_auth(other["key"])).status_code == 404  # not theirs: the same answer as for no such class
    assert client.get("/api/teacher/class/nope", headers=_auth(other["key"])).status_code == 404
    assert client.get(f"{url}?key={mine['key']}", headers=_auth(mine["key"])).status_code == 400


def test_a_student_cannot_read_a_class(client, course, student):
    class_id, _ = _class(course, 6)
    assert client.get(f"/api/teacher/class/{class_id}", headers=_auth(student["key"])).status_code == 403


def test_a_leaver_loses_access_at_once(client, course):
    class_id, _ = _class(course, 6)
    t = teachers.add_teacher("Leaver")
    teachers.assign_class(t["id"], class_id)
    assert client.get(f"/api/teacher/class/{class_id}", headers=_auth(t["key"])).status_code == 200
    teachers.leave_teacher(t["id"])
    assert client.get(f"/api/teacher/class/{class_id}", headers=_auth(t["key"])).status_code == 401


# --- the page ---------------------------------------------------------------------------------------------------------


def test_the_teacher_page_states_what_it_does_not_show():
    from edux.web import app as web

    html = (web.STATIC / "teacher.html").read_text(encoding="utf-8")
    for line in ("Any one student", "fewer than five students", "Grades, predictions, rankings", "How sure students are", "special needs"):
        assert line in html
    assert "graph.js" in html and "teacher.js" in html and 'id="class-body" hidden' in html
