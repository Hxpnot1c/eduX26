# Branch vs proposal (final check)

N = 1000 synthetic students per group per cell. FastBackend (equal to the real 05e learner code: see validate.json). Every truth-model number is our choice.

- **branch**: prior=0.3, learn_rate=0.1, correct_share=0.67, verify_share=None, ask_min_features=2, half_life=2.0, q_slip=0.15, q_guess=0.2, t_slip=0.1, t_guess=0.15, u_slip=0.05, u_guess=0.1, h_guess=0.25, ignored=zero
- **wave1_quick_fixes**: prior=0.3, learn_rate=0.1, correct_share=0.67, verify_share=None, ask_min_features=3, half_life=2.0, q_slip=0.15, q_guess=0.2, t_slip=0.1, t_guess=0.15, u_slip=0.05, u_guess=0.2, h_guess=0.25, ignored=missing
- **settable_now**: prior=0.3, learn_rate=0.1, correct_share=0.67, verify_share=None, ask_min_features=3, half_life=2.0, q_slip=0.15, q_guess=0.3, t_slip=0.1, t_guess=0.35, u_slip=0.05, u_guess=0.2, h_guess=0.25, ignored=zero
- **settable_now_keep_task**: prior=0.3, learn_rate=0.1, correct_share=0.67, verify_share=None, ask_min_features=3, half_life=2.0, q_slip=0.15, q_guess=0.3, t_slip=0.1, t_guess=0.15, u_slip=0.05, u_guess=0.2, h_guess=0.25, ignored=zero
- **proposal**: prior=0.3, learn_rate=0.05, correct_share=0.67, verify_share=0.67, ask_min_features=3, half_life=14.0, q_slip=0.15, q_guess=0.3, t_slip=0.1, t_guess=0.35, u_slip=0.05, u_guess=0.2, h_guess=0.25, ignored=missing

## ask

| metric | branch 0 mnar | branch sym10 mnar | branch sym20 mnar | branch len20 mnar | wave1_quick_fixes 0 mnar | wave1_quick_fixes sym10 mnar | wave1_quick_fixes sym20 mnar | wave1_quick_fixes len20 mnar | settable_now 0 mnar | settable_now sym10 mnar | settable_now sym20 mnar | settable_now len20 mnar | settable_now_keep_task 0 mnar | settable_now_keep_task sym10 mnar | settable_now_keep_task sym20 mnar | settable_now_keep_task len20 mnar | proposal 0 mnar | proposal sym10 mnar | proposal sym20 mnar | proposal len20 mnar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none secure, worst weekly read | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 |
| none ever secure (incl. in-chat) | 0.01 | 0.03 | 0.06 | 0.13 | 0.02 | 0.04 | 0.09 | 0.18 | 0.00 | 0.01 | 0.03 | 0.05 | 0.00 | 0.01 | 0.03 | 0.05 | 0.00 | 0.01 | 0.02 | 0.07 |
| gamer secure w3-10 | 0.08 | 0.07 | 0.05 | 0.21 | 0.16 | 0.12 | 0.09 | 0.33 | 0.08 | 0.06 | 0.04 | 0.21 | 0.08 | 0.06 | 0.04 | 0.21 | 0.10 | 0.07 | 0.05 | 0.28 |
| partial secure w3-10 | 0.11 | 0.09 | 0.07 | 0.29 | 0.23 | 0.16 | 0.12 | 0.45 | 0.12 | 0.08 | 0.06 | 0.29 | 0.12 | 0.08 | 0.06 | 0.29 | 0.16 | 0.11 | 0.07 | 0.38 |
| strong secure w3-10 | 0.97 | 0.87 | 0.63 | 0.95 | 0.99 | 0.94 | 0.76 | 0.98 | 0.98 | 0.89 | 0.64 | 0.96 | 0.98 | 0.89 | 0.64 | 0.96 | 0.99 | 0.94 | 0.73 | 0.98 |
| strong median days to secure | 4.86 | 6.68 | 9.78 | 5.73 | 4.84 | 5.81 | 7.75 | 5.68 | 6.77 | 8.76 | 14.69 | 6.84 | 6.77 | 8.76 | 14.69 | 6.84 | 4.86 | 5.84 | 8.74 | 5.71 |
| strong median moments to secure | 2 | 2 | 4 | 2 | 2 | 2 | 4 | 2 | 3 | 4 | 7 | 3 | 3 | 4 | 7 | 3 | 2 | 2 | 4 | 2 |
| strong secure by day 28 | 0.99 | 0.94 | 0.81 | 0.99 | 1.00 | 0.99 | 0.89 | 1.00 | 0.99 | 0.94 | 0.78 | 0.98 | 0.99 | 0.94 | 0.78 | 0.98 | 1.00 | 0.98 | 0.85 | 1.00 |
| improver secure w6 | 0.59 | 0.39 | 0.23 | 0.55 | 0.71 | 0.49 | 0.31 | 0.67 | 0.51 | 0.32 | 0.17 | 0.51 | 0.51 | 0.32 | 0.17 | 0.51 | 0.27 | 0.17 | 0.09 | 0.33 |
| AUC none-strong w8 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 |
| AUC partial-strong w8 | 1.00 | 0.98 | 0.91 | 0.98 | 1.00 | 0.99 | 0.92 | 0.98 | 1.00 | 0.99 | 0.92 | 0.98 | 1.00 | 0.99 | 0.92 | 0.98 | 1.00 | 0.99 | 0.94 | 0.99 |
| AUC gamer-strong w8 | 1.00 | 0.98 | 0.92 | 0.99 | 1.00 | 0.99 | 0.94 | 0.99 | 1.00 | 0.99 | 0.93 | 0.99 | 1.00 | 0.99 | 0.93 | 0.99 | 1.00 | 0.99 | 0.95 | 0.99 |

