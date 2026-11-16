# Learner model

What the system believes each student knows, and how it updates. All numbers are in `settings.toml`. All state is derived from events, so changing a rule here and running `python -m edux.cli rebuild` re-scores every student.

## What is tracked
- **Per part:** `p_known` (chance the student knows it now, before decay), `half_life_days`, `last_seen`, `n_evidence`, `offload_left`, `was_secure`.
- **Per misconception:** active or not, last seen.
- **Approach records:** which support approach was used on a part and whether the next check went well.
- **Review queue:** parts due for review, with a reason.

Concepts, subtopics and topics are never tracked directly. Their level is the mean of their parts' current `p_known`, weighted by part importance.

## Current p_known (decay)
Read time only, never written back:

```
p_now = p_known × 0.5 ^ (days_since(last_seen) / half_life_days)
```

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

Then:
- `half_life ×= on_success` (or `on_failure`), floored at `min_half_life_days`
- `n_evidence += 1`
- `last_seen = now`

If `offload_left > 0`, guess is replaced by `offloading.guess_after` and `offload_left -= 1`.

### 2. Ordinary exchange (no check)
A small odds nudge from the labels the chatbot sent:

```
odds = p / (1-p)
odds ×= depth[question_depth] × engagement[engagement]
p = odds / (1 + odds)
```

If the exchange is tagged with a concept rather than parts, each of its parts gets the nudge at `concept_tag_strength` (the multiplier's distance from 1 is scaled).

`last_seen` updates. `half_life` does not change, because no evidence was given.

### 3. Offloading ("just show me")
- `offload_left = checks_discounted`
- A review is queued after `just_show_me_gap_days`.
- `p_known` itself is unchanged.

### 4. Prerequisite propagation
When evidence raises a part, each direct prerequisite gets `prereq_boost × gain`. One hop only, never downward.

### 5. Misconceptions
- When the chatbot labels a misconception, it becomes active.
- Correct evidence on its part makes it inactive.

### 6. Overconfidence
After `overconfident_after` exchanges on a part with no evidence, if `p_now < overconfident_below`, a review is queued with reason `overconfident`.

## Spacing (review queue)
After any evidence on a part:

```
gap = share × days_to_exam
```

- `share` comes from `scheduling` based on days to the student's next relevant exam paper (`exam_date_override` wins if set).
- The gap is floored at `min_gap_days`.
- `due = now + gap`

Shares are adapted from Cepeda et al. (2008): the optimal gap shrinks as the test gets closer. With no exam date, `base_half_life_days` is used as the gap.

`reviews_due` returns up to `max_reviews_per_reply` due parts, ordered by importance.

## Choosing what to teach next (candidates)
A part is a candidate when its `p_now` is inside `queue_band` and its prerequisites are at least developing. Candidates are ordered by `importance × (1 - p_now)`.

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
