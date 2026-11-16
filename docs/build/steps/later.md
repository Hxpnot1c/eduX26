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

#### Level-marked questions (9, 15 and 25 marks)
1. The chatbot places the answer in a **level** using the level descriptors in `mark_scheme_items` (`kind = level`).
2. **It never gives a numeric mark.** A specific mark within a level needs examiner judgement.
3. **Every level comes with the one specific step to reach the next level,** taken from the next level's descriptor. Example: "Level 3. To reach Level 4, your evaluation needs a supported judgement."

   **Why:** grades alone lead to lower achievement and motivation than comments (Koenka et al., 2021, meta-analysis, school students). Grades with comments gave the best motivational effects in a randomised study of 12–15 year olds (Koenka, 2020).
4. It also returns a **readiness checklist**, each item met or not, with one line of why:
   - command word followed (did "evaluate" actually evaluate?)
   - indicative content covered
   - chain of reasoning complete
   - evaluation with a supported judgement
   - conclusion follows
5. **Evidence:**
   - Each checklist item scores as evidence on the parts it touches, via `mark_scheme_items.node_ids`.
   - The level as a whole scores `level / max_level` on the question's parts.
6. **Evaluation task:** a teacher (or the team) levels 10–20 answers independently, and the results are compared with the chatbot's. Report exact agreement and within-one-level agreement, labelled as a small sample, in the evaluation section of the README.

#### Text
- `text/checks/level.md`
- `text/checks/points.md`

### 08 Tests (`build/08-tests`)
pytest for:
- validation errors
- weights
- each learner rule
- rebuild giving the same state
- context assembly per profile
- tool round-trips through the MCP client

Add CI (GitHub Actions) once tests exist.

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

## Extras (only if time allows)
- Automated extraction from the specification, papers and textbook into a draft pack.
- Other exam boards and subjects.
- Embeddings alongside FTS for note search.
- OAuth instead of keys.
- Hosting and Postgres.
- A real safeguarding detector and the escalation route.
- A browser extension for chatbots without connectors.
