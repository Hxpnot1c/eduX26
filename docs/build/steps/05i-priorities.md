# Step 05i: Pick add-on steps by expected marks, counting the student's own tests

Branch `build/priorities`.

## What
The student's message still sets the main step. This step changes only the choices Synapse makes itself:
- the add-on step in `plan._second_step`: an earned extend, the best due review, or nothing;
- the order of due reviews (`context_blocks.reviews_due`);
- the order of prerequisite repairs (`context_blocks.weak_prerequisites`).

These choices now follow the expected marks from each step. That counts the student's own upcoming homework, class tests and mocks as well as the final exam, using the level the student is predicted to have on each test date.

## Why, with sources
- **The best review gap depends on how far away the test is** (Cepeda et al., 2008). A mock next week should pull spacing towards it, and spacing should go back to the final exam once the mock has passed.
- **Predicted level on the test date, not today.** A part that is secure now but will fade before the mock is still a gap, and decay is already in the model.
- **Hand-set weights, not a learned policy, for now.** Reinforcement-learning policies have mostly not beaten sensible rule-based ones in tutoring (Doroudi, Aleven & Brunskill, 2019). So the `[priorities]` weights stay hand-set, and every candidate not picked is logged (`considered`) as the data a later, learned policy would be checked against first.
- **No cramming.** A test changes what is reviewed first, never whether a review is due.

## The value score
```
value = Σ over the final exam and the upcoming assessments covering the part
        [ weight(kind) × urgency(days to it) × (1 − p on its date) ]
urgency(days) = clamp(horizon_days / max(days, 1), urgency_floor, 1)
```
- `p on its date` is `p_now(p_known, half_life_days, clock_start, date)`: the predicted level on the test date.
- The final exam is always in the sum (`weight_final`), at the date spacing uses (`exam_date_override`, else the pack's exam papers). With none ahead, it counts at `urgency_floor` with today's p.
- *(Removed in step [05n](05n-priorities-fixes.md):* this score first had a `move_chance` factor, the student's learn rate. It was the same for every step, so it scaled every value equally and never changed a choice.)
- **Eligibility is unchanged:** only due reviews (share gap or `review_when_below`) and an earned extend are candidates.
- **Ties** keep today's order: extend, then overdue × importance.

## Files
- `migrations/012_student_assessment.sql`: `student_assessment(id, student_id, name, kind, date, part_ids, created_at)`.
  - `kind` is `homework`, `class_test` or `mock`; `part_ids` is a JSON list.
  - It is profile, not events: a rebuild uses the assessments as they are now, like `exam_date_override`.
- `edux/learner.py`:
  - `assessments`, `final_exam_days` and `days_to_exam` (now the soonest of the final and the assessments covering the part);
  - `p_on`, `step_value` and `reason_text`.
- `edux/service.py` and `edux/server.py`: `update_my_profile` gets `add_assessment {name, kind, date, topics}` and `remove_assessment {id}`.
  - Topics are matched to the pack's topic names and spec codes, ignoring only case and spacing.
  - With no match, nothing is added and the topics come back to pick from.
  - An unknown kind or a past date is an error.
- `edux/context_blocks.py`: reviews and prerequisite repairs are ordered by value, then the old score. `Turn.value` caches values for the turn.
- `edux/plan.py`: `_second_step` picks the candidate with the highest value.
  - A review picked because of a test gets `data.reason` and the cue `ask_mcq_review_reason` (no new section).
  - The candidates not picked go to `issued_plan` as `considered`.
- `edux/cli.py`: the student view lists upcoming assessments and the top three due reviews with their values.
- `edux/demo.py`: demo-weak gets a mock in 5 days on the market-failure topic, and one part of it answered 8 days ago, so it's due.
- `text/tools/update_my_profile.md` and `text/moves/ask_mcq_review_reason.cue.md`.
- `scripts/check_mcp.py`: a priorities run.

## Settings
```toml
[priorities]               # starting guesses, to be learned from pilot data
weight_homework = 0.3
weight_class_test = 0.6
weight_mock = 1.0
weight_final = 1.0
horizon_days = 7
urgency_floor = 0.2
```

## Done when
- A due review covered by a mock in 3 days beats an earned extend on a part with only the final ahead. The same part with no mock loses to that extend.
- A part not yet due is never reviewed, whatever tests are coming.
- With a mock 5 days away on a part, its review gap shrinks. After the mock date, it goes back to the final-exam gap.
- Adding then removing an assessment and rebuilding gives the same state as never adding it.
- An unmatched topic returns the topic list and adds nothing.
- `considered` is stored with its values and never appears in a tool result.
- Server instructions stay at 894 words. No result is over 2,400 characters. Rebuild gives identical state.

## Tests
All in `scripts/check_mcp.py` (`priorities`), using a throwaway student. Part state is set by hand for the choice checks, and built from events for the rebuild check.
