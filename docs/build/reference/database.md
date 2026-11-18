# Databases

Two SQLite files (see `design-for-change.md`). Use WAL mode; each thread opens its own connection. Queries that serve content ignore rows with `status = 'rejected'`. Enum values are checked by `ingest/registry.py`, not by SQL constraints.

## content.db (`edux/content_schema.sql`, recreated on every load)

```sql
CREATE TABLE course (id TEXT PRIMARY KEY, name TEXT NOT NULL, exam_board TEXT, spec_code TEXT, spec_version TEXT, extra TEXT);
CREATE TABLE exam_paper (id TEXT PRIMARY KEY, course_id TEXT, name TEXT, date TEXT, node_ids TEXT, extra TEXT);
CREATE TABLE source (id TEXT PRIMARY KEY, course_id TEXT, type TEXT NOT NULL, title TEXT, edition TEXT, reference TEXT, notes TEXT, extra TEXT);

-- every content table below also has: status, flag, updated_by, updated_at, extra
CREATE TABLE node (id TEXT PRIMARY KEY, course_id TEXT NOT NULL, parent_id TEXT, level TEXT NOT NULL, name TEXT NOT NULL,
  aliases TEXT DEFAULT '', spec_ref TEXT DEFAULT '', part_type TEXT, description TEXT NOT NULL, source_ids TEXT DEFAULT '',
  extraction_confidence REAL DEFAULT 1.0, difficulty REAL,
  intuition TEXT DEFAULT '',         -- parts only (step 05d)
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE edge (from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL, note TEXT DEFAULT '', confidence REAL DEFAULT 0.8,
  source_ids TEXT DEFAULT '', teach_use TEXT DEFAULT 'none',   -- intuition / contrast / none (step 05d)
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT,
  PRIMARY KEY (from_id, to_id, type));
CREATE TABLE note (id TEXT PRIMARY KEY, node_id TEXT NOT NULL, summary TEXT NOT NULL, key_points TEXT DEFAULT '', key_wording TEXT DEFAULT '',
  source_id TEXT, location TEXT,
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE VIRTUAL TABLE note_fts USING fts5(id UNINDEXED, body, tokenize = 'porter');
CREATE VIRTUAL TABLE node_fts USING fts5(id UNINDEXED, name, aliases, description, tokenize = 'porter');
CREATE TABLE misconception (id TEXT PRIMARY KEY, node_id TEXT NOT NULL, wrong_idea TEXT NOT NULL, correction TEXT NOT NULL, source_ids TEXT DEFAULT '',
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE mark_point (id TEXT PRIMARY KEY, node_id TEXT NOT NULL, point TEXT NOT NULL, exemplar TEXT DEFAULT '', source_ids TEXT NOT NULL,
  "order" INTEGER,                  -- within the part (step 05d)
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE past_paper (id TEXT PRIMARY KEY, course_id TEXT, exam_paper_id TEXT, series TEXT, question_source_id TEXT,
  mark_scheme_source_id TEXT, examiner_report_source_id TEXT, extra TEXT);
CREATE TABLE question (id TEXT PRIMARY KEY, past_paper_id TEXT NOT NULL, number TEXT, marks INTEGER NOT NULL, command_word TEXT, format TEXT,
  assessment_objectives TEXT, node_ids TEXT NOT NULL, summary TEXT,
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE mark_scheme_item (id TEXT PRIMARY KEY, question_id TEXT NOT NULL, kind TEXT, marks INTEGER, level INTEGER, text TEXT NOT NULL, node_ids TEXT DEFAULT '',
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE trusted_source (id TEXT PRIMARY KEY, node_id TEXT NOT NULL, name TEXT NOT NULL, url TEXT NOT NULL, what_for TEXT NOT NULL,
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);  -- step 05e
CREATE TABLE question_node (question_id TEXT, node_id TEXT, PRIMARY KEY (question_id, node_id));  -- filled from node_ids for joins
CREATE TABLE node_weight (node_id TEXT PRIMARY KEY, exam_weight REAL, dependents INTEGER, importance REAL);
CREATE TABLE edge_weight (from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL,
  exam_questions INTEGER NOT NULL DEFAULT 0, exam_marks REAL NOT NULL DEFAULT 0, material_count INTEGER NOT NULL DEFAULT 0,
  computed REAL, teacher_weight REAL, weight REAL,   -- weight = teacher_weight if set, else computed
  PRIMARY KEY (from_id, to_id, type));
CREATE TABLE trusted_source (id TEXT PRIMARY KEY, node_id TEXT NOT NULL, name TEXT NOT NULL, url TEXT NOT NULL,
  what_for TEXT DEFAULT '',          -- step 05e
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE id_map (old_id TEXT PRIMARY KEY, new_id TEXT NOT NULL);
CREATE TABLE teacher_feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, teacher TEXT, tbl TEXT, target_id TEXT, action TEXT,
  field TEXT, value TEXT, note TEXT, applied INTEGER, message TEXT);
CREATE TABLE load_info (loaded_at TEXT, course_id TEXT, pack_path TEXT, summary TEXT);

CREATE INDEX idx_node_parent ON node(parent_id);
CREATE INDEX idx_edge_to ON edge(to_id, type);
CREATE INDEX idx_edge_from ON edge(from_id, type);
CREATE INDEX idx_qnode_node ON question_node(node_id);
```

