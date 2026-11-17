# Step 05c: Lean results

**Branch:** `build/05c-lean-results`
**Read first:** `docs/build/README.md`, `reference/tools-and-context.md`, `reference/settings.md`, `edux/server.py`, `edux/plan.py`, `edux/context_blocks.py`, `text/`

## Why
- **Results pile up.** Every `tutor_turn` result stays in the chat, and the chatbot re-reads all of them on every later message.
- **No help from the client.** claude.ai summarises a long chat only near its limit, only on paid plans with code execution, and the summary is lossy. Quality drops as the chat grows well before that point.
- **Results are already large.** On example-mini, a 05b result is about 815 tokens. A real pack's will be bigger.
- **Long arguments are slow.** The chatbot spends time writing out its arguments, so long point ids cost speed.
- **A bug.** The `check_prereq` text contains a literal `` `name` `` placeholder that is never filled in.

## What changes, in one line each
1. Placeholders in move texts are filled from the step's `data`.
2. Move instructions go in the server instructions, once per chat. Each step carries a one-line cue.
3. `style` is sent only when it's needed.
4. Each move pulls in only the reference blocks it uses.
5. Score points get short letter ids per turn.
6. A result budget, with overruns logged.
7. A shorter `tutor_turn` description.

Every number goes in `settings.toml` and all wording goes in `text/`.

---

## A. Fill placeholders
- Move texts may contain `{field}` placeholders, filled from the step's `data` (e.g. `{name}` from the prerequisite's name).
- A placeholder with no matching field is a startup error for texts that are always used with that field, and a warning otherwise. No `{…}` or backticked placeholder reaches output.
- Check every move text for the same problem, and fix `check_prereq.md` (`` `name` `` becomes `{name}`).

## B. Move instructions once, cues per turn
- **Server instructions** are built at startup from:
  - `text/server_instructions.md`
  - `text/style.md`
  - one short section per move text: `## <key>`, then the text of `text/moves/<key>.md`
- **Move keys.** A move's key is its text file's name: the move, plus `_<level>` for `teach` (e.g. `teach_worked_example`) and `_<mode>` for `review` (e.g. `review_transfer`). The cue files and the `[moves.<key>]` tables in D use the same keys. A table for the bare move (`[moves.teach]`) applies to all its variants unless a variant has its own.
- Each `text/moves/<move>.md` is cut to **at most 2 sentences**. A test at startup warns when one is longer.
- **Each plan step** carries only `move`, `part_id`, `data` and `cue`.
  - `cue` is one line of at most 15 words from `text/moves/<key>.cue.md`, so the move is still clear in a long chat where the instructions are far back.
  - The full move text is no longer sent per step.
- `text/server_instructions.md` gains a line: "Each plan step names a move; do what that move's section below says, using the step's `data`."

## C. Style only when it's needed
`style` is included only when:
- this is the first `tutor_turn` of a session (a session as in 04c: a gap longer than `session.gap_minutes` starts a new one), or
- `client`, `interests` or `max_words` differ from the last style sent.

Otherwise it is left out. The style last sent is kept in `issued_plan.plan_json` as `style_sent`, so nothing new is stored in state, and rebuild is unaffected.

## D. Reference only what the moves need
A new table per move key in `context.toml` lists the reference blocks that move uses, in priority order:

```toml
[moves.feedback]
reference = ["misconceptions"]
[moves.reteach_gap]
reference = ["notes"]
[moves.prequestion]
reference = []
[moves.check_prereq]
reference = []
[moves.correct_misconception]
reference = ["misconceptions"]
[moves.switch_approach]
reference = ["anchor", "confusables"]
[moves.show]
reference = ["notes", "misconceptions"]
[moves.teach]                # all teach levels
reference = ["notes", "misconceptions"]
[moves.extend]
reference = ["causal"]
[moves.review_recall]
reference = []
[moves.review_transfer]
reference = ["notes"]
# offer_stop, step_back, ask_which: none
```

- `misconceptions` here means only the held misconceptions for the step's part. `watch_for` is no longer sent.
- `notes` is limited to the step's part.
- **`exam_relevance`** is added only when the message mentions an exam, or a command word used in that part's questions. The cue words are a list in `settings.toml` (`blocks.exam_cues`), like `causal_cues`.
- The reference sent is the union over the plan's steps, in step order and then list order. The profile still decides which blocks exist at all: a block missing from the profile is never sent.
- A move with no table gets no reference.

## E. Short point ids
- `score_next` labels each part's points `a`, `b`, `c`… in order (mark-point order, or note key-point order in the fallback).
- The server keeps the mapping in `issued_plan.plan_json` (`point_ids: {part_id: {"a": "<full id>", …}}`).
- `answer.points_met` takes the letters. The server translates them back to point ids before scoring, so scores are computed as before. An unknown letter is a validation error, as an unknown id was.
- An answer arriving with no saved mapping (for example, after `seed-demo --reset`) is rejected with a clear error, and nothing is recorded.

## F. Result budget
```toml
[results]
max_chars = 2400   # about 600 tokens
```
- `plan`, `score_next`, `focus` and `style` are never cut.
- When the result is over budget, reference blocks are dropped one at a time, from the end of the priority order in D, until it fits.
- If it is still over budget with no reference left, it is sent as is, with a warning:
  - migration `007_call_log_budget.sql` adds `over_budget INTEGER NOT NULL DEFAULT 0` to `call_log`;
  - the console line ends with `OVER BUDGET`, e.g. `tutor_turn demo-weak 18ms 2.9k chars ok OVER BUDGET`.
- `calls` shows the median and largest `result_chars` per tool, and how many calls were over budget.

## G. Tool description
`text/tools/tutor_turn.md` is cut to at most 8 lines. The detail it held moves to the server instructions, which are sent once.

## Docs and scripts
- `reference/tools-and-context.md`: cues, style only when needed, reference per move, letter ids and the budget.
- `reference/settings.md`: `[results]`, `blocks.exam_cues` and the `[moves.<move>]` tables.
- `reference/database.md`: migration 007.
- `scripts/check_mcp.py`: the three-message run sends letters, and prints each result's size.

## Commits (one logical change each, no attribution)
1. `fix(text): fill placeholders in move texts`
2. `refactor(server): send move instructions once and short cues per turn`
3. `feat(context): send style only when it changes`
4. `feat(context): include reference blocks per move`
5. `feat(server): label score points with short letters`
6. `feat(server): enforce a result budget and log overruns`

## Done when (by hand, no tests yet)
- The three-message run from 05b still behaves the same: pre-question, then feedback naming m1 and a teach step, then `reteach_gap` with only the missing point and a recorded score of 0.5.
- The median `tutor_turn` result on example-mini is at most 2,400 characters, and none in the run is over budget.
- No placeholder text (`{…}` or `` `name` ``) appears in any result or in the server instructions.
- The second call in a session has no `style`.
- `calls` shows result sizes and the over-budget count.
- `rebuild` gives identical state.
