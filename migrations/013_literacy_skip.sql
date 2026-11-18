-- An AI-literacy task or how-AI-works check left unanswered after its re-ask (research fixes, 0003). It is missing,
-- not wrong: no evidence row is written; this event only counts the skips shown beside the level. Append-only.
CREATE TABLE literacy_skip (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, ts TEXT NOT NULL,
  part_id TEXT NOT NULL);                -- the skill's part (ail_ask, ail_verify) or the how-AI-works part
CREATE INDEX idx_literacy_skip_student ON literacy_skip(student_id, part_id);
