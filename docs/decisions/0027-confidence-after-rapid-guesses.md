# 0027. Ask "how sure are you?" only after rapid guesses, and let the break offer wait

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (his rule of 19 November)
- **Pull request:** see the branch `build/confidence-after-rapid`
- **Amends:** [0019](0019-confidence-and-calibration.md) (when the question is asked; the calibration line and the "never feeds `p_known`" rule are unchanged)

## Context

Decision 0019 asked "how sure are you?" after any answer to a check, a review or a prerequisite check, up to six times a session. Every such answer then took one extra exchange. Vishnu wants the question kept for the moment it is most useful: when the student seems to be answering without reading.

The two rules clashed. Rushing mode (`fatigue.rapid_guesses = 2`) started on the second rapid guess in a session and offered a break or a quick burst at once, and 0019 never asked confidence while rushing.

## Decision

1. **When it is asked.** Only when an answer to a check, a review or a prerequisite check makes `confidence.after_rapid` (2) rapid-guess answers to such checks **in a row** in the session. A rapid guess is the existing rule (`learner.rapid_guess`: faster than reading the question at `fatigue.reading_wpm` plus typing the answer at `fatigue.typing_wpm`). It is never asked on an ordinary check, a pre-question, a how-AI-works check, ordinary chat or after "just show me".
2. **In a row.** It is counted per answer (one exchange), not per stored point. Only check, review and prerequisite answers move the run: a rapid one adds one, a slower one resets it to 0. Ordinary chat, pre-questions and how-AI-works answers in between leave it. A new session starts at 0.
3. **Once a session.** `confidence.max_per_session = 1`.
4. **Skips.** `confidence.stop_after_skips = 2` is now counted across sessions: two skipped asks in a row (necessarily in two sessions) stop the question for good. A rating breaks the streak. With one ask a session, a per-session streak could never be reached. Asks are counted per answer: one skipped multi-point answer is one skip, not one per point (this fixes a miscount from 0019).
5. **The clash with rushing.** Rushing mode itself is unchanged: the second rapid guess in a session still starts it, with its slip, shorter replies and the rest, so `p_known` and rebuild are untouched. Only the plan changes. On the turn the question is asked, the held reply leaves out the break offer and the offer is not marked as made. The offer then waits until rushing continues, meaning a later answer is again a rapid guess. A slower answer, or chat, keeps it waiting. Long-session mode (from `fatigue.mode_minutes`) is never held back.
6. **Long session plus rapid guesses.** The question is still asked: the trigger is the rushing, not the clock.
7. **Unchanged.** The rating never feeds `p_known`. A confidence the chatbot sends with an answer is stored without asking. `EDUX_CONFIDENCE` still switches it off or on.

## Research basis

The same as 0019 (cognitive forcing: Buçinca, Malaya & Gajos, 2021), applied where it matters most. A rapid guess is answered faster than the question can be read (Wise & Kong, 2005), which is the moment a prompt to commit and reflect has most to work on. **Asking only then is a judgement call** (Vishnu, 19 November); no study compares asking always with asking after rapid guesses.

## Alternatives considered

- **Ask first, then offer the break on the same reply.** Two stop steps in one reply; the student can only answer one.
- **Move rushing mode to the third rapid guess.** It would change which answers count as fatigued, and so `p_known` and rebuild.
- **Keep a per-session skip streak.** With one ask a session it could never trigger.

## Consequences

- The calibration line (five rated answers in a level) will now fill slowly, over at least five sessions with rushing in them, and the ratings lean towards rushed answers, so likely towards "guess". The question is now mainly a commit-before-feedback nudge rather than a calibration measure.
- A chatbot that does not send `this_message.words` never produces a rapid guess, so its students are never asked.
- A student who rushes gets the break offer one rapid answer later than before, if they keep rushing.

## Verification

`tests/test_calibration.py`: an ordinary check is never asked; the second rapid check in a row asks and holds the break offer; the held reply has no offer; a slower answer keeps it waiting; a rapid one brings it; rapid guesses not in a row get the offer as before and no question; once a session and again next session; two skips across sessions stop it and a rating breaks the streak; a multi-point ask counts once; long-session time is never held; the rating never changes `p_known`; the settings refuse `after_rapid < 1`. `scripts/check_mcp.py` calibration run sends two one-word answers at once.

## What would change our mind

Pilot data showing students rarely rush (the question is then almost never asked), or that being asked after rushing reads as a reprimand.
