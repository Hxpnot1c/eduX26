-- Confidence ratings (step 05z, audit item C7). An event, like evidence_log: the student's answer to "how sure are you?"
-- for one answer to a check. It is never an input to what the model thinks they know (p_known): it feeds only the calibration
-- line the student can see. level is guess, fairly_sure, certain, or skipped (asked, no answer: no penalty).
CREATE TABLE confidence_log (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, evidence_id INTEGER NOT NULL,
  ts TEXT NOT NULL, level TEXT NOT NULL);
CREATE INDEX idx_confidence_student ON confidence_log(student_id, ts);
