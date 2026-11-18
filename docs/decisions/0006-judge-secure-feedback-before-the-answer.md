# 0006. Judge feedback's "secure" flag on the level before the answer

- **Status:** Proposed
- **Date:** 2026-11-18
- **Pull request:** #49
- **Step:** [05k](../build/steps/05k-tune-from-research-fixes.md) (issues #23, #26)

## Context

The `feedback` move skips its one-line "why" for a right answer on a part that is `secure`. `plan.choose` read the part's level *after* the answer had been applied. The right answer that lifts a part past 0.75 therefore counted as "already secure" and lost its why, even though the student was not secure when they answered and the answer may have been a lucky guess.

## Decision

`service.tutor_turn` reads the stored `p_before` for the answer just recorded (`learner.answer_p_before`, from `evidence_derived`) and passes it to the plan. `plan.choose` sets `secure` only when the answer is right and the part was secure *before* it. If no `p_before` exists the plan falls back to the old reading. The review-threshold behaviour (#23) is unchanged and is now pinned by tests: a part at or below `review_when_below` keeps the share gap, and `min_gap_days` floors a crossing that would come sooner.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Butler, Karpicke & Roediger (2008), *Journal of Experimental Psychology: Applied* | Feedback on a correct answer helps most when the learner was unsure. | Single series of experiments | Adults, lab tasks. |
| Wisniewski, Zierer & Hattie (2020), *Frontiers in Psychology* | Feedback has a medium effect (d = 0.48) that depends on how much information it carries. | Meta-analysis | Not about chatbot tutors. |

Both are already in `docs/build/reference/research.md`. No new numbers.

## Alternatives considered

- **Always give the why.** Simpler, but it adds a line to every right answer on a secure part, where it carries no information and costs words.
- **Use a higher threshold for the flag.** Needs a new number with no source.

## Consequences

The answer that tips a part to secure now gets its why; the next right answer on that part does not. A student sees at most one extra line, once per part. No migration, no setting, no change to the instruction word count.

## Verification

`tests/test_secure_flag_and_reviews.py` (6 tests); `scripts/check_mcp.py` and `pytest` pass; rebuild identical.

## What would change our mind

If students find the extra why on the tipping answer unhelpful, restore the old reading and keep the tests for the review edge cases.
