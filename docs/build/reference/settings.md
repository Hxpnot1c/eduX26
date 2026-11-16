# Settings

Every number the system uses lives in `settings.toml`. Everything about what the chatbot is given lives in `context.toml` and `text/`. Code never hard-codes either. Both files are hashed together into `settings_hash`, which is stored on every event (see `design-for-change.md`).

`edux/settings.py` loads both files once at startup into typed dataclasses and fails loudly on a missing or mistyped key.

## settings.toml

```toml
protocol = "v0.1"          # bump when the meaning of labels or scoring changes

[levels]                   # part levels shown to students
new = 0.40                 # p_known below this = new
secure = 0.75              # at or above this = secure; between = developing

[bkt]                      # Bayesian knowledge tracing
prior = 0.30               # p_known before any evidence
learn_rate = 0.10          # chance of learning from one piece of evidence
correct_share = 0.67       # share of a link/check score that counts as "correct"

[bkt.evidence]             # slip / guess per evidence type
explain_back = { slip = 0.10, guess = 0.10 }
past_question = { slip = 0.10, guess = 0.10 }
link = { slip = 0.10, guess = 0.10 }
review = { slip = 0.10, guess = 0.15 }
find_error = { slip = 0.15, guess = 0.25 }
prequestion = { slip = 0.20, guess = 0.20 }
mcq = { slip = 0.10, guess = 0.25 }

[nudges]                   # small odds multipliers from an ordinary exchange
depth = { surface = 0.9, mechanism = 1.0, transfer = 1.1 }
engagement = { passive = 1.0, active = 1.0, constructive = 1.05 }
concept_tag_strength = 0.5 # a nudge on a concept tag reaches its parts at this strength

[offloading]
guess_after = 0.40         # guess used for the next checks after "just show me"
checks_discounted = 2

[decay]
base_half_life_days = 2.0
on_success = 2.0           # half-life multiplier after correct evidence
on_failure = 0.5           # multiplier after incorrect evidence
min_half_life_days = 1.0

[propagation]
prereq_boost = 0.20        # share of a gain passed one hop to prerequisites
queue_band = [0.30, 0.75]  # parts in this band are candidates to teach next

[importance]
w_exam = 0.6
w_dependents = 0.4

[authority]                # higher wins when sources disagree
mark_scheme = 6
specification = 5
examiner_report = 4
question_paper = 3
textbook = 2
ours = 1

[scheduling]               # review gap as a share of days left to the exam
share_far = 0.25           # > 60 days to the exam
share_mid = 0.15           # 14–60 days
share_near = 0.08          # < 14 days
min_gap_days = 1
just_show_me_gap_days = 1.5
max_reviews_per_reply = 3
overconfident_after = 4    # this many exchanges on a part with no check
overconfident_below = 0.5  # and p_known below this → queue a review

[support]                  # which support level to suggest, by p_now
worked_example_below = 0.40
hint_below = 0.75          # at or above: ask them to explain it back

[teaching_note]
max_words = 200
exam_close_days = 14
approach_min_records = 2   # past approaches needed before "what worked before" is shown

[link_weight]              # how strongly two linked nodes are related, computed on load
base = 0.3                 # weight of a link with no evidence; evidence raises it towards 1
w_exam = 0.7               # share from past-paper questions that test both ends
w_material = 0.3           # share from teaching materials that cover both ends in one section
w_misconception = 0.0      # cross-student misconception signal, read from learner.db (off until checks exist)
material_source_types = ["textbook", "teacher"]
suggest_min_questions = 2  # questions co-testing two unlinked parts before a link is suggested

[resolve]                  # turning a student's message into the parts it is about
name_boost = 2.0           # a match on a node's name or alias counts this many times a match in a note
candidate_ratio = 0.8      # other results scoring at least this share of the top one are "close": ask which
```

## context.toml

Decides which blocks `get_learning_context` returns, in what order, and how long each may be. A **profile** is a named set of blocks. Students use the default unless their `student.profile` says otherwise, which allows A/B comparisons without code changes.

```toml
default_profile = "full"

[profiles.full]
blocks = ["focus", "support", "weak_prerequisites", "anchor", "confusables",
          "active_misconceptions", "notes", "exam_relevance", "reviews_due", "teaching_note"]

[profiles.minimal]         # for comparison: notes only
blocks = ["focus", "notes"]

[limits]
notes = 3                  # notes per focus part
key_wording = 4
weak_prerequisites = 2
confusables = 2
misconceptions = 2
reviews_due = 3
candidates = 3             # candidate parts when the message is ambiguous
```

## text/

Plain markdown files read at startup. Changing wording never touches code.

| file | used for |
|---|---|
| `server_instructions.md` | the MCP server instructions |
| `tools/<tool>.md` | each tool's description |
| `support/<level>.md` | the support instruction sent with each support level |
| `teaching_note.md` | the teaching-note template with `{placeholders}` |
| `chatbot_setup.md` | the text students paste into their chatbot's custom instructions |
