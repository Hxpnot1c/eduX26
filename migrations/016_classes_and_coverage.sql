-- Classes and coverage (step 05q). Coverage is profile, not events: a row counts for an event only when taught_on is
-- on or before the event's date, so a rebuild gives the same state.
CREATE TABLE class (id TEXT PRIMARY KEY, name TEXT NOT NULL, course_pack TEXT, created TEXT NOT NULL);
ALTER TABLE student ADD COLUMN class_id TEXT;
-- Which parts of the spec a class has been taught, and when. A row on a node marks all its parts.
CREATE TABLE class_coverage (class_id TEXT NOT NULL, node_id TEXT NOT NULL, taught_on TEXT NOT NULL, set_by TEXT NOT NULL,
  PRIMARY KEY (class_id, node_id));
-- The same for one student who says what they covered in class (a fallback for a class with no teacher record).
CREATE TABLE student_coverage (student_id TEXT NOT NULL, node_id TEXT NOT NULL, taught_on TEXT NOT NULL, set_by TEXT NOT NULL,
  PRIMARY KEY (student_id, node_id));
