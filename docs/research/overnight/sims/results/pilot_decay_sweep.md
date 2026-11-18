> PILOT run (3 seeds, seeds 1-3). The main-run re-sweep was stopped at wrap-up.

# Scoring/decay rules replayed on the same answers (current closed-loop logs), scored on exam day

Synthetic students (all 7 types; guesser included), example-mini pack. FDR = model-secure parts the student truly doesn't know (mastery < 0.5) / model-secure parts. Coverage = truly secure parts (>= 0.75) the model calls secure. Spread = SD over students of each student's FDR. Rules marked shim are emulated in the sim, not built.

| rule | scenario | FDR of 'secure' | FDR SD over students | coverage | mean p_now - truth |
|---|---|---|---|---|---|
| current | far | 72% (96 secure) | 22 | 57% | +0.36 |
| current | near | 7% (125 secure) | 12 | 83% | +0.01 |
| proposal | far | 72% (96 secure) | 22 | 57% | +0.36 |
| proposal | near | 7% (121 secure) | 13 | 80% | -0.01 |
| proposal+mcq_guess | far | 72% (96 secure) | 22 | 57% | +0.36 |
| proposal+mcq_guess | near | 7% (121 secure) | 13 | 80% | -0.01 |
| proposal+immediate_x1.0 | far | 53% (15 secure) | 46 | 13% | -0.10 |
| proposal+immediate_x1.0 | near | 1% (69 secure) | 9 | 51% | -0.22 |
| proposal+immediate_x1.5 | far | 70% (27 secure) | 37 | 17% | +0.00 |
| proposal+immediate_x1.5 | near | 8% (106 secure) | 13 | 70% | -0.06 |
| proposal+on_success_1.5 | far | 62% (13 secure) | 49 | 13% | -0.07 |
| proposal+on_success_1.5 | near | 9% (87 secure) | 13 | 56% | -0.14 |
| proposal+scaled | far | 0% (0 secure) | 0 | 0% | -0.19 |
| proposal+scaled | near | 0% (1 secure) | 0 | 1% | -0.49 |
| proposal+scaled+mcq_guess | far | 0% (0 secure) | 0 | 0% | -0.19 |
| proposal+scaled+mcq_guess | near | 0% (1 secure) | 0 | 1% | -0.49 |
| proposal+immediate_x1.0+mcq_guess | far | 53% (15 secure) | 46 | 13% | -0.10 |
| proposal+immediate_x1.0+mcq_guess | near | 1% (69 secure) | 9 | 51% | -0.23 |
