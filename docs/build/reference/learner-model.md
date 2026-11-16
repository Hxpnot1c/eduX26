# Learner model

What the system believes each student knows, and how it updates. All numbers are in `settings.toml`. All state is derived from events, so changing a rule here and running `python -m edux.cli rebuild` re-scores every student.

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

Later, a cross-student estimate (`learner.difficulty_signal`, e.g. first-attempt failure rates) is blended in at share `difficulty.w_cross`. It's 0 until checks exist.

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

### 1. Evidence (checks, explain-back, links)
Standard BKT with the slip and guess for that evidence type. For a check scored 0–1, the result counts as correct if `score ≥ bkt.correct_share`.

```
if correct: p = p(1-slip) / (p(1-slip) + (1-p)guess)
else:       p = p·slip / (p·slip + (1-p)(1-guess))
p = p + (1-p) × learn_rate
```

The update starts from `p_now`, the decayed value. Then:
- `half_life ×= on_success` (or `on_failure`), floored at `min_half_life_days`
- `n_evidence += 1`, `exchanges_since_evidence = 0`
- `last_seen = now`, and the clock as described under decay

If `offload_left > 0`, guess is replaced by `offloading.guess_after` and `offload_left -= 1`.

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

### 4. Prerequisite propagation
When evidence raises a part, each direct prerequisite gets `prereq_boost × gain`, added to its `p_now`. One hop only, never downward. A prerequisite on a concept boosts each of its parts.

### 5. Misconceptions
- When the chatbot labels a misconception, it becomes active.
- Correct evidence on its part makes it inactive.

Approach records: an exchange with `support_given` other than `none` adds a record. The next evidence on that part fills in `next_check_correct` on the latest open record.

### 6. Untested ("familiar but untested")
After `untested_after` exchanges on a part with no evidence, if `p_now < untested_below`, a review is queued straight away with reason `untested`. A student who keeps discussing a part can feel they know it because it's familiar. If the model still thinks they're weak, they should be checked rather than taught it again.

A review queued by an exchange keeps any earlier due date already in the queue. A review scheduled after evidence replaces it.

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
- `< support.hint_below` → `hint`
- otherwise → `explain_back`

The text sent with each level is in `text/support/`.

## Teaching note
A short paragraph built from `text/teaching_note.md` with:
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
1. Deletes the student's derived rows.
2. Replays their events in `ts` order through the rules above, with the current settings.

`rebuild_all()` does every student. Events keep the `protocol` and `settings_hash` they were recorded under, for analysis.

Evidence has no event log until checks add `check_log` (step 07). Until then, `apply_evidence` effects are not replayed by a rebuild.

A rebuild uses the student's current `exam_date_override`, not the value it had when each event happened.
