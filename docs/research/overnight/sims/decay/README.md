# Decay-clock asymmetry on economics parts (overnight research w3-06)

**Question.** On `main`, `p_now` decays only once a part has a clock, and the clock starts only on a right answer (`edux/learner.py`: `p_now` returns `p_known` when `since is None`; `_apply_evidence` sets `clock_start` only when `correct`, or restarts a clock that is already running). Does this rank economics parts or students wrongly, and which fix keeps BKT's meaning and rebuild determinism?

The scripts drive the **real** learner code on the `coursepacks/example-mini` pack (9 parts). Each uses a throwaway `EDUX_DATA_DIR` under `/tmp/claude-1000/w3-06/`. Fixes are in-memory monkeypatches (`population.install`). No repo file is edited. Settings are `settings.toml` as is (`edux_sim.use_settings("current")`).

**Every simulated-student number is our choice.** The results describe these rules on this pack. They are not evidence about real students.

## Files

| file | what it does | output |
|---|---|---|
| `cases.py` | First-principles students on one part (untouched, wrong once, right once, and so on), through the real code. Covers crossing times, the review gap against the crossing time, propagation onto a never-right prerequisite, exchange nudges with no check, and untouched priors against the candidate band | `results/cases.md` |
| `fix_cases.py` | The same students under each fix | `results/fix_cases.md` |
| `population.py` | Synthetic students study a random 60% of the parts with prerequisite checks, checks after teaching and spaced reviews (from `due_reviews`). The event log is generated live under `current`, then replayed under each fix and read at the same snapshot times. Determinism: live state vs `rebuild_state` twice | `results/population.jsonl.gz` (gzipped, 2.x MB; uncompressed copy at `/tmp/claude-1000/w3-06/population.jsonl`; `analyse.py` reads the uncompressed file, so `gunzip -k` first) |
| `analyse.py` | Pairwise inversions (never-right vs right-at-least-once), across students and within a student, split by truth. Also AUC, Brier, level changes, prerequisite-gate flips and false secure | `results/population.md` |

## Fixes tested

| variant | change | stored state changes? |
|---|---|---|
| `current` | `main` as is | no |
| `a_clock_any` | (a) A wrong answer before any right one also starts the clock (one line in `_apply_evidence`) | yes (`clock_start`) |
| `b_cap_prior` | (b) Read-time cap: a part never answered right reads at most its prior. The display would say "not yet shown" (counted post hoc; `level()` only sees `p`) | no |
| `c_to_prior` | (c) Decay towards the part's prior instead of 0: `p = prior + (p_known − prior)·0.5^(d/h)`, used at read time and inside updates (as `p_now` is today) | yes (later posteriors) |
| `ac` | (a) + (c) | yes |
| `bc` | (b) + (c) | yes |

## Truth model (our choice)

There is one memory trace per part, with recall = floor + (1 − floor)·exp(−d/S). S starts at 4 days; a right retrieval multiplies it by 2 (12 h or more after the last) or by 1.1 (massed). Two truth regimes are run: floor 0 (forgetting to nothing, like the model) and floor 0.3 (savings: some memory remains).

| parameter | value |
|---|---|
| learn chance when taught | typical .35, slow .15, fast .60, guesser .10 |
| slip | .10 |
| MCQ guess | 1 in 4 |
| coverage | 60% of parts per student |
| sessions | every 1, 2, 3 or 7 days |
| parts per session | 2 new parts |
| review compliance | 0, .5 or 1 |
| scenarios | near (35 days to the exam) and far (148 days to the exam, 60 days of study) |

## Rerun

```bash
PY=/home/vishnu/edux26/.venv/bin/python; export PYTHONPATH=/home/vishnu/edux26-research
D=docs/research/overnight/sims/decay
$PY $D/cases.py; $PY $D/fix_cases.py
$PY $D/population.py --seeds 60 --workers 7     # 960 students x 6 variants
$PY $D/analyse.py                               # reads results/population.jsonl (gunzip -k the .gz first)
```

## Limits

- The study policy reads only due dates, not `p_now`. So this is an open-loop comparison of the fixes on identical event logs. It doesn't show how a fix would change what the tutor asks next. `learner.candidates()` is not called by live code, so candidate ordering is reported from first principles only.
- The pack has 9 parts. A real course has many more untouched parts.
- Exchanges are labelled mechanism/active, so they carry no nudge. The nudge-only path is shown in `cases.py`.
