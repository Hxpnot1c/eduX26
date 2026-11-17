# Research

The evidence behind teaching and modelling decisions. Effect sizes are as reported by each source. Settings based on them are starting points, to be tuned against real data.

| Decision | Source | What it shows | Caveat |
|---|---|---|---|
| Pre-questions | St. Hilaire, Chan & Ahn (2024), *Psychonomic Bulletin & Review*, meta-analysis | g = 0.54 on the asked material; multiple choice ≈ short answer; guessing 0.65 vs reading 0.22 | Near-zero benefit on material not asked about (0.04) |
| Pre-questions, wider benefit of multiple choice | Little & Bjork (2016), *Memory & Cognition* | Multiple-choice pretests helped related information more than cued recall | Not supported overall by the meta-analysis |
| Pre-questions in classrooms | Soderstrom & Bjork (2023); Geller et al. (2017) | One classroom benefit; one null result in STEM | Mixed classroom evidence |
| Correct the chosen option | Roediger & Marsh (2005); Butler & Roediger (2008) | Multiple-choice wrong options can be learned; feedback reduces this | |
| Explain-back | Bisra et al. (2018), *Educational Psychology Review* | Self-explanation prompts g = 0.55 (64 reports) | Mostly undergraduates |
| Re-teach only the gap | Wisniewski, Zierer & Hattie (2020), *Frontiers in Psychology* | Feedback d = 0.48; effect depends on how much information it carries | |
| Completion problems for procedures only | Barbieri et al. (2023); Zamary & Rawson (2018) | Worked examples help maths; faded examples no better for declarative concepts | |
| Reviews in a new context | Pan & Rickard (2018), *Psychological Bulletin* | Transfer d = 0.40; strongest to application and inference | Needs explanatory feedback and some initial success |
| Higher-order questions from developing | Agarwal (2019), *Journal of Educational Psychology* | Higher-order and mixed quizzes beat fact quizzes for higher-order learning | |
| Levels plus next step | Koenka et al. (2021), *Educational Psychology*; Koenka (2020) | Comments beat grades alone; grades plus comments best for motivation | |
| Fatigue within a session | Randles, Harlow & Inzlicht (2017), *PLOS ONE* | Fatigue within an hour on task; negligible time-of-day effect | Online self-testing, not school chatbots |
| Stuck vs tired | Beck & Gong (2013), AIED | Wheel-spinning: repeated failure to master a skill | Definitions vary across studies |
| Spacing anchored to the exam | Cepeda et al. (2008) | The best gap shrinks as the test gets closer | |
| One point per message | Rey et al. (2019), *Educational Psychology Review*, meta-analysis | Meaningful, learner-paced segments improve retention and transfer, and reduce load | Mostly multimedia, not chat |
| Check after each point | Chan, Meissner & Davis (2018), *Psychological Bulletin*, meta-analysis | Testing earlier material improves learning of the next material | |
| Not too often | Davis, Chan & Wilford (2017) | Frequent switching between retrieval and study can impair new learning | |
| Move on once a point is learned, with a skip | Kulik, Kulik & Bangert-Drowns (1990), *Review of Educational Research* | Mastery programmes: about 0.5 SD, larger for weaker students | Can lower completion; estimates vary widely across syntheses |
| Checking sources | Wineburg et al. (2022), *Journal of Educational Psychology* | Six lessons in lateral reading improved high-school students' judgement of online sources (randomised) | About websites, not AI output |
| Assess AI literacy inside normal work | Shute (2011); Rahimi & Shute (2023), *ETR&D* | Stealth assessment embeds evidence collection in the learning activity and supports the skill as well as measuring it | Evidence mostly from games and simulations |
| Competency, evidence and task models | Mislevy, Steinberg & Almond (2003) | Evidence-centred design links what's measured, what counts as evidence and where it comes from | |
| Behaviour, not self-report | Lintner (2024), *npj Science of Learning* | 3 performance-based vs 13 self-report AI-literacy scales | |
| Performance predicts better | Jin et al. (2025), GLAT, *Computers and Education: AI* | A performance test predicted AI-assisted task performance better than self-report | A separate test, university students |
| How-AI-works checks | Ng et al. (2021); AILit (2026) | "Know and understand AI" / "Shape AI" are core aspects of AI literacy | |
| Don't withhold answers | Our reasoning; Oreopoulos & Low (2026), NBER WP 35620, for context | Refusing an answer doesn't stop a student asking another chatbot. The Khanmigo trial does not show students left when refused: use of the tutor was thin from the start (median student messaged in 17% of mistake sessions), with small gains similar to Khan Academy practice alone | Not evidence that refusing answers drives students away (`docs/research/personalisation.md` §4) |
| Question templates | Fu & Choe (2022); item-model literature | Templates can produce comparable items, but many need revision | |
| Context stays small | Anthropic docs on compaction | Long chats are summarised only near the limit; quality degrades as context grows | Product behaviour may change |

## Considered and not adopted
- **FSRS scheduling.** It targets a constant level of recall with no exam date. It no longer needs hundreds of reviews per user: the current optimiser uses default parameters below 64 reviews and pulls a full fit towards the defaults (FSRS-7; FSRS-6 also fitted only the initial stabilities from 8 reviews; `docs/research/personalisation.md` §4, finding 8-10). Our model is a simpler version of the same idea (difficulty, half-life, `p_now`). Revisit with real review data.
- **A hard gate that blocks progress.** The chatbot's interface can't enforce it, and students would go round it. Graduated choices are used instead.
- **Ending sessions.** The server can't end them. It offers stopping and protects the learner model instead.
