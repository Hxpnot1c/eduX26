# Step 05d: Point by point

**Branch:** `build/05d-point-by-point`
**Read first:** `docs/build/README.md`, `reference/tools-and-context.md` (choosing the plan), `reference/learner-model.md` (evidence, offloading), `reference/course-pack-format.md` (nodes, edges, mark points, misconceptions), `reference/research.md`, `edux/plan.py`

## Why
Sources are in `reference/research.md`.
- **Learner-paced segments.** Meaningful, coherent segments that the learner moves through at their own pace improve retention and transfer, and reduce cognitive load (Rey et al., 2019).
- **A quick test after a segment** helps learning of the next one: the forward testing effect (Chan, Meissner & Davis, 2018).
- **But not too often.** Switching often between testing and studying can hurt new learning (Davis, Chan & Wilford, 2017). So the check comes after each meaningful point, not after every sentence.
- **Mastery learning** helps, especially weaker students, but strict gating can lower completion (Kulik, Kulik & Bangert-Drowns, 1990). So a student who already knows a point can skip to its check.
- **Checks the server can score.** The server scores a multiple-choice check from the letter picked, without relying on the chatbot's judgement, and a wrong pick names the misconception directly.

## What changes, in one line each
1. The course pack gets an intuition line per part, a teaching use and a required note on every edge, and an order for mark points.
2. An intuition question replaces the pre-question.
3. Teaching a part becomes a loop: one short point, then one multiple-choice check on that point.
4. "Just show me" shows the point and still ends with its check, and no longer discounts later evidence.
5. "I know this" skips straight to the point's check.
6. The loop ends with an explain-back of the whole part.

---

## A. Course pack
- **`nodes.csv`** gets `intuition`: for parts, one line in everyday language that leads into the idea (e.g. for PED: "If the price of your usual snack went up, would you still buy it?").
- **`edges.csv`:**
  - `note` is required for every edge type, not only analogous and causal;
  - new column `teach_use`: `intuition` (the linked part can lead into this one), `contrast` (use it to show the difference) or `none` (default).
- **`mark_points.csv`** gets `order`: an integer within a part.
- **Validation:**
  - errors: an edge with no note, a bad `teach_use`, a duplicate `order` within a part;
  - warnings: a part with fewer than `points.warn_min` or more than `points.warn_max` points; a part with fewer than `mcq.min_distractors` misconceptions (replacing the "no misconception" warning); a part with no `intuition`.
- **Fallback:** a part with no mark points uses its notes' key points, in file order (ids `<note_id>:k<n>`, as now).
- Score points everywhere (`score_next`, letters from 05c) follow this order.
- `example-mini` gets notes on every edge, `teach_use` where it fits, `intuition` on every part, and `order` on every mark point.

## B. Multiple-choice questions
The server builds both MCQs below:
- **Options:** the correct option plus up to `mcq.max_options − 1` of the part's misconceptions (their `wrong_idea`), shuffled by the server, lettered `A`, `B`, `C`….
- **The letter → option map is stored in `issued_plan.plan_json`** (`mcq`). The chatbot shows the options as given.
- **The student answers with a letter.** The chatbot sends `answer.choice` (e.g. `"B"`). The server scores it (1 or 0) and activates the picked misconception.
- **Few misconceptions:** when the part has fewer than `mcq.min_distractors`, `data.extra_option` names a free letter, and the move text lets the chatbot write one more distractor for it, using only `data.terms` (05c). Picking it scores 0 and activates nothing.
- **Lost map:** if the map is missing (e.g. after a restart or `seed-demo --reset`), nothing is recorded, and the plan re-asks the same question with freshly shuffled options.

## C. The loop for one part
1. **`intuition_mcq`** **(stop)**, replacing `prequestion`. At most `mcq.intuition_max` per part, each from a different source:
   - **Source:** an edge with `teach_use = intuition` from a part the student has at developing or above (`data.note` is the edge note, `data.via` its name); otherwise the part's `intuition` line.
   - **Correct option:** the correct idea, as for the pre-question now.
   - Eligibility and scoring are as for the pre-question (05b): evidence type `prequestion`, weighted by coverage, so on an untaught part it is diagnostic only.
   - After a correct answer, or when sources run out, teaching starts.
2. **`teach_point`**, then **`check_mcq`** **(stop)**, in the same reply:
   - **`teach_point`** carries one point. `data`: `index`, `total`, `point`, `exemplar`. **Reply shape:**
     - a heading line, `Point {index} of {total}: {short title}`;
     - one or two sentences;
     - one worked line (LaTeX when it applies).

     At most `points.max_words` words, no tangents, at most one example.
   - **`check_mcq`** checks that point only. The correct option is the point's wording; the distractors are the part's misconceptions (B). `data.answer_type = mcq_check`.
   - `support_given` on the exchange is the part's support level (`worked_example` or `hint`), so the immediate-recall rule applies to the answer.
3. **The student answers** (`answer.type = mcq_check`, `answer.choice`). The next plan is:
   - **`feedback`:** right: one line on why; wrong: name the picked misconception and why it's wrong;
   - then either:
     - right: the next `teach_point` and `check_mcq`;
     - wrong: `reteach_point` (a different way in: the known linked part, a different example or the diagram) and `check_mcq` again, freshly shuffled. At most `points.reteach_limit` re-teaches per point; after that, move on to the next point. The wrong evidence already schedules the part's review under the spacing rules, so nothing extra is recorded.
