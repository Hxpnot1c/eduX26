Call this at the start of every reply about the course, before writing anything. It records the student's message and answer, then returns the plan for your reply.

- message: the student's message, word for word.
- this_message: honest labels for the student's message: question_depth, engagement, and choice (what they chose when you offered try first / hint / just show me; none if nothing was offered).
- node_ids: optional; part ids from the last plan or focus, when the message continues that topic.
- answer: only when the message answers something you asked last turn. part_id is that step's part_id and type its data.answer_type. For a pre-question send correct, and picked_misconception_id if they picked a wrong option. Otherwise send points_met: the ids from score_next of the points they actually produced, in their own words. Never score it yourself.
- client: your name, e.g. claude, chatgpt or gemini.

Returns:
- plan: one or two steps. Do them in order, following each step's text and data, and nothing else.
- score_next: the points to tick in the student's next answer.
- reference: notes, links and exam questions; use them only when they help the current step.
- focus: the parts this turn is about, with the student's level.

If the result is {"ok": false}, fix the field named in the error and call again.
