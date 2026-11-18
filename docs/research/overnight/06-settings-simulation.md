# 06 · Settings simulation: three bugs, the proposal's settings, and what the alarms catch

Wave 1 (overnight 17–18 Nov 2026). Sources: scout notes `work/w1/w1-06.md`, blind verifier marks `work/w1/verify-I.json` (w1-06-*), the panel files, and the simulation outputs in `sims/results/`. The verifier reran the probes and recomputed every number from `results/metrics.csv`. A partial rerun (seeds 1–2, all variants, both scenarios, 42 runs) reproduced the stored rows exactly.

**Every result here is simulation: synthetic students, example pack.** The course is `coursepacks/example-mini` (9 parts). The students' memory and behaviour parameters are **our choice** (`sims/README.md`). The outcomes are prediction accuracy (does the model's "secure" match the simulated truth), load counts and code behaviour. **None of them is a learning gain**, and none is evidence about real 16–18-year-olds.

**How to read the numbers.** "± SD" is the spread over seeds in the tables. "± 95% CI" is for paired differences: the same student type and seed under two settings variants. The main run finished 920 of 1,120 planned runs. That is 16–17 seeds per cell: near 17 seeds (one type 16), far 16. The header of `summary.md` says "17 seeds per cell", which is wrong (it counts distinct seeds overall). Anything marked **pilot** comes from 3 seeds (1–3) in the near scenario only.

## Summary
- **Three bugs found by driving the real code. All are small Wednesday fixes.** (1) `p_known` reaches exactly 1.0, and the next exchange crashes `tutor_turn` with a divide-by-zero (w1-06-01 ✓). This could crash a live demo. (2) Once a part is flagged stuck, every later plan in the session is the same prerequisite check (w1-06-02 ~). (3) "Quiz me on what's due" teaches the old focus instead of the due reviews (w1-06-03 ✓).
- **"Secure" goes stale.** Far scenario (study 150–90 days before the exam, then stop), current settings: on exam day, on average 76% of the parts the model calls secure are truly below 0.5 mastery (w1-06-04 ✓).
- **The proposal's settings that the code already reads are a net win in the sim.** Exam-day false secure (far) falls by 21 points (−20.6 ± 5.8 CI). Truly secure parts at the end rise by +0.5 (near) and +0.8 (far) of 9. Reviews due per morning in the last 14 days fall from 4.5 to 2.9 (near) (w1-06-04 ✓, -05 ✓, -06 ✓).
- **Don't ship `on_success_immediate = 1.0`.** Emulated, it leaves 1.6 of 9 parts model-secure at the end (current 6.2) and 3.1 fewer truly secure parts (near). The cause: 59–80% of evidence counts as "immediate", so the half-life never grows (w1-06-07 ✓).
- **The built fatigue detector barely separates tired from non-tired sessions** (pilot): 12% of the tired student's sessions flagged, against 11% of other students' sessions. Likelihood ratio about 1.1 (w1-06-08 ~).
- **The stuck detector finds the truly stuck part in 99% of sessions, but it also raises false flags.** These are common for slow and tired students, especially in the far scenario (main run: up to 43–47% of their sessions). Each false flag starts the bug-2 loop (w1-06-12 ~).
- **Gaming.** The always-"A" guesser hits 32–34% on 3-option checks, not the 0.25 the model assumes. It still averaged only 0.06–0.12 parts model-secure, because open answers hold it down (w1-06-10 ~). The offloader is the bigger risk: far scenario, exam day, its parts are rated +0.73 (proposal) to +0.87 (current) above truth (`summary.md`).
- **For the pitch, show two bars together:** "secure but not known on exam day" (76% → 55%) and "parts truly secure" (3.9 → 4.7), both far scenario. A false-secure bar on its own misleads.

## The three bugs (rank first: Wednesday fixes)

All three reproduce deterministically with `sims/probes.py`, on the real code path with no sim clamp. The verifier confirmed the line numbers.

