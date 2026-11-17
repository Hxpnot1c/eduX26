-- Operational, not an event: the last plan tutor_turn issued to each student, so the next turn knows what was
-- asked and what support was given without the chatbot repeating it. rebuild_state ignores it.
CREATE TABLE issued_plan (student_id TEXT PRIMARY KEY,
  ts TEXT NOT NULL,
  plan_json TEXT NOT NULL);          -- {"plan": [steps], "focus": [part ids], "corrected": [misconception ids this session]}
