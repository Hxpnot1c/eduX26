# Simulating `review_when_below` (audit item C14)

**These are synthetic students on the example pack.** They test how the scheduling rules behave when the assumptions below hold. They are not evidence about real students and must never be presented as learning gains. Run `python scripts/simulate_review_threshold.py` to reproduce them.

## The question
`scheduling.review_when_below` (0.50) makes a part due for review when its predicted recall is expected to fall below that value. The research review suggested 0.70 to 0.80. Vishnu's decision of 18 November: do not change it before the results are in; run it at 0.50 and 0.75, everything else equal; he decides from the comparison.

## Where "0.70 to 0.80" comes from, exactly
It is **not** a finding about 0.50 against 0.75. The only source is Eglington & Pavlik (2020), "Practice schedules and individual differences in learning", *npj Science of Learning* 5, 15 ([PMC7567101](https://pmc.ncbi.nlm.nih.gov/articles/PMC7567101)), as recorded in `personalisation-findings.csv` rows 2-12 and 7b-03 (read from the overnight research; the paper itself was not re-read for this pull request):

- 291 adult online workers learned Japanese-English word pairs; practice was scheduled when each item's model-predicted recall fell to a threshold (an "optimal efficiency" schedule).
- Thresholds of **0.86 and 0.94** gave better final retention than **0.40**, than **0.98**, and than conventional spaced practice (d = 0.64 for the best against conventional; p < .05).
- They **did not differ significantly from 0.70** (ps > .17). **0.50 was not tested.** There was nothing between 0.70 and 0.86 either.
- The row's own caveat: "vocabulary recall probability, not p_known". Their threshold is on a fitted recall model for word pairs; ours is on `p_now`, a knowledge-tracing probability decayed by an assumed half-life. The scales are not the same thing.
- `personalisation.md` §7 then gives a range of 0.70 to 0.94 and **0.80 as "our choice"**, marked as partly supported. So 0.80 is an interpolation; the source supports "high thresholds beat very low and very high ones, for adults learning word pairs".

## The simulation
- **Students:** 60 per variant, paired by seed. Each studies every one of the 9 parts of `example-mini` in the first 4 weeks (an explain-back after teaching, right with probability 0.7), then comes to a session every other day with probability 0.8 and does up to 3 of the reviews the real code says are due (`learner.due_reviews`), for 90 days.
- **Hidden truth (our choice, not a finding):** one memory trace per part, recall = exp(−days since last retrieval / S); S starts at 4 days; a right review multiplies S by 2 (if at least half a day after the last), a wrong one by 0.5 (not below 1 day). An answer is right with probability recall × (1 − 0.10) + (1 − recall) × 0.25. The dice depend only on (seed, part, day), so every variant meets the same dice.
- **What is real:** the learner model (BKT with forgetting), the review queue, the share gap, `review_when_below` and `min_gap_days`, all from `settings.toml`; only `review_when_below` changes.
- **Measured on exam day:** reviews a week; mean true recall (retention); parts the model calls secure whose true recall is below 0.5 (false secure); parts it calls secure whose true recall is at least 0.75 (truly secure); due reviews not reached by the 3-a-session cap.

## Results (mean ± standard error, 60 synthetic students per row)
| `review_when_below` | reviews a week | true retention on exam day | false secure | truly secure | due reviews over the cap |
|---|---|---|---|---|---|
| 0.40 | 4.89 ± 0.06 | 0.216 ± 0.012 | 0.00 | 0.78 ± 0.11 | 46.1 ± 0.9 |
| **0.50 (now)** | 4.83 ± 0.06 | 0.202 ± 0.010 | 0.00 | 0.73 ± 0.09 | 44.9 ± 1.0 |
| 0.60 | 4.81 ± 0.06 | 0.188 ± 0.010 | 0.00 | 0.57 ± 0.09 | 43.9 ± 1.0 |
| **0.75** | 4.81 ± 0.06 | 0.182 ± 0.009 | 0.00 | 0.45 ± 0.08 | 43.5 ± 1.0 |
| 0.90 | 4.81 ± 0.06 | 0.180 ± 0.010 | 0.00 | 0.45 ± 0.08 | 42.3 ± 1.0 |

## What it shows, and what it does not
- **Raising the threshold to 0.75 did not help here.** Retention was lower (0.182 against 0.202) and fewer parts were both called secure and truly secure (0.45 against 0.73), at the same workload (about 4.8 reviews a week). Nothing was falsely secure at any threshold.
- **Why, as far as the code shows:** the recall-crossing review applies only to a part whose `p_known` is above the threshold (a part at or below it keeps the share gap). A higher threshold therefore switches off the earlier review for more parts, and the share gap is long when the exam is far off. The workload is set mostly by the 3-a-session cap (a large backlog stays over the cap at every threshold), not by the threshold.
- **Retention is low in absolute terms for every variant** (0.18 to 0.22): the model forgets in a 2-day half-life and nine parts compete for three review slots a session. That is a property of the settings and of this truth model, and a reason to look at the cap and the half-life next, not a prediction about students.
- **The truth model is ours.** A different memory model, a different cap or real attendance could reverse the ordering. The comparison says only that the case for 0.75 from this research is not supported by this simulation; the Eglington & Pavlik result is about a different quantity.
- **Not simulated:** the extend, bridge and priority steps, fatigue, the confidence question, real misconceptions, or A-level content.

## Recommendation (Vishnu decides)
Keep `review_when_below = 0.50`, label it a judgement call (as `settings.md` now does), and do not claim 0.70 to 0.80 as research for this setting. If the review backlog matters for the demo, the cap (`max_reviews_per_reply`) and the half-life are the levers that moved the numbers in this simulation, not the threshold.

## After decision 0025 (fading to the normal start, "needs review", the fading review)
The same simulation, rerun on 19 November once learnt parts fade towards their normal start instead of 0 and are reviewed before they fade below new (`scripts/simulate_review_threshold.py --thresholds 0.5 0.75`; synthetic students, not learning gains):

| `review_when_below` | reviews a week | true retention on exam day | false secure | truly secure | due reviews over the cap |
|---|---|---|---|---|---|
| **0.50 (now)** | 4.99 ± 0.06 | 0.221 ± 0.014 | 0.00 | 1.07 ± 0.11 | 50.1 ± 0.9 |
| **0.75** | 4.95 ± 0.06 | 0.211 ± 0.012 | 0.00 | 1.13 ± 0.10 | 48.0 ± 0.8 |

Both thresholds now keep more parts truly secure (about 1.1 against 0.73 and 0.45), at slightly more reviews a week and a slightly larger backlog over the cap. The gap between 0.50 and 0.75 has closed to within noise: with forgetting stopping at the normal start, fewer parts drop far enough for the threshold to matter. This does not change the recommendation to keep 0.50; the cap and the half-life are still the levers.
