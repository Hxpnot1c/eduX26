# Research

The evidence behind Synapse's teaching and modelling decisions. Effect sizes are as reported by each source. Settings based on them are starting points, to be refitted from real data.

**How to read this file:**
- **Finding ids** (e.g. `w1-06-07`) refer to the overnight research on branch `research/overnight`, in `docs/research/overnight/findings.csv`. Their marks: ✓ = verified by a blind verifier; ~ = partly verified or corrected.
- **"Our simulation"** means synthetic students on the example pack. It measures whether the model's estimates match a simulated truth, or how the code behaves. It is never a learning gain, and never evidence about real 16–18-year-olds.
- **Settings** are labelled in `settings.md` as "from research" (with the source here) or "judgement call, starting value".

---

## Teaching moves

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Pre-questions | St. Hilaire, Chan & Ahn (2024), *Psychonomic Bulletin & Review*, meta-analysis | g = 0.54 on the asked material; multiple choice ≈ short answer; guessing 0.65 vs reading 0.22 | Near-zero benefit on material not asked about (0.04) |
| Bridge question to the next topic aims at its first key point | St. Hilaire, Chan & Ahn (2024) | The benefit is specific to what the prequestion asked, so the bridge asks about the next part's first key point, framed through the link | No general benefit, so a vague "any thoughts?" bridge wouldn't help |
| Pre-questions, wider benefit of multiple choice | Little & Bjork (2016), *Memory & Cognition* | Multiple-choice pretests helped related information more than cued recall | Not supported overall by the meta-analysis |
| Pre-questions in classrooms | Soderstrom & Bjork (2023); Geller et al. (2017) | One classroom benefit; one null result in STEM | Mixed classroom evidence |
| Repeated "just show me": a 2-option question first, then the show | St. Hilaire, Chan & Ahn (2024) (pretesting) | Trying before being told helps learning even when the guess is wrong; the full show still follows, so a stuck student isn't refused | The 3rd-request trigger is a judgement call |
| Correct the chosen option | Roediger & Marsh (2005); Butler & Roediger (2008) | Multiple-choice wrong options can be learned; feedback reduces this | |
| A right answer below secure gets one line on why, judged on the level *before* the answer | Butler, Karpicke & Roediger (2008); Wisniewski, Zierer & Hattie (2020) | Feedback on correct answers helps most when the learner was unsure; the answer that tips a part to secure may be a lucky guess | |
| Explain-back | Bisra et al. (2018), *Educational Psychology Review* | Self-explanation prompts g = 0.55 (64 reports) | Mostly undergraduates |
| Re-teach only the gap | Wisniewski, Zierer & Hattie (2020), *Frontiers in Psychology* | Feedback d = 0.48; effect depends on how much information it carries | |
| Completion problems for procedures only | Barbieri et al. (2023); Zamary & Rawson (2018) | Worked examples help maths; faded examples no better for declarative concepts | |
| Reviews in a new context | Pan & Rickard (2018), *Psychological Bulletin* | Transfer d = 0.40; strongest to application and inference | Needs explanatory feedback and some initial success |
| Higher-order questions from developing | Agarwal (2019), *Journal of Educational Psychology* | Higher-order and mixed quizzes beat fact quizzes for higher-order learning | |
| Levels plus next step | Koenka et al. (2021), *Educational Psychology*; Koenka (2020) | Comments beat grades alone; grades plus comments best for motivation | |
| One point per message | Rey et al. (2019), *Educational Psychology Review*, meta-analysis | Meaningful, learner-paced segments improve retention and transfer, and reduce load | Mostly multimedia, not chat. A student's "more detail" raises a teaching step only to 120 words (judgement call) so it stays one point |
| Check after each point | Chan, Meissner & Davis (2018), *Psychological Bulletin*, meta-analysis | Testing earlier material improves learning of the next material | |
| Not too often | Davis, Chan & Wilford (2017) | Frequent switching between retrieval and study can impair new learning | |
| Move on once a point is learned, with a skip | Kulik, Kulik & Bangert-Drowns (1990), *Review of Educational Research* | Mastery programmes: about 0.5 SD, larger for weaker students | Can lower completion; estimates vary widely across syntheses |
| Performance straight after teaching isn't treated as retention | Soderstrom & Bjork (2015), *Perspectives on Psychological Science* (learning vs performance) | Performance just after instruction overstates what's retained | So immediate evidence keeps its own handling, and "secure" needs a correct answer on a later visit |
| Shorter replies once a part is known | Kalyuga, Ayres, Chandler & Sweller (2003), *Educational Psychologist* | Expertise reversal: full explanations that help novices slow down learners who already know the material | So reviews and checks on known parts get about half the words |
| No learning styles | Pashler, McDaniel, Rohrer & Bjork (2008), *Psychological Science in the Public Interest* | No good evidence that matching format to a student's learning style helps | Diagrams follow the content, never the student |
| The student sketches the diagram, then explains it | Leutner & Biele (2025), *Educational Psychology Review* 37, https://doi.org/10.1007/s10648-025-10067-7 | Drawing support that helps integration: g = 0.35 (14 studies, 16 comparisons, N = 1,213); other drawing support g = −0.15, n.s. | Cited for the sketch cue only, not for the chatbot drawing. Checked against the abstract; the issue is given as 37(4) in one source and 37(1), art. 93, in another |
| Study plans with days and topics | Sheeran, Listrom & Gollwitzer (2024), *European Review of Social Psychology*, meta-analysis of 642 tests (w2-03-07 ~); Duckworth et al. (2011) (w2-03-08) | Implementation intentions (if-then plans) improved outcomes, d = .27–.66; mental contrasting with implementation intentions led high-school students to complete over 60% more practice questions | So `plan_my_study` gives concrete days and parts, not a general "revise more" |
| Write-up plans never write the content | JCQ AI Use in Assessments (2025) (w1-02-13 ✓); DfE Generative AI product safety standards (2026) (w1-02-12 ✓) | Unacknowledged AI use in assessed work can be malpractice; tools shouldn't hand over final answers by default | |
| Checking sources | Wineburg et al. (2022), *Journal of Educational Psychology* | Six lessons in lateral reading improved high-school students' judgement of online sources (randomised) | About websites, not AI output |

