-- Whether a piece of evidence was applied as immediate recall (personal-learning-rate), so the per-student
-- learning-rate offset can leave it out. Derived: `python -m edux.cli rebuild` fills it for existing rows.
ALTER TABLE evidence_derived ADD COLUMN immediate INTEGER NOT NULL DEFAULT 0;
