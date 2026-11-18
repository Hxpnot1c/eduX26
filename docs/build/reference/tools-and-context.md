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
Called once, at the start of every reply (from step 05e, research questions about the world too). It replaces `get_learning_context` and `log_exchange` (protocol `v0.2`).

| arg | what it is |
|---|---|
| `message` | the student's message, word for word |
| `this_message` | labels for the student's message: `question_depth` (`surface` / `mechanism` / `transfer`), `engagement` (`passive` / `active` / `constructive`), `choice` (`try_first` / `hint` / `just_show_me` / `skip_point` / `none`, default `none`; `skip_point` is "I know this", step 05d), `request_type` (`concept` / `research` / `homework` / `other`, step 05e), `question_features` (research only: any of `concept`, `context`, `asks_sources`, `asks_reasoning`), `source_conflict` (a link failed or didn't say what was claimed), `web_access` (research only: the chatbot can search the web in this chat), `asks_recent` (research only: about recent data or events), `pushback_changed` (the student challenged the last answer and the chatbot changed it), `conflict_flagged` (the chatbot corrected its own earlier mistake this turn, step 05c) |
| `node_ids` | optional: part ids from an earlier plan or focus |
| `answer` | optional: only when the message answers something asked last turn (see below). Not sent when the student asks something instead of answering |
| `client` | e.g. `claude`, `chatgpt`, `gemini`; picks the formatting note |

`answer` fields:
- `part_id` and `type`: the asking step's `part_id` and `data.answer_type`. Types are `prequestion` and `review` (until 05d), `mcq` (any `ask_mcq`, step 05d), `explain_back`, `extend`, `past_question`, `ail_task` and `ail_unprompted` (step 05e; `ail_unprompted` is sent without being asked, when the student reports checking a claim).
- `correct`: prequestion only.
- `picked_misconception_id`: prequestion only, when they picked a wrong option.
- `choice`: the letter picked, for `mcq` (step 05d). The server scores it from the letter → option map stored in `issued_plan`, and activates the picked misconception. If the map is missing, nothing is recorded and the plan re-asks the same question with freshly shuffled options. After a `reask`, the map is kept only when the re-asked question is multiple choice (`ask_mcq` or `prequestion`), so a stray letter is never scored against a question already answered.
- `points_met`: the letters from `score_next`, or full point ids, or a mix (step 05c). A letter is the point at that position in the part's ordered points, so no saved mapping is needed. Only ids or letters that don't belong to the part are rejected.
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
   - `offloading` is `choice == just_show_me`; from step 05d it only marks the exchange (for trends and the review), with no nudge and no discount;
   - `conflict_flagged` is `this_message.conflict_flagged` or `source_conflict`;
   - `choice_taken` is `choice`;
   - `support_given` comes from the last issued plan: a teach step's level, `worked_example` for `show`, otherwise `none`.

   No exchange is recorded when there is no focus part and no answer.
