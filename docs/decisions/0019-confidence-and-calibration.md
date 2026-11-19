# 0019. Ask "how sure are you?" after a check and show a calibration line

- **Status:** Proposed; when it is asked is amended by [0027](0027-confidence-after-rapid-guesses.md)
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (new student-facing behaviour; his design of 18 November)
- **Pull request:** #62
- **Step:** [05z](../build/steps/05z-calibration.md) (audit item C7)

## Context

The research review names calibration, the gap between how sure a student feels and how often they are right, as the signature measure for AI literacy and for the "appropriate reliance" the product is about, and cognitive forcing (commit before the answer is revealed) as one of the few things shown to reduce over-reliance. Synapse recorded no confidence at all.

## Decision

After an answer to a check, a review or a prerequisite check, ask "How sure are you: guess, fairly sure or certain?" before the feedback. Because the answer arrives at the start of the next reply, the server records and scores the answer, computes the whole reply as usual, and **holds it back one turn** while it asks; the next call (with `this_message.confidence`) stores the rating and delivers the held reply. Asking is optional and free to skip, sparing (at most six a session, two skips in a row stop it for the session), and never on ordinary chat, a pre-question, a how-AI-works check, in long-session or rushing mode, or after "just show me". The rating is an event stored apart from the answer and **never enters `p_known`**. The progress view carries one calibration line, per level, after at least five rated answers in that level.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Fernandes et al. (2025), CHI | AI use raised task scores but inflated self-estimates; higher AI literacy predicted worse calibration. | Single research group (seen via a secondary paper) | University samples; no validated reliance instrument exists. |
| Buçinca, Malaya & Gajos (2021), *PACM HCI* (CSCW) | Cognitive forcing (commit before seeing the AI's recommendation) reduced over-reliance, and was liked less. | Experiments (N = 199 and 113) | Decision tasks with AI advice, not revision checks. |
| Research review, Summary §3.2 principle 3 and §6(e) | Calibration should be a first-class output; individual scores at small counts are unreliable. | Our own synthesis and arithmetic | Not published as such. |
| ICO Children's Code, Standard 5 | Do not turn a measure into pressure. | Regulatory guidance | Hence optional and free to skip. |
| Butterfield & Metcalfe (2001) | High-confidence errors are corrected well when feedback follows: **not built**, because the A-level evidence is thin. | Lab experiments | Facts, not exam skills. |

The limits (six a session, two skips, five answers a group) are **judgement calls, starting values**; five answers a group is Vishnu's rule.

## Alternatives considered

- **Ask before the question is shown.** A confidence in advance is a different thing (prediction); the research is about committing to an answer.
- **Ask on every message.** A hurdle and noise.
- **Feed confidence into the learner model** (a high-confidence error weighs more). No evidence for the weights, and it would let a self-report move a performance estimate.
- **Hold the reply in the chatbot** (ask it to wait before calling the tool). The chatbot must call the tool first, every reply (rule 1).

## Consequences

- A check answer now takes one extra short exchange; feedback arrives one turn later. This is the cost of the design, and the main thing to watch in the dry run.
- A student sees a calibration line only after five rated answers in a level.
- `confidence_log` (migration **019**); instructions stay at 899 of 900 words (the new move section is 15 words; I trimmed 16 elsewhere without changing meaning).
- The scripted check harness answers with `confidence: none`, standing in for a chatbot that does not ask.
- **Open:** whether the extra turn costs more in engagement than the calibration feedback gives is untested.

## Verification

`tests/test_calibration.py` (14 tests): the reply asks and holds the feedback; the held plan is delivered and the rating stored; skipping is free; two students with identical answers and different ratings have identical state; a confidence sent with the answer is stored without asking; not asked after a pre-question or on ordinary chat; the skip streak and per-session limits; the line appears at five answers and shows one part per level; skipped asks are not counted; an unanswered ask is dropped after the session gap; deletion removes ratings. `scripts/check_mcp.py` (calibration run); rebuild identical.

## What would change our mind

A pilot showing students skip it nearly always, find it irritating, or that the line does not change how they judge their own answers.
