-- Map links from get_my_progress (decision 0026). A 'link' row is a single-use token the chatbot shares; opening it swaps
-- it once for a 'session' row the browser keeps as its bearer. Only the SHA-256 of either token is stored, never the token,
-- and both expire. The student_id column means delete_student and export_student cover this table without listing it.
CREATE TABLE web_link (token_hash TEXT PRIMARY KEY, student_id TEXT NOT NULL, kind TEXT NOT NULL CHECK (kind IN ('link', 'session')),
  expires_at TEXT NOT NULL, used_at TEXT);
CREATE INDEX idx_web_link_expires ON web_link(expires_at);
