# 06 · Settings simulation: three bugs, the proposal's settings, the alarms, and the decay asymmetry

Waves 1 and 3 (overnight 17–18 Nov 2026). Wave 2 added no 06 scout note.

**Sources.**
- **Wave 1.** Scout notes `work/w1/w1-06.md`, blind verifier marks `work/w1/verify-I.json` (w1-06-*), the panel files, and the simulation outputs in [`sims/results/`](sims/README.md). The verifier reran the probes and recomputed every number from `results/metrics.csv`. A partial rerun (seeds 1–2, all variants, both scenarios, 42 runs) reproduced the stored rows exactly.
- **Wave 3.** Scout note `work/w3/w3-06.md` (the decay-clock asymmetry on economics parts), blind verifier marks `work/w3/verify-M.json` (w3-06-*), and the scripts and results in [`sims/decay/`](sims/decay/README.md).
  - The verifier recomputed the crossing times by hand and reran `cases.py`; `results/cases.md` came out byte-identical. It also reran the full 960-student population; `population.md` came out byte-identical.
  - Four of its marks are ~, and their corrections are applied below: the review-gap window (-02), the snapshot range (-04), the nudge case (-06) and the cap's effect (-09).
  - The code read and driven is `origin/main` at `7ad4bb3`, the same as this worktree's HEAD. The verifier notes that the local branch `main` in the build checkout is stale.

**Every result here is simulation: synthetic students, example pack.** The course is `coursepacks/example-mini` (9 parts). The students' memory and behaviour parameters are **our choice** (`sims/README.md`, `sims/decay/README.md`). The outcomes are prediction accuracy (does the model's "secure" or ranking match the simulated truth), load counts and code behaviour. **None of them is a learning gain**, and none is evidence about real 16–18-year-olds.

**How to read the wave-1 numbers.** "± SD" is the spread over seeds in the tables. "± 95% CI" is for paired differences: the same student type and seed under two settings variants. The main run finished 920 of 1,120 planned runs. That is 16–17 seeds per cell: near 17 seeds (one type 16), far 16. The header of `summary.md` says "17 seeds per cell", which is wrong (it counts distinct seeds overall). Anything marked **pilot** comes from 3 seeds (1–3) in the near scenario only.

## Summary
- **Three bugs found by driving the real code. All are small Wednesday fixes (wave 1).**
  1. `p_known` reaches exactly 1.0, and the next exchange crashes `tutor_turn` with a divide-by-zero (w1-06-01 ✓). This could crash a live demo.
  2. Once a part is flagged stuck, every later plan in the session is the same prerequisite check (w1-06-02 ~).
  3. "Quiz me on what's due" teaches the old focus instead of the due reviews (w1-06-03 ✓).
- **"Secure" goes stale, and the proposal's settings help.** Far scenario, current settings: on exam day, on average 76% of the parts the model calls secure are truly below 0.5 mastery. The proposal's settings that the code already reads cut this to 55% (−20.6 ± 5.8 CI). They also raise truly secure parts by +0.5 (near) and +0.8 (far) of 9, and cut reviews due per morning from 4.5 to 2.9 (w1-06-04 ✓, -05 ✓, -06 ✓). For the pitch, always show the false-secure bar and the coverage bar together.
- **Don't ship `on_success_immediate = 1.0`.** Emulated, it leaves 1.6 of 9 parts model-secure at the end (current 6.2) and 3.1 fewer truly secure parts (near). The cause: 59–80% of evidence counts as "immediate" (w1-06-07 ✓).
- **The alarms are weak (wave 1).**
  - The built fatigue detector flags 12% of the tired student's sessions against 11% of others'. That is a likelihood ratio of about 1.1 (pilot; w1-06-08 ~).
  - The stuck detector finds the truly stuck part in 99% of sessions. But it raises false flags in up to 43–47% of slow and tired students' sessions (far), and each one starts the bug-2 loop (w1-06-12 ~).
  - The always-"A" guesser hits 32–34% on 3-option checks, yet averages only 0.06–0.12 parts model-secure. The offloader is the bigger overconfidence risk (w1-06-10 ~).
- **The decay-clock asymmetry ranks economics parts wrongly on `main` (wave 3).** A part answered right once reads .646. It falls below "new" after 2.8 days and below an untouched part (.30) after 4.4 days. After 8.5 days it falls below a part answered wrong once and never right, which stays frozen at .149 (w3-06-01 ✓).
  - Spacing doesn't hide this whenever the exam is more than about 30 days away. The review gap is then longer than the 4.4-day crossover (w3-06-02 ~, corrected).
  - Across 960 synthetic students, a never-right student read above a right-at-least-once student in 0.82–1.00 of pairs at day 30 (w3-06-03 ✓).
  - Inversions that the simulated truth supports are only 0.00–0.05 of pairs from day 14 on (0.07–0.08 at day 7). Most are plain errors (w3-06-04 ~).
- **Two more paths keep a never-right part high, with no decay (wave 3).**
  - *Propagation:* six right answers on `ped_values` lift its never-answered prerequisite `ped_formula` to .527 (developing) for good. A developing prerequisite no longer triggers the prerequisite check (`plan.py:359-361`: `level == "new"`) (w3-06-05 ✓).
  - *Talk alone:* 14 exchanges with no check take a part to .763 (**secure**), and it stays frozen. An "untested" review is queued, due immediately, but nothing re-tests it unless that review is taken (w3-06-06 ~).
- **Fixes compared: build (b) + (c) together (wave 3).**
  - **(c)** decays towards the part's prior instead of 0. Day-30 inversions fall from 0.82–1.00 to 0.03–0.26, and AUC against truth rises from 0.48–0.59 to 0.62–0.71. The level shown changes in 5–11% of readings (w3-06-08 ✓).
  - **(b)** caps never-right parts at the prior and shows "not yet shown". It removes every never-right part shown as developing or secure, and leaves rankings almost unchanged (w3-06-09 ~).
  - **(a)**, starting the clock on wrong answers too, helps little alone (w3-06-08 ✓).
  - All variants are deterministic: live state equals two rebuilds in 5,760 of 5,760 runs (w3-06-10 ✓).
