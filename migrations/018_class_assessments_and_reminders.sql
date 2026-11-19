-- Class assessments and reminders (step 05u). A test or assignment can now belong to a class (set by a teacher) as
-- well as to one student; exactly one of student_id and class_id is set. Profile, not events: a rebuild uses the rows as
-- they are now. A student's reminders can be switched off.
CREATE TABLE student_assessment_new (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, class_id TEXT,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,                -- homework / class_test / mock / written_assignment
  date TEXT NOT NULL,                -- YYYY-MM-DD
  part_ids TEXT NOT NULL,            -- JSON list of the parts it covers
  created_at TEXT NOT NULL,
  CHECK ((student_id IS NULL) <> (class_id IS NULL)));
INSERT INTO student_assessment_new (id, student_id, class_id, name, kind, date, part_ids, created_at)
  SELECT id, student_id, NULL, name, kind, date, part_ids, created_at FROM student_assessment;
DROP TABLE student_assessment;
ALTER TABLE student_assessment_new RENAME TO student_assessment;
CREATE INDEX idx_student_assessment_student ON student_assessment(student_id, date);
CREATE INDEX idx_student_assessment_class ON student_assessment(class_id, date);
ALTER TABLE student_profile ADD COLUMN reminders INTEGER NOT NULL DEFAULT 1;
