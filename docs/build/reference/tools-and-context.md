# Tools and context

The MCP server is a thin layer. `edux/server.py` registers tools and prompts and converts arguments. All logic is in `edux/service.py`, which calls:
- `edux/graph.py` (content lookups)
- `edux/learner.py` (state and scoring)
- `edux/context_blocks.py` (the blocks a turn is built from)
- `edux/plan.py` (the plan chosen from them)

Descriptions, instructions and move texts are read from `text/`.

**Principle: the chatbot labels and ticks, the server scores and plans.** The server never calls an LLM. The chatbot sends structured labels and the ids of the points a student produced. The server applies fixed rules from `settings.toml` and returns a short plan.

## Identity
Each student has a key. The connector URL is `https://<host>/mcp?key=<key>`.
- The server reads the key from the request, looks up the student, and rejects unknown keys.
- The key is never passed as a tool argument.
- A request without a known key is refused with 401 before the MCP handshake, and each tool checks the key again.
- The key never reaches a log. uvicorn's access log is off, and the call log stores the student id.

## Call timing
Every tool adapter is wrapped to time it. Each call:
- writes a `call_log` row (see `database.md`);
- prints one console line, e.g. `tutor_turn demo-weak 18ms 3.1k chars ok`, ending in `OVER BUDGET` when the result was over `results.max_chars` (step 05c; the row's `over_budget` is 1).

`python -m edux.cli calls [--student] [--last N]` lists:
- recent calls;
- the median and 90th-percentile server time per tool;
- the median and largest result size per tool, and how many calls were over budget;
- the median gap between a student's consecutive calls (roughly the chatbot's time per turn).

## Tools

### tutor_turn(message, this_message, node_ids?, answer?, client?)
Called once, at the start of every reply about the course. It replaces `get_learning_context` and `log_exchange` (protocol `v0.2`).

| arg | what it is |
|---|---|
| `message` | the student's message, word for word |
| `this_message` | labels for the student's message: `question_depth` (`surface` / `mechanism` / `transfer`), `engagement` (`passive` / `active` / `constructive`), `choice` (`try_first` / `hint` / `just_show_me` / `skip_point` / `none`, default `none`; `skip_point` is "I know this", step 05d), `request_type` (`concept` / `research` / `homework` / `other`, step 05e), `question_features` (research only: any of `concept`, `context`, `asks_sources`, `asks_reasoning`), `source_conflict` (a link failed or didn't say what was claimed) |
| `node_ids` | optional: part ids from an earlier plan or focus |
| `answer` | optional: only when the message answers something asked last turn (see below) |
| `client` | e.g. `claude`, `chatgpt`, `gemini`; picks the formatting note |

`answer` fields:
- `part_id` and `type`: the asking step's `part_id` and `data.answer_type`. Types are `prequestion`, `explain_back`, `review`, `extend`, `past_question`, `point_check` (step 05d), `ail_task` and `ail_unprompted` (step 05e; `ail_unprompted` is sent without being asked, when the student reports checking a claim).
- `correct`: prequestion only.
- `picked_misconception_id`: prequestion only, when they picked a wrong option.
- `points_met`: the letters from `score_next` (step 05c). The server translates them back to point ids with the mapping saved in `issued_plan`.
- `misconception_ids`: other misconceptions the answer showed.

#### What the server does, in order
1. **Validate.** A bad label, part, answer type, point id or misconception returns `{ok: false, error}` and records nothing.
2. **Score the answer.** A prequestion scores 1 if `correct`, else 0, and its picked misconception is attached. Any other type scores `len(points_met) / len(score points for the part)`.
   - **Score points** are the part's mark points, with their `mark_point` ids.
   - If the part has none, its notes' key points are used, with ids `<note_id>:k<n>` (n from 1).
3. **Find the focus.**
   - `node_ids` if given;
   - else, with an answer, the previous turn's focus (so a prerequisite check or review leads back to the topic), or the answer's part if there was none;
   - else the message (`graph.resolve`);
   - a message that names nothing keeps the previous turn's focus.