- **What users see today.**
  - Within one student, the inversion is live: `_levers`, `weak_prerequisites`, the prerequisite gate and the levels shown all read `p_now` (w3-06-07 ✓).
  - Across students it is latent, because no code on `main` compares students yet. It matters for any future teacher view and for evaluation.

## Ranked recommendations

Ranks 1–8 are the wave-1 list, unchanged (other reports cite recs 1–3 and 8). Wave 3 adds ranks 9–14. Ranks 1–11 can be done before Thursday 23:59; 12 is "maybe"; 13–14 come later.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | Clamp `p_known` to [0.001, 0.999] (bug 1). Add a test: 50 correct checks on one part, then one more exchange, with no exception. | build | S | yes | w1-06-01 ✓ |
| 2 | Break the step-back loop: one prerequisite check per stuck part per session, then reteach or switch (bug 2). | build | S | yes | w1-06-02 ~, w1-06-12 ~ |
| 3 | Make "Quiz me on what's due" reach the reviews (bug 3). This is needed before any spacing claim in the pitch or video. | build | S | yes | w1-06-03 ✓ |
| 4 | Adopt the proposal's settings that the code already reads: `share_far = 0.10`, `share_mid = 0.19`, `share_near = 0.30`, and guess 0.20 for `explain_back`, `past_question`, `link` and `extend`. | settings | S | yes | w1-06-04 ✓, -05 ✓, -06 ✓ |
| 5 | **Don't ship `on_success_immediate = 1.0`.** If the rule is built, use about 1.5 (our choice), or apply it only to MCQ checks straight after `teach_point`, not to explain-backs. Better: shorten `evidence.immediate_window_minutes` (now 30) and choose the value by replay. | settings, build | S (setting), M (code) | setting yes; code no | w1-06-07 ✓ |
| 6 | Show staleness on "secure" in `get_my_progress`: "secure, last checked N days ago". Or show "developing" when the last correct answer is more than about 30 days old (our choice). | build, demo | S | yes | w1-06-04 ✓ |
| 7 | Raise `session.fatigue_threshold` from −0.25 to −0.35 (our choice). Treat `offer_stop` as an offer only. Consider `fatigue_slip_add = 0` until a better detector exists, because a false alarm silently discounts real errors. | settings | S | yes | w1-06-08 ~ (pilot); w1-06-09 ✓ (confounded, see below) |
| 8 | Pitch chart: "eduX tested its own alarms" (chart below). Always caption it "simulation: synthetic students, example pack". The wave-3 deck outline ([pitch-notes](pitch-notes.md) §(c)) moves it off the 8 slides, to the leave-behind and a back-up slide for Q&A. | pitch, video | S | yes | w1-06-04 ✓, -05 ✓ |
| 9 | **Decay towards the prior (fix c), built together with rec 10 (variant `bc`).**<br>• In `edux/learner.py`, give `p_now` a `floor` argument: `return floor + (p_known - floor) * 0.5 ** (days / half_life_days)`.<br>• `_p_at(state, ts)` and `part_p` pass `initial_state(part_id)[0]`. About 8 lines.<br>• Update the decay section of `docs/build/reference/learner-model.md`: "evidence goes stale towards the starting estimate".<br>• Run `rebuild_all()` after deploying, because later posteriors change.<br>• Add a test that a part whose latest evidence was right never reads below an untouched one. A part answered right and then wrong can still read below the prior (.208 in `fix_cases`). | build | S–M (2–3 h with tests and docs) | yes, if the build day allows | w3-06-01 ✓, -03 ✓, -08 ✓, -10 ✓ |
| 10 | **Cap never-right parts at the prior, and show "not yet shown" (fix b).**<br>• In `part_p`: `if row["last_correct"] is None: p = min(p, prior)`. Read-time only; stored state and rebuilds are unchanged.<br>• Where a level is shown for a part with `last_correct IS NULL`, show "not yet shown". This needs a 4th label in `service._node_entry`/`_part_summary`, or a separate `shown: false` flag.<br>• **Keep `level()` returning "new"**, so the `== "new"` gates (prerequisite check, `known_parts`, `intuition_source`) don't change.<br>• This alone removes the propagation and talk-only inflation (w3-06-05 ✓, -06 ~). **If the build day is too full, build this one alone** (about 4 lines) and use the "not yet shown" wording in the demo. | build, demo | S (code ~1 h); the label M | yes | w3-06-05 ✓, -06 ~, -09 ~ |
| 11 | **Pitch and video wording:** "A part only counts as known once the student has got it right. Until then it says *not yet shown*." This is the censoring idea from reliability engineering: no observed success, no certificate. Say it only after rec 10 lands. | pitch, video | S | yes (after rec 10) | w3-06-09 ~, -11 ✓ |
| 12 | **Re-run the 05e How AI works AUC (w2-02-05 ~) with fix (c).** It should improve by construction, but it is untested. This report tests economics parts on `main` only. | sims | S | maybe | open |
| 13 | **Store the prior at first touch** (a `p_floor` column in `part_state`, set in `_load_state`), so fix (c) stays rebuild-stable when difficulty changes or `w_cross > 0`. It needs a migration. Until then keep `difficulty.w_cross = 0` (it is 0 today) and don't edit teacher difficulty without a rebuild. | build | M | no | w3-06-10 ✓ |
| 14 | **Latent: hard parts start below the candidate band.** A difficulty-0.7 part starts at prior 0.24, below `queue_band` 0.30, so `learner.candidates()` would never offer it untouched. It isn't live today. Fix it before wiring `candidates()` in, e.g. band floor = `min(prior)`. | build | S | no | w3-06-07 ✓ |

## The three bugs (rank first: Wednesday fixes)

All three reproduce deterministically with `sims/probes.py`, on the real code path with no sim clamp. The verifier confirmed the line numbers.

