# Settings

Every number the system uses lives in `settings.toml`. Everything about what the chatbot is given lives in `context.toml` and `text/`. Code never hard-codes either. Both files are hashed together into `settings_hash`, which is stored on every event (see `design-for-change.md`).

`edux/settings.py` loads both files once at startup into typed dataclasses and fails loudly on a missing or mistyped key.

## settings.toml

```toml
protocol = "v0.2"          # bump when the meaning of labels or scoring changes (v0.2: labels describe the student's message; scores come from points met)

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
extend = { slip = 0.10, guess = 0.10 }      # an answer to a harder, extending question
immediate = { slip = 0.10, guess = 0.30 }   # chat evidence straight after a worked example or hint
ail_question = { slip = 0.15, guess = 0.20 }     # a research question, scored by its features (step 05e)
ail_task = { slip = 0.10, guess = 0.15 }         # the answer to a verify task, or 0 for an ignored task
ail_unprompted = { slip = 0.05, guess = 0.10 }   # checking a claim without being asked: counts more
mcq_check = { slip = 0.10, guess = 0.25 }   # a multiple-choice check on one point (step 05d); guess about 1 in 4 options
ail_question = { slip = 0.15, guess = 0.20 }    # question features of a research question (step 05e)
ail_task = { slip = 0.10, guess = 0.15 }        # a literacy task done when asked
ail_unprompted = { slip = 0.05, guess = 0.10 }  # checking a claim without being asked: counts more

[nudges]                   # small odds multipliers from an ordinary exchange
depth = { surface = 1.0, mechanism = 1.0, transfer = 1.1 }   # a basic question doesn't lower the estimate; evidence does that
engagement = { passive = 1.0, active = 1.0, constructive = 1.05 }
concept_tag_strength = 0.5 # a nudge on a concept tag reaches its parts at this strength

[evidence]
immediate_window_minutes = 30   # evidence this soon after a worked example or hint on the part counts as `immediate`

[offloading]               # removed in step 05d: "just show me" no longer discounts later evidence
guess_after = 0.40         # guess used for the next checks after "just show me"
checks_discounted = 2

[decay]
base_half_life_days = 2.0
on_success = 2.0           # half-life multiplier after correct evidence
on_failure = 0.5           # multiplier after incorrect evidence
min_half_life_days = 1.0
seen_refresh = 0.2         # an exchange moves the forgetting clock this share of the way to now; a correct answer resets it

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
untested_after = 4         # this many exchanges on a part with no check
untested_below = 0.5       # and p_now below this → queue an "untested" review

[support]                  # which support level to suggest, by p_now
worked_example_below = 0.40
hint_below = 0.75          # at or above: ask them to explain it back
extend_from = 0.40         # developing and above get higher-order questions mixed in
procedural_types = ["calculation", "diagram"]   # these part types get the procedural hint; others the conceptual one

[teaching_note]
max_words = 200
exam_close_days = 14
approach_min_records = 2   # past approaches needed before "what worked before" is shown

[prequestion]              # a question asked before teaching an untaught part (the intuition MCQ from step 05d)
enabled = true
max_options = 4            # moves to mcq.max_options in step 05d
min_distractors = 2        # moves to mcq.min_distractors in step 05d
exchange_weight = 0.5      # an exchange on the part counts this much towards coverage
full_weight_at = 3.0       # coverage at which a pre-question counts as full evidence

[literacy]                 # AI-literacy coaching (step 05e)
secure_every = 3           # at secure, a task every this many research questions (others: the feedback line only)
max_followups = 1          # re-asks of an ignored literacy task before it scores 0
ask_min_features = 2       # fewer question features than this: coach the question (Ask), else Verify
importance = 0.5           # fixed importance of the AI-literacy parts (they have no exam weight)

[session]                  # sessions, fatigue and getting stuck, derived from events
gap_minutes = 30           # a longer gap starts a new session
fatigue_min_minutes = 25   # no fatigue call before this
fatigue_window = 4         # pieces of evidence in the rolling mean
fatigue_threshold = -0.25  # mean surprise at or below this = doing worse than expected
fatigue_min_parts = 2      # the drop must span at least this many parts
fatigue_slip_add = 0.15    # extra slip while fatigued
slip_cap = 0.40
signal_window = 6          # exchanges used for the supporting signals
stuck_attempts = 3         # open answers on a part before it can count as stuck (MCQ checks: same point missed twice)
stuck_below = 0.5          # and their mean score below this
quick_parts = 3            # parts offered for a short burst when fatigued
pattern_min_sessions = 3   # sessions with a fatigue onset before study_pattern is shown

[difficulty]               # optional teacher-set difficulty per node (0 easy – 1 hard), inherited by parts
default = 0.5              # used when no node above the part has one
prior_shift = 0.15         # starting p_known moves down (hard) or up (easy) by up to this much
half_life_shift = 0.5      # starting half-life shrinks (hard) or grows (easy) by up to this share
w_cross = 0.0              # share of the cross-student difficulty estimate (off until there is data)

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

[progress]                 # get_my_progress (step 05)
levers = 5                 # parts listed as the biggest levers: highest importance x (1 - p_now)
weak_links = 5             # confusable or causal pairs with one side weak
trend_days = 14            # AI-literacy trends compare this many recent days with everything before
trend_min_change = 0.05    # a share must move at least this much to count as up or down

[blocks]                   # how each turn ranks what goes into each context block (step 05)
review_link_boost = 0.5    # a due review linked to the current focus counts this much more
review_importance_floor = 0.1   # added to importance so unweighted parts still rank by how overdue they are
confusable_mixup = 1.0     # a misconception this student has had on either side adds this
confusable_mention = 1.0   # the message mentions the other part: adds this x its relevance
causal_mention = 1.0       # the message mentions the other end of a causal link: adds this x its relevance
causal_cues = ["affect", "effect", "cause", "impact", "lead", "result", "consequence", "happen", "why", "because"]
exam_w_marks = 0.5         # exam_relevance: share from marks at stake
exam_w_closeness = 0.3     # share from how close the paper's exam is
exam_w_command = 0.2       # share from the question's command word appearing in the message
exam_horizon_days = 365    # an exam this far off or further adds nothing for closeness
exam_cues = ["exam", "paper", "marks", "question"]   # exam_relevance is sent only when the message has one of these or a command word (step 05c)

[style]                    # how tutor_turn asks the chatbot to write (step 05b)
max_words = 120            # default length of a reply's explanation (MCQ options don't count); the student's profile answer_length overrides

[results]                  # size of a tutor_turn result (step 05c)
max_chars = 2400           # about 600 tokens; over this, reference blocks are dropped, then the call is logged as over budget

[instructions]             # the MCP server instructions, sent once per chat (step 05c)
max_words = 900            # server_instructions.md + style.md + every move section; over this is a startup error
max_sentences = 2          # per move section; longer is a startup warning
cue_max_words = 15         # per cue; longer is a startup warning

[points]                   # point-by-point teaching (step 05d)
max_words = 80             # words of explanation per teach_point (MCQ options don't count)
reteach_limit = 1          # re-teaches of a missed point before moving on
warn_min = 2               # validation warning below this many points per part
warn_max = 4               # and above this many

[mcq]                      # server-built multiple-choice questions (step 05d)
max_options = 4            # correct option plus up to this many minus one misconceptions
min_distractors = 2        # fewer misconceptions: the chatbot may write one extra distractor; also a validation warning
# one intuition question per part, whatever the answer; teaching follows it

[literacy]                 # AI-literacy coaching (step 05e)
secure_every = 3           # at secure, a task every this many research turns
max_followups = 1          # re-asks of an ignored task before it scores 0
max_followups = 1          # re-asks of an ignored literacy task before it scores 0
ask_min_features = 2       # fewer question features than this: coach the question (Ask), else Verify
importance = 0.5           # fixed importance of the AI-literacy parts
```

