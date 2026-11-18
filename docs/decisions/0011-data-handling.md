# 0011. Opaque ids, hashed keys, and delete, export and retention

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Vishnu (decided 18 November; confirm retention periods with each school)
- **Pull request:** #54
- **Step:** [05x](../build/steps/05x-data-handling.md) (audit item C6)

## Context

The audit found that Synapse could not delete, export or expire a student's data. Every table was append-only and kept for ever. Student ids were slugs of the real name plus four hex characters, printed to the console and stored in the call log. The student's key was stored in plain text, so anyone who could read the database could use every link. `demo.remove_students` left `call_log` rows behind. A `STORE_PROMPTS` setting existed for storing students' messages, but nothing wrote them.

## Decision

1. **Opaque ids** (`s-<8 hex>`); the display name lives in one place only.
2. **Hashed keys:** SHA-256 of the key, a 128-bit random secret, so a plain hash is enough. A student from before the migration keeps a plaintext key until their first request, then it is hashed. Demo keys are kept in `demo-keys.json` in the git-ignored data folder.
3. **`delete-student`, `export-student`, `leave-student`, `purge`,** covering every table with a `student_id` column, found from the schema, so a table added later (the learner cache, class tables) is covered automatically.
4. **Retention settings,** `call_log_days = 30` and `after_leaving_days = 90`, both **judgement calls, starting values** for schools to change.
5. **Remove `STORE_PROMPTS`** and the `prompt_text` column: message text is never stored.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| UK GDPR Art. 5(1)(c) and (e); ICO storage-limitation guidance | Collect only what is needed; erase or anonymise data once there is no clear reason to keep it; there are no fixed periods. | Law and regulator guidance | Does not give numbers. |
| ICO, "Edtech examined" audit findings (2026) | About 70% of audited ed-tech providers did not specify retention periods or what happens at their end. | Regulator audit | Secondary summary read. |
| UK GDPR Art. 17 (erasure) and Art. 20 (portability) | A person can ask for their data to be erased or exported. | Law | Applies to the controller; the school is likely the controller. |
| UK GDPR Art. 32; RFC 9110 §17.9; OWASP session management | Security must suit the risk; secrets in URLs are exposed to logs and history; store a hash of an identifier. | Law and standards | Hashing protects the database, not the link: the key is still in the connector URL (OAuth stays held). |
| Project research, Q8 | Chat logs 30 to 90 days, assessment records for the academic year plus a short appeal window. | Our own proposal; not regulatory | The two periods here are starting values, not requirements. |

## Alternatives considered

- **Keep keys in plain text** for easier support. Rejected: a read-only leak of the database would give access to every student.
- **Salted, slow hashing (bcrypt, Argon2).** Unnecessary for a 128-bit random key and slower on every request.
- **Delete by listing tables** in code. Rejected: it already missed `call_log` once.
- **A longer or shorter retention default.** Schools set their own; 30 and 90 days follow the research proposal and are labelled as judgement calls.

## Consequences

- A student's data can be removed or exported in one command, and expires on a schedule.
- Existing connector URLs keep working (legacy keys are matched once and hashed). Ids of existing students do not change.
- The demo is unaffected: demo ids are fixed and its keys are kept in `demo-keys.json`.
- Event sourcing and deletion: deleting a student deletes their events, so there is nothing to replay for them and other students' state is unchanged (tested).
- Migration **014**. No change to the instruction word count.

## Verification

`tests/test_data_handling.py` (13 tests); `scripts/check_mcp.py` passes with the demo keys read from `demo-keys.json`; rebuild identical.

## What would change our mind

A school needing a different retention period (change the settings), or a requirement to keep an audit trail of deletions (add a minimal log without personal data).