| # | Bug | Where (file:line) | Effect | One-line fix idea | Finding |
|---|---|---|---|---|---|
| 1 | **Divide-by-zero crash.** The BKT update plus the learn step `p += (1 − p) × learn_rate` has no upper clamp, so `p_known` reaches exactly 1.0 in floating point. `apply_exchange` then computes `odds = p / (1 − p)`. | `edux/learner.py:634-637` (update, saved at `:650`); `edux/learner.py:457` (the division) | Probe: 44 correct `mcq_check` answers 2 minutes apart on one part, then the next ordinary exchange raises `ZeroDivisionError` and `tutor_turn` fails. Main run, current settings: 11 saturations per run (near), 4 (far), and 66 for the stuck student (near). Without the sim clamp, each of these would have crashed the next exchange on that part. | Clamp `p_known` to [0.001, 0.999] after the update in `_apply_evidence` and again in `apply_exchange`. | w1-06-01 ✓ |
| 2 | **Step-back loop.** The plan returns the prerequisite check whenever the session is "stuck" and the focus is the stuck part. `stuck_parts` is recomputed over the whole session's evidence, so the flag never clears. An answer keeps `last["focus"]`, so the focus stays on the stuck part. | `edux/plan.py:332-337`, with `edux/learner.py:785-822` (`stuck_parts`) and `edux/service.py:243-244` (focus carried over) | Probe: 12 of 14 consecutive plans were the same prerequisite check, answered right every time. Main run: the longest streak per session is 16–17 for the stuck student, and 6–7 for the typical student in the near scenario (5.6–8.7 in far). | Step back once per stuck part per session. After a correct prerequisite answer, reteach the whole part through its anchor, or offer another part. | w1-06-02 ~ (typical-student streak of 6–7 is near only) |
| 3 | **"Quiz me on what's due" misses the reviews.** A message that resolves to no parts falls back to `last["focus"]`, with no session or time check. So the `reviews_only` branch, whose code comment says it is for "quiz me on what's due", is never reached. | `edux/service.py:246-247`, with `edux/plan.py:343-348` (the unreachable branch) | Probe: 2 parts due, asked 5 days after studying another part. The plan teaches the old part and offers 0 of the 2 reviews. A chatbot that passes the due parts' `node_ids` avoids the bug, but the `review_due` prompt doesn't send them. | Don't inherit `last["focus"]` when the message has no parts and is a review cue, or when the last turn was in an earlier session. Or have the `review_due` prompt send a flag. | w1-06-03 ✓ |

Bug 1 is reachable in one session, and bug 2 makes it more likely: the stuck student, who keeps answering the same prerequisite check right, hit 66 saturations per run (w1-06-01 ✓). Without the sim clamp, any of these could crash a live demo. Fix both before filming.

### Evidence for rank 7 (fatigue threshold)

The only clean test of the threshold alone is the pilot replay. On the same logs, moving from −0.25 to −0.35 cut false alarms on other students' sessions from 11.3% (71/630) to 5.9% (37/630). Recall on tired sessions fell from 12% (13/105) to 10% (10/105) (`pilot_detector_sweep.md`).

The main run's `tuned` variant cut flagged sessions from 11% to 4% (−6.4 ± 1.2 CI, near; w1-06-09 ✓). But that drop **can't be credited to the threshold**. `proposal_shims` keeps the threshold at −0.25 and falls by about as much (−6.8 ± 1.4 near, −4.9 ± 1.6 far), so the emulated shims cause most of it.

## Settings results: current vs proposal (paired)

Simulation: synthetic students, example pack. Mean ± SD over seeds, all 7 student types pooled. The paired column gives the proposal minus current, with a 95% CI.

| Metric | Scenario | Current | Proposal | Paired difference | Pairs | Finding |
|---|---|---|---|---|---|---|
| "Secure" parts truly below 0.5 mastery, exam day | far | 76% ± 23 | 55% ± 30 | −20.6 ± 5.8 pts | 96 | w1-06-04 ✓ |
| Same | near | 7% ± 11 | 3% ± 7 | −3.5 ± 2.0 pts | 101 | `summary.md` |
| Overconfidence on exam day (model − truth) | far | +0.37 ± 0.24 | +0.26 ± 0.23 | −0.11 ± 0.03 | 112 | w1-06-04 ✓ |
| Parts truly secure at the end (of 9) | near | 6.40 ± 2.47 | 6.90 ± 2.48 | +0.50 ± 0.18 | 118 | w1-06-05 ✓ |
| Same | far | 3.88 ± 2.06 | 4.68 ± 2.48 | +0.80 ± 0.28 | 112 | w1-06-05 ✓ |
| Parts model-secure at the end (of 9) | far | 6.14 ± 3.14 | 5.05 ± 2.80 | (not paired in summary) | — | `summary.md` |
| Reviews due per morning, last 14 days | near | 4.50 ± 1.74 | 2.89 ± 1.11 | −1.60 ± 0.18 | 118 | w1-06-06 ✓ (near only) |
| Parts truly below 0.5 when they first turn secure | near | 23% ± 21 | 24% ± 23 | +1.2 ± 1.8 pts | 118 | w1-06-11 ✓ |

How to read it:
- **The 76% is a mean of per-run shares.** It averages over the 96 runs that had any secure part on exam day. It is not a pooled share of parts (verifier note on w1-06-04).
- **The proposal makes the model more cautious *and* gets more parts truly secure (far scenario).** The model calls fewer parts secure (6.1 → 5.1), and more parts are truly secure (3.9 → 4.7). Both changes go the right way.
- **Reviews due is a backlog count, not reviews shown.** Bug 3 means reviews rarely surface in normal plans. The simulated students named due parts themselves, which flatters eduX (`sims/README.md`).
- **About 23% of parts are truly weak at the moment they first turn secure, under every variant tested** (w1-06-11 ✓). Fixing this needs a code change: require a correct check in a later session before showing "secure". See Later.

**Why "secure" goes stale.** Every in-session success doubles the half-life. And 59–80% of all evidence falls inside the 30-minute "immediate" window after a worked example (w1-06-07 ✓; range across variants and scenarios). So a part answered right a few times in one sitting looks durable months later. In our truth model, massed retrieval strengthens real memory only ×1.1 (our choice). `sensitivity.py`, which tests other values, was not run.

