# 0025. Fade learnt parts towards their normal start, show "needs review", and review before a part fades

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (decided 19 November, after the code freeze)
- **Pull request:** #82
- **Research:** [research.md](../build/reference/research.md) row 53 (patch 0005, held until now); supersedes row 70

## Context

`p_now = p_known × 0.5^(d/h)` faded every answered part towards 0, so a part answered right once soon read below an untouched one (0.30). A simulation on the stack tip (25 synthetic students, 8 weeks, `example-mini`) found that by week 8, 90% of (student, taught part) pairs read *new*. Of the parts reading *new* that had been answered right at least once, 134 of 136 were not due for review: the `recall_below` review applies only while `p_known` is above 0.50, and below that a part waits for the share gap (about 20 days with a June exam). The overnight research had already found the fix: decaying towards the starting estimate cut day-30 inversions from 0.82–1.00 to 0.03–0.26 and raised AUC from 0.48–0.59 to 0.62–0.71 (patch 0005, held).

## Decision

1. **Fade towards the normal start, not 0.** `p_now = floor + (p_known − floor) × 0.5^(d/h)`, with no decay before the first right answer, as before. The floor (`learner.decay_floor`) is the part's normal start (`initial_state`, 0.30 on the example pack), the same for every student. Ask and Verify fade towards `decay.literacy_floor` = 0, as in patch 0005, so passing once doesn't keep a student near secure. How-AI-works parts use their normal start. Every `p_now` call site uses the floor, and `days_until_below` becomes `h × log2((p_known − floor) / (θ − floor))`, or `None` when θ ≤ floor. `_floored`, the minimal decay-to-prior for unanswered covered parts, is now part of the floor and was removed; its guarantee is kept as a test. The fade is symmetric: a `p_known` below the floor, after a later wrong answer, rises towards it, so an old wrong answer counts for less too (Vishnu's call, as in patch 0005). Settings: `decay.floor = "start"` (`"zero"` keeps the old rule), `decay.literacy_floor = 0.0`, `protocol = "v0.4"`.
2. **Show "needs review", not "new", for a part that has faded.** `shown_level` returns `needs_review` for a part answered right at least once (`last_correct` set) whose `p_now` is below `levels.new`. Before the first answer it still returns `taught_in_class` or `new`. *new* now means "not shown yet". This is a display state only: `level()`, the planner, the prerequisite gates and the queue band still read the number. It is used in the progress results (tree, levers, reviews), the student's page ("needs review": new's colours with a centre mark) and the progress tool's text for the chatbot. On the teacher's page a part keeps its band, and students who need review do not count as practised. When at least `coverage.class_min_students` (5) of those who answered need review, the cell's note says "5 or more need review", never the count. With the answered count beside it, the count would show a small group by subtraction (decision 0024).
3. **Review a learnt part before it fades to new.** After a right answer, alongside the `recall_below` check, the part is also due when `p_now` is expected to fall below `levels.new`, if that comes before the share gap, with reason `fading`. `min_gap_days`, the 3-a-reply cap and the other rules are unchanged. Setting: `scheduling.review_before_new = true` (judgement call, mirrors `review_when_below`). Because `levels.new` (0.40) is below `review_when_below` (0.50), this only decides when `p_known` is in (0.40, 0.50] after the answer.

**Why the normal start and not the covered start.** The brief asked for the part's base start (normal start or covered start). The covered start is about 0.41 with `coverage.boost_logit = 0.5`, which is above `levels.new` (0.40). With that floor, a covered part could never read new again. The pre-question stopped for untouched covered parts (it fires below 0.40; `scripts/check_mcp.py` failed 5 checks). A covered part answered right once would show *developing* for good, never *needs review*. And no `fading` review could be queued, since θ ≤ floor. Vishnu chose the normal start (19 Nov), which is also what patch 0005 used. The coverage boost still sets where a covered part starts, and it fades from there.

## Research basis

research.md row 53: the overnight simulation (w3-06-01, w3-06-08, w3-06-09, w4-fix-core-4) and patch 0005. `literacy_floor = 0` and the symmetric fade follow patch 0005. `review_before_new` and the display state are judgement calls. All numbers below are from **synthetic students on the example pack**: they show how the rules behave, never a learning gain.

**Class simulation** (`scripts/simulate_class_levels.py`, 25 students, 8 weeks, final exam only). Share of (student, taught part) pairs at week 8:

| | by the number: new / developing / secure | as shown: new / needs review / developing / secure | reviews per student that week | reviews due, not done, per student |
|---|---|---|---|---|
| Before (main, 5f30b4d) | 0.90 / 0.09 / 0.01 | 0.90 / – / 0.09 / 0.01 | 2.76 | 0.20 |
| Changes 1 and 2 | 0.84 / 0.15 / 0.01 | 0.22 / 0.62 / 0.15 / 0.01 | 2.56 | 0.32 |
| After (all three) | 0.84 / 0.15 / 0.01 | 0.22 / 0.63 / 0.15 / 0.01 | 2.44 | 0.24 |