## context.toml

Decides which blocks each turn is built from, in what order, and how long each may be. `tutor_turn` chooses its plan from the plan-input blocks (`focus`, `prequestion`, `support`, `session`, `reviews_due`) and sends the rest as `reference`; `teaching_note` is only shown by the `context` CLI command. A **profile** is a named set of blocks plus `plan`: with `plan = false` (the `minimal` comparison profile) `tutor_turn` returns no plan. Students use the default unless their `student.profile` says otherwise, which allows A/B comparisons without code changes.

```toml
default_profile = "full"

[profiles.full]
blocks = ["focus", "prequestion", "support", "session", "weak_prerequisites", "anchor", "confusables", "causal",
          "misconceptions", "notes", "exam_relevance", "reviews_due", "teaching_note"]
plan = true                # tutor_turn chooses a plan from the blocks; the rest go to reference

[profiles.minimal]         # for comparison: notes only, no plan
blocks = ["focus", "notes"]
plan = false

[limits]
notes = 3                  # notes per focus part
terms = 30                 # course terms in data.terms, sent once per plan (step 05c)
key_wording = 4
weak_prerequisites = 2
confusables = 2
misconceptions = 2
causal = 2
exam_questions = 2
reviews_due = 3
candidates = 3             # candidate parts when the message is ambiguous

# Reference blocks each move uses, in priority order (step 05c). Keys are the move plus its variant (teach_<level> and
# review_<mode> until 05d, ask_mcq_<purpose> from 05d); a bare move's table covers its variants. `misconceptions` means the
# step part's held ones only. The result carries the union over the plan's steps; over the result budget, blocks are dropped
# from the end. A move with no table gets no reference.
[moves.feedback]           # also holds a held misconception's correction (correct_misconception before 05c)
reference = ["misconceptions"]
[moves.reteach]            # missing points, or the whole part through the anchor when stuck
reference = ["notes", "anchor"]
[moves.show]
reference = ["notes"]
[moves.teach]              # all teach levels until 05d; teach_point from 05d
reference = ["notes", "misconceptions"]
[moves.teach_point]
reference = ["notes", "misconceptions"]
[moves.extend]
reference = ["causal"]
[moves.answer_brief]
reference = ["notes"]
[moves.review_transfer]    # until 05d
reference = ["notes"]
# prequestion, check_prereq, step_back, review_recall, reask, offer_stop, ask_which; from 05d ask_mcq and explain_back;
# from 05e answer_with_sources, literacy_task, source_conflict: none
```

