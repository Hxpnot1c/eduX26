"""Bad configuration is refused with a clear message: wrong types, missing and unknown keys, impossible numbers."""

import re

import pytest

from edux import settings
from edux.settings import SettingsError

TOML = settings.SETTINGS_PATH.read_text(encoding="utf-8")
CONTEXT = settings.CONTEXT_PATH.read_text(encoding="utf-8")


def _load(tmp_path, text):
    path = tmp_path / "settings.toml"
    path.write_text(text, encoding="utf-8")
    return settings.load_settings(path)


def _swap(old, new, text=TOML):
    assert old in text, old
    return text.replace(old, new, 1)


def test_the_shipped_files_load():
    assert settings.load_settings().levels.new < settings.load_settings().levels.secure
    assert settings.load_context().default_profile


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("new = 0.40 ", 'new = "low" #', "number"),
        ("max_options = 4 ", "max_options = 4.5 #", "integer"),
        ("max_options = 4 ", "max_options = [4] #", "integer"),
        ("protocol = ", "protocol = 3 #", "string"),
        ("class_estimate_enabled = false", "class_estimate_enabled = 1", "true or false"),
        ("queue_band = [0.30, 0.75]", "queue_band = [0.30]", "items"),
        ("queue_band = [0.30, 0.75]", "queue_band = 0.3", "array"),
        ("new = 0.40 ", "new = 0.9 #", "levels"),
        ("ceiling = 0.35", "ceiling = 0.5", "ceiling"),
        ("[levels]", "[levels]\nnonsense = 1", "unknown"),
        ("secure = 0.75 ", "# secure removed #", "missing"),
    ],
)
def test_a_bad_value_is_refused(tmp_path, old, new, message):
    text = re.sub(re.escape(old), new, TOML, count=1)
    with pytest.raises(SettingsError, match=message):
        _load(tmp_path, text)


def test_a_missing_or_broken_file_is_refused(tmp_path):
    with pytest.raises(SettingsError, match="not found"):
        settings.load_settings(tmp_path / "nope.toml")
    with pytest.raises(SettingsError):
        _load(tmp_path, "this is = = not toml")


def test_guess_plus_slip_must_stay_below_one(tmp_path):
    text = _swap("explain_back = { slip = 0.10, guess = 0.20 }", "explain_back = { slip = 0.60, guess = 0.60 }")
    with pytest.raises(SettingsError, match="below 1"):
        _load(tmp_path, text)


def test_learn_rate_must_stay_identifiable(tmp_path):
    with pytest.raises(SettingsError, match="learn_rate"):
        _load(tmp_path, _swap("learn_rate = 0.10 ", "learn_rate = 0.9 #"))


def test_personal_bounds_and_requested_words_are_checked(tmp_path):
    with pytest.raises(SettingsError, match="learn_rate_weight_bounds"):
        _load(tmp_path, re.sub(r"learn_rate_weight_bounds = \[[^\]]*\]", "learn_rate_weight_bounds = [1.5, 0.5]", TOML, count=1))
    with pytest.raises(SettingsError, match="max_words_requested"):
        _load(tmp_path, re.sub(r"max_words_requested = \d+", "max_words_requested = 1", TOML, count=1))


def test_context_checks_its_profiles_and_blocks(tmp_path):
    path = tmp_path / "context.toml"
    path.write_text(CONTEXT.replace('default_profile = "full"', 'default_profile = "nothing"', 1), encoding="utf-8")
    with pytest.raises(SettingsError, match="no profile named"):
        settings.load_context(path)
    path.write_text(re.sub(r"(\[moves\.[^\]]+\]\s*\n\s*reference\s*=\s*\[)", r'\1"no_such_block", ', CONTEXT, count=1), encoding="utf-8")
    with pytest.raises(SettingsError, match="no profile has block"):
        settings.load_context(path)


def test_a_table_is_expected_where_a_table_belongs():
    with pytest.raises(SettingsError, match="expected a table"):
        settings._convert(5, settings.Levels, "levels")
    with pytest.raises(SettingsError, match="expected a table"):
        settings._convert(5, dict[str, settings.Levels], "levels")
    with pytest.raises(SettingsError, match="unsupported type"):
        settings._convert(5, object, "x")