With a half-term mock on the last day, week 8 goes from 0.89 / 0.03 / 0.08 by the number to 0.62 / 0.27 / 0.11 (shown: 0.11 new, 0.52 needs review). The backlog of due reviews not done is 7.08 a student in all three versions: the mock's schedule fills the 3-a-session cap, not the fading review.

**Review-threshold simulation** (`scripts/simulate_review_threshold.py`, 60 students a row, 90 days):

| `review_when_below` | | reviews a week | true retention | false secure | truly secure | due reviews over the cap |
|---|---|---|---|---|---|---|
| 0.50 | before | 4.83 ± 0.06 | 0.202 ± 0.010 | 0.00 | 0.73 ± 0.09 | 44.9 ± 1.0 |
| 0.50 | after | 4.99 ± 0.06 | 0.221 ± 0.014 | 0.00 | 1.07 ± 0.11 | 50.1 ± 0.9 |
| 0.75 | before | 4.81 ± 0.06 | 0.182 ± 0.009 | 0.00 | 0.45 ± 0.08 | 43.5 ± 1.0 |
| 0.75 | after | 4.95 ± 0.06 | 0.211 ± 0.012 | 0.00 | 1.13 ± 0.10 | 48.0 ± 0.8 |

Changes 1 and 2 alone gave 4.96 / 0.220 / 1.05 / 49.2 at 0.50, so the fading review adds about 0.03 reviews a week and 0.9 over the cap.

## What it shows, and what it does not

- The display now says what happened: about two thirds of taught pairs read *needs review* rather than *new*, and *new* is left for parts never got right (about a fifth).
- **By the number most pairs still read new** (84%), because the floor (0.30) is below `levels.new` (0.40). That is intended: a part answered right weeks ago is not known now, and the display carries the difference. Secure stays rare in this class run (1%) because the 3-a-session cap and the 2-day half-life limit how much review sticks; the review-threshold write-up names those as the next levers.
- The fading review rarely decides, because it only applies between 0.40 and 0.50. It did not make the backlog grow week on week.
- **Review timing matters more than the floor for "secure".** Vishnu's earlier run with patch 0005's formula monkeypatched into `p_now` gave 82 / 10 / 8 by the number at week 8, against 84 / 15 / 1 here. Rerunning this branch with `days_until_below` forced back to the old formula (no floor) gives 81 / 11 / 8 at week 8 and 3.24 reviews a student that week (against 2.44): the old formula puts the `recall_below` crossing sooner, so parts are reviewed sooner and more stay secure. The floored formula is the correct crossing time for the new `p_now`, so it was kept; when `recall_below` should fire is a separate question (see what would change our mind).

## What stays held

- Patch 0005's **"a part never answered right reads at most its starting estimate"**. It is not part of this change: the exchange-nudge ceiling (decision 0003) already stops talk alone from lifting a part past new.
- A floor that keeps any of the coverage boost.

## Alternatives considered

- **The covered start as the floor** (the brief as written): rejected for the reasons above.
- **Covered start capped just under `levels.new`:** keeps a little of the boost, but adds a second judgement-call number.
- **Lower `coverage.boost_logit`** so the covered start is below 0.40: changes another setting's meaning for this one.
- **Fade only downwards** (a `p_known` below the floor stays there): keeps old wrong answers at full weight; patch 0005 and the research simulation used the symmetric fade.

## Consequences

- Later posteriors change, because updates read `p_now` before applying evidence: `protocol` v0.4. Stored data: no migration (as for v0.3, decision 0003). Events keep their `protocol` and `settings_hash`; existing learner state should be rebuilt (`python -m edux.cli rebuild`), which re-scores them under v0.4 and gives the same state twice (tested).
- The demo students change: demo-secure's part answered once 60 days ago reads *needs review* (0.24; was *new*, 0.00) and its part answered five times reads *developing* (0.55; was *new*, 0.38), which matches the seed's own description. demo-weak's parts no longer sit near 0.
- The progress views are slower: the every-part view of a demo student goes from about 23 to 34 ms on the example pack, from the floor and "answered right" lookups. The 384-part scale test still passes.

## Verification

`tests/test_decay_floor.py`, `tests/test_needs_review.py`, `tests/test_fading_review.py`, the class simulation's smoke test in `tests/test_simulation_script.py`, the existing rebuild tests, the result-size checks, `scripts/check_mcp.py` and `scripts/check_contrast.py`.

## What would change our mind

Real students' review answers showing how fast A-level parts are forgotten (a different half-life or floor); a teacher finding *needs review* confusing next to *new*; the review backlog growing once real classes use it; or a decision to review sooner (a higher `review_when_below` or an earlier crossing), which the simulation above suggests would keep more parts secure for about one more review a student a week.
