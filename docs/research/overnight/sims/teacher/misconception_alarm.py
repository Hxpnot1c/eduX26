"""Class-level misconception alarm: false-alarm and detection rates (w2-05t).

Question: when should a teacher view flag "this misconception is common in your
class this week"? Analogy: outbreak detection in disease surveillance, which
pairs a statistical threshold with a minimum count (Farrington et al. 1996 as
implemented in R `surveillance`: no alarm with fewer than 5 cases in 4 weeks).

Model (all parameters are OUR CHOICE, not measured):
  * class of n students (A level: 12-25).
  * each student, independently, makes a first-attempt MCQ answer on the part
    this week with probability a (attempters m ~ Binomial(n, a)).
  * each attempter picks the misconception distractor with probability p.
    "Background" p0 = rate in a class where it is NOT a class-wide problem.
    "Outbreak"   p1 = rate in a class where it IS (worth a starter on Monday).
  * one count per student (first attempt), so a student can't trigger it alone.

Rule R(k, x, m_min): flag if attempters >= m_min AND count >= k AND
count / attempters >= x.

Outputs: exact operating characteristics (binomial), family-wise false alarms
per class-week and per 12-week term, a Monte Carlo check with overdispersion
(students' propensities ~ Beta with intra-class correlation rho), and a
Bernoulli CUSUM alternative across weeks.

Pure standard library. Run:
  python docs/research/overnight/sims/teacher/misconception_alarm.py > \
      docs/research/overnight/sims/teacher/results.md
"""
import math
import random

CLASS_SIZES = [12, 16, 20, 25]
ATTEMPT = [0.5, 0.8]            # share of class answering a check on the part this week
P_NULL = [0.10, 0.15, 0.25]      # background rates (0.25 = stress: a very attractive distractor)
P_ALT = [0.35, 0.50]             # class-wide misconception
RULES = [  # (k, x, m_min)
    (3, 0.25, 5),
    (4, 0.30, 5),
    (5, 0.30, 5),
    (5, 0.40, 5),
    (6, 0.40, 5),
]
CELLS_PER_WEEK = 10   # misconceptions with any attempts in a class-week (our choice)
WEEKS = 12            # one term


def binom_pmf(n, j, p):
    return math.comb(n, j) * p ** j * (1 - p) ** (n - j)


def p_flag_given_m(m, p, k, x, m_min):
    if m < m_min:
        return 0.0
    need = max(k, math.ceil(x * m - 1e-9))
    return sum(binom_pmf(m, j, p) for j in range(need, m + 1))


def p_flag(n, a, p, rule):
    k, x, m_min = rule
    return sum(binom_pmf(n, m, a) * p_flag_given_m(m, p, k, x, m_min) for m in range(n + 1))


def exact_table():
    out = ["## 1. Exact per-cell flag probability (one misconception, one class-week)", "",
           "Rows: rule (k = min students, x = min share of attempters, m_min = min attempters). "
           "Null columns are false-alarm rates; alt columns are detection rates.", ""]
    for a in ATTEMPT:
        out.append(f"### Attempt share a = {a}")
        out.append("")
        hdr = "| rule | n | " + " | ".join(f"null p={p}" for p in P_NULL) + " | " + \
              " | ".join(f"alt p={p}" for p in P_ALT) + " | expected false flags/term @p=0.15 (10 cells x 12 wk) |"
        out.append(hdr)
        out.append("|" + "---|" * (3 + len(P_NULL) + len(P_ALT)))
        for rule in RULES:
            for n in CLASS_SIZES:
                nulls = [p_flag(n, a, p, rule) for p in P_NULL]
                alts = [p_flag(n, a, p, rule) for p in P_ALT]
                fa_term = nulls[1] * CELLS_PER_WEEK * WEEKS
                out.append(f"| k={rule[0]}, x={rule[1]:.0%}, m_min={rule[2]} | {n} | " +
                           " | ".join(f"{v:.3f}" for v in nulls) + " | " +
                           " | ".join(f"{v:.2f}" for v in alts) + f" | {fa_term:.1f} |")
        out.append("")
    return out


def beta_sample(rng, mean, rho):
    """Student propensity with mean `mean` and intra-class correlation rho."""
    if rho <= 0:
        return mean
    s = 1 / rho - 1  # alpha + beta
    return rng.betavariate(mean * s, (1 - mean) * s)


def mc_overdispersed(n, a, p, rule, rho, reps, rng):
    k, x, m_min = rule
    flags = 0
    for _ in range(reps):
        # class-level shared shock: draw the class's rate from Beta around p
        pc = beta_sample(rng, p, rho)
        m = sum(rng.random() < a for _ in range(n))
        c = sum(rng.random() < pc for _ in range(m))
        if m >= m_min and c >= k and c >= x * m - 1e-9:
            flags += 1
    return flags / reps


def mc_table(rng):
    out = ["## 2. Monte Carlo with clustering (class-level rate ~ Beta, ICC rho)", "",
           "Clustering stands for shared causes (same lesson, friends comparing answers). "
           "a = 0.8, 20 000 reps per cell.", "",
           "| rule | n | rho | null p=0.15 | alt p=0.50 |", "|---|---|---|---|---|"]
    for rule in [(4, 0.30, 5), (5, 0.40, 5)]:
        for n in [12, 25]:
            for rho in [0.0, 0.05, 0.15]:
                fa = mc_overdispersed(n, 0.8, 0.15, rule, rho, 20000, rng)
                de = mc_overdispersed(n, 0.8, 0.50, rule, rho, 20000, rng)
                out.append(f"| k={rule[0]}, x={rule[1]:.0%} | {n} | {rho} | {fa:.3f} | {de:.2f} |")
    out.append("")
    return out