## Learner model and settings

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Open-answer guess 0.20 (explain_back, past_question, link, extend) and spacing shares 0.10 / 0.19 / 0.30 | Settings proposal (`docs/research/settings-proposal.toml`); tested in overnight report 06 (w1-06-04 ✓, w1-06-05 ✓) | Far scenario: false "secure" on exam day fell by 20.6 points (paired CI ±5.8); truly secure parts rose by +0.5 (near) and +0.8 (far) of 9; reviews due per morning fell from 4.5 to 2.9 | Our simulation |
| MCQ guess = 1 / options shown | Standard BKT practice; overnight report 06 | Chance of guessing depends on the number of options | |
| `review_when_below = 0.50` (a **judgement call**; corrected 19 Nov) | Eglington & Pavlik (2020), *npj Science of Learning* 5, 15 (nearest study); our simulation | The study (291 adults, word pairs) found recall thresholds of 0.86 and 0.94 beat 0.40, 0.98 and conventional spacing, and did not differ from 0.70; 0.50 was not tested, and the quantity is a fitted recall probability, not our `p_now`. In 60 synthetic students per row, raising the threshold to 0.75 gave slightly lower retention and fewer truly secure parts at the same workload | Our simulation; the truth model is ours (`docs/research/review-threshold-simulation.md`). The earlier "0.70 to 0.80" is an interpolation, not a finding |
| Surprise = score − expected success, with expected = p(1 − slip) + (1 − p) × guess | Overnight report 06 | Counts guessing and slips, so weak students aren't cushioned and strong students aren't penalised | |
| Clamp `p_known` to [0.001, 0.999] | w1-06-01 ✓, w4-fix-core-1 ✓ | Reaching exactly 1.0 crashed `tutor_turn` with a divide-by-zero | Bug fix found by simulation |
| One step back per stuck part per session, then a stuck ladder | w1-06-02 ~, w4-fix-core-2 ✓, w5-fix-stuck-1 ✓ | The step-back check repeated on 12 of 14 turns; with the ladder an always-failing student gets a stop/switch offer at turn 8 instead of never | Our simulation |
| Review requests reach the reviews | w1-06-03 ✓, w4-fix-core-3 ~, w5-fix-reviews-1 ✓ | "Quiz me on what's due" taught the old focus; review asks now answered 18/18 | |
| A research or other message never sets the course focus | w4-fix-focus-1 ✓ | False focus fell from 15/43 to 3/43 | |
| Decay towards the starting estimate (patch 0005; **built**, decision 0025: the normal start, Ask and Verify towards 0) | w3-06-01 ✓, w3-06-08 ✓, w3-06-09 ~, w4-fix-core-4 ✓ | On `main`, a part answered right once fell below an untouched part after 4.4 days. Decaying to the prior cut day-30 inversions from 0.82–1.00 to 0.03–0.26 and raised AUC from 0.48–0.59 to 0.62–0.71; a talk-only part reads 0.300 instead of 0.763 | Our simulation. Built 19 Nov with the normal start as the floor for every part (the covered start, about 0.41, is above `levels.new`); patch 0005's cap on never-right parts stays held (the nudge ceiling, decision 0003, covers talk). Class simulation at week 8: 90% of taught pairs new before, 84% after by the number, 22% shown new and 63% "needs review" |
| Starting points depend on whether the class has covered the topic | Koedinger, Carvalho, Liu & McLaughlin (2023), *PNAS* | Achievement gaps come mainly from differences in learning opportunities, so a student who does well early has most likely been taught it in class | The covered-topic default prior (0.50) is a judgement call, replaced per class by the class's own first answers |
| The forgetting clock starts on the date a topic was taught in class | Cepeda et al. (2008); the decay model | Topics taught but never practised in Synapse fade and get scheduled for review | |
| Prerequisites feed forward into new parts' starting points | Käser et al. (2014), ITS; Käser et al. (2017), *IEEE Transactions on Learning Technologies* | Modelling links between skills outperformed plain BKT in prediction on five large datasets | `forward_weight = 0.5` is a judgement call |
| Richer correct open answers count for more (guess 0.20 / 0.15 / 0.10 for ≤2 / 3 / 4+ mark points) | Reasoning, not a study | A complete multi-point answer is far harder to produce by luck than picking a letter | Judgement call |
| Weakest point from each point's last 5 answers | Galyardt & Goldin (2015), EDM, "Move your lamp post" | The best-predicting recency weighting puts 75–93% of the weight on the last 5 attempts | ASSISTments maths data |

