# Settings grid: ranked

3480 settings combinations, 100 synthetic students per group per cell, cells = label noise {10%, 20% symmetric} x ignoring {mcar, mnar}. Constraint and objective: see grid.py. Hold = mean share of strong students shown secure at weekly reads, weeks 3-10, at 10% noise, mnar. A = Ask, V = Verify. FS = no-skill students shown secure (point: worst weekly read; ever: ever, incl. straight after a moment). All synthetic; every truth-model number is our choice.

- passing the constraint (FS point <= 5%): 1256
- passing the strict constraint (FS ever <= 5% too): 1062

## Branch values but ask_min_features 3 (the grid ties min_features to the threshold; not the real branch: see final.md)

| # | settings | strong hold (A/V) | days to secure (A/V) | moments (A/V) | worst FS point / ever | partial secure | gamer V | AUC p-s | improver w6 | hold @20% |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior 0.3, lr 0.1, hl 2, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.77 (0.93/0.61) | 5.7/9.7 | 2/3 | 0.02 / 0.08 | 0.09 | 0.05 | 0.97 | 0.39 | 0.58 |

## Top 15, balanced rule (788 pass): strict + gamer Verify <= 10%, ranked by strong hold - partial secure

| # | settings | strong hold (A/V) | days to secure (A/V) | moments (A/V) | worst FS point / ever | partial secure | gamer V | AUC p-s | improver w6 | hold @20% |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior 0.3, lr 0.05, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.84 (0.94/0.74) | 5.7/10.7 | 2/3 | 0.01 / 0.03 | 0.09 | 0.10 | 0.98 | 0.24 | 0.63 |
| 2 | prior 0.2, lr 0.05, hl 14, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.1 | 0.83 (0.92/0.74) | 9.7/10.8 | 5/3 | 0.00 / 0.01 | 0.09 | 0.09 | 0.97 | 0.23 | 0.61 |
| 3 | prior 0.2, lr 0.05, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.83 (0.94/0.72) | 9.7/13.9 | 4/4 | 0.00 / 0.02 | 0.08 | 0.08 | 0.98 | 0.23 | 0.62 |
| 4 | prior 0.3, lr 0.02, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.81 (0.91/0.71) | 5.9/13.9 | 2/4 | 0.01 / 0.03 | 0.06 | 0.07 | 0.98 | 0.14 | 0.56 |
| 5 | prior 0.3, lr 0.02, hl 14, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.1 | 0.80 (0.90/0.71) | 6.7/9.7 | 2/2 | 0.00 / 0.03 | 0.06 | 0.08 | 0.98 | 0.14 | 0.54 |
| 6 | prior 0.3, lr 0.05, hl 14, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.84 (0.94/0.74) | 5.7/11.8 | 2/3 | 0.00 / 0.03 | 0.10 | 0.09 | 0.98 | 0.24 | 0.62 |
| 7 | prior 0.3, lr 0.02, hl 14, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.81 (0.91/0.71) | 6.7/13.7 | 2/3 | 0.00 / 0.03 | 0.07 | 0.07 | 0.98 | 0.14 | 0.55 |
| 8 | prior 0.2, lr 0.05, hl 14, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.83 (0.94/0.72) | 9.7/13.7 | 5/3 | 0.00 / 0.01 | 0.08 | 0.09 | 0.98 | 0.23 | 0.61 |
| 9 | prior 0.3, lr 0.02, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.2 | 0.83 (0.91/0.74) | 5.9/10.7 | 2/2 | 0.01 / 0.01 | 0.08 | 0.10 | 0.98 | 0.15 | 0.57 |
| 10 | prior 0.3, lr 0.02, hl 30, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.84 (0.93/0.76) | 5.9/13.7 | 2/3 | 0.01 / 0.03 | 0.10 | 0.10 | 0.98 | 0.17 | 0.60 |
| 11 | prior 0.2, lr 0.05, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.3 | 0.84 (0.94/0.74) | 9.7/10.7 | 4/2 | 0.00 / 0.02 | 0.10 | 0.10 | 0.97 | 0.24 | 0.62 |
| 12 | prior 0.3, lr 0.05, hl 14, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.1 | 0.81 (0.93/0.69) | 5.7/12.8 | 2/3 | 0.00 / 0.03 | 0.07 | 0.06 | 0.98 | 0.21 | 0.58 |
| 13 | prior 0.3, lr 0.02, hl 7, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.1 | 0.80 (0.89/0.70) | 6.8/8.7 | 2/2 | 0.00 / 0.03 | 0.06 | 0.08 | 0.98 | 0.14 | 0.54 |
| 14 | prior 0.3, lr 0.05, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.35, u_guess 0.2 | 0.83 (0.94/0.71) | 5.7/12.7 | 2/3 | 0.00 / 0.02 | 0.09 | 0.07 | 0.98 | 0.21 | 0.61 |
| 15 | prior 0.2, lr 0.02, hl 30, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.2 | 0.81 (0.90/0.72) | 9.8/10.8 | 5/2 | 0.00 / 0.00 | 0.07 | 0.09 | 0.97 | 0.12 | 0.57 |