**`on_success_immediate = 1.0` (emulated in `proposal_shims`, not built).** Near scenario, against current:
- Model-secure parts at the end: 1.63 vs 6.19.
- Truly secure parts at the end: −3.07 ± 0.33 (118 pairs).
- Far: −1.57 ± 0.31 (112 pairs).

Students never get past their first parts, because almost no evidence grows the half-life. Its far-scenario false-secure figure looks best (−38.6 ± 13.8 pts), but that is on only 35 pairs. It looks good only because almost nothing turns secure.

**The `tuned` package** is the proposal plus `on_success_immediate = 1.5` (shim), `mcq_guess_from_options` (shim) and fatigue −0.35. It had the best calibration (far overconfidence +0.06 against current +0.37). But it ended with fewer truly secure parts than current (−0.28 ± 0.29 near, −0.47 ± 0.30 far). Rejected as the headline; see below.

## Fatigue and stuck detectors: precision

### Fatigue (pilot only: 3 seeds, near scenario, open-loop replay)
- **Built detector (threshold −0.25, window 4, min parts 2).**
  - Recall: 12% of tired sessions flagged (13/105).
  - False alarms: 11.3% of other students' sessions (71/630).
  - Likelihood ratio about 1.1. Precision 15% in the simulated mix (1 tired type in 7) (w1-06-08 ~).
- **Grid of 24 settings.** Most settings have a likelihood ratio of 0.8–2. A few strict settings reach 2.4–4.0, but only at very low recall and tiny counts. For example, −0.45 / window 6 / min parts 2 flags 2/105 tired sessions against 3/630 others (verifier correction to w1-06-08). **No grid setting gives a useful detector.**
- **Main run (16–17 seeds), current settings.**
  - The tired student is flagged in 14% (near) and 13% (far) of sessions.
  - Other types are flagged in 1–15% of sessions (`summary.md`).
  - So the pilot picture holds.
- **Alternative rules: not verified, output not saved.** The scout's pilot run tried two alternatives:
  - "errors on material the model thinks is known";
  - a drop against the session's own baseline (a control-chart idea).

  Both reportedly reached a likelihood ratio of about 3–4. This was in-sample, and the scratch script (`/tmp/claude-1000/w1-06/altfat.py`, not in the repo) only printed its results. **Treat these as ideas to test, not findings.**
- **Cross-field link (analogy only).** Clinical alarm fatigue: monitors with mostly false alarms get ignored. The scout checked this only through a secondary source, so it is not a claim here.

### Stuck (pilot and main run, labelled)

| | Pilot (3 seeds, near) | Main run (16–17 seeds), near | Main run, far |
|---|---|---|---|
| Recall on the true stuck part | 99% (102/103) | 99% (548/552) | 99% (317/320) |
| False-flag sessions: typical | 8% | 10% | 17% |
| slow (ambiguous: may truly be stuck) | 30% | 23% | 47% |
| tired | 30% | 37% | 43% |
| guesser | 100% | 100% | 100% |

Source: w1-06-12 ~; the verifier says the main run's shares differ from the pilot and are higher in the far scenario. Each false flag currently starts the bug-2 loop. So fixing the loop matters more than tuning the rule. The pilot's alternative stuck rule (B: the same point missed on three checks) had 7% recall, because `reteach_limit = 1` moves on after two misses. Rejected.

## Gaming

- **The always-"A" guesser is held back by open answers** (w1-06-10 ~).
  - Hit rate on 3-option checks: 33–34% (near) and 32–33% (far). On 4-option checks: 23–26%. The model assumes a guess of 0.25.
  - Even so, it averaged only 0.06–0.12 parts model-secure at the end (near and far, current and proposal). Some runs reach 1 part. It is not "0 of 9" as the scout wrote.
- **`mcq_guess_from_options` (guess = 1/n options) is right in principle but changed little here.** Most MCQ checks fall in the immediate window and are scored with the immediate guess (0.30) instead (w1-06-07 ✓; pilot decay replay: `proposal+mcq_guess` is identical to `proposal`).
- **The offloader is the overconfidence risk.** It says "just show me" and gives surface answers.
  - Far scenario, exam day: its parts are rated +0.87 (current) and +0.73 (proposal) above truth.
  - Near: +0.23 and +0.14.
  - Source: `summary.md`, main run. The scout's "+0.6 to +0.9" was a pilot figure.
- **What the sim doesn't test:** the teacher's and student's objection, a student who picks the shortest option (see Panel objections).

## Recommended chart for the pitch

**"eduX tested its own alarms"**: two small grouped bar charts side by side. Both use the far scenario and compare current with evidence-based settings.

| Panel | Current | Evidence-based settings | Paired difference |
|---|---|---|---|
| "Secure" but not known on exam day | 76% | 55% | −21 pts (95% CI ±6) |
| Parts truly secure at the end (of 9) | 3.9 | 4.7 | +0.8 (95% CI ±0.3) |

- **Always show both panels.** A model that never says "secure" scores 0% false secure. `proposal_shims` shows this: it has the best false-secure figure (−39 pts) and the worst coverage. The coverage bar stops the first bar misleading.
- Optional third panel (near scenario): reviews due per morning in the last two weeks, 4.5 → 2.9.
- Caption, on the slide: "Simulation: synthetic students on our 9-part example pack. Not a learning result."
- **Don't reuse `results/false_secure.svg` as it is.** It plots all four variants with SD whiskers, on an axis that runs to 114%, and has no coverage panel. Build the chart fresh from the numbers above.
- Say "evidence-based settings", not "tuned". The `tuned` variant is a different package.

## Decay-clock asymmetry on economics parts (wave 3)

**Question.** On `main`, `p_now` decays only once a part has a clock, and the clock starts only on a right answer (`edux/learner.py`: `p_now` returns `p_known` when there is no clock; `_apply_evidence` sets `clock_start` only on a correct answer). Does this rank economics parts or students wrongly? Which fix keeps BKT's meaning and rebuild determinism? [02](02-ai-literacy-assessment.md) found the same asymmetry on the 05e branch's How AI works parts (w2-02-05 ~) and asked for this check (02 rec 26).

