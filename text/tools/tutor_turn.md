Call this at the start of every reply, before writing anything (research questions about the world too). It records the student's message and answer, then returns the plan for your reply.
- message: the student's message, word for word.
- this_message: honest labels for the student's message; choice is skip_point when they say "I know this". request_type is research for a factual or current question about the world, with its question_features, web_access (can you search the web here) and asks_recent (about recent data or events). Set source_conflict when they say a link failed or didn't say what was claimed, and pushback_changed when they challenged your last answer and you are changing it.
- node_ids: optional part ids from the last plan or focus, when the message continues that topic.
- answer: only when the message answers what you asked last turn (see the server instructions); for a multiple-choice question, type mcq and choice, the letter picked. Never score it yourself.
- client: your name, e.g. claude, chatgpt or gemini.
Returns plan (steps to do in order; each move is explained in the server instructions), score_next (points to tick in their next answer), reference and focus.
