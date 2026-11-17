# Step 05: Server and context

**Branch:** `build/05-server-context`
**Read first:** `../reference/tools-and-context.md`, `../reference/settings.md` (context.toml, text/), `../reference/research.md`

## Goal
The MCP server over Streamable HTTP at `/mcp`, with student keys, the four base tools, the two prompts and configurable context blocks.

## Work
- `edux/context_blocks.py`:
  - one function per block, each taking `(student, parts, settings)` and returning a dict or `None`
  - a `BLOCKS` registry
  - `assemble(profile, ...)`, which follows `context.toml` and applies the limits
- `edux/service.py`: `learning_context`, `log_exchange`, `my_progress` and `update_profile`. These hold the logic; the server only adapts arguments.
- `edux/server.py`:
  - FastMCP with instructions from `text/server_instructions.md` and tool descriptions from `text/tools/`.
  - Read `key` from the request query string; map it to a student; reject unknown keys.
  - `Literal` types for labels.
  - Transport security with `ALLOWED_HOSTS` from the environment, so a tunnel host works.
- Prompts: `review_due` and `check_me`.
- Fill in the `text/` files with real wording, including `chatbot_setup.md` (the paste-in instructions for students).
- `text/tools/log_exchange.md` must say: send `evidence` only when the student actually produced an answer or explanation in this turn, scored 0–1 against the notes and mark points from `get_learning_context`. Never send it for the chatbot's own explanation.
- `python -m edux.cli serve`, and `set-profile --student --profile` to switch a student's context profile.
- `context.toml`: add `prequestion`, `session` and `causal` to the `full` profile.
- Unknown keys are refused at the HTTP level (401) before the MCP handshake, as well as in each tool.
- **Progress levers:** "five biggest levers" are ranked by `importance × (1 − p_now)` (important and weak), the same as candidates.
- **Safeguarding** is left to the chatbot's own guardrails. The server instructions don't add a rule for it.

## Pre-questions, support levels, reviews and sessions

### Pre-question block (`prequestion`)
**Why:**
- Answering a question before being taught improves learning of the material asked about: g = 0.54 in a 2023 meta-analysis, with no significant difference between multiple choice and short answer (0.51 vs 0.58) (St. Hilaire, Chan & Ahn, 2024).
- The benefit for material that wasn't asked about is near zero (g = 0.04).
- Committing to a guess matters: g = 0.65 when students guess, 0.22 when they only read the question.
- Multiple choice can plant wrong answers (Roediger & Marsh, 2005), and feedback removes that (Butler & Roediger, 2008).

**Shown when** all of these hold:
- the focus part has `n_evidence = 0` and `p_now < support.worked_example_below`
- the part has at least `prequestion.min_distractors` approved misconceptions
- the student hasn't chosen "just show me" in this session
- `prequestion.enabled` is true

**Returns:**
- **target:** the part's core idea (its first mark point, otherwise its main key wording, otherwise its note's first key point)
- **correct:** the correct idea, in one line
- **distractors:** up to `prequestion.max_options − 1` misconceptions (`id`, `wrong_idea`, `correction`), examiner-report sources first
- **text:** from `text/support/prequestion.md`

**`prequestion.md` tells the chatbot to:**
1. Ask one multiple-choice question about the target, with 3–4 options in random order, before explaining anything.
2. Give no hints, and wait for the student's answer. Never answer its own question.
3. After the answer: if they picked a misconception, name it and say why it's wrong (using `correction`). Then teach the part.
4. Log the answer with `log_exchange` as evidence type `prequestion`, score 1 or 0, including the misconception id if they picked one.
5. Skip the question if the student says "just show me".

**How the answer counts** (see `learner-model.md`): on a part that hasn't been taught, it's diagnostic only. It activates the chosen misconception but doesn't move `p_known`. On a part that has been covered, its effect is weighted by how much it has been covered.

### Support levels: four instead of three
The support block returns a level, and can also return `extend: true`.