| # | Bug | Where (file:line) | Effect | One-line fix idea | Finding |
|---|---|---|---|---|---|
| 1 | **Divide-by-zero crash.** The BKT update plus the learn step `p += (1 − p) × learn_rate` has no upper clamp, so `p_known` reaches exactly 1.0 in floating point. `apply_exchange` then computes `odds = p / (1 − p)`. | `edux/learner.py:634-637` (update, saved at `:650`); `edux/learner.py:457` (the division) | Probe: 44 correct `mcq_check` answers 2 minutes apart on one part, then the next ordinary exchange raises `ZeroDivisionError` and `tutor_turn` fails. Main run, current settings: 11 saturations per run (near), 4 (far), and 66 for the stuck student (near). Without the sim clamp, each of these would have crashed the next exchange on that part. | Clamp `p_known` to [0.001, 0.999] after the update in `_apply_evidence` and again in `apply_exchange`. | w1-06-01 ✓ |
| 2 | **Step-back loop.** The plan returns the prerequisite check whenever the session is "stuck" and the focus is the stuck part. `stuck_parts` is recomputed over the whole session's evidence, so the flag never clears. An answer keeps `last["focus"]`, so the focus stays on the stuck part. | `edux/plan.py:332-337`, with `edux/learner.py:785-822` (`stuck_parts`) and `edux/service.py:243-244` (focus carried over) | Probe: 12 of 14 consecutive plans were the same prerequisite check, answered right every time. Main run: the longest streak per session is 16–17 for the stuck student, and 6–7 for the typical student in the near scenario (5.6–8.7 in far). | Step back once per stuck part per session. After a correct prerequisite answer, reteach the whole part through its anchor, or offer another part. | w1-06-02 ~ (typical-student streak of 6–7 is near only) |
| 3 | **"Quiz me on what's due" misses the reviews.** A message that resolves to no parts falls back to `last["focus"]`, with no session or time check. So the `reviews_only` branch, whose code comment says it is for "quiz me on what's due", is never reached. | `edux/service.py:246-247`, with `edux/plan.py:343-348` (the unreachable branch) | Probe: 2 parts due, asked 5 days after studying another part. The plan teaches the old part and offers 0 of the 2 reviews. A chatbot that passes the due parts' `node_ids` avoids the bug, but the `review_due` prompt doesn't send them. | Don't inherit `last["focus"]` when the message has no parts and is a review cue, or when the last turn was in an earlier session. Or have the `review_due` prompt send a flag. | w1-06-03 ✓ |

Bug 1 is reachable in one session, and bug 2 makes it more likely: the stuck student, who keeps answering the same prerequisite check right, hit 66 saturations per run (w1-06-01 ✓). Without the sim clamp, any of these could crash a live demo. Fix both before filming.

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | Clamp `p_known` to [0.001, 0.999] (bug 1). Add a test: 50 correct checks on one part, then one more exchange, with no exception. | build | S | yes | w1-06-01 ✓ |
| 2 | Break the step-back loop: one prerequisite check per stuck part per session, then reteach or switch (bug 2). | build | S | yes | w1-06-02 ~, w1-06-12 ~ |
| 3 | Make "Quiz me on what's due" reach the reviews (bug 3). This is needed before any spacing claim in the pitch or video. | build | S | yes | w1-06-03 ✓ |
| 4 | Adopt the proposal's settings that the code already reads: `share_far = 0.10`, `share_mid = 0.19`, `share_near = 0.30`, and guess 0.20 for `explain_back`, `past_question`, `link` and `extend`. | settings | S | yes | w1-06-04 ✓, -05 ✓, -06 ✓ |
| 5 | **Don't ship `on_success_immediate = 1.0`.** If the rule is built, use about 1.5 (our choice), or apply it only to MCQ checks straight after `teach_point`, not to explain-backs. Better: shorten `evidence.immediate_window_minutes` (now 30) and choose the value by replay. | settings, build | S (setting), M (code) | setting yes; code no | w1-06-07 ✓ |
| 6 | Show staleness on "secure" in `get_my_progress`: "secure, last checked N days ago". Or show "developing" when the last correct answer is more than about 30 days old (our choice). | build, demo | S | yes | w1-06-04 ✓ |
| 7 | Raise `session.fatigue_threshold` from −0.25 to −0.35 (our choice). Treat `offer_stop` as an offer only. Consider `fatigue_slip_add = 0` until a better detector exists, because a false alarm silently discounts real errors. | settings | S | yes | w1-06-08 ~ (pilot); w1-06-09 ✓ (confounded, see below) |
| 8 | Pitch slide: "eduX tested its own alarms" (chart below). Always caption it "simulation: synthetic students, example pack". | pitch, video | S | yes | w1-06-04 ✓, -05 ✓ |

