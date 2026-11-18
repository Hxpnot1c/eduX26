# Step 05o: Fixes to reply-style (#38, #39)

Branch `build/fix-reply-style`, from `main`. Follow-up to step [05j](05j-reply-style.md) (PR #40, merged).

## What
1. **#38: confirm the built choices, with one change.**
   - **Which steps shrink:** confirmed as built.
   - **A shorter `answer_length` always wins.** `teach_point`'s `max_words` becomes the student's length when it is below `points.max_words` (80).
   - **A longer `answer_length` raises `teach_point`'s `max_words` only up to `points.max_words_requested` (120),** so it stays one point per message. Other steps take the student's length as before.
   - The test that "no step carries a smaller `max_words`" is updated: `teach_point` may carry min(their length, 120).
   - Fatigue shrinking follows whatever "fatigued" means once step [05s](05s-fatigue-time-on-task.md) lands. There's no change here.
2. **#39: confirm as built.**
   - The cue goes on the first step per diagram part.
   - The three example-pack diagram parts stay as flagged.
   - The Leutner & Biele citation is already checked and in `reference/research.md`.

## Why, with sources
- **One point per message:** meaningful, learner-paced segments improve retention and transfer (Rey et al., 2019). A request for more detail shouldn't turn one point into several.
- 120 is a judgement call. It equals `style.max_words`, the default reply ceiling.

## Files
- `edux/service.py`: `reply_style`, `teach_point` under `answer_length`.
- `settings.toml`: `points.max_words_requested`.
- `scripts/check_mcp.py`: the `reply_style` run, with `answer_length` of 50 (teach_point 50) and of 200 (teach_point 120).
- `tests/test_reply_style.py`: 50 gives 50, 100 gives 100, 200 gives 120, and the setting is at least `points.max_words`.
- `edux/settings.py`: `Points.max_words_requested`, checked to be at least `points.max_words`.
- **Docs:** this file; `docs/build/steps/05j-reply-style.md` (a note pointing here); `reference/settings.md`; `reference/research.md` (the "One point per message" row already names 120).

## Settings
```toml
[points]
max_words_requested = 120   # judgement call, starting value: a longer answer_length raises teach_point only to this
```

## Commits
1. `fix(service): cap teach_point at 120 words under a longer answer_length`
2. `chore(scripts): check teach_point under short and long answer lengths`
3. `docs(reference): label points.max_words_requested`

## Done when
- With `answer_length` 50, `teach_point` carries 50. With 200, it carries 120.
- Issues #38 and #39 are closed with a one-line comment.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (unchanged).

## Tests
In `scripts/check_mcp.py` (`reply_style`), as listed under Files.
