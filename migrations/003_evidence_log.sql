-- Evidence is an event: one append-only row per part, from chat now and from checks later.
-- evidence_type is stored as sent; rules such as the immediate-recall discount are applied when replaying.
CREATE TABLE evidence_log (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, ts TEXT NOT NULL,
  part_id TEXT NOT NULL,             -- one row per part
  evidence_type TEXT NOT NULL,       -- a key of [bkt.evidence], as sent
  score REAL NOT NULL,               -- 0–1; correct when score >= bkt.correct_share
  origin TEXT NOT NULL,              -- chat / check
  exchange_id INTEGER,               -- the exchange_log row it came with, if any
  check_id TEXT,                     -- the issued check, if any (step 07)
  misconception_ids TEXT DEFAULT '',
  protocol TEXT NOT NULL, settings_hash TEXT NOT NULL);
CREATE INDEX idx_evidence_student ON evidence_log(student_id, ts);
