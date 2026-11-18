# Step 05e: Literacy coaching inside everyday questions

**Branch:** `build/05e-literacy-coaching`
**Read first:** `docs/build/README.md`, `reference/tools-and-context.md`, `reference/learner-model.md`, `reference/course-pack-format.md`, `reference/research.md`, `edux/plan.py`, `edux/service.py`

## Why
- **Refusing answers drives students away.** Students who were refused answers stopped using the tool (the Khanmigo trial, in the team research doc). So the answer is never withheld.
- **Every research answer teaches a little.** Each one comes with one line of feedback and one task for the student to do. That's how the skill is built up over time.
- **Checking claims can be taught.** Checking claims the way fact-checkers do ("lateral reading") can be taught to high-school students in a few lessons (Wineburg et al., 2022, randomised). We apply it to AI answers.

## How this assesses AI literacy
AI literacy is assessed by **stealth assessment** (Shute, 2011): evidence comes from what students do in their normal work, and the same moments are used to build the skill, rather than from a separate test. It's designed with **evidence-centred design** (Mislevy, Steinberg & Almond, 2003), which uses three models:

- **Competency model (what we measure):** the AI-literacy parts `ail_ask`, `ail_verify` and the "how AI works" parts (A), alongside the course parts.
- **Evidence model (what counts, how it's scored):** the chatbot's labels and ticks, plus multiple-choice letters, scored by the server's fixed rules into the existing Bayesian learner model.
- **Task model (where evidence comes from):** moments in normal work. A research question leads to a literacy task. A failed link, a self-correction or a changed answer after pushback leads to a one-question "how AI works" check (G).

## What changes, in one line each
1. Three AI-literacy skills (Ask, Verify, How AI works), loaded with every pack, tracked by the existing learner model.
2. Each message is labelled with a request type and, for research questions, question features.
3. A research question gets a full answer with sources, then one feedback line and one task.
4. A task the student hasn't done is re-asked once, then recorded as 0. A task that never got its re-ask expires at session end with no score.
5. Trusted sources per topic in the course pack.
6. AI-literacy levels and trends in `get_my_progress`.
7. A failed link, a self-correction or a changed answer after pushback gets a one-question "how AI works" check.

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
- concept `ail_how_ai_works` → one part per AI failure type (G):

| part | taught when | point (correct option) |
|---|---|---|
| `ail_how_fabrication` | a link or source fails, or doesn't say what was claimed (`source_conflict`) | It predicts likely text, so it can make up real-looking links |
| `ail_how_confidence` | the chatbot corrects itself (`conflict_flagged`) | Sounding confident doesn't show whether an answer is correct |
| `ail_how_cutoff` | a research question about recent data or events (`asks_recent`) when the chatbot has no web access (`web_access = false`) | Without searching, a chatbot's knowledge stops at its training date |
| `ail_how_agreement` | the chatbot changes its answer after the student pushes back (`pushback_changed`) | Chatbots can shift answers to agree with you, so check against the notes |

  Each part has:
  - **the point** above, as its one mark point;
  - **3 misconceptions** (`misconceptions.csv`), used as the wrong options. They are real beliefs about AI, kept **similar in length and detail to the correct option** so the answer doesn't stand out. For `ail_how_fabrication`:
    - "It copied a page that was later deleted from the internet"
    - "It searched a source database and picked the wrong entry"
    - "It invents links on purpose when it can't find an answer"
  - **a one-line `intuition`**, used in the feedback ("why").
- No exam weight. Importance is fixed at `literacy.importance`. All AI-literacy parts are left out of course levers, candidates, search, course reviews, coverage warnings and the course tree in progress (they get their own section, F).
- The existing learner model tracks them: decay, spacing and levels as for any part.

## B. Labels
`this_message` gets:
- `request_type`: `concept`, `research` (a factual or current question about the world), `homework` or `other`;
- `question_features`, for `research` only: which of `concept`, `context`, `asks_sources` and `asks_reasoning` the question shows;
- `source_conflict`, a boolean: the student reports that a link failed or didn't say what was claimed;
- `web_access`, a boolean: whether the chatbot can search the web in this chat. The chatbot sets it on research turns;
- `asks_recent`, a boolean, for `research` only: the question is about recent data or events;
- `pushback_changed`, a boolean: the student challenged the previous answer and the chatbot changed it.

Migration `009_exchange_request.sql` adds `request_type`, `question_features`, `source_conflict`, `web_access`, `asks_recent` and `pushback_changed` columns to `exchange_log` (events, so they are replayed). `source_conflict` also sets the existing `conflict_flagged`.

`concept` and `homework` follow the existing plan and never get literacy tasks. `other` gets an empty plan.

## C. Evidence
- **Ask, on every research question:** type `ail_question` on `ail_ask`, score = features present / 4.
- **Verify:** from the student's reply to a verify task, scored by the ticks they produced (`points_met`, letters from `score_next`). Type `ail_task` on `ail_verify`.
- **Unprompted checking:** a student who reports checking a claim without being asked sends `answer.type = ail_unprompted` on `ail_verify`, ticked the same way. It has a lower slip, so it counts more. Every research turn's `score_next` includes `ail_verify`'s ticks, so this can be scored on the next turn.
- **How AI works:** type `ail_how` on the `ail_how_*` part, scored 1 or 0 from the multiple-choice letter (G). A wrong pick activates that misconception.
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
| developing | Ask: name the one feature the question lacks ("Your question has no time period."). Verify: one tip ("Check figures against the publisher, not a news story about them.") | Ask: "Rewrite your question adding a time period." No rewrite is modelled for them. Verify: "Which claim above would you check first, and where?" |
| secure | credit what they did: "You asked for sources; that's why these are traceable." | a spot-check only every `literacy.secure_every` research turns: "Check one figure and tell me if it matches." Other turns get the feedback line only |

At secure, a task comes when the student's total research-question count is a multiple of `literacy.secure_every`. The count comes from `exchange_log`, so it survives a restart. (A count since the last task wouldn't work: a finished Ask task leaves no `ail_task` row to count from.)

