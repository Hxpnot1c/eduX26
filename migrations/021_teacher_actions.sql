-- What teachers change through the web pages (step 09, decision 0023): one row per change, so a class's coverage and
-- tests can be traced to who set them. teacher_id is the id only, never a name; it is replaced by 'former teacher' if
-- the teacher is deleted, so the trail outlives the person without keeping their identity.
CREATE TABLE teacher_action (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, teacher_id TEXT NOT NULL, class_id TEXT NOT NULL,
  action TEXT NOT NULL, detail TEXT NOT NULL);
CREATE INDEX idx_teacher_action_class ON teacher_action(class_id, ts);
