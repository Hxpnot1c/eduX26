-- Per-session cache of the learner offsets (step 05r). Derived, not events: filled in session order, cleared on
-- rebuild, deleted with the student, and dropped whenever it could be stale (an out-of-order event, a change of
-- coverage, other settings). It holds nothing that cannot be recomputed from the event logs.
CREATE TABLE learner_offset_cache (
  student_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  settings_hash TEXT NOT NULL,        -- the cache is used only under the settings it was computed with
  learn_state TEXT,                   -- learning-rate offset: the running state at this session's boundary (JSON)
  learn_offset REAL, learn_n INTEGER,
  covered_offset REAL, covered_n INTEGER,        -- starting offsets for the session that began at session_id
  uncovered_offset REAL, uncovered_n INTEGER,
  PRIMARY KEY (student_id, session_id));