### Not ignorable, never a barrier
- The task is saved as pending in `issued_plan.plan_json` (`literacy: {skill, part_id, followups, waited}`). It never becomes the course's pending question.
- **Not done in the next message:** answer the new message as usual. When the plan doesn't already end in a question, it adds `reask`, which re-asks the pending task in one line (the same move that re-asks a pending question, step 05c). A reply never ends in two questions.
- **Waiting:** when the plan already ends in a course question, the task waits. After `literacy.max_waits` replies waiting, it takes the next reply's question slot in place of the course question, never a how-AI-works check's slot. The course resumes after.
- **Still not done after `literacy.max_followups` re-asks:** record `ail_task` with score 0 on that skill's part, and drop the task.
- **Expiry:** a new task replaces it, and a new session drops it with no score. Only a task that was re-asked and then ignored scores 0.
- **A skipped course check:** when a course check loses its slot (to a literacy re-ask or a how-AI-works check), that point stays unchecked (`check_due` in `points`). The next reply asks its check only, without teaching the point again.
- **Bad links:** when `source_conflict` is set, a `source_conflict` step comes first: tell the student that's exactly what checking is for, and correct the claim. If they reported the ticks, they are scored as for any verify task.
- **Fatigue:** no task while the student is fatigued (04c). The answer still comes with sources.

## G. How-AI-works checks
A one-question check on how chatbots work, asked at the moment one has just failed.

**Triggers**, each for one part. When several fire in one turn, the order is fabrication, agreement, confidence, cutoff. A self-correction counts as `confidence` only without `source_conflict`.

| trigger | part |
|---|---|
| `source_conflict` | `ail_how_fabrication` |
| `conflict_flagged` (the chatbot corrects itself) | `ail_how_confidence` |
| `request_type = research`, `asks_recent = true` and `web_access = false` | `ail_how_cutoff` |
| `pushback_changed` | `ail_how_agreement` |

**The plan:**
- **First, the moment is handled as usual:** correct the claim (`source_conflict`), own the mistake (self-correction), or answer the question.
- **Then `ask_mcq` with `purpose = how_ai_works`** **(stop)** is added as the last step, for the part matching the trigger. The server builds and shuffles it as in 05d: the point plus the part's 3 misconceptions, lettered `A`–`D`, with the map stored in `issued_plan.plan_json` (`mcq`). The student answers with a letter (`answer.type = mcq`, `answer.choice`) and the server scores it as `ail_how`.
- **Limits:**
  - at most one how-AI-works check per reply;
  - at most one per part per session;
  - none while fatigued;
  - at `levels.secure`, only every `literacy.how_secure_every` triggers for that part.
- **Priority:** the check wins over a literacy task and over the plan's own course question, because the moment is rare and it's happening now. The literacy task waits; a skipped course check comes alone in the next reply (`check_due`).
- **Not ignorable, as for literacy tasks:** the check is saved as pending (`how` in `issued_plan`), re-asked in the next reply with the same options and letter map (`reask`), up to `literacy.max_followups` times, then recorded as `ail_how` with score 0.
- **The letter map after a re-ask:** kept only when the re-asked question is itself multiple choice. After any other re-ask, a stray letter isn't scored against a question already answered.
- **Feedback after the answer:** one line. Name the misconception if they picked one, then the part's `intuition` line. Then back to what they were doing.

