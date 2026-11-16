-- Forgetting runs from the last time the student got a part right, not from when they last saw it.
-- clock_start: when the current decay began (a correct answer resets it; exposure moves it a little);
--   NULL until the first correct answer, because nothing learnt means nothing to forget.
-- last_correct: the last correct evidence on the part.
-- exchanges_since_evidence: exchanges on the part since its last evidence (for the "untested" review rule).
ALTER TABLE part_state ADD COLUMN clock_start TEXT;
ALTER TABLE part_state ADD COLUMN last_correct TEXT;
ALTER TABLE part_state ADD COLUMN exchanges_since_evidence INTEGER NOT NULL DEFAULT 0;
