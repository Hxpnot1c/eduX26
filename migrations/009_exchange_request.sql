-- What the student's message asked for, and the AI-failure moments (step 05e). Events, so rebuild replays them.
ALTER TABLE exchange_log ADD COLUMN request_type TEXT;                                -- concept / research / homework / other
ALTER TABLE exchange_log ADD COLUMN question_features TEXT DEFAULT '';                -- research only: concept;context;asks_sources;asks_reasoning
ALTER TABLE exchange_log ADD COLUMN source_conflict INTEGER NOT NULL DEFAULT 0;       -- a link failed or didn't say what was claimed
ALTER TABLE exchange_log ADD COLUMN web_access INTEGER;                               -- research only: can the chatbot search the web (null: not said)
ALTER TABLE exchange_log ADD COLUMN asks_recent INTEGER NOT NULL DEFAULT 0;           -- research only: about recent data or events
ALTER TABLE exchange_log ADD COLUMN pushback_changed INTEGER NOT NULL DEFAULT 0;      -- the chatbot changed its answer after pushback
