# Step 05y: Ask and Verify are formative, and asking for sources earns nothing alone

Branch `build/formative-literacy-wording`, from `main` once step 05s (#55) is merged. Audit item C3; Vishnu's decision of 18 November.

## What
1. **Student view.** `get_my_progress` keeps the Ask, Verify and How-AI-works levels but adds, for each, the evidence behind it (`evidence: {checks, over_days}`) and a `formative` line: "practice feedback, not a grade". The tool text tells the chatbot to say it that way: "Verify: developing, from 4 checks over 2 weeks: practice feedback, not a grade". Teacher aggregates are unchanged.
2. **Ask scoring, checked.** The server scores Ask from the question features the chatbot labels (`concept`, `context`, `asks_sources`, `asks_reasoning`); it reads no prose, length or polish. Finding: all four features counted equally, including `asks_sources`, so a student could earn Ask credit by requesting sources, which invites a chatbot to invent them. **Fixed:** `asks_sources` counts only when the student has checked a claim (Verify evidence) earlier in the session. The `tutor_turn` tool text now says to judge a feature by what the question asks for, never by wording, length, polish or the student's English.
3. The Ask/Verify feedback patterns already pair every research answer with a Verify task, so the sources nudge is always alongside checking.

## Why
See [decision 0014](../../decisions/0014-formative-literacy-and-ask-scoring.md). In short: about four items per level give a standard error near 0.25 (research summary §6(e)), prompt length is unrelated to grade (r = .036), and a phrasing pattern may penalise English-as-an-additional-language writers (F5-19).

## Files
- `edux/learner.py`: `verified_this_session`, `question_evidence(features, sources_credit)`.
- `edux/service.py`: `_ai_literacy` adds `formative` and `evidence`; the research-question evidence passes `sources_credit`.
- `text/tools/get_my_progress.md`, `text/tools/tutor_turn.md`.
- `tests/test_literacy_wording.py` (5 tests).
- Docs: `reference/learner-model.md`, `reference/tools-and-context.md`.

## Done when
- A test shows `asks_sources` scores nothing alone and scores with a Verify moment this session.
- The progress view carries the evidence and the formative line; `check_mcp` passes with levels-only progress within 2,400 characters (2,275 measured); rebuild identical.
- Instructions unchanged (899 of 900).

## Not in this step
The EAL subgroup audit of the labelling, a plain-language mode and a student notice (decision 0014, open items).