| level | when | text file |
|---|---|---|
| worked_example | `p_now < support.worked_example_below` | `support/worked_example.md` |
| hint | below `support.hint_below` | `support/hint_<part_type group>.md` |
| explain_back | otherwise | `support/explain_back.md` |
| extend (added on) | `p_now ≥ support.extend_from` and the student's latest evidence on the part was correct | `support/extend.md` |

**Hints depend on the part type.** Worked examples help procedural learning (Barbieri et al., 2023, maths meta-analysis). For declarative concepts, faded examples were no better than full examples and took longer (Zamary & Rawson, 2018).
- `hint_procedural.md`, for `calculation` and `diagram` parts: a completion problem. Give a worked example with the last step missing, or a diagram description with one shift missing, and ask the student to finish it.
- `hint_conceptual.md`, for `definition`, `mechanism`, `evaluation` and `application` parts: a short complete example, then one guiding question.

These two files replace `support/hint.md`.

**Explain-back re-teaches only the gap.** Self-explanation prompts: g = 0.55 (Bisra et al., 2018), though most of the studies were with undergraduates. Specific feedback beats right/wrong feedback (Wisniewski, Zierer & Hattie, 2020). `explain_back.md` tells the chatbot to:
- ask for the explanation when the student says they've got it or tries to move on
- ask for it in their own words, not copied from the chat above
- score it 0–1 against the part's mark points and key wording, and send that as evidence
- if anything is missing, name the specific missing point(s) and re-teach only those, never the whole topic

**Extend: harder questions from "developing", not just once secure.** Higher-order and mixed quizzes improved higher-order performance, but fact quizzes did not (Agarwal, 2019). `extend.md` tells the chatbot, after a correct recall, to add one question of one of these kinds:
- apply the idea to an unseen case
- "when does this break / what assumption matters?"
- follow a causal link from the context

The answer is logged as evidence with `question_depth = transfer`.

### Reviews: recall first, then a new context
Practice testing transfers to new situations (d = 0.40), most strongly to application and inference questions. But it depends on feedback that explains, and on the student being able to answer at all first; without those, the benefit largely disappears (Pan & Rickard, 2018).

Each item in `reviews_due` gets a `mode`:
- **`recall`:** when `p_now < levels.new`. Ask straight recall of the part.
- **`transfer`:** otherwise. Ask about the same idea in a new context, chosen in this order: a causal or analogous link from the graph, then a past-paper question from a series the student hasn't seen, then an unseen case.

Feedback on a review always explains why, not just right or wrong.

### Session block (`session`)
Built from `learner.session_state` (step 04c).
- Returns `null` when there's nothing to say.
- When **fatigued**, it returns `{state: "fatigued", minutes, quick_parts}` plus `text/session/fatigued.md`. `quick_parts` are up to `session.quick_parts` parts with `p_now` between `levels.new` and `levels.secure`.
- When **stuck**, it returns `{state: "stuck", parts, step_back_to}` plus `text/session/stuck.md`. `step_back_to` is the weakest prerequisite of the stuck part.

**`fatigued.md`:** offer the student a choice. Stopping is the default suggestion: give a one-line summary of what they covered and when their next reviews are due. The alternative is a short burst of 2–3 quick questions on `quick_parts`. Never push them to keep going.

**`stuck.md`:** don't repeat the same explanation. Either step back to `step_back_to`, or switch approach (use the anchor, a different example or a diagram).

### Progress: study pattern
`get_my_progress` gains `study_pattern`:
- When at least `session.pattern_min_sessions` sessions had a fatigue onset: "your answers tend to drop after about N minutes", using the median onset minute.
- Otherwise `null`.

### Server instructions: additions
- **Pre-questions:** ask before explaining, wait for the answer, and correct the misconception the student picked.
- **Explain-back:** re-teach only the missing points.
- **Reviews:** explain why.
- **Fatigue:** offer stopping first.
- **Level-marked questions:** never give a numeric mark. (Level-marked checks come in step 07, but the rule is stated now.)

