"""The demo seeding: role choice and its overrides, errors, the saved keys, and what the three students look like."""

import json

import pytest

from edux import demo, graph, learner


def test_roles_are_chosen_from_the_pack(course):
    roles, warnings = demo.pick_roles()
    assert set(demo.ROLES) <= set(roles) and isinstance(warnings, list)
    assert graph.get_node(roles["target"])["level"] == "part"


def test_overrides_are_applied(course):
    parts = learner.all_parts()
    roles, _ = demo.pick_roles(f"target={parts[0]},prereq={parts[1]},anchor={parts[2]},confusable={parts[3]}")
    assert roles["target"] == parts[0] and roles["prereq"] == parts[1]
    roles, _ = demo.pick_roles(f"review_parts={parts[0]};{parts[1]},showme_parts={parts[2]}")
    assert roles["review_parts"] == [parts[0], parts[1]] and roles["showme_parts"] == [parts[2]]


@pytest.mark.parametrize(
    "overrides",
    ["nonsense=1", "target=", "target=no_such_part", "review_parts=no_such_part"],
)
def test_bad_overrides_are_refused(course, overrides):
    with pytest.raises(demo.DemoError):
        demo.pick_roles(overrides)


def test_a_misconception_override_is_checked(course):
    target = demo.pick_roles()[0]["target"]
    misconception = graph.misconceptions_for([target])[0]["id"]
    assert demo.pick_roles(f"target={target},misconception={misconception}")[0]["misconception"] == misconception
    with pytest.raises(demo.DemoError):
        demo.pick_roles("misconception=no_such_id")


def test_a_pack_with_no_parts_is_refused(course, monkeypatch):
    monkeypatch.setattr(learner, "all_parts", lambda: [])
    with pytest.raises(demo.DemoError, match="no parts"):
        demo.pick_roles()


def test_the_course_must_be_unambiguous(course):
    assert demo._course(None) == course
    assert demo._course(course) == course
    with pytest.raises(demo.DemoError, match="unknown course"):
        demo._course("elsewhere")


def test_seed_saves_keys_and_reset_keeps_them(course):
    first = demo.seed()
    saved = demo.demo_keys()
    assert set(saved) == set(demo.STUDENTS) and saved == first["students"]
    again = demo.seed(reset=True)
    assert again["students"] == first["students"]
    with pytest.raises(demo.DemoError, match="already exist"):
        demo.seed()


def test_unreadable_keys_file_means_no_keys(course):
    demo.keys_path().write_text("not json", encoding="utf-8")
    assert demo.demo_keys() == {}


def test_a_legacy_database_without_a_keys_file_still_yields_its_keys(course):
    demo.seed()
    demo.keys_path().unlink()
    assert demo.remove_students() == {}  # the keys exist only as hashes now, so none can be handed back
    assert learner.get_student("demo-secure") is None


def test_the_demo_students_tell_the_story_the_script_promises(course):
    demo.seed()
    now = learner.now_iso()
    secure, weak, showme = ("demo-secure", "demo-weak", "demo-showme")
    assert learner.part_p(secure, demo.pick_roles()[0]["target"], now) < learner.part_p(secure, demo.pick_roles()[0]["prereq"], now)
    assert learner.upcoming(weak, now)  # the weak student has a mock coming up
    assert learner.get_student(showme) is not None
    assert json.loads(demo.keys_path().read_text(encoding="utf-8"))
