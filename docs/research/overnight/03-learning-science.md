# 03 · Learning science we haven't used yet

Wave 2. Sources: scout notes `work/w2/w2-03.md`, verifier marks `work/w2/verify-F.json`, the teacher and student panel `work/w2/panel-teacher-student.md`. Builds on `docs/build/reference/research.md` and `docs/research/personalisation.md` (§1–4 and the 134-row CSV), and adds only what is new. Mark-structure work and the chain and evaluation checks are in [04](04-economics-education.md).

eduX already uses pre-questions, explain-back, feedback, spacing to the exam, interleaving of confusables, segmenting, the testing effect, mastery, confidence ratings and utility value. Ideas already in the CSV are not repeated: successive relearning (7b-17), productive failure (2-06), desirable-difficulty limits (2-14), the "85%" and "80%" success-rate myths (2-11, 7b-01, 7b-02), half-life regression (7a-10) and hypercorrection (3-08, 3-09).

Marks: ✓ confirmed by a blind verifier; ~ broadly supported, with the verifier's caveat. **Every w2-03 finding is ~**: the verifier read abstracts only, and nearly all figures matched. No finding is ✗. Code claims below (the `confusable` edges, the `confusables` block, `[moves.reteach]`, `distractors()`) were spot-checked in the repo for this report.

## Summary

