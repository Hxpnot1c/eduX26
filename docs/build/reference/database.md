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
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE edge (from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL, note TEXT DEFAULT '', confidence REAL DEFAULT 0.8,
  source_ids TEXT DEFAULT '',
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
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE past_paper (id TEXT PRIMARY KEY, course_id TEXT, exam_paper_id TEXT, series TEXT, question_source_id TEXT,
  mark_scheme_source_id TEXT, examiner_report_source_id TEXT, extra TEXT);
CREATE TABLE question (id TEXT PRIMARY KEY, past_paper_id TEXT NOT NULL, number TEXT, marks INTEGER NOT NULL, command_word TEXT, format TEXT,
  assessment_objectives TEXT, node_ids TEXT NOT NULL, summary TEXT,
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE mark_scheme_item (id TEXT PRIMARY KEY, question_id TEXT NOT NULL, kind TEXT, marks INTEGER, level INTEGER, text TEXT NOT NULL, node_ids TEXT DEFAULT '',
  status TEXT DEFAULT 'draft', flag TEXT DEFAULT '', updated_by TEXT DEFAULT 'extraction', updated_at TEXT, extra TEXT);
CREATE TABLE question_node (question_id TEXT, node_id TEXT, PRIMARY KEY (question_id, node_id));  -- filled from node_ids for joins
CREATE TABLE node_weight (node_id TEXT PRIMARY KEY, exam_weight REAL, dependents INTEGER, importance REAL);
CREATE TABLE edge_weight (from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL,
  exam_questions INTEGER NOT NULL DEFAULT 0, exam_marks REAL NOT NULL DEFAULT 0, material_count INTEGER NOT NULL DEFAULT 0,
  computed REAL, teacher_weight REAL, weight REAL,   -- weight = teacher_weight if set, else computed
  PRIMARY KEY (from_id, to_id, type));
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
  surprise REAL NOT NULL,            -- score − p_before (scaled by the coverage weight for pre-questions)
  fatigued INTEGER NOT NULL DEFAULT 0);
CREATE INDEX idx_evidence_derived_session ON evidence_derived(student_id, session_id);
```