## Personalisation: where students start, and how fast they learn

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Personalise the starting point quickly | Koedinger et al. (2023), *PNAS*: 1.3 million observations, 27 datasets | Students started in very different places but learned at astonishingly similar rates, about 0.1 log-odds (2.5% accuracy) per opportunity | Online practice systems with feedback |
| … replicated at scale | Simpson, Norberg & Fancsali (2024), EDM: 822k MATHia records | Student learning-rate variance was 37–430× smaller than starting-knowledge variance; starting-knowledge SD about 0.57–0.90 logits | Six maths topics |
| … but the size of the learning-rate spread is uncertain | Lee, Lichand et al. (2026), arXiv 2605.01690 | The same model on the same data gives learning-rate variation inflated by a median of 118% depending on which observations are included | Preprint |
| A per-student starting point | Pardos & Heffernan (2010), UMAP | Individualising the initial-knowledge parameter gave a reliable improvement in predicting real data, even set simply from first responses | |
| The counterpoint | Yudelson, Koedinger & Gordon (2013), AIED | In individualised BKT, student-specific learning speed helped prediction more than student-specific prior knowledge | Older, smaller-scale than Koedinger (2023) |
| Coverage lifts a covered part's start by 0.5 log-odds; no start above 0.65; a part with no answer never shows developing or secure | Koedinger et al. (2023) on learning opportunities; the decisions of 18 November | Achievement gaps come mainly from what students have been taught; a start is a prior, not a result | The size (0.5) and the cap (0.65) are judgement calls; display rule follows the nudge ceiling (decision 0003) |
| ~~A part taught in class and never answered forgets only to its untaught start~~ (superseded by row 53, decision 0025) | Reasoning | With a 2-day half-life a part taught weeks ago would decay to 0.00, below an untaught one (0.30) | Superseded: the floor in row 53 now covers answered and unanswered parts alike (`_floored` removed; its guarantee is a test) |
| Starting adjustment: k = 25 first answers, bounds ±1.5 logits | Simpson et al. (2024) spread plus our simulation | With that spread, k ≈ 18–44 for half weight; after 10 first answers the estimate correlates 0.4–0.6 with the truth | Our simulation |
| Starting adjustment split into covered and not-covered sectors | Koedinger et al. (2023), opportunities | Success on topics taught in class says little about topics not yet taught | |
| Only pre-teaching answers feed the starting adjustment | Soderstrom & Bjork (2015) | Answers straight after teaching show the student followed it, not that they knew it | |
| Learning-rate offset **off by default**; starting-point adjustments stay on | ICO Children's Code, Standard 12 (profiling off by default unless there is a compelling reason); `personalisation.md` §5 ("off until evaluated") | After recalibration the offset barely moves, so switching it on buys little and is profiling a minor | A judgement call about risk, not a finding about learning |
| Learning-rate offset recalibrated: k = 400, scale 1.0, bounds 0.7–1.3, recency half-life 100 | Koedinger (2023); Simpson (2024); our simulation | After 48 answers, average surprise correlates only 0.10–0.23 with the true learning rate at research-sized spreads (10–30%), implying k ≈ 400+ and a scale ≈ 0.2–1.0 | Our simulation; the half-life is a judgement call |
| The offset uses only answers after the first on each part | Reasoning | Otherwise "already knew it" is counted twice: once in the starting point and again as faster learning | |
| Downward moves allowed more readily (factor 2) | Doroudi & Brunskill (2019), LAK, "Fairer but not fair enough" | Models fit to the whole population can leave lower-performing students under-practised; over-crediting is the more harmful mistake | The direction is from the source; the factor of 2 is a judgement call |
| AI-literacy evidence stays out of personalisation; AI-literacy parts use the population rate | Reasoning | A different skill, measured differently; an Ask score comes with every research question and would swamp the average | |

