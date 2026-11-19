# Step 05k: Fixes to tune-from-research (#23, #24, #26)

Branch `build/fix-tune-from-research`, from `main`. Follow-up to step [05f](05f-tune-from-research.md) (PR #22, merged).

## What
1. **#23 `review_when_below`: confirm the built behaviour.** There's no code change, only a check that pins it down.
   - A part already at or below 0.50 (or with no forgetting clock) keeps the share gap.
   - `min_gap_days` floors the threshold crossing as well as the share gap.
2. **#26 `data.secure` is judged on the level before this answer.**
   - In `plan.choose`, `secure` is set when the answer is right and the part was secure **before** the answer was applied. That value is `evidence_derived.p_before`, which is already stored.
   - The answer that makes a part secure still gets its one-line why.
   - Open answers at secure keep the `points_met` line; only the why is dropped (unchanged).
3. **#24 is replaced by step [05s](05s-fatigue-time-on-task.md)**, the fatigue redesign. `session.fatigue_threshold` stays as it is here, and 05s removes it.

## Why, with sources
- **Feedback on right answers helps most when the learner was unsure** (Butler, Karpicke & Roediger, 2008; Wisniewski, Zierer & Hattie, 2020). The answer that tips a part to secure may be a lucky guess.
- **#23:** a part already below 0.50 being due straight away would flood `reviews_due` with parts the student is learning anyway.

## Files
- `edux/plan.py`: in `choose`, read `p_before` for the answer's evidence (from `evidence_derived`, or `turn` before the update) in place of `turn.p` after it.
- `edux/learner.py`: a small reader for an evidence row's `p_before`, if one isn't already exposed.
- `tests/test_secure_flag_and_reviews.py` (pytest, no server needed; replaces the planned `check_mcp` checks):
  - #23: a part at or below 0.50 keeps the share gap; a crossing sooner than `min_gap_days` is floored;
  - #26: the answer that makes a part secure was not secure before it; the next right answer is on a secure part.
- `edux/service.py`: `tutor_turn` reads the stored `p_before` after recording the answer and passes it to the plan.
- **Docs:** this file; `reference/learner-model.md` (the `secure` flag and the `review_when_below` edge cases); 05f is already written to match.

## Settings
None.

## Commits
1. `fix(plan): judge feedback's secure flag on the level before the answer`
2. `chore(scripts): check review_when_below edge cases and the secure flag`
3. `docs(reference): note when feedback counts a part as secure`

## Done when
- The answer that tips a part to secure gets its why. A right answer on an already-secure part doesn't.
- The #23 edge cases are checked.
- Issues: #23 and #26 closed with a one-line comment; #24 closed pointing to 05s.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (unchanged).

## Tests
In `scripts/check_mcp.py`, as listed under Files.
