# Later

Build these once the base (steps 01–06) works end to end. Each one is its own branch and pull request, following the same rules.

## Next, in order

### 07 Checks (`build/07-checks`)
- A migration adding a `check` table for issued checks: `check(id, student_id, ts, check_type, part_ids, question_id, max_score, protocol, settings_hash)`. There is no separate check log: results are evidence.
- `start_check(node_ids?, type?)`:
  - Picks a past question for the part when one exists and its marks are within `checks.max_question_marks_in_chat`; otherwise uses our mark points.
  - Types: `past_question`, `explain_back`, `link` (score 0–5 with a knowledge-integration rubric) and `find_error`, at most at the `find_error_free_rate`.
  - Returns the question and the rubric for the chatbot to mark against.
- `submit_check(check_id, score, misconception_ids?)`: writes the result to `evidence_log` with origin `check` and that `check_id` (one row per part, through `learner.record_evidence`), which applies it.
- Approach records get `next_check_correct` filled.
- Add the `[checks]` section to settings.toml.
- Fill in `learner.misconception_link_signal`: when students give wrong evidence on X with a misconception that belongs to Y, strengthen the X–Y link. Set `link_weight.w_misconception` above 0 once there is enough data.

#### Point-marked questions (e.g. 2–4 mark define, calculate, explain)
- Say which mark points were met and which were missed.
- The score for evidence is the share of mark points met.

#### Level-marked questions (Edexcel's longer data-response and essay questions)
Edexcel 9EC0 mark schemes level these answers in two strands: **KAA** (knowledge, application and analysis) and **evaluation**, each with its own levels.
1. The chatbot places the answer in a **level for each strand separately**, using the level descriptors in `mark_scheme_items` (`kind = level`). A level row gets a `strand` column: `kaa` or `evaluation`.
2. **It never gives a numeric mark.** A specific mark within a level needs examiner judgement.
3. **Each strand's level comes with its own next step,** taken from that strand's next level descriptor. Example: "KAA: Level 3. To reach Level 4, take your chain of reasoning one more step, to the effect on the firm. Evaluation: Level 1. To reach Level 2, weigh up one factor that could change the outcome." A strand already at its top level gets no step.

   **Why:** grades alone lead to lower achievement and motivation than comments (Koenka et al., 2021, meta-analysis, school students). Grades with comments gave the best motivational effects in a randomised study of 12–15 year olds (Koenka, 2020).
4. It also returns a **readiness checklist**, each item met or not, with one line of why:
   - command word followed (did "evaluate" actually evaluate?)
   - indicative content covered
   - chain of reasoning complete
   - evaluation with a supported judgement
   - conclusion follows
5. **Evidence:**
   - Each checklist item scores as evidence on the parts it touches, via `mark_scheme_items.node_ids`.
   - Each strand scores `level / max_level` for that strand on the question's parts, as two separate evidence rows.
6. **Evaluation task:** a teacher (or the team) levels 10–20 answers independently, per strand, and the results are compared with the chatbot's. Report exact agreement and within-one-level agreement for each strand, labelled as a small sample, in the evaluation section of the README.

#### Question templates
`question_templates.csv` in the course pack, one row per template:

| column | meaning |
|---|---|
| source_question_id | the past question it is modelled on |
| node_ids | parts it tests |
| command_word, marks, format | as in `questions.csv` |
| stem | the question in our own words, with `{slots}` |
| slots | allowed values or ranges per slot |
| answer_rule | for calculations, a formula over the slots |
| mark_item_ids | mark-scheme items reused from the source question |

Plus the standard status columns.

- **The server fills the slots,** seeded per student so questions don't repeat, and computes the answer key for calculations. The chatbot never invents a question or an answer when a template exists.
- **Written questions** keep the command word, marks and level descriptors, and change only the context.
- **Fallback:** free generation, labelled "Edexcel-style practice", limited to the part, command word and marks.
- **Edexcel's 1-mark multiple-choice questions** (Section A of Papers 1 and 2) are question templates for `check_mcq` practice (`ask_mcq` with purpose `check` once step 05c's move set lands). Each becomes a template in our own words: a stem and a correct option, with the wrong options mapped to misconceptions where one fits. The server builds, shuffles and scores it as for any check (step 05d).
- **Transfer-mode reviews** use templates when they exist.
- **Templates start as drafts.** Not every template produces questions of equal difficulty (Fu & Choe, 2022: 9 of 23 worked without revision), so teacher approval matters.

