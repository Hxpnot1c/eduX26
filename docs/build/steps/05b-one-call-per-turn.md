# Step 05b: One call per turn, timing, length and formatting

**Branch:** `build/05b-one-call-per-turn`
**Read first:** `docs/build/README.md`, `reference/design-for-change.md`, `reference/tools-and-context.md`, `edux/server.py`, `edux/service.py`, `edux/context_blocks.py`

## Why: what the first claude.ai test showed
- **Slow.** The first message took 23 s (including claude.ai loading the tools) and the second took 10 s. Most of that was the chatbot writing a ~400-word reply and making two tool calls. Our server time is small (about 2 ms to apply an exchange and about 20 ms to build context on example-mini), but nothing measures it in production.
- **Too long, wrong order.** `get_learning_context` returns about ten blocks, each with its own "do this" text and no order between them. The chatbot used all of them: worked example, misconception, confusable, notes caveats and exam relevance. It also offered "try first / hint / show me" at the end, after already showing everything, and skipped the prerequisite check.
- **The answer arrives a turn late.** A student's answer (e.g. to a pre-question) is in their next message, but it only reaches the server through `log_exchange` after the chatbot has already asked for context. That context still says "ask the pre-question". On top of that, the update goes to a background queue nothing waits for.
- **Scores are guessed.** The chatbot invents a 0–1 score, so different models will score the same answer differently.
- **Leaky and confusing details:**
  - `p_now` numbers are shown to the chatbot.
  - `active_misconceptions` includes ones the student doesn't hold.
  - The worked-example text says "use the student's interests" but the interests are never sent, so claude.ai filled the gap from its own memory.
  - Formulas came out as plain text.
  - The access log prints student keys.

## What changes, in one line each
1. **Timing log** for every tool call, with keys removed from all logs.
2. **One tool, `tutor_turn`, called at the start of each reply.** It carries the labels for the student's message and their answer, if any. The server applies them immediately, then returns a 1–2 step plan.
3. **The chatbot ticks the mark points the student hit; the server computes the score.**
4. **A default reply length, plus profile interests,** sent with every turn.
5. **Per-chatbot formatting notes:** LaTeX, currency, diagrams.
6. **Tidy-ups:** levels only (no `p_now`), held vs watch-for misconceptions, short texts.

Every number goes in `settings.toml` and all wording in `text/`. Bump `protocol` to `v0.2`, because labels now describe the student's message and scores come from points.

---