## Top 15, strict constraint

| # | settings | strong hold (A/V) | days to secure (A/V) | moments (A/V) | worst FS point / ever | partial secure | gamer V | AUC p-s | improver w6 | hold @20% |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior 0.2, lr 0.05, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.94 (0.96/0.92) | 9.7/8.8 | 4/2 | 0.02 / 0.05 | 0.28 | 0.34 | 0.97 | 0.62 | 0.79 |
| 2 | prior 0.3, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.94 (0.95/0.92) | 5.7/9.7 | 2/2 | 0.02 / 0.05 | 0.23 | 0.31 | 0.97 | 0.61 | 0.77 |
| 3 | prior 0.3, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.94 (0.94/0.93) | 5.9/7.9 | 2/2 | 0.02 / 0.05 | 0.21 | 0.32 | 0.97 | 0.49 | 0.75 |
| 4 | prior 0.2, lr 0.05, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.94 (0.96/0.91) | 9.7/8.8 | 4/2 | 0.02 / 0.05 | 0.27 | 0.32 | 0.96 | 0.61 | 0.78 |
| 5 | prior 0.3, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.93 (0.95/0.91) | 5.7/9.7 | 2/2 | 0.02 / 0.05 | 0.23 | 0.30 | 0.97 | 0.60 | 0.76 |
| 6 | prior 0.3, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.93 (0.94/0.92) | 5.9/9.7 | 2/2 | 0.02 / 0.04 | 0.20 | 0.29 | 0.97 | 0.47 | 0.74 |
| 7 | prior 0.2, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.93 (0.95/0.91) | 9.7/9.7 | 4/2 | 0.02 / 0.04 | 0.23 | 0.30 | 0.97 | 0.59 | 0.76 |
| 8 | prior 0.2, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.93 (0.93/0.93) | 9.8/9.7 | 5/2 | 0.02 / 0.02 | 0.20 | 0.29 | 0.97 | 0.48 | 0.73 |
| 9 | prior 0.3, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.93 (0.94/0.91) | 5.9/9.7 | 2/2 | 0.02 / 0.04 | 0.20 | 0.26 | 0.97 | 0.47 | 0.73 |
| 10 | prior 0.2, lr 0.05, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.1 | 0.93 (0.96/0.89) | 9.7/9.7 | 4/2 | 0.02 / 0.05 | 0.24 | 0.28 | 0.97 | 0.60 | 0.76 |
| 11 | prior 0.2, lr 0.1, hl 30, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.92 (0.97/0.88) | 5.7/8.8 | 2/2 | 0.02 / 0.05 | 0.22 | 0.27 | 0.97 | 0.49 | 0.78 |
| 12 | prior 0.3, lr 0.02, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.92 (0.93/0.91) | 5.9/8.7 | 2/2 | 0.02 / 0.04 | 0.16 | 0.27 | 0.98 | 0.46 | 0.71 |
| 13 | prior 0.2, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.92 (0.93/0.92) | 9.8/9.7 | 5/2 | 0.02 / 0.02 | 0.19 | 0.27 | 0.97 | 0.47 | 0.72 |
| 14 | prior 0.2, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.92 (0.95/0.89) | 9.7/9.7 | 4/2 | 0.02 / 0.04 | 0.22 | 0.28 | 0.96 | 0.57 | 0.75 |
| 15 | prior 0.2, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.92 (0.93/0.92) | 9.8/9.7 | 5/2 | 0.02 / 0.02 | 0.19 | 0.24 | 0.97 | 0.47 | 0.71 |

## Top 10, point constraint only

| # | settings | strong hold (A/V) | days to secure (A/V) | moments (A/V) | worst FS point / ever | partial secure | gamer V | AUC p-s | improver w6 | hold @20% |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior 0.2, lr 0.05, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.96 (0.98/0.93) | 5.7/8.8 | 2/2 | 0.05 / 0.17 | 0.37 | 0.39 | 0.97 | 0.72 | 0.86 |
| 2 | prior 0.3, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.96 (0.97/0.94) | 5.7/7.9 | 2/2 | 0.02 / 0.06 | 0.30 | 0.33 | 0.97 | 0.63 | 0.82 |
| 3 | prior 0.3, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.96 (0.98/0.93) | 5.7/8.7 | 2/2 | 0.05 / 0.19 | 0.32 | 0.38 | 0.98 | 0.72 | 0.85 |
| 4 | prior 0.2, lr 0.1, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.96 (0.97/0.94) | 5.7/9.7 | 2/2 | 0.05 / 0.16 | 0.32 | 0.37 | 0.97 | 0.77 | 0.83 |
| 5 | prior 0.2, lr 0.1, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.3 | 0.95 (0.97/0.93) | 5.7/9.7 | 2/2 | 0.05 / 0.16 | 0.32 | 0.36 | 0.96 | 0.76 | 0.83 |
| 6 | prior 0.2, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.95 (0.98/0.92) | 5.7/9.7 | 2/2 | 0.04 / 0.16 | 0.31 | 0.35 | 0.98 | 0.70 | 0.84 |
| 7 | prior 0.3, lr 0.05, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.2 | 0.95 (0.96/0.94) | 5.7/8.8 | 2/2 | 0.03 / 0.06 | 0.28 | 0.35 | 0.96 | 0.66 | 0.79 |
| 8 | prior 0.2, lr 0.02, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.2, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.95 (0.97/0.93) | 5.7/9.7 | 2/2 | 0.02 / 0.06 | 0.29 | 0.30 | 0.97 | 0.62 | 0.82 |
| 9 | prior 0.2, lr 0.1, hl none, ignored missing, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.25, u_guess 0.1 | 0.95 (0.98/0.92) | 5.7/8.7 | 2/2 | 0.05 / 0.17 | 0.32 | 0.34 | 0.97 | 0.71 | 0.83 |
| 10 | prior 0.3, lr 0.05, hl none, ignored zero, ask_share 0.67 (min_feat 3), q 0.15/0.3, verify_share 0.67, t 0.1/0.15, u_guess 0.1 | 0.95 (0.95/0.94) | 5.7/8.7 | 2/2 | 0.05 / 0.11 | 0.24 | 0.37 | 0.98 | 0.64 | 0.79 |

