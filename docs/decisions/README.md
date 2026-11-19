# Decision records

Short records of the decisions behind changes to Synapse, with the evidence each one rests on. Each record answers four questions:

1. What did we decide?
2. Why? What does the research say, and how well is it established?
3. What else did we consider?
4. How do we know it works, and what would change our mind?

They sit beside [`docs/build/reference/research.md`](../build/reference/research.md). That file lists the evidence for each teaching and modelling choice. These records explain how a specific *change* follows from that evidence, or why it is a judgement call.

## When to write one

Write a record in the same pull request whenever a change:

- alters what the learner model computes, what a student or teacher sees, or what is stored about a student;
- adds, removes or retunes a number in `settings.toml`;
- is made because of the research, or departs from it.

Pure refactors, typo fixes and test-only changes do not need one.

## File names and numbering

`NNNN-short-title.md`, numbered in the order the records are created. Take the next free number when you open your branch. If two branches take the same number, the one merged second renumbers.

Write in British English, in plain sentences. Keep each record to one page where you can.

## Status values

| Status | Meaning |
|---|---|
| Proposed | Written, not yet agreed. The pull request is open. |
| Accepted | Agreed and merged. |
| Held | Agreed in principle but deliberately not started (for example the held list in the handover). |
| Superseded by NNNN | Replaced by a later record. Keep the old one; do not delete it. |

A product call is anything that changes what a student or teacher sees, a claim in the pitch or paper, or an item on the held list. A record that contains a product call says **Decision owner: Vishnu** and stays *Proposed* until Vishnu confirms.

## How to cite research

- Give the author, year and venue in full. A reader should not need another file to find the source.
- Say how well the claim is established, using these words: **replicated**, **single study**, **review or meta-analysis**, **abstract only** (we have not read the full text), **our simulation** (synthetic students, never a learning gain), or **judgement call** (no source; a starting value to refit from real data).
- The numbered ids (for example `G1-90`) refer to the project's literature review, which lives outside this repository. They are for the team. The full citation is always repeated in the record.
- Say what the evidence does **not** show. Most of it comes from adults, lab tasks or other subjects, and very little from A-level Economics.
- Do not quote exam-board text. Do not reuse tutor2u content.

## Template

```markdown
# NNNN. Title

- **Status:** Proposed | Accepted | Held | Superseded by NNNN
- **Date:** YYYY-MM-DD
- **Decision owner:** (omit unless this is a product call)
- **Pull request:** #nn
- **Audit item:** (the code from record 0002, if any)

## Context
What was wrong or missing, and where in the code or docs.

## Decision
What we are doing, stated plainly. Name the files and settings.

## Research basis
| Source | What it shows | How well established | Limits |
|---|---|---|---|

## Alternatives considered
Each with the reason it was not chosen.

## Consequences
What changes for students, teachers, the demo, stored data and the instruction word count. What gets worse.

## Verification
The commands and checks that show it works.

## What would change our mind
The result that would make us revisit this.
```

## Index

| No. | Title | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Record decisions with their research basis | Accepted |
| [0002](0002-research-alignment-register.md) | Research alignment register | Proposed |
| [0003](0003-cap-the-exchange-nudge.md) | Cap what an ordinary exchange can do to a part's estimate | Proposed |
| [0004](0004-count-results-as-sent.md) | Count tool results as they are sent, and keep every default result inside the budget | Proposed |
| [0005](0005-name-the-product-synapse.md) | Name the product Synapse; eduX is the competition | Proposed |
| [0006](0006-judge-secure-feedback-before-the-answer.md) | Judge feedback's "secure" flag on the level before the answer | Proposed |
| [0007](0007-personal-learning-rate-off-by-default.md) | Recalibrate the personal learning rate and switch it off by default | Proposed |
| [0008](0008-drop-move-chance-from-the-value-score.md) | Drop the learning-chance factor from the priority value score | Proposed |
| [0009](0009-cap-teach-point-under-a-longer-answer-length.md) | Cap teach_point at 120 words under a longer answer length | Proposed |
| [0010](0010-engagement-rule-fixes.md) | Engagement rules: question first, a session summary on stop, and less noisy signals | Proposed |
| [0011](0011-data-handling.md) | Opaque ids, hashed keys, and delete, export and retention | Proposed |
| [0013](0013-fatigue-as-pacing.md) | Fatigue becomes pacing: time on task and rapid guesses | Proposed |
| [0014](0014-formative-literacy-and-ask-scoring.md) | Ask and Verify are formative practice feedback, and asking for sources earns nothing alone | Proposed |
| [0015](0015-coverage-and-starting-points.md) | Classes, coverage and starting points | Proposed |
| [0016](0016-learner-offset-cache.md) | Cache the per-session learner offsets | Proposed |
| [0017](0017-bridge-ending.md) | End a finished part with a bridge question towards the next topic | Proposed |
| [0018](0018-class-assessments-reminders-plans.md) | Class assessments, deadline reminders and study plans | Proposed |

Each later record is added to this table in the pull request that introduces it.