- **Contrasting cases are the best new idea for reteach.** Across 57 experiments, comparing cases side by side beat single, sequential or non-analogous cases and ordinary teaching, d = .50 [.44, .56] (learning). It worked best when learners looked for what the cases share and got the principle *after* the comparison (w2-03-01 ~). eduX already has `confusable` edges and a `confusables` block with a `past_mixup` flag, but reteach doesn't receive it. The example pack has just one confusable edge (PED↔YED). The other pairs depend on [04](04-economics-education.md) rec 6.
- **Self-marking before feedback has school evidence.** In grades 3–12, students who graded their own work did better on later tests, g = .34 (learning). Their grades were close to teachers' (g = .04, r = .67). The gain was larger in randomised studies, but the evidence base is small (w2-03-02 ~). eduX already has the rubric: each part's points.
- **Diagram practice helps only with an integration step.** Drawing support that joined words and picture raised comprehension, g = 0.35. Support without that step had no effect, g = −0.15, n.s. (learning; 14 studies, N = 1,213; w2-03-03 ~). So: sketch on paper, then say which curve moved, which way, and what happened to P and Q.
- **Successive relearning re-asks missed items in the same session.** In a university course, missed items came back up to two more times per session. Relearning beat restudy at the end of term with exposure time held equal (learning; w2-03-04 ~). The student panel objects to re-asking. Our version is skippable, uses a different question, and says why it is there (rec 3).
- **Nudges are mostly engagement results, or nulls at scale.** Implementation intentions: .27 ≤ d ≤ .66 over 642 tests, with publication bias (w2-03-07 ~). Low-touch planning plus reminders or coaching: precise nulls on grades in more than 9,000 college students (w2-03-09 ~). The one UK 16–19 trial, texting GCSE-resit students in FE colleges, found 0 months' progress (w2-03-11 ~, secondary source). eduX can't send messages anyway.
- **The easiest game version was the most engaging and taught the slowest** (engagement and learning moved in opposite directions; about 10,000 and 70,000 players; w2-03-12 ~). This backs setting difficulty by `p_now`, not by time-on-app, and makes a strong pitch line.
- **Psychometrics gives one cheap, speculative idea.** Rotate which misconceptions appear as options when a part has more than three. Today `distractors()` always picks the same top three (w2-03-13 ~; our analogy from exposure control). Success-rate targeting needs a calibrated item bank, so it waits.
- **Analogies belong in the pitch, not the build.** A surgical checklist helped in an 8-hospital pre/post study, but a mandated rollout across 101 Ontario hospitals found no effect (w2-03-14 ~). Deliberate practice explains only 4% of performance variance in education (w2-03-15 ~). The lesson: a check works when the student owns it and it is specific. Don't sell "more practice time".

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on |
|---|---|---|---|---|---|
| 1 | **Contrast the twin concept in reteach.** Add `"confusables"` to `[moves.reteach].reference` in `context.toml` (today it is `["notes", "anchor"]`). Add one sentence to `text/moves/reteach.md`: when a confusable has `past_mixup`, show two short cases side by side, one per concept, and ask "what's the same, and what's the one difference?". Then give the principle (the missing point), then the usual check. Show both concepts as correct ideas, never as a right/wrong pair. No schema change. `past_mixup` needs a held misconception on either side, so the pairs need misconception rows too. The example pack has one pair (PED↔YED). Add the rest as `confusable` edges from [04](04-economics-education.md) rec 6. | `context.toml`, `text/moves/reteach.md`, pack edges; pitch | S | yes | w2-03-01 ~ |
| 2 | **Self-mark against the points before feedback** on `explain_back`, and on `past_question` for **point-marked 4- and 8-markers only**. The chatbot lists the part's point titles (not their text) and asks "which did you include?". Feedback then shows where the student and the marking agree and where they differ: the student panel called this the useful part. The self-mark is one tap, **skippable**, at most once per session (our choice), and never when fatigued. Self-marks never change `p_known`, which is still scored from the chatbot's ticks. It is never offered on levelled 12- and 25-markers. Levels reward connected chains, not point counts, and server rule 7 forbids turning anything into a mark there. Self-mark data is never shown to teachers. Settings: `[self_mark] enabled = true`, `max_per_session = 1`, `skippable = true`. | `text/moves/explain_back.md`, `feedback.md`; one plan flag; demo | M | yes (text-only version) | w2-03-02 ~; [04](04-economics-education.md) w2-04-03 ✓ |
| 3 | **Supported diagram practice for `diagram` parts.** In `explain_back` (and `teach_point` at hint level): "Sketch it on paper. Then tell me which curve moves, which way, and what happens to price and quantity." Then compare the answer with the reference description. That comparison is the integration step. Never a bare "draw it" with no follow-up. The server never sees the sketch, so we don't claim to assess diagrams. This uses the same wording as [04](04-economics-education.md) check type C3. Keyed on `support.procedural_types`. | `text/moves/explain_back.md`; demo | S | yes | w2-03-03 ~ |
| 4 | **Pitch and video line: "We set difficulty for learning, not for time on the app."** Easier game versions kept players longer but taught slowest. eduX sets support by `p_now` and has no streaks. Pair it with the DfE standard against engagement-prolonging features. | pitch, video | S | yes | w2-03-12 ~ |
| 5 | **"Sleep on it" in `offer_stop`.** Add one optional sentence: "A short go tomorrow will stick better than more tonight." This is lab evidence from 40 adults learning vocabulary, and scheduling doesn't change (`min_gap_days = 1` already). No sleep tracking or profiling. | `text/moves/offer_stop.md` | S | yes | w2-03-16 ~ |
| 6 | **Rotate distractors (speculative).** When a part has more than `max_options − 1` misconceptions, `distractors()` picks with a seeded rotation. It always includes one the student holds, then the least recently shown, and still prefers examiner-report rows. This doesn't fix the option-form give-away ([04](04-economics-education.md) rec 1). Setting `mcq.rotate = true`. | build (`edux/plan.py`), settings | S | yes (optional) | w2-03-13 ~ (analogy) |
| 7 | **Pitch Q&A framing from checklists, deliberate practice and nudges.** "Every answer is checked against named points, by the student." Checklists worked when owned and failed when mandated. Practice hours explain little in education. Planning and reminder nudges gave nulls on grades, including the UK FE trial. So eduX puts its effort into teaching moves, not nudges. Present these as analogies or as other people's trials, never as eduX evidence. | pitch, business plan | S | yes | w2-03-09 ~, -11 ~, -14 ~, -15 ~ |
| 8 | **Relearn inside a session: skippable, a different question, with a reason.** Details below. Spec it in the white paper if it isn't built on Wednesday. | build (`plan.py` / `service.py` pending-review queue), settings, `text/` | M | maybe | w2-03-04 ~; student panel #1 |
| 9 | **Optional student-written next-step plan (implementation intention), exam-directed only.** At most once a week, when the student stops: "Want to pick when and where you'll do your next 10 minutes on X?" It stays in the chat. No reminders, no streaks, nothing stored server-side, and never "come back to eduX". Call it optional study-skills support, not a learning gain. | `text/` only | S | optional, low priority | w2-03-07 ~, -08 ~ |

