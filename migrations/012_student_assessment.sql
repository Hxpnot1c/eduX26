-- A student's own upcoming assessments (priorities): profile, not events, like exam_date_override. A rebuild uses
-- the assessments as they are now. Past ones are ignored everywhere and stay in the table.
CREATE TABLE student_assessment (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,                -- homework / class_test / mock
  date TEXT NOT NULL,                -- YYYY-MM-DD
  part_ids TEXT NOT NULL,            -- JSON list of the parts it covers
  created_at TEXT NOT NULL);
CREATE INDEX idx_student_assessment_student ON student_assessment(student_id, date);
