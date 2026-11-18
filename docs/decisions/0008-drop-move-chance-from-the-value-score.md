# 0008. Drop the learning-chance factor from the priority value score

- **Status:** Proposed
- **Date:** 2026-11-18
- **Pull request:** #51
- **Step:** [05n](../build/steps/05n-priorities-fixes.md) (issues #35, #36)

## Context

Step 05i ranks the add-on steps (a due review, an extend) by `value = move_chance × Σ weight(kind) × urgency × (1 − p on its date)`, over the final exam and the student's own tests. `move_chance` was the student's BKT learn rate. There is one learn rate for every evidence type, so it is the same number for every step. A constant factor scales every value equally and cannot change which step wins.

## Decision

Remove `learner.move_chance`. `learner.step_value(student_id, part_id, at)` returns the sum alone. The `considered` values logged in `issued_plan` change scale but not order. Per-type learn rates stay a research item in `later.md`. The five edge choices in #36 are confirmed as built and pinned by tests: no final exam ahead counts the final at `urgency_floor` with today's p; the reason names the assessment that adds most; prerequisite repairs are ordered by value × link weight; partial topic matches add the test and return the rest as unmatched; the CLI's top three are due reviews only.

## Research basis

None needed: a constant factor cannot change an argmax. Hand-set priorities until there is data follow Doroudi, Aleven & Brunskill (2019), *International Journal of Artificial Intelligence in Education*, which found hand-tuned policies hard to beat without data (already cited in `research.md`).

## Alternatives considered

- **Keep the factor.** Harmless, but it implies the score accounts for how much a step teaches, which it does not.
- **Make the learn rate per evidence type now.** No evidence on whether review, extend and check differ in learning gain for this age group; it would invent numbers.

## Consequences

No student-visible change and no change to which step is chosen. `learning_offset` is no longer read by the priority code, which removes one hidden dependency on the personalisation switch. No setting, migration or word-count change.

## Verification

`tests/test_priorities.py` (4 tests); `pytest` and `scripts/check_mcp.py` pass, including the priorities run; rebuild identical.

## What would change our mind

Evidence that different step types teach different amounts. Then add a per-type factor, with the source in `research.md`.