**Method.** All in [`sims/decay/`](sims/decay/README.md):
- `cases.py` and `fix_cases.py` push first-principles students through the real `edux.learner` code;
- `population.py` runs 960 synthetic students (60 seeds × 4 types × 2 scenarios × 2 truth regimes), with the event log replayed under each fix so comparisons are paired;
- `analyse.py` builds the tables.

Fixes are in-memory patches; no repo file was edited. **Simulation: synthetic students, example pack.**

### What goes wrong on `main` (deterministic cases, real code)

| student on one part (prior .30) | p_now | below "new" (.40) | below untouched (.30) | below wrong-once (.149) |
|---|---|---|---|---|
| U: untouched | .30, frozen | — | — | — |
| W: wrong once, never right | .149, frozen (no clock) | — | — | — |
| C: right once (`mcq_check`), half-life 4 days | .646 | 2.8 days | 4.4 days | 8.5 days |
| CCC: right on days 0, 2, 6, half-life 16 days | .833 | — | 23.6 days after the last | 39.8 days after the last |

Source: `results/cases.md` (w3-06-01 ✓). The verifier recomputed these from `settings.toml` and `learner.py:379-387, 615-646`. The frozen value equals the prior only for untouched parts. Other never-right parts freeze wherever their evidence left them: .149, .527, .763 (w3-06-11 ✓ note).

**Spacing doesn't hide it unless the exam is close.** The review gap after a right answer is a share of the days left to the exam (`learner.review_gap_days`). It is longer than the 4.4-day crossover whenever the exam is more than about 29.5 days away: 37.5 days at 150 days out (p_now .001 when the review falls due), 22.5 at 90, 15.2 at 61, 6.8 at 45 and 4.5 at 30. Inside about 30 days the gap is shorter. At 20 days the gap is 3.0 days and the part still reads .385 when due, above the untouched .30 (w3-06-02 ~, the verifier's correction of "only within about 14 days").

**Two paths keep a never-right part high with no decay at all.**
- **Propagation (w3-06-05 ✓).** Six right answers on `ped_values`, two days apart, lift its never-answered prerequisite `ped_formula` .30 → .369 → .433 → .479 → .506 → .520 → .527 (developing) through `prereq_boost`. It has no clock, so it still reads .527 at day 40 and day 100 (`learner.py:652-660`, `384-385`). A developing prerequisite is never offered a prerequisite check, because `plan.py:359-361` offers it only when `level == "new"`. **A student can skip a prerequisite they never showed.** The learning risk is untested.
- **Talk only (w3-06-06 ~).** Fourteen transfer + constructive exchanges with no check (odds × 1.1 × 1.05 each) take `pes_definition` from .30 to **.763 (secure)**. The part has no clock, so it stays frozen (`learner.py:460`, `384-385`). An "untested" review is queued and due immediately (`learner.py:471-472`), so the part is re-checked only if that review is taken. Verifier's correction: .788 is the value after a 15th exchange, not the same 14-exchange state 90 days on. This is the "can a student chat their way to secure?" case a judge may probe.

### Across and within students (population, 960 synthetic students)

Pairs compare a student never right on a part (A) with a student right at least once on the same part (B). "Inverted" means A reads above B.

| measure | current, day 30 | source |
|---|---|---|
| Across students: A above B | 0.82–1.00 of pairs (by cell: .998 / .997 / .922 / .825) | w3-06-03 ✓ |
| … by days since B's last right answer: 0–3 / 3–7 / 7–14 | 0.30–0.34 / 0.79–0.84 / 0.96–0.98 (these bins pool all snapshots, not only day 30) | w3-06-03 ✓ |
| Within one student, across parts | 0.84–1.00 (.999 / .998 / .921 / .835) | w3-06-03 ✓ |
| Inversions the truth supports (A really knows it better) | 0.00–0.05 of pairs from day 14 on; 0.07–0.08 at day 7 | w3-06-04 ~ |
| Inversions the truth contradicts | 0.51–0.61 from day 14 on; 0.38–0.40 at day 7 (the rest are truth ties, both forgotten) | w3-06-04 ~ |
| Full review compliance vs none | far 0.85 → 0.86; near 0.78 → 0.62–0.71 | w3-06-04 ~ |

### Who sees it today (w3-06-07 ✓)
- **Live readers of `p_now`:**
  - part levels (`context_blocks.py:56`) and topic rollups (`learner.py:693-702`; `service.py:309, 347`);
  - `_levers` (`service.py:325-333`) and `weak_prerequisites` (`context_blocks.py:266-285`);
  - the prerequisite-check gate (`plan.py:359-361`) and `support_level` (`plan.py:394, 434`);
  - `known_parts` (`context_blocks.py:709-712`) and `intuition_source` (`context_blocks.py:191-199`).
- **Within one student the inversion is live.** `_levers` and `weak_prerequisites` both score `(1 − p)`, so a decayed part outranks an untouched one for lever or prerequisite priority. `p_now` also goes to the chatbot in `_part_summary`.
- **The level shown mostly doesn't invert.** A decayed part and an untouched one both read "new". A visibly wrong level comes from propagation or talk lifting a never-right part to developing or secure: 0.8–2.2% of never-right readings.
- **Not affected:** `due_reviews` sorts by importance and due date only (`learner.py:714`).
- **Latent:** no code on `main` compares students, and `learner.candidates()` has no live caller. The across-student numbers matter for any future teacher view and for evaluation (AUC), not for today's product.

### The fixes, on identical event logs

| fix | what changes | keeps BKT's meaning? | stored state | rebuild-stable? | size |
|---|---|---|---|---|---|
| (a) clock starts on any evidence | a wrong answer before any right one also starts the clock | **Yes.** It is the version consistent with BKT-with-forgetting. But untouched parts stay frozen at the prior, so every attempted part sinks below untouched ones (a "trying penalty") | changes (`clock_start`) | yes | 1–2 lines |
| (b) cap never-right at the prior; show "not yet shown" | read-time cap in `part_p` | **Yes.** It is a display rule; BKT is untouched | unchanged | yes (identical) | about 4 lines + a label |
| (c) decay towards the prior | `p = prior + (p_known − prior)·0.5^(d/h)` at read time and inside updates | **Not strictly.** `p_now` becomes a belief that relaxes to the base rate when evidence goes stale. In exchange it matches the permanent prior the model already uses | later posteriors change | yes, while the prior is fixed (`w_cross = 0`, no difficulty edits) | about 8 lines |

