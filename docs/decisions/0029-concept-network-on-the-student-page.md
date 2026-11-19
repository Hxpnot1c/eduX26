# 0029. The concept network replaces the map on the student's page

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (his design preview `synapse-concept-network.html`, 19 November)
- **Pull request:** #88 (stacked on #87)
- **Amends:** [0024](0024-visual-language-and-what-the-pages-will-not-show.md) (the colour ramp and look of this one map only)

## Context

A student who asks the chatbot about their progress opens their own page (`/me`, decision 0026). Its map was the course map from `/map`, coloured by level. Vishnu's design preview draws the course as a concept network instead: every idea as a circle sized by importance, grouped by topic, joined by the pack's links ("builds on", "works the same way", "easy to mix up"), with a card per idea on hover or tap.

## Decision

1. **The student's page shows the network** in place of the old map. The layout, the physics, the legend, the card and the wording are the preview's. The data is the student's own, from `/api/me` (`network`, built in `views.student_network`):
   - each course part as an idea, with `imp` its importance (the map's normalised importance);
   - `band` its topic, and `concept` its concept's name;
   - `q` the part's intuition question, and `d` its description;
   - the pack's edges.
2. **Levels only, never a probability (0024 holds).** The preview coloured each idea continuously from the model's probability. Here each level sits at a fixed point on the same ramp: new and needs review at the red end, developing at yellow, secure at green. "Not started" is grey, and "taught in class, not yet checked" is grey with a dashed ring. No probability reaches the page.
3. **The test chip** ("In Friday's test") shows when a test or assignment covering the idea is due within `reminders.days_ahead` (7) days, so the weekday is never ambiguous.
4. **The site's fonts** (Atkinson Hyperlegible Next and Newsreader), not IBM Plex from Google Fonts. Nothing leaves the origin, and the scripts and styles are files, as the Content-Security-Policy requires.
5. **What changes in 0024.** This map uses a red-to-green ramp, and its card has a shadow and rounded corners: Vishnu's design call. The level is also given in words on every card and in each circle's accessible label, so nothing depends on seeing colour. The public course map (`/map`) and the teacher page are unchanged.

## Alternatives considered

- **Colour from the probability, as in the preview.** It breaks "never a probability" (0024).
- **IBM Plex from Google Fonts.** The policy blocks it, and 0024 keeps every request on the origin.

## Consequences

- The red-to-green ramp reads as a verdict, and it is harder for red-green colour-blind students. The words on every card and label are the fallback.
- The forgetting fade on the old map (fainter when answered long ago) is not drawn; the card's note says when the idea was last answered.
- `scripts/check_contrast.py` does not check this map's own palette.

## Verification

`tests/test_web_student.py`:
- every part is an idea with a level and no probability;
- edges and bands come from the pack only;
- a test this week tags its parts;
- the page loads `network.js`, not `graph.js`.

`tests/test_web_browser.py` (with Chromium): the page draws one circle per part, the note in the accessible label, and the legend.

## What would change our mind

Students reading the red end as "bad at", or colour-blind students not able to tell the levels apart.