5. **Build the turn** (`order_parts`, the blocks in the student's profile), **choose the plan**, save it to `issued_plan` and return.

#### Choosing the plan
At most two steps (three from step 05d, for feedback, `teach_point` and `ask_mcq`). Each is `{move, part_id, cue, data}`. `cue` is one line from `text/moves/<key>.cue.md`, where the key is the move plus its variant (`teach_<level>` and `review_<mode>` until 05d, `ask_mcq_<purpose>` from 05d), falling back to the bare move; what the move means is in the server instructions, sent once (step 05c). The moves are listed in "The move set" below. Steps that ask something carry `data.answer_type`. Steps marked **(stop)** end the plan, because the student needs to reply.

**A question instead of an answer (step 05c).** The question last asked is kept in `issued_plan` as `pending`. A message with no `answer` while one is pending, on the same part or with no new focus, gets `answer_brief` (a few lines), then `reask` **(stop)**: the same question, with the same `score_next`. A message about another part, a research question, "just show me", a pick from `offer_choice` or a new session drops `pending`. Fatigue and stuck rules come first.

**With an answer,** the plan is a feedback step, then the main step:
- prequestion → `feedback`: confirm, or name the picked misconception with its correction, plus the correct idea.
- all points met → `feedback`, with the points they made.
- points missing → `feedback` (naming any misconceptions the answer showed), then `reteach` **(stop)** with only the missing points' wording (step 05c; before, one `reteach_gap` step did both). It re-teaches those and asks them to try again, and nothing else follows it. If they are fatigued or stuck, the `feedback` step also names what's missing and is followed by `offer_choice`, `step_back` or `reteach` with the anchor.

**The main step** is the first rule that matches:
1. Fatigued, and not yet offered this session → `offer_choice` (`reason = fatigued`, `options` stop and quick, with `quick_parts`) **(stop)**. If they carry on, teaching goes on.
2. Stuck on the focus part:
   - `step_back` to its weakest prerequisite **(stop)**;
   - or, when it has no prerequisite, `reteach` of the whole part (through the anchor, or a different example; `switch_approach` before 05c).
3. Focus ambiguous → `ask_which` with the candidates **(stop)**. No focus at all (e.g. "quiz me on what's due") → the top due `review`, if any.
4. `choice == just_show_me` → `show`: a short worked example. Nothing else follows it.
   - A pick from `offer_choice`, sent back as `this_message.choice` (engagement-rules): `quiz` → the current point's check (as `skip_point`), `extend` → `extend` **(stop)**, `stop` → an empty plan (the chatbot wraps up with a one-line summary).
5. Passive streak (engagement-rules): the student's last `engagement.passive_run` messages this session were all labelled `passive`, they aren't fatigued, and it hasn't been offered this session → `offer_choice` (`reason = passive`, `options` quiz, extend and stop) **(stop)**. It's read from `exchange_log` each turn and never stored as a trait.
6. Pre-question eligible → `prequestion` **(stop)**.
   - Eligible means the part has no evidence yet, its level is below `support.worked_example_below`, it has enough misconceptions and there was no "just show me" this session.
   - It is never asked twice: not on the turn its answer arrives, and not again when the last plan already asked it.
   - Options are the correct idea and misconception wrong ideas, in an order fixed per student and part.
7. A weak prerequisite at level new, not checked this session (no evidence on it this session, and not asked in the last plan) → `check_prereq`: one quick question on it **(stop)** (an `ask_mcq` with purpose `prereq` from step 05d; `step_back` likewise, with `data.stuck`).
8. A misconception held on the focus, not already corrected this session (by feedback or an earlier step; carried in `issued_plan`) → `feedback` with the held misconception (`correct_misconception` before 05c).
9. Otherwise → `teach` at the support level. The try / hint / show-me line closes the teaching step:
   - `worked_example`: a short example, then "try this one, or ask for a hint";
   - `hint`: a completion problem for `calculation` and `diagram` parts, otherwise an example and a guiding question;
   - `explain_back` **(stop)**: ask them to explain it.

**Without an answer,** when the main step isn't a stop step or `show`, a second step is added: `extend` if earned, otherwise the top due `review` (in its mode, `recall` or `transfer`; an `ask_mcq` with purpose `review` from step 05d), otherwise nothing.

**Point by point (step 05d).** Where the main step would be `prequestion`, or `teach` at `worked_example` or `hint`, the part is taught one point at a time, in mark-point order:
- **MCQs are built by the server:** the correct option plus up to `mcq.max_options − 1` of the part's misconceptions, shuffled, lettered `A`, `B`, …, with the map stored in `issued_plan` (`mcq`). When the part has fewer than `mcq.min_distractors` misconceptions, `data.extra_option` names a letter for which the chatbot may write one distractor, using only `data.terms`; picking it scores 0.
- **Every server-built MCQ is one move, `ask_mcq` (stop), with a `purpose`:**

  | purpose | asks about | correct option | evidence type |
  |---|---|---|---|
  | `intuition` | the part, before teaching (replaces `prequestion`) | the correct idea | `prequestion` (coverage-weighted) |
  | `check` | the point just taught | the point's wording | `mcq_check` |
  | `prereq` | a weak prerequisite (replaces `check_prereq`; with `data.stuck`, replaces `step_back`) | the prerequisite's first point | `mcq_check` |
  | `review` | a due part, `data.mode` `recall` or `transfer` (with `data.new_context`, a setting the chatbot frames the question in) | one of its points, rotating: the point at (the part's evidence count) mod (its number of points), so nothing is stored | `mcq_check` |

  Distractors are always the asked part's misconceptions, with `extra_option` when it has too few. The answer is `answer.type = mcq` with `answer.choice`; the server reads the purpose from the stored map. Before 05d, `check_prereq` and `review` were free-text questions scored by `points_met`; as MCQs they score 1 or 0. A due review is cleared by any evidence on the part, so the change of evidence type doesn't affect scheduling.
- `ask_mcq` (`intuition`) is asked **once** per part, from an edge with `teach_use = intuition` from a part the student has at developing or above (with the edge note), otherwise from the part's `intuition` line. Eligibility and scoring are as for the pre-question. **Whatever the answer, teaching starts:** `feedback` (right: one line on why; wrong: one line naming the picked misconception), then `teach_point` and `ask_mcq` (`check`) for point 1. It is never re-asked until correct.
- `teach_point` then `ask_mcq` (`check`): one point (`data`: `index`, `total`, `point`, `exemplar`, `level`), as a heading `Point {index} of {total}: {short title}`, one or two sentences and one worked line, at most `points.max_words` words of explanation (the MCQ options don't count); then an MCQ on that point. `support_given` is the part's support level.
- The answer (score 1 or 0) gets `feedback` (naming the picked misconception when wrong), then the next `teach_point` and `ask_mcq`, or, when wrong, `reteach` of that point and `ask_mcq` again, freshly shuffled, at most `points.reteach_limit` times before moving on.
- `choice == skip_point` → `ask_mcq` (`check`) only.
- `choice == just_show_me` → `show`: a one-line intuition from the same source, then the point or formula, short, followed by that point's `ask_mcq` (`check`).
- After the last point → `explain_back` of the whole part **(stop)**, scored on all its points (`teach_explain_back` before 05d). A part already at `levels.secure` goes straight to it.
- Linked parts the student has below developing are never mentioned.
- Progress is kept per part in `issued_plan` (`points`). Moving to another part keeps that part's progress; coming back resumes where it stopped.

**Research questions (step 05e).** `request_type == research` gets:
1. `answer_with_sources`: a full answer, never withheld, with sources and links (`data.trusted_sources`: up to `limits.trusted_sources` from the focus parts, or the candidates, and their ancestors, nearest first), the claims that need checking marked, and a plain statement when the chatbot has no web access.
2. `literacy_task`: line 1 is feedback on the skill, line 2 is one task to do now. The skill is Ask when the question shows fewer than `literacy.ask_min_features` features, otherwise Verify; the wording comes from `text/literacy/<skill>_<level>.md` for the skill's level. `data`: `skill` (`ask` / `verify`), `level`, `task`, the question's `features` and `pattern` (the feedback and task lines from `text/literacy/<skill>_<level>.md`; a missing file is a startup error); a verify task has `answer_type = ail_task`. At secure, the task appears only when the student's research-question count is a multiple of `literacy.secure_every` (counted from `exchange_log`, so it survives a restart), and other turns get the feedback line only. Skipped while fatigued. A literacy step is on its skill's part, but gets no course `terms`.
- The task is saved as pending in `issued_plan` (`literacy`: `skill`, `part_id`, `followups`, `waited`). It is done when a verify task is answered (`answer.type = ail_task`), or, for an ask task, when the next message is a research question (its `ail_question` is the score).
- Not done: that message is answered as usual and, when the plan doesn't already end in a question, `reask` (`data.asked = literacy_task`) re-asks the task in one line. After `literacy.max_followups` re-asks, the next message that doesn't do it records `ail_task` with score 0 on the skill's part, and the task is dropped.
- A plan that already ends in a question leaves the task waiting. After `literacy.max_waits` replies waiting, it takes the next reply's question slot in place of the course question (never a how-AI-works check's), and the course resumes after.
- A new task replaces it. A new session drops it unscored: only a re-asked, ignored task scores 0.
- When a course check loses its slot (to a how-AI-works check or a literacy re-ask), that point stays unchecked (`check_due` in `points`), and the next reply asks its check only, without teaching it again.
- A literacy task never becomes the course's `pending` question.
- `source_conflict` (on any turn) puts a `source_conflict` step first: that's exactly what checking is for, and the claim is corrected. The plan keeps its last steps, where its question is, within the three-step limit.
- `concept` and `homework` follow the rules above and never get a literacy task. `other` gets an empty plan. A research question that comes with an answer to a course question is planned as that answer.

**How-AI-works checks (step 05e).** A one-question check on how chatbots work, at the moment one has just failed. Triggers, in priority order (`plan.HOW_TRIGGERS`), each for one part:
- `source_conflict` → `ail_how_fabrication`;
- `pushback_changed` → `ail_how_agreement`;
- `conflict_flagged` without `source_conflict` (the chatbot corrects itself) → `ail_how_confidence`;
- a research question with `asks_recent = true` and `web_access = false` → `ail_how_cutoff`.

The moment is handled as usual first; then `ask_mcq` with `purpose = how_ai_works` **(stop)** is the last step: the part's point plus its three misconceptions, shuffled and lettered by the server, answered by letter and scored as `ail_how` (with its `point_id`). The check wins: the plan's own question and any literacy task are left out (a literacy task waits; a course check comes in the next reply), and the steps handling the moment are kept within the three-step limit.
- **Limits:** at most one check per reply (the first trigger that passes); at most one per part per session (any `ail_how` evidence on it this session); none while fatigued; with the part at secure, only when the count of that trigger in `exchange_log` is a multiple of `literacy.how_secure_every`.
- **Not ignorable:** the check is kept in `issued_plan` (`how`). Not answered in the next message, it is re-asked (`reask`, same options and letter map), up to `literacy.max_followups` times; not answered after that, `ail_how` is recorded with score 0. While fatigued, a pending check is dropped unscored.
- **Feedback:** one line: whether they were right, naming the picked misconception, then the part's `intuition` (`data.intuition`). Then back to what they were doing (nothing more when there is no course focus).

A profile with `plan = false` (`minimal`) gets no plan, but still gets `score_next` for its focus parts, so its answers are scored.

#### The move set
Fewer moves means a shorter server instructions text and fewer cues to keep apart. Moves that do the same job share one move and one text; `data` says what differs. The final set, after step 05e, is 14 moves:

| move | asks? | from | replaces | `data` that varies it | reference | words in its section |
|---|---|---|---|---|---|---|
| `ask_mcq` | yes **(stop)** | 05d | `prequestion`, `intuition_mcq`, `check_mcq`, `check_prereq`, `step_back`, `review_recall`, `review_transfer` | `purpose` (`intuition` / `check` / `prereq` / `review` / `how_ai_works`, 05e), `options`, `extra_option`; `note` and `via` (intuition), `stuck` (prereq), `mode` and `new_context` (review) | none | 60 |
| `teach_point` | no: an `ask_mcq` check follows | 05d | `teach_worked_example`, `teach_hint_procedural`, `teach_hint_conceptual` | `index`, `total`, `point`, `exemplar`, `level` | notes, misconceptions | 45 |
| `show` | no: an `ask_mcq` check follows | 05b | | `point`, `note` | notes | 30 |
| `explain_back` | yes **(stop)** | 05b | `teach_explain_back` | | none | 25 |
| `extend` | yes **(stop)** | 05b | | | causal | 35 |
| `feedback` | no | 05b | `correct_misconception` (05c) | `correct`, `points_met`, `misconceptions` (picked, shown or held), `secure` (a right answer on a part at secure: confirm, no why) | misconceptions | 45 |
| `reteach` | yes **(stop)**, unless an `ask_mcq` check follows | 05c | `reteach_gap`, `switch_approach` (05c), `reteach_point` (05d) | `missing` or `point`, `anchor`, `answer_type` | notes, anchor | 45 |
| `answer_brief` | no | 05c | | | notes | 20 |
| `reask` | yes **(stop)** | 05c | `literacy_followup` (05e) | `pending` | none | 20 |
| `offer_choice` | yes **(stop)** | 05b | `offer_stop` (engagement-rules) | `reason` (`fatigued` / `passive`), `options` (from `stop`, `quick`, `quiz`, `extend`), `quick_parts` | none | 45 |
| `ask_which` | yes **(stop)** | 05b | | `candidates` | none | 20 |
| `answer_with_sources` | no | 05e | | `trusted_sources` | notes | 40 |
| `literacy_task` | yes **(stop)** when `data.task` | 05e | | `skill`, `level`, `task`, `features`, `pattern` | none | 35 |
| `source_conflict` | no | 05e | | | none | 25 |

- **Sharing.** `feedback` is the only move that names a misconception (picked, shown or held) and corrects it: the wrong idea, one line on why it's wrong, then the right idea, with no praise. A right answer gets one line on why it's right, unless the part is at secure (`data.secure`, tune-from-research). `reteach` never repeats that: it re-teaches only what was missed, a different way in.
- **Interim set (05c).** Step 05c builds the sections and cues for the moves that exist before server-built MCQs: `prequestion`, `check_prereq`, `step_back`, `review_recall`, `review_transfer`, `teach_worked_example`, `teach_hint_procedural`, `teach_hint_conceptual`, `teach_explain_back`, `show`, `feedback`, `reteach`, `extend`, `answer_brief`, `reask`, `offer_stop` and `ask_which` (17). It already merges `correct_misconception` into `feedback`, and `reteach_gap` and `switch_approach` into `reteach`.
- **05d** replaces the asking moves with `ask_mcq`, the teach levels with `teach_point`, and renames `teach_explain_back` to `explain_back`, deleting the old texts. **05e** adds three moves and folds `literacy_followup` into `reask`. **Engagement-rules** generalises `offer_stop` into `offer_choice`, with no new section.
- **Word budget.** The sections above total about 510 words with their headings. With `server_instructions.md` (about 200) and `style.md` (about 90), the whole is about 800, under `instructions.max_words = 900`. As built in 05c, the 17 interim sections with the 10 rules come to about 880 words, so 05d's cut to 11 moves must land before 05e adds three.

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
- `score_next`: for each part a step asks about (and an `offer_choice`'s quick parts), except a pre-question or `ask_mcq` (step 05d), which are answered by option: the points to tick in the student's next answer.
- `data.terms` (step 05c), once per plan, on its first step on a part: names and aliases of the steps' parts, then of known parts (developing or above) linked to them, then of other known parts by importance, up to `limits.terms`. The chatbot doesn't introduce course terms outside it, and explains in plain words when one is needed.
- `score_next` ids are letters, `a`, `b`, `c`… per part in point order (step 05c). A research turn's `score_next` always includes `ail_verify`'s ticks (step 05e).
- `style`, sent only on the first `tutor_turn` of a session or when `client`, `interests` or `max_words` changed since it was last sent (step 05c):
  - `max_words`: the profile's `answer_length`, else `style.max_words`. It limits the explanation only; MCQ options don't count.
  - `interests`: from the profile. When empty, the chatbot uses a neutral everyday example (tune-from-research: it no longer guesses from what it knows about the student).
  - `format`: `text/format/<client>.md`, the first of `claude`, `chatgpt` or `gemini` contained in `client`, else `default`.
- `reference`: only the blocks the plan's moves use, from `[moves.<move>] reference` in `context.toml` (step 05c), and only those in the profile. `misconceptions.held` is the step part's held misconceptions, in full. `misconceptions.watch_for` goes only with moves that ask something (`[watch_for] moves`), as `id` and `wrong_idea` only, so the chatbot can tag a new one. `exam_relevance` is added only when the message mentions an exam or a command word. Before 05c: the profile's blocks that are not plan inputs. Plan inputs are `focus`, `prequestion`, `support`, `session` and `reviews_due`; `teaching_note` is never sent. A block that is only `{"items": [...]}` is sent as the list. The move texts say to use reference only when it helps the current step.
- `candidates` appears when the focus is ambiguous, and `unknown_ids` when `node_ids` had unknown ids.
- **Budget:** a result over `results.max_chars` drops reference blocks from the end of the moves' priority order until it fits, with watch-for misconceptions dropped last. `plan`, `score_next`, `focus` and `style` are never cut. If it is still over, it is sent and the call is logged as over budget.
- Levels only: `p_now` never appears in chatbot-facing output (the CLI keeps the numbers).

#### Blocks
Each block is data for the plan or for reference, without instructions:

| block | contents |
|---|---|
| focus | resolved parts with name, level and type; or `candidates` when ambiguous |
| prequestion | on an untaught, weak part: target, correct idea and misconception distractors; from step 05d, the intuition MCQ's source (a known linked part's edge note, or the part's `intuition` line) |
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
- `ai_literacy` (step 05e): `ask` and `verify`, each with the `level` of `ail_ask` and `ail_verify`; `how_ai_works`, the rollup `level` of its parts and `held`, the wrong ideas about AI the student still holds; and `question_features`: for each feature, the share of research questions showing it over the last `progress.trend_days` against before (`recent`, `before`, `direction` up, down or steady, as for `trends`). These parts are left out of the tree, levers and reviews above.
- `study_pattern`: "your answers tend to drop after about N minutes" (median fatigue onset), when at least `session.pattern_min_sessions` sessions had one; otherwise `null`.

### update_my_profile(interests?, exam_date_override?, answer_length?)
Updates `student_profile`. `interests` and `answer_length` come back in every turn's `style`.

## Prompts
- `review_due`: "Quiz me on what's due."
- `check_me`: "Check my understanding of ___."

## Server instructions
`text/server_instructions.md`, with `text/style.md` appended, then one section per move (`## <move>` and `text/moves/<move>.md`, at most 2 sentences each; step 05c). The whole is at most `instructions.max_words` (900 words); over that is a startup error. The `tutor_turn` description is at most 8 lines.

`style.md` says that `style.max_words` limits the explanation only: MCQ options don't count towards it. The same holds for `points.max_words` on a `teach_point`.

The numbered rules:
1. Call `tutor_turn` at the start of every reply, before writing anything (step 05e: not only about the course).
2. Do the plan's steps in order and nothing else.
3. Label the student's message honestly.
4. Tick only the points the student actually produced.
5. Use `reference` only when it helps.
6. Follow `style`.
7. Never give a numeric mark for a level-marked question.
8. Each plan step names a move: do what that move's section says, using the step's `data` (step 05c).
9. When you find a mistake in something you said, say so in one line, correct it and set `conflict_flagged` (step 05c).
10. Don't introduce course terms that aren't in the step's `terms`; explain in plain words instead (step 05c).
11. One point per message, ending in one question (step 05d). `style.max_words` counts the explanation only, not MCQ options.
12. Never claim to be a teacher. (Safeguarding is left to the chatbot's own guardrails.)

## Changes
- Adding a field to a tool's output is fine.
- Removing or renaming one needs a new tool name, or a `protocol` bump and a note in the PR.
  - Example: `v0.2` replaced `get_learning_context` and `log_exchange` with `tutor_turn`, made the labels describe the student's message, and moved scoring to points met.

## Later (not in the base)
- `start_check` / `submit_check`: past-question, find-the-error and link checks.
- A `check` table for issued checks; results go to `evidence_log` with origin `check`.

See `steps/later.md`.