4. **"I know this"** (`this_message.choice = skip_point`, a new value) → `check_mcq` only, with no teaching. `support_given` is `none`, so the answer is not discounted as immediate recall.
5. **"Just show me"** (`choice = just_show_me`) → `show`: a one-line intuition from the same source as `intuition_mcq`, then the point or formula, short, ending with that point's `check_mcq`. See D for how it is scored.
6. **After the last point** → `explain_back` of the whole part **(stop)**. This joins the points together and is the main evidence. It is scored on all of the part's points (`points_met`), as type `explain_back`.
7. **Well-known parts:** a part already at `levels.secure` skips the loop and goes straight to `explain_back`.

**Rules for every step in the loop:**
- Linked parts the student doesn't know (below developing) are never mentioned, in the intuition or in teaching. Only edges to known parts are sent, and course terms are limited to `data.terms` (05c).
- Fatigue and stuck rules still come first, as in 05b.
- A plan can now have **three steps** (feedback, `teach_point`, `check_mcq`). Nothing is added after a stop step.

## D. "Just show me" no longer changes understanding
- **No nudge:** an exchange with `choice = just_show_me` gets no depth or engagement nudge.
- **No offloading discount:** `offload_left` is no longer set, and `offloading.guess_after` and `offloading.checks_discounted` are removed. The immediate-recall rule already lowers the credit for an answer straight after being shown.
- **Still recorded:** the exchange keeps `offloading = 1` for the AI-literacy trends, and the `just_show_me` review is still queued after `scheduling.just_show_me_gap_days`.
- `part_state.offload_left` stays in the schema, always 0. `rebuild` applies the new rule to old events too.

## E. Point progress
Progress is kept per part in `issued_plan.plan_json`, not in learner state:

```json
"points": {"ped_formula": {"index": 2, "reteaches": 0, "intuition_asked": 1}, "ped_values": {"index": 1, "reteaches": 1, "intuition_asked": 2}}
```

- A message that moves to a different part keeps the first part's progress. Coming back resumes at the point it stopped on.
- A finished part (explain-back asked) is removed from the map, so teaching it again starts from point 1.
- `evidence_log` stores no point id, so progress can't be rebuilt from events, and doesn't need to be: losing it only means starting a part from point 1 again.
- Rebuild is unaffected: it replays the evidence, and point progress is not part of state.

## F. Learner model
- New evidence type `mcq_check`, with its own slip and guess in `[bkt.evidence]`. Its guess is about 1 in 4 options, so one check counts for less than an explanation.
- The immediate-recall rule applies to it as to any chat evidence.
- The offloading rule changes as in D.

## Settings
```toml
[points]                   # point-by-point teaching (step 05d)
max_words = 80             # words per teach_point
reteach_limit = 1          # re-teaches of a missed point before moving on
warn_min = 2               # validation warning below this many points per part
warn_max = 4               # and above this many

[mcq]                      # server-built multiple-choice questions (step 05d)
max_options = 4            # replaces prequestion.max_options
min_distractors = 2        # replaces prequestion.min_distractors; fewer: the chatbot may add one
intuition_max = 2          # intuition questions per part

[bkt.evidence]
mcq_check = { slip = 0.10, guess = 0.25 }

# removed: [offloading] guess_after, checks_discounted
```

In `context.toml`, the watch-for list follows the new moves:
```toml
[watch_for]
moves = ["intuition_mcq", "check_prereq", "check_mcq", "teach_explain_back", "review", "extend"]
```

## Text
- `text/moves/intuition_mcq.md`, `teach_point.md`, `check_mcq.md`, `reteach_point.md`, each with a `.cue.md`. `show.md` is rewritten for the loop. `prequestion.md` is removed.
- `text/server_instructions.md` gets a "one point per message, ending in one question" rule.
- `text/tools/tutor_turn.md` lists `skip_point`, `mcq_check`, `intuition_mcq` and `answer.choice`.

## Docs and scripts
- `reference/course-pack-format.md`: `intuition`, `teach_use`, required edge notes, `order`, validation.
- `reference/tools-and-context.md`: the MCQs, the loop, the new moves, `skip_point`, `answer.choice`, three-step plans.
- `reference/learner-model.md`: `mcq_check` and the offloading change.
- `reference/settings.md`: `[points]`, `[mcq]`, the new evidence type and the removed offloading settings.
- `reference/database.md`: what `issued_plan` carries.
- `scripts/check_mcp.py`: a point-by-point run (below).

## Commits (one logical change each, no attribution)
1. `feat(ingest): add intuition lines, edge teaching use and mark-point order`
2. `feat(learner): add MCQ check evidence`
3. `feat(learner): stop discounting evidence after "just show me"`
4. `feat(context): build and score multiple-choice questions on the server`
5. `feat(context): ask intuition questions from known links before teaching`
6. `feat(context): teach one point at a time with a check after each`
7. `feat(context): let students skip or be shown a point, then check it`
8. `feat(context): finish a part with an explain-back of all its points`
9. `docs(text): write point-by-point move texts`
10. `chore(scripts): add a point-by-point run to the MCP check`

## Done when (by hand, no tests yet)
- `scripts/check_mcp.py` runs `ped_formula` as demo-secure: intuition MCQ → point 1 of N with a check MCQ → a correct letter → point 2 → a wrong letter (feedback names the misconception, and it is active) → one re-teach → … → explain-back.
- Every `teach_point` asks for at most 80 words, and every reply in the loop ends in exactly one question.
- MCQ options are shuffled differently for different students, and the stored map scores the letter.
- With the map deleted, an answer records nothing and the same question comes back with new options.
- "I know this" goes straight to the check; "just show me" shows the point and ends with its check.
- After "just show me", the next answer's evidence uses the normal or immediate guess, not a discount.
- No step mentions a linked part the student has below developing.
- `rebuild` gives identical state.
- **claude.ai check (Vishnu runs it):** each reply is short and ends in one question.
