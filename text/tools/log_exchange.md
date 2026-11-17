Call this after every answer about the course. It returns at once; the student's record is updated in the background.

Label the exchange honestly:
- node_ids: the parts or concepts the exchange was about (ids from get_learning_context).
- question_depth: surface (what is it), mechanism (how or why it works), transfer (applying it somewhere new).
- engagement: passive (read your answer), active (asked or answered something), constructive (produced their own reasoning).
- offloading: true if the student asked you to do the work for them instead of trying.
- support_given: worked_example, hint, explain_back or none.
- choice_taken: what the student chose when offered: try_first, hint, just_show_me or none.
- misconception_ids: misconceptions the student showed this turn.
- conflict_flagged: true if the notes disagreed with each other or with you.

evidence: send it only when the student actually produced an answer or explanation in this turn. One item per part: {part_id, type, score, misconception_ids}. Score it from 0 to 1 against the notes and mark points from get_learning_context: 1 means every mark point is there, 0 means none. Use type prequestion for an answer to a pre-question (score 1 or 0, with the misconception id they picked), explain_back for an explanation in their own words, review for a review question, and past_question for a past-paper question. Never send evidence for your own explanation, or for an answer the student copied from the chat.

If the result is {"ok": false}, fix the field named in the error and call again.
