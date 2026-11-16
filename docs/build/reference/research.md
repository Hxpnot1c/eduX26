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

## Considered and not adopted
- **FSRS scheduling.** It needs many graded reviews per user to fit, and it targets a constant level of recall with no exam date. Our model is a simpler version of the same idea (difficulty, half-life, `p_now`). Revisit only with real review data.
- **A hard gate that blocks progress.** The chatbot's interface can't enforce it, and students would go round it. Graduated choices are used instead.
- **Ending sessions.** The server can't end them. It offers stopping and protects the learner model instead.