## A. Timing log
- Migration `005_call_log.sql` adds `call_log(id, ts, student_id, tool, ms REAL, result_chars INTEGER, ok INTEGER, error TEXT)`. It's operational, not an event: rebuild ignores it.
- Wrap every tool adapter in `server.py` to time it, write a `call_log` row, and print one console line: `tutor_turn demo-weak 18ms 3.1k chars ok`. Never print the key.
- Turn off uvicorn's access log, or add a filter that strips the query string, so keys never reach any log.
- CLI `calls [--student] [--last N]`:
  - recent calls
  - median and 90th-percentile ms per tool
  - median gap between consecutive calls per student (roughly the chatbot's time per turn)

## B. `tutor_turn` replaces `get_learning_context` and `log_exchange`
The MCP tool list becomes `tutor_turn`, `get_my_progress` and `update_my_profile`. Fewer tools also load faster in clients. Keep `service.learning_context` for the CLI and debugging, but don't expose it as a tool. The trade-off: an answer in the student's very last message of a chat is never scored. That's accepted.

### Arguments
| arg | what it is |
|---|---|
| `message` | the student's message, word for word |
| `node_ids` | optional; ids from an earlier plan if the chatbot knows them |
| `this_message` | labels for the student's message: `question_depth` (surface/mechanism/transfer), `engagement` (passive/active/constructive), `choice` (try_first/hint/just_show_me/none) |
| `answer` | optional; only when the message answers something the chatbot asked last turn. Fields: `part_id`; `type` (prequestion/explain_back/review/extend/past_question); `correct` (bool, prequestion only); `picked_misconception_id` (prequestion only); `points_met` (ids from `score_next`); `misconception_ids` (others shown) |
| `client` | e.g. claude, chatgpt, gemini |

`offloading` is derived: `choice == just_show_me`. `support_given` and what was asked come from the **last plan the server issued** to this student. Store that in an operational table `issued_plan(student_id PK, ts, plan_json)`, so the chatbot doesn't have to repeat it.

### What the server does, in order
1. Validate. On a bad label or an unknown point id, return `{ok: false, error}` and record nothing.
2. **Compute the score:**
   - prequestion: 1 if `correct`, else 0
   - everything else: `len(points_met) / len(score points for that part)`
3. Record the exchange and evidence (`record_exchange`, with `support_given` taken from `issued_plan`). **Apply them now (`apply="now"`), not in the background.** The worker is no longer needed on this path.
4. Build the turn as today (`graph.resolve`, `order_parts`, the state), then choose the plan (below).
5. Save the plan to `issued_plan` and return the response.

### Choosing the plan: at most 2 steps, first match wins for step 1
Each step is `{move, part_id, text, data}`. `text` comes from `text/moves/<move>.md`. Steps marked **(stop)** end the plan, because the student needs to reply.

1. **The student answered something** (`answer` given) → `feedback`.
   - prequestion: confirm, or name the picked misconception and its correction.
   - Otherwise:
     - all points met: say specifically what was good
     - else `reteach_gap`, with the missing points' wording only
2. **Fatigued** (session block) → `offer_stop` with `quick_parts` **(stop)**.
3. **Stuck** on the focus → `step_back` (to the weakest prerequisite) or `switch_approach` (anchor or different example).
4. **Focus ambiguous** → `ask_which` with the candidates **(stop)**.
5. **`choice == just_show_me`** → `show`: a short worked example. Nothing else this turn.
6. **Pre-question eligible** (existing rules) → `prequestion` **(stop)**.
7. **Weak prerequisite at level new,** not checked this session → `check_prereq`: one quick question on it **(stop)**.
8. **Held misconception** on the focus, not already handled in step 1 → `correct_misconception`.
9. **Otherwise teach at the support level:**
   - `worked_example`: a short example, then "try this one, or ask for a hint"
   - `hint`: per part type, as today
   - `explain_back`: ask them to explain it **(stop)**

   The try / hint / show-me choice is the **closing line** of the teaching step, never offered after showing everything.
10. **Step 2,** only if step 1 isn't a stop step: `extend` if eligible, otherwise one `review` (in its mode), otherwise nothing.

### Response
```json
{
  "ok": true,
  "plan": [{"move": "feedback", "part_id": "...", "text": "...", "data": {...}},
           {"move": "teach", "part_id": "...", "text": "...", "data": {"level": "worked_example"}}],
  "score_next": {"<part_id>": [{"id": "ped_formula_p1", "point": "..."}, ...]},
  "style": {"max_words": 120, "interests": "football", "format": "..."},
  "reference": {"notes": [...], "anchor": {...}, "confusables": [...], "causal": [...], "exam_relevance": {...}},
  "focus": [{"id": "...", "name": "...", "level": "new"}]
}
```
- **`score_next`** lists the points to score the student's *next* answer against, for parts in steps that ask something. Points are the part's `mark_point` ids. If a part has no mark points, use its notes' key points with ids `<note_id>:k<n>`.
- **`reference`** is background. The move texts say to use it only when it helps the current step. The context profile still decides which reference blocks are included, and `minimal` stays as the comparison profile (notes only, no plan).
- The old blocks become inputs to the plan and to `reference`. `teaching_note` is dropped from the output.

## C. Length and personalisation
- `settings.toml`:
  ```toml
  [style]
  max_words = 120   # default reply length; profile answer_length overrides
  ```
- **`style.max_words`:** the profile's `answer_length`, otherwise the setting.
- **`style.interests`:** from the profile.
- `text/style.md`, sent once in the server instructions:
  - keep each reply under `max_words` unless the student asks for more
  - use `interests` for examples; if empty, use what you already know about the student if it's appropriate, otherwise a neutral everyday example
  - mention that the notes don't cover something only when the student asks beyond them

## D. Formatting per chatbot
- `text/format/claude.md`, `chatgpt.md`, `gemini.md` and `default.md`, picked by `client` and returned in `style.format`. Keep each under about 80 words.
  - **claude:**
    - formulas in LaTeX with `$$…$$`
    - write money as £5, or escape dollars as `\$`, because `$` starts maths
    - for `diagram` parts, or when the student asks, draw the diagram inline (as an SVG visual) with labelled axes, curves, the shift and P1→P2 / Q1→Q2; never ASCII art
  - **chatgpt:** LaTeX with `\(…\)` and `\[…\]`. For diagrams, draw a labelled chart with Python when available, otherwise describe it.
  - **gemini:** LaTeX with `$…$`. Diagrams described in words.
  - **default:** plain text, formulas in words, diagrams described in words.
- Draw only when the part type is `diagram` or the student asks, because drawing is slow.

## E. Tidy-ups
- Chatbot-facing output carries levels only, never `p_now` (the CLI keeps the numbers).
- Misconceptions are split into `held` (correct these) and `watch_for` (only raise them if the student shows them).
- Rewrite `text/server_instructions.md` to at most 8 short lines:
  1. call `tutor_turn` at the start of every reply about the course
  2. do the plan's steps in order and nothing else
  3. label the student's message honestly
  4. tick only the points the student actually produced
  5. use `reference` only when it helps
  6. follow `style`
  7. never give a numeric mark for level-marked questions
  8. never claim to be a teacher
- One `text/moves/<move>.md` per move. Each is at most 3 sentences, reusing the existing support and session wording where it fits. Remove texts no longer used.
- Update `text/chatbot_setup.md`: "Call tutor_turn at the start of every reply about my course."

## Docs and scripts
- `reference/tools-and-context.md`: the new tool, the plan rules, the response and the score-by-points rule.
- `reference/settings.md`: `[style]`, `protocol = v0.2`.
- `reference/database.md`: migration 005 and `issued_plan`.
- `steps/05b-one-call-per-turn.md` (this file), added to the README steps table.
- `scripts/check_mcp.py` for the new tool list, with a scripted three-message run (below).
- `README.md` and `docs/demo-script.md` for the new flow.

## Commits (one logical change each, no attribution)
1. `docs: plan one call per turn`
2. `feat(server): log tool call timing and keep keys out of logs`
3. `feat(learner): score answers from mark points met`
4. `feat(context): choose a short ordered plan for each turn`
5. `feat(server): replace context and logging tools with tutor_turn`
6. `feat(context): add reply length, interests and per-client formatting`
7. `refactor(context): send levels only and split held and watch-for misconceptions`
8. `docs(text): rewrite instructions and move texts`
9. `chore(scripts): update MCP check for tutor_turn`
10. `docs: update README, demo script and references`

## Done when (by hand, no tests yet)
- `scripts/check_mcp.py` passes, and runs this conversation as demo-secure on example-mini:
  1. "How do I calculate PED?" → plan is a single `prequestion` (stop).
  2. A wrong answer picking `ped_formula_m1` → plan is `feedback` (naming m1) then `teach`. **No second pre-question.** State shows m1 active and the prequestion evidence recorded.
  3. An explanation with 1 of 2 points met → plan is `reteach_gap` with only the missing point. The recorded score is 0.5.
- `rebuild` gives identical state.
- `calls` shows `tutor_turn` server time under 100 ms on example-mini.
- No key appears in any console output or log.
- `p_now` doesn't appear anywhere in `tutor_turn` output.
- **claude.ai check (Vishnu runs it):**
  - one tool call per message
  - the second message's reply is about 150 words or fewer
  - the try / hint / show-me line comes at the end of a teaching step, not after everything is shown
  - the PED formula renders as LaTeX

  Note the time for the first and second message.
