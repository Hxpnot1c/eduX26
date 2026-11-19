# 0014. Ask and Verify are formative practice feedback, and asking for sources earns nothing alone

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (changes student-facing wording; decided 18 November)
- **Pull request:** #57
- **Step:** [05y](../build/steps/05y-formative-literacy-wording.md) (audit item C3)

## Context

Ask and Verify are shown to a student as levels (new, developing, secure) built from a handful of chatbot-labelled moments. The audit found three problems. A level from about four items has a standard error near 0.25, so it can look more exact than it is. The Ask score gave `asks_sources` the same credit as the other three features, so a student could raise Ask by asking a chatbot for sources, which invites invented citations (in one study 39.8% of 400 references from eight free chatbots were erroneous or fabricated) and is not checking. And a score based on how a question is phrased risks penalising English-as-an-additional-language writers.

## Decision

1. The student view keeps the level but shows the evidence behind it (checks, over how many days) and calls it formative: "practice feedback, not a grade". Teacher aggregates are unchanged.
2. `asks_sources` counts towards Ask only when the student has checked a claim (Verify evidence) earlier in the session.
3. The chatbot is told to judge question features by what the question asks for, never its wording, length, polish or English.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Research summary §6(e) (our own arithmetic) | At about 16 items an individual reliance score has a standard error near 0.25; shrinkage and counts are needed. | Our own calculation | Not published. |
| Study of prompt length and grade (F1-10 in the review) | Prompt length was unrelated to grade (r = .036). | Single study | Not about A-level economics. |
| F5-19, F5-18 in the review; Liang et al. (2023) on detector bias | Scoring from prose style can disadvantage non-native English writers; score structured judgements. | Several studies | Detectors, not question features. |
| Cabezas-Clavijo & Sidorenko-Bautista (2025), arXiv 2505.18059 | Of 400 references from 8 free chatbots, 39.8% were erroneous or fabricated. | Descriptive audit | Chatbots change quickly. |
| Shute (2011) stealth assessment; review W1-17, W1-18 | Stealth-assessment validity evidence is thin and unreplicated, so levels should be formative. | Reviews | Mostly games. |

## Alternatives considered

- **Drop the Ask level from the student view.** Loses a useful nudge; the evidence line gives the honesty.
- **Remove `asks_sources` from the pack.** It is still a good habit when paired with checking.
- **Show counts instead of levels.** The levels drive the practice feedback; counts are shown beside them.

## Consequences

- A student who only asks for sources scores at most three of four on Ask, so Ask cannot reach secure by that route alone.
- The progress view is about 100 characters larger (2,275 of 2,400 for the longest demo case).
- No migration; instructions unchanged (899 of 900).

## Verification

`tests/test_literacy_wording.py` (5 tests); `scripts/check_mcp.py` passes; rebuild identical.

## What would change our mind

A labelling-agreement study (the review recommends a double-coded gold set of about 100 turns) showing the features are labelled reliably across writers, or an EAL audit showing the opposite.

## Open

An EAL subgroup audit of the labelling, a plain-language mode and a plain student notice of what is recorded (Children's Code Standard 11) are still to do.
