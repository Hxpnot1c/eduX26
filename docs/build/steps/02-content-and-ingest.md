# Step 02: Content and ingest

**Branch:** `build/02-content-ingest`
**Read first:** `../reference/course-pack-format.md`, `../reference/database.md` (content.db)

## Goal
Turn a course-pack folder into `content.db`: validate it, load it, compute weights, apply teacher feedback, and print a report.

## Work
- `ingest/registry.py`: every file and column from the format reference, with type, required flag, enum values and default. One place to add or change a column.
- `python -m ingest.cli templates <dir>`: writes header-only CSVs from the registry.
- `ingest/validate.py`: every error and warning in the format reference. Collect them all rather than stopping at the first. Print the cycle path for prerequisite cycles.
- `ingest/load.py`:
  1. Recreate `content.db` from `content_schema.sql`.
  2. Insert rows. Unknown columns go to `extra` as JSON. Parse `;` lists.
  3. Fill `question_node` and `id_map`.
  4. Build `note_fts` from summary, key points and key wording.
  5. Compute `node_weight` (exam_weight, dependents, importance).
  6. Apply `teacher_feedback/<course>.csv` in `ts` order, recording each action in `teacher_feedback` with applied and message.
  7. Write `load_info` and print the report: counts per table, warnings, flagged rows, rows with `extraction_confidence < 0.5`, feedback not applied.
- `python -m ingest.cli validate <pack>` and `python -m ingest.cli load <pack>`.
- `coursepacks/example-mini/`: a small hand-made pack (two topics, ~8 parts, every edge type, two synthetic past-paper questions labelled `synthetic`) that loads with no errors.

## Commits
1. `feat(ingest): add column registry and template command`
2. `feat(ingest): validate course packs`
3. `feat(ingest): load course pack into content database`
4. `feat(ingest): compute exam weight, dependents and importance`
5. `feat(ingest): apply teacher feedback overlay`
6. `feat(ingest): print load report`
7. `feat: add example-mini course pack`

## Done when
- `python -m ingest.cli load coursepacks/example-mini` prints a report with no errors.
- Breaking the pack on purpose shows the right error. Try a prerequisite cycle, an analogous edge with no note, and a mark point with no source.
- A teacher-feedback `reject` row hides that node from queries.
- `node_weight` values sum sensibly.