def cusum_run(n, a, p_true_by_week, p0, p1, h, rng, max_weeks):
    """Bernoulli CUSUM on the stream of first-attempt answers; returns week of first signal or None."""
    up = math.log(p1 / p0)
    down = math.log((1 - p1) / (1 - p0))
    s = 0.0
    for w in range(max_weeks):
        p = p_true_by_week(w)
        m = sum(rng.random() < a for _ in range(n))
        picks = [rng.random() < p for _ in range(m)]
        for hit in picks:
            s = max(0.0, s + (up if hit else down))
            if s >= h:
                return w + 1
    return None


def cusum_table(rng):
    out = ["## 3. Bernoulli CUSUM across weeks (alternative for slow build-up)", "",
           "Designed for p0 = 0.15 vs p1 = 0.40. a = 0.8. 4000 runs per row. "
           "'False signal in a term' = share of 12-week terms with any signal when p = 0.15 throughout. "
           "'Weeks to signal' = median week of first signal when p = 0.50 from week 1.", "",
           "| n | h | false signal in a term (p=0.15) | x 10 cells (approx, any) | weeks to signal (p=0.50) | detected by wk 2 |",
           "|---|---|---|---|---|---|"]
    for n in [12, 20, 25]:
        for h in [2.5, 3.5, 4.5]:
            runs = 4000
            fa = sum(cusum_run(n, 0.8, lambda w: 0.15, 0.15, 0.40, h, rng, WEEKS) is not None
                     for _ in range(runs)) / runs
            fa10 = 1 - (1 - fa) ** CELLS_PER_WEEK
            ds = [cusum_run(n, 0.8, lambda w: 0.50, 0.15, 0.40, h, rng, WEEKS) for _ in range(runs)]
            got = sorted(d for d in ds if d is not None)
            med = got[len(got) // 2] if got else float('nan')
            by2 = sum(1 for d in ds if d is not None and d <= 2) / runs
            out.append(f"| {n} | {h} | {fa:.3f} | {fa10:.2f} | {med} | {by2:.2f} |")
    out.append("")
    return out


def min_detectable(out):
    out += ["## 4. What the recommended rule means in plain numbers", "",
            "Rule k = 5, x = 40%, m_min = 5: smallest count that flags, by number of attempters.", "",
            "| attempters | students needed | share |", "|---|---|---|"]
    for m in [5, 8, 10, 12, 15, 20, 25]:
        need = max(5, math.ceil(0.40 * m - 1e-9))
        out.append(f"| {m} | {need} | {need / m:.0%} |")
    out.append("")
    return out


def window_table(out):
    out += ["## 5. Two-week rolling window for low-activity classes", "",
            "If only half the class answers on the part each week (a = 0.5), counting distinct "
            "students over two weeks gives an effective attempt share of 1 - 0.5^2 = 0.75 "
            "(assumes independent weeks and an unchanged rate). Rule k = 5, x = 40%, m_min = 5.", "",
            "| n | 1-week FA p=0.15 | 2-week FA p=0.15 | 1-week detect p=0.5 | 2-week detect p=0.5 |",
            "|---|---|---|---|---|"]
    rule = (5, 0.40, 5)
    for n in CLASS_SIZES:
        a1, a2 = 0.5, 1 - 0.5 ** 2
        out.append(f"| {n} | {p_flag(n, a1, 0.15, rule):.3f} | {p_flag(n, a2, 0.15, rule):.3f} | "
                   f"{p_flag(n, a1, 0.5, rule):.2f} | {p_flag(n, a2, 0.5, rule):.2f} |")
    out.append("")
    return out


def chosen_table(out):
    out += ["## 6. Recommended rule vs the k = 5 alternative (2-week rolling window)", "",
            "Recommended (our choice): flag when at least 6 distinct students AND at least 40% of "
            "students offered that distractor picked it on first attempt, counted over a 2-week "
            "rolling window (one window only, so figures can't be differenced). k = 6 means a count "
            "of 5 or fewer is never shown (DfE performance-table convention). Effective attempt "
            "share over two weeks = 1 - (1 - a)^2. FA = false-alarm probability per misconception per "
            "evaluation; 'FA/term' = EXPECTED NUMBER of false flags per term (10 misconceptions x 12 "
            "weekly evaluations; overlapping windows, so flags are correlated), not a probability.", "",
            "| rule | n | a/week | FA p=0.15 | FA/term p=0.15 | FA p=0.25 (stress) | FA/term p=0.25 | detect p=0.35 | detect p=0.50 |",
            "|---|---|---|---|---|---|---|---|---|"]
    for rule in [(6, 0.40, 6), (5, 0.40, 5)]:
        for n in CLASS_SIZES:
            for a in ATTEMPT:
                a2 = 1 - (1 - a) ** 2
                f15, f25 = p_flag(n, a2, 0.15, rule), p_flag(n, a2, 0.25, rule)
                out.append(f"| k={rule[0]}, x=40% | {n} | {a} | {f15:.3f} | {f15 * CELLS_PER_WEEK * WEEKS:.1f} | "
                           f"{f25:.3f} | {f25 * CELLS_PER_WEEK * WEEKS:.1f} | {p_flag(n, a2, 0.35, rule):.2f} | "
                           f"{p_flag(n, a2, 0.50, rule):.2f} |")
    out.append("")
    return out


def main():
    rng = random.Random(20261118)
    out = ["# Misconception alarm simulation (w2-05t)", "",
           "All parameters are our choice. Synthetic numbers, not evidence about real classes.", ""]
    out += exact_table()
    out += mc_table(rng)
    out += cusum_table(rng)
    out = min_detectable(out)
    out = window_table(out)
    out = chosen_table(out)
    print("\n".join(out))


if __name__ == "__main__":
    main()