## learner.db (`migrations/001_init.sql`; later changes as new numbered files)

```sql
CREATE TABLE schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);

-- who
CREATE TABLE student (id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL, display_name TEXT, course_id TEXT,
  profile TEXT,                      -- context profile name; NULL = default from context.toml
  created TEXT NOT NULL);
CREATE TABLE student_profile (student_id TEXT PRIMARY KEY, interests TEXT DEFAULT '', exam_date_override TEXT, answer_length INTEGER);

-- events (append-only; the source of truth)
CREATE TABLE exchange_log (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, ts TEXT NOT NULL, client TEXT,
  node_ids TEXT NOT NULL, question_depth TEXT, engagement TEXT, offloading INTEGER NOT NULL DEFAULT 0,
  support_given TEXT, choice_taken TEXT, misconception_ids TEXT DEFAULT '', conflict_flagged INTEGER NOT NULL DEFAULT 0,
  protocol TEXT NOT NULL,            -- e.g. v0.1/full
  settings_hash TEXT NOT NULL,
  prompt_text TEXT);                 -- only when STORE_PROMPTS=1
-- evidence_log is added by migration 003 (below)

-- derived (rebuilt from events by learner.rebuild_state)
CREATE TABLE part_state (student_id TEXT NOT NULL, part_id TEXT NOT NULL, p_known REAL NOT NULL, half_life_days REAL NOT NULL,
  last_seen TEXT NOT NULL, n_evidence INTEGER NOT NULL DEFAULT 0, offload_left INTEGER NOT NULL DEFAULT 0, was_secure INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (student_id, part_id));
CREATE TABLE student_misconception (student_id TEXT NOT NULL, misconception_id TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, last_seen TEXT NOT NULL,
  PRIMARY KEY (student_id, misconception_id));
CREATE TABLE approach_record (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, part_id TEXT NOT NULL, approach TEXT NOT NULL,
  ts TEXT NOT NULL, next_check_correct INTEGER);
CREATE TABLE review_queue (student_id TEXT NOT NULL, part_id TEXT NOT NULL, due TEXT NOT NULL, reason TEXT NOT NULL,
  PRIMARY KEY (student_id, part_id));

CREATE INDEX idx_exchange_student ON exchange_log(student_id, ts);
```

`migrations/002_part_state_clock.sql` adds to `part_state`:
- `clock_start`: when the current decay began (see `learner-model.md`)
- `last_correct`: the last correct evidence on the part
- `exchanges_since_evidence`: exchanges since its last evidence, for the `untested` review rule

`migrations/003_evidence_log.sql` adds the second event log:

```sql
CREATE TABLE evidence_log (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, ts TEXT NOT NULL,
  part_id TEXT NOT NULL,             -- one row per part
  evidence_type TEXT NOT NULL,       -- a key of [bkt.evidence], as sent
  score REAL NOT NULL,               -- 0–1; correct when score >= bkt.correct_share
  origin TEXT NOT NULL,              -- chat / check
  exchange_id INTEGER,               -- the exchange_log row it came with, if any
  check_id TEXT,                     -- the issued check, if any (step 07)
  misconception_ids TEXT DEFAULT '',
  protocol TEXT NOT NULL, settings_hash TEXT NOT NULL);
CREATE INDEX idx_evidence_student ON evidence_log(student_id, ts);
```

`migrations/004_session_signals.sql` (step 04c) adds a **derived** table, cleared and refilled by `rebuild_state`:

```sql
CREATE TABLE evidence_derived (evidence_id INTEGER PRIMARY KEY, student_id TEXT NOT NULL, session_id TEXT NOT NULL,
  p_before REAL NOT NULL,            -- the part's p_now just before this evidence
  surprise REAL NOT NULL,            -- weight × (score − p_before)
  weight REAL NOT NULL DEFAULT 1,    -- 1, or the coverage weight of a pre-question (0 = diagnostic only)
  fatigued INTEGER NOT NULL DEFAULT 0);
CREATE INDEX idx_evidence_derived_session ON evidence_derived(student_id, session_id);
```

