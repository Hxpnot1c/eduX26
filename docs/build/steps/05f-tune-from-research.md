# Step 05f: Tune settings and rules from the research review

Branch `build/tune-from-research` (PR #22, merged). Fixes in step [05k](05k-tune-from-research-fixes.md), branch `build/fix-tune-from-research`.

This step doc was written after the merge. It describes the feature as it stands once 05k lands.

## What
1. **Settings from the personalisation review** (`settings.toml`):
   - The guess for open answers (`explain_back`, `past_question`, `link`, `extend`) is 0.20, so one lenient reply can't make a part secure.
   - Review shares are 0.10 / 0.19 / 0.30 (far / mid / near), which puts the exam-anchored spacing the right way round.
   - `bkt.mcq_guess_from_options = true`: a multiple-choice answer guesses 1 / the options shown. Migration `010_evidence_options.sql` adds a nullable `n_options` to `evidence_log`; older rows keep the type's guess.
   - Immediate recall uses `immediate`'s slip and the larger of `immediate`'s guess and the type's own.
2. **Startup check.** Settings fail to load unless, for every evidence type, G + S < 1 and learn_rate < 1 − S/(1 − G).
   - S is taken at `session.slip_cap`.
   - G is taken at its largest: 1/2 for a multiple-choice type, with the immediate rule applied.
3. **Surprise against expected success.** Surprise = score − expected, where expected = p(1 − slip) + (1 − p) × guess for that evidence.
4. **`scheduling.review_when_below = 0.50`.** A part is due at the earlier of its share gap and the time `p_now` is expected to fall below 0.50, with reason `recall_below`.
   - A part already at or below 0.50, or with no forgetting clock yet, keeps the share gap (05k, #23).
   - `min_gap_days` floors the crossing as well as the share gap (05k, #23).
5. **Feedback text:**
   - A wrong idea is named, with one line on why it's wrong, then the right idea, and no praise.
   - A right answer gets one line on why it's right, unless the part was already secure **before** this answer (`data.secure`, 05k, #26). The answer that makes a part secure still gets its why.
   - For open answers at secure, the "what was good" line (`points_met`) stays; only the why is dropped.
   - `style.md`: with no interests, use a neutral everyday example.

**Removed after review**, as the overnight research advised:
- `decay.on_success_immediate = 1.0`: in simulation it left 1.6 of 9 parts secure instead of 6.2 (w1-06-07).
- "Secure only after delayed evidence": replaced by the show-then-pick cap (patch 0010b).

## Why, with sources
- **Open-answer guess, shares and MCQ guess:** the settings proposal (`docs/research/settings-proposal.toml`, `docs/research/personalisation.md` §2.2, §2.3, §6), tested in overnight report 06 (w1-06-04, w1-06-05). In the far scenario, false "secure" on exam day fell by 20.6 points. This is our simulation.
- **Spacing:** Cepeda et al. (2008). The best gap is a smaller share of the time left when the exam is far.
- **Surprise counts guessing and slips**, so weak students aren't cushioned and strong students aren't penalised (overnight report 06).
- **Feedback on right answers helps most when the learner was unsure** (Butler, Karpicke & Roediger, 2008; Wisniewski, Zierer & Hattie, 2020). The answer that tips a part to secure may be a lucky guess, so it's judged on the level before the answer.
- Full rows are in `reference/research.md`, under "Learner model and settings" and "Teaching moves".

## Files
- `settings.toml`, `edux/settings.py`: the values above; the startup identifiability check.
- `migrations/010_evidence_options.sql`: `evidence_log.n_options`.
- `edux/learner.py`: `slip_guess`, surprise in `apply_evidence_event`, `days_until_below` and the `recall_below` reason in `_apply_evidence`.
- `edux/plan.py`: `data.secure` on feedback (from 05k: read at the level before the answer).
- `text/moves/feedback.md`, `text/style.md`.
- `scripts/check_mcp.py`: `n_options` is stored for multiple-choice answers from chat.

## Settings
| Setting | Value | Label |
|---|---|---|
| `bkt.evidence.{explain_back,past_question,link,extend}.guess` | 0.20 | from research: settings proposal, tested in our simulation |
| `scheduling.share_far / share_mid / share_near` | 0.10 / 0.19 / 0.30 | from research: Cepeda et al. (2008), via the settings proposal |
| `bkt.mcq_guess_from_options` | true | from research: standard BKT practice |
| `scheduling.review_when_below` | 0.50 | from the settings proposal, not a study |

## Done when
- Settings with a degenerate type fail to load with a clear error.
- A multiple-choice answer from chat stores `n_options`, and its guess is 1 / n.
- A part above 0.50 gets the earlier of the share gap and the crossing, floored at `min_gap_days`. A part at or below 0.50 gets the share gap.
- A right answer that makes a part secure gets its why; a right answer on a part already secure doesn't. An open answer at secure keeps `points_met`.
- Rebuild gives identical state. No result is over 2,400 characters.

## Tests
In `scripts/check_mcp.py` (the tune-from-research checks, and the 05k additions for #23 and #26).
