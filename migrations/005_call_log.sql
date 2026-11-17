-- Operational, not an event: one row per MCP tool call, for timing. rebuild_state ignores it.
CREATE TABLE call_log (id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,                  -- when the call started, ISO UTC to the millisecond
  student_id TEXT,                   -- null when the key didn't resolve
  tool TEXT NOT NULL,
  ms REAL NOT NULL,                  -- server time for the call
  result_chars INTEGER NOT NULL,     -- size of the JSON result
  ok INTEGER NOT NULL,               -- 0 when the tool raised or returned ok: false
  error TEXT);
CREATE INDEX idx_call_log_student ON call_log(student_id, ts);
