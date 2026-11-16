-- Derived from exchange_log and evidence_log; rebuild_state clears and refills it.
-- One row per applied piece of evidence: its session, what the model expected, and whether the session was fatigued.
CREATE TABLE evidence_derived (evidence_id INTEGER PRIMARY KEY, student_id TEXT NOT NULL, session_id TEXT NOT NULL,
  p_before REAL NOT NULL,            -- the part's p_now just before this evidence
  surprise REAL NOT NULL,            -- weight × (score − p_before)
  weight REAL NOT NULL DEFAULT 1,    -- 1, or the coverage weight of a pre-question (0 = diagnostic only)
  fatigued INTEGER NOT NULL DEFAULT 0);
CREATE INDEX idx_evidence_derived_session ON evidence_derived(student_id, session_id);
