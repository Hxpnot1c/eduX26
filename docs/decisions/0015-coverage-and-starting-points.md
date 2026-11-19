# 0015. Classes, coverage and starting points

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (decided 18 November; the boost, the cap and the display rule are his)
- **Pull request:** #58
- **Step:** [05q](../build/steps/05q-class-coverage-and-starting-points.md) (Part 2 B)

## Context

Synapse started every part at the same prior (0.30, shifted by difficulty), whatever the student's class had been taught, and treated a student's first answers like any others. The research says students differ mainly in where they start, not how fast they learn (Koedinger et al., 2023, with the caveat that the learning-rate result is sensitive to how many practice opportunities are included). A part the class was taught three weeks ago should not start where an untaught one does, and a student who shows they already know a topic before it is taught should start higher on similar parts. Four risks needed handling: a starting number that reads like a result, personal profiling of a minor, a cross-student estimate, and forgetting that erases anything not practised.

## Decision

1. **Classes and a coverage record** (migration 016): which sections a class has been taught and when, set by a teacher (CLI, CSV, export for the mock-up's tick-list) or by the student for themselves (`update_my_profile(covered_in_class)`). Coverage is profile, not events; a row counts from its `taught_on` date.
2. **A covered part starts 0.5 log-odds above its normal start** (0.30 becomes about 0.41), and its forgetting clock starts on the taught date. It is due for review (reason `taught_in_class`) without ever being practised here.
3. **A personal starting adjustment, split by sector** (covered and not covered never mix), from the student's first answers when they came before any teaching, shrunk with k = 25 and bounded at ±1.5 logits. **A prerequisite shift** moves a new part by half the average change in its answered prerequisites.
4. **The combined starting point is at most 0.65.** Answers can take a part anywhere.
5. **Display:** a part with no answer never shows "developing" or "secure": a covered one shows "taught in class, not yet checked", any other "new". The planner still uses the number.
6. **The class estimate stays off** (school instruction only, at least 5 students, never more than 0.075 below the boosted start), with a student notice while it is on.
7. **The explain-back guess falls as mark points rise** (0.20, 0.15, 0.10).
8. **Two judgement additions:** a part taught in class and never answered forgets only to its untaught start; and the prerequisite shift counts only prerequisites the student has answered on.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Koedinger, Carvalho, Liu & McLaughlin (2023), *PNAS* 120(13) | Starting accuracy varied widely (about 55% to 75% between lower and upper halves of a class) while learning rate was similar; gaps follow learning opportunities. | Large analysis; replicated (Simpson et al., 2024) | Online practice systems; the rate result is fragile to sequence length (Lee et al., 2026). |
| Pardos & Heffernan (2010), UMAP | Setting a student's own prior, even from first responses, improved prediction. | Single study; less stable later | Older ASSISTments data. |
| Simpson, Norberg & Fancsali (2024), EDM | Starting-knowledge SD about 0.57 to 0.90 logits, implying k of about 18 to 44; 25 is the middle. | Replication, one vendor | Maths. |
| Yudelson, Koedinger & Gordon (2013), AIED | The counterpoint: student-specific learning speed helped more than a student-specific prior. | Single study | Recorded, not resolved. |
| Soderstrom & Bjork (2015) | Performance straight after teaching shows the student followed it, not that they knew it, so only pre-teaching answers feed the start. | Review | Lab tasks. |
| Käser et al. (2014, 2017) | Modelling skill links beats plain BKT; they give no weight, so 0.5 is a judgement call. | Single studies | Not a weight. |
| Bhattacharjee & Wayllace (2025), AIED | Deep models struggle on new students; an explicit prior is needed. | Single study | ASSISTments. |
| Doroudi & Brunskill (2019), LAK | Knowledge tracing can be inequitable under misspecification, so log which prior was used and keep it weak. | Simulation-based | Direction only. |
| ICO Children's Code, Standard 12 | Profiling off by default unless there is a compelling reason, which is why the cross-student class estimate is off. | Regulatory guidance | Not about education specifically. |

Labels: `coverage.boost_logit` (0.5), `starting.cap` (0.65) and `propagation.forward_weight` (0.5) are **judgement calls, starting values**; `starting.k` (25), `starting.bound_logits` (1.5) and `coverage.class_k` (25) are **from research plus our simulation**; `class_min_students` and `class_max_down` follow the personalisation review (§5, §7).

## Alternatives considered

- **A fixed covered prior of 0.50** (the first design). It ignored the part's difficulty; the boost respects it.
- **Show the starting number as a level.** Rejected: a starting point is a prior, not a result, the same argument as the nudge ceiling.
- **Let forgetting run to zero.** Made a taught part look weaker than an untaught one (0.00 against 0.30); the floor fixes it without changing answered parts.
- **Feed unanswered prerequisites forward.** Double-counts forgetting for covered dependents.
- **Turn the class estimate on.** Cross-student profiling; off by default and in the demo.

## Consequences

- The demo class (`demo-class`) has its first two Theme 1 concepts (PED, PES) marked as taught 25 days ago. **Levels per part for the demo students, `main` before the series and after this step** (number, level):
  - `demo-secure`: ped_definition 0.86 → 0.85 secure; ped_formula 0.30 → 0.30 new; **ped_values 0.38 new → 0.41 developing by number, but shown as "taught in class" because it has no answer**; pes_definition 0.46 → 0.46 developing; pes_formula 0.82 → 0.80 secure; the rest unchanged.
  - `demo-weak`: ped_definition 0.16 → 0.05 new and ped_formula 0.15 → 0.04 new (their answers were wrong and have faded since the class was taught); the rest unchanged and new.
  - `demo-showme`: ped_definition 0.96 → 0.93 secure; pes_definition 0.20 → 0.19 new; the rest unchanged.
  - Unanswered covered parts sit at their normal start (0.30) because forgetting stops there, and read "taught in class". No part shows developing or secure without an answer.
- `get_my_progress` may show `taught_in_class` levels; chatbots must say it in plain words.
- Teachers can record coverage without a UI; the mock-up's tick-list reads the JSON export.
- Migration **016**. Instruction word count unchanged (899 of 900).
- `docs/build/reference/dpia-notes.md` (in pull request #56) needs a line for the coverage tables and the class estimate when both are merged.

## Verification

`tests/test_coverage_and_starting_points.py` (36 tests): boost respects difficulty; dated-after coverage ignored; the clock; reviews; the display rule; sector separation; post-teaching answers excluded; finite bounded offsets; feed-forward and its stop; the cap; literacy untouched; the explain-back guess; the class estimate off, below 5 students, and floored; the notice; student coverage; rebuild identical. `scripts/check_mcp.py` passes (new coverage run); rebuild identical.

## What would change our mind

A pilot showing the boost or the offsets do not improve prediction on held-out first answers; or evidence on the right size of the boost for A-level students; or a school asking for the class estimate (then a DPIA entry first).