All trigger counts and per-session limits come from `exchange_log`, `evidence_log` and `issued_plan`, so they survive a restart and replay in a rebuild.

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
`get_my_progress` adds an `ai_literacy` section with three skills:
- **Ask** and **Verify**: the level of each part;
- **How AI works**: the rollup of its parts, with the misconceptions about AI the student still holds (active ones);
- the trend in question features: the share of research questions showing each feature over the last `progress.trend_days`, against before, as up, down or steady.

## Settings
```toml
[literacy]                 # AI-literacy coaching (step 05e)
secure_every = 3           # at secure, a task every this many research turns
max_followups = 1          # re-asks of an ignored task before it scores 0
max_waits = 2              # replies a task waits behind a course question before it takes the question slot
ask_min_features = 2       # fewer features than this: coach the question (Ask), else Verify
importance = 0.5           # fixed importance of the AI-literacy parts
how_secure_every = 3       # at secure, a how-AI-works check every this many triggers

[bkt.evidence]
ail_question = { slip = 0.15, guess = 0.20 }
ail_task = { slip = 0.10, guess = 0.15 }
ail_unprompted = { slip = 0.05, guess = 0.10 }
ail_how = { slip = 0.10, guess = 0.25 }   # 4-option multiple choice
```

## Text
- `text/moves/answer_with_sources.md`, `literacy_task.md` and `source_conflict.md`, each with a `.cue.md`. `reask.md` covers a pending literacy task too. The server instructions stay within `instructions.max_words` (the budget is in `reference/tools-and-context.md`, "The move set").
- `text/literacy/<skill>_<level>.md` (`ask_new`, `ask_developing`, `ask_secure`, `verify_new`, `verify_developing`, `verify_secure`): the feedback and task patterns from the table above.
- `text/moves/ask_mcq.md` gets a `how_ai_works` purpose line: "After handling what just happened, ask this one question about how chatbots work, then return to the student's task." Plus `ask_mcq_how_ai_works.cue.md`.
- No `text/literacy/how_*.md`: the wording lives in the mini pack's points, misconceptions and intuition lines.
- `text/tools/tutor_turn.md` lists the new labels, including `web_access`, `asks_recent` and `pushback_changed`.

## Docs and scripts
- `reference/course-pack-format.md`: `trusted_sources.csv`, the AI-literacy mini pack (including the how-AI-works parts and their misconceptions), validation.
- `reference/tools-and-context.md`: the labels, the research plan, the how-AI-works checks and limits, the new moves and the progress section.
- `reference/learner-model.md`: the AI-literacy parts and evidence types, including `ail_how`. (The "Assessment design" paragraph was written with this plan.)
- `reference/settings.md`: `[literacy]` and the new evidence types.
- `reference/database.md`: migration 009 and the `trusted_source` table.
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
8. `feat(ingest): add how-AI-works parts with misconception options`
9. `feat(context): add live how-AI-works checks on AI failure moments`
10. `chore(scripts): add a research-question run to the MCP check`

Added after review:

11. `fix(context): give a waiting literacy task the question slot and check a skipped point next`
12. `docs(text): name the missing feature in the developing Ask task`
13. `fix(ingest): shorten the fabrication point to match its options`
14. `chore(scripts): check a fatigued student and a waiting literacy task`

Commits 8 and 9 come after the research plan and follow-ups (4 and 5), which the `cutoff` trigger, the priority rule and the re-ask build on. Commit 9 also adds How AI works to the progress section and the `how_ai_works` text for `ask_mcq`.

## Done when (by hand, no tests yet)
- **A research question from a new student** gets `answer_with_sources`, then a `literacy_task` with one feedback line and one task.
- **Ignoring the task** gets one `reask`, then a recorded `ail_task` score of 0.
- **A task behind course questions** waits `literacy.max_waits` replies, then takes the question slot; the skipped course check comes in the next reply.
- **A task never re-asked** expires at session end with no score.
- **Answering a verify task** raises `ail_verify`.
- **A well-phrased question** raises `ail_ask`.
- **At secure level,** the task appears only every `secure_every` research turns.
- **Course questions** (`request_type = concept`) never get literacy tasks.
- **`source_conflict` set:** the reply corrects the claim, then gives an `ask_mcq` on `ail_how_fabrication` with 4 shuffled options. A correct letter raises the part. A wrong one activates the picked misconception.
- **Ignored how-AI-works check:** one `reask`, then a recorded `ail_how` score of 0.
- **Limits:** a second failure of the same type in the same session gets no second check.
- **Fatigue:** a fatigued student gets the correction but no check and no literacy task (a throwaway fatigued student in `check_mcp`).
- **Cutoff:** fires only when `asks_recent = true` and `web_access = false`.
- **Options:** all four options for each how-AI-works part are similar in length (check by eye in the pack).
- `rebuild` gives identical state.
