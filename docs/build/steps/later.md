# Later

Build these once the base (steps 01–06) works end to end. Each one is its own branch and pull request, following the same rules.

## Next, in order

### 07 Checks (`build/07-checks`)
- Migration `002_check_log.sql`: `check_log(id, student_id, ts, check_type, part_ids, question_id, score, max_score, result, protocol, settings_hash)`.
- `start_check(node_ids?, type?)`:
  - Picks a past question for the part when one exists and its marks are within `checks.max_question_marks_in_chat`; otherwise uses our mark points.
  - Types: `past_question`, `explain_back`, `link` (score 0–5 with a knowledge-integration rubric) and `find_error`, at most at the `find_error_free_rate`.
  - Returns the question and the rubric for the chatbot to mark against.
- `submit_check(check_id, score, misconception_ids?)`: writes the event and calls `apply_evidence`.
- Approach records get `next_check_correct` filled.
- Add the `[checks]` section to settings.toml.
- Fill in `learner.misconception_link_signal`: when students fail a check on X with a misconception that belongs to Y, strengthen the X–Y link. Set `link_weight.w_misconception` above 0 once there is enough data.

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
