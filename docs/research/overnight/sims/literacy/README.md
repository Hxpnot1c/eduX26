# AI-literacy scoring simulation (overnight research w2-02)

Synthetic students with a known AI-literacy skill go through the step 05e literacy flow for 10 weeks. We measure how often the levels are wrong, and search the settings for a combination that keeps no-skill students from being shown "secure". Notes and findings are in `../../work/w2/w2-02.md`.

**The results are only as good as the truth model.** Every number in `TRUTH` (in `lit_model.py`) is our choice, not evidence. The students are synthetic. The results show how the scoring rules behave under these assumptions, not how real students behave.

## What runs

- **The flow.** `lit_model.run_student` emulates `service.tutor_turn` turn by turn for literacy:
  - `plan.literacy_task` sets Ask below `ask_min_features` labelled features, otherwise Verify. At secure there is a task only every `secure_every` research questions.
  - `service._literacy_followup` re-asks a pending task, makes it wait behind course questions (`max_waits`), scores it 0 after `max_followups`, and drops it unscored when the session ends.
  - `_how_ai_works` runs a check per trigger, with `how_secure_every` at secure.
  - `smoke_tutor_turn.py` runs four scripted sessions through the real `tutor_turn` and confirms the same evidence rows (`results/smoke_tutor_turn.json`).
- **The learner model.** There are two backends:
  - `RealBackend` is the 05e branch's own `edux.learner` (export at `/tmp/claude-1000/edux-05e`, read-only), on a throwaway `EDUX_DATA_DIR`, with settings swapped in memory.
  - `FastBackend` is a pure-Python replica used for the grid.
  - `validate.py` runs both on the same students, including the proposal. Results: 17,500 weekly values compared (5 students × 5 groups × 2 noise levels × 5 settings variants), max |diff| 3e-16, 0 mismatched students (`results/validate.json`). An earlier run with 8 students per cell compared 22,400 values with the same result.
- **Literacy-only trick.** The students produce literacy evidence only, so the global `bkt.prior`, `bkt.learn_rate`, `bkt.correct_share` and `decay.base_half_life_days` act as literacy-only settings in the sim. In the product they need new `[literacy]` keys, which is a code change.
  - A Verify-only threshold (`verify_share`) is emulated in `RealBackend` by passing 1.0 or 0.0. This is exact for the BKT update.
  - "Ignored = missing" means the zero row is not written.

## Truth model in one paragraph (all our choice)

- **Groups.** Five groups:
  - none;
  - partial (sits at the threshold);
  - strong;
  - improver (none for weeks 1–4, then strong);
  - gamer (no checking skill, but has learnt the ritual: asks for sources by habit, restates the reply as a "check", and often says "I checked" unprompted).
- **Moments.** 2 or 3 research questions a week (wave-1 estimate). Each is followed by 0–6 more turns in the session.
- **Ask.** Each question feature is shown with a per-group probability.
- **Verify.** Ticks come with per-group probabilities. A no-skill student who answers gets "opened" and "matched" ticks about half the time.
- **Ignoring.** Tasks are ignored at 30% for everyone (mcar), or 50/30/15% for none/partial/strong (mnar).
- **Label noise.** Each feature or tick label is flipped with probability e (symmetric), or wrongly ticked at e and wrongly missed at e/3 (lenient). In addition, the chatbot reports a false "unprompted check" in e/4 of sessions.
- **How AI works.** A how-AI-works trigger comes in a week with p = 0.6 (at most one a week, our choice). A no-skill student picks the right letter with p = 0.40, because the cue wording makes it test-wise.

## Files

| file | what it does |
|---|---|
| `lit_model.py` | Truth model, behaviour scripts (common random numbers per seed), noise, the 05e literacy flow, both backends |
| `validate.py` | FastBackend vs RealBackend on the same students → `results/validate.json` |
| `smoke_tutor_turn.py` | Four scripted sessions through the real `service.tutor_turn` → `results/smoke_tutor_turn.json` |
| `grid.py` | Metrics per settings variant. `baseline` (branch + one change at a time, run at N = 500) → `results/baseline.json`. `search` → `results/grid.jsonl`: a decomposed grid of 3,480 configs, N = 100 per group per cell, cells = {10%, 20% symmetric noise} × {mcar, mnar}. Verify's settings vary with Ask's guess fixed, and Ask's guess varies with Verify's settings at the branch values. |
| `rank.py` | Applies the selection rule → `results/ranked.md`, `results/best.json` |
| `how_sweep.py` | How AI works: trigger rate × half-life × guess × ignored rule → `results/how_sweep.md` |
| `final.py` | Branch, wave-1 quick fixes, two settable-now variants (no code change) and the proposal, over every noise and ignore cell including the lenient stress test, N = 1000 → `results/final.md`, `results/final.json`. The proposal is `results/chosen.json` |
| `moment_rates.py` | Share of moments scored correct, by group and noise → `results/moment_rates.md` |

## Rerun

```bash
PY=/home/vishnu/edux26/.venv/bin/python
cd docs/research/overnight/sims/literacy
mkdir -p /tmp/claude-1000/w2-02/base
(cd /tmp/claude-1000/edux-05e && EDUX_DATA_DIR=/tmp/claude-1000/w2-02/base PYTHONPATH=. $PY -m edux.cli load coursepacks/example-mini)
PYTHONPATH=/tmp/claude-1000/edux-05e:. $PY validate.py 8          # ~1 min
PYTHONPATH=/tmp/claude-1000/edux-05e:. $PY smoke_tutor_turn.py
$PY grid.py search 100                                            # ~20-40 min on 8 cores
$PY rank.py
$PY grid.py baseline 500
$PY how_sweep.py
$PY final.py 1000
$PY moment_rates.py
```