## Fatigue, timing and rapid guesses

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Time-based slip: 0 before 28 minutes, then +0.002 per minute, capped at 0.12 | Randles, Harlow & Inzlicht (2017), *PLOS ONE* | In 72,082 and 147,186 online self-testing sessions, accuracy declined from about 28 minutes and was 4–5 points below its peak by about 50 | Online self-testing by undergraduates; one author worked for the data provider |
| The cap of 12 points | Brown, Kaur, Kingdon & Schofield, "Cognitive endurance as human capital" (NBER working paper); TIMSS analysis in the same paper | About 7.5% (TIMSS) to 12% lower chance of a correct answer late in a test | Primary-school and international test data; the cap is picked from the range |
| Fatigued mode from 50 minutes, no break offers before then | Randles et al. (2017) | A meaningful drop by about 50 minutes; set to suit classroom-length sessions | |
| A 30-minute gap starts a new session | Sievertsen, Gino & Piovesan (2016), *PNAS*; Lee (2018), *Computers in Human Behavior* | A 20–30 minute break raised test performance by 1.7% of an SD; studies drop gaps above a 10–60 minute cut-off as off-task | |
| The 4-answer average fatigue rule is dropped | w1-06-08 ~ (overnight); our simulation | The built detector flagged 12% of tired-student sessions against 11% of others' (likelihood ratio about 1.1). Our simulation of the 4-answer rule flagged 77% of not-tired students by 60 minutes | Pilot and simulation |
| Answers alone can't reliably detect a tired student at chat pace | Our simulation, with the research-sized drop | A sequential test with false alarms held to 11% of 60-minute sessions caught only 27% of tired students by 60 minutes | One answer every 2 minutes assumed; check against real logs |
| No "slow answer" rule | Boksem et al. (2005), cited in Mangin et al. (2022), *Frontiers in Psychology* | After 3 hours of a task, reaction time rose only 5.2% (misses +71%), far below normal variation in chat reply times | |
| No response-time variability signal | Esterman et al. (2013), *Cerebral Cortex*, "In the zone or zoning out" | Variability marks attention lapses, but it needs many responses per minute | Not usable at chat pace |
| Rapid guess = faster than reading the question at 300 wpm plus typing the answer at 52 wpm | Brysbaert (2019), *Journal of Memory and Language*: 238 wpm mean for non-fiction, 175–300 range; Palin et al. (2019), MobileHCI: 36.2 wpm on phones (37,370 volunteers); Dhakal et al. (2018), CHI: about 52 wpm on keyboards | The fastest normal reading and typing speeds, so few students are flagged wrongly | Latency includes the chatbot's generation time, which makes flags less likely |
| Rapid guesses don't count towards knowledge | Wise & Kong (2005); Wise & Ma (2012), normative threshold method (NT10, with 20–30% also used); Wise & DeMars (2006), effort-moderated model | Rapid guesses are about as accurate as chance and signal disengagement | Developed for low-stakes tests |
| Fatigue curves per student and per class | Wu, Debeer et al. (2019), *Large-scale Assessments in Education* (PISA) | How well test takers keep up their performance varies considerably between people | Class curves show students' own sessions; those who choose long sessions may differ |

