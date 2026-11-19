# 0009. Cap teach_point at 120 words under a longer answer length

- **Status:** Proposed
- **Date:** 2026-11-18
- **Pull request:** #52
- **Step:** [05o](../build/steps/05o-reply-style-fixes.md) (issues #38, #39)

## Context

A student can ask for shorter or more detailed replies; the chatbot saves this as `answer_length`. Step 05j made `teach_point`'s word budget equal to that length. A student who asks for "much more detail" (say 300 words) would turn each point into a long explanation of several ideas, against the one-point-per-message rule. The diagram cue (#39) was confirmed as built.

## Decision

`teach_point`'s `max_words` is the student's `answer_length` when that is below `points.max_words` (80), and otherwise the student's length up to `points.max_words_requested = 120` (equal to `style.max_words`). Other steps take the student's length as before. The setting is a **judgement call, starting value**, and `load_settings` requires it to be at least `points.max_words`.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Rey, Beege, Nebel, Wirzberger, Schmitt & Schneider (2019), *Educational Psychology Review* | Meaningful, learner-paced segments improve retention and transfer and reduce cognitive load. | Meta-analysis | Mostly multimedia learning, not chat. |
| Kalyuga, Ayres, Chandler & Sweller (2003), *Educational Psychologist* | Full explanations can slow down learners who already know the material (expertise reversal). | Review of experiments | Mostly technical domains. |

The 120-word value has no source; it matches the default reply ceiling.

## Alternatives considered

- **No cap.** A student's request would turn one point into several.
- **Cap at 80 even when the student asks for more.** Refuses what the student asked for. The 120 cap honours the request as far as one point allows, and the chatbot can offer the next point instead.

## Consequences

A student who sets a length above 120 gets one point of up to 120 words, then the check; they are never refused. No migration; the instruction word count is unchanged.

## Verification

`tests/test_reply_style.py` (4 tests) and the `reply_style` run in `scripts/check_mcp.py`: length 50 gives 50, 200 gives 120; rebuild identical.

## What would change our mind

Evidence from real use that students want longer single-point explanations, or that a longer cap does not hurt retention.
