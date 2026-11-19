Call this when the student asks how they are doing or what to work on next.

Returns:
- tree: each topic and concept with the student's level (new, developing, secure); set include_parts to true to see every part. A part can also be taught_in_class (covered in class, not yet checked) or needs_review (they got it right before and it is fading: suggest a quick review, not a re-teach).
- levers: the parts where work pays off most (important and not yet secure).
- weak_links: pairs of related ideas where one side is still new.
- reviews_due: what is due for review.
- trends: how their use of the chatbot is changing: deeper questions, their own reasoning, and how often they ask to be shown answers.
- ai_literacy: how well they ask a chatbot precise questions (ask), check its claims (verify) and understand how chatbots work (how_ai_works, with the wrong ideas they still hold), each with the evidence behind its level (evidence.checks over evidence.over_days), how many tasks they skipped (skipped never lowers a level), and which question features they use more or less than before. It is formative: say each level with its evidence and that it is practice feedback, not a grade, e.g. "Verify: developing, from 4 checks over 2 weeks".

- map_url (only if the server has a web address): a link to the student's own map and progress page. It works once and expires after map_url_expires_minutes. Share it when they ask about their progress or their map, and say it works once and soon expires; if it has expired, call again for a new one. Don't repeat it unprompted. It is not their key: never ask for or share their key.

Explain it in plain words and suggest one next step. Don't read out the numbers.
