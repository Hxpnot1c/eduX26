# 0018. Class assessments, deadline reminders and study plans

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (new student-facing behaviour: a reminder and a planning tool)
- **Pull request:** #61
- **Step:** [05u](../build/steps/05u-class-assessments.md) (Part 2 F)

## Context

Priorities (step 05i) counted a student's own tests only, so a teacher's test had to be typed in by every student. Nothing told a student a test was close, and nothing helped them spread revision over the days left. Synapse runs only when a student writes, so it cannot push reminders.

## Decision

1. **Class assessments:** a teacher (CLI `assessment add --class`) sets a test or assignment for every member of a class; priorities and review timing count the student's own plus their class's. A student cannot remove a class one. New kind `written_assignment`.
2. **An in-chat reminder:** on the first call of a session, tests due within 7 days are listed once, with a neutral cue. Not in long-session or rushing mode. **The student can switch it off** (`update_my_profile(reminders=false)`).
3. **`plan_my_study`:** a day-by-day plan to the due date, weakest topics first, ending in mixed practice; for a written assignment, four dated stages tied to how it is marked, saying what to do and never what to write.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Sheeran, Listrom & Gollwitzer (2024); Gollwitzer & Sheeran (2006) | Implementation intentions ("when and where") improved goal attainment, d = .27 to .66. | Meta-analyses | Mostly other goals; not chat-generated plans. |
| Duckworth et al. (2011) | With mental contrasting, high-school students completed over 60% more practice questions. | Single study | One setting. |
| Cepeda et al. (2008) | Space reviews as a falling share of the time to the test; the plan puts the weakest first and repeats only after the others. | Experiment | Adults, trivia facts. |
| Fryer (2016); Oreopoulos et al. (NBER w25036); Bergman & Chan (2021) | Reminders to students alone had no measurable effect on outcomes; texts to parents reduced course failures. | Several studies | US samples; university students in some. |
| ICO Children's Code, Standards 5, 12 and 13 | No detrimental use of data, profiling off by default, no nudge techniques that weaken privacy. | Regulatory guidance | Standard 13's text is about data and privacy nudges, not reminders: the opt-out and plain wording are our design guidance. |
| JCQ (2025); DfE (2026) | Unacknowledged AI use in assessed work can be malpractice; tools should not hand over final answers by default. | Guidance | Not an experiment. |

`reminders.days_ahead` (7), `plan.sessions_per_week` (3) and `priorities.weight_written_assignment` (0.6) are **judgement calls, starting values**.

## Alternatives considered

- **No reminder.** The evidence says student-directed nudges rarely change outcomes, so the reminder is a courtesy, not a lever; it is cheap, once per session, and switch-off is one sentence.
- **Remind on every call.** Nagging; against the Code.
- **A plan that drafts the essay.** Against JCQ and DfE guidance and against the learning evidence (the work is the learning).
- **Calendar or Teams links.** Out of scope (held in `later.md`).

## Consequences

- Teachers can set a class test without a UI; the mock-up's form has the same fields as the CLI.
- A student sees one extra line at the start of a session when something is due soon, and can ask for a plan.
- A student's own tests now match any topic, concept or part (so "PED" works).
- Migration **018**. Instruction word count unchanged (899 of 900): the reminder cue and the plan wording are data and the tool text sits outside the instruction cap.
- **Open:** whether the reminder helps at all is untested; log whether students act on it before claiming anything.

## Verification

`tests/test_class_assessments.py` (16 tests); `scripts/check_mcp.py` (assessments run): the reminder appears once and not for a test 16 days away, `plan_my_study` stays within 2,400 characters and ends in mixed practice, a written assignment gets four stages and no sessions, a student cannot remove a class assessment; rebuild identical.

## What would change our mind

A pilot showing students ignore or dislike the reminder, or plans that are not followed; or a school asking for push reminders (then a DPIA entry first).