| variant | inversions (near, floor 0, day 30) | all cells, day 30 | AUC vs truth | level shown changed | never-right shown developing+ | Brier, far exam day (floor 0 / 0.3) |
|---|---|---|---|---|---|---|
| current | 0.92 | 0.82–1.00 | 0.48–0.59 | — | 0.8–2.2% | 0.028 / 0.061 |
| (a) alone | 0.73 | 0.62–0.80 (across snapshots) | — | — | — | — |
| (b) alone | 0.92 | as current (within about .004) | as current | 0.4–1.1% | **0** | as current |
| (c) alone | 0.26 | 0.03–0.26 | 0.62–0.71 | 5–11% | 0.9–2.3% (as current) | 0.078 / 0.050 |
| (b)+(c) | 0.25 | 0.02–0.25 | 0.62–0.72 (highest tested) | 5.5–12% | 0 | 0.077 / 0.049 |

Sources: `results/population.md`, w3-06-08 ✓ and w3-06-09 ~. Notes:
- **(b) is not quite identical on ranking.** It stays within 0.003 of current on AUC and nearly all inversion cells. One within-student cell differs by .004 (.730 vs .726). Its stored final state equals current in 960 of 960 students (w3-06-09 ~).
- **(c)'s gain is largest at day 30 and shrinks later.** In the far, floor-0 cell, its inversion share rises to 0.26–0.33 at days 45–60 (`population.md`).
- **(c) trades calibration for ordering.** If true memory really falls to zero, Brier gets worse (0.028 → 0.078) and false secure rises from 0.0002 to 0.0025 (near, floor 0). If some memory remains, Brier improves (0.061 → 0.050). Which regime is right for A level economics is unknown.
- **(a)+(c)** was slightly worse than (b)+(c) on every metric.

**Recommendation: (b)+(c)** (recs 9–10). This knowingly trades strict BKT meaning for internal consistency and correct ordering. If strict BKT meaning matters more, build (a)+(b). That pair wasn't run as such, and (a) alone left 0.62–0.80 inversions. **Fallback if Wednesday is full:** (b) alone. It fixes what a student or judge can see (no never-right part shown as developing or secure), but not the ordering.

**Determinism (w3-06-10 ✓).** Live part state equalled `rebuild_state`, and two rebuilds equalled each other, in 5,760 of 5,760 student × variant runs. The check covers `p_known`, `half_life_days`, `clock_start`, `last_correct` and `n_evidence`.
- All three fixes are deterministic functions of the log and settings.
- (a) and (c) change stored state, so run `rebuild_all()` after deploying.
- (c) is stable only while the prior it decays towards is stable: `difficulty.w_cross = 0` and teacher difficulty unchanged. Storing the prior at first touch removes this condition (rec 13).

### Cross-field link (reliability engineering; analogy, w3-06-11 ✓)
- In survival analysis, a unit with no observed event is **censored**: you know only that its event time lies beyond what you watched (Kaplan & Meier 1958). Treat "first right answer" as the event, and a never-right part is censored.
- `main` doesn't age censored parts, but ages every part with an observed event towards 0. That is the familiar bias of ageing only inspected units: units with no record look newer than ones that were inspected and passed.
- The two standard remedies map onto the fixes:
  - don't certify a unit with no observed success: fix (b), "not yet shown";
  - shrink a stale estimate back to the fleet baseline, not to zero: fix (c).
- In maths, a two-state learnt/forgotten chain with forgetting rate λ and relearning rate μ relaxes to π = μ/(λ+μ). `main` uses π = 0 for clocked parts but keeps the untouched prior .30 forever, which is π = .30. So the model holds two equilibria at once, and (c) makes them agree.
- **This is an analogy.** It explains the inconsistency; it is not evidence that students' memory has a floor.

## Limits

- **Example pack only.** `example-mini` has 9 parts. Real course packs have more parts and different prerequisite structures.
- **Synthetic students.** There are 7 types (typical, slow, fast, guesser, offloader, tired, stuck). No real logs were used.
- **The parameters are our choice:**
  - learn rates, slip 0.10;
  - memory recall = exp(−days/S), S = 4 days, ×2 after spaced and ×1.1 after massed retrieval;
  - the tired student's slip 0.45 from minute 30;
  - 5% lucky ticks on open answers.

  The far-scenario false-secure result depends most on the massed-retrieval value.
- **`sensitivity.py` was not run.** The far-scenario gap has not been checked under other memory assumptions.
- **The main run is partial.** 920 of 1,120 runs finished, 16–17 seeds per cell. The detector and decay sweeps are **pilot only** (3 seeds, near). The main-run re-sweep was stopped. The pilot seeds (1–3) are inside the main run, so the pilot-chosen parameters have not been tested on held-out logs.
- **Two harness choices flatter or cap results:**
  - Simulated students name due parts themselves, which flatters the review results (see bug 3).
  - The sim clamps `p_known` at 1 − 1e-9 so that runs continue (bug 1).
- **Shims are emulated, not built.** `on_success_immediate` and `mcq_guess_from_options` exist only in the sim.
- **What was measured:** prediction accuracy against a simulated truth, load counts and code behaviour. No learning outcome.
- **Wave 3 (decay) limits.**
  - Its truth model is separate from wave 1's and is also our choice: one memory trace per part, S = 4 days, ×2 after a spaced right retrieval, a floor of 0 or 0.3 ([`sims/decay/README.md`](sims/decay/README.md)).
  - The study policy reads only due dates, so it is an open-loop comparison on identical logs. It doesn't show how a fix would change what the tutor asks next.
  - Population exchanges carry no nudge. The talk-only path is shown only in `cases.py`.
  - The pack has 9 parts. On a full course most parts are untouched, so untouched-vs-decayed inversions would be more common, not less.

