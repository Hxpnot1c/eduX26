-- A tool result over results.max_chars after dropping every reference block (step 05c). Operational only.
ALTER TABLE call_log ADD COLUMN over_budget INTEGER NOT NULL DEFAULT 0;
