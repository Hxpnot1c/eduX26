# Step 05za: Find-the-error practice (Part 2 G)

Branch `build/find-the-error`, from `main` once step 05z (#62) is merged. Scoped in [decision 0012](../../decisions/0012-find-the-error-scoping.md) (pull request #56); built and recorded in [decision 0021](../../decisions/0021-find-the-error-build.md). **Built but off by default** (`find_error.enabled = false`, or `EDUX_FIND_ERROR=1`) until Vishnu approves it: the evidence for planted-error practice is thin.

## What
- A rare practice item, always labelled "Practice, not a real answer... It may contain one mistake, or none": a short numbered explanation of the focus part built from its own mark points, with one sentence swapped for one of its misconceptions (the sentence its correction most resembles), or left whole as a clean control (40%).
- Rare: at most one a session, only on a part at developing or above that the student has answered on, never while rushing. Misconceptions rotate. It is offered in the ending's tier 2, ahead of the bridge.
- Scored on the server, from four letters that are the same for every item (a: says there is a mistake; b: which sentence; c: what is right; d: no mistake). Hits and false alarms are apart: an error item scores 1 only for b and c; a clean item only for d with none of a, b, c. "There is a mistake" alone scores nothing, so blanket suspicion is never rewarded.
- The correct statement is always given afterwards, naming the planted wrong idea and the right one.
- Evidence on the part (`find_error`) and on Verify as its own type (`ail_find_error`). No misconception is activated.

## Files
`edux/plan.py` (`find_error_step`, the tier, the feedback branch, `score_next`), `edux/learner.py` (`score_find_error`, `find_error_on`, `FIND_ERROR_POINTS`), `edux/service.py` (scoring against the kept item, the Verify row), `settings.toml` `[find_error]` and `ail_find_error`, `text/find_error/`, `text/moves/say_line.md` (shared with the confidence question: no extra instruction words, 898 of 900), `tests/test_find_error.py` (27 tests), `scripts/check_mcp.py` (`find_error_run`).

## Done when
Off by default nothing is offered (checked); switched on, an item is offered, labelled, gives nothing away, is scored on the server, recorded on the part and on Verify, and the correct statement is given; the gate passes in both modes.

## Open
Items are made from the pack's own mark points and misconceptions and are marked "not yet signed off by a teacher"; a teacher should check them before a real pilot. Evidence: see decision 0012 (Fan & Chang's paper does not support an effect size; erroneous-example effects are small, g about .14).

## Also on this branch stack (audit, 19 Nov)
- #65: demo script update, `EDUX_CONFIDENCE` switch, labelling rule in `settings.toml`.
- #66: input length limits on every tool (register C18) and the pupil-facing notice (C11) in `text/chatbot_setup.md`.
