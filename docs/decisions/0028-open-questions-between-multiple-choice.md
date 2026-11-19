# 0028. Two open questions after every multiple-choice question

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (his rule of 19 November)
- **Pull request:** see the branch `build/open-after-mcq`

## Context

The point-by-point loop (step 05d) checked each point with a multiple-choice question, and reviews and prerequisite checks were multiple choice too. A student could go through a whole part picking letters. Vishnu wants more of the questions to be written answers.

## Decision

1. **The rule.** After any multiple-choice question (a point check, an intuition pre-question, a prerequisite check, a review or a how-AI-works check), the next `questions.min_open_between_mcq` (2) questions the student is asked are open (written). The count is kept with the saved plan. It is reset by a multiple-choice question and goes up by one for each open question asked. Asking the same question again (a re-ask) counts once. A choice of ways on, a literacy task or "how sure are you?" doesn't count. It carries across sessions. Before any multiple-choice question has been asked, there is no gap.
2. **The exception.** While the student is fatigued or rushing (long-session or rushing mode), multiple choice is allowed without the gap. Such a question still resets the count.
3. **Open forms, using what exists.**
   - A point check, prerequisite check or the two-option check before a repeated "show me" becomes `explain_back` on that one point (key `explain_back_check`, `data.point`, `data.point_id`, and the same `purpose`). It is scored 0 or 1 on that point, as the coasting explain-back already was. It then goes on as its MCQ would: right means the next point, wrong means a re-teach of the point and its check again.
   - A review becomes an open recall question on one point (key `explain_back_review`, with `name`, `mode` and `new_context`). It is answered as type `review` and scored on that point.
   - A whole-part explain-back, `extend` and find-the-error practice are open already.
4. **No open form.** An intuition pre-question (and the bridge question) is a guess before teaching, scored right or wrong. A how-AI-works check needs its fixed options. When the gap blocks either one, it is dropped: the intuition is marked as asked for that part, so it doesn't turn up mid-teaching, and the bridge falls through to the next ending option. A how-AI-works check fires again at the next failure.
5. **The cap after teaching.** A one-point answer straight after teaching, open or picked, can't make a part secure (it shows one point). Before, only picked answers had this cap (0010b). Without it, two right one-point written answers in the first teaching pass could make a whole part secure. This also covers the coasting student's one-point explain-back.
6. **Wrong ideas from written answers.** `answer.misconception_ids` already worked for every answer type, the watch-for wrong ideas are already sent on explain-back, extend, re-teach and re-ask, and `feedback` names them. The field's description now tells the chatbot to send ids from `reference.misconceptions` that the answer showed, written answers included.
7. **A switch.** `EDUX_QUESTION_GAP` (a whole number; 0 turns the gap off) overrides the setting without editing `settings.toml`, for demos and for `scripts/check_mcp.py`.

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Kang, McDermott & Roediger (2007), *European Journal of Cognitive Psychology* | With feedback, short-answer tests gave better later retention than multiple-choice tests | Lab experiments | Students and prose, not A-level exam skills |
| Generation effect (Slamecka & Graf, 1978) | Producing an answer is remembered better than reading or recognising it | Well replicated | Simple materials |

**The number 2 and the exceptions are judgement calls** (Vishnu, 19 November).

## Alternatives considered

- **Open questions every time.** It loses the server-checked wrong-option picks, the best source of "common wrong ideas" for teachers.
- **Ask the intuition question open.** It is a guess before teaching; there are no points to tick yet.
- **Wait for the next turn when MCQ is allowed** for intuition and how-AI-works. The moment has passed by then.

## Consequences

- **Fewer server-checked wrong ideas.** The teacher page's "common wrong ideas" now relies more on the chatbot noticing a wrong idea in a written answer. Expect fewer entries, and less reliable ones.
- **Fewer pre-questions.** Fewer pre-questions mean less evidence for the starting offsets (05q).
- **Time to secure is unchanged** (`scripts/simulate_open_checks.py`, 20 runs of each, the parts with 3 or more points). Delayed answers to secure: 2.00, 2.58, 3.44 all-MCQ against 2.00, 2.55, 3.40 for MCQ, open, open, at 100%, 85% and 70% right. Straight after teaching, a one-point answer never makes a part secure in either pattern, as today.
- **`scripts/check_mcp.py`.** With the gap on, it runs only the question-mix check. Its full run needs `EDUX_QUESTION_GAP=0` on the server and the script.

## Verification

`tests/test_question_mix.py`:
- On six parts, every multiple-choice question is followed by two open ones.
- A check after an MCQ is open on the same point, with its own letter only.
- An open check is scored on its point, then re-teaches or moves on.
- The conversions: check, prerequisite and review become open; intuition and how-AI-works are dropped.
- An open review is recorded as `review` on its point.
- The count, and the fatigued exception.
- Rushing allows multiple choice without the gap.
- The intuition question is dropped and stays dropped.
- A wrong idea in a written answer is stored and corrected.
- The cap after teaching.
- A gap of 0, the environment switch, and the settings check.

`scripts/check_mcp.py`: the question-mix run, and the full run with the gap off.

## What would change our mind

Pilot logs showing the chatbot rarely labels wrong ideas in written answers (the teacher view thins out), or students skipping open questions far more than multiple-choice ones.
