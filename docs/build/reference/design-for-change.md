# Designing for change

The teaching protocol, the course-pack columns, the tools and the context given to the chatbot will all change during the build as research comes in. These five rules keep those changes cheap. They apply to every step.

## 1. Two databases
- **`content.db`** is rebuilt from the course pack on every load. It never needs migrations: add, rename or drop columns freely.
- **`learner.db`** holds students and their event logs. It changes rarely, and only through numbered migration files in `migrations/` (`001_init.sql`, `002_...`). A `schema_version` table records which have run. Never edit a migration once merged.
- The server opens `learner.db` and attaches `content.db` (`ATTACH DATABASE ... AS content`), so queries can join across both.

## 2. Events first, state rebuilt from them
- `exchange_log` and `evidence_log` are append-only event logs. They hold everything needed to recompute a student's state. Evidence comes from chat (with an exchange) now and from checks later; both go in `evidence_log`.
- `part_state`, `student_misconception`, `approach_record` and `review_queue` are **derived**. `learner.rebuild_state(student_id)` replays that student's events from both logs, in order, through the current scoring functions. `rebuild_all()` does every student.
- Every event row records `protocol` (the `protocol` version from `settings.toml` plus the student's context profile, e.g. `v0.1/full`) and `settings_hash` (the first 8 hex characters of the SHA-256 of `settings.toml` plus `context.toml`). This lets the team see which version of the protocol produced which data.
- After any change to scoring settings, or to which parts exist, run `python -m edux.cli rebuild`.

## 3. One registry for course-pack columns
- `ingest/registry.py` defines every course-pack file once: its columns, types, required flags and allowed values (enums). Edge types, part types, levels, formats and statuses are listed here, not as database `CHECK` constraints.
- Validation, loading, the empty CSV templates (`python -m ingest.cli templates`) and `coursepacks/README.md` are generated from the registry.
- Adding a column is one line in the registry.
- Unknown extra columns in a CSV are kept in a JSON `extra` column on that row instead of being rejected, so extraction can try new columns before the code uses them.

## 4. Thin tools, wording in text files
- Each MCP tool in `edux/server.py` is a short adapter: resolve the student, call one function in `edux/service.py`, return its result. Logic lives in the service layer.
- Tool descriptions, server instructions and labelling rubrics are markdown files in `text/`, loaded at startup. Changing wording never touches Python.
- Change tool outputs by **adding** fields; rename or remove only with a note in the pull request. Chatbots re-read the tool list when they reconnect, so changes reach them without a client update.

## 5. Context built from configured blocks
- `get_learning_context` returns a list of named blocks. Each block is one function in `edux/context_blocks.py` that takes the resolved situation (student, focus, settings) and returns a small dict, or nothing.
- `context.toml` lists the blocks to include, their order and limits (items, words), per **profile**. A profile is a named version of the protocol, e.g. `full` and `minimal`. Each student has a profile (default from `context.toml`).
- The teaching note is a template file, `text/teaching_note.md`, filled from the blocks.

## Ids
Once students have data, never rename a content id. If you must, add a row to `coursepacks/<id>/id_map.csv` (`old_id,new_id`). `rebuild_state` applies the map to events before replaying them.
