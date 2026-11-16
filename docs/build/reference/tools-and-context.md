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
| support | support level and its text |
| weak_prerequisites | prerequisites below secure |
| anchor | a secure analogous part with the edge note |
| confusables | parts to contrast |
| active_misconceptions | wrong idea and correction |
| notes | summaries, key points and key wording, in source-authority order, with source titles |
| exam_relevance | papers and marks that test these parts |
| reviews_due | up to N due parts |
| teaching_note | short paragraph (see `learner-model.md`) |

Unknown blocks in a profile are skipped with a warning.

### log_exchange(node_ids, question_depth, engagement, offloading, support_given?, choice_taken?, misconception_ids?, conflict_flagged?, prompt_text?)
Called after answering. The labels are `Literal` enums:
- `question_depth`: `surface` / `mechanism` / `transfer`
- `engagement`: `passive` / `active` / `constructive`
- `support_given`: `worked_example` / `hint` / `explain_back` / `none`
- `choice_taken`: `try_first` / `hint` / `just_show_me` / `none`

The tool:
1. Writes the event with `protocol` and `settings_hash`.
2. Returns `{"ok": true}` immediately.
3. Applies the update on a background worker.

`prompt_text` is stored only when `STORE_PROMPTS=1`.

### get_my_progress()
For students.
- Tree with levels: topic → subtopic → concept, with parts on request.
- Five biggest levers: lowest `p_now × importance`.
- Weak links: confusable or causal pairs where one side is weak.
- Reviews due.
- AI-literacy trends, as directions over the last 14 days vs before: share of mechanism/transfer questions, share of constructive engagement, "just show me" rate.

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
8. Never claim to be a teacher; flag safeguarding concerns as instructed.

## Changes
- Adding a field to a tool's output is fine.
- Removing or renaming one needs a new tool name, or a `protocol` bump and a note in the PR.

## Later (not in the base)
- `start_check` / `submit_check`: past-question, find-the-error and link checks.
- `check_log` migration.

See `steps/later.md`.
