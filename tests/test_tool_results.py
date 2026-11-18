"""What a tool sends and how it is counted: one compact JSON text, measured as it is sent, and logging that cannot break a reply."""

import pytest

from edux import server, service


def test_a_pound_sign_is_one_character_and_there_are_no_spaces():
    assert service.compact_json({"a": "£", "b": [1, 2]}) == '{"a":"£","b":[1,2]}'
    assert service.result_size({"a": "£"}) == len('{"a":"£"}')


def test_the_size_counted_is_the_text_sent():
    result = {"ok": True, "plan": [{"move": "teach_point", "cue": "Explain £ and €"}]}
    sent = server.timed("get_my_progress", lambda: result)()
    assert len(sent.content[0].text) == service.result_size(result)


def test_a_failed_call_log_does_not_replace_the_result(monkeypatch, capsys):
    def locked(*args, **kwargs):
        raise RuntimeError("database is locked")

    monkeypatch.setattr(service, "log_call", locked)
    sent = server.timed("get_my_progress", lambda: {"ok": True})()
    assert sent.content[0].text == '{"ok":true}'
    assert "call log failed for get_my_progress: RuntimeError" in capsys.readouterr().err


def test_error_text_is_cut_before_it_is_stored(monkeypatch):
    logged = []
    monkeypatch.setattr(service, "log_call", lambda *args: logged.append(args))

    def refuses():
        raise ValueError("x" * 500)

    with pytest.raises(ValueError):
        server.timed("update_my_profile", refuses)()
    error = logged[0][6]
    assert len(error) == server.ERROR_CHARS


def test_an_ok_false_result_is_logged_with_its_cut_error(monkeypatch):
    logged = []
    monkeypatch.setattr(service, "log_call", lambda *args: logged.append(args))
    server.timed("tutor_turn", lambda: {"ok": False, "error": "y" * 500})()
    assert logged[0][5] is False and len(logged[0][6]) == server.ERROR_CHARS


def _progress(n):
    item = {"part_id": "p", "name": "x" * 60, "level": "new"}
    return {"tree": {"a": "b"}, "levers": [dict(item) for _ in range(n)], "weak_links": [dict(item) for _ in range(n)],
            "reviews_due": [dict(item) for _ in range(n)], "trends": {}, "ai_literacy": {}, "study_pattern": None}


def test_the_levels_view_is_trimmed_from_the_lowest_ranked_items_to_fit():
    limit = service._settings().results.max_chars
    fitted = service.fit_progress(_progress(12))
    assert service.result_size(fitted) <= limit
    assert fitted["weak_links"] == [] or len(fitted["weak_links"]) < 12     # trimmed first
    assert fitted["tree"] == {"a": "b"} and "ai_literacy" in fitted             # never cut


def test_a_progress_view_that_already_fits_is_left_alone():
    small = _progress(1)
    assert service.fit_progress(dict(small)) == small


def test_over_budget_covers_every_tool():
    limit = service._settings().results.max_chars
    for tool in ("tutor_turn", "get_my_progress", "update_my_profile"):
        assert service.over_budget(tool, limit + 1)
        assert not service.over_budget(tool, limit)


def test_the_every_part_progress_view_has_its_own_larger_limit():
    results = service._settings().results
    assert results.max_chars_full_progress > results.max_chars
    assert not service.over_budget("get_my_progress", results.max_chars + 1, full_progress=True)
    assert service.over_budget("get_my_progress", results.max_chars_full_progress + 1, full_progress=True)
    assert service.over_budget("tutor_turn", results.max_chars + 1, full_progress=True)    # only progress gets the larger limit


def test_the_every_part_view_is_trimmed_to_its_own_limit():
    limit = service._settings().results.max_chars_full_progress
    fitted = service.fit_progress(_progress(40), limit)
    assert service.result_size(fitted) <= limit
    assert len(fitted["levers"]) > 0 or len(fitted["reviews_due"]) > 0 or len(fitted["weak_links"]) > 0
