CREATE TABLE course (id TEXT PRIMARY KEY, name TEXT NOT NULL, exam_board TEXT, spec_code TEXT, spec_version TEXT, extra TEXT);
CREATE TABLE exam_paper (id TEXT PRIMARY KEY, course_id TEXT, name TEXT, date TEXT, node_ids TEXT, extra TEXT);
CREATE TABLE source (id TEXT PRIMARY KEY, course_id TEXT, type TEXT NOT NULL, title TEXT, edition TEXT, reference TEXT, notes TEXT, extra TEXT);

-- every content table below also has: status, flag, updated_by, updated_at, extra
CREATE TABLE node (id TEXT PRIMARY KEY, course_id TEXT NOT NULL, parent_id TEXT, level TEXT NOT NULL, name TEXT NOT NULL,
  aliases TEXT DEFAULT '', spec_ref TEXT DEFAULT '', part_type TEXT, description TEXT NOT NULL, source_ids TEXT DEFAULT '',
  extraction_confidence REAL DEFAULT 1.0,
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
