# Step 05v: Cap the exchange nudge

Branch `build/fix-exchange-nudge`, from `main` once step 08 (#45) is merged.

## What
An ordinary exchange nudges a part's odds by the chatbot's `question_depth` and `engagement` labels (`transfer` ×1.1, `constructive` ×1.05). Add `nudges.ceiling` (0.40, never above `levels.new`): the nudge can raise a part towards the ceiling and no further. It never lowers a part, and it leaves a part alone once evidence has lifted it past the ceiling. `protocol` becomes `v0.3`.

## Why
Without a cap, about 14 to 20 labelled messages reached "secure" with no answer tested, and the labels come from the student's own chatbot, unchecked. Talk is not evidence. The reasoning and sources are in [decision 0003](../../decisions/0003-cap-the-exchange-nudge.md).

## Files
- `settings.toml`: `[nudges] ceiling`, and `protocol = "v0.3"`.
- `edux/settings.py`: `Nudges.ceiling`; `load_settings` refuses a ceiling outside `0 < ceiling <= levels.new`.
- `edux/learner.py`: `apply_exchange` applies the ceiling.
- `tests/test_exchange_nudge.py`.
- `docs/build/reference/settings.md`, `docs/build/reference/learner-model.md` (§2).
- `docs/decisions/0003-cap-the-exchange-nudge.md`, and the row for C1 in `0002`.

## Done when
- `pytest` passes, including 80 deep exchanges staying at or below the ceiling.
- `scripts/check_mcp.py` passes; rebuild gives identical state.
- The three demo students' levels per part are identical to `main` after `seed-demo --reset`.
- No migration is needed.

## Notes
Product call: levels shown to students can change for any part that talk alone had pushed past 0.40. The demo is unaffected. Decision owner: Vishnu.
