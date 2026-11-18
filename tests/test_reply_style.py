"""Step 05o: a student's answer_length decides teach_point's word budget, up to one point's worth."""

import pytest

from edux import plan, service


class _Turn:
    def p(self, part_id):          # not reached: a student's own length skips the mastery-based shrinking
        raise AssertionError("turn.p should not be read when answer_length is set")


def _teach_point(part):
    data = {"index": 1, "total": 3, "point": "x", "exemplar": "y", "level": "new", "max_words": 80}
    return plan._step("teach_point", part, data)


def _words_with_answer_length(student, part, length):
    service.update_profile(student, answer_length=length)
    out = service.reply_style([_teach_point(part)], student, _Turn(), {})
    return out[0]["data"]["max_words"]


def test_a_shorter_answer_length_always_wins(student, part):
    assert _words_with_answer_length(student, part, 50) == 50


def test_a_longer_answer_length_raises_teach_point_only_to_the_requested_cap(student, part):
    assert _words_with_answer_length(student, part, 200) == service._settings().points.max_words_requested == 120


def test_a_length_between_the_two_is_taken_as_it_is(student, part):
    assert _words_with_answer_length(student, part, 100) == 100


def test_settings_keep_the_requested_cap_at_least_the_default_budget():
    p = service._settings().points
    assert p.max_words_requested >= p.max_words
