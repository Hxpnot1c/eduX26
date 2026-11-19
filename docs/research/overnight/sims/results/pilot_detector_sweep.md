> PILOT run (3 seeds, seeds 1-3). The main-run re-sweep was stopped at wrap-up.

# Detector sweep (open-loop replay; current settings otherwise; near scenario; synthetic students, example-mini pack)

Each recorded event log is rebuilt with the detector setting below; truth is the simulated state.
Fatigue: a session (>= 30 min long) of the tired student is a positive; any other student's session is a negative. Precision is for the simulated mix (1 tired type in 7).

| fatigue_threshold | fatigue_window | fatigue_min_parts | recall (tired sessions flagged) | onset minute (mean ± SD) | flagged before minute 30 | false-alarm rate (other students' sessions) | precision | false alarms by type |
|---|---|---|---|---|---|---|---|---|
| -0.25 | 4 | 2 | 12% (13/105) | 35 ± 6 | 4 | 11.3% (71/630) | 15% | fast 7%, guesser 2%, offloader 11%, slow 9%, stuck 18%, typical 21% |
| -0.15 | 4 | 2 | 19% (20/105) | 34 ± 7 | 8 | 24.6% (155/630) | 11% | fast 13%, guesser 7%, offloader 28%, slow 24%, stuck 36%, typical 40% |
| -0.35 | 4 | 2 | 10% (10/105) | 36 ± 6 | 2 | 5.9% (37/630) | 21% | fast 4%, guesser 0%, offloader 8%, slow 4%, stuck 12%, typical 8% |
| -0.45 | 4 | 2 | 8% (8/105) | 37 ± 6 | 2 | 2.7% (17/630) | 32% | fast 2%, guesser 0%, offloader 4%, slow 1%, stuck 8%, typical 2% |
| -0.15 | 6 | 2 | 28% (29/105) | 31 ± 6 | 17 | 30.8% (194/630) | 13% | fast 28%, guesser 6%, offloader 37%, slow 28%, stuck 39%, typical 48% |
| -0.25 | 6 | 2 | 15% (16/105) | 33 ± 7 | 6 | 9.8% (62/630) | 21% | fast 4%, guesser 1%, offloader 11%, slow 8%, stuck 18%, typical 17% |
| -0.35 | 6 | 2 | 7% (7/105) | 37 ± 8 | 2 | 4.0% (25/630) | 22% | fast 1%, guesser 1%, offloader 5%, slow 4%, stuck 10%, typical 4% |
| -0.45 | 6 | 2 | 2% (2/105) | 33 ± 6 | 1 | 0.5% (3/630) | 40% | fast 0%, guesser 0%, offloader 0%, slow 1%, stuck 1%, typical 1% |
| -0.15 | 8 | 2 | 28% (29/105) | 32 ± 6 | 14 | 29.5% (186/630) | 13% | fast 30%, guesser 10%, offloader 26%, slow 25%, stuck 31%, typical 55% |
| -0.25 | 8 | 2 | 11% (12/105) | 34 ± 8 | 6 | 8.9% (56/630) | 18% | fast 6%, guesser 3%, offloader 9%, slow 10%, stuck 12%, typical 14% |
| -0.35 | 8 | 2 | 3% (3/105) | 37 ± 6 | 0 | 2.1% (13/630) | 19% | fast 2%, guesser 0%, offloader 0%, slow 3%, stuck 4%, typical 4% |
| -0.45 | 8 | 2 | 0% (0/105) | nan ± 0 | 0 | 0.3% (2/630) | 0% | fast 0%, guesser 0%, offloader 0%, slow 2%, stuck 0%, typical 0% |
| -0.15 | 4 | 1 | 64% (67/105) | 32 ± 5 | 22 | 58.9% (371/630) | 15% | fast 68%, guesser 33%, offloader 47%, slow 71%, stuck 56%, typical 78% |
| -0.25 | 4 | 1 | 38% (40/105) | 34 ± 4 | 6 | 28.6% (180/630) | 18% | fast 30%, guesser 17%, offloader 20%, slow 31%, stuck 25%, typical 48% |
| -0.35 | 4 | 1 | 23% (24/105) | 33 ± 4 | 3 | 15.6% (98/630) | 20% | fast 14%, guesser 9%, offloader 11%, slow 15%, stuck 19%, typical 25% |
| -0.45 | 4 | 1 | 13% (14/105) | 34 ± 4 | 3 | 8.3% (52/630) | 21% | fast 8%, guesser 3%, offloader 7%, slow 9%, stuck 12%, typical 11% |
| -0.15 | 6 | 1 | 48% (50/105) | 31 ± 5 | 24 | 52.2% (329/630) | 13% | fast 57%, guesser 27%, offloader 45%, slow 61%, stuck 58%, typical 66% |
| -0.25 | 6 | 1 | 20% (21/105) | 33 ± 5 | 7 | 18.7% (118/630) | 15% | fast 17%, guesser 10%, offloader 14%, slow 20%, stuck 21%, typical 30% |
| -0.35 | 6 | 1 | 9% (9/105) | 35 ± 6 | 2 | 7.1% (45/630) | 17% | fast 5%, guesser 4%, offloader 6%, slow 8%, stuck 10%, typical 11% |
| -0.45 | 6 | 1 | 5% (5/105) | 34 ± 3 | 1 | 1.7% (11/630) | 31% | fast 1%, guesser 2%, offloader 0%, slow 3%, stuck 1%, typical 4% |
| -0.15 | 8 | 1 | 34% (36/105) | 32 ± 6 | 16 | 39.4% (248/630) | 13% | fast 40%, guesser 30%, offloader 27%, slow 39%, stuck 33%, typical 68% |
| -0.25 | 8 | 1 | 12% (13/105) | 33 ± 7 | 6 | 11.3% (71/630) | 15% | fast 10%, guesser 9%, offloader 9%, slow 10%, stuck 12%, typical 18% |
| -0.35 | 8 | 1 | 5% (5/105) | 35 ± 4 | 0 | 3.2% (20/630) | 20% | fast 4%, guesser 2%, offloader 0%, slow 3%, stuck 4%, typical 7% |
| -0.45 | 8 | 1 | 2% (2/105) | 35 ± 3 | 0 | 0.8% (5/630) | 29% | fast 0%, guesser 2%, offloader 0%, slow 3%, stuck 0%, typical 0% |

## Stuck rule (settings.toml fatigue values)

Rule A = the built rule (same point missed on its check and again on the re-check after its reteach; open answers: 3 attempts, mean < 0.5, no improvement). Rule B = sim-only alternative: the same point missed on three checks in a session.

| rule | recall on the true stuck part | sessions with a false stuck flag, by type |
|---|---|---|
| A | 99% (102/103) | fast 5%, guesser 100%, offloader 12%, slow (ambiguous) 30%, stuck 10%, tired 30%, typical 8% |
| B | 7% (7/103) | fast 0%, guesser 97%, offloader 3%, slow (ambiguous) 3%, stuck 2%, tired 3%, typical 0% |
