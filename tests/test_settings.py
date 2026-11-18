"""settings.toml loads, and its BKT parameters obey the identifiability rules."""

import dataclasses

import pytest

from edux import settings


def test_settings_load():
    s = settings.load_settings()
    assert 0 < s.levels.new < s.levels.secure < 1


def test_guess_plus_slip_below_one_for_every_evidence_type():
    s = settings.load_settings()
    for name, sg in s.bkt.evidence.items():
        assert sg.guess + sg.slip < 1, name


def test_identifiability_check_rejects_a_bad_pair():
    s = settings.load_settings()
    bad = dict(s.bkt.evidence)
    bad["explain_back"] = dataclasses.replace(bad["explain_back"], slip=0.9)
    broken = dataclasses.replace(s, bkt=dataclasses.replace(s.bkt, evidence=bad))
    with pytest.raises(settings.SettingsError):
        settings.check_identifiable(broken)
