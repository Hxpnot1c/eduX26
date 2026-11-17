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
8. A question asked instead of an answer is answered briefly, then the pending question is asked again.
9. The chatbot corrects its own mistakes in one line and flags them.
10. Each step lists the course terms the student knows, and the chatbot doesn't introduce others.
11. Fewer moves: `feedback` absorbs `correct_misconception`, and `reteach` absorbs `reteach_gap` and `switch_approach`, so feedback and re-teaching share one text each. The final move set, through 05e, is fixed before building (K).
12. `style.max_words` counts the explanation only; MCQ options don't count.

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
- **Move keys.** A move's key is the move plus its variant: `_<level>` for `teach` (e.g. `teach_worked_example`) and `_<mode>` for `review` (e.g. `review_transfer`); from 05d, `_<purpose>` for `ask_mcq`. The section text, cue file and `[moves.<key>]` table are looked up by the full key first, then the bare move. So `ask_mcq` (05d) has one section and a cue per purpose.
- Each `text/moves/<move>.md` is cut to **at most 2 sentences**. A test at startup warns when one is longer.
- **The whole server instructions are capped at `instructions.max_words` (900 words),** counting `server_instructions.md`, `style.md` and every move section. Over the cap is a startup error that names the longest sections. The final 14 moves (K) are budgeted at about 510 words of sections, about 800 in all.
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
[moves.feedback]              # includes a held misconception (was correct_misconception)
reference = ["misconceptions"]
[moves.reteach]               # missing points, or the whole part through the anchor when stuck
reference = ["notes", "anchor"]
[moves.show]
reference = ["notes"]
[moves.teach]                # all teach levels
reference = ["notes", "misconceptions"]
[moves.extend]
reference = ["causal"]
[moves.answer_brief]
reference = ["notes"]
[moves.review_transfer]
reference = ["notes"]
# prequestion, check_prereq, step_back, review_recall, reask, offer_stop, ask_which: none
```

- `misconceptions` here means the held misconceptions for the step's part, in full (wrong idea and correction).
- **Watch-for misconceptions** go with every move that asks the student something, so the chatbot can tag a misconception the answer shows. They are sent as `id` and `wrong_idea` only, with no correction, for the step's part. The moves are listed in `context.toml`:
  ```toml
  [watch_for]                # moves that ask the student something also get the part's watch-for misconceptions (step 05c)
  moves = ["prequestion", "check_prereq", "step_back", "teach_explain_back", "review", "extend"]
  ```
  A bare move (`review`) covers its variants, as with the reference tables.
- `notes` is limited to the step's part.
- **`exam_relevance`** is added only when the message mentions an exam, or a command word used in that part's questions. The cue words are a list in `settings.toml` (`blocks.exam_cues`), like `causal_cues`.
- The reference sent is the union over the plan's steps, in step order and then list order. The profile still decides which blocks exist at all: a block missing from the profile is never sent.
- A move with no table gets no reference.

## E. Short point ids
- `score_next` labels each part's points `a`, `b`, `c`… in order (mark-point order, or note key-point order in the fallback).
- A letter means the point at that position in the part's ordered points, so the server works it out from the course content. No mapping is saved, and an answer still scores after `issued_plan` is lost (for example, after `seed-demo --reset`).
- `answer.points_met` accepts letters, full point ids, or a mix. Both are translated to point ids before scoring, so scores are computed as before.
- Only an id or letter that doesn't belong to the answer's part is a validation error, and then nothing is recorded.

## F. Result budget
```toml
[results]
max_chars = 2400   # about 600 tokens
```
- `plan`, `score_next`, `focus` and `style` are never cut.
- When the result is over budget, reference blocks are dropped one at a time, from the end of the priority order in D, until it fits. Watch-for misconceptions are dropped last, after every other reference block.
- If it is still over budget with no reference left, it is sent as is, with a warning:
  - migration `007_call_log_budget.sql` adds `over_budget INTEGER NOT NULL DEFAULT 0` to `call_log`;
  - the console line ends with `OVER BUDGET`, e.g. `tutor_turn demo-weak 18ms 2.9k chars ok OVER BUDGET`.
- `calls` shows the median and largest `result_chars` per tool, and how many calls were over budget.

## G. Tool description
`text/tools/tutor_turn.md` is cut to at most 8 lines. The detail it held moves to the server instructions, which are sent once.

## H. Questions aren't answers
- When the student asks something instead of answering what they were asked, the chatbot doesn't send `answer`.
- The question last asked is kept in `issued_plan.plan_json` as `pending` (the asking step: move, part and data) until it is answered.
- **A message with no `answer` while a question is pending,** on the same part or with no new focus → `answer_brief` (answer their question in a few lines), then `reask` **(stop)**: the same pending question, word for word, with the same `score_next`.
- A message about a different part, or a research question, drops `pending` and is planned as usual.
- Fatigue and stuck rules still come first.

## I. Self-correction
- When the chatbot finds a mistake in something it said earlier, it says so in one line, gives the correction, and carries on.
- It sets `this_message.conflict_flagged = true`, a new label stored on the exchange's existing `conflict_flagged` column.
- One line in `text/server_instructions.md` says this.

## J. Known terms
- Every step that teaches or asks gets `data.terms`: the names and aliases of the focus part, and of parts the student has at developing or above.
  - Order: the focus part, then known parts linked to it by an edge, then other known parts by importance, up to `limits.terms` in `context.toml`.
- `text/server_instructions.md`: don't introduce course terms that aren't in `terms`; when one is needed, explain it in plain words instead.

## K. The move set
Moves that do the same job share one move and one text, and `data` says what differs. The final set, through 05e, is listed with each move's word budget in `reference/tools-and-context.md` ("The move set"):

| move | from | absorbs |
|---|---|---|
| `ask_mcq` (purpose `intuition` / `check` / `prereq` / `review`) | 05d | `prequestion`, `check_prereq`, `step_back`, `review_recall`, `review_transfer` |
| `teach_point` | 05d | the `teach_<level>` hint and worked-example texts |
| `show`, `extend`, `offer_stop`, `ask_which` | 05b | |
| `explain_back` | 05d rename | `teach_explain_back` |
| `feedback` | 05b | `correct_misconception` (this step) |
| `reteach` | this step | `reteach_gap`, `switch_approach` (this step), `reteach_point` (05d) |
| `answer_brief`, `reask` | this step | `literacy_followup` (05e) goes into `reask` |
| `answer_with_sources`, `literacy_task`, `source_conflict` | 05e | |

This step builds sections and cues for the interim 17 moves (listed in the reference), and does the merges that don't need server-built MCQs:
- **`feedback`** is the only move that names misconceptions: picked, shown in the answer, or held on the focus (the old `correct_misconception` main step becomes `feedback` with `data.misconceptions`). One line for the verdict, one line per misconception with its correction.
- **`reteach`** re-teaches only `data.missing` (after a partial answer), or the whole part through `data.anchor` or a different example (when stuck with no prerequisite). It never names misconceptions, ends by asking them to try again, and is a stop step.
- A partial answer now gets `feedback` then `reteach` (two steps), instead of one `reteach_gap` step that did both.

## L. Reply length counts the explanation only
`text/style.md`: `style.max_words` limits the explanation; MCQ options don't count. The same wording goes on `points.max_words` in 05d.

## Docs and scripts
- First commit of this step: the docs for the changes above, including the final move set, the 900-word cap and the 05d changes to the intuition question and the merged `ask_mcq`.
- `reference/tools-and-context.md`: cues, style only when needed, reference per move, letter ids and the budget.
- `reference/settings.md`: `[results]`, `[instructions]`, `blocks.exam_cues`, the `[moves.<key>]` tables, `[watch_for]` and `limits.terms`.
- `text/moves/answer_brief.md`, `reask.md` and `reteach.md`, each with a `.cue.md`. `correct_misconception.md`, `reteach_gap.md` and `switch_approach.md` are removed.
- `reference/database.md`: migration 007.
- `scripts/check_mcp.py`: the three-message run sends letters, and prints each result's size.

## Commits (one logical change each, no attribution)
1. `docs: plan the final move set and a 900-word instructions cap`
2. `fix(text): fill placeholders in move texts`
3. `refactor(context): share feedback and reteach moves`
4. `refactor(server): send move instructions once and short cues per turn`
5. `feat(context): send style only when it changes`
6. `feat(context): include reference blocks per move`
7. `feat(server): label score points with short letters`
8. `feat(server): enforce a result budget and log overruns`
9. `feat(context): answer a question asked instead of an answer, then re-ask`
10. `feat(server): flag the chatbot's own corrections`
11. `feat(context): list the course terms the student knows`

## Done when (by hand, no tests yet)
- The three-message run from 05b still behaves the same, with the merged moves: pre-question, then feedback naming m1 and a teach step, then `feedback` and `reteach` with only the missing point and a recorded score of 0.5.
- The median `tutor_turn` result on example-mini is at most 2,400 characters, and none in the run is over budget.
- No placeholder text (`{…}` or `` `name` ``) appears in any result or in the server instructions.
- The second call in a session has no `style`.
- Every step that asks the student something carries the part's watch-for misconceptions as `id` and `wrong_idea` only.
- An answer with full point ids, with letters, or with no saved plan scores the same; an id from another part is rejected.
- The server instructions are at most 900 words, with sections for the 17 interim moves only.
- No result names `correct_misconception`, `reteach_gap` or `switch_approach`.
- A question asked instead of an answer gets `answer_brief` then `reask` with the same question, and nothing is scored.
- `conflict_flagged = true` is stored on the exchange.
- `data.terms` on a teaching step for a new student holds only the focus part's names.
- `calls` shows result sizes and the over-budget count.
- `rebuild` gives identical state.
