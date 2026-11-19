-- Teachers (step 09, decision 0023). A teacher signs in to the web pages with a key, stored only as its SHA-256 like a
-- student's. A teacher sees only the classes assigned to them, and only class-level views (never one student's record).
-- left_on is set when a teacher leaves; the key stops working at once and the row is deleted by purge after
-- retention.after_leaving_days.
CREATE TABLE teacher (id TEXT PRIMARY KEY, name TEXT NOT NULL, key_hash TEXT NOT NULL UNIQUE, created_on TEXT NOT NULL,
  left_on TEXT);
CREATE TABLE teacher_class (teacher_id TEXT NOT NULL, class_id TEXT NOT NULL, PRIMARY KEY (teacher_id, class_id));
