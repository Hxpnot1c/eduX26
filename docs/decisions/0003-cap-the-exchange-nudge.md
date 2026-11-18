# 0003. Cap what an ordinary exchange can do to a part's estimate

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Vishnu (levels shown to students can change)
- **Pull request:** #46
- **Audit item:** C1 in [0002](0002-research-alignment-register.md)

## Context

Every `tutor_turn` carries labels the student's own chatbot chooses: `question_depth` (surface, mechanism, transfer) and `engagement` (passive, active, constructive). `apply_exchange` in `edux/learner.py` multiplies the part's odds by 1.1 for `transfer` and 1.05 for `constructive`, on every message, with no cap. A part starts at `bkt.prior` = 0.30.

Worked through: about 20 `transfer` messages, or about 14 labelled both `transfer` and `constructive`, take a part from 0.30 to "secure" (0.75) with no answer ever tested. The forgetting clock has not started either (`clock_start` is empty until a first correct answer), so nothing decays. The labels are unvalidated: nothing checks them against the message, and a student who asks transfer-style questions can steer them.

This is the opposite of the first design principle in the research: judge behaviour, not self-report or fluency. It also contradicts the claim the pitch will make, that levels come from what students can do.

## Decision

Add `nudges.ceiling = 0.40` in `settings.toml`. An exchange may raise a part towards the ceiling and no further:

```
p = max(p_before, min(odds / (1 + odds), nudges.ceiling))
```

- It never lowers a part (multipliers are at least 1).
- It does nothing to a part that evidence has already lifted past the ceiling.
- `load_settings` refuses a ceiling above `levels.new` (0.40), so conversation alone can never move a part out of "new".
- Bump `protocol` to `v0.3`, because the meaning of scoring changes.

The labels stay in the exchange log. The AI-literacy trends and the engagement rules still read them.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Soderstrom & Bjork (2015), *Perspectives on Psychological Science* 10(2) | Performance during learning is a poor guide to learning; fluency is misread as mastery. | Review | Mostly lab tasks with adults. |
| Bastani et al. (2025), *PNAS* | In a field experiment with about 1,000 students, unrestricted GPT-4 raised practice scores by 48% but lowered unaided exam scores by 17%. A guard-railed tutor removed the harm. | Single study (one school, short term) | The guard-railed arm showed no detectable harm, not proven benefit. |
| Research review, Summary §1 and principle 1 | Self-report and surface behaviour are weak proxies for competence; triangulate with performance. | Review | Abstract-level for some sources. |
| Research review, F1 (LLM scoring of chat logs) | The best case found was 0.85 accuracy against expert labels with no annotator agreement reported; no validated scorer for chat-log constructs exists. | Abstract only | Not about this exact label set. |
| Sharma et al. (2023), arXiv 2310.13548 | Assistants agree with users, and preference models sometimes reward it. | Single study, replicated across five assistants | Not tested on depth labels. |

The size of the ceiling (0.40) is a **judgement call, starting value**. No study gives it. It is set equal to the "new" threshold so the rule is easy to state: talking alone never moves a part out of "new".

## Alternatives considered

- **Set both multipliers to 1.0.** Same safety, but it deletes the feature. A small early lift on a part the student is clearly working on helps the planner notice interest without claiming understanding.
- **Cap at `levels.secure − 0.05`.** A student could still reach "developing" by talk alone, and "developing" changes the support level and the reviews offered.
- **Leave it and rely on later evidence to correct it.** Rejected: until then the level is wrong, and the demo and any teacher view would show it.
- **Validate the labels server-side.** Better in the long term (audit item C2), but a larger change. The ceiling is the minimal safe step.

## Consequences

- A part with no tested answer can no longer show "developing" or "secure" from conversation.
- Seeded demo students are unchanged: their levels are identical before and after (checked on all three; see Verification).
- The planner still treats talk as a weak signal below the ceiling.
- Stored data: no migration. Events keep their `protocol` and `settings_hash`; a rebuild re-scores them under v0.3.
- Instruction word count is unchanged (897 of 900).

## Verification

```
.venv/bin/python -m pytest -q
EDUX_DATA_DIR=... python -m edux.cli load coursepacks/example-mini && python -m edux.cli seed-demo
python -m edux.cli state --student <each demo student>        # levels identical to main
python scripts/check_mcp.py --url http://127.0.0.1:8765/mcp   # all checks passed, rebuild identical
```

New tests in `tests/test_exchange_nudge.py`: 80 deep exchanges stay at or below the ceiling and not "secure"; a nudge still raises a low part; a nudge never lowers a part evidence lifted; a surface, passive exchange changes nothing; a ceiling above `levels.new` is refused when settings load.

## What would change our mind

A pilot with real students that shows labelled depth or engagement predicts later unaided performance (on held-out answers) would justify a higher ceiling, with a value fitted from that data. Until then, the chatbot's labels are context, not evidence.
