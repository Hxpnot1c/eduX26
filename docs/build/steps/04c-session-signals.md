# Step 04c: Session signals

**Branch:** `build/04c-session-signals`
**Read first:** `../reference/learner-model.md` (evidence, sessions), `../reference/database.md` (learner.db), `../reference/research.md`

## Goal
Detect fatigue and getting stuck within a study session, and protect the learner model from errors caused by tiredness. Everything is derived from the existing event logs, so `rebuild_state` reproduces it exactly. There are no new event tables.

## Why
- **Fatigue builds within a session, not across the day.** A preregistered study of ~17,000 students on an online learning platform found fatigue within an hour on task, but almost no effect of time of day (Randles, Harlow & Inzlicht, 2017). Breaks can remove the decline (Danish national test data, cited in the same paper).
- **Feeling tired isn't the same as performing worse,** so fatigue is detected from answers, not from the clock alone.
- **Wheel-spinning** (Beck & Gong, 2013) is a different problem: repeated failure on one skill. It needs a different approach, not a break.
- **Hard material looks like fatigue.** Answers often go wrong later in a session because the material got harder. So each answer is compared with what the model expected (`p_now`), not with "correct or not".

## Work
1. **Sessions.** A student's exchanges and evidence, in time order, form one session until there's a gap longer than `session.gap_minutes`. `session_id` is the start timestamp.
2. **Surprise.** For each piece of evidence, `surprise = score − p_before`, where `p_before` is the part's `p_now` just before applying it.
   - Pre-question evidence is scaled by its coverage weight (see `learner-model.md`), so pre-questions on untaught parts give a surprise of 0.
   - Surprise is stored in a new **derived** table, `evidence_derived(evidence_id PK, student_id, session_id, p_before, surprise, fatigued INTEGER)`, added in migration `004_session_signals.sql`.
   - `rebuild_state` clears and refills it.
3. **Fatigue.** A session is in the fatigued state from the first piece of evidence where all of these hold:
   - minutes since the session started ≥ `session.fatigue_min_minutes`
   - the session has at least `session.fatigue_window` pieces of evidence, and the mean surprise of the last `session.fatigue_window` is ≤ `session.fatigue_threshold`
   - those pieces cover at least `session.fatigue_min_parts` different parts, so it's broad and not one hard part

   It lasts until the session ends. Two supporting signals are reported but never trigger fatigue on their own: the "just show me" share and the `surface` question share over the last `session.signal_window` exchanges.
4. **Protect the estimate while fatigued.** Evidence applied in the fatigued state uses `slip + session.fatigue_slip_add`, capped at `session.slip_cap`.
   - Errors from tiredness then count for less.
   - Correct answers still count fully, because guess is unchanged.
   - `fatigued = 1` is recorded on that evidence's `evidence_derived` row.
5. **Stuck.** A part is stuck in a session when it has at least `session.stuck_attempts` pieces of evidence, their mean score is below `session.stuck_below`, and the latest score is no better than the first. It's reported per part.
6. **API.**
   - `learner.session_state(student_id, at)` returns `{session_id, minutes, n_evidence, rolling_surprise, fatigued, fatigued_since_minute, stuck_parts, just_show_me_share, surface_share}`, or `None` when there's no current session.
   - `learner.sessions(student_id)` lists past sessions with minutes, evidence count and the minute fatigue began, if it did.
7. **CLI.**
   - `state` prints the current session line.
   - A new `sessions --student` command lists sessions.

## Settings
Added to `settings.toml` in this step (`quick_parts` and `pattern_min_sessions` follow in step 05):

```toml
[session]
gap_minutes = 30           # a longer gap starts a new session
fatigue_min_minutes = 25   # no fatigue call before this
fatigue_window = 4         # pieces of evidence in the rolling mean
fatigue_threshold = -0.25  # mean surprise at or below this = doing worse than expected
fatigue_min_parts = 2      # the drop must span at least this many parts
fatigue_slip_add = 0.15    # extra slip while fatigued
slip_cap = 0.40
signal_window = 6          # exchanges used for the supporting signals
stuck_attempts = 3
stuck_below = 0.5
```

## Commits
1. `feat(db): add derived session signals table`
2. `feat(learner): derive sessions and surprise from events`
3. `feat(learner): detect fatigue and soften evidence while fatigued`
4. `feat(learner): detect parts a student is stuck on`
5. `feat(cli): show current session and list sessions`

## Done when
Checked by hand with `example-mini`:
- **Fatigue:** a scripted 50-minute session runs, with good answers early, then wrong answers after minute 30 on 2+ parts the student was previously right on.
  - Fatigue starts at the right minute.
  - Those wrong answers lower `p_known` less than the same answers outside fatigue.
- **Not fatigue:** wrong answers on hard, new parts early in a session do not trigger fatigue (low `p_before`, so the surprise is small).
- **Stuck:** three failed explain-backs on one part mark it as stuck, not fatigued.
- **Rebuild:** `rebuild` reproduces `evidence_derived` and the state exactly.