## Priorities, assessments and coverage

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Spacing anchored to the exam | Cepeda et al. (2008) | The best gap shrinks as the test gets closer | |
| Spacing towards the student's own and the class's tests | Cepeda et al. (2008) | The best gap depends on how far away the test is, so a mock pulls spacing towards it | Lab and online studies, not school tests |
| Hand-set priorities before a learned policy | Doroudi, Aleven & Brunskill (2019), *International Journal of Artificial Intelligence in Education* | Reinforcement-learning instructional policies mostly didn't beat sensible rule-based baselines | So the `[priorities]` weights stay hand-set until there's real data; the options not picked are logged for that |
| The ending of a reply follows a fixed order: urgent review, bridge, extend, other review | Cepeda et al. (2008); St. Hilaire, Chan & Ahn (2024) | Protect what's about to be tested, then build forward | The order itself is a judgement call |
| `move_chance` removed from the score | Reasoning | One learning rate for all evidence types makes it a constant, so it never changed a choice | Per-type learning rates are a research item in `later.md` |

## AI literacy

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| The framework | OECD / European Commission (2026), AILit Framework, doi:10.1787/65cd27d4-en (w1-02-01 ✓) | Four domains (Engage, Create, Manage, Shape) with 19 competences | |
| Verify as an Engage 3 skill | AILit Engage with AI 3 (w1-02-03 ✓) | Expectations progress from why to verify, to verifying against trusted sources, to justifying decisions | |
| Assess AI literacy inside normal work | Shute (2011); Rahimi & Shute (2023), *ETR&D* | Stealth assessment embeds evidence collection in the learning activity and supports the skill as well as measuring it | Evidence mostly from games and simulations |
| Competency, evidence and task models | Mislevy, Steinberg & Almond (2003) | Evidence-centred design links what's measured, what counts as evidence and where it comes from | |
| Behaviour, not self-report | Lintner (2024), *npj Science of Learning* | 3 performance-based vs 13 self-report AI-literacy scales | |
| Performance predicts better | Jin et al. (2025), GLAT, *Computers and Education: AI* | A performance test predicted AI-assisted task performance better than self-report | A separate test, university students |
| How-AI-works checks | Ng et al. (2021); AILit (2026) | "Know and understand AI" / "Shape AI" are core aspects of AI literacy | Their ranking of students was near chance on 05e settings (w2-02-05 ~); patch 0005's decay, now built (decision 0025), is expected to improve it (AUC 0.85–0.88 in simulation) |
| The `pushback_changed` label | Fanous et al. (2025), SycEval, arXiv:2502.08177 (w2-02-38 ✓) | Rebuttals changed chatbot answers in 58% of cases, 15% towards a wrong answer | |
| A found dead or mismatched source scores 1; an ignored task is a skip, not 0 | w4-fix-verify-1 ✓; w2-02-07 ✓ | A reported dead page moves Verify from 0.300 to 0.748 instead of down to 0.143; recording ignored tasks as missing barely changes false-secure | Our simulation |
| Scoring isn't gaming-proof; caps on cheap reports | w5-06g-01 ~; w6-c2b-1 ✓, w6-c2b-2 ✓; w6-c1b-1 ✓, w6-c1b-2 ✓ | Two bare "the link is broken" reports made Verify secure for 100% of zero-skill students; the dead-link cap takes them to 0% at a small honest cost (62% vs 64%); the show-then-pick cap takes "show me, then match" gamers from 9 secure parts to 0 | Never claim "gaming-proof" |
| The Ask guard | w5-fix-guard-1 ✓ | Answers labelled as research no longer write Ask 0.0 | |
| AI-literacy scoring is a school setting (`literacy.scoring_enabled`) | Overnight report 09 (safety and ethics), rec 11 | The school's public task covers AI-literacy scoring only where the school teaches AI literacy | Held item |

## Multiple-choice quality

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Options alike in form, and right-option length rank checked | Haladyna, Downing & Rodriguez (2002), item-writing guidelines (via w3-05-08 ~) | Every example-pack part's right option differed in form from its wrong options | |
| … and the effect of fixing it | w4-fix-mcq-1 ✓; w5-06g-05 ~; w6-len-1 ✓ | A testwise student who knows nothing fell from 0.96 to 0.28 right (chance 0.31). A remaining cue (drop longest and shortest) got 58%, addressed by patch 0011's rewording and ingest warnings | Our simulation; the wording needs an economist's read |
| Rotating wrong options (held) | Roediger & Marsh (2005) | Seeing the same wrong option repeatedly can teach it | Held item |

