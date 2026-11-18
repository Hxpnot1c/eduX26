"""Talk is not evidence: an ordinary exchange can nudge a part up to nudges.ceiling and no further."""

import pytest

from edux import learner, settings


def _p_known(student_id, part_id):
    row = learner._conn().execute(
        "SELECT p_known FROM part_state WHERE student_id = ? AND part_id = ?", (student_id, part_id)).fetchone()
    return row["p_known"]


def test_many_deep_exchanges_never_pass_the_ceiling(student, part):
    ceiling = learner._settings().nudges.ceiling
    for _ in range(80):    # about 14 labelled messages used to reach "secure"
        learner.record_exchange(student["id"], [part], "transfer", "constructive", apply="now")
    assert _p_known(student["id"], part) <= ceiling + 1e-9
    assert learner.level(learner.part_p(student["id"], part)) != "secure"


def test_the_nudge_still_raises_a_part_below_the_ceiling(student, part):
    start = learner.initial_state(part)[0]
    learner.record_exchange(student["id"], [part], "transfer", "constructive", apply="now")
    assert _p_known(student["id"], part) > start


def test_a_nudge_never_lowers_a_part_that_evidence_has_lifted(student, part):
    sid = student["id"]
    for _ in range(4):
        learner.record_evidence(sid, part, "mcq_check", 1.0, apply="now", n_options=4)
    lifted = _p_known(sid, part)
    assert lifted > learner._settings().nudges.ceiling
    learner.record_exchange(sid, [part], "transfer", "constructive", apply="now")
    assert _p_known(sid, part) == pytest.approx(lifted)


def test_a_surface_passive_exchange_changes_nothing(student, part):
    start = learner.initial_state(part)[0]
    learner.record_exchange(student["id"], [part], "surface", "passive", apply="now")
    assert _p_known(student["id"], part) == pytest.approx(start)


def test_settings_refuse_a_ceiling_above_the_new_level(tmp_path):
    text = settings.SETTINGS_PATH.read_text(encoding="utf-8")
    assert "ceiling = 0.40" in text
    bad = tmp_path / "settings.toml"
    bad.write_text(text.replace("ceiling = 0.40", "ceiling = 0.90"), encoding="utf-8")
    with pytest.raises(settings.SettingsError, match="nudges.ceiling"):
        settings.load_settings(bad)
