# 0020. Keep `review_when_below` at 0.50; label it a judgement call

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (he decides from the comparison)
- **Pull request:** #63
- **Audit item:** C14 in [0002](0002-research-alignment-register.md)

## Context

The audit suggested raising `review_when_below` from 0.50 to 0.70 to 0.80, citing the research. Vishnu's decision (18 November): change nothing before the results are in; give the exact source and passage; simulate 0.50 and 0.75 with everything else equal and report reviews a week, true retention on exam day, false "secure" and truly secure parts, captioned as simulation.

## Decision

No change to the setting. Relabel it **a judgement call, starting value** in `settings.toml`, `settings.md` and `research.md`, and stop citing "0.70 to 0.80" as a finding. Add the simulation (`scripts/simulate_review_threshold.py`) and its write-up (`docs/research/review-threshold-simulation.md`) so the comparison can be rerun when settings change.

## Research basis

The only source, Eglington & Pavlik (2020), *npj Science of Learning* 5, 15, tested thresholds of 0.40, 0.70, 0.86, 0.94 and 0.98 on recall probabilities for adults learning word pairs: 0.86 and 0.94 beat 0.40, 0.98 and conventional spacing and did not differ from 0.70. 0.50 was not tested, there was nothing between 0.70 and 0.86, and the quantity is a fitted recall model, not our decayed knowledge-tracing probability. Our own simulation (synthetic students on the example pack, never a learning gain): raising the threshold to 0.75 lowered true retention on exam day from 0.202 to 0.182 and truly secure parts from 0.73 to 0.45 at the same workload (about 4.8 reviews a week); nothing was falsely secure at any value. A higher threshold switches off the earlier recall-crossing review for parts at or below it, and the workload is set mostly by the 3-a-session cap.

## Alternatives considered

- **Raise it to 0.80** on the strength of the study. The study neither tested 0.50 nor measures our quantity, and our simulation did not reward it.
- **Lower it to 0.40.** Slightly better in the simulation, but within noise of 0.50 and it would let weaker parts wait longer; not recommended without real data.

## Consequences

No change for students or the demo. The write-up points at the review cap and the half-life as the levers that moved the numbers.

## Verification

`tests/test_simulation_script.py` runs the script end to end on 2 students; the full table is reproducible with `python scripts/simulate_review_threshold.py --students 60 --thresholds 0.4 0.5 0.6 0.75 0.9`.

## What would change our mind

Real students' reviews and exam results, or a simulation with a truth model backed by data on A-level retention; or a decision to change the cap or the half-life, which would change the comparison.
