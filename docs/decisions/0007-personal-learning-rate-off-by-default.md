# 0007. Recalibrate the personal learning rate and switch it off by default

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Vishnu (decided 18 November; confirm in review)
- **Pull request:** #50
- **Step:** [05m](../build/steps/05m-personal-learning-rate-fixes.md) (issues #31, #32; audit item C5)

## Context

Step 05h gave each student a learning-rate offset: if their answers are repeatedly better than the model expected, they are assumed to learn faster. It shipped on by default with settings the project's own simulation called "mostly noise" (shrinkage k = 20, scale 2.0, bounds 0.5 to 1.5, recency half-life 20). It also counted a part's first answer, which already feeds the starting-point adjustment, so "already knew it" was counted twice as "learns fast", and it let AI-literacy evidence move the rate used for course parts.

## Decision

1. **Recalibrate** to k = 400, scale 1.0, bounds 0.7 to 1.3 and recency half-life 100. `max_change_per_session` stays 0.25 and `down_change_factor` 2.0.
2. **Leave out each part's first answer** from the offset, and leave AI-literacy evidence out (it already was) so that AI-literacy parts learn at the population rate.
3. **Switch the offset off by default** (`personalisation.enabled = false`). `EDUX_PERSONALISATION=1` turns it on. This covers the learning-rate offset only: the starting-point adjustments (step 05q) stay on, because they use the student's own pre-teaching answers, only for their own teaching.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Koedinger et al. (2023), *PNAS* 120(13) | Across 27 datasets, learning rate was similar between students (about 0.1 log-odds per opportunity) while starting accuracy varied widely. | Large analysis; replicated | Online practice systems with feedback; the rate-spread result depends on how many practice opportunities are included. |
| Simpson, Norberg & Fancsali (2024), EDM | Student learning-rate variance was 37 to 430 times smaller than starting-knowledge variance. | Replication, one vendor | Maths topics. |
| Lee, Lichand et al. (2026), arXiv 2605.01690 | The learning-rate variance estimate is fragile: it grows sharply when practice sequences are truncated. | Preprint | Same data family. |
| Yudelson, Koedinger & Gordon (2013), AIED | In individualised BKT, student-specific learning speed helped prediction more than student-specific prior knowledge. | Single study | Older, smaller; points the other way. |
| Doroudi & Brunskill (2019), LAK | Population-fitted models can leave lower performers under-practised, so over-crediting is the more harmful mistake. | Simulation-based | Direction only; the factor of 2 is a judgement call. |
| ICO Age Appropriate Design Code, Standard 12 | Profiling options should be off by default unless there is a compelling reason in the child's best interests. | Regulatory guidance | Does not mention education specifically. |
| Our simulation (synthetic students on the example pack, never a learning gain) | After 48 answers, average surprise correlates only 0.10 to 0.23 with the true rate at research-sized spreads, implying k of 400 or more. | Simulation | Says nothing about real students. |

Labels: k = 400 and scale 1.0 are *from research spread plus our simulation*; the bounds are *from research* (about two standard deviations of the replicated spread); the half-life and `min_observations`, `min_parts` and `max_change_per_session` are *judgement calls, starting values*; the default-off is a judgement call about risk.

## Alternatives considered

- **Leave it on with the new values.** The offset would barely move, so it buys little while still profiling a minor.
- **Remove the feature.** It is the part of the white paper's claim ("learning rate only as fast as the evidence allows") that needs a place to live. Off by default keeps it available for a pilot.
- **Switch off the starting-point adjustments too.** Rejected: that is the part the evidence supports most, and it uses the student's own answers for their own teaching.

## Consequences

- The demo no longer shows a learning-rate offset. `demo.sh` and the demo script can set `EDUX_PERSONALISATION=1` only if a pilot wants it.
- Existing students need a rebuild to re-score (events keep their `settings_hash`).
- The startup identifiability check passes at the new top bound (0.10 × 1.3 in odds).
- No migration; instruction word count unchanged (897 of 900).

## Verification

`tests/test_personal_learning_rate.py` (7 tests); `pytest` and `scripts/check_mcp.py` pass with `EDUX_PERSONALISATION=1` and with it unset; rebuild identical.

## What would change our mind

A pilot with real students, evaluated on held-out answers, showing the offset predicts better than the population rate, with fairness checks across subgroups. Then switch it on at the school's request, with a fitted k.
