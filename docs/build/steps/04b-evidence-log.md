# Step 04b: Evidence log

**Branch:** `build/04b-evidence-log`
**Read first:** `../reference/design-for-change.md` (events first), `../reference/learner-model.md`, `../reference/database.md` (learner.db)

## Goal
Make evidence an event. In the base, nothing produced evidence: `p_known` only moved through exchange nudges, so nothing left "new", the forgetting clock never started and no scheduled review appeared. Evidence also bypassed the event log, so `rebuild_state` couldn't replay it. Fix this before step 05.

## Work
- Migration `003_evidence_log.sql`: an append-only `evidence_log`. One row per part: `id, student_id, ts, part_id, evidence_type` (a key of `[bkt.evidence]`), `score` (0–1), `origin` (`chat` now, `check` later), `exchange_id` (nullable), `check_id` (nullable), `misconception_ids`, `protocol`, `settings_hash`.
- A score counts as correct when `score >= bkt.correct_share`. Wrong evidence that carries misconception ids activates them, as exchanges do.
- **Immediate recall:** performance straight after teaching overstates learning. Chat evidence on a part within `[evidence] immediate_window_minutes` of an exchange on that part with `support_given` = `worked_example` or `hint` is applied as type `immediate` (`[bkt.evidence] immediate`). Evidence later in the session, or in a later session, uses its own type. The stored type stays as sent, so the rule is re-applied on rebuild.
- `learner.record_exchange` takes an optional evidence list of `{part_id, type, score, misconception_ids?}`.
  - It writes the exchange row, then the evidence rows, all with the same `ts`.
  - The worker applies the exchange, then each piece of evidence.
  - Concept ids in evidence expand to their parts, with the score unchanged.
- `learner.record_evidence(...)`: evidence with no exchange, for demo seeding and later checks.
- `rebuild_state` replays `exchange_log` and `evidence_log` merged in order of (`ts`, exchanges before evidence, `id`). Rebuilding gives exactly the same state as live application.
- CLI: `log` gains a repeatable `--evidence part_id:type:score`, and a new `evidence` subcommand (`--student --part --type --score [--ts] [--misconceptions]`).
- `settings.toml`: `nudges.depth.surface = 1.0`. Asking a basic question shouldn't lower the estimate; evidence does that work now.

## Commits
1. `docs: plan evidence log step and update references`
2. `feat(db): add evidence log migration`
3. `feat(learner): record and apply chat evidence with immediate-recall discount`
4. `feat(learner): replay evidence in rebuild`
5. `feat(cli): record evidence by hand`
6. `fix(settings): stop penalising surface questions`

## Done when
Checked by hand with `example-mini`:
- A student with 5 exchanges on `ped_formula`, then correct `explain_back` evidence the next day, reaches "developing". The forgetting clock starts and a `scheduled` review appears.
- The same correct evidence given 5 minutes after a `worked_example` exchange raises `p_known` noticeably less (immediate).
- Wrong evidence with a misconception id activates the misconception. Later correct evidence clears it.
- `rebuild` gives identical state with both logs.
