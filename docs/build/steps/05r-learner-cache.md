# Step 05r: Cache the per-session learner offsets (#34)

Branch `build/learner-cache`, from `main` after step 05q.

## Built
Migration **017** `learner_offset_cache(student_id, session_id, settings_hash, learn_state, learn_offset, learn_n, covered_offset, covered_n, uncovered_offset, uncovered_n)` (two columns more than planned: `settings_hash`, so the cache is used only under the settings it was computed with, and `learn_state`, the running statistics at a session boundary). `learning_offset` now keeps the count, the recency-weighted sums and the parts seen, and updates them one piece at a time, resuming from the last cached boundary; `starting_offsets` caches its two offsets per session. Dropped when it could be stale: an event earlier than the cached sessions, a change of coverage or class membership, a rebuild, deleting the student, other settings, and always (not cached) while the class estimate is on. Decision [0016](../../decisions/0016-learner-offset-cache.md). Tests: `tests/test_offset_cache.py` compares against the previous implementation (kept in the test file) after every session of a synthetic history; `scripts/time_offsets.py` gives the timing; `check_mcp` compares cached and uncached for the demo students.

## What
`learner.learning_offset` (step 05h) re-reads every earlier session's evidence each time evidence is applied, live and on rebuild. That's about sessions × evidence per call. Step 05q's two starting offsets work the same way.

Cache them per (student, session) in a derived table:
- the learning-rate offset step;
- the covered and not-covered starting offsets.

The table is filled in session order and cleared on rebuild. Each new session adds only its own step, computed from the previous session's cached values plus the evidence between.

## Why
- #34: `tutor_turn`'s median is about 22 ms at demo scale, but the cost grows with real use.
- The values are pure functions of earlier events, so a cache that's cleared and refilled on rebuild gives the same state.

## Files
- **Migration:** the next free number when you start. It adds `learner_offset_cache(student_id, session_id, learn_offset, learn_n, covered_offset, covered_n, uncovered_offset, uncovered_n)`.
- `edux/learner.py`:
  - `learning_offset` and `starting_offsets` read the cache, and fill it in order on a miss;
  - `rebuild_state` clears the student's rows first.
- `scripts/check_mcp.py`: cached and uncached results match for every demo student, and for a long synthetic history.
- A timing script, `scripts/time_offsets.py`: a synthetic student with a long history (e.g. 200 sessions × 10 answers), timed before and after.
- **Docs:** this file; `reference/database.md` (the cache is derived, not events); `reference/learner-model.md` (one line).

## Settings
None.

## Commits
1. `refactor(learner): cache learner offsets per session` (migration)
2. `chore(scripts): time offsets on a long synthetic history`
3. `chore(scripts): check cached and uncached offsets match`
4. `docs(reference): note the offset cache`

## Done when
- Cached and uncached offsets match exactly.
- The PR shows the before and after timing for the long synthetic history.
- Issue #34 is closed with a one-line comment.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (unchanged).

## Tests
`scripts/check_mcp.py`: cached equals uncached. `scripts/time_offsets.py`: the timing in the PR.