mcar ignoring, ask: none secure worst weekly / strong secure w3-10

| variant | 0 | sym10 | sym20 | len20 |
|---|---|---|---|---|
| branch | 0.001 / 0.97 | 0.000 / 0.87 | 0.003 / 0.62 | 0.009 / 0.95 |
| wave1_quick_fixes | 0.001 / 0.99 | 0.001 / 0.93 | 0.004 / 0.73 | 0.012 / 0.97 |
| settable_now | 0.000 / 0.97 | 0.000 / 0.87 | 0.001 / 0.60 | 0.004 / 0.95 |
| settable_now_keep_task | 0.000 / 0.97 | 0.000 / 0.87 | 0.001 / 0.60 | 0.004 / 0.95 |
| proposal | 0.000 / 0.99 | 0.000 / 0.93 | 0.003 / 0.71 | 0.012 / 0.98 |

## verify

| metric | branch 0 mnar | branch sym10 mnar | branch sym20 mnar | branch len20 mnar | wave1_quick_fixes 0 mnar | wave1_quick_fixes sym10 mnar | wave1_quick_fixes sym20 mnar | wave1_quick_fixes len20 mnar | settable_now 0 mnar | settable_now sym10 mnar | settable_now sym20 mnar | settable_now len20 mnar | settable_now_keep_task 0 mnar | settable_now_keep_task sym10 mnar | settable_now_keep_task sym20 mnar | settable_now_keep_task len20 mnar | proposal 0 mnar | proposal sym10 mnar | proposal sym20 mnar | proposal len20 mnar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none secure, worst weekly read | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 |
| none ever secure (incl. in-chat) | 0.00 | 0.02 | 0.05 | 0.07 | 0.00 | 0.01 | 0.01 | 0.05 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.01 | 0.04 | 0.00 | 0.00 | 0.01 | 0.03 |
| gamer secure w3-10 | 0.12 | 0.08 | 0.04 | 0.18 | 0.11 | 0.06 | 0.03 | 0.17 | 0.04 | 0.02 | 0.01 | 0.08 | 0.08 | 0.05 | 0.03 | 0.13 | 0.16 | 0.09 | 0.06 | 0.22 |
| partial secure w3-10 | 0.06 | 0.05 | 0.04 | 0.12 | 0.06 | 0.04 | 0.03 | 0.12 | 0.02 | 0.01 | 0.01 | 0.04 | 0.04 | 0.03 | 0.02 | 0.09 | 0.09 | 0.06 | 0.04 | 0.16 |
| strong secure w3-10 | 0.86 | 0.68 | 0.43 | 0.78 | 0.86 | 0.66 | 0.38 | 0.78 | 0.75 | 0.50 | 0.24 | 0.65 | 0.83 | 0.61 | 0.35 | 0.74 | 0.92 | 0.70 | 0.41 | 0.82 |
| strong median days to secure | 7.69 | 9.76 | 14.68 | 7.82 | 7.87 | 10.83 | 17.86 | 8.82 | 16.75 | 25.75 | 45.70 | 18.72 | 8.72 | 11.83 | 18.77 | 9.69 | 10.80 | 14.82 | 25.85 | 11.77 |
| strong median moments to secure | 2 | 3 | 4 | 2 | 2 | 3 | 4 | 2 | 4 | 6 | 11 | 5 | 2 | 3 | 5 | 2 | 3 | 3 | 6 | 3 |
| strong secure by day 28 | 0.95 | 0.87 | 0.71 | 0.92 | 0.95 | 0.83 | 0.62 | 0.91 | 0.75 | 0.54 | 0.34 | 0.68 | 0.93 | 0.80 | 0.60 | 0.89 | 0.93 | 0.77 | 0.53 | 0.87 |
| improver secure w6 | 0.31 | 0.20 | 0.12 | 0.27 | 0.35 | 0.20 | 0.12 | 0.27 | 0.16 | 0.08 | 0.04 | 0.12 | 0.32 | 0.19 | 0.11 | 0.25 | 0.34 | 0.21 | 0.13 | 0.28 |
| AUC none-strong w8 | 1.00 | 0.98 | 0.92 | 1.00 | 1.00 | 0.97 | 0.89 | 1.00 | 0.99 | 0.95 | 0.84 | 0.99 | 0.99 | 0.96 | 0.87 | 0.99 | 1.00 | 0.98 | 0.91 | 1.00 |
| AUC partial-strong w8 | 0.98 | 0.95 | 0.88 | 0.95 | 0.99 | 0.95 | 0.88 | 0.95 | 0.99 | 0.95 | 0.87 | 0.95 | 0.98 | 0.95 | 0.87 | 0.95 | 0.99 | 0.95 | 0.87 | 0.94 |
| AUC gamer-strong w8 | 0.96 | 0.93 | 0.85 | 0.92 | 0.97 | 0.94 | 0.85 | 0.92 | 0.98 | 0.94 | 0.85 | 0.93 | 0.97 | 0.93 | 0.85 | 0.92 | 0.97 | 0.93 | 0.84 | 0.91 |

