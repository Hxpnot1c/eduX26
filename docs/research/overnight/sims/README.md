# eduX synthetic-student simulations (overnight research w1-06)

These scripts drive synthetic students through the **real** eduX code: `edux.service.tutor_turn` calls `edux.learner`. The course content is the `coursepacks/example-mini` pack (9 parts). Each run uses a throwaway data folder under `/tmp/claude-1000/w1-06/` and a simulated clock. Each synthetic student has a hidden true state, so the model's beliefs can be scored against the truth.

**The results apply only to the example-mini pack and these synthetic students.** They test how the rules behave when the assumptions below hold. They are not evidence about real students.

## Safety

- Nothing here edits `settings.toml`, `edux/` or any other repo file. A settings variant is built in memory (settings.toml plus an overlay), and in each process the cached accessors `learner._settings`, `service._settings` and `graph._settings` are swapped for it.
- Every database lives under `/tmp/claude-1000/w1-06/`. The repo's `data/` folder is never touched.

## Files

| file | what it does |
|---|---|
| `edux_sim.py` | Harness: settings variants and shims, the truth model (`TRUTH_PARAMS`, all our choice), and the closed loop through `tutor_turn` |
| `run_sims.py` | Runs the closed loop over seeds × student types × scenarios × variants, in parallel, appending to `results/runs.jsonl` |
| `summarise.py` | Writes `results/metrics.csv` (one row per run), `results/summary.md` (mean ± SD, paired differences) and SVG charts |
| `sweep_detectors.py` | Open-loop replay: rebuilds each recorded log under a grid of fatigue settings plus alternative fatigue and stuck rules, and scores them against the truth (`results/detector_sweep.md`) |
| `sweep_decay.py` | Open-loop replay of scoring and decay rules (immediate window, half-life growth, MCQ guess), scored on exam day (`results/decay_sweep.md`), with a staleness split |
| `sensitivity.py` | Re-runs current vs proposal under other truth-model memory assumptions (`results/sensitivity/sensitivity.md`) |
| `probes.py` | Three deterministic probes of behaviours found in the simulations, run on the real code path (no clamp) |

Not part of w1-06: `literacy/` (AI-literacy scoring sim, w2-02, own README), `teacher/` (misconception-alarm sim, w2-05t), and `capture_demo.py` with `demo-captures/` (demo storyboard captures, w1-07).

## Run status (what is in `results/`)

- **Main closed-loop run: partial.** 920 of the planned 1,120 runs finished (seeds 1–17) before wrap-up. Near: 118 runs per variant (17 seeds, one student type 16). Far: 112 runs per variant (16 seeds). So it is **16–17 seeds per cell**. The header of `results/summary.md` says "17 seeds per cell"; `summarise.py` counts distinct seeds across all rows, not seeds per cell; the true figure is 16–17.
- The main run's raw log is `/tmp/claude-1000/w1-06/main_ok.jsonl` (920 rows); it was not copied into `results/`, so `results/runs.jsonl` does not exist. `summary.md`, `metrics.csv`, `false_secure.svg` and `review_load.svg` come from it.
- **Detector and decay sweeps: pilot only.** `results/pilot_detector_sweep.md` and `results/pilot_decay_sweep.md` come from a 3-seed pilot (seeds 1–3, near scenario for the detectors). The re-sweep on the main-run logs was stopped at wrap-up, so `detector_sweep.md` and `decay_sweep.md` (the names the scripts write) are not in `results/`.
- **`sensitivity.py` was not run.** `results/sensitivity/` does not exist.
- The pilot used seeds 1–3, which are also the first seeds of the main run, so those logs are not held out. A held-out test of pilot-chosen parameters must use seeds 4 and up.

## Rerun

Run from the worktree root:

```bash
PY=/home/vishnu/edux26/.venv/bin/python
export PYTHONPATH=/home/vishnu/edux26-research
S=docs/research/overnight/sims
rm -f $S/results/runs.jsonl
$PY $S/run_sims.py --seeds 20 --workers 7                 # ~50 min on 7 cores (1,120 runs)
$PY $S/summarise.py                                       # summary.md, metrics.csv, *.svg
$PY $S/sweep_detectors.py --scenario near                 # detector_sweep.md (rebuilds the run databases)
$PY $S/sweep_decay.py                                     # decay_sweep.md
$PY $S/sensitivity.py --seeds 6 --run                     # sensitivity/sensitivity.md (~15 min)
$PY $S/probes.py                                          # three lines; FOUND marks a bug still present
```

