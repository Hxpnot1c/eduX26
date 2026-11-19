# Settings

Every number the system uses lives in `settings.toml`. Everything about what the chatbot is given lives in `context.toml` and `text/`. Code never hard-codes either. Both files are hashed together into `settings_hash`, which is stored on every event (see `design-for-change.md`).

`edux/settings.py` loads both files once at startup into typed dataclasses and fails loudly on a missing or mistyped key.

## settings.toml

```toml
protocol = "v0.4"          # bump when the meaning of labels or scoring changes (v0.2: labels describe the student's message; scores come from points met; v0.3: an exchange alone can't lift a part past nudges.ceiling; v0.4: stale evidence fades towards the part's starting estimate, not to 0, so p_now and every later update read differently)

[levels]                   # part levels shown to students
new = 0.40                 # p_known below this = new
secure = 0.75              # at or above this = secure; between = developing

[bkt]                      # Bayesian knowledge tracing
prior = 0.30               # p_known before any evidence
learn_rate = 0.10          # chance of learning from one piece of evidence; startup check: below 1 - slip/(1 - guess) for every type (learner-model.md)
correct_share = 0.67       # share of a link/check score that counts as "correct"
mcq_guess_from_options = true   # a multiple-choice guess is 1 / the options shown (mcq_check, ail_how, an intuition question; tune-from-research)

[bkt.explain_back_guess]   # judgement call: a complete multi-point answer is far harder to produce by luck
up_to_2 = 0.20             # explain-back guess when the answer needs 1 or 2 mark points
three = 0.15               # 3 mark points
four_plus = 0.10           # 4 or more

[bkt.evidence]             # slip / guess per evidence type
explain_back = { slip = 0.10, guess = 0.20 }    # open answers 0.20 from tune-from-research: one reply can't reach secure
past_question = { slip = 0.10, guess = 0.20 }
link = { slip = 0.10, guess = 0.20 }
review = { slip = 0.10, guess = 0.15 }
find_error = { slip = 0.15, guess = 0.25 }
prequestion = { slip = 0.20, guess = 0.20 }
mcq = { slip = 0.10, guess = 0.25 }
extend = { slip = 0.10, guess = 0.20 }      # an answer to a harder, extending question
immediate = { slip = 0.10, guess = 0.30 }   # chat evidence straight after a worked example or hint; guess is at least the type's own
ail_question = { slip = 0.15, guess = 0.20 }     # a research question, scored by its features (step 05e)
ail_task = { slip = 0.10, guess = 0.15 }         # the answer to a verify task (a reported dead or mismatched source scores 1)
ail_unprompted = { slip = 0.05, guess = 0.10 }   # checking a claim without being asked: counts more
ail_find_error = { slip = 0.15, guess = 0.25 }   # find-the-error practice, on Verify: its own type so it cannot inflate Verify from real moments (decision 0012)
ail_how = { slip = 0.10, guess = 0.25 }          # a how-AI-works check: 4-option multiple choice
mcq_check = { slip = 0.10, guess = 0.25 }   # a multiple-choice check on one point (step 05d); guess about 1 in 4 options

[nudges]                   # small odds multipliers from an ordinary exchange. Judgement calls, starting values (no study gives them); ceiling: decision 0003
depth = { surface = 1.0, mechanism = 1.0, transfer = 1.1 }   # a basic question doesn't lower the estimate; evidence does that
engagement = { passive = 1.0, active = 1.0, constructive = 1.05 }
ceiling = 0.35             # an exchange alone never lifts a part above this p_known; strictly below levels.new
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
floor = "start"            # from research: research.md row 53, patch 0005 (our simulation: day-30 inversions 0.82-1.00 -> 0.03-0.26, AUC 0.48-0.59 -> 0.62-0.71). p_now fades towards the part's normal start (0.30 here), not to 0; not the covered start, which is above levels.new (Vishnu, 19 Nov); "zero" keeps the old behaviour
literacy_floor = 0.0       # judgement call (patch 0005): Ask and Verify fade towards 0, so passing once doesn't keep a student near secure

[propagation]
prereq_boost = 0.20        # share of a gain passed one hop to prerequisites
queue_band = [0.30, 0.75]  # parts in this band are candidates to teach next
forward_weight = 0.5       # judgement call, starting value: Kaser et al. (2014, 2017) model skill links but give no weight; shifts a new part by this share of its prerequisites' log-odds change

[coverage]                 # starting points for parts a class has been taught (step 05q; Vishnu's change of 18 Nov: a boost, not a fixed prior)
boost_logit = 0.5          # judgement call, starting value: a covered part starts this far up in log-odds from its normal start (0.30 -> about 0.41)
class_k = 25               # from research: Simpson et al. (2024) intercept SD 0.57-0.90 logits implies k of about 18-44 in our simulation
class_estimate_enabled = false   # off by default: on only with the school's written instruction (personalisation.md section 7)
class_min_students = 5     # from personalisation.md sections 5 and 7: minimum cell size
class_max_down = 0.075     # from personalisation.md section 7: the class estimate never starts a covered part more than this below its boosted start

[starting]                 # a student's own starting adjustment (step 05q)
k = 25                     # from research: Simpson et al. (2024) spread plus our simulation: first answers for half weight
bound_logits = 1.5         # from research: about +-2 SD of the same spread
cap = 0.65                 # judgement call, starting value: no starting point (coverage, personal adjustment and feed-forward together) is above this; answers can take a part anywhere


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
share_far = 0.10           # > 60 days to the exam (tune-from-research: was 0.25)
share_mid = 0.19           # 14–60 days (was 0.15)
share_near = 0.30          # < 14 days (was 0.08)
min_gap_days = 1
review_when_below = 0.50   # judgement call, starting value: also due when recall is expected to fall below this, if that comes before the share gap. Not from research (see docs/research/review-threshold-simulation.md)
review_before_new = true   # judgement call (Vishnu, 19 Nov), mirrors review_when_below: after a right answer, also due when p_now is expected to fade below levels.new, if that comes before the share gap (reason "fading")
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
max_followups = 1          # re-asks of an ignored literacy task or check before it counts as skipped (missing, not 0)
max_waits = 2              # replies a literacy task waits behind a course question before it takes the question slot
ask_min_features = 2       # fewer question features than this: coach the question (Ask), else Verify
how_secure_every = 3       # at secure, a how-AI-works check every this many triggers for that part
importance = 0.5           # fixed importance of the AI-literacy parts (they have no exam weight)

[session]                  # sessions, fatigue and getting stuck, derived from events
gap_minutes = 30           # a longer gap starts a new session
slip_cap = 0.40            # judgement call: the most any slip can reach, time on task included
signal_window = 6          # exchanges used for the supporting signals
stuck_attempts = 3         # open answers on a part before it can count as stuck (MCQ checks: same point missed twice)
stuck_below = 0.5          # and their mean score below this
quick_parts = 3            # parts offered for a short burst in long-session or rushing mode

[fatigue]                  # time on task and rapid guesses (step 05s). Pacing, never an emotion: no affect label, no biometric data
slip_start_minutes = 28    # from research: Randles, Harlow & Inzlicht (2017), performance declines from about 28 minutes
slip_per_minute = 0.002    # from research (fit to the same decline of 4-5 points by about 50 minutes): extra slip per minute after that
extra_slip_cap = 0.12      # from research: end-of-test declines of 7.5-12% (Brown, Kaur, Kingdon & Schofield; TIMSS); the top is used
mode_minutes = 50          # from research: Randles et al. (2017), with Sievertsen, Gino & Piovesan (2016) on breaks: long-session mode starts here
rapid_guesses = 2          # judgement call, starting value: rapid guesses in a session that start rushing mode
reading_wpm = 300          # from research: Brysbaert (2019), mean silent reading 238 wpm, range 175-300; the top is used so fewer students are flagged wrongly
typing_wpm = 52            # from research: Dhakal et al. (2018), mean typing speed 52 wpm on a keyboard
min_students_per_bin = 5   # judgement call: a class fatigue-curve bin with fewer students is hidden

[engagement]               # in-session engagement rules (engagement-rules); never stored as a trait
passive_run = 4            # passive messages in a row before offer_choice offers ways on (once a session, never when fatigued)
low_share = 0.5            # passive or "just show me" share of the last session.signal_window messages at or above which the
                           # explain-back asks for the weakest point only
weakest_last_n = 5          # from research: Galyardt & Goldin (2015), 75-93% of predictive weight on the last 5 attempts
coasting_min_messages = 2   # judgement call, starting value: messages in the window before a student can count as coasting

[confidence]               # "how sure are you?" after an answer to a check (step 05z). Never an input to p_known
enabled = true             # judgement call: asked only on checks, reviews and prerequisite checks, never on ordinary chat or while rushing
max_per_session = 6        # judgement call, starting value: at most this many asks in a session
stop_after_skips = 2       # judgement call, starting value: two skips in a row and it stops asking for the session (no penalty for skipping)
min_per_group = 5          # judgement call (Vishnu, 18 Nov): the calibration line shows a group only after this many rated answers in it

[find_error]               # find-the-error practice (decision 0012). Built but OFF until Vishnu approves it: the evidence is thin
enabled = false            # judgement call: EDUX_FIND_ERROR=1 turns it on without editing this file
clean_share = 0.4          # judgement call, starting value: share of items with no error at all (the review's design rules say 30 to 50%; no study gives a ratio)
max_per_session = 1        # judgement call: rare, at most this many a session, never while rushing, only on a part at developing or above

[web]                      # the map, student and teacher pages (decision 0023)
public_example_map = true  # judgement call: serve the synthetic example pack's course map with no key; any other pack always needs a key
public_base_url = ""       # where the pages are served; get_my_progress links the student's map only when set. EDUX_PUBLIC_BASE_URL overrides it (decision 0026)
link_minutes = 15          # judgement call: a map link works once, within this many minutes
session_minutes = 120      # judgement call: the read-only browser session a map link opens ends after this, or when the tab closes

[reminders]               # in-chat deadline reminders (step 05u). Synapse cannot push notifications
days_ahead = 7             # judgement call, starting value: tests due within this many days are mentioned, once, at the start of a session

[plan]                     # day-by-day study plans (step 05u)
sessions_per_week = 3      # judgement call, starting value; the student can say otherwise

[show]                     # "just show me" (engagement-rules)
max_per_part_session = 2   # after this many shows of one part in a session, the next first asks a 2-option question on the point

[personalisation]          # per-student learning rate (05h, recalibrated in 05m). Not the starting-point adjustments (05q), which are core and always on
enabled = false            # judgement call: off by default (Children's Code Standard 12, profiling off by default; the recalibrated offset barely moves); EDUX_PERSONALISATION=1 turns it on without editing this file
learn_rate_k = 400         # from research spread plus our simulation: shrinkage, the offset is n / (n + k) of the evidence's mean surprise
min_observations = 10      # judgement call, starting value: pieces of evidence (earlier sessions, not fatigued, immediate, untaught or a part's first answer) before any offset
min_parts = 3              # judgement call, starting value: and across at least this many parts
recency_half_life = 100    # judgement call: the rate is treated as a stable trait, so a piece of evidence counts half as much 100 pieces later
surprise_scale = 1.0       # from our simulation's regression slope: log-odds of learn-rate change per unit of shrunk mean surprise
learn_rate_weight_bounds = [0.7, 1.3]   # from research: about +-2 SD of the replicated spread (Koedinger et al., 2023; Simpson et al., 2024); odds multiplier on bkt.learn_rate
max_change_per_session = 0.25   # judgement call, starting value: log-odds the offset may rise from one session to the next
down_change_factor = 2.0   # direction from Doroudi & Brunskill (2019); size is a judgement call: it may fall this many times faster, since under-crediting is the safer mistake

[priorities]               # which add-on step Synapse picks, by expected marks (priorities). These are starting guesses, to be learned
                           # from pilot data (the considered logs in issued_plan)
weight_homework = 0.3      # how much a test of each kind counts
weight_class_test = 0.6
weight_mock = 1.0
weight_final = 1.0         # the final exam, always in the sum
horizon_days = 7           # urgency = clamp(horizon_days / days to the test, urgency_floor, 1)
urgency_floor = 0.2

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
length_known_share = 0.5   # a review or check on a part at developing or above: this share of the ceiling (step 05j; Kalyuga et al., 2003)
length_fatigued_share = 0.4   # every step while fatigued; neither shrinks a student's own answer_length

[retention]                # how long data is kept (step 05x). Judgement calls, starting values: schools set their own; run `purge` to apply them
call_log_days = 30         # call-log detail (timing, sizes, errors per call) is deleted after this many days
after_leaving_days = 90    # a student marked as having left has all their data deleted this many days later (a window for appeals and questions)

[results]                  # size of a tool result, in characters of compact JSON as sent (steps 05c, 05w)
max_chars = 2400           # engineering budget, about 600 tokens, not from research; every tool but get_my_progress. Over this, reference blocks (tutor_turn) are dropped, then the call is logged as over budget
max_chars_progress = 3000  # engineering budget, not from research: get_my_progress (levels view), map link included; raised from 2400 when the real Edexcel Theme 1 pack overflowed it (decision 0026)
max_chars_full_progress = 6500   # engineering budget, not from research: get_my_progress with include_parts; raised from 4000 for the same reason

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
# prequestion, check_prereq, step_back, review_recall, reask, offer_choice (offer_stop before engagement-rules), ask_which; from 05d ask_mcq and explain_back;
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
| `moves/<move>.md` | what each move does, at most 2 sentences, with `{field}` placeholders filled from the step's `data`. Sent once, as a section of the server instructions (step 05c). The final set is the 14 moves in `tools-and-context.md` ("The move set"): `ask_mcq`, `teach_point`, `show`, `explain_back`, `extend`, `feedback`, `reteach`, `answer_brief`, `reask`, `offer_choice` (`offer_stop` until engagement-rules), `ask_which`, `answer_with_sources`, `literacy_task`, `source_conflict`. Step 05c has the interim 17 listed there |
| `moves/<key>.cue.md` | one line, at most 15 words, sent with every step of that move (step 05c). The key adds the variant (`ask_mcq_<purpose>`, `teach_<level>`, `review_<mode>`), falling back to the bare move |
| `literacy/<skill>_<level>.md` | feedback and task patterns for `ask` and `verify` at `new`, `developing` and `secure` (step 05e) |
| `format/<client>.md` | formatting for maths, money and diagrams per chatbot (`claude`, `chatgpt`, `gemini`, `default`), returned in `style.format` |
| `progress/calibration.md` | the calibration line in `get_my_progress` (only after enough rated answers; step 05z) |
| `fatigue/long_session.md`, `fatigue/rushing.md` | the break and the slow-down suggestions (steps 05s; pacing, not a mood label) |
| `bridge/reason.md`, `cues/upcoming.md`, `cues/diagram.md` | the "this links to what's next in class" lead-in (05t) and the upcoming-test and diagram cues |
| `plan/*.md` | the study-plan wording for `plan_my_study` (05u) |
| `notices/class_estimate.md` | the notice shown when a class-level estimate is on (05q) |
| `confidence/ask.md` | the "how sure are you?" line (05z) |
| `find_error/intro.md`, `reveal_error.md`, `reveal_clean.md` | the find-the-error practice item and its reveals (05za) |
| `checks/<kind>.md` | marking instructions for `points` and `level` checks (step 07) |
| `prompts/<prompt>.md` | the text of the `review_due` and `check_me` prompts (`{topic}` is filled in) |
| `teaching_note.md` | the teaching-note template with `{placeholders}` (debugging output only) |
| `chatbot_setup.md` | the text students paste into their chatbot's custom instructions |
