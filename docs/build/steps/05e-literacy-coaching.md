# Step 05e: Literacy coaching inside everyday questions

**Branch:** `build/05e-literacy-coaching`
**Read first:** `docs/build/README.md`, `reference/tools-and-context.md`, `reference/learner-model.md`, `reference/course-pack-format.md`, `reference/research.md`, `edux/plan.py`, `edux/service.py`

## Why
- **Refusing answers drives students away.** Students who were refused answers stopped using the tool (the Khanmigo trial, in the team research doc). So the answer is never withheld.
- **Every research answer teaches a little.** Each one comes with one line of feedback and one task for the student to do. That's how the skill is built up over time.
- **Checking claims can be taught.** Checking claims the way fact-checkers do ("lateral reading") can be taught to high-school students in a few lessons (Wineburg et al., 2022, randomised). We apply it to AI answers.

## What changes, in one line each
1. Two AI-literacy skills, loaded with every pack, tracked by the existing learner model.
2. Each message is labelled with a request type and, for research questions, question features.
3. A research question gets a full answer with sources, then one feedback line and one task.
4. An ignored task is re-asked once, then recorded as 0.
5. Trusted sources per topic in the course pack.
6. AI-literacy levels and trends in `get_my_progress`.

---

## A. AI-literacy skills
A committed mini pack, `ingest/ai_literacy/`, in course-pack format (`nodes.csv`, `mark_points.csv`), is loaded with every pack:
- topic `ai_literacy` → concept `ai_literacy_skills` → two parts:
  - `ail_ask`: phrasing a precise, answerable question;
  - `ail_verify`: checking a claim against an independent source.
- **The four question features are `ail_ask`'s mark points** (`concept`, `context`, `asks_sources`, `asks_reasoning`).
- **The four verify ticks are `ail_verify`'s mark points**, in order:
  1. opened the source;
  2. named the publisher and date;
  3. compared the claim;
  4. said whether it matched.
- No exam weight. Importance is fixed at `literacy.importance`. Both parts are left out of course levers, candidates and the course tree in progress (they get their own section, F).
- The existing learner model tracks them: decay, spacing and levels as for any part.

## B. Labels
`this_message` gets:
- `request_type`: `concept`, `research` (a factual or current question about the world), `homework` or `other`;
- `question_features`, for `research` only: which of `concept`, `context`, `asks_sources` and `asks_reasoning` the question shows;
- `source_conflict`, a boolean: the student reports that a link failed or didn't say what was claimed.

Migration `008_exchange_request.sql` adds `request_type`, `question_features` and `source_conflict` columns to `exchange_log` (events, so they are replayed). `source_conflict` also sets the existing `conflict_flagged`.

`concept` and `homework` follow the existing plan and never get literacy tasks. `other` gets an empty plan.

## C. Evidence
- **Ask, on every research question:** type `ail_question` on `ail_ask`, score = features present / 4.
- **Verify:** from the student's reply to a verify task, scored by the ticks they produced (`points_met`, letters from `score_next`). Type `ail_task` on `ail_verify`.
- **Unprompted checking:** a student who reports checking a claim without being asked sends `answer.type = ail_unprompted` on `ail_verify`, ticked the same way. It has a lower slip, so it counts more. Every research turn's `score_next` includes `ail_verify`'s ticks, so this can be scored on the next turn.
- **An ask task** (rewrite your question) is done when the next message is a research question. Its `ail_question` evidence is the score; nothing else is recorded.

## D. The plan for a research turn
1. **`answer_with_sources`:**
   - **Answer fully.** Never withheld.
   - **Give sources and links** where the chatbot can, preferring the pack's trusted sources for the topic (`data.trusted_sources`, from the resolved topic and its ancestors).
   - **Mark the claims that need checking** (data and figures).
   - **Say plainly if it has no web access,** and point to where to check.
2. **`literacy_task`**, always included:
   - **Line 1 is feedback on the skill:** on their question (Ask), or on how to check this kind of claim (Verify).
   - **Line 2 is one concrete task they do now.**
   - **Which skill:** Ask when the question shows fewer than `literacy.ask_min_features` features, otherwise Verify.
   - **The task gets harder with the skill's level:**