4. **Record the exchange and any evidence, and apply them now** (`apply="now"`). On the exchange:
   - `offloading` is `choice == just_show_me`;
   - `choice_taken` is `choice`;
   - `support_given` comes from the last issued plan: a teach step's level, `worked_example` for `show`, otherwise `none`.

   No exchange is recorded when there is no focus part and no answer.
5. **Build the turn** (`order_parts`, the blocks in the student's profile), **choose the plan**, save it to `issued_plan` and return.

#### Choosing the plan
At most two steps. Each is `{move, part_id, cue, data}`. `cue` is one line from `text/moves/<key>.cue.md`, where the key is the move text's name (`teach_<level>`, `review_<mode>`, otherwise the move); what the move means is in the server instructions, sent once (step 05c). Steps that ask something carry `data.answer_type`. Steps marked **(stop)** end the plan, because the student needs to reply.

**With an answer,** the plan is a feedback step, then the main step:
- prequestion → `feedback`: confirm, or name the picked misconception with its correction, plus the correct idea.
- all points met → `feedback`, with the points they made.
- points missing → `reteach_gap` **(stop)**, with only the missing points' wording (and any misconceptions the answer showed). It re-teaches those and asks them to try again, and nothing else follows it. If they are fatigued or stuck, it becomes a `feedback` step naming what's missing, followed by `offer_stop`, `step_back` or `switch_approach`.

**The main step** is the first rule that matches:
1. Fatigued, and stopping not yet offered this session → `offer_stop` with `quick_parts` **(stop)**. If they carry on, teaching goes on.
2. Stuck on the focus part:
   - `step_back` to its weakest prerequisite **(stop)**;
   - or, when it has no prerequisite, `switch_approach` (through the anchor, or a different example).
3. Focus ambiguous → `ask_which` with the candidates **(stop)**. No focus at all (e.g. "quiz me on what's due") → the top due `review`, if any.
4. `choice == just_show_me` → `show`: a short worked example. Nothing else follows it.
5. Pre-question eligible → `prequestion` **(stop)**.
   - Eligible means the part has no evidence yet, its level is below `support.worked_example_below`, it has enough misconceptions and there was no "just show me" this session.
   - It is never asked twice: not on the turn its answer arrives, and not again when the last plan already asked it.
   - Options are the correct idea and misconception wrong ideas, in an order fixed per student and part.
6. A weak prerequisite at level new, not checked this session (no evidence on it this session, and not asked in the last plan) → `check_prereq`: one quick question on it **(stop)**.
7. A misconception held on the focus, not already corrected this session (by feedback or an earlier step; carried in `issued_plan`) → `correct_misconception`.
8. Otherwise → `teach` at the support level. The try / hint / show-me line closes the teaching step:
   - `worked_example`: a short example, then "try this one, or ask for a hint";
   - `hint`: a completion problem for `calculation` and `diagram` parts, otherwise an example and a guiding question;
   - `explain_back` **(stop)**: ask them to explain it.

**Without an answer,** when the main step isn't a stop step or `show`, a second step is added: `extend` if earned, otherwise the top due `review` (in its mode, `recall` or `transfer`), otherwise nothing.

**Point by point (step 05d).** Where the main step would be `teach` at `worked_example` or `hint`, the part is taught one point at a time, in mark-point order:
- `teach_point` **(stop)**: one point (`data`: `index`, `total`, `point`, `exemplar`, `check_hint`), as a heading `Point {index} of {total}: {short title}`, one or two sentences, one worked line, then one quick check question on that point only. At most `points.max_words` words. `support_given` is the part's support level.
- The answer (`point_check`, score 1 or 0) gets `feedback`, then the next `teach_point`, or, when wrong, `reteach_point` **(stop)**: a different way in, with the same check, at most `points.reteach_limit` times before moving on.
- `choice == skip_point` → `check_point` **(stop)**: the check question only.
- `choice == just_show_me` → `show` for the current point, with no check.
- After the last point → `explain_back` of the whole part **(stop)**, scored on all its points. A part already at `levels.secure` goes straight to it.
- Progress is kept per part in `issued_plan` (`points`). Moving to another part keeps that part's progress; coming back resumes where it stopped.

**Research questions (step 05e).** `request_type == research` gets:
1. `answer_with_sources`: a full answer, never withheld, with sources and links (`data.trusted_sources` for the message's topic first), the claims that need checking marked, and a plain statement when the chatbot has no web access.
2. `literacy_task`: line 1 is feedback on the skill, line 2 is one task to do now. The skill is Ask when the question shows fewer than `literacy.ask_min_features` features, otherwise Verify; the wording comes from `text/literacy/<skill>_<level>.md` for the skill's level. At secure, the task appears only every `literacy.secure_every` research turns, and other turns get the feedback line only. Skipped while fatigued.
- The task is saved as pending in `issued_plan` (`literacy`). If the next message doesn't do it, that message is answered as usual and `literacy_followup` re-asks the task in one line. After `literacy.max_followups`, the task is recorded as `ail_task` with score 0 and dropped.
- `source_conflict` puts a `source_conflict` step first: that's exactly what checking is for, and the claim is corrected.
- `concept` and `homework` follow the rules above and never get a literacy task. `other` gets an empty plan.

A profile with `plan = false` (`minimal`) gets no plan, but still gets `score_next` for its focus parts, so its answers are scored.

#### Response
```json
{
  "ok": true,
  "plan": [{"move": "feedback", "part_id": "ped_formula", "cue": "...", "data": {"type": "prequestion", "correct": false, "picked": {...}, "correct_idea": "..."}},
           {"move": "teach", "part_id": "ped_formula", "cue": "...", "data": {"level": "worked_example", "part_type": "calculation", "answer_type": "explain_back"}}],
  "score_next": {"ped_formula": [{"id": "a", "point": "Percentage change = change / original x 100"}, ...]},
  "style": {"max_words": 120, "interests": "football", "format": "..."},
  "reference": {"anchor": {...}, "confusables": [...], "misconceptions": {"held": [...], "watch_for": [...]}, "notes": {...}, "exam_relevance": {...}},
  "focus": [{"id": "ped_formula", "name": "PED: formula and calculation", "level": "new"}]
}
```
- `score_next`: for each part a step asks about (and an `offer_stop`'s quick parts), except a pre-question, which is answered by option: the points to tick in the student's next answer.
- `score_next` ids are letters, `a`, `b`, `c`… per part in point order (step 05c). A research turn's `score_next` always includes `ail_verify`'s ticks (step 05e).
- `style`, sent only on the first `tutor_turn` of a session or when `client`, `interests` or `max_words` changed since it was last sent (step 05c):
  - `max_words`: the profile's `answer_length`, else `style.max_words`.
  - `interests`: from the profile.
  - `format`: `text/format/<client>.md`, the first of `claude`, `chatgpt` or `gemini` contained in `client`, else `default`.
- `reference`: only the blocks the plan's moves use, from `[moves.<move>] reference` in `context.toml` (step 05c), and only those in the profile. Misconceptions are the held ones for the step's part only; `watch_for` is no longer sent. `exam_relevance` is added only when the message mentions an exam or a command word. Before 05c: the profile's blocks that are not plan inputs. Plan inputs are `focus`, `prequestion`, `support`, `session` and `reviews_due`; `teaching_note` is never sent. A block that is only `{"items": [...]}` is sent as the list. The move texts say to use reference only when it helps the current step.
- `candidates` appears when the focus is ambiguous, and `unknown_ids` when `node_ids` had unknown ids.
- **Budget:** a result over `results.max_chars` drops reference blocks from the end of the moves' priority order until it fits. `plan`, `score_next`, `focus` and `style` are never cut. If it is still over, it is sent and the call is logged as over budget.
- Levels only: `p_now` never appears in chatbot-facing output (the CLI keeps the numbers).

#### Blocks
Each block is data for the plan or for reference, without instructions:

| block | contents |
|---|---|
| focus | resolved parts with name, level and type; or `candidates` when ambiguous |
| prequestion | on an untaught, weak part: target, correct idea and misconception distractors |
| support | support level (`worked_example` / `hint` / `explain_back`) and `extend: true` when earned |
| session | only when fatigued (with `quick_parts`) or stuck (with `step_back_to`) |
| weak_prerequisites | prerequisites below secure |
| anchor | a secure analogous part with the edge note |
| confusables | parts to contrast |
| causal | what this part affects, and what affects it, with the edge notes |
| misconceptions | `held` (the student holds these: correct them) and `watch_for` (raise only if the student shows them) |
| notes | summaries, key points and key wording, in source-authority order, with source titles; plus mark points |
| exam_relevance | papers and marks that test these parts |
| reviews_due | up to N due parts, each with a `mode`: `recall` (weak) or `transfer` (a new context) |
| teaching_note | short paragraph, for the `context` CLI command only |

Unknown blocks in a profile are skipped with a warning. `python -m edux.cli context --student <id> --message "..."` prints a message's blocks, numbers included, without recording anything.

`prompt_text` is stored on the exchange only when `STORE_PROMPTS=1` (tutor_turn doesn't send it).

**Trade-off:** an answer in the student's very last message of a chat is never scored, because no later `tutor_turn` call carries it.

### get_my_progress(include_parts?)
For students. Levels only, never numbers.
- Tree with levels: topic → subtopic → concept, with parts when `include_parts` is true.
- Five biggest levers: highest `importance × (1 − p_now)`, i.e. important and weak.
- Weak links: confusable or causal pairs where one side is weak.
- Reviews due.
- AI-literacy trends, as directions over the last 14 days vs before: share of mechanism/transfer questions, share of constructive engagement, "just show me" rate.
- `ai_literacy` (step 05e): the level of `ail_ask` and `ail_verify`, and the share of research questions showing each question feature over the last `progress.trend_days` against before, as up, down or steady. These parts are left out of the tree and levers above.
- `study_pattern`: "your answers tend to drop after about N minutes" (median fatigue onset), when at least `session.pattern_min_sessions` sessions had one; otherwise `null`.

### update_my_profile(interests?, exam_date_override?, answer_length?)
Updates `student_profile`. `interests` and `answer_length` come back in every turn's `style`.

## Prompts
- `review_due`: "Quiz me on what's due."
- `check_me`: "Check my understanding of ___."

## Server instructions
`text/server_instructions.md`, with `text/style.md` appended, then one section per move (`## <move>` and `text/moves/<move>.md`, at most 2 sentences each; step 05c). The `tutor_turn` description is at most 8 lines. The numbered rules:
1. Call `tutor_turn` at the start of every reply about the course.
2. Do the plan's steps in order and nothing else.
3. Label the student's message honestly.
4. Tick only the points the student actually produced.
5. Use `reference` only when it helps.
6. Follow `style`.
7. Never give a numeric mark for a level-marked question.
8. Each plan step names a move: do what that move's section says, using the step's `data` (step 05c).
9. One point per message, ending in one question (step 05d).
10. Never claim to be a teacher. (Safeguarding is left to the chatbot's own guardrails.)

## Changes
- Adding a field to a tool's output is fine.
- Removing or renaming one needs a new tool name, or a `protocol` bump and a note in the PR.
  - Example: `v0.2` replaced `get_learning_context` and `log_exchange` with `tutor_turn`, made the labels describe the student's message, and moved scoring to points met.

## Later (not in the base)
- `start_check` / `submit_check`: past-question, find-the-error and link checks.
- A `check` table for issued checks; results go to `evidence_log` with origin `check`.

See `steps/later.md`.
