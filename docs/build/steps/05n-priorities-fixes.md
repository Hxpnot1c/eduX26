# Step 05n: Fixes to priorities (#35, #36)

Branch `build/fix-priorities`, from `main`. Follow-up to step [05i](05i-priorities.md) (PR #37, merged).

## What
1. **#35: remove `move_chance` from the value score.** There is one learn rate for all evidence types, so it's the same for every step: it scales every value equally and never changes a choice. The score becomes:
   ```
   value = Σ over the final exam and the upcoming assessments covering the part
           [ weight(kind) × urgency(days to it) × (1 − p on its date) ]
   ```
   - `learner.move_chance` and its use in `step_value` and `plan` are removed.
   - `reference/learner-model.md` says why.
   - Per-type learn rates go to `later.md` as a research item.
2. **#36: confirm all five edge choices as built:**
   - with no final exam ahead, the final counts at `urgency_floor` with today's p;
   - `data.reason` names the assessment that adds most, on reviews only;
   - prerequisite repairs are ordered by value × link weight;
   - partial topic matches add the test and return the rest as `unmatched`;
   - the CLI's top three are due reviews only.

   The bridge reason and the CLI's four ending tiers come in step [05t](05t-bridge-ending.md).

## Why, with sources
- **A constant factor can't change an argmax.** No source is needed. Recorded in `reference/research.md` ("`move_chance` removed from the score").
- **Hand-set priorities until there's data** (Doroudi, Aleven & Brunskill, 2019). Unchanged.

## Files
- `edux/learner.py`: remove `move_chance`; `step_value` drops its chance argument.
- `edux/context_blocks.py`, `edux/plan.py`, `edux/cli.py`: callers updated. The `considered` values change scale but not order.
- `docs/build/steps/05i-priorities.md`: the formula, with a note pointing here.
- `docs/build/steps/later.md`: the per-type learn-rate research item is already listed by the docs PR. Update it if the wording changes.
- `scripts/check_mcp.py`: the priorities run, unchanged in outcome.
- **Docs:** this file; `reference/learner-model.md`.

## Settings
None.

## Commits
1. `refactor(learner): drop move_chance from the value score`
2. `docs(reference): explain why the value score has no learning chance`

## Done when
- Every priorities check gives the same picks as before.
- Issues #35 and #36 are closed with a one-line comment.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (unchanged).

## Tests
In `scripts/check_mcp.py` (`priorities`): same picks, same reasons.