mcar ignoring, verify: none secure worst weekly / strong secure w3-10

| variant | 0 | sym10 | sym20 | len20 |
|---|---|---|---|---|
| branch | 0.000 / 0.74 | 0.001 / 0.55 | 0.004 / 0.32 | 0.005 / 0.65 |
| wave1_quick_fixes | 0.001 / 0.81 | 0.000 / 0.59 | 0.002 / 0.33 | 0.003 / 0.72 |
| settable_now | 0.000 / 0.62 | 0.000 / 0.38 | 0.001 / 0.16 | 0.001 / 0.51 |
| settable_now_keep_task | 0.001 / 0.71 | 0.000 / 0.49 | 0.002 / 0.26 | 0.003 / 0.61 |
| proposal | 0.002 / 0.88 | 0.001 / 0.66 | 0.004 / 0.37 | 0.009 / 0.78 |

## how

| metric | branch 0 mnar | branch sym10 mnar | branch sym20 mnar | branch len20 mnar | wave1_quick_fixes 0 mnar | wave1_quick_fixes sym10 mnar | wave1_quick_fixes sym20 mnar | wave1_quick_fixes len20 mnar | settable_now 0 mnar | settable_now sym10 mnar | settable_now sym20 mnar | settable_now len20 mnar | settable_now_keep_task 0 mnar | settable_now_keep_task sym10 mnar | settable_now_keep_task sym20 mnar | settable_now_keep_task len20 mnar | proposal 0 mnar | proposal sym10 mnar | proposal sym20 mnar | proposal len20 mnar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none secure, worst weekly read | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| none ever secure (incl. in-chat) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gamer secure w3-10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| partial secure w3-10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| strong secure w3-10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| strong median days to secure | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never |
| strong median moments to secure | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never | never |
| strong secure by day 28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| improver secure w6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| AUC none-strong w8 | 0.40 | 0.40 | 0.40 | 0.40 | 0.28 | 0.28 | 0.28 | 0.28 | 0.40 | 0.40 | 0.40 | 0.40 | 0.40 | 0.40 | 0.40 | 0.40 | 0.88 | 0.88 | 0.88 | 0.88 |
| AUC partial-strong w8 | 0.47 | 0.47 | 0.47 | 0.47 | 0.43 | 0.43 | 0.43 | 0.43 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.77 | 0.77 | 0.77 | 0.77 |
| AUC gamer-strong w8 | 0.45 | 0.45 | 0.45 | 0.45 | 0.41 | 0.41 | 0.41 | 0.41 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.89 | 0.89 | 0.89 | 0.89 |

mcar ignoring, how: none secure worst weekly / strong secure w3-10

| variant | 0 | sym10 | sym20 | len20 |
|---|---|---|---|---|
| branch | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 |
| wave1_quick_fixes | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 |
| settable_now | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 |
| settable_now_keep_task | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 |
| proposal | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 | 0.000 / 0.00 |
