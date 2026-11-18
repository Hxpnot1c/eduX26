# Learner model

What the system believes each student knows, and how it updates. All numbers are in `settings.toml`. All state is derived from events, so changing a rule here and running `python -m edux.cli rebuild` re-scores every student.

## Assessment design
AI literacy is assessed by stealth assessment (Shute, 2011): evidence comes from normal work, and the same moments build the skill. It follows evidence-centred design (Mislevy, Steinberg & Almond, 2003):

| model | what it is here |
|---|---|
| Competency (what we measure) | the AI-literacy parts `ail_ask`, `ail_verify` and the `ail_how_*` parts, alongside the course parts |
| Evidence (what counts, how it's scored) | the chatbot's labels and ticks, plus multiple-choice letters, scored by the server's fixed rules into this learner model |
| Task (where evidence comes from) | moments in normal work: a research question leads to a literacy task; a failed link, a self-correction or a changed answer after pushback leads to a one-question how-AI-works check |

## What is tracked
- **Per part:** `p_known` (chance the student knows it, before decay), `half_life_days`, `clock_start` (when the current decay began), `last_correct`, `last_seen`, `n_evidence`, `exchanges_since_evidence`, `offload_left`, `was_secure` (set once the part reaches secure).
- **Per misconception:** active or not, last seen.
- **Approach records:** which support approach was used on a part and whether the next check went well.
- **Review queue:** parts due for review, with a reason.

Concepts, subtopics and topics are never tracked directly. Their level is the mean of their parts' current `p_now`, weighted by part importance.

Every rule runs at the event's own timestamp, so replaying the events always gives the same state.

## Starting point and difficulty
A part the student hasn't met starts at `bkt.prior` with `decay.base_half_life_days`, shifted by its **difficulty** (0 easy – 1 hard):
- The teacher's value comes from the `difficulty` column on the part or its nearest ancestor (course pack or teacher feedback). Without one, it's `difficulty.default`.
- `shift = (difficulty − default) / 0.5`, clamped to −1…1.
- The starting `p_known` is `prior − prior_shift × shift`.
- The starting half-life is `base_half_life_days × (1 − half_life_shift × shift)`.
- So hard parts start lower and are forgotten faster.

Later, a cross-student estimate (`learner.difficulty_signal`, e.g. first-attempt failure rates) is blended in at share `difficulty.w_cross`. It's 0 until there is enough evidence across students.

## Current p_known (decay)
Read time only, never written back:

```
p_now = p_known × 0.5 ^ (days_since(clock_start) / half_life_days)
```

Forgetting runs from the last time the student **got the part right**, not from when they last saw it. Seeing something isn't the same as knowing it.
- **A correct answer** restarts the clock (`clock_start = last_correct = now`).
- **An exchange** moves the clock only `decay.seen_refresh` of the way to now. Being reminded helps a little, but less than recalling it.
- **Before the first correct answer** there is no clock and no decay: with nothing learnt, there's nothing to forget.
- **A wrong answer** sets `p_known` to the new, lower estimate and, if a clock is running, restarts it from that value.

## Level
- **new:** `p_now < levels.new`
- **developing:** between the two thresholds
- **secure:** `p_now ≥ levels.secure`

## Updates

### 1. Evidence (chat and checks)
Evidence is an event in `evidence_log`, one row per part, with a score from 0 to 1. It comes from two places:
- **chat:** when the student's message answers something the chatbot asked, the chatbot sends it as `answer` with the next `tutor_turn` call, ticking the points from `score_next` the student produced. The server computes the score: 1 or 0 for a pre-question, otherwise points met / points for the part (the part's mark points, or its notes' key points when it has none). Never for the chatbot's own explanation.
- **check:** results of issued checks (step 07).

Evidence types from chat, each with its own slip and guess in `[bkt.evidence]`:
- `prequestion`, `explain_back`, `review`, `extend`, `past_question`: as asked by the plan. From step 05d, an `ask_mcq` with purpose `intuition` records `prequestion`, and `review` is no longer sent (reviews are MCQs, below); old `review` events still replay.
- `mcq_check` (step 05d): a server-built multiple-choice question on one point: a check while a part is taught point by point, a prerequisite check, or a review (`ask_mcq` with purpose `check`, `prereq` or `review`). Score 1 or 0 from the letter picked; a wrong pick activates its misconception. Its guess is about 1 in 4, so one point counts for less than an explanation of the whole part. The row records the point asked as `point_id` (migration 008), which the stuck rule reads. Progress through a part's points is kept in `issued_plan`, not in state, so rebuild is unaffected.
- `ail_question`, `ail_task`, `ail_unprompted` (step 05e): AI-literacy evidence (see below).

The result counts as correct if `score ≥ bkt.correct_share`. Wrong evidence that carries misconception ids activates them.

**Multiple-choice guess.** With `bkt.mcq_guess_from_options`, a multiple-choice answer (`mcq_check`, `ail_how`, an intuition `prequestion`) guesses `1 / n_options`, the options it showed, stored on the row (migration 010). Rows written before that have no `n_options` and keep the type's guess.

**Immediate recall.** Performance straight after teaching overstates learning. Evidence on a part within `evidence.immediate_window_minutes` of an exchange on that part with `support_given` = `worked_example` or `hint` (including the exchange it was sent with) is applied as `immediate`: `immediate`'s slip, and the larger of `immediate`'s guess and the type's own (so a 2- or 3-option question is never discounted less). A correct immediate answer grows the half-life by the normal `decay.on_success` (a half-life multiplier of 1.0 for immediate evidence left 1.6 of 9 parts secure instead of 6.2 in the overnight simulation, report 06, finding w1-06-07, so it isn't used). Evidence later in the session, or in a later session, uses its own type. The type is stored as sent and the rule applied when replaying, so changing the window re-scores old evidence.

