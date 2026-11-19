"""The labelling rule (decision 0002, R5) stays at the top of settings.toml, and the research tags name a source."""

from pathlib import Path

TOML = (Path(__file__).resolve().parent.parent / "settings.toml").read_text()


def test_the_labelling_rule_is_stated_first():
    assert TOML.startswith("# LABELLING RULE") and "JUDGEMENT CALL, STARTING VALUE" in TOML.split("\n\n")[0]


def test_every_from_research_tag_names_a_source():
    for line in TOML.splitlines():
        if "from research" in line and "not from research" not in line and not line.startswith("#"):
            tail = line.split("from research", 1)[1]
            assert any(c.isalpha() for c in tail[:60]) and ("(" in tail or ":" in tail or "personalisation.md" in tail), line
