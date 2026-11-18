# Misconception alarm simulation (w2-05t)

All parameters are our choice. Synthetic numbers, not evidence about real classes.

## 1. Exact per-cell flag probability (one misconception, one class-week)

Rows: rule (k = min students, x = min share of attempters, m_min = min attempters). Null columns are false-alarm rates; alt columns are detection rates.

### Attempt share a = 0.5

| rule | n | null p=0.1 | null p=0.15 | null p=0.25 | alt p=0.35 | alt p=0.5 | expected false flags/term @p=0.15 (10 cells x 12 wk) |
|---|---|---|---|---|---|---|---|
| k=3, x=25%, m_min=5 | 12 | 0.019 | 0.054 | 0.175 | 0.33 | 0.56 | 6.5 |
| k=3, x=25%, m_min=5 | 16 | 0.042 | 0.111 | 0.319 | 0.54 | 0.79 | 13.3 |
| k=3, x=25%, m_min=5 | 20 | 0.061 | 0.160 | 0.432 | 0.69 | 0.90 | 19.1 |
| k=3, x=25%, m_min=5 | 25 | 0.063 | 0.175 | 0.494 | 0.77 | 0.96 | 21.0 |
| k=4, x=30%, m_min=5 | 12 | 0.002 | 0.010 | 0.052 | 0.14 | 0.34 | 1.1 |
| k=4, x=30%, m_min=5 | 16 | 0.007 | 0.028 | 0.130 | 0.30 | 0.59 | 3.3 |
| k=4, x=30%, m_min=5 | 20 | 0.014 | 0.052 | 0.222 | 0.46 | 0.77 | 6.2 |
| k=4, x=30%, m_min=5 | 25 | 0.017 | 0.069 | 0.295 | 0.59 | 0.89 | 8.2 |
| k=5, x=30%, m_min=5 | 12 | 0.000 | 0.001 | 0.011 | 0.04 | 0.16 | 0.1 |
| k=5, x=30%, m_min=5 | 16 | 0.001 | 0.005 | 0.041 | 0.13 | 0.37 | 0.6 |
| k=5, x=30%, m_min=5 | 20 | 0.003 | 0.014 | 0.095 | 0.26 | 0.59 | 1.7 |
| k=5, x=30%, m_min=5 | 25 | 0.006 | 0.032 | 0.185 | 0.44 | 0.78 | 3.8 |
| k=5, x=40%, m_min=5 | 12 | 0.000 | 0.001 | 0.011 | 0.04 | 0.16 | 0.1 |
| k=5, x=40%, m_min=5 | 16 | 0.001 | 0.005 | 0.039 | 0.13 | 0.37 | 0.6 |
| k=5, x=40%, m_min=5 | 20 | 0.002 | 0.010 | 0.076 | 0.23 | 0.57 | 1.2 |
| k=5, x=40%, m_min=5 | 25 | 0.002 | 0.012 | 0.103 | 0.32 | 0.72 | 1.5 |
| k=6, x=40%, m_min=5 | 12 | 0.000 | 0.000 | 0.002 | 0.01 | 0.05 | 0.0 |
| k=6, x=40%, m_min=5 | 16 | 0.000 | 0.001 | 0.010 | 0.05 | 0.19 | 0.1 |
| k=6, x=40%, m_min=5 | 20 | 0.000 | 0.003 | 0.030 | 0.12 | 0.38 | 0.3 |
| k=6, x=40%, m_min=5 | 25 | 0.001 | 0.006 | 0.067 | 0.24 | 0.61 | 0.8 |

### Attempt share a = 0.8

