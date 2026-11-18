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

**Immediate recall.** Performance straight after teaching overstates learning. Evidence on a part within `evidence.immediate_window_minutes` of an exchange on that part with `support_given` = `worked_example` or `hint` (including the exchange it was sent with) is applied as type `immediate`, which has a higher guess. Evidence later in the session, or in a later session, uses its own type. The type is stored as sent and the rule applied when replaying, so changing the window re-scores old evidence.

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
- **`ail_task`** on `ail_verify`: the student's reply to a verify task, scored by the ticks they produced / 4. An ignored task (any skill) is recorded as `ail_task` with score 0 on that skill's part after `literacy.max_followups` re-asks. A task that was never re-asked expires at session end with no score.
- **`ail_unprompted`** on `ail_verify`: the student reports checking a claim without being asked. Its slip is lower, so it counts more.
- **`ail_how`** on an `ail_how_*` part: a how-AI-works multiple-choice check, scored 1 or 0 from the letter. A wrong pick activates that misconception (section 5). An ignored check is recorded as 0 after `literacy.max_followups` re-asks.

## Spacing (review queue)
After any evidence on a part:

```
gap = share × days_to_exam
```

- `share` comes from `scheduling` based on days to the student's next relevant exam paper (`exam_date_override` wins if set).
- The gap is floored at `min_gap_days`.
- `due = now + gap`, with reason `scheduled`

Shares are adapted from Cepeda et al. (2008): the optimal gap shrinks as the test gets closer. With no exam date, `base_half_life_days` is used as the gap.

`reviews_due` returns up to `max_reviews_per_reply` due parts, ordered by importance.

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
- **Surprise:** `score − p_before` for each piece of evidence, where `p_before` is the part's `p_now` just before applying it (scaled by `w` for pre-questions). It is stored with `fatigued` in the derived table `evidence_derived`. Comparing with the model's expectation, not with "correct or not", stops hard material from looking like fatigue.
- **Fatigue:** from the first piece of evidence where:
  - the session is at least `session.fatigue_min_minutes` old
  - the mean surprise of the last `session.fatigue_window` pieces is ≤ `session.fatigue_threshold`
  - those pieces span at least `session.fatigue_min_parts` parts

  It lasts until the session ends. Evidence while fatigued uses the raised slip above, so errors count for less and correct answers still count fully. The "just show me" share and the `surface` share over the last `session.signal_window` exchanges are reported but never trigger fatigue.
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

A rebuild uses the student's current `exam_date_override`, not the value it had when each event happened.
