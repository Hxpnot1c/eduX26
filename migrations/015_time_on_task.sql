-- Time on task (step 05s): the timing of an answer, stored so the rapid-guess flag can be replayed, and the flag itself.
-- latency_s: seconds since the student's previous exchange in the session (NULL for the first); answer_words: the
-- word count of the student's message (a count, never the text); question_words: words in the question being answered.
ALTER TABLE exchange_log ADD COLUMN latency_s REAL;
ALTER TABLE exchange_log ADD COLUMN answer_words INTEGER;
ALTER TABLE exchange_log ADD COLUMN question_words INTEGER;
ALTER TABLE evidence_derived ADD COLUMN rapid INTEGER NOT NULL DEFAULT 0;
