# Step 05h: A per-student learning rate

Branch `build/personal-learning-rate` (PR #33, merged). Fixes in step [05m](05m-personal-learning-rate-fixes.md), branch `build/fix-personal-learning-rate`. Caching in step [05r](05r-learner-cache.md).

This step doc was written after the merge. It describes the feature as it stands once 05m lands.

**The values here replace those in `docs/research/personalisation.md` §7 and the `[personalisation]` keys of `docs/research/settings-proposal.toml`** (k = 20, bounds [0.5, 1.5]). Those files record the first proposal. Later research found that students differ far less in learning rate than in starting knowledge, so 05m recalibrates. For the current sources, see `reference/research.md`, section "Personalisation: where students start, and how fast they learn".

## What
1. **Migration `011_evidence_immediate.sql`:** `evidence_derived.immediate` records whether evidence was applied as immediate recall.
2. **`learner.learning_offset`:** one global offset per student, in log-odds, applied as an odds weight on `bkt.learn_rate`.
   - **Built from** the recency-weighted mean surprise of evidence in earlier sessions.
   - **Left out:**
     - fatigued and immediate evidence;
     - weight-0 pre-questions;
     - AI-literacy (`ail_*`) evidence;
     - from 05m, each part's **first** answer. First answers belong to the starting-point adjustment in step 05q, so "already knew it" isn't counted twice.
   - **Shrunk** by n / (n + `learn_rate_k`), scaled by `surprise_scale`, and bounded by `learn_rate_weight_bounds`.
   - **Minimum data:** 0 until there are `min_observations` (10) pieces of evidence across `min_parts` (3) parts.
   - **Steps once per session:** it rises at most `max_change_per_session` and falls at most `down_change_factor` times that.
   - **AI-literacy parts use the population learn rate, with no offset** (05m, #32).
   - It is a pure function of earlier events, so rebuild stays identical. It is never shown as a label.
3. **Switches:** `personalisation.enabled = false` by default (changed in step [05m](05m-personal-learning-rate-fixes.md); it was on for the demo). `EDUX_PERSONALISATION=1` turns it on and `=0` off without editing the file.
4. **Startup check:** the identifiability check uses the learn rate at the top bound.
5. **CLI:** `python -m edux.cli state --student <id>` prints the offset, its odds weight and n. Nothing is added to `tutor_turn` or `get_my_progress`.

## Why, with sources
- **Students differ far less in learning rate than in starting knowledge.**
  - Koedinger et al. (2023): about 0.1 log-odds per opportunity, similar across students.
  - Simpson, Norberg & Fancsali (2024): student slope variance 37–430× smaller than intercept variance.
  - Lee, Lichand et al. (2026): these variance estimates are fragile.
- **Our simulation:** after 48 answers, average surprise correlates only 0.10–0.23 with the true rate at research-sized spreads. So the offset is heavily shrunk and narrowly bounded.
- **Downward moves allowed more readily:** the direction is from Doroudi & Brunskill (2019); the factor of 2 is a judgement call.
- **The first proposal** (k = 20, scale 2.0, bounds 0.5–1.5) reads mostly noise at those spreads. It's listed under "Considered and not adopted" in `reference/research.md`.

## Files
- `migrations/011_evidence_immediate.sql`.
- `edux/learner.py`: `personalisation_on`, `learning_offset`, `personal_learn_rate`, and the call in `apply_evidence_event` (from 05m: skipped on `ail_*` parts, and first answers left out).
- `edux/settings.py`: the `[personalisation]` section and the startup check.
- `edux/cli.py`: the offset line in `state`.
- `scripts/check_mcp.py`: the offset is within bounds, absent from the current session alone, and never in a tool result.

## Settings (after 05m)
| Setting | Value | Label |
|---|---|---|
| `personalisation.learn_rate_k` | 400 | from research spread plus our simulation |
| `personalisation.surprise_scale` | 1.0 | from our simulation's regression slope |
| `personalisation.learn_rate_weight_bounds` | [0.7, 1.3] | from research: about ±2 SD of the replicated spread |
| `personalisation.recency_half_life` | 100 | judgement call: the rate is treated as a stable trait |
| `personalisation.down_change_factor` | 2.0 | direction from Doroudi & Brunskill (2019); size is a judgement call |
| `personalisation.max_change_per_session` | 0.25 | judgement call, starting value (as built) |
| `personalisation.min_observations` / `min_parts` | 10 / 3 | judgement call, starting value (as built) |

## Done when
- The offset stays within bounds, is 0 from the current session alone, and never appears in a tool result.
- First answers on a part and `ail_*` evidence don't move it. `ail_*` parts update with the population learn rate.
- Rebuild gives identical state, with personalisation on and off.

## Tests
In `scripts/check_mcp.py` (the personal-learning-rate checks, and the 05m additions).
