# Step 08: Unit tests

Branch `build/08-tests`, from `main` once the decision records (#44) are merged.

## What
The first unit tests. Until now the only check was `scripts/check_mcp.py`, which needs a running server and runs end to end. These tests run in under a second with no server and cover the pieces every later change relies on.

## Why
Several audit findings need a test to prove the fix and to stop it breaking again (record 0002, C19): the exchange nudge, the result budget, and the retention and erasure commands. The handover's gate also names two checks (tool results within 2,400 characters, instructions within the word cap) that should be one command.

## Files
- `tests/conftest.py`: fixtures. `course` loads `coursepacks/example-mini` into a throwaway data folder (`EDUX_DATA_DIR` set per test) and points the learner model at it. `student` creates a student. `part` picks the most important part.
- `tests/test_settings.py`: `settings.toml` loads; guess + slip < 1 for every evidence type; a bad pair is refused.
- `tests/test_learner_model.py`: the prior for an unseen part; a right answer raises and a wrong one lowers `p_known`; one open answer cannot reach "secure"; the 0.001 to 0.999 clamp; forgetting halves recall per half-life; level thresholds; **rebuild reproduces the state**.
- `tests/test_budgets.py`: the server instructions are within `instructions.max_words` and the spare words are printed; `fit_budget` drops reference blocks from the end and never the plan.
- `tests/test_soak.py` and `scripts/soak_turns.py` (19 Nov): a seeded random walk of `tutor_turn` calls (all answer types, random labels, find-the-error and the confidence question on, a clock that advances seconds to 90 minutes a turn). It checks no crash, every result within `results.max_chars`, no server-only `item` reaching the chatbot, and rebuild identical. Run by hand with more turns (`python scripts/soak_turns.py --turns 500 --seed N`); seeds 1 to 9 at 500 turns were clean. **Known limit:** event times have one-second resolution, so two turns inside the same second can replay in a different order (a pre-question's weight counts exchanges up to its time). A real chat turn takes longer, so the soak does not generate this; it is not fixed.
- `pyproject.toml`: a `dev` extra with pytest, and the test path.

## Run
```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

## Done when
- All tests pass on a clean checkout.
- `pytest` prints the instruction word count (`-s` shows it).
- `scripts/check_mcp.py` is unchanged and still passes.

## Not in this step
CI (GitHub Actions), the MCP round-trip tests and the tricky-message set. They stay in [Later](later.md).
