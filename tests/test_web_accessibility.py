"""Accessibility basics for the pages' markup, so they cannot quietly regress: one h1, landmarks, a skip link that goes
somewhere, a label for every form control, text on every button, no positive tabindex, and tap targets of at least
44 px. (A browser-based check of focus order and screen-reader output is still a manual step; see step 09.)"""

import re

import pytest

from edux.web import app as web

PAGES = ["index", "map", "me", "teacher"]


def html(name):
    return (web.STATIC / f"{name}.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", PAGES)
def test_each_page_has_one_h1_a_title_a_main_landmark_and_a_working_skip_link(name):
    page = html(name)
    assert len(re.findall(r"<h1[ >]", page)) == 1
    assert re.search(r"<title>[^<]+</title>", page)
    assert page.count("<main ") == 1 and 'id="main"' in page and 'href="#main"' in page
    assert "<nav " in page and 'aria-label="Pages"' in page and "<header " in page and "<footer " in page


@pytest.mark.parametrize("name", PAGES)
def test_headings_do_not_skip_a_level(name):
    levels = [int(m) for m in re.findall(r"<h([1-6])[ >]", html(name))]
    assert levels[0] == 1 and all(b - a <= 1 for a, b in zip(levels, levels[1:]))


@pytest.mark.parametrize("name", PAGES)
def test_every_form_control_has_a_label(name):
    page = html(name)
    for tag in re.findall(r"<(?:input|select|textarea)\b[^>]*>", page):
        if 'type="checkbox"' in tag or 'type="hidden"' in tag:
            continue
        ident = re.search(r'id="([^"]+)"', tag)
        labelled = ident and re.search(rf'<label[^>]*for="{ident.group(1)}"', page)
        assert labelled or "aria-label" in tag, f"{name}: a control has no label: {tag}"


@pytest.mark.parametrize("name", PAGES)
def test_no_positive_tabindex_and_no_button_without_text(name):
    page = html(name)
    assert not re.search(r'tabindex="[1-9]', page)
    for button in re.findall(r"<button\b[^>]*>(.*?)</button>", page, re.S):
        assert button.strip(), f"{name}: an empty button"


def test_scripts_label_what_they_create():
    graph = (web.STATIC / "js" / "graph.js").read_text(encoding="utf-8")
    assert graph.count('"aria-label"') >= 3 and 'role: "button"' in graph and "tabindex" in graph
    teacher = (web.STATIC / "js" / "teacher.js").read_text(encoding="utf-8")
    assert 'setAttribute("aria-label"' in teacher  # the class picker and each Remove button name themselves
    me = (web.STATIC / "js" / "me.js").read_text(encoding="utf-8")
    assert 'setAttribute("aria-label", "Part to be checked on")' in me


def test_tap_targets_are_at_least_44_pixels_and_motion_can_be_turned_off():
    base = (web.STATIC / "css" / "base.css").read_text(encoding="utf-8")
    assert "min-height: 2.75rem" in base  # 44 px at the base size
    tokens = (web.STATIC / "css" / "tokens.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in tokens and "--motion: 0ms" in tokens
    assert ":focus-visible" in base and ".visually-hidden" in base


def test_the_teacher_page_prints_without_its_forms():
    base = (web.STATIC / "css" / "base.css").read_text(encoding="utf-8")
    printed = base.split("@media print", 1)[1]
    assert re.search(r"\bform\b[^{]*\{[^}]*display: none", printed)