`p_known` is saved clamped to [0.001, 0.999] (research fixes, 0001): a long run of right answers can otherwise round it to exactly 1.0, which breaks the exchange nudge's odds, p / (1 − p).

Standard BKT with the slip and guess for the evidence type:

```
if correct: p = p(1-slip) / (p(1-slip) + (1-p)guess)
else:       p = p·slip / (p·slip + (1-p)(1-guess))
p = p + (1-p) × learn_rate
```

The update starts from `p_now`, the decayed value. Then:
- `half_life ×= on_success` (or `on_failure`), floored at `min_half_life_days`
- `n_evidence += 1`, `exchanges_since_evidence = 0`
- `last_seen = now`, and the clock as described under decay

If `offload_left > 0`, guess is replaced by `offloading.guess_after` and `offload_left -= 1`. (Removed in step 05d: see Offloading.)

While the session is fatigued (see Sessions), slip is raised by `session.fatigue_slip_add`, capped at `session.slip_cap`.

**Startup check (identifiability).** Settings fail to load unless, for every evidence type, with slip at its largest (`session.slip_cap`) and guess at its largest (1/2 for a multiple-choice type when `mcq_guess_from_options` is on, and the immediate rule's larger guess):
- `guess + slip < 1`, so a correct answer is evidence of knowing;
- `learn_rate < 1 - slip / (1 - guess)`, so a wrong answer still lowers the estimate (Baker, Corbett & Aleven, 2008).

With the current values the tightest case is a 2-option question while fatigued: `learn_rate` must stay below 0.20.

**Personal learning rate (personal-learning-rate).** Each student has one learning-rate offset, pooled across their course parts (`learner.learning_offset`; `docs/research/personalisation.md`, section 7). It is applied as an odds weight on `bkt.learn_rate`: `odds(learn_rate) × exp(offset)`.
- **What it's built from:** the `surprise` of the student's evidence in earlier sessions. Fatigued evidence, immediate recall (`evidence_derived.immediate`), untaught pre-questions (weight 0) and AI-literacy parts are left out.
- **Size:** `target = n / (n + learn_rate_k) × recency-weighted mean surprise × surprise_scale`, within `log(learn_rate_weight_bounds)`.
  - Each piece of evidence counts half as much `recency_half_life` pieces later.
  - The target is 0 until there are `min_observations` pieces across `min_parts` parts.
- **Steps:** the offset moves once per session, towards the target. It rises at most `max_change_per_session` log-odds and falls at most `down_change_factor` times that, so under-crediting is the more likely error.
- **Rebuild:** it is a pure function of earlier events, so rebuild gives the same state.
- **Switching it on and off:** `personalisation.enabled = true` by default. `EDUX_PERSONALISATION=0` turns it off without editing the file, and changing either then needs a rebuild to re-score.
- **Who sees it:** it is never a label and is never shown to students or teachers. Only the CLI student view (`python -m edux.cli state`) prints the offset and `n`.
- **What isn't personal:** slip and guess stay per evidence type.

**Pre-questions.** A pre-question is asked before teaching, so a wrong answer on untaught material reveals little, and so does a lucky right one. Its effect is weighted by how much the part has been covered:

```
coverage = exchanges on the part × prequestion.exchange_weight + n_evidence
w = min(1, coverage / prequestion.full_weight_at)
p = p_before + w × (p_bkt − p_before)     # p_bkt: the normal update with the prequestion slip and guess
```

- With `w = 0` (never taught), it is diagnostic only. The chosen misconception is activated, and nothing else changes.
- With `w > 0`, half-life, `n_evidence`, the clock and propagation update as for other evidence, with the gain scaled by `w`.

### 2. Ordinary exchange (no check)
A small odds nudge from the labels the chatbot sent:

```
odds = p / (1-p)
odds ×= depth[question_depth] × engagement[engagement]
p = odds / (1 + odds)
```

If the exchange is tagged with a concept rather than parts, each of its parts gets the nudge at `concept_tag_strength` (the multiplier's distance from 1 is scaled). The same strength scales the clock refresh.

`last_seen` updates, `exchanges_since_evidence += 1`, and the clock moves by `seen_refresh`. `half_life` does not change, because no evidence was given. Old ids in events resolve through `id_map`. Unknown misconception ids are ignored.

### 3. Offloading ("just show me")
Triggered by the `offloading` label or by `choice_taken = just_show_me`.
- `offload_left = checks_discounted`
- A review is queued after `just_show_me_gap_days`.
- `p_known` itself is unchanged.

**From step 05d, being shown doesn't change understanding:** the exchange gets no depth or engagement nudge, and `offload_left` is no longer set (it stays 0, and `offloading.guess_after` and `checks_discounted` are removed). The immediate-recall rule already lowers the credit for an answer straight after being shown. The exchange still records `offloading = 1`, for the AI-literacy trends, and the review is still queued.

### 4. Prerequisite propagation
When evidence raises a part, each direct prerequisite gets `prereq_boost × gain`, added to its `p_now`. One hop only, never downward. A prerequisite on a concept boosts each of its parts.

### 5. Misconceptions
- When the chatbot labels a misconception, it becomes active.
- Correct evidence on its part makes it inactive.

Approach records: an exchange with `support_given` other than `none` adds a record. The next evidence on that part fills in `next_check_correct` on the latest open record.

### 6. Untested ("familiar but untested")
After `untested_after` exchanges on a part with no evidence, if `p_now < untested_below`, a review is queued straight away with reason `untested`. A student who keeps discussing a part can feel they know it because it's familiar. If the model still thinks they're weak, they should be checked rather than taught it again.

A review queued by an exchange keeps any earlier due date already in the queue. A review scheduled after evidence replaces it.

### 7. AI-literacy skills (step 05e)
The parts `ail_ask`, `ail_verify` and the four `ail_how_*` parts (`fabrication`, `confidence`, `cutoff`, `agreement`), loaded with every pack (see `course-pack-format.md`), are tracked like any other part: decay, spacing and levels. They have a fixed importance (`literacy.importance`) and are left out of the course tree, levers, candidates, search and course reviews (they are practised through their tasks and checks).
- **`ail_question`** on `ail_ask`, on every research question: score = question features present / 4.
- **`ail_task`** on `ail_verify`: the student's reply to a verify task, scored by the ticks they produced / 4. A correct Verify answer moves the part only `score` of the way (3 of 4 ticks moves it 3/4 as far as 4 of 4). A reported dead or mismatched source (`source_conflict`, sent as the Verify answer or while a verify task is pending this session) is a successful check: `ail_task` with score 1, whatever was ticked, since a dead page has no publisher, date or figure to tick. It is always `ail_task`, never `ail_unprompted`, so one report can't make Verify secure (research fixes, 0003).
- **Skips (research fixes, 0003).** A task (any skill) still ignored after `literacy.max_followups` re-asks is missing, not wrong: no evidence is written, and the skip is recorded in `literacy_skip` (an event table, migration 013) and shown as `skipped` beside the level in progress. A task that was never re-asked expires at session end with nothing recorded.
- **`ail_unprompted`** on `ail_verify`: the student reports checking a claim without being asked. Its slip is lower, so it counts more.
- **`ail_how`** on an `ail_how_*` part: a how-AI-works multiple-choice check, scored 1 or 0 from the letter. A wrong pick activates that misconception (section 5). An ignored check is a skip after `literacy.max_followups` re-asks, with no evidence.

## Spacing (review queue)
After any evidence on a part:

```
gap = share × days_to_exam
```

- `share` comes from `scheduling` based on days to the student's next test on the part (`learner.days_to_exam`): the soonest of the final exam (`exam_date_override` if set and ahead, else the pack's exam papers) and the student's own upcoming assessments covering the part (priorities: homework, class tests, mocks). Spacing works towards the nearest test, and goes back to the final exam once that test has passed (Cepeda et al., 2008).
- The gap is floored at `min_gap_days`.
- **Recall threshold:** when a clock is running and `p_known > scheduling.review_when_below`, the part is also due when `p_now` is expected to fall below that threshold, `half_life × log2(p_known / review_when_below)` days on. If that comes first, it replaces the share gap (still floored at `min_gap_days`) with reason `recall_below`. A part already below the threshold, or with no clock, uses the share gap only.
- `due = now + gap`, with reason `scheduled` (or `recall_below`)

Shares are adapted from Cepeda et al. (2008): the optimal gap shrinks as the test gets closer, but it is a larger share of the time left (0.10 far, 0.19 mid, 0.30 near; tune-from-research). With no exam date, `base_half_life_days` is used as the gap.

`reviews_due` returns up to `max_reviews_per_reply` due parts, ordered by importance.

## Priorities: the add-on step by expected marks
The student's message still sets the main step. The value score orders only the choices eduX makes itself:
- the add-on step (`plan._second_step`): an earned `extend`, the best due review, or nothing;
- the order of due reviews (`reviews_due`);
- the order of prerequisite repairs (`weak_prerequisites`).

```
value = move_chance × Σ over the final exam and the student's upcoming assessments covering the part
        [ weight(kind) × urgency(days to it) × (1 − p on its date) ]
urgency(days) = clamp(horizon_days / max(days, 1), urgency_floor, 1)
```

- **Prediction at the test date.** `p on its date` is `p_now` with decay run forward to the test date, not today's value, so a part that is secure now but will fade before the mock counts as a gap.
- **The final exam is always in the sum** (`weight_final`), at the date spacing uses. With no exam ahead, it counts at `urgency_floor` with today's p.
- **`move_chance`** is the student's learn rate, including their personal offset. The learn rate isn't per evidence type, so a review and an extend get the same chance today.
- **No cramming.** Due-ness (the share gap or `review_when_below`) still decides whether a review is eligible. A test only orders the eligible reviews and decides between extend, a review or nothing; it never makes a review due.
- **Ties** keep the old order (extend first, then overdue × importance), so with no assessments only the extend-vs-review choice changes.
- **Reason.** A review picked because of a test (the assessment adding the most to its value) carries `data.reason`, e.g. "on your mock on Tuesday" (the day name within 7 days, else the date).
- **Logging.** The candidates not picked are saved with their values as `considered` in `issued_plan`. They are never sent: they are the data a later model would learn the weights from.
- **Weights.** The weights in `[priorities]` are hand-set starting guesses. Learned policies have mostly not beaten sensible rule-based ones (Doroudi, Aleven & Brunskill, 2019), so they stay hand-set until there is pilot data.

## Choosing what to teach next (candidates)
A part is a candidate when its `p_now` is inside `queue_band` and its prerequisites are at least developing. Candidates are ordered by `importance × (1 - p_now)`. Parts the student hasn't met count at their starting estimate.

## Anchor
`learner.anchor(student, part)` picks the best secure analogous part to teach through: highest link weight, then the same part type (a calculation anchors a calculation), then the highest `p_now`.

## Interleaving
When a focus part has `confusable` edges, those parts are returned (limit in context.toml) so the chatbot can contrast them.

## Support level
- `p_now < support.worked_example_below` → `worked_example`
- `< support.hint_below` → `hint`: `hint_procedural` for `calculation` and `diagram` parts (a completion problem), and `hint_conceptual` for the other part types (a short example, then one guiding question)
- otherwise → `explain_back` (re-teach only the missing points)
- **extend** is added on when `p_now ≥ support.extend_from` and the student's latest evidence on the part was correct: one higher-order question (an unseen case, a breaking assumption, or a causal link)

The text sent with each level is in `text/support/`. A **pre-question** (`text/support/prequestion.md`) comes before any of these on an untaught part; see `tools-and-context.md`.

## Review modes
Each due review has a mode:
- **`recall`:** when `p_now < levels.new`. Straight recall of the part.
- **`transfer`:** otherwise. The same idea in a new context: a causal or analogous link, then an unseen past-paper question, then an unseen case.

## Sessions
Derived from both event logs at read and rebuild time. There are no session events.
- **Session:** a student's exchanges and evidence in time order, until a gap longer than `session.gap_minutes`. `session_id` is the start timestamp.
- **Surprise:** `score − expected` for each piece of evidence, where `expected = p_before × (1 − slip) + (1 − p_before) × guess` is the chance of a correct answer under that evidence's slip and guess (after the multiple-choice and immediate rules, before any fatigue slip), and `p_before` is the part's `p_now` just before applying it. Scaled by `w` for pre-questions. Measuring against `p_before` alone made a lucky guess on a 4-option question look like a surprise and a slip on a known part look larger than it is (tune-from-research). It is stored with `fatigued` and `immediate` (migration 011) in the derived table `evidence_derived`. Comparing with the model's expectation, not with "correct or not", stops hard material from looking like fatigue.
- **Fatigue:** from the first piece of evidence where:
  - the session is at least `session.fatigue_min_minutes` old
  - the mean surprise of the last `session.fatigue_window` pieces is ≤ `session.fatigue_threshold`
  - those pieces span at least `session.fatigue_min_parts` parts

  It lasts until the session ends. Evidence while fatigued uses the raised slip above, so errors count for less and correct answers still count fully. The "just show me" share and the `surface` share over the last `session.signal_window` exchanges are reported but never trigger fatigue.
- **Engagement (engagement-rules):**
  - `learner.passive_streak` counts the latest messages in the session labelled `passive`, in a row. It drives a one-off `offer_choice`.
  - `learner.coasting_share` is the share of the last `session.signal_window` messages that were `passive` or "just show me". At `engagement.low_share` or above, the explain-back asks for the weakest point only (`learner.weakest_point`).
  - `learner.shows_this_session` counts "just show me" on a part. After `show.max_per_part_session`, a 2-option check comes first.

  See `tools-and-context.md` for the plans these give. Like fatigue, these signals are in-session only, read from the events each turn, and never stored as a trait of the student.
- **Stuck:** a part the student keeps failing in the session. This calls for a different approach, not a break. Intuition and other prequestion evidence never count.
  - On 0/1 MCQ checks (`mcq_check`, and `ail_how` from step 05e): the same `point_id` missed on its check and again on the re-check after its reteach (a part with no score points counts as one point).
  - On open answers: at least `session.stuck_attempts` of them, mean score below `session.stuck_below`, and a latest score no better than the first.
- **API:**
  - `learner.session_state(student_id, at)` returns the current session (minutes, rolling surprise, fatigued and since when, stuck parts, supporting signals), or `None`.
  - `learner.sessions(student_id)` lists past sessions with fatigue onset minutes.

## Teaching note
Debugging output only (`python -m edux.cli context`); `tutor_turn` doesn't send it. A short paragraph built from `text/teaching_note.md` with:
- focus parts and levels
- weak prerequisites
- the anchor (an analogous part that is secure, with its edge note)
- active misconceptions
- exam proximity (only when within `exam_close_days`)
- "what worked before" (only with `approach_min_records` or more records)
- interests and answer length from the profile

Personalisation never uses learning styles.

## Rebuild
`learner.rebuild_state(student_id)`:
1. Deletes the student's derived rows, including `evidence_derived`.
2. Replays their events from `exchange_log` and `evidence_log`, merged in order of `ts`, then each exchange followed straight away by the evidence that came with it, then evidence with no exchange, through the rules above with the current settings. This is the same order they are applied live, so a rebuild gives exactly the live state.

`rebuild_all()` does every student. Events keep the `protocol` and `settings_hash` they were recorded under, for analysis.

A rebuild uses the student's current `exam_date_override`, not the value it had when each event happened. The same goes for their assessments (`student_assessment`, priorities): they are profile, not events, so a rebuild uses the assessments as they are now, and adding then removing one leaves the state as if it was never added.