## Later (not before Thursday; for the business plan and Q&A)
- **Require a correct check in a later session before showing "secure".** This targets the 23% of parts that are truly weak when they first turn secure (w1-06-11 ✓). Code change, M.
- **Prototype the "errors on known material" fatigue rule.** Test it on held-out logs (seeds ≥ 4 of the main run), not the pilot seeds. M.
- **Choose `immediate_window_minutes` by replay** with `sweep_decay.py`.
- **Run `sensitivity.py`** to check whether the far-scenario gap survives `stability_growth_massed = 2.0`.
- **Build `mcq_guess_from_options`** (guess = max(1/n, immediate)) and keep explain-back gating (w1-06-10 ~). It barely matters until the immediate window shrinks.
- **Replace the truth model with values fitted to real pilot logs** (slip, guess, learn rate).
- **Fit real retention curves (wave 3).** Does A level economics memory fall to 0 or keep a floor? The answer decides whether fix (c) improves or worsens calibration (w3-06-08 ✓).
- **Store the prior at first touch** and **fix the candidate band** (recs 13, 14).
- **Closed-loop test of fix (c):** with `candidates()` and levers driving the policy, does (c) change what is taught?
- **Ranking by a lower confidence bound or by evidence count** for any teacher-facing ranking. It is more principled, but it needs a variance the model doesn't keep.

## Considered and rejected
- **`on_success_immediate = 1.0` as proposed.** It stalls students on their first parts (w1-06-07 ✓).
- **`on_success_scaled`** (half-life grows only by how much had decayed). In the pilot replay almost nothing reached secure: coverage 0% (far) and 1% (near) (`pilot_decay_sweep.md`). Too conservative under our truth model.
- **The `tuned` package as the headline.** It had the best calibration but fewer truly secure parts than current (−0.28 near, −0.47 far). Its fatigue gain mostly comes from the shims, not the threshold.
- **Lowering `fatigue_min_parts` to 1.** Pilot, at −0.25 / window 4: recall rose to 38% (40/105), but false alarms rose to 28.6% (180/630). The likelihood ratio stayed about 1.3 (`pilot_detector_sweep.md`).
- **Stuck rule B (3 misses on the same point).** 7% recall (pilot). Keep the built rule and fix the loop instead.
- **Fix (a) alone: start the clock on any evidence (wave 3).** It follows BKT-with-forgetting, but an untouched part still sits frozen at .30. So every attempted part now decays below every untouched one: a wrong-once part reads .019 after 3 days, against .30 untouched (`fix_cases.md`). Inversions fell only from 0.92 to 0.73 (near, floor 0) (w3-06-08 ✓).
- **Fix (b) alone as the ranking fix (wave 3).** It leaves the decayed part at 0, so the inversion rate is unchanged (0.92 → 0.92). We keep it as the display and honesty fix (rec 10), not as the ranking fix (w3-06-09 ~).
- **Decaying the prior itself, so untouched parts decay from enrolment (wave 3).** When prior knowledge started is unknown (left-censored). Any start date would be invented, and it would make rankings depend on sign-up date.
- **Leaning on spacing reviews to hide the asymmetry (wave 3).** The gap exceeds the 4.4-day crossover whenever the exam is more than about 30 days away, and full compliance barely changed far-scenario inversions (w3-06-02 ~, -04 ~).
- **Raising `levels.secure` to 0.85–0.95.** The scout reports that pilot exam-day false secure stayed at 71–73% while coverage fell. The false secures sit near p ≈ 1 because of half-life inflation, not near the threshold. This was **not verified, and the output was not saved**. The direction is consistent with the immediate-share data above.

## Panel objections this report answers or leaves open
- **Teacher #2 / #3 and student #3, "What stops a student picking the shortest option?": partly.** The sim's guesser always picks "A", not the shortest option. Open-answer evidence held it near 0 secure parts (w1-06-10 ~). A shortest-option guesser is still untested. The wave-3 option-form audit found the opposite cue: in 7 of 9 example-pack parts the correct option is longer than every distractor (w3-05-08 ~, [05](05-product-features.md)), so a longest-option guesser would do well.
- **Judges #3, "Why believe a 'secure' Verify?": open here.** That objection is about AI-literacy levels; this report covers course parts only. See [02](02-ai-literacy-assessment.md).
- **Judges (expected), "Can a student chat their way to secure?": recommended.** Yes, on `main`: 14 exchanges with no check reach .763 (w3-06-06 ~). Rec 10 caps never-right parts at the prior and shows "not yet shown". Not built.
- **"A diligent student ranks below one who never started" (teacher-view and credibility risk; w3-06-01 ✓): recommended.** Recs 9–10, not built. Across-student rankings are latent until a teacher view exists.
- Bugs 1–3 answer no panel objection directly. Their fixes are **recommended**, not built.

## Findings

