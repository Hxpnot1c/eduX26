# Step 05z: "How sure are you?" and the calibration line

Branch `build/calibration`, from `main` once step 05u (#61) is merged. Audit item C7; Vishnu's decision of 18 November.

## What
1. **Ask after a check answer, before the feedback.** After an answer to a check, a review or a prerequisite check (never ordinary chat, a pre-question or a how-AI-works check), the reply is one short question: "How sure are you: guess, fairly sure or certain? (You can skip this.)" (`say_line` with key `say_line_confidence`, wording in `text/confidence/ask.md` as `data.line`; first named `ask_confidence`). The answer is recorded and scored at once. **The feedback and the next question are computed in the same call but held back one turn** (saved in `issued_plan` with `confidence_for`), so no server state is computed twice. The next call, with `this_message.confidence`, stores the rating and delivers the held plan. A chatbot that already sends `confidence` with the answer is not asked again.
2. **Optional, no penalty.** `this_message.confidence = none` (or anything else) stores `skipped`. Two skips in a row stop the asking for the session; at most six asks a session; never in long-session or rushing mode or after "just show me"; an unanswered ask is dropped after the session gap.
3. **Stored as an event** (`confidence_log`, migration 019), never an input to `p_known`.
4. **One calibration line in `get_my_progress`**, shown for a level only after `confidence.min_per_group` (5) rated answers in it: "When you were certain, you were right 8 of 10 times; when you were guessing, 4 of 10." Skipped asks are not counted.

## Why
See [decision 0019](../../decisions/0019-confidence-and-calibration.md). Calibration is the product's signature measure in the research review; committing before the answer is revealed reduces over-reliance (Buçinca et al., 2021).

## Files
- `migrations/019_confidence_log.sql`; `edux/learner.py` (`record_confidence`, `confidence_asks`, `calibration`, `evidence_ids_of_exchange`); `edux/plan.py` (`ask_confidence`, the stop set); `edux/service.py` (`_confidence_due`, the held plan, `_calibration`); `edux/server.py` (`this_message.confidence`).
- `text/moves/say_line.md` and `say_line_confidence.cue.md`, `text/confidence/ask.md`, `text/progress/calibration.md`, `text/tools/tutor_turn.md`.
- `settings.toml` `[confidence]`.
- `tests/test_calibration.py` (14 tests); `scripts/check_mcp.py` (the harness answers with `confidence: none`, and a dedicated run).
- Instruction words: the new move section is 15 words; I cut 16 from rules 2 and 9, `teach_point` and `answer_brief` to stay at 899 of 900.

## Done when
A test shows the feedback is held one turn and delivered with the rating stored; the rating never changes `p_known` (tested with a "certain" and a "guess" student); skipping is free; the line appears only at 5 rated answers; the gate passes.

## Not in this step
Routing high-confidence errors to an early review (hypercorrection, Butterfield & Metcalfe, 2001), the A-level evidence for which is thin; a teacher view of calibration; aided versus unaided evidence (C8, after filming).
