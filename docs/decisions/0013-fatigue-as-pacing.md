# 0013. Fatigue becomes pacing: time on task and rapid guesses, not how well a student answers

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (decided 18 November; confirm the wording and the 50-minute point)
- **Pull request:** #55
- **Step:** [05s](../build/steps/05s-fatigue-time-on-task.md) (audit item C4; issue #24)

## Context

Until now "fatigued" was inferred from performance: from 25 minutes into a session, if the last four answers were worse than expected on at least two parts, the session was marked fatigued for good. Our own simulation found the rule flagged 77% of students who were not tired by 60 minutes, because a run of four answers near the expected rate says little. The state then changed what a student saw (shorter replies, no literacy checks, a stop offer) and was stored as a per-student `study_pattern` ("your answers tend to drop after about N minutes"), a stored personal trait the project's own rules say is never shown as a label. The label "fatigue" also invites reading an inferred emotional or physical state into performance data.

## Decision

1. **Time-based slip for everyone.** Extra slip is 0 until 28 minutes into a session, then 0.002 per minute, up to 0.12, within the slip cap.
2. **Rapid guesses.** An answer that arrives faster than the question can be read (300 words per minute) plus the answer typed (52 words per minute) gets weight 0 for knowledge and is counted. The latency, the question's word count and the answer's word count are stored on the exchange (counts only, no text), so a rebuild replays the flag. A chatbot that does not send `this_message.words` is never flagged.
3. **Long-session or rushing mode** (the old fatigued mode) starts at 50 minutes into a session or at the 2nd rapid guess in it. One offer is made, in plain words about pacing, not tiredness. Teachers see "long-session mode" and "rushing (answers faster than reading time)".
4. **Remove the 4-answer rule and its settings, and the stored `study_pattern`.**

## Research basis

| Source | What it shows | How well established | Limits |
|---|---|---|---|
| Randles, Harlow & Inzlicht (2017), *Frontiers in Psychology* | Performance declines from about 28 minutes on a task, by 4 to 5 points by about 50. | Single study | Mostly adults; lab tasks. |
| Brown, Kaur, Kingdon & Schofield (NBER working paper); TIMSS analysis in the same paper | End-of-test declines of 7.5 to 12%. | Working paper | Test settings, not chat. |
| Sievertsen, Gino & Piovesan (2016), *PNAS* | Breaks restore performance in school tests (a 20 to 30 minute break lifted scores by about 1.7% of an SD). | Single natural experiment | Small average effects at school-day scale. |
| Wise & Kong (2005); Wise & Ma (2012); Wise & DeMars (2006) | Answers faster than the item can be read are rapid guesses and say little about ability; scoring that sets them aside is more accurate. | Replicated measurement literature | Low-stakes tests; thresholds vary by item. |
| Lindner, Lüdtke & Nagy (2019), *Frontiers in Psychology* | Rapid guessing starts late for reasons of motivation and working memory (pupils aged about 10 to 11). | Single study | Younger sample. |
| Brysbaert (2019), *Journal of Memory and Language* | Mean silent reading about 238 words per minute (range 175 to 300). 300 is used so fewer students are flagged wrongly. | Meta-analysis | Silent reading of general text. |
| Dhakal et al. (2018), CHI | Mean typing speed about 52 words per minute on a keyboard. | Large observational study | Phones are slower; 52 is the conservative pick. |
| Commission guidelines on prohibited AI practices (4 February 2025), paras 249 to 251 | The EU ban on emotion inference in education covers inference from biometric data. Timing and text are out of scope; keystroke dynamics are biometric. | Regulatory guidance | Does not address response timing explicitly. **[COUNSEL]** |

Labels: the 28-minute start, 0.12 cap, 50-minute mode, 300 and 52 words per minute are **from research**; the slip rate of 0.002 per minute is **from research** (fitted to the same 4 to 5 point decline by about 50 minutes); `rapid_guesses = 2` and `min_students_per_bin = 5` are **judgement calls, starting values**.

## Alternatives considered

- **Keep the performance rule with a higher bar.** Still reads a state from noisy answers, and still needs an affect label.
- **Use typing speed or keystroke timing.** Behavioural biometrics under the EU guidelines; not used.
- **A single global timeout.** Ignores that a rapid guess is relative to the question's length.
- **Offer a break earlier than 50 minutes.** No evidence for an earlier point; the offer is one-off and the student can carry on.

## Consequences

- No student is called tired. A student who is rushing is asked if they want to switch; one who has worked for 50 minutes is offered a break.
- Late wrong answers cost slightly less than early ones, for everyone.
- The old stored trait is gone, which also removes a profiling concern (Children's Code Standard 12).
- Needs one new tool field, `this_message.words`; chatbots that omit it get no rapid-guess flags (safe direction).
- Migration **015**. Instruction word count 899 of 900 (the line wording lives in `text/fatigue/`, sent as data, so the cap is barely touched).
- **Not in this pull request:** the `answer_timing` table, `fatigue-curve` and the class curve (they need the classes from step 05q).

## Verification

`tests/test_time_on_task.py` (9 tests); `scripts/check_mcp.py` passes, including a long-session student and a rushing student; rebuild identical.

## What would change our mind

Real students answering faster than reading speed for good reasons (they know it already), which would argue for a higher threshold or requiring accuracy as well; or evidence for a different break point.