## Marginals (strict-passing configs): best and median hold by each setting value

| setting | value | n passing | best hold | median hold | median worst FS ever |
|---|---|---|---|---|---|
| prior | 0.2 | 555/1740 | 0.94 | 0.69 | 0.01 |
| prior | 0.3 | 507/1740 | 0.94 | 0.69 | 0.02 |
| learn_rate | 0.02 | 412/1160 | 0.94 | 0.68 | 0.01 |
| learn_rate | 0.05 | 371/1160 | 0.94 | 0.69 | 0.02 |
| learn_rate | 0.1 | 279/1160 | 0.92 | 0.70 | 0.04 |
| half_life | 2 | 262/696 | 0.87 | 0.67 | 0.01 |
| half_life | 7 | 236/696 | 0.88 | 0.73 | 0.01 |
| half_life | 14 | 230/696 | 0.90 | 0.76 | 0.02 |
| half_life | 30 | 207/696 | 0.92 | 0.79 | 0.02 |
| half_life | 1e+06 | 127/696 | 0.94 | 0.77 | 0.04 |
| ignored | missing | 511/1740 | 0.94 | 0.71 | 0.02 |
| ignored | zero | 551/1740 | 0.94 | 0.68 | 0.02 |
| correct_share | 0.5 | 0/1740 | - | - | - |
| correct_share | 0.67 | 1062/1740 | 0.94 | 0.69 | 0.02 |
| q_guess | 0.2 | 26/120 | 0.92 | 0.85 | 0.04 |
| q_guess | 0.3 | 990/3240 | 0.94 | 0.64 | 0.02 |
| q_guess | 0.4 | 46/120 | 0.89 | 0.80 | 0.03 |
| verify_share | 0.5 | 26/1080 | 0.87 | 0.84 | 0.03 |
| verify_share | 0.67 | 550/1320 | 0.94 | 0.82 | 0.02 |
| verify_share | 1 | 486/1080 | 0.64 | 0.48 | 0.01 |
| t_guess | 0.15 | 388/1320 | 0.94 | 0.74 | 0.02 |
| t_guess | 0.25 | 330/1080 | 0.93 | 0.65 | 0.02 |
| t_guess | 0.35 | 344/1080 | 0.89 | 0.65 | 0.02 |
| u_guess | 0.1 | 390/1320 | 0.94 | 0.73 | 0.03 |
| u_guess | 0.2 | 334/1080 | 0.94 | 0.65 | 0.02 |
| u_guess | 0.3 | 338/1080 | 0.94 | 0.65 | 0.02 |

## Half-life sweep around the best strict config (other settings fixed)

| half-life | strong hold A/V | worst FS point / ever | partial secure | improver w6 | days to secure A/V |
|---|---|---|---|---|---|
| 2 | 0.86/0.49 | 0.00 / 0.03 | 0.03 | 0.12 | 9.9/21.7 |
| 7 | 0.91/0.63 | 0.00 / 0.03 | 0.05 | 0.17 | 5.8/13.7 |
| 14 | 0.93/0.69 | 0.00 / 0.03 | 0.07 | 0.21 | 5.7/12.8 |
| 30 | 0.94/0.74 | 0.01 / 0.03 | 0.09 | 0.24 | 5.7/10.7 |
| none | 0.96/0.82 | 0.02 / 0.05 | 0.16 | 0.52 | 5.7/9.7 |

## Ignored = zero vs missing around the best strict config

| ignored | strong hold A/V | worst FS point / ever | partial secure | AUC partial-strong |
|---|---|---|---|---|
| zero | 0.94/0.74 | 0.01 / 0.03 | 0.09 | 0.98 |
| missing | 0.95/0.78 | 0.01 / 0.03 | 0.12 | 0.98 |