## Confidence and calibration (step 05z)

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Calibration (confidence against accuracy) as a signature measure, shown to the student as feedback | Fernandes et al. (2025), CHI; the project's literature review (Summary §3.2, principle 3) | AI use raised task scores but inflated self-estimates, and higher AI literacy predicted worse calibration | One research group, seen via a secondary paper; no validated reliance instrument exists |
| Ask for the commitment before the feedback is revealed | Buçinca et al. (2021), CSCW, cognitive forcing | Making people commit before the AI's answer reduced over-reliance, and was liked less | Decision tasks with AI recommendations, not revision checks |
| Optional, switch-off, no penalty for skipping | ICO Children's Code, Standard 5 (detrimental use of data); `personalisation.md` §2.4 | Do not make a measure a hurdle or a source of pressure | Design guidance |
| Asked only after `confidence.after_rapid` (2) rapid-guess check answers in a row, once a session; two skipped asks in a row (across sessions) stop it; the rushing break offer waits until rushing continues (decision 0027) | Wise & Kong (2005) for the rapid-guess rule; Buçinca et al. (2021) for committing before feedback | A rapid guess is answered faster than the question can be read: the moment a prompt to commit has most to work on | Judgement call (Vishnu, 19 Nov): no study compares asking always with asking after rapid guesses. The calibration line fills slowly and leans to rushed answers |
| A calibration line only after 5 rated answers in a level | Our own arithmetic: small counts mislead (research summary §6(e)) | A level with fewer than 5 answers swings with one answer | Judgement call |
| Rating never changes p_known | Reasoning | A self-report is a different quantity from a performance; mixing them would let confidence inflate or deflate the model | Tested |
| Not built: early review of high-confidence errors (hypercorrection) | Butterfield & Metcalfe (2001) | Errors made with high confidence are corrected well when feedback is given | Lab recall of facts; thin for A-level |

## Reminders, deadlines and study plans (step 05u)

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| A concrete plan with days and topics | Sheeran, Listrom & Gollwitzer (2024), meta-analysis; Gollwitzer & Sheeran (2006); Duckworth et al. (2011) | Implementation intentions improved outcomes (d = .27 to .66); with mental contrasting, high-school students completed over 60% more practice questions | Mostly other goals and populations; not tested on chat-generated plans |
| Spacing towards the class's tests; weakest first | Cepeda et al. (2008), *Psychological Science* | The best gap is a falling share of the time to the test | Adults, trivia facts |
| In-chat reminder only, once, switch-off, no streaks | Fryer (2016), *Journal of Public Economics*; Oreopoulos et al. (NBER w25036); Bergman & Chan (2021); ICO Children's Code, Standards 5, 12 and 13 | Texts to students alone had no measurable effect on outcomes; texts to parents did; nudges can crowd out motivation (Damgaard & Nielsen, 2018) | So the reminder is a courtesy, not a claimed lever; the opt-out and wording are design guidance (the Code's Standard 13 text is about data and privacy nudges) |
| A written-assignment plan never writes the content | JCQ (2025) on unacknowledged AI use in assessed work; DfE (2026) on tools not handing over final answers | Unacknowledged AI use in assessed work can be malpractice | Guidance, not an experiment |
| Teacher-set low-stakes quizzes help | Yang et al. (2021), *Psychological Bulletin* | Classroom quizzing g = 0.50 (222 studies) | Abstract-level read |

## Evidence for held work (not yet built)

| Planned item | Source | What it shows | Caveat |
|---|---|---|---|
| Reteach as refutation: name the wrong idea, then ask a probe | Schroeder & Kucera (2022), refutation-text meta-analysis; Danielson et al. (2025) | Refutation texts g = 0.41 | |
| Guiding question at the gap | Asher, Cao & Carvalho (2026) | Socratic tutoring +0.24 SD | Preprint |
| Twin-concept contrasts | Alfieri, Nokes-Malach & Schunn (2013), *Educational Psychologist* (w2-03-01, w2-04-10) | Case comparisons d = 0.50 (57 experiments) | |
| Planted-error "spot the error" Verify task | Fan & Chang (2026) | d = 0.35, with 12 planted errors | Must always be labelled as practice |
| Literacy expansion: rare How AI works checks, new parts, "whose view is missing?" | AILit (2026) competence crosswalk (overnight report 02) | Raises coverage from 8 to about 14 of 19 competences, partly | |

