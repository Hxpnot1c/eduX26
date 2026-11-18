# Step 05l: Fixes to engagement-rules (#28, #29, #30)

Branch `build/fix-engagement-rules`, from `main`. Follow-up to step [05g](05g-engagement-rules.md) (PR #27, merged).

## What
1. **#28 Repeated show: question first, then the show.**
   - The repeated-show 2-option question comes first. After the student answers it, the next plan gives the feedback and then the full show (`show`, then its check).
   - **The wrong option** is chosen in this order:
     1. a misconception the student holds on the part (active in `student_misconception`);
     2. otherwise a watch-for one (the `watch_for` list `context_blocks` already builds);
     3. otherwise the first in pack order.
   - How the plan knows: the 2-option question is marked in `issued_plan` (`data.then_show = true`). When its answer arrives, `choose` adds the show after the feedback.
2. **#29 Three changes to `offer_choice` picks.**
   - **`choice == stop` is treated like fatigue** in `_literacy_followup` and `_how_ai_works`. There's no re-ask, and a waiting task is dropped unscored.
   - **Stop returns a summary step** instead of an empty plan. New move `session_summary`:
     - `data.covered`: the parts worked on this session (names);
     - `data.next_review`: the next due review's part and date, or none.

     Its move section is at most 2 sentences. The chatbot signs off using it.
   - **"extend" appears in the passive offer only when extend is earned** (`support.extend_from`). Otherwise the offer is quiz and stop.
3. **#30 Two changes to coasting.**
   - **Weakest point:** the mean of each point's last `engagement.weakest_last_n` (5) answers, not all of them.
   - **Coasting needs at least `engagement.coasting_min_messages` (2) messages** in the window. A single passive first message no longer counts.

**Instructions word cap.** `session_summary` adds a move section, of about 25 words. Cut first:
- tighten `offer_choice.md`, whose stop option no longer needs "(a one-line summary)";
- tighten other sections if needed.

Only if the cuts can't make room, raise `instructions.max_words` to at most 950, with the reason in `settings.md`. Report the count in the PR.

## Why, with sources
- **Pretesting:** trying before being told helps even when the guess is wrong (St. Hilaire, Chan & Ahn, 2024). The show still follows, so a stuck student isn't refused.
- **A held misconception is the most useful wrong option.** Picking it and getting feedback corrects it (Roediger & Marsh, 2005; Butler & Roediger, 2008).
- **Last 5 answers:** the best-predicting recency weighting puts 75–93% of the weight on the last 5 attempts (Galyardt & Goldin, 2015).
- **Stopping is offered neutrally, with progress kept** (`docs/research/personalisation.md` §5). The summary says what was done and when to come back.

## Files
- `edux/plan.py`:
  - `two_option_check` (wrong-option order, `then_show`);
  - `choose` (show after the feedback);
  - `picked` (stop returns `session_summary`);
  - `main_step` (the passive offer's options);
  - `session_summary`.
- `edux/learner.py`: `weakest_point` (last n per point), `coasting_share` (minimum messages); a reader for the session's covered parts.
- `edux/service.py`: stop in `_literacy_followup` and `_how_ai_works`.
- `text/moves/session_summary.md` and `session_summary.cue.md`; `text/moves/offer_choice.md`.
- `settings.toml`: `engagement.weakest_last_n`, `engagement.coasting_min_messages`.
- `scripts/check_mcp.py`: the engagement run, extended.
- **Docs:** this file; 05g is written to match; `reference/tools-and-context.md` (`session_summary`, choice values); `reference/settings.md` (the two settings, labelled); `reference/research.md` rows if anything ends up different.

## Settings
```toml
[engagement]
weakest_last_n = 5          # from research: Galyardt & Goldin (2015), 75–93% of predictive weight on the last 5 attempts
coasting_min_messages = 2   # judgement call, starting value
```

## Commits
1. `fix(plan): ask the repeated-show question first, then show`
2. `fix(plan): pick the two-option distractor from held, then watch-for misconceptions`
3. `feat(plan): return a session summary when the student stops`
4. `fix(service): treat stop like fatigue for literacy follow-ups`
5. `fix(plan): offer extend in the passive offer only when earned`
6. `fix(learner): weakest point from each point's last five answers`
7. `fix(learner): need two messages before a student counts as coasting`
8. `chore(scripts): check the engagement fixes in the MCP check`
9. `docs(reference): document session_summary and the coasting rules`

## Done when
- The third show gets the 2-option question. Its answer gets feedback, then the show and its check.
- The wrong option is a held misconception when there is one.
- Stop gives `session_summary` with covered parts and the next review. A waiting literacy task is dropped unscored, not re-asked.
- With extend not earned, the passive offer lists quiz and stop only.
- A point whose early answers were wrong but last 5 right isn't picked as weakest. One passive message isn't coasting.
- Issues #28, #29 and #30 are closed with a one-line comment.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported.

## Tests
In `scripts/check_mcp.py` (the engagement run): one check per item under Done when.
