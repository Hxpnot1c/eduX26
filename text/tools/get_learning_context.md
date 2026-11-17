Call this before answering any course question. It returns what to teach and how, for this student and this message.

- message: the student's message, word for word.
- node_ids: optional; the part or concept ids you think the message is about (from an earlier focus block). Leave empty to let the server find them.
- client: optional; your name, e.g. claude, chatgpt or gemini.

Returns blocks, each present only when it has something to say:
- focus: the parts this message is about with the student's level (new, developing, secure), or candidates to ask about when it is ambiguous.
- prequestion: a multiple-choice question to ask before teaching, with the correct idea and misconception options.
- support: how much help to give (worked_example, hint, explain_back), extend: true when to add a harder question, and how.
- session: the student seems tired, or is stuck on a part.
- weak_prerequisites, anchor, confusables, causal: related parts to check, build on, contrast or connect.
- active_misconceptions: wrong ideas to correct.
- notes and mark_points: what to teach from, and what answers are scored against.
- exam_relevance: past-paper questions and papers on these parts.
- reviews_due: parts to revisit, each with a mode (recall or transfer).
- teaching_note: a short summary of all of this.
