# Step 05s: Fatigue from time on task, and rapid guesses

Branch `build/fatigue-time-on-task`, from `main` after step 05r. This replaces the rule questioned in #24.

## Built, and deferred
**Built in the first pull request (migration 015):** the time-based slip; rapid guesses (`this_message.words`, latency, question words stored on the exchange; `evidence_derived.rapid`); the new fatigued-mode rule (50 minutes or the 2nd rapid guess) replacing the 4-answer rule and its settings; the plain pacing lines (`text/fatigue/`, sent as `data.line`); and **the stored `study_pattern` removed** (audit item C4, Vishnu's decision). Tests: `tests/test_time_on_task.py` (9) and two `check_mcp` checks.

**Deferred to a follow-up:** the `answer_timing` table, `fatigue-curve` in the CLI, the per-class curve and its school setting (`fatigue.class_curve_enabled`). The class curve needs the classes from step [05q](05q-class-coverage-and-starting-points.md), and the teacher mock-up's chart is labelled seeded data either way.

## What
A student's answers can't reliably show tiredness at chat pace. Our simulation of the current 4-answer rule flagged 77% of not-tired students by 60 minutes. So fatigue now follows the published time-on-task curve, plus rapid guesses.

**Remove:**
- the 4-answer-average start rule in `learner._fatigued`;
- its settings: `session.fatigue_window`, `fatigue_threshold`, `fatigue_min_parts`, `fatigue_slip_add`, and `fatigue_min_minutes`, which `fatigue.mode_minutes` replaces;
- any "slow answer" idea.

`session.slip_cap` stays.

1. **Time-based slip.**
   `extra_slip(minutes into session) = 0 before 28; then 0.002 per minute after 28; capped at 0.12`
   - It's added to the evidence type's slip, within `session.slip_cap`, in both the expected-success calculation and the BKT update.
   - So it's 0 at 27 minutes, 0.044 at 50, and reaches the 0.12 cap at 88 minutes.
2. **Rapid guesses.** An answer is a rapid guess when it arrives faster than reading the question at 300 wpm plus typing the answer at 52 wpm.
   - **Latency:** the time since the previous `tutor_turn` in the session (from `call_log`). It includes the chatbot's generation time, which makes flags less likely; that's the safe direction.
   - **Question words:**
     - MCQs: the server-built stem plus options;
     - otherwise: the step's reference text, as a proxy.
   - **Answer words:** `this_message.words`, the word count of the student's message, is added to the tool input. It's short, and no text is stored.
   - Latency, question words and answer words are stored on the exchange when it's logged. So the flag is replayable, and a rebuild stays identical.
   - **Effects:**
     - a rapid-guess answer gets weight 0 for knowledge (the effort-moderated idea);
     - it's counted in the session.
3. **Fatigued mode** (shorter replies, no literacy checks, short reteach) starts at either:
   - `fatigue.mode_minutes` (50) into the session; or
   - the `fatigue.rapid_guesses` (2nd) rapid guess in the session.

   It lasts until a new session (a gap of `session.gap_minutes`, 30, or more).
   - The existing fatigued `offer_choice` fires when the mode starts.
   - At 50 minutes, its text includes a short break line ("a short break helps it stick"), via a cue variant.
   - **There's no break offer before 50 minutes.**
   - For 2 rapid guesses, the offer has `reason = rapid`, with options to switch to something different (`quick`) or `stop`.
   - `evidence_derived.fatigued` now means "in fatigued mode". The learning-rate offset still leaves those answers out.
4. **Fatigue-curve tracking.**
   - **Derived table** `answer_timing(evidence_id, student_id, session_id, minutes, score, expected_no_time_slip, rapid)`. It's built from existing timestamps and the stored exchange fields, so a rebuild stays identical.
   - **Per student:** mean shortfall from expected, and rapid-guess rate, in 10-minute bins (0–10 … 60+), across sessions.
   - **Per class, aggregate only:**
     - the same curve, with answers and students per bin, beside the research curve;
     - bins with fewer than `fatigue.min_students_per_bin` (5) students hidden;
     - a session-length distribution.
   - **Where it shows:**
     - `fatigue-curve --student … | --class …` in the CLI;
     - `fatigue-curve … --json` for the teacher mock-up's chart, from seeded data and labelled "seeded data".
   - **Caveat (in the docs):** students who choose long sessions may differ from those who stop early. So the class curve describes your students' sessions, not pure fatigue.

## Why, with sources
- **Time-based slip:**
  - Randles, Harlow & Inzlicht (2017): a decline from about 28 minutes, and 4–5 points by about 50.
  - The cap comes from end-of-test declines of 7.5–12% (Brown, Kaur, Kingdon & Schofield; TIMSS), picking 12.
- **Fatigued mode at 50 minutes and new sessions after 30:**
  - Randles et al. (2017);
  - Sievertsen, Gino & Piovesan (2016): breaks restore performance;
  - Lee (2018): off-task gap cut-offs of 10–60 minutes.
- **The thresholds:**
  - Brysbaert (2019): 238 wpm mean reading, 175–300 range. 300 is used so fewer students are flagged wrongly.
  - Palin et al. (2019): 36 wpm on phones. Dhakal et al. (2018): about 52 on keyboards. 52 is the conservative pick.
- **The method:** Wise & Kong (2005); Wise & Ma (2012). The weight-0 treatment follows Wise & DeMars (2006).
- **No slowness or variability signal:**
  - Boksem et al. (2005): only +5.2% reaction time after 3 hours;
  - Esterman et al. (2013): variability needs many responses a minute.
- **Persistence varies between people** (Wu, Debeer et al., 2019), hence the per-student curves.
- Full rows are in `reference/research.md`, under "Fatigue, timing and rapid guesses".

## Who sees the curves
`docs/research/personalisation.md` §5 says fatigue shown to teachers is non-core and off by default, and personal traits are never shown as labels. So:
- **The class aggregate** sits behind a school setting, `fatigue.class_curve_enabled`. It is off by default.
  - It is on in the demo seed, labelled "seeded data": `scripts/demo.sh` sets `EDUX_FATIGUE_CLASS_CURVE=1`, like `EDUX_PERSONALISATION`.
  - With it off, `fatigue-curve --class` says it's off and shows nothing.
  - Bins with fewer than 5 students are hidden.
  - It is listed in `docs/build/reference/dpia-notes.md`.
- **Per-student curves are CLI only.** There is no per-student teacher view.
- `later.md` gets a line saying a per-student teacher view would come only behind a DPIA.

## Files
- **Migration:** the next free number when you start. It adds:
  - `exchange_log.answer_words`, `question_words` and `latency_s`;
  - the `answer_timing` table.
- `edux/learner.py`:
  - `extra_slip`, used in `apply_evidence_event` and `_apply_evidence`;
  - `rapid_guess`;
  - `_fatigued` rewritten (time or rapid count);
  - `session_state` (rapid count, mode reason);
  - `answer_timing` rows and `fatigue_curve(student | class)`.
- `edux/service.py`, `edux/server.py`:
  - `this_message.words`;
  - question words from the last plan;
  - latency from `call_log`.
- `edux/plan.py`: the fatigued offer's reason (`fatigued` / `rapid`) and the break cue at 50 minutes.
- `edux/context_blocks.py`: the session block's reason.
- `edux/cli.py`: `fatigue-curve`; `sessions` shows rapid guesses.
- `edux/demo.py`: seeded sessions long enough to show a curve.
- `text/moves/offer_choice_break.cue.md`, `offer_choice_rapid.cue.md`, and `text/tools/tutor_turn.md` (`this_message.words`).
- `settings.toml`: remove the old keys; add `[fatigue]`.
- `scripts/demo.sh`: turns the class curve on for the demo.
- `docs/build/reference/dpia-notes.md`: lists the class fatigue curve (non-core, school setting, off by default).
- `scripts/check_mcp.py`: a `fatigue` run.
- **Docs:**
  - this file;
  - `reference/learner-model.md`;
  - `reference/settings.md` (labels);
  - `reference/database.md`;
  - `reference/tools-and-context.md` (`this_message.words`);
  - `reference/research.md` rows if anything ends up different.
- `later.md` already lists the school-fitted curve and per-student persistence (docs PR). Update them if they change.

## Settings
```toml
[fatigue]
slip_start_minutes = 28      # from research: Randles, Harlow & Inzlicht (2017)
slip_per_minute = 0.002      # from research: 4–5 points by about 50 minutes (Randles et al. 2017)
slip_max = 0.12              # from research: end-of-test declines of 7.5–12% (Brown, Kaur et al.; TIMSS), picking 12
mode_minutes = 50            # from research: Randles et al. (2017)
rapid_guesses = 2            # judgement call, starting value
read_wpm = 300               # from research: Brysbaert (2019), top of the 175–300 range
type_wpm = 52                # from research: Dhakal et al. (2018) keyboards; Palin et al. (2019) phones are slower
min_students_per_bin = 5     # from personalisation.md §5: minimum cell size
bin_minutes = 10             # judgement call
class_curve_enabled = false  # school setting, off by default (personalisation.md §5: non-core); on in the demo seed
```

## Commits
1. `refactor(learner): remove the four-answer fatigue rule and its settings`
2. `feat(learner): add slip that grows with time on task`
3. `feat(server): take the student message's word count`
4. `feat(learner): flag rapid guesses and give them no weight` (migration)
5. `feat(learner): start fatigued mode at 50 minutes or the second rapid guess`
6. `feat(plan): add the break line and the rapid-guess offer`
7. `feat(learner): record answer timing for fatigue curves`
8. `feat(cli): show fatigue curves per student and per class`
9. `feat(demo): seed sessions that show a fatigue curve`
10. `chore(scripts): check time slip, rapid guesses and fatigued mode`
11. `docs(reference): document time-on-task fatigue and rapid guesses`

## Done when
- Slip is 0 at 27 minutes, 0.044 at 50, and capped at 0.12.
- A rapid answer is flagged, given weight 0 and counted.
- Fatigued mode starts at 50 minutes or on the 2nd rapid guess, and ends with a new session.
- There's no break offer before 50 minutes.
- Curve bins are correct, and small-class suppression works.
- The class curve is off by default, and on with the school setting.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported. Cues don't count; if the `offer_choice` section changes, cut first.

## Tests
In `scripts/check_mcp.py` (`fatigue`), one check per item under Done when.
