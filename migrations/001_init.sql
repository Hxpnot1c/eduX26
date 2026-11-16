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
-- check_log is added in a later migration together with checks (see steps/later.md)

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
