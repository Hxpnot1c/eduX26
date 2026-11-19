# 0016. Cache the per-session learner offsets

- **Status:** Proposed
- **Date:** 2026-11-19
- **Pull request:** #59
- **Step:** [05r](../build/steps/05r-learner-cache.md) (issue #34; Part 2 C)

## Context

`learner.learning_offset` re-read every earlier session's evidence and, for each session boundary, re-filtered and re-summed the whole prefix: work that grows with sessions × evidence on every call. It runs every time an answer is applied, live and on rebuild. Step 05q added two starting offsets that read the logs the same way. Measured on one synthetic student with 600 answers over 60 sessions (synthetic students on the example pack: this times the code and says nothing about learning), applying one more answer cost 113.6 ms and a rebuild 32.9 seconds; a history of 2,000 answers did not finish building in four minutes.

## Decision

Cache the offsets per session in a derived table (migration 017). The learning-rate offset keeps its running statistics (count, recency-weighted sums, parts seen, offset) at each session boundary and resumes from the last one, so a call reads only the sessions since. The recency-weighted mean is updated one piece at a time (`S = S × r + x`, `W = W × r + 1`, `r = 0.5^(1/half-life)`), which equals the direct sum. The two starting offsets are cached per session. The cache is derived, not events: cleared on rebuild and with the student, used only under the settings hash it was written with, and dropped for an out-of-order event, a change of coverage or class, and never used while the school's class estimate is on (that estimate depends on other students).

## Research basis

None: this is a performance change that must give the same answers. The method is incremental updating of an exponentially weighted mean (a standard identity), checked against the previous code.

## Alternatives considered

- **In-memory cache only.** Lost on restart and on a second process; the rebuild would stay slow.
- **Store the offset per event.** Larger and still stale on out-of-order events.
- **Leave it.** Fine at demo scale (22 ms median), not for a class of students over a year.

## Consequences

| Synthetic student, 600 answers, 60 sessions | Before | After |
|---|---|---|
| Apply one more answer (per turn) | 113.6 ms | 3.4 ms |
| Current learning-rate offset | 111.9 ms | 2.4 ms |
| Rebuild the whole history | 32.9 s | 1.9 s |

(Both runs shared the machine, so read them as an order of magnitude: about 30 to 40 times for a turn and 17 times for a rebuild.) The cached and uncached values agree to 1e-9 after every session of a synthetic history (tests compare against the previous implementation kept in the test file), and rebuild gives the same cache rows. Floating-point updates are in the same order live and on rebuild, so rebuild stays identical. Migration **017**. No change to what a student sees; instructions unchanged.

## Verification

`tests/test_offset_cache.py` (10 tests); `scripts/check_mcp.py` (cached and uncached offsets match for the three demo students); `scripts/time_offsets.py` for the timing; rebuild identical.

## What would change our mind

A cache bug found in real use. The cache can always be dropped (`DELETE FROM learner_offset_cache`), and the values recomputed from the logs.
