# 0010. Engagement rules: question first, a session summary on stop, and less noisy signals

- **Status:** Proposed
- **Date:** 2026-11-18
- **Pull request:** #53
- **Step:** [05l](../build/steps/05l-engagement-rules-fixes.md) (issues #28, #29, #30)

## Context

Step 05g added in-session engagement rules (a repeated "just show me", a passive streak, a coasting explain-back). Review found three kinds of problem. The repeated show asked its two-option question but then did not give the show the student had asked for. Picking "stop" returned an empty plan, a pending literacy task could still be re-asked after it, and a passive streak always offered "extend" even to a student who had not earned it. The weakest point used all of a point's answers, so early misses that were later put right still counted, and a single passive first message could count as coasting.

## Decision

1. **Question first, then the show (#28).** After `show.max_per_part_session` shows, the next "just show me" first gets the two-option question (marked `data.then_show`). Its answer gets feedback and then the full show and its check, right or wrong, so a stuck student is never refused. The wrong option is a misconception the student holds on the part, else a watch-for one, else the first in pack order.
2. **Stopping (#29).** `stop` returns a new `session_summary` move: what was covered and the next review. It is treated like fatigue: a waiting literacy task or how-AI-works check is dropped unscored and not re-asked. The passive offer lists `extend` only when it is earned.
3. **Signals (#30).** The weakest point uses the mean of each point's last 5 answers (`engagement.weakest_last_n`). Coasting needs at least 2 messages in the window (`engagement.coasting_min_messages`).

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| St. Hilaire, Chan & Ahn (2024), *Psychonomic Bulletin & Review* | Trying before being told helps, even when the guess is wrong (prequestion effect, g = 0.54 overall). | Meta-analysis | Mostly adult lab studies; school evidence is thin and mixed (Geller et al., 2017: null in a STEM classroom). |
| Roediger & Marsh (2005); Butler & Roediger (2008) | Wrong multiple-choice options can be learned, and feedback reduces this; correcting the chosen wrong idea helps. | Experiments | Adults; lab. |
| Galyardt & Goldin (2015), *Journal of Educational Data Mining* | The best recency weighting put 75 to 93% of the weight on the last 5 attempts. | Single study | Tutoring-system data. |
| `docs/research/personalisation.md` §5 | Stopping should be offered neutrally, with progress kept. | Design review | Not a trial. |

`engagement.weakest_last_n = 5` is **from research**; `engagement.coasting_min_messages = 2` is a **judgement call, starting value**.

## Alternatives considered

- **Always show after "just show me".** What the first two shows do. After the cap it removes the pause that gets the student to try first.
- **Refuse further shows.** Rejected: it denies the student what they asked for.
- **Keep an empty plan on stop.** Left the chatbot to improvise a summary without data.

## Consequences

- A third "just show me" now takes two replies to reach the show instead of one. The student always gets the show.
- Stopping now ends with a two-sentence summary. This adds a move section of 23 words to the server instructions. Cuts of about the same size were made to `offer_choice`, `ask_mcq`, `reask`, `extend`, `answer_with_sources` and the instruction list, so the count stays at 897 of 900.
- No migration. No effect on the demo path; the engagement checks in `check_mcp.py` are updated.

## Verification

`tests/test_engagement_rules.py` (8 tests), `scripts/check_mcp.py` (engagement run) pass; rebuild identical; instructions 897 of 900.

## What would change our mind

Students who stop mid-point finding the summary unhelpful, or evidence that a 5-answer window misjudges slow learners.
