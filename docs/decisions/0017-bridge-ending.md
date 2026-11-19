# 0017. End a finished part with a bridge question towards the next topic

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (changes what a student sees at the end of a reply)
- **Pull request:** #60
- **Step:** [05t](../build/steps/05t-bridge-ending.md) (Part 2 E)

## Context

When a reply has no question of its own (a part has just finished, or the reply only explains), Synapse added whichever of an earned extend or a due review had the highest value. Nothing pointed the student towards what comes next, and nothing used the class's coverage record (step 05q) to say where the class is going.

## Decision

Choose the ending in four tiers, each ordered by the value score: (1) a due review on a part covered by a test within 7 days; (2) a bridge question towards the next topic; (3) an earned extend; (4) any other due review. The bridge is the existing pre-question move on the target part's first key point, framed through the link, and carries the pack edge as `data.link`. The target is the class's next not-yet-covered section when a pack edge links it to the current part and its prerequisites are at least developing; otherwise the not-yet-taught part with the strongest link; otherwise none. After the answer the first teaching step says the student can stop or switch. No new move section (cues only), so the instruction word count is unchanged.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| St. Hilaire, Chan & Ahn (2024), *Psychonomic Bulletin & Review* | The prequestion effect: g = 0.54 across 97 comparisons, benefit mainly for the specific information asked about; larger when the learner generates an answer (g = 0.65 against 0.22 for reading). | Meta-analysis | Mostly adult lab studies. |
| Geller et al. (2017), *Cognitive Research: Principles and Implications* | In a STEM classroom, prequestions did not add to the benefit of retrieval practice. | Single classroom study | The school evidence is thin and mixed; none for A-level Economics. |
| Pan & Carpenter (2023), *Educational Psychology Review* | Pre-instruction testing often helps; the moderators are unclear. | Review | Does not cover transfer to a new topic. |
| Cepeda et al. (2008), *Psychological Science* | Review gaps should shrink as a share of the time to the test, which is why an urgent review comes first. | Experiment | Adults, trivia facts. |
| Doroudi, Aleven & Brunskill (2019), *IJAIED* | Hand-set orderings are hard to beat without data, so log the options not picked. | Review | Direction only. |

The tier order itself is a **judgement call**. The research supports the question's form (ask about the specific next point, not a vague "any thoughts?"), not the claim that a bridge improves learning of the next topic: no study tests that for A-level students, so the pitch should call it "supported in lab studies, untested here".

## Alternatives considered

- **Keep the single best-value choice.** Never points forward.
- **Put the bridge first.** Would delay a review for a test within a week, against the spacing evidence.
- **A bridge on every reply.** Only when the reply has no question of its own.

## Consequences

- A student who finishes a part now usually sees a short lead-in question on a linked, untaught part instead of an extend. They can stop or switch.
- `extend` is now a stop step (it ends in a question); before, a due review could be added after an extend, giving two questions in one reply.
- The bridge answer is pre-teaching evidence: it feeds the starting offset of its target's sector (step 05q).
- The candidates not picked are logged with their tier; nothing new is stored. Instruction words unchanged (899 of 900).

## Verification

`tests/test_bridge_ending.py` (12 tests): an urgent review beats the bridge; the bridge beats an earned extend; no link means no bridge; a target whose prerequisites are not developing is skipped; the target is untaught; coverage-next is preferred and carries its reason; a fallback to the strongest link; the evidence feeds the right sector; considered is logged. `scripts/check_mcp.py` (bridge run): the bridge appears with `data.link`, the answer gets feedback then a teaching step that says they can stop or switch, and `stop` gives the session summary.

## What would change our mind

A pilot showing students skip or dislike the lead-in question, or no gain on the next topic's first answers.
