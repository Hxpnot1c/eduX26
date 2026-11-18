# Step 05x: Data handling

Branch `build/data-handling`, from `main` once step 05w is merged. Audit item C6; Vishnu's decision of 18 November. Comes before step [05r](05r-learner-cache.md), because a cache is another place a student's data lives.

## What
- **Opaque ids.** A new student's id is `s-<8 hex>`, never made from a name. A display name, if given, is stored in `student.display_name` only.
- **Hashed keys.** Only the SHA-256 of a key is stored; the key is shown once, when the student is created. A student from before this step keeps a plaintext key until their first request, which replaces it with a hash. The demo students' keys are kept in `demo-keys.json` in the data folder (git-ignored) so the demo script can print them and `seed-demo --reset` keeps them. OAuth stays held.
- **Delete.** `delete-student --student <id> --yes` removes every row about a student from every table with a `student_id` column, found from the schema.
- **Export.** `export-student --student <id> [--out file]` writes everything stored about a student as JSON, never the key or its hash.
- **Retention.** `retention.call_log_days = 30` and `retention.after_leaving_days = 90` (judgement calls, starting values; schools set their own). `leave-student` marks a student as having left; `purge` deletes old call-log rows and students who left long enough ago.
- **No message text.** The dead `STORE_PROMPTS` setting and the `prompt_text` column are removed.

## Why
See [decision 0011](../../decisions/0011-data-handling.md): minimisation, storage limitation and security (UK GDPR Art. 5 and 32, ICO guidance), and the audit's finding that nothing could be deleted, exported or expired.

## Files
- `migrations/014_data_handling.sql` (the next free number): rebuilds `student` with `key_hash`, a nullable `key` and `left_on`; drops `exchange_log.prompt_text`.
- `edux/learner.py`: `key_hash`, `add_student`, `student_by_key`, `get_student`, `delete_student`, `export_student`, `leave_student`, `purge`; the `prompt_text` parameter and `STORE_PROMPTS` removed.
- `edux/demo.py`: demo keys in `demo-keys.json`; `remove_students` uses `delete_student`, so it also clears `call_log`.
- `edux/cli.py`: `delete-student`, `export-student`, `leave-student`, `purge`.
- `edux/settings.py`, `settings.toml`: `[retention]`.
- `scripts/check_mcp.py`: reads demo keys from `demo-keys.json`.
- `tests/test_data_handling.py` (13 tests): opaque ids; hashed keys; a legacy key still works once and is then hashed; the migration keeps an existing key; delete leaves no row in any table; other students untouched and a rebuild identical; export holds every table and never the key; purge by call-log age and by leaving date; no message-text column.
- Docs: `reference/database.md`, `reference/settings.md`, `reference/tools-and-context.md`, `README.md`, `.env.example`.

## Done when
- A test shows delete leaves no row about the student anywhere.
- `check_mcp` passes, `seed-demo --reset` keeps the demo keys, and rebuild is identical.
- The migration number is reported in the pull request: **014**.

## Not in this step
OAuth or header tokens (held), a student-facing "what is recorded" page, and the DPIA notes (a separate docs pull request).