| id | Claim | Strength | Population | Outcome | Mark |
|---|---|---|---|---|---|
| w1-06-01 | `p_known` hits exactly 1.0 after 44 correct checks, and the next exchange divides by zero (`learner.py:634-637`, `:457`). 11 (near) / 4 (far) saturations per run; 66 for the stuck type. | simulation (deterministic probe) | synthetic, example-mini | other (system reliability) | ✓ |
| w1-06-02 | Once stuck, every later plan is the same prerequisite check. Probe 12/14. Main-run streak 16–17 (stuck type), 6–7 typical (near only; 5.6–8.7 far). | simulation | synthetic, example-mini | engagement (plan behaviour) | ~ typical-type range holds for near only |
| w1-06-03 | "Quiz me on what's due" offers 0 of 2 due reviews (`service.py:246-247`). | simulation (deterministic probe) | synthetic, example-mini | other (feature behaviour) | ✓ (avoided if the chatbot passes due `node_ids`) |
| w1-06-04 | Far, exam day: 76% → 55% of "secure" parts are truly below 0.5 (−20.6 ± 5.8, 96 pairs). Overconfidence 0.37 → 0.26. | simulation | synthetic, example-mini | prediction | ✓ (mean of per-run shares) |
| w1-06-05 | Truly secure parts at the end: +0.50 ± 0.18 (near), +0.80 ± 0.28 (far). | simulation | synthetic, example-mini | prediction (simulated mastery, not learning) | ✓ |
| w1-06-06 | Reviews due per morning in the last 14 days: 4.5 → 2.9 (−1.60 ± 0.18). | simulation | synthetic, example-mini | cost (load) | ✓ near scenario only |
| w1-06-07 | Emulated `on_success_immediate = 1.0`: 1.6 vs 6.2 parts model-secure; −3.07 ± 0.33 truly secure (near). 59–80% of evidence is "immediate". | simulation | synthetic, example-mini | prediction | ✓ (shim emulated, not built) |
| w1-06-08 | Built fatigue detector: recall 12% (13/105) vs false alarms 11.3% (71/630), LR ≈ 1.1. | simulation (pilot, 3 seeds, near) | synthetic, example-mini | prediction | ~ some grid settings reach LR 2.4–4.0 at tiny counts; pilot only |
| w1-06-09 | `tuned` (incl. threshold −0.35) cut flagged sessions 11% → 4% (−6.4 ± 1.2, near). | simulation | synthetic, example-mini | prediction | ✓ (confounded with shims: `proposal_shims` falls as much at −0.25) |
| w1-06-10 | Guesser hits 33–34% (near) / 32–33% (far) on 3-option checks; averages 0.06–0.12 parts model-secure. | simulation | synthetic, example-mini | prediction | ~ not "0 of 9"; far hit rate lower |
| w1-06-11 | About 23% of parts are truly below 0.5 when they first turn secure; no variant changes it (+1.2 ± 1.8). | simulation | synthetic, example-mini | prediction | ✓ |
| w1-06-12 | The stuck rule finds the true stuck part in 99%. False flags: pilot typical 8%, slow 30%, tired 30%; main near 10/23/37%, far 17/47/43%; guesser 100%. | simulation | synthetic, example-mini | prediction | ~ the scout's figures were pilot only |
| w3-06-01 | Right once: .646, below "new" after 2.8 d, below untouched after 4.4 d, below wrong-once (.149, frozen) after 8.5 d; CCC 23.6 / 39.8 d | simulation (deterministic, real code) | synthetic, example-mini | prediction (model state) | ✓ (rerun byte-identical) |
| w3-06-02 | Review gap exceeds the 4.4-day crossover at 150 / 90 / 61 / 45 / 30 days out (37.5 … 4.5 d) | simulation (deterministic) | synthetic | prediction | ~ the gap stays under the crossover for any exam under about 29.5 days away, not "only within 14 days" |
| w3-06-03 | Never-right above right-at-least-once in 0.82–1.00 of pairs at day 30 (within student 0.84–1.00) | simulation | 960 synthetic students | prediction (ranking) | ✓ (days-since bins pool all snapshots) |
| w3-06-04 | Truth-supported inversions 0.00–0.05; truth-contradicted 0.51–0.61; compliance barely helps | simulation | synthetic | prediction | ~ those ranges hold from day 14/30; at day 7 they are .07–.08 and .38–.40 |
| w3-06-05 | Six right answers on `ped_values` lift never-answered `ped_formula` to .527 for good; no prerequisite check offered | simulation (deterministic) + code | synthetic | prediction | ✓ |
| w3-06-06 | 14 talk-only exchanges take a part to .763 (secure), frozen | simulation (deterministic) | synthetic | prediction | ~ .788 is after a 15th exchange; an untested review is queued, due immediately |
| w3-06-07 | `p_now` feeds levels, rollups, levers, weak prerequisites, the prereq gate, support level, known parts, intuition source; not `due_reviews`; `candidates()` unused | official document (code) | n/a | policy (code behaviour) | ✓ |
| w3-06-08 | Fix (c): day-30 inversions 0.82–1.00 → 0.03–0.26; AUC 0.48–0.59 → 0.62–0.71; levels changed 5–11%; Brier 0.028 → 0.078 (floor 0), 0.061 → 0.050 (floor 0.3) | simulation | synthetic | prediction | ✓ |
| w3-06-09 | Fix (b): ranking almost unchanged; never-right shown developing+ 0.8–2.2% → 0; stored state unchanged | simulation | synthetic | prediction (levels shown) | ~ within 0.003 except one within-student cell (.004) |
| w3-06-10 | Live state = two rebuilds in 5,760 / 5,760 student × variant runs | simulation | synthetic | policy (determinism) | ✓ |
| w3-06-11 | Censoring analogy; two-state chain relaxes to μ/(λ+μ), so `main` holds two equilibria | theory / analogy | n/a | n/a (model design) | ✓ (frozen value is the prior only for untouched parts) |

## How to rerun

Run from the worktree root. Full commands, output files and the run status are in [`sims/README.md`](sims/README.md).

```bash
PY=/home/vishnu/edux26/.venv/bin/python
export PYTHONPATH=/home/vishnu/edux26-research
S=docs/research/overnight/sims
$PY $S/probes.py                                   # the three bugs: prints a FOUND line for each
rm -f $S/results/runs.jsonl                        # run_sims.py appends
$PY $S/run_sims.py --seeds 20 --workers 7          # main run, ~50 min (1,120 runs) -> results/runs.jsonl
$PY $S/summarise.py                                # summary.md, metrics.csv, SVGs
$PY $S/sweep_detectors.py --scenario near          # needs the run databases still in /tmp
$PY $S/sweep_decay.py
$PY $S/sensitivity.py --seeds 6 --run              # not yet run (~15 min)
```

After bugs 1–3 are fixed, `probes.py` should print no FOUND line (probe 1 then reports "next exchange ok"; probes 2 and 3 print "ok"). That makes it a cheap regression check before filming.

**Wave 3 (decay asymmetry).** Scripts, results and their README are in [`sims/decay/`](sims/decay/README.md).

```bash
PY=/home/vishnu/edux26/.venv/bin/python
export PYTHONPATH=/home/vishnu/edux26-research
D=docs/research/overnight/sims/decay
$PY $D/cases.py; $PY $D/fix_cases.py            # results/cases.md, results/fix_cases.md
$PY $D/population.py --seeds 60 --workers 7     # 960 students x 6 variants
gunzip -k $D/results/population.jsonl.gz         # analyse.py reads the uncompressed file
$PY $D/analyse.py                               # results/population.md
```
