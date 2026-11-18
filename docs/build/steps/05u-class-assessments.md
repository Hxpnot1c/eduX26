# Step 05u: Class assessments, reminders and study plans

Branch `build/class-assessments`, from `main` after step 05t.

## What
1. **Class-level assessments.**
   - `student_assessment` gets a nullable `class_id`, and `student_id` becomes nullable. A check requires exactly one of the two.
   - New kind: `written_assignment`.
   - CLI: `assessment add --class … --name … --kind … --date … --topics …`. The teacher mock-up gets the same form; its fields match the CLI.
   - Priorities and `days_to_exam` count the student's own assessments plus their class's.
   - A student can't remove a class assessment through `update_my_profile`.
2. **Deadline reminders.** The first `tutor_turn` of a session includes `upcoming` for assessments due within `reminders.days_ahead` (7): name, kind, due date and days left. It comes with a one-line cue.
   - It appears once per session.
   - It doesn't appear when the student is fatigued.
   - Synapse can't push notifications, so this is in-chat only. The docs say so.
3. **Study plan on request:** a new tool, `plan_my_study(assessment_id?)`. With no id, it uses the soonest upcoming assessment. It returns a day-by-day plan from today to the due date:
   - **Sessions:** `plan.sessions_per_week` (3). The student can say otherwise through a `sessions_per_week` argument.
   - **Order:** the parts the assessment covers, by predicted weakness on the due date (`p_on`). Repeats are spaced by the existing gap rules.
   - **The last session before the date** is mixed practice.
   - **For `written_assignment`:** stages tied to how it's marked (knowledge, application, analysis, evaluation), each with a date. **Synapse never writes the content.** Each stage says what to do, not what to write.
   - The result stays within 2,400 characters. The tool description doesn't count towards the instructions cap.

## Why, with sources
- **Concrete plans with days and topics:**
  - implementation intentions improved outcomes, d = .27–.66 (Sheeran, Listrom & Gollwitzer, 2024, meta-analysis; Gollwitzer & Sheeran, 2006);
  - with mental contrasting, high-school students completed over 60% more practice questions (Duckworth et al., 2011).
- **Write-up plans never write the content:** unacknowledged AI use in assessed work can be malpractice (JCQ, 2025); tools shouldn't hand over final answers by default (DfE, 2026).
- **Spacing towards the class's tests** (Cepeda et al., 2008), as in step 05i.
- **No push reminders:** Synapse runs only when the student messages (`reference/research.md`, "Considered and not adopted").

## Files
- **Migration:** the next free number when you start. It changes `student_assessment` (nullable `student_id`, `class_id`, and a check that exactly one is set). SQLite needs a table rebuild for this, done in the migration.
- `edux/learner.py`:
  - `assessments` includes class assessments;
  - `ASSESSMENT_KINDS` gains `written_assignment`;
  - `upcoming(student_id, at, days)`;
  - `study_plan(student_id, assessment_id, sessions_per_week, at)`.
- `edux/service.py`, `edux/server.py`:
  - `upcoming` on the first turn of a session;
  - the `plan_my_study` tool.
- `edux/cli.py`: `assessment add --class …`.
- `text/tools/plan_my_study.md`, `text/cues/upcoming.md`.
- `settings.toml`: `[reminders]`, `[plan]`.
- `scripts/check_mcp.py`: an `assessments` run.
- `docs/build/steps/later.md`: the Teams, Google Classroom and calendar items are already listed (docs PR). Remove the "planned in step 05u" bullet from "Priorities, next".
- **Docs:** this file; `reference/database.md`; `reference/tools-and-context.md`; `reference/settings.md` (labels); `reference/research.md` rows if anything ends up different.

## Settings
```toml
[reminders]
days_ahead = 7            # judgement call, starting value

[plan]
sessions_per_week = 3     # judgement call, starting value; the student can say otherwise
```

## Commits
1. `feat(learner): let assessments belong to a class` (migration)
2. `feat(cli): add class assessments`
3. `feat(learner): add written assignments as an assessment kind`
4. `feat(service): remind about assessments due this week, once a session`
5. `feat(server): add plan_my_study for a day-by-day plan`
6. `feat(learner): stage written-assignment plans by how they are marked`
7. `chore(scripts): check class assessments, reminders and study plans`
8. `docs(reference): document class assessments, reminders and plan_my_study`

## Done when
- Class assessments reach every class member's priorities.
- The reminder appears once per session, and only within 7 days.
- The plan covers the right parts, is spaced, and ends with mixed practice.
- The written-assignment plan has stages and no content.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported.

## Tests
In `scripts/check_mcp.py` (`assessments`), one check per item under Done when.