## Product and context

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Don't withhold answers | Our reasoning; Oreopoulos & Low (2026), NBER WP 35620, for context; Bastani et al. (2025), *PNAS* (w2-09-08, w2-09-09) | Refusing an answer doesn't stop a student asking another chatbot. The Khanmigo trial does not show students left when refused: use of the tutor was thin from the start (median student messaged in 17% of mistake sessions), with small gains similar to Khan Academy practice alone. Unrestricted GPT access harmed later unaided performance, while a guarded tutor didn't | Not evidence that refusing answers drives students away (`docs/research/personalisation.md` §4) |
| Question templates | Fu & Choe (2022); item-model literature | Templates can produce comparable items, but many need revision | |
| Context stays small | Anthropic docs on compaction | Long chats are summarised only near the limit; quality degrades as context grows | Product behaviour may change |
| Instructions capped (900 words, at most 950 if cuts can't make room) | Same as above | The instructions sit in context for the whole chat, beside the school's own instructions and every result | Our own budget, not an external limit |

## Our simulations

Each value that comes from one of these is labelled "from our simulation" in `settings.md`, and is to be refitted from real logs.
- **Overnight research, waves 1–6** (`docs/research/overnight/sims/`): settings, decay, literacy scoring, gaming, the patch stack. All synthetic students on the example pack.
- **Fatigue (18 Nov):**
  - the 4-answer rule's false-alarm rate;
  - a time-weighted Bayesian rule;
  - a sequential test using the research decline curve.

  Assumes one answer every 2 minutes and a 10-point drop when tired (the middle of the 5–18% research range).
- **Learning rate (18 Nov):** how much average surprise reveals the true learning rate. BKT prior 0.30, learn rate 0.10, slip 0.10, guess 0.25; true spreads of 10%, 15% and 30%; 48 answers per student.
- **Starting point (18 Nov):** how quickly first answers reveal starting knowledge, using Simpson et al.'s spread of 0.57–0.90 logits.

## Considered and not adopted

- **FSRS scheduling.** It targets a constant level of recall with no exam date. It no longer needs hundreds of reviews per user: the current optimiser uses default parameters below 64 reviews and pulls a full fit towards the defaults (FSRS-7; FSRS-6 also fitted only the initial stabilities from 8 reviews; `docs/research/personalisation.md` §4, finding 8-10). Our model is a simpler version of the same idea (difficulty, half-life, `p_now`). Revisit with real review data.
- **A hard gate that blocks progress.** The chatbot's interface can't enforce it, and students would go round it. Graduated choices are used instead.
- **Ending sessions.** The server can't end them. It offers stopping and protects the learner model instead.
- **`on_success_immediate = 1.0`.** In simulation it left 1.6 of 9 parts secure instead of 6.2, because 59–80% of evidence counts as immediate (w1-06-07 ✓).
- **"Secure only after delayed evidence."** Replaced by the show-then-pick cap (patch 0010b).
- **The 4-answer average fatigue rule.** Mostly noise (w1-06-08 ~; our simulation: 77% false alarms by 60 minutes).
- **A "slow answer" fatigue rule.** Fatigue slows reactions only about 5% even after 3 hours (Boksem et al. 2005).
- **Response-time variability as an attention signal.** Needs dozens of responses a minute (Esterman et al. 2013).
- **A single personal starting boost across all topics.** It would carry success on taught topics over to topics not yet taught (Koedinger et al. 2023). Split by coverage instead.
- **Personal learning rate at k = 20, scale 2.0, bounds 0.5–1.5.** It reads mostly noise at research-sized spreads (Koedinger 2023; Simpson 2024; our simulation).
- **Scoring candidates by how much Synapse's estimate would move.** That favours questions that measure over questions that teach.
- **A learned priorities policy (contextual bandit) now.** There's no data, and learned policies mostly didn't beat sensible rules (Doroudi, Aleven & Brunskill 2019). The options not picked are logged so it can be learned later.
- **Matching format to learning styles.** No good evidence (Pashler et al. 2008).
- **Push reminders.** Synapse runs only when the student messages. Reminders are in-chat at session start; calendar and Teams or Google Classroom links are in `later.md`.