#### Text
- `text/checks/level.md`
- `text/checks/points.md`

### 08 Tests (`build/08-tests`)
Started in [step 08](08-tests.md): the harness, settings, learner-model core and the two size gates. The rest of this list is still to do.

pytest for:
- validation errors
- weights
- each learner rule
- rebuild giving the same state
- context assembly per profile
- tool round-trips through the MCP client

**Tricky-message set.** A scripted set of conversations run through the MCP client, each with the plan expected at every turn:
- a question asked instead of an answer (answered briefly, then the same question again);
- an MCQ answered with a letter that wasn't offered, or in words instead of a letter;
- an MCQ answer after the letter map was lost (nothing recorded, question re-asked);
- "I know this" and "just show me" in the middle of a part;
- a switch to another part mid-loop, then back (progress resumes);
- an answer with full point ids, letters, or ids from another part;
- the chatbot correcting itself (`conflict_flagged`);
- a research question in the middle of a part, and an ignored literacy task;
- fatigue or getting stuck in the middle of a part;
- a message that needs a course term the student hasn't met.

CI (GitHub Actions) is done: see `.github/workflows/ci.yml` and step 08.

### 09 Student page (`build/09-student-page`)
A simple read-only page at `/me?key=` showing:
- the tree with levels
- the biggest levers
- reviews due
- AI-literacy trends
- the "Set up my chatbot" copy box

### 10 Teacher view (`build/10-teacher-view`)
- Class-level weak parts and misconceptions only, never chats.
- Content review: list flagged and draft rows with approve, reject and edit, writing to the teacher feedback CSV.

### Priorities, next (after step 05i)
- *(Teachers setting assessments for a whole class: built in step 05u.)*
- Mock marks counted as evidence.
- **Research item: per-type learn rates.** The model has one learn rate for all evidence types, so the value score can't prefer the step a student learns most from (step 05n). Find evidence on whether learning differs by question type before adding per-type rates.
- Learning the `[priorities]` weights from the `considered` logs: a contextual bandit, checked first against old logs (offline evaluation) before it changes any choice.

### Fatigue, next (after step 05s)
- Fit the school's own time-on-task curve, to replace the research average once there's data.
- Per-student persistence, using the same shrinkage approach as the starting offsets. Persistence varies between students (Wu, Debeer et al., 2019).
- A per-student fatigue view for teachers, only behind a DPIA. For now per-student curves are CLI only (`personalisation.md` §5: personal traits are never shown as labels).

### Assessments, next (after step 05u)
- Import assignments from Microsoft Teams Assignments and Google Classroom instead of entering them twice.
- Real calendar reminders. Synapse can only remind in chat, at the start of a session.

### Rename, after the competition
- Rename the internal identifiers (the `edux/` package and imports, `EDUX_*` environment variables, the `edux_ai_literacy` source id) to Synapse in one commit, after the competition. The GitHub repository is already `synapse-eduX26`.

### Diagrams, next (after step 05j)
- Server-drawn diagrams: Synapse draws standard diagrams (supply and demand shifts, a tax wedge, externalities, AD/AS) by rule and returns an image link, for chatbots that can't draw.

## Extras (only if time allows)
- **Investigate activity.** An optional guided research task: ask → predict → AI answer with tagged claims → verify two claims → apply in a paragraph → reflect. It scores the AI-literacy skills from 05e (`ail_ask`, `ail_verify`), plus `think_first`, `apply` and `reflect`.
- Automated extraction from the specification, papers and textbook into a draft pack.
- Other exam boards and subjects.
- Embeddings alongside FTS for note search.
- OAuth instead of keys.
- Hosting and Postgres.
- A browser extension for chatbots without connectors.
