-- The one point a multiple-choice question asked (check, re-check, prereq, review; step 05d follow-ups).
-- Null for open answers that cover several points, for intuition questions and for rows written before this.
ALTER TABLE evidence_log ADD COLUMN point_id TEXT;
