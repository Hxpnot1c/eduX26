# Step 05g: In-session engagement rules

Branch `build/engagement-rules` (PR #27, merged). Fixes in step [05l](05l-engagement-rules-fixes.md), branch `build/fix-engagement-rules`.

This step doc was written after the merge. It describes the feature as it stands once 05l lands.

## What
Three in-session rules. Each signal is read from `exchange_log` each turn and is never stored as a trait of the student.

1. **`offer_stop` becomes `offer_choice`**, with `data.reason` (`fatigued` / `passive` / `stuck`) and `data.options` (from `stop`, `quick`, `quiz`, `extend`).
   - The student's pick comes back as `this_message.choice` (`quiz`, `extend` and `stop` are choice values). A pick drops the pending question.
   - `quiz`: the current point's check. `extend`: an `extend` question.
   - `stop` returns a `session_summary` step (05l, #29), not an empty plan:
     - `data.covered`: the parts worked on this session;
     - `data.next_review`: the next due review's part and date.

     The chatbot signs off using it.
   - `stop` is treated like fatigue in the literacy follow-up and the how-AI-works check: there is no re-ask, and a waiting task is dropped unscored (05l, #29).
   - `issued_plan` keeps `offered`, the reasons already offered this session.
2. **Passive streak.** After `engagement.passive_run` (4) messages in a row labelled `passive`, `offer_choice` offers quiz, extend or stop.
   - "extend" is listed only when extend is earned (`support.extend_from`); otherwise the offer is quiz or stop (05l, #29).
   - It happens at most once per session and never when fatigued. It comes before a re-ask of a pending question.
3. **Repeated show: question first, then the show** (05l, #28).
   - After `show.max_per_part_session` (2) "just show me"s on one part in a session, the next one first gets a 2-option `ask_mcq` (check): the point, plus one wrong option.
   - The wrong option is a misconception the student holds on the part, else a watch-for one, else the first in pack order.
   - After the student answers, the next plan gives the feedback and then the full show (show, then its check).
   - It is stored with `n_options = 2`, so its guess is 1/2.
4. **Coasting.** The rule needs:
   - at least `engagement.coasting_min_messages` (2) messages in the window (05l, #30);
   - a passive or "just show me" share of the last `session.signal_window` messages of at least `engagement.low_share` (0.5).

   When both hold, the explain-back asks for the weakest point only (`data.point`, `data.point_id`, cue `explain_back_point`).
   - The weakest point has the lowest mean score over **each point's last `engagement.weakest_last_n` (5) answers** (05l, #30). A point never asked counts as 0.5; ties go to the earlier point.
   - The answer is scored on that point only, with its `point_id`.

## Why, with sources
- **Trying before being told helps learning, even when the guess is wrong** (St. Hilaire, Chan & Ahn, 2024, pretesting). The full show still follows, so a stuck student isn't refused.
- **Engagement checks are core and in-session only**, never stored as a trait (`docs/research/personalisation.md` §5).
- **Weakest point from the last 5 answers:** the best-predicting recency weighting puts 75–93% of the weight on the last 5 attempts (Galyardt & Goldin, 2015).
- **Stopping is offered neutrally, with progress kept** (`personalisation.md` §5). The summary tells the student what they covered and when to come back.
- The 3rd-request trigger, the passive run of 4, the 0.5 share and the 2-message minimum are judgement calls.

## Files
- `edux/plan.py`: `offer_choice`, `picked`, `two_option_check`, `shown_or_skipped`, `explain_back`, and `session_summary` (from 05l).
- `edux/learner.py`: `passive_streak`, `coasting_share`, `weakest_point`, `shows_this_session`.
- `edux/service.py`: choice handling, `offered` in `issued_plan`, and (from 05l) stop in `_literacy_followup` and `_how_ai_works`.
- `text/moves/offer_choice.md` and its cues, `text/moves/explain_back_point.cue.md`, and (from 05l) `text/moves/session_summary.md` and its cue.
- `settings.toml`: `[engagement]`, `[show]`.
- `scripts/check_mcp.py`: the engagement run, with one throwaway student per rule.

## Settings
| Setting | Value | Label |
|---|---|---|
| `engagement.passive_run` | 4 | judgement call, starting value |
| `engagement.low_share` | 0.5 | judgement call, starting value |
| `engagement.coasting_min_messages` | 2 | judgement call, starting value (05l) |
| `engagement.weakest_last_n` | 5 | from research: Galyardt & Goldin (2015) (05l) |
| `show.max_per_part_session` | 2 | judgement call, starting value |

## Done when
- A passive streak gets one offer per session, with extend only when earned. Each pick does what it says; stop returns `session_summary`.
- The third show on a part gets the 2-option question, then feedback and the full show.
- A coasting student's explain-back asks for their weakest point by its last 5 answers. A single passive message doesn't count as coasting.
- No result is over 2,400 characters. The instructions stay within the cap.

## Tests
In `scripts/check_mcp.py` (the engagement run, and the 05l additions).
