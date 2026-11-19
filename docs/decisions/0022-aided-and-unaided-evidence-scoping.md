# 0022. Aided and unaided evidence: scoping (not built)

- **Status:** Held for Vishnu
- **Date:** 2026-11-19
- **Decision owner:** Vishnu
- **Audit item:** C8 in [0002](0002-research-alignment-register.md)

## Context

The strongest warning in the research is that help improves performance while it is given and can hurt performance once it is taken away (Bastani et al., PNAS 2025: a GPT-4 tutor group scored 48% higher on practice but 17% lower on the later unaided test; a guarded tutor removed the harm). Synapse's levels should therefore rest on **unaided** evidence. What the code does today:
- Chat evidence soon after a worked example or hint on the part (30 minutes) is "immediate": a higher guess rate, so it moves the estimate less ([learner-model](../build/reference/learner-model.md)).
- Checks, reviews and explain-backs are not marked either way. A check asked straight after teaching in the same session counts like a check a week later.
- `request_type = homework` is accepted and labelled, but changes no plan and no scoring.
- The exchange nudge is capped below the "new" ceiling (0.35) by [0003](0003-cap-the-exchange-nudge.md), so chat cannot make a part secure alone.

## Options

1. **Do nothing; document.** The immediate discount and the nudge ceiling already stop the worst case. State plainly in the pitch that levels include same-session checks.
2. **Secure needs one unaided correct answer.** A part cannot be shown as `secure` unless one correct check or review exists that came at least `X` hours after the last teaching step on that part (starting value to be chosen; no source gives one, so a judgement call). Below that it is shown as `developing`. Cheap, explainable, aligned with the spaced-retrieval research, but it changes demo levels and delays "secure" for a student who did everything right in one sitting.
3. **An `aided` flag on evidence** (migration), set when a worked example, hint or "just show me" came in the same turn or the turn before, used both in scoring (as `immediate` does) and in the progress view ("3 of 5 checks were unaided"). Richer, needs a migration and a rebuild, and the aided definition needs care.
4. **Homework mode:** when the student labels a request `homework`, offer only a hint ladder and score nothing. Overlaps the held better-reteach work (C12).

## Recommendation

Option 2 first (smallest change that answers the research), with option 4 folded into the held C12 work. Do not build option 3 until there are real logs to show how often evidence is aided.

## Research basis

Bastani et al. (2025) and OECD Digital Education Outlook (2026) for the harm of unguarded help; Cepeda et al. (2008) and Carpenter, Pan & Butler (2022) for delayed retrieval; Soderstrom & Bjork (2015) for performance during learning not predicting learning. The **threshold in option 2 is not from research**.

## What would change our mind

A pilot showing students are rarely given help before a check (making the rule redundant), or the simulation (`scripts/simulate_review_threshold.py` style) showing option 2 delays secure for most students with no gain in retention.
