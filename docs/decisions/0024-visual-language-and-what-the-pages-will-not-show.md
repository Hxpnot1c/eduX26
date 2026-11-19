# 0024. Visual language, and what the pages will not show

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (what teachers may see is a product call; fonts are a design call)
- **Pull request:** #72 (tokens, type, key); applied by the map and dashboard pull requests

## Context
Three pages (a course map, a student page, a teacher page) show a child's learning record. Both how they look and what they leave out carry consequences: a dashboard can nudge, label and rank without anyone intending it.

## Decision: what the pages will not show
Taken from `personalisation.md` §5, the DfE product safety standards (10 and 13) and decision 0014:
- **No grade, prediction, single course score, ranking, streak, badge or comparison with other students.** Levels only, never a probability. A level always comes with its evidence (how many answers, how recently) because it is often based on very few.
- **An unchecked part is never "weak".** A part the class covered that the student has not answered on reads "taught in class, not yet checked".
- **Teachers see classes, not students.** Class-level only, cells under 5 students blank. Never a per-student record, chat text, confidence or calibration, fatigue, rapid guesses, learning speed, or any SEND, EAL or demographic data. A per-student view would need a DPIA first (05s).
- **No claim that the dashboards improve outcomes** (Kaliisa et al., 2023: limited evidence on achievement across 38 studies).
- **Nothing leaves the origin:** no CDN, font host, script or analytics.

## Decision: visual language
- **Surface:** warm paper, ink, 1px hairline rules; no gradients, shadows, rounded cards, icons or emoji. Structure from whitespace and a narrow label column beside a reading column.
- **Colour means one thing:** how well a part is known. Pale to deep for new, developing, secure, in a ramp that keeps its order in greyscale. Every level is repeated by ring and fill (ring only, half, solid), "taught in class, not yet checked" is a dashed ring, "no answers yet" a faint dot, so nothing depends on seeing colour. Edge type, when drawn, is carried by line style, never colour. One accent (vermilion) for focus, selection and "due now" only.
- **Type:** Atkinson Hyperlegible Next for interface text (designed for legibility; a sensible choice for a school product and for readers of English as an additional language) and Newsreader for headings. Both are SIL OFL 1.1, self-hosted as Latin subsets (about 100 KB), with the licence texts beside them. Deliberately not Inter, Roboto, Poppins or Space Grotesk.
- **Motion:** 120 ms state changes, none under `prefers-reduced-motion`. **Layout:** 8 px grid, 16 px gutters, list-first on a phone, a print stylesheet, light and dark schemes.

## Research basis
WCAG 2.2 (text 4.5:1, 7:1 for body ink; non-text 3:1); `scripts/check_contrast.py` enforces these for both schemes and checks the level fills keep their order in luminance. Atkinson Hyperlegible was designed with the Braille Institute for legibility; the evidence that it helps readers beyond people with low vision is **thin**, so the choice is defended on legibility and licence, not on a proven reading benefit. Not tested with real students or colour-blind users yet.

## Alternatives considered
A conventional dashboard (cards, gradients, a score ring): rejected, it invites exactly the grading and comparison the research warns against. Red/amber/green: rejected, it fails for common colour blindness and reads as a verdict. A third-party design system or icon set: rejected, extra requests and a look we cannot control.

## Consequences
Pages look unlike a typical dashboard and carry less decoration. The palette and type are tokens in one file; changing them is cheap, and the contrast check stops a weak palette.

## Verification
`tests/test_web_foundations.py` runs the contrast check and a negative test (a pale muted colour and two merged levels are caught). Headless screenshots at 390 and 1280 px, light and dark, reviewed by eye.

## What would change our mind
A user test showing the key or the rings are not understood, or that the margin-label layout hurts reading on small screens.