### Settings added in this step
```toml
[prequestion]
enabled = true
max_options = 4
min_distractors = 2
exchange_weight = 0.5      # an exchange on the part counts this much towards coverage
full_weight_at = 3.0       # coverage at which a pre-question counts as full evidence

[support]
extend_from = 0.40         # developing and above get higher-order questions mixed in

[session]
quick_parts = 3
pattern_min_sessions = 3
```

## Choosing what goes into each block
Graph lookups (step 03) return full lists with the numbers needed to rank them. Each block chooses what reaches the chatbot **for this turn**, not by a fixed top N. Most blocks combine three ingredients:
1. **Content weights:** node importance, link weight (`edge_weight`), source authority, marks.
2. **The student's state:** `p_now`, active misconceptions, recent activity (step 04).
3. **Relevance to the message:** `graph.relevance` / `graph.node_relevance`.

| block | what decides what's shown |
|---|---|
| focus | how well each part matches the message (`graph.resolve`). Ties go to parts the student touched recently, then importance |
| support | the student's `p_now` on the focus part. Nothing to rank |
| weak_prerequisites | how weak the student is on it × link weight × importance |
| anchor | the student is secure on the analogous part × link weight |
| confusables | past mix-ups by this student, or the message mentions the other part × link weight |
| causal (new) | the message asks about effects or causes and mentions the other end × link weight. Uses `graph.causal_out` / `causal_in` |
| active_misconceptions | ones the student holds first, then relevance to the message, then how recently seen |
| notes | relevance to the message first, then source authority (a calculation question gets the formula note) |
| exam_relevance | marks at stake, closeness of the exam, and command word matching the request ("calculate", "explain") |
| reviews_due | due-ness × importance, boosted when the due part is linked to the current focus |
| prequestion | shown only on untaught, weak parts with enough misconceptions; distractors from examiner-report sources first |
| session | shown only when fatigued or stuck (`learner.session_state`) |
| teaching_note | built from the other blocks. Nothing to rank |

- Every coefficient in these scores goes in `settings.toml`, under a section per block if they differ. The limits stay in `context.toml`.
- Add `causal` to `BLOCKS`, to the `full` profile in `context.toml`, and to the block table in `reference/tools-and-context.md`.
- The cross-student misconception signal (`learner.misconception_link_signal`) is added to link weight when it is read, with share `link_weight.w_misconception`. It's 0 until there is enough evidence across students.

## Commits
1. `feat(context): add context blocks and profile assembly`
2. `feat(service): add learning context, exchange logging, progress and profile`
3. `feat(server): serve tools over streamable HTTP with student keys`
4. `feat(server): add review and check prompts`
5. `feat(context): add pre-question block from misconceptions`
6. `feat(context): add extend level and part-type hints`
7. `feat(context): set recall or transfer mode for reviews`
8. `feat(context): add session block for fatigue and stuck parts`
9. `feat(service): add study pattern to progress`
10. `docs(text): write server instructions, tool descriptions and support text`
11. `docs(text): write pre-question, support, session and review wording`

## Done when
- MCP Inspector, connected to `http://localhost:<port>/mcp?key=<key>`, lists the tools.
- `get_learning_context` returns the blocks for an `example-mini` part.
- `log_exchange` returns at once, and `state` shows the update.
- A wrong key is refused.
- Switching the student's profile to `minimal` changes the output.
- **Pre-questions:** a new part with misconceptions returns a pre-question with 2–3 distractors drawn from misconceptions. The same part, once it has evidence, gets no pre-question.
- **Hints:** a calculation part at hint level gets the procedural hint text, and a definition part gets the conceptual one.
- **Extend:** a developing part whose latest answer was correct includes `extend: true` in support.
- **Reviews:** with due reviews, one weak part shows `recall` and one developing part shows `transfer`.
- **Session:** a fatigued test student from 04c gets the session block, with stopping offered first.
- The checks above are also run through a small Python MCP client script (list tools, call each, wrong key, profile switch), so they don't depend on Node.
