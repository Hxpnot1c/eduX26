# Build plan

This folder is the build plan for Synapse, the learning service: an MCP server that a school's chatbot connects to. It holds the course as a knowledge graph built from real exam material, keeps a learner model for each student, and tells the chatbot how to teach that student each turn.

- `reference/`: what we're building. Read the relevant reference file before each step.
- `steps/`: the order to build it in, one branch and pull request per step.

## Steps

| Step | Branch | What it delivers |
|---|---|---|
| [01](steps/01-scaffold.md) | `build/01-scaffold` | Full folder and file layout, with stubs only. Merged before any real code |
| [02](steps/02-content-and-ingest.md) | `build/02-content-ingest` | Course-pack format, content database, validation, loading, teacher feedback overlay, exam weights |
| [03](steps/03-graph-lookups.md) | `build/03-graph-lookups` | Tree, edge and note lookups |
| [04](steps/04-learner-model.md) | `build/04-learner-model` | Learner database, event logs, state rebuilt from events, decay, nudges, scheduling, teaching policy |
| [04b](steps/04b-evidence-log.md) | `build/04b-evidence-log` | Evidence as an event: chat evidence with exchanges, immediate-recall discount, replay in rebuild |
| [04c](steps/04c-session-signals.md) | `build/04c-session-signals` | Sessions from events, surprise against the model's expectation, fatigue (softened evidence) and stuck parts |
| [05](steps/05-server-context.md) | `build/05-server-context` | MCP server over HTTP: learning context, exchange logging, progress, profile; context assembled from configurable blocks |
| [05b](steps/05b-one-call-per-turn.md) | `build/05b-one-call-per-turn` | One `tutor_turn` call per reply returning a short ordered plan; scores from mark points; call timing; reply length, interests and per-client formatting |
| [05c](steps/05c-lean-results.md) | `build/05c-lean-results` | Smaller results: move instructions sent once with short cues per step, style only when it changes, reference blocks per move, letter point ids, a result budget |
| [05d](steps/05d-point-by-point.md) | `build/05d-point-by-point` | Teaching one point per message with a quick check after each, a skip to the check, and an explain-back to finish the part |
| [05e](steps/05e-literacy-coaching.md) | `build/05e-literacy-coaching` | AI-literacy coaching: research questions answered in full with sources, plus one feedback line and one task; live how-AI-works checks when the chatbot fails; trusted sources; AI-literacy progress, all as stealth assessment |
| [05f](steps/05f-tune-from-research.md) | `build/tune-from-research` | Settings from the personalisation review: open-answer guess, exam-anchored shares, MCQ guess from options, a BKT sanity check at startup, surprise against expected success, review below a recall threshold, feedback wording |
| [05g](steps/05g-engagement-rules.md) | `build/engagement-rules` | In-session engagement rules, never stored as a trait: ways on after a passive streak (`offer_choice`), a two-option question before a repeated "show me", a weakest-point explain-back when coasting |
| [05h](steps/05h-personal-learning-rate.md) | `build/personal-learning-rate` | A per-student learning-rate offset, heavily shrunk towards the population rate, built from earlier surprise, replayed in rebuild, never shown as a label |
| [05i](steps/05i-priorities.md) | `build/priorities` | Add-on steps (extend, the best due review, or nothing) and the order of reviews and prerequisite repairs follow expected marks, counting the student's own homework, class tests and mocks, with a reason and a log of the candidates not picked |
| [05j](steps/05j-reply-style.md) | `build/reply-style` | Reply length per step follows mastery and fatigue (the student's own length always wins); a `diagram` flag on parts adds a draw-or-sketch cue |
| [05k](steps/05k-tune-from-research-fixes.md) | `build/fix-tune-from-research` | Fixes to 05f: `review_when_below` edge cases confirmed; feedback's secure flag read before the answer (#23, #24, #26) |
| [05l](steps/05l-engagement-rules-fixes.md) | `build/fix-engagement-rules` | Fixes to 05g: question first, then the show; stop returns a session summary; extend offered only when earned; weakest point from the last 5 answers (#28–#30) |
| [05m](steps/05m-personal-learning-rate-fixes.md) | `build/fix-personal-learning-rate` | Fixes to 05h: learning rate recalibrated to the research; first answers and AI-literacy evidence left out (#31, #32) |
| [05n](steps/05n-priorities-fixes.md) | `build/fix-priorities` | Fixes to 05i: `move_chance` removed from the value score; edge choices confirmed (#35, #36) |
| [05o](steps/05o-reply-style-fixes.md) | `build/fix-reply-style` | Fixes to 05j: a longer `answer_length` raises `teach_point` only to 120 words (#38, #39) |
| [05p](steps/05p-synapse-rename.md) | `build/synapse-rename` | The product is called Synapse everywhere a user sees it; internal identifiers stay until after the competition |
| [05q](steps/05q-class-coverage-and-starting-points.md) | `build/class-coverage-and-starting-points` | Classes and a coverage record; starting points by coverage, with the forgetting clock from the taught date; personal starting offsets split by sector; prerequisites feed forward; richer open answers count for more |
| [05r](steps/05r-learner-cache.md) | `build/learner-cache` | Learner offsets cached per session, cleared on rebuild (#34) |
| [05s](steps/05s-fatigue-time-on-task.md) | `build/fatigue-time-on-task` | Fatigue from time on task and rapid guesses, replacing the 4-answer rule; fatigue curves per student and per class |
| [05t](steps/05t-bridge-ending.md) | `build/bridge-ending` | The reply's ending in a fixed order: urgent review, a bridge question towards the next topic, extend, other reviews |
| [05u](steps/05u-class-assessments.md) | `build/class-assessments` | Teacher-set class tests and assignments, in-chat deadline reminders, and `plan_my_study` day-by-day plans |
| [05v](steps/05v-exchange-nudge-ceiling.md) | `build/fix-exchange-nudge` | An ordinary exchange can raise a part only up to `nudges.ceiling` (0.40); `protocol` v0.3 (C1) |
| [05w](steps/05w-result-size-as-sent.md) | `build/fix-result-size` | Results sent as compact JSON and sized as sent; levels-only progress kept within the budget; a logging failure can't replace a result (C15, C16) |
| [05x](steps/05x-data-handling.md) | `build/data-handling` | Opaque student ids, hashed keys, `delete-student`, `export-student`, `leave-student` and `purge`, retention settings, no stored message text (migration 014) |
| [05y](steps/05y-formative-literacy-wording.md) | `build/formative-literacy-wording` | Ask and Verify shown as formative with the evidence behind each level; asking for sources earns Ask credit only alongside a Verify moment (C3) |
| [05z](steps/05z-calibration.md) | `build/calibration` | "How sure are you?" after a check answer (the feedback held back one turn), stored as an event, and a calibration line in the progress view after 5 rated answers (C7; migration 019) |
| [06](steps/06-demo.md) | `build/06-demo` | Demo seeding script, README, tunnel and connector set-up |
| [08](steps/08-tests.md) | `build/08-tests` | Unit tests with pytest: a fixture that loads the example pack into a throwaway folder, settings checks, learner-model core, rebuild, and the instruction and result size gates |
| [Later](steps/later.md) | | Checks (past-question, explain-back, link, find-the-error), automated tests, student and teacher pages, extras |

Checks and tests come after the base works end to end; the step files say where they will plug in.

## Working rules

**Branches and pull requests**
- One branch per step, created from the latest `main`. Never commit directly to `main`.
- Open a pull request when the step's "done when" list is met. Merge with **rebase and merge**, so `main` keeps a linear history of meaningful commits.
- Start the next step from the updated `main`.

**Commits**
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`, with a short imperative summary (≤ 72 characters).
- One logical change per commit. Each step file lists the commits it expects; small deviations are fine.
- No work-in-progress commits, no commented-out code, no generated databases, no secrets.
- Commit and pull-request messages describe the change only. They contain no tool or assistant attribution, co-author trailers, session links or "generated with" lines.

**Pull-request description**
```
## What
<one paragraph>

## How to check
<commands to run and what you should see>

## Notes
<decisions, follow-ups>
```

**Decision records**
- A change that alters the learner model, a setting, what a student or teacher sees, or what is stored about a student comes with a record in [`docs/decisions`](../decisions/README.md), written in the same pull request. It states the research behind the change and how well established that is.
- The pull request description ends with "Docs updated: …" and names the record.

**Code**
- Python 3.11+, SQLite, MCP Python SDK `mcp>=1.30,<2`.
- Every teaching or scoring number lives in `settings.toml`. What the chatbot sees is configured in `context.toml` and the `text/` folder. Nothing else hard-codes them.
- If something in the plan conflicts with what you find (for example an SDK API has changed), stop and raise it in the pull request rather than guessing.
