Call this when the student tells you something to remember about how they want to learn.

- interests: things they care about, used to choose examples (e.g. "football, cooking").
- exam_date_override: the date of their exam as YYYY-MM-DD if it differs from the course's paper dates; an empty string clears it.
- answer_length: roughly how many words they want in an answer. Set it whenever they ask for shorter or more detailed replies; their choice then wins over the per-step lengths.
- add_assessment: an upcoming homework, class_test or mock of their own, with its date and the topics it covers. Read back the matched topics and part count so they can confirm; if nothing matched, show them the topics returned and ask which.
- remove_assessment: the id of one to remove (the profile lists them).
- covered_in_class: topics their class has been taught, and about when, when their teacher has not recorded it. Read back the matched topics; if nothing matched, show the topics returned and ask which. It applies to this student only.

Only send the fields that changed. Returns the updated profile.