| rule | n | null p=0.1 | null p=0.15 | null p=0.25 | alt p=0.35 | alt p=0.5 | expected false flags/term @p=0.15 (10 cells x 12 wk) |
|---|---|---|---|---|---|---|---|
| k=3, x=25%, m_min=5 | 12 | 0.065 | 0.167 | 0.442 | 0.70 | 0.92 | 20.0 |
| k=3, x=25%, m_min=5 | 16 | 0.064 | 0.179 | 0.504 | 0.78 | 0.97 | 21.4 |
| k=3, x=25%, m_min=5 | 20 | 0.046 | 0.154 | 0.508 | 0.81 | 0.98 | 18.5 |
| k=3, x=25%, m_min=5 | 25 | 0.029 | 0.127 | 0.508 | 0.84 | 0.99 | 15.2 |
| k=4, x=30%, m_min=5 | 12 | 0.012 | 0.046 | 0.205 | 0.45 | 0.77 | 5.6 |
| k=4, x=30%, m_min=5 | 16 | 0.021 | 0.078 | 0.324 | 0.63 | 0.92 | 9.4 |
| k=4, x=30%, m_min=5 | 20 | 0.012 | 0.058 | 0.307 | 0.65 | 0.94 | 7.0 |
| k=4, x=30%, m_min=5 | 25 | 0.007 | 0.046 | 0.311 | 0.69 | 0.97 | 5.5 |
| k=5, x=30%, m_min=5 | 12 | 0.002 | 0.009 | 0.073 | 0.23 | 0.56 | 1.1 |
| k=5, x=30%, m_min=5 | 16 | 0.007 | 0.035 | 0.202 | 0.48 | 0.83 | 4.2 |
| k=5, x=30%, m_min=5 | 20 | 0.010 | 0.052 | 0.290 | 0.63 | 0.93 | 6.2 |
| k=5, x=30%, m_min=5 | 25 | 0.007 | 0.046 | 0.311 | 0.69 | 0.97 | 5.5 |
| k=5, x=40%, m_min=5 | 12 | 0.002 | 0.009 | 0.073 | 0.23 | 0.56 | 1.1 |
| k=5, x=40%, m_min=5 | 16 | 0.002 | 0.014 | 0.113 | 0.34 | 0.75 | 1.6 |
| k=5, x=40%, m_min=5 | 20 | 0.001 | 0.009 | 0.100 | 0.35 | 0.80 | 1.1 |
| k=5, x=40%, m_min=5 | 25 | 0.000 | 0.004 | 0.075 | 0.33 | 0.82 | 0.5 |
| k=6, x=40%, m_min=5 | 12 | 0.000 | 0.001 | 0.019 | 0.09 | 0.33 | 0.2 |
| k=6, x=40%, m_min=5 | 16 | 0.001 | 0.008 | 0.079 | 0.27 | 0.67 | 0.9 |
| k=6, x=40%, m_min=5 | 20 | 0.001 | 0.008 | 0.097 | 0.34 | 0.79 | 1.0 |
| k=6, x=40%, m_min=5 | 25 | 0.000 | 0.004 | 0.075 | 0.33 | 0.82 | 0.5 |

## 2. Monte Carlo with clustering (class-level rate ~ Beta, ICC rho)

Clustering stands for shared causes (same lesson, friends comparing answers). a = 0.8, 20 000 reps per cell.

| rule | n | rho | null p=0.15 | alt p=0.50 |
|---|---|---|---|---|
| k=4, x=30% | 12 | 0.0 | 0.048 | 0.77 |
| k=4, x=30% | 12 | 0.05 | 0.078 | 0.73 |
| k=4, x=30% | 12 | 0.15 | 0.123 | 0.69 |
| k=4, x=30% | 25 | 0.0 | 0.048 | 0.97 |
| k=4, x=30% | 25 | 0.05 | 0.110 | 0.90 |
| k=4, x=30% | 25 | 0.15 | 0.170 | 0.80 |
| k=5, x=40% | 12 | 0.0 | 0.010 | 0.56 |
| k=5, x=40% | 12 | 0.05 | 0.030 | 0.55 |
| k=5, x=40% | 12 | 0.15 | 0.066 | 0.53 |
| k=5, x=40% | 25 | 0.0 | 0.004 | 0.82 |
| k=5, x=40% | 25 | 0.05 | 0.031 | 0.74 |
| k=5, x=40% | 25 | 0.15 | 0.088 | 0.67 |

## 3. Bernoulli CUSUM across weeks (alternative for slow build-up)

Designed for p0 = 0.15 vs p1 = 0.40. a = 0.8. 4000 runs per row. 'False signal in a term' = share of 12-week terms with any signal when p = 0.15 throughout. 'Weeks to signal' = median week of first signal when p = 0.50 from week 1.

| n | h | false signal in a term (p=0.15) | x 10 cells (approx, any) | weeks to signal (p=0.50) | detected by wk 2 |
|---|---|---|---|---|---|
| 12 | 2.5 | 0.663 | 1.00 | 1 | 0.97 |
| 12 | 3.5 | 0.289 | 0.97 | 1 | 0.91 |
| 12 | 4.5 | 0.102 | 0.66 | 2 | 0.82 |
| 20 | 2.5 | 0.844 | 1.00 | 1 | 1.00 |
| 20 | 3.5 | 0.435 | 1.00 | 1 | 0.99 |
| 20 | 4.5 | 0.160 | 0.82 | 1 | 0.98 |
| 25 | 2.5 | 0.909 | 1.00 | 1 | 1.00 |
| 25 | 3.5 | 0.527 | 1.00 | 1 | 1.00 |
| 25 | 4.5 | 0.211 | 0.91 | 1 | 0.99 |