`run_sims.py` defaults to `--seeds 30`; the command above asks for 20. It appends to `results/runs.jsonl`, so delete that file first (as above) or pass `--out` to a fresh folder. The sweeps rebuild the databases the main run wrote in `/tmp`, so run them after it finishes and before `/tmp` is cleared; pass `--runs` if the log is not `results/runs.jsonl`. They write `detector_sweep.md` and `decay_sweep.md`; the files now in `results/` are the renamed pilot outputs. The pilot (3 seeds) was used to choose the alternative-rule parameters. Seeds 1–3 are shared with the main run, so a fair test of those parameters uses only main-run seeds 4 and up; that re-sweep has not been done.

## Settings variants

| variant | what it is |
|---|---|
| `current` | `settings.toml` as is |
| `proposal` | `settings.toml` plus every key from `docs/research/settings-proposal.toml` that the code reads today: open-answer guess 0.20 (explain_back, past_question, link, extend) and scheduling shares 0.10 / 0.19 / 0.30 |
| `proposal_shims` | `proposal` plus two proposal rules the code doesn't have yet, emulated here ("shim, not built"): `on_success_immediate = 1.0` and `mcq_guess_from_options` |
| `tuned` | `proposal` plus `on_success_immediate = 1.5` (shim), `mcq_guess_from_options` (shim) and `session.fatigue_threshold = -0.35`. A candidate, chosen from the pilot (our choice) |

Proposal keys that can't be patched cleanly, because no code reads them: `validate_degeneracy`, `on_success_scaled` (emulated only in `sweep_decay.py`), `review_when_below`, `one_review_per_part_per_session`, `transfer_requires_correct`, `min_evidence_for_fade`, `fade_requires`, `target_low`/`target_high`, `prequestion.max_options`, the style keys, and the `[feedback]`, `[confidence]`, `[engagement]`, `[show]`, `[relevance]` and `[personalisation]` sections. `summary.md` lists them for each run.

**Sim-only clamp (all variants).** BKT can push `p_known` to exactly 1.0. The next ordinary exchange then divides by zero, and `tutor_turn` would crash (`probes.py` #1). To keep the runs going, the harness clamps `p_known` at 1 − 1e-9 and counts each clamp (the `clamps` column).

## Truth model: every number is OUR CHOICE

| parameter | value |
|---|---|
| P(learn a point when it is taught) | typical 0.35, slow 0.15, fast 0.60, guesser 0.10, offloader 0.35, tired 0.35, stuck 0.35 (0 on `ped_formula`) |
| "just show me" show / feedback after a wrong answer | teach at 0.4× / 0.5× the learn rate |
| slip | 0.10. The tired student's slip is 0.45 from session minute 30, and their learning halves |
| memory | recall = exp(−days / S). New point S = 4 days. Correct retrieval ≥ 12 h after the last one: S × 2; within 12 h: S × 1.1 |
| MCQ | knows and recalls the point: picks the correct option (minus slip); otherwise a uniform guess over the options shown. The guesser always picks "A" |
| open answers | each recalled point is ticked (× 0.8 for extend); an unknown point is ticked 5% of the time (generous chatbot labelling) |
| offloader | says "just show me" to start every part and instead of half of its checks; surface/passive labels |
| behaviour | 1.0–2.5 min per turn; 45-min sessions; at the start of each session works 2 due parts (by naming them), then the first part the model doesn't call secure, in pack order (cap of 12 turns per part per session); carries on after `offer_stop` |
| scenarios | near: from 35 days before the exam (2027-06-08), a session every day. far: from 150 days before, a session every 3 days for 60 days, then none until the exam |
| truth labels | false secure = model `p_now ≥ 0.75` while true mastery < 0.5. Truly secure = mastery ≥ 0.75 |

Known simplifications:
- Prerequisites don't gate true learning (`ped_values` can be learnt without `ped_formula`).
- Reviews happen only because the simulated student names due parts. In normal plans, reviews rarely surface (see `probes.py` #2), so the review results flatter eduX.
- The simulated student leaves a part after 12 turns on it per thread (`turns_per_part_cap`). The step-back streak can carry across threads in one session (that is how it reaches 16–17), but the cap still cuts the loop off, so the reported streak is a lower bound on what a student who stays on the part would see.
