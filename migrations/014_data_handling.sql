-- Data handling (step 05x): student keys are stored hashed, a student can be marked as having left (so their
-- data can be deleted after the retention period), and the unused prompt_text column is dropped.
CREATE TABLE student_new (id TEXT PRIMARY KEY, key_hash TEXT UNIQUE, key TEXT UNIQUE, display_name TEXT, course_id TEXT,
  profile TEXT, created TEXT NOT NULL, left_on TEXT);
-- Existing students keep their plaintext key until their first request, which replaces it with a hash.
INSERT INTO student_new (id, key_hash, key, display_name, course_id, profile, created, left_on)
  SELECT id, NULL, key, display_name, course_id, profile, created, NULL FROM student;
DROP TABLE student;
ALTER TABLE student_new RENAME TO student;
ALTER TABLE exchange_log DROP COLUMN prompt_text;