### Rec 8 in detail: relearning the student won't resent

The panel student said a re-asked question "feels like detention", and that it sends them back to ChatGPT. Their fix has three parts: say why it's back, ask a different question, and let them skip it. Higham's study re-asked the same fill-in-the-blank items, not MCQs (w2-03-04 ~). We assume the benefit comes from retrieving the missed point again, not from identical wording. That is our assumption, and it is untested.

- **Trigger.** A review check is missed. eduX gives feedback, then queues one re-ask for later in the same session, after at least one other exchange. At most 2 re-asks per part per session, following Higham's "up to two more times".
- **Say why, in one line.** For example: "One more go at this later so it sticks. Skip it if you like." The reason is part of the plan text, not left to the chatbot.
- **A different question on the same missed point, built from what exists.** There is no item bank, so "different" means one of:
  - the missed point as a **one-line explain-back** ("in a sentence, why…?") instead of an MCQ; or
  - the missed point as an MCQ with a **different cue** (for example the review or transfer cue instead of the check cue), **fresh distractors** (rec 6's rotation) and new letters.

  Never the same stem with the same options, and never a different point: that would not re-test what was missed.
- **Skippable with one tap.** A skip is **not a miss**: it writes no evidence. The part keeps its normal spaced review on a later day, which the student panel asked to be told ("you'll still see it on a later day").
- **Scoring.** A within-session re-ask is not a new spaced review and earns no half-life growth. Performance right after feedback overstates learning (CSV 7a-08, 7b-14), so the re-ask is scored with a raised guess (`relearn_guess = 0.35`, our choice). Two correct re-asks then can't push a weak part past secure. Only the next spaced review counts in full. This matches two **proposed, not live**, settings in `settings-proposal.toml`: `decay.on_success_immediate = 1.0` and `one_review_per_part_per_session`, where the latter counts only the first, spaced review.
- **Order of rules.** The fatigue rule wins: there is no re-ask when fatigue or a stop is flagged. With `points.reteach_limit = 1`, the sequence is reteach once, then the re-ask, then move on.
- **Settings (our choice):** `[scheduling] relearn_in_session = true`, `relearn_max = 2`, `relearn_min_gap_exchanges = 1`, `relearn_skippable = true`, `relearn_guess = 0.35`.

Open: how many extra exchanges this adds per session for a weak student, and whether it collides with `fatigue_min_minutes = 25`. A simulation (synthetic students, example pack) should answer that before we build it. Whether a *skippable*, *reworded* re-ask keeps the accuracy gain is untested (student panel question 3).

## Later (not before Thursday; for the business plan and Q&A)

- **Success-rate targeting in the CAT style.** Once enough responses exist to calibrate items (Elo; CSV 8-05), select reviews by maximum information at a shifted ability (w2-03-13 ~). The target success rate is our choice, tuned on data. There is **no** evidence-based "70%" or "85%" (CSV 2-11, 7b-01).
- **A/B test the one-line self-mark** once pilots exist. The Sanchez et al. effect comes from classrooms with rubrics and training (w2-03-02 ~), and nobody has tested a chatbot version.
- **A contrasting-cases study on economics concepts.** The larger effects in Alfieri et al. came from perceptual content and immediate tests (w2-03-01 ~). Economics is verbal and the exam is delayed, so expect less than d = .50.
- **Successive relearning with 14–18-year-olds.** Get the full text of Rawson, Dunlosky & Sciartelli (2013). Its abstract is elided, so no numbers are claimed.
- **The EEF FE texting report's effect sizes and CIs.** The pages returned 403 (w2-03-11 ~).
- **Add w2-03-06 (generation effect, d ≈ 0.40) to `research.md`** as backing for pre-questions and the hint level's "last step left for you". Team edit to `docs/build/`.

## Considered and rejected

| Idea | Reason |
|---|---|
| Texting students or parents | eduX is called by a chatbot and can't send messages. Collecting phone numbers breaks the privacy checklist (§5). The UK 16–19 FE trial found 0 months' progress (w2-03-11 ~). |
| Commitment contracts | They raised exam sign-up and passing at a German university and completion in a MOOC (w2-03-10 ~). But eduX owns no deadlines, and "commit to coming back" is engagement-prolonging (DfE). Rec 9 is the most we'd do. |
| Planning modules with reminders | Precise nulls on grades in more than 9,000 college students (w2-03-09 ~). |
| Productive failure beyond one pre-question | Already rejected (CSV 2-06). The average gain is g = 0.36 [0.20, 0.51], larger only with high-fidelity design that includes a consolidation phase chat can't guarantee (w2-03-05 ~). Don't quote the bias-adjusted 0.87 without that caveat. |
| Elaborative interrogation as its own move | It overlaps with explain-back and `extend`. We found no newer meta-analysis than Dunlosky et al. (2013), which we didn't re-read. |
| The generation effect as a new feature | It is real (w2-03-06 ~), but it is already built into pre-questions, the hint level and explain-back. Extending it to `show` would ignore expertise reversal (CSV 2-01). |
| A hypercorrection boost | Already rejected as a `p_known` boost (CSV 3-08, 3-09). |
| A fixed 70% or 85% success target | A myth (CSV 2-11, 7b-01). Maximum-information testing gives about 50% correct, and easier targets cost precision (w2-03-13 ~). |
| A mandated checklist on every turn | The Ontario null argues against imposed checklists (w2-03-14 ~). The light, skippable self-mark (rec 2) is the version with education evidence. |
| Scheduling around sleep | We can't see sleep and must not profile it. The lab study is 40 adults learning vocabulary (w2-03-16 ~). |
| Re-asking the same question word for word | The student panel's objection, and the evidence doesn't need it (rec 8). |

## Panel objections this report answers or leaves open

Status words: **answered** = built or answered by a document; **recommended** = fix recommended, not built; **partly**; **open**.

| Objection (panel) | Status | Where |
|---|---|---|
| "You're bringing back the re-asked question; it feels like detention" (student #1) | **Recommended** | Rec 8: skippable with one tap, a skip is not a miss, a different question on the same point (an explain-back, or a new cue with fresh options), a one-line reason, never when fatigued. Not built. |
| "Self-marking: I'll tick everything; it costs a turn" (student #4) | **Recommended** | Rec 2: one tap, skippable, once per session, shows where student and marking disagree. Self-marks never change `p_known`. Not built. |
| "What does self-marking teach about levels?" (teacher Q&A 3) | **Recommended** | Rec 2: point-marked 4- and 8-markers only, never on 12- or 25-markers. |
| "Why will contrasting cases work here? Are the pairs in the pack?" (teacher Q&A 5) | **Partly** | d = .50 is cross-field, with larger effects for perceptual content (w2-03-01 ~). The example pack has one pair. The rest are [04](04-economics-education.md) rec 6, a team edit not yet made. |
| "Selection still counts towards mastery; C3 never makes anyone draw" (teacher #3) | **Recommended** | Rec 3 here and C3 in [04](04-economics-education.md): sketch on paper, then answer. The server never sees the sketch. |
| "Not making it easier just to keep me on it. I'd trust that" (student praise) | **Answered** | eduX already sets support by `p_now` and has no streaks. Rec 4 turns this into a pitch line (w2-03-12 ~). |
| "Can I send a photo of my diagram?" (student Q&A 2) | **Open** | Not researched. Whether chatbot image input can reliably label a shift is a next-wave question. |
| Teacher-screen flag rates, draft counts, school routes (teacher #4–5, student #2–3, #5) | **Open** here | Not learning-science questions; see the product, safety and competition reports. |

## Findings

All marks are ~ because the verifier read abstracts only. The caveats are given in short form.

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w2-03-01 | Case comparison beat other case formats and ordinary teaching, d = .50 [.44, .56]; larger with similarity search, principle after comparison, perceptual content and immediate tests | meta-analysis (57 experiments, 336 tests) | mixed lab and classroom; ages not given; not 16–18-specific, not UK | learning | ~ abstract only |
| w2-03-02 | Self-grading g = .34, peer grading g = .29; self vs teacher grades g = .04, r = .67 | meta-analysis | grades 3–12 (includes 16–18); country not given | learning | ~ abstract only; larger in randomised studies; small evidence base |
| w2-03-03 | Drawing support aimed at integration g = 0.35; without integration g = −0.15 (n.s.); 14 studies, N = 1,213 | meta-analysis | mostly science learning; ages not given | learning | ~ abstract only |
| w2-03-04 | Missed items re-asked up to 2 more times per session; relearning beat restudy at end of term, exposure controlled | RCT (within-class) | university introductory psychology; country not in abstract; not 16–18 | learning | ~ abstract only |
| w2-03-05 | Problem solving before instruction g = 0.36 [0.20, 0.51]; high-fidelity design 0.37–0.58; bias-adjusted 0.87; instruction first favoured for grades 2–5 on domain-general skills | meta-analysis (53 studies, 166 comparisons) | mixed school and university; not UK | learning | ~ abstract only; "on", not "and", domain-general skills (a combined condition) |
| w2-03-06 | Generating items rather than reading them improved memory, about 0.40 SD (86 studies, 445 effect sizes) | meta-analysis | mostly adult lab, word lists | learning | ~ abstract only |
| w2-03-07 | Implementation intentions .27 ≤ d ≤ .66 across 642 tests; larger with if-then format, high motivation, rehearsal | meta-analysis | mostly adults; not 16–18 | engagement / interest (behaviour, cognition, affect; mostly not grades) | ~ abstract only; online 2024, volume dated 2025; publication bias |
| w2-03-08 | MCII: high-school students did >60% more practice questions (n = 66); 5th graders' grades partial η² = .07, attendance .05, conduct .07 (n = 77) | RCT (small) | 2011: high-school 2nd-years, country not named; 2013: US low-income urban 5th graders | engagement (2011); learning (2013) | ~ abstracts only; partial η² values |
| w2-03-09 | Low-touch time-management programmes: precise nulls on credits, grades and retention (>9,000 students, 3 colleges) | RCT | US/Canadian college students | learning | ~ abstract only; two separate programmes (planning module; texts or coaching), not one |
| w2-03-10 | Soft commitment raised exam sign-up, participation and passing; reminder alone did not. MOOC commitment device: +40% completion, +0.29 SD grades | RCT (field) | university students; MOOC adults | adoption (sign-up, completion); learning | ~ abstracts only; Himmler's German business-student population and Patterson's n = 657 not stated in abstracts |
| w2-03-11 | Texting GCSE-resit students and/or supporters: 0 months' progress in each arm (3,779 students, 31 FE colleges). Texting Parents: about +1 month maths (36 schools, ~16,000 pupils) | RCT (official evaluation) | **UK, 16–19 FE**; secondary pupils | learning | ~ secondary sources only (EEF pages 403); not confirmed per subject |
| w2-03-12 | Easier game versions kept players engaged longer; the most engaging conditions gave the slowest learning (~10,000 and ~70,000 players) | RCT (online) | anonymous online players; age not given | engagement vs learning (opposite) | ~ abstract only |
| w2-03-13 | Maximum-information CAT gives about 50% correct; shifted-ability selection gives easier tests under 1PL and 2PL | simulation / theory | simulated test-takers | prediction (measurement precision) | ~ abstract only |
| w2-03-14 | Surgical checklist: deaths 1.5% → 0.8% in 8 hospitals (pre/post); mandated Ontario rollout, 101 hospitals: OR 0.91 [0.80, 1.03], no change | quasi-experimental | surgical patients 16+; analogy only | n/a (analogy; health outcomes) | ~ abstracts only |
| w2-03-15 | Deliberate practice explains 26% of variance in games, 21% music, 18% sports, 4% education, <1% professions | meta-analysis (correlational) | mixed | learning/performance (correlational) | ~ abstract only |
| w2-03-16 | Sleeping between two relearning sessions halved relearning practice and improved retention at 1 week and 6 months (n = 40) | RCT (small lab) | adults, foreign vocabulary; ages not given | learning | ~ abstract only |