Two **operational** tables (step 05b) follow. They are not events and not derived: `rebuild_state` neither replays nor clears them.

`migrations/005_call_log.sql` adds one row per MCP tool call, for timing (`python -m edux.cli calls`). The key is never stored:

```sql
CREATE TABLE call_log (id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,                  -- when the call started, ISO UTC to the millisecond
  student_id TEXT,                   -- null when the key didn't resolve
  tool TEXT NOT NULL,
  ms REAL NOT NULL,                  -- server time for the call
  result_chars INTEGER NOT NULL,     -- size of the JSON result
  ok INTEGER NOT NULL,               -- 0 when the tool raised or returned ok: false
  error TEXT);
CREATE INDEX idx_call_log_student ON call_log(student_id, ts);
```

`migrations/006_issued_plan.sql` keeps the last plan `tutor_turn` issued to each student. The next turn reads what was asked from it, and the support given (`support_given` on the exchange), so the chatbot doesn't repeat them. `seed-demo --reset` clears it for the demo students.

```sql
CREATE TABLE issued_plan (student_id TEXT PRIMARY KEY,
  ts TEXT NOT NULL,
  plan_json TEXT NOT NULL);          -- {"plan", "focus", "corrected", "offered", "considered"}: carried within a session ("considered": add-on candidates not picked, with values; never sent) ("offered": the offer_choice reasons made; "offered_stop" before engagement-rules)
```

`migrations/007_call_log_budget.sql` (step 05c) adds `over_budget INTEGER NOT NULL DEFAULT 0` to `call_log`: 1 when a result was still over `results.max_chars` after dropping every reference block. `issued_plan.plan_json` also carries `style_sent` (the style last sent, so it is sent again only when it changes) and `pending` (the question last asked, until it is answered). From step 05d it carries `points` (progress through each part's points) and `mcq` (the letter → option map of the last MCQ), and from step 05e `literacy` (the pending literacy task and its follow-ups).

`migrations/008_evidence_point.sql` (05d follow-ups) adds the one point a multiple-choice question asked to `evidence_log`. It is set for checks, re-checks, prerequisite checks (the prerequisite's first point) and reviews, and from step 05e for `ail_how` checks. It stays null for explain-backs and other open answers that cover several points, and for intuition questions. Older rows stay null and replay unchanged.

```sql
ALTER TABLE evidence_log ADD COLUMN point_id TEXT;                 -- a mark_point id, or a note key point id (<note>:k<n>)
```

`migrations/009_exchange_request.sql` (step 05e) adds labels to `exchange_log`. They are events, so rebuild replays them:

```sql
ALTER TABLE exchange_log ADD COLUMN request_type TEXT;              -- concept / research / homework / other
ALTER TABLE exchange_log ADD COLUMN question_features TEXT DEFAULT '';  -- research only: concept;context;asks_sources;asks_reasoning
ALTER TABLE exchange_log ADD COLUMN source_conflict INTEGER NOT NULL DEFAULT 0;  -- a link failed or didn't say what was claimed; also sets conflict_flagged
ALTER TABLE exchange_log ADD COLUMN web_access INTEGER;             -- research only: can the chatbot search the web (null: not said)
ALTER TABLE exchange_log ADD COLUMN asks_recent INTEGER NOT NULL DEFAULT 0;   -- research only: about recent data or events
ALTER TABLE exchange_log ADD COLUMN pushback_changed INTEGER NOT NULL DEFAULT 0;  -- the chatbot changed its answer after pushback
```

`migrations/010_evidence_options.sql` (tune-from-research) adds how many options a multiple-choice question showed. With `bkt.mcq_guess_from_options` its guess is `1 / n_options`. It is null for open answers and for older rows, which keep the type's guess.

```sql
ALTER TABLE evidence_log ADD COLUMN n_options INTEGER;
```

`migrations/011_evidence_immediate.sql` (personal-learning-rate) records in `evidence_derived` whether a piece of evidence was applied as immediate recall, so the per-student learning-rate offset can leave it out. It is derived: `python -m edux.cli rebuild` fills it for existing rows, which start at 0.

```sql
ALTER TABLE evidence_derived ADD COLUMN immediate INTEGER NOT NULL DEFAULT 0;
```

`migrations/012_student_assessment.sql` (priorities) adds the student's own upcoming assessments. They are profile, not events, like `exam_date_override`: a rebuild uses them as they are now. Past ones are ignored everywhere and stay in the table.

```sql
CREATE TABLE student_assessment (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,                -- homework / class_test / mock
  date TEXT NOT NULL,                -- YYYY-MM-DD
  part_ids TEXT NOT NULL,            -- JSON list of the parts it covers
  created_at TEXT NOT NULL);
CREATE INDEX idx_student_assessment_student ON student_assessment(student_id, date);
```