`exam_relevance` is not listed per move: it is added when the message mentions an exam (`blocks.exam_cues`) or a command word from the part's questions.

```toml
[watch_for]                # moves that ask the student something also get the part's watch-for misconceptions (step 05c)
moves = ["ask_mcq", "explain_back", "extend", "reask"]   # step 05c: ["prequestion", "check_prereq", "step_back", "teach", "review", "extend", "reteach", "reask"]
```

Watch-for misconceptions are sent as `id` and `wrong_idea` only, so the chatbot can tag one the student's answer shows. Over the result budget they are dropped last.

## text/

Plain markdown files read at startup. Changing wording never touches code.

| file | used for |
|---|---|
| `server_instructions.md` | the MCP server instructions |
| `tools/<tool>.md` | each tool's description (`tutor_turn`: at most 8 lines) |
| `style.md` | reply length, interests and formatting rules, appended to the server instructions |
| `moves/<move>.md` | what each move does, at most 2 sentences, with `{field}` placeholders filled from the step's `data`. Sent once, as a section of the server instructions (step 05c). The final set is the 14 moves in `tools-and-context.md` ("The move set"): `ask_mcq`, `teach_point`, `show`, `explain_back`, `extend`, `feedback`, `reteach`, `answer_brief`, `reask`, `offer_stop`, `ask_which`, `answer_with_sources`, `literacy_task`, `source_conflict`. Step 05c has the interim 17 listed there |
| `moves/<key>.cue.md` | one line, at most 15 words, sent with every step of that move (step 05c). The key adds the variant (`ask_mcq_<purpose>`, `teach_<level>`, `review_<mode>`), falling back to the bare move |
| `literacy/<skill>_<level>.md` | feedback and task patterns for `ask` and `verify` at `new`, `developing` and `secure` (step 05e) |
| `format/<client>.md` | formatting for maths, money and diagrams per chatbot (`claude`, `chatgpt`, `gemini`, `default`), returned in `style.format` |
| `progress/study_pattern.md` | the study-pattern line in `get_my_progress` (`{minutes}` is filled in) |
| `checks/<kind>.md` | marking instructions for `points` and `level` checks (step 07) |
| `prompts/<prompt>.md` | the text of the `review_due` and `check_me` prompts (`{topic}` is filled in) |
| `teaching_note.md` | the teaching-note template with `{placeholders}` (debugging output only) |
| `chatbot_setup.md` | the text students paste into their chatbot's custom instructions |
