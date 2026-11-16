# Step 04: Learner model

**Branch:** `build/04-learner-model`
**Read first:** `../reference/learner-model.md`, `../reference/database.md` (learner.db), `../reference/design-for-change.md` (events first)

## Goal
`learner.db`, append-only events, and every rule in the learner-model reference. State is always rebuildable from events.

## Work
- `edux/db.py`: a migrations runner that applies `migrations/NNN_*.sql` in order and records `schema_version`; and `ATTACH` of content.db.
- `edux/learner.py`:
  - `record_exchange(...)`: writes the event with `protocol` and `settings_hash`, then calls `apply_exchange`.
  - `apply_exchange(event)`: nudges, offloading, misconception activation, overconfidence, `last_seen`.
  - `apply_evidence(student, part, evidence_type, correct)`: the BKT update, half-life, propagation, misconception clearing and scheduling. Implement it now even though checks come later; the base does not call it yet.
  - `p_now(...)`, `level(...)`, `rollup(node_id)`.
  - `due_reviews(student, limit)` and `candidates(student, limit)`.
  - `support_level(p_now)`, `anchor(student, part)` and `approaches(student, part)`.
  - `rebuild_state(student_id)` and `rebuild_all()`.
- `edux/cli.py`:
  - `add-student --name --course`: prints the key.
  - `rebuild [--student]`.
  - `state --student [--node]`: prints parts with `p_now`, level and due date.
- A background worker (a queue and a thread) so events are written synchronously and applied asynchronously.

## Commits
1. `feat(db): add learner database migrations runner`
2. `feat(learner): record exchange events with protocol and settings hash`
3. `feat(learner): apply exchange nudges, offloading and misconceptions`
4. `feat(learner): add evidence update, decay and prerequisite propagation`
5. `feat(learner): schedule reviews from exam dates`
6. `feat(learner): choose candidates, support level and anchor`
7. `feat(learner): rebuild state from events`
8. `feat(cli): add student, state and rebuild commands`

## Done when
- After logging a handful of exchanges by hand, `state` shows sensible changes.
- Running `rebuild` gives identical state.
- Changing a number in `settings.toml` and rebuilding changes the state as expected.
