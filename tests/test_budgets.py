"""The two size gates in the handover: tool results within results.max_chars, instructions within the word cap."""

from edux import plan, service, settings


def test_instructions_are_inside_the_word_cap_and_the_headroom_is_reported(capsys):
    s = settings.load_settings()
    words = len(plan.server_instructions(s).split())
    with capsys.disabled():
        print(f"\nserver instructions: {words} of {s.instructions.max_words} words ({s.instructions.max_words - words} spare)")
    assert words <= s.instructions.max_words


def test_fit_budget_drops_reference_blocks_from_the_end_but_never_the_plan(course):
    limit = settings.load_settings().results.max_chars
    out = {
        "ok": True,
        "plan": [{"move": "teach_point"}],
        "score_next": {},
        "focus": [],
        "reference": {"notes": ["x" * 900], "anchor": ["y" * 900], "causal": ["z" * 900]},
    }
    fitted = service.fit_budget(out)
    assert service.result_size(fitted) <= limit
    assert fitted["plan"] == [{"move": "teach_point"}]
    assert "notes" in fitted["reference"]  # the first block in priority order survives longest