| skill level | feedback line | task |
|---|---|---|
| new | model it: "I read your question as: UK petrol prices, 2025, effect on demand." | "Rewrite your question adding a time period, then I'll answer the sharper version." / "Open the ONS link: what month is that figure for?" |
| developing | one tip: "Data questions work better with a place and a date." | "Which claim above would you check first, and where?" |
| secure | credit what they did: "You asked for sources; that's why these are traceable." | a spot-check only every `literacy.secure_every` research turns: "Check one figure and tell me if it matches." Other turns get the feedback line only |

The research-turn count since the last task comes from `exchange_log` and `evidence_log`, so it survives a restart.

### Not ignorable, never a barrier
- The task is saved as pending in `issued_plan.plan_json` (`literacy: {skill, part_id, followups}`).
- **Not done in the next message:** answer the new message as usual, and the plan adds `literacy_followup`, which re-asks the pending task in one line.
- **Still not done after `literacy.max_followups`:** record `ail_task` with score 0 on that skill's part, and drop the task.
- **Bad links:** when `source_conflict` is set, a `source_conflict` step comes first: tell the student that's exactly what checking is for, and correct the claim. If they reported the ticks, they are scored as for any verify task.
- **Fatigue:** no task while the student is fatigued (04c). The answer still comes with sources.

## E. Course pack: trusted sources
`trusted_sources.csv`:

| column | meaning |
|---|---|
| id | stable id, e.g. `ons_inflation`, so teacher feedback can target the row |
| node_id | a topic or concept the source is good for |
| name | e.g. `ONS` |
| url | the landing page for this kind of data |
| what_for | one line, e.g. `UK inflation and price indices` |

Plus the standard status columns. Examples: ONS, Bank of England, OBR, IFS and CMA, linked to topics.

**Validation (errors):** a malformed URL, or an unknown `node_id`.

## F. Progress
`get_my_progress` adds an `ai_literacy` section:
- the level of each skill;
- the trend in question features: the share of research questions showing each feature over the last `progress.trend_days`, against before, as up, down or steady.

## Settings
```toml
[literacy]                 # AI-literacy coaching (step 05e)
secure_every = 3           # at secure, a task every this many research turns
max_followups = 1          # re-asks of an ignored task before it scores 0
ask_min_features = 2       # fewer features than this: coach the question (Ask), else Verify
importance = 0.5           # fixed importance of the AI-literacy parts

[bkt.evidence]
ail_question = { slip = 0.15, guess = 0.20 }
ail_task = { slip = 0.10, guess = 0.15 }
ail_unprompted = { slip = 0.05, guess = 0.10 }
```

## Text
- `text/moves/answer_with_sources.md`, `literacy_task.md`, `literacy_followup.md` and `source_conflict.md`, each with a `.cue.md`.
- `text/literacy/<skill>_<level>.md` (`ask_new`, `ask_developing`, `ask_secure`, `verify_new`, `verify_developing`, `verify_secure`): the feedback and task patterns from the table above.
- `text/tools/tutor_turn.md` lists the new labels.

## Docs and scripts
- `reference/course-pack-format.md`: `trusted_sources.csv`, the AI-literacy mini pack, validation.
- `reference/tools-and-context.md`: the labels, the research plan, the new moves and the progress section.
- `reference/learner-model.md`: the AI-literacy parts and evidence types.
- `reference/settings.md`: `[literacy]` and the new evidence types.
- `reference/database.md`: migration 008 and the `trusted_source` table.
- `example-mini`: a few trusted sources.
- `scripts/check_mcp.py`: a research-question run (below).

## Commits (one logical change each, no attribution)
1. `feat(ingest): add AI-literacy skills and trusted sources`
2. `feat(server): label request type and question features`
3. `feat(learner): record AI-literacy evidence`
4. `feat(context): answer research questions with sources and a literacy task`
5. `feat(context): follow up an unanswered literacy task`
6. `feat(service): show AI-literacy skills in progress`
7. `docs(text): write literacy feedback and task texts`
8. `chore(scripts): add a research-question run to the MCP check`

## Done when (by hand, no tests yet)
- **A research question from a new student** gets `answer_with_sources`, then a `literacy_task` with one feedback line and one task.
- **Ignoring the task** gets one `literacy_followup`, then a recorded `ail_task` score of 0.
- **Answering a verify task** raises `ail_verify`.
- **A well-phrased question** raises `ail_ask`.
- **At secure level,** the task appears only every `secure_every` research turns.
- **Course questions** (`request_type = concept`) never get literacy tasks.
- `rebuild` gives identical state.
