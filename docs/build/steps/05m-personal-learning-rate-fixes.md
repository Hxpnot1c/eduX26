# Step 05m: Recalibrate the personal learning rate (#31, #32)

Branch `build/fix-personal-learning-rate`, from `main`. Follow-up to step [05h](05h-personal-learning-rate.md) (PR #33, merged).

## What
1. **#31: recalibrate to the research.** The new values are in the Settings table below.
2. **Only answers after the first on each part count towards the offset.**
   - A part's first answer belongs to the starting-point adjustment (step [05q](05q-class-coverage-and-starting-points.md)). This stops "already knew it" being counted twice.
   - Here, "first answer" means the student's first evidence row on that part, in `evidence_log` order.
3. **#32: AI-literacy evidence stays out of the offset, and AI-literacy parts use the population learn rate.** `apply_evidence_event` passes `bkt.learn_rate` unchanged for `ail_*` parts.
4. **Off by default (audit item C5, Vishnu's decision of 18 November).** `personalisation.enabled = false`, for the learning-rate offset only. `EDUX_PERSONALISATION=1` turns it on. The starting-point adjustments (05q) stay on. Reasons: after the recalibration the offset barely moves; `docs/research/personalisation.md` §5 says "off until evaluated"; and the ICO Children's Code (Standard 12) says profiling is off by default. See [decision 0007](../../decisions/0007-personal-learning-rate-off-by-default.md).

## Why, with sources
- **Students differ far less in learning rate than in starting knowledge.**
  - Koedinger et al. (2023): about 0.1 log-odds per opportunity, similar across students.
  - Simpson, Norberg & Fancsali (2024): student slope variance is 37–430× smaller than intercept variance.
  - Lee, Lichand et al. (2026): those variance estimates are fragile.
- **Our simulation:** after 48 answers, average surprise correlates only 0.10–0.23 with the true rate. That implies k ≈ 400+ and a scale of about 0.2–1.0.
- **Downward moves allowed more readily:** the direction is from Doroudi & Brunskill (2019).
- **AI literacy is a different skill, measured differently.** An Ask score comes with every research question and would swamp the average.
- **These values replace** `docs/research/personalisation.md` §7 and the `[personalisation]` keys of `settings-proposal.toml`. 05h says so and points to `reference/research.md`.

## Files
- `settings.toml`: the `[personalisation]` values below, with their labels as comments.
- `edux/learner.py`:
  - `learning_offset` leaves out each part's first evidence row (`ail_*` is already left out);
  - `apply_evidence_event` uses the population learn rate on `ail_*` parts.
- `tests/test_personal_learning_rate.py` (pytest, replaces the planned `check_mcp` checks): off by default; the environment switch; a first answer is left out (16 answers on 4 parts give n = 12); AI-literacy evidence leaves the offset alone; an `ail_*` update uses the population rate; the offset stays within the bounds.
- **Docs:** this file; 05h is written to match; `reference/settings.md` (values and labels); `reference/learner-model.md` (first answers, `ail_*`); `reference/research.md` rows if anything ends up different.
- The demo: re-capture each demo student's offset (it will be smaller) and update the 05h "How to check" numbers in the PR description.

## Settings
| Setting | Value | Label |
|---|---|---|
| `learn_rate_k` | 400 | from research spread plus our simulation |
| `surprise_scale` | 1.0 | from our simulation's regression slope |
| `learn_rate_weight_bounds` | [0.7, 1.3] | about ±2 SD of the replicated spread |
| `recency_half_life` | 100 | judgement call: the rate is treated as a stable trait |
| `down_change_factor` | 2.0 | direction from Doroudi & Brunskill (2019); size is a judgement call |
| `max_change_per_session` | 0.25 (as built) | judgement call, starting value |

## Commits
1. `feat(settings): recalibrate the personal learning rate to the research`
2. `fix(learner): leave each part's first answer out of the learning-rate offset`
3. `fix(learner): use the population learn rate on AI-literacy parts`
4. `chore(scripts): check first answers and AI-literacy parts in the offset`
5. `docs(reference): label the personalisation settings`

## Done when
- The startup identifiability check passes at the top bound (0.10 × 1.3 in odds).
- A first answer and `ail_*` evidence leave the offset unchanged.
- Issues #31 and #32 are closed with a one-line comment.
- The gate passes:
  - `check_mcp` passes, with `EDUX_PERSONALISATION=1` and with it unset (off);
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (unchanged).

## Tests
In `scripts/check_mcp.py`, as listed under Files.