## 4. What the recommended rule means in plain numbers

Rule k = 5, x = 40%, m_min = 5: smallest count that flags, by number of attempters.

| attempters | students needed | share |
|---|---|---|
| 5 | 5 | 100% |
| 8 | 5 | 62% |
| 10 | 5 | 50% |
| 12 | 5 | 42% |
| 15 | 6 | 40% |
| 20 | 8 | 40% |
| 25 | 10 | 40% |

## 5. Two-week rolling window for low-activity classes

If only half the class answers on the part each week (a = 0.5), counting distinct students over two weeks gives an effective attempt share of 1 - 0.5^2 = 0.75 (assumes independent weeks and an unchanged rate). Rule k = 5, x = 40%, m_min = 5.

| n | 1-week FA p=0.15 | 2-week FA p=0.15 | 1-week detect p=0.5 | 2-week detect p=0.5 |
|---|---|---|---|---|
| 12 | 0.001 | 0.007 | 0.16 | 0.49 |
| 16 | 0.005 | 0.014 | 0.37 | 0.72 |
| 20 | 0.010 | 0.011 | 0.57 | 0.79 |
| 25 | 0.012 | 0.005 | 0.72 | 0.82 |

## 6. Recommended rule vs the k = 5 alternative (2-week rolling window)

Recommended (our choice): flag when at least 6 distinct students AND at least 40% of students offered that distractor picked it on first attempt, counted over a 2-week rolling window (one window only, so figures can't be differenced). k = 6 means a count of 5 or fewer is never shown (DfE performance-table convention). Effective attempt share over two weeks = 1 - (1 - a)^2. FA = false-alarm probability per misconception per evaluation; 'FA/term' = EXPECTED NUMBER of false flags per term (10 misconceptions x 12 weekly evaluations; overlapping windows, so flags are correlated), not a probability.

| rule | n | a/week | FA p=0.15 | FA/term p=0.15 | FA p=0.25 (stress) | FA/term p=0.25 | detect p=0.35 | detect p=0.50 |
|---|---|---|---|---|---|---|---|---|
| k=6, x=40% | 12 | 0.5 | 0.001 | 0.1 | 0.014 | 1.7 | 0.07 | 0.27 |
| k=6, x=40% | 12 | 0.8 | 0.004 | 0.5 | 0.045 | 5.4 | 0.18 | 0.56 |
| k=6, x=40% | 16 | 0.5 | 0.006 | 0.7 | 0.062 | 7.4 | 0.22 | 0.59 |
| k=6, x=40% | 16 | 0.8 | 0.010 | 1.2 | 0.107 | 12.8 | 0.36 | 0.80 |
| k=6, x=40% | 20 | 0.5 | 0.009 | 1.1 | 0.098 | 11.7 | 0.34 | 0.77 |
| k=6, x=40% | 20 | 0.8 | 0.005 | 0.6 | 0.086 | 10.4 | 0.36 | 0.83 |
| k=6, x=40% | 25 | 0.5 | 0.005 | 0.6 | 0.082 | 9.8 | 0.34 | 0.82 |
| k=6, x=40% | 25 | 0.8 | 0.002 | 0.2 | 0.059 | 7.1 | 0.33 | 0.85 |
| k=5, x=40% | 12 | 0.5 | 0.007 | 0.9 | 0.057 | 6.9 | 0.18 | 0.49 |
| k=5, x=40% | 12 | 0.8 | 0.020 | 2.4 | 0.138 | 16.5 | 0.38 | 0.77 |
| k=5, x=40% | 16 | 0.5 | 0.014 | 1.7 | 0.108 | 13.0 | 0.33 | 0.72 |
| k=5, x=40% | 16 | 0.8 | 0.010 | 1.2 | 0.107 | 12.9 | 0.36 | 0.80 |
| k=5, x=40% | 20 | 0.5 | 0.011 | 1.3 | 0.107 | 12.8 | 0.35 | 0.79 |
| k=5, x=40% | 20 | 0.8 | 0.005 | 0.6 | 0.086 | 10.4 | 0.36 | 0.83 |
| k=5, x=40% | 25 | 0.5 | 0.005 | 0.6 | 0.082 | 9.8 | 0.34 | 0.82 |
| k=5, x=40% | 25 | 0.8 | 0.002 | 0.2 | 0.059 | 7.1 | 0.33 | 0.85 |