**Evidence for rank 7.** The only clean test of the threshold alone is the pilot replay. On the same logs, moving from −0.25 to −0.35 cut false alarms on other students' sessions from 11.3% (71/630) to 5.9% (37/630). Recall on tired sessions fell from 12% (13/105) to 10% (10/105) (`pilot_detector_sweep.md`).

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

## Later (not before Thursday; for the business plan and Q&A)
- **Require a correct check in a later session before showing "secure".** This targets the 23% of parts that are truly weak when they first turn secure (w1-06-11 ✓). Code change, M.
- **Prototype the "errors on known material" fatigue rule.** Test it on held-out logs (seeds ≥ 4 of the main run), not the pilot seeds. M.
- **Choose `immediate_window_minutes` by replay** with `sweep_decay.py`.
- **Run `sensitivity.py`** to check whether the far-scenario gap survives `stability_growth_massed = 2.0`.
- **Build `mcq_guess_from_options`** (guess = max(1/n, immediate)) and keep explain-back gating (w1-06-10 ~). It barely matters until the immediate window shrinks.
- **Replace the truth model with values fitted to real pilot logs** (slip, guess, learn rate).

## Considered and rejected
- **`on_success_immediate = 1.0` as proposed.** It stalls students on their first parts (w1-06-07 ✓).
- **`on_success_scaled`** (half-life grows only by how much had decayed). In the pilot replay almost nothing reached secure: coverage 0% (far) and 1% (near) (`pilot_decay_sweep.md`). Too conservative under our truth model.
- **The `tuned` package as the headline.** It had the best calibration but fewer truly secure parts than current (−0.28 near, −0.47 far). Its fatigue gain mostly comes from the shims, not the threshold.
- **Lowering `fatigue_min_parts` to 1.** Pilot, at −0.25 / window 4: recall rose to 38% (40/105), but false alarms rose to 28.6% (180/630). The likelihood ratio stayed about 1.3 (`pilot_detector_sweep.md`).
- **Stuck rule B (3 misses on the same point).** 7% recall (pilot). Keep the built rule and fix the loop instead.
- **Raising `levels.secure` to 0.85–0.95.** The scout reports that pilot exam-day false secure stayed at 71–73% while coverage fell. The false secures sit near p ≈ 1 because of half-life inflation, not near the threshold. This was **not verified, and the output was not saved**. The direction is consistent with the immediate-share data above.

## Panel objections this report answers or leaves open
- **Teacher #2 / #3 and student #3, "What stops a student picking the shortest option?": partly.** The sim's guesser always picks "A", not the shortest option. Open-answer evidence held it near 0 secure parts (w1-06-10 ~). A shortest-option guesser and an option-form audit are still needed (see w1-07 and w1-04).
- **Judges #3, "Why believe a 'secure' Verify?": open here.** That objection is about AI-literacy levels; this report covers course parts only. See [02](02-ai-literacy-assessment.md).
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
