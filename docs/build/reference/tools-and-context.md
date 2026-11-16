# Tools and context

The MCP server is a thin layer. `edux/server.py` registers tools and prompts and converts arguments. All logic is in `edux/service.py`, which calls `edux/graph.py` (content lookups), `edux/learner.py` (state and scoring) and `edux/context_blocks.py` (assembling context). Descriptions and instructions are read from `text/`.

**Principle: the chatbot labels, the server scores.** The server never calls an LLM. The chatbot sends structured labels; the server applies fixed rules from `settings.toml`.

## Identity
Each student has a key. The connector URL is `https://<host>/mcp?key=<key>`. The server reads the key from the request, looks up the student, and rejects unknown keys. The key is never passed as a tool argument.

## Tools in the base

### get_learning_context(message, node_ids?, client?)
Called before answering any course question.
- `message`: the student's message, used for note search when `node_ids` is empty.
- `node_ids`: parts or concepts the chatbot thinks the message is about.
- `client`: e.g. `claude`, `chatgpt`, `gemini`.

Returns the blocks named in the student's context profile (see `settings.md`):

| block | contents |
|---|---|
| focus | resolved parts with name, level and type; or `candidates` when ambiguous |
| prequestion | on an untaught, weak part: a multiple-choice question to ask before teaching (target, correct idea, misconception distractors, text) |
| support | support level (`worked_example` / `hint` / `explain_back`), `extend: true` when earned, and the text for the part type |
| session | only when fatigued (offer stopping first, or a few quick questions) or stuck (step back or switch approach) |
| weak_prerequisites | prerequisites below secure |
| anchor | a secure analogous part with the edge note |
| confusables | parts to contrast |
| causal | what this part affects, and what affects it, with the edge notes |
| active_misconceptions | wrong idea and correction |
| notes | summaries, key points and key wording, in source-authority order, with source titles |
| exam_relevance | papers and marks that test these parts |
| reviews_due | up to N due parts, each with a `mode`: `recall` (weak) or `transfer` (a new context) |
| teaching_note | short paragraph (see `learner-model.md`) |

Unknown blocks in a profile are skipped with a warning.

### log_exchange(node_ids, question_depth, engagement, offloading, support_given?, choice_taken?, misconception_ids?, conflict_flagged?, prompt_text?, evidence?)
Called after answering. The labels are `Literal` enums:
- `question_depth`: `surface` / `mechanism` / `transfer`
- `engagement`: `passive` / `active` / `constructive`
- `support_given`: `worked_example` / `hint` / `explain_back` / `none`
- `choice_taken`: `try_first` / `hint` / `just_show_me` / `none`

`evidence` (optional) is a list of `{part_id, type, score, misconception_ids?}`, sent only when the student produced an answer or explanation in this turn. `score` is 0–1, judged against the notes and mark points from `get_learning_context`. Never sent for the chatbot's own explanation. It is written to `evidence_log` with origin `chat` (see `learner-model.md`).

The tool:
1. Writes the exchange event, and any evidence events, with `protocol` and `settings_hash`.
2. Returns `{"ok": true}` immediately.
3. Applies the update on a background worker.

`prompt_text` is stored only when `STORE_PROMPTS=1`.

### get_my_progress()
For students.
- Tree with levels: topic → subtopic → concept, with parts on request.
- Five biggest levers: highest `importance × (1 − p_now)`, i.e. important and weak.
- Weak links: confusable or causal pairs where one side is weak.
- Reviews due.
- AI-literacy trends, as directions over the last 14 days vs before: share of mechanism/transfer questions, share of constructive engagement, "just show me" rate.
- `study_pattern`: "your answers tend to drop after about N minutes" (median fatigue onset), when at least `session.pattern_min_sessions` sessions had one; otherwise `null`.

### update_my_profile(interests?, exam_date_override?, answer_length?)
Updates `student_profile`.

## Prompts
- `review_due`: "Quiz me on what's due."
- `check_me`: "Check my understanding of ___."

## Server instructions (summary of `text/server_instructions.md`)
1. Call `get_learning_context` before answering any course question.
2. Answer from the notes. Cite them. Say if they don't cover it.
3. Follow the support level. Offer the choice: try first, a hint, or just show me.
4. Use the anchor and confusables when they help.
5. Correct active misconceptions explicitly.
6. Weave in at most one review when due.
7. Call `log_exchange` after answering, with honest labels.
8. Never claim to be a teacher. If a student says something suggesting they or someone else is at risk, stop tutoring, encourage them to speak to a trusted adult or the school's safeguarding lead, and give emergency contacts if urgent. (No automatic reporting yet.)
9. Pre-questions: ask before explaining, wait for the answer, and correct the misconception the student picked.
10. Explain-back: re-teach only the missing points.
11. Reviews: feedback explains why, not just right or wrong.
12. Fatigue: offer stopping first; never push the student to continue.
13. Never give a numeric mark for a level-marked question.

## Changes
- Adding a field to a tool's output is fine.
- Removing or renaming one needs a new tool name, or a `protocol` bump and a note in the PR.

## Later (not in the base)
- `start_check` / `submit_check`: past-question, find-the-error and link checks.
- A `check` table for issued checks; results go to `evidence_log` with origin `check`.

See `steps/later.md`.
