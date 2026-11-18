# Pitch notes: what we can say, what we must not say, and the deck

Wave 1. Every claim below comes from a finding in `findings.csv`, checked by one blind verifier. ✓ = confirmed against the source. ~ = broadly right with a stated problem; we use a ~ finding only when its caveat is built into the wording. Our own measurements are labelled and have not been verifier-checked. Numbers we chose are marked "our choice".

Use the wording as written. If you shorten a line, keep the caveat.

## (a) Claims we can make

### Defining AI literacy
| # | Wording for slide or voiceover | Source | Mark |
|---|---|---|---|
| 1 | "We anchor our definition to the OECD–European Commission AILit Framework, finalised in 2026: four domains, 19 competences." | w1-02-01 (report 02) | ✓ |
| 2 | "AILit itself says AI literacy is not the same as using AI tools. So we don't count chatbot use. We score what students do with it." | w1-02-02 (02) | ✓ |
| 3 | "Our Verify skill follows AILit's progression for judging AI output: from checking against a trusted source, towards deciding to accept, revise or reject it, and saying why." | w1-02-03 (02) | ✓ |
| 4 | "England's Curriculum and Assessment Review says young people should understand how AI works and use it without becoming dependent on it." | w1-02-11 (02) | ✓ |
| 5 | "What we cover is narrow on purpose: asking, checking and knowing why chatbots fail, for study. Ethics, creation and building AI are out of scope." | definition and crosswalk in report 02 | our design |

### Why observe behaviour instead of asking
| # | Wording | Source | Mark |
|---|---|---|---|
| 6 | "Self-rated AI literacy tracks real knowledge poorly. In one study, the correlation was only 0.21." (Spoken caveat if asked: 120 German adults.) | w1-02-25 (02) | ✓ |
| 7 | "In a study of university students, a 20-question AI-literacy test predicted how well they did on an AI-assisted task. A self-report scale did not." | w1-02-23 (02) | ✓ |
| 8 | "Checking sources is hard even for teenagers who grew up online. In a US national sample of 3,446 high-school students, 52% took a misleading video as strong evidence of voter fraud." | w1-02-27 (02) | ✓ (US, not UK) |
| 9 | "Embedded assessments in published game studies reached correlations of about 0.4 with external tests. That's the bar our pilot is designed to test." | w1-02-21, w1-02-22 (02) | ✓ (US school students; convergent validity, not learning) |

### Honest about measurement (these build credibility)
| # | Wording | Source | Mark |
|---|---|---|---|
| 10 | "One moment of evidence is weak. A stable level needs about a dozen moments per skill, so we show the evidence count and call early levels provisional." | w1-02-31 (02) | ✓ (our calculation) |
| 11 | "We don't claim a validated test. We claim a validity argument: fixed scoring rules, the chatbot's labels checked against humans, evidence counts, and a pilot designed to correlate with an external AI-literacy test." | w1-02-33 (02) | ~ framework read from abstracts and secondary sources; the structure is standard, so the wording stands |
| 12 | "Only the how-AI-works answers are scored by our server alone. Ask and Verify rest on the chatbot's labels and on what the student reports." | report 02, "Scoring problems" | our design review |

### Educational value
| # | Wording | Source | Mark |
|---|---|---|---|
| 13 | "Every wrong option is a real misconception. On one classic opportunity-cost question, only about one in five economists and economics PhD students picked the intended answer, and economists still argue about the key. The wrong ideas are common and sticky, which is why we build checks from them." | w1-04-01 (04) | ✓ (the key dispute rests on Potter & Sanders 2012, not separately verified, so the caveat stays in the line) |
| 14 | "In 2022, 36% of UK adults thought a fall in inflation meant prices were falling. That is a distractor we use." | w1-04-07 (04) | ✓ (UK adults, not students) |
| 15 | "Misconceptions survive teaching. On a US college test, one wrong idea about productive capacity fell only from 43% to 32% after a whole principles course." | w1-04-05 (04) | ✓ (US college) |
| 16 | "England's product safety standards for AI learning tools say not to hand over final answers by default, and to track offloading. eduX's default is one point, then a check, and it flags when a student asks to be shown." | w1-09-01 (09) | ✓ (say "follows this default", never "compliant": "just show me" still skips the attempt) |

### Who it helps, how it works in practice
| # | Wording | Source | Mark |
|---|---|---|---|
| 17 | "eduX runs inside the school's chatbot. It never calls an AI model itself, so its running cost is hosting." | architecture (`docs/build/README.md`) | our design |
| 18 | "Built on the open Model Context Protocol. Tested with claude.ai. ChatGPT and Microsoft Copilot Studio document MCP support; we haven't tested them yet." | w1-05-01, w1-05-05, w1-05-11 (05) | ✓ |
| 19 | Caption: "Filmed on an adult team member's account. claude.ai consumer plans are 18+. Students under 18 would use a school-managed chatbot." | w1-05-02 (05) | ✓ |
| 20 | "For schools, the best-documented route is Microsoft Copilot Studio, which supports the per-student key eduX uses. We haven't tested it yet. OAuth is our next build." | w1-05-11 (05) | ✓ |
| 21 | "There were 46,365 A level Economics entries in England in 2026, up 10.7%." | w1-08-01 (business plan) | ✓ (England only) |
| 22 | "73% of secondary teachers think pupils have used generative AI for homework. Only 34% of secondary schools had a policy on safe use of AI." | w1-08-04 (business plan) | ✓ (teachers' perceptions, not measured use) |
| 23 | "A department licence would sit well under the £10,000 level where DfE buying guidance asks for multiple quotes." | w1-08-06 (business plan) | ~ the bands are confirmed; we don't claim anything about frameworks |
| 24 | "Even a 100-school trial could detect only about 0.17 of a standard deviation. So our first pilot measures feasibility, not learning." | w1-08-08 (business plan) | ✓ (our calculation, large-sample multiplier; the small-sample figure of 0.18 is ours and unchecked) |

### Our own measurements (not verifier-checked; label them)
| # | Wording | Source |
|---|---|---|
| 25 | "In our test runs, the server answered each turn in about 14 milliseconds, with no network calls." Caption: "our test run, synthetic students". | `sims/demo-captures/` (demo-plan) |
| 26 | "All 51 automated checks pass." Say which build: `main` without 05e, unless re-run on the merged build. | `sims/demo-captures/check_mcp_output.txt` (demo-plan) |

## (b) Claims to avoid

| Don't say | Why | Say instead |
|---|---|---|
| "Students stopped using Khanmigo when it refused to give answers." | The trial doesn't support it (w1-09-08 ~, abstract only). It is still in the 05e step doc, line 7. | "We give full answers to research questions so students practise checking a real answer. Course questions follow DfE's hint-first default." If you cite the trial: "small gains, about 0.06–0.08 SD per school year, US middle-school maths (abstract)". |
| "Works with Gemini", "works with any chatbot", "school-ready", Gemini or Copilot logos | Gemini custom apps are 18+, US-only, personal accounts; school accounts are excluded (w1-05-09 ✓). ChatGPT and Copilot Studio are untested. `text/format/gemini.md` existing is not support. | Line 18 above. |
| "A validated AI-literacy assessment" or "validated test" | No agreement study, no pilot, no external correlation yet (report 02). | Line 11 above. |
| "Stealth assessment" | Ask and Verify are overt tasks, and the how-AI-works check is an open question. Nothing is hidden. | "Embedded assessment: scored from moments in normal study." "Unobtrusive" fits only the scoring of the questions students already ask. |
| "eduX improves learning" or "raises grades", or any learning gain | We have measured none. Simulations use synthetic students and are not evidence about learning. | "We haven't measured learning yet. Here's the pilot design, and why it measures feasibility first." |
| "Economists don't understand opportunity cost" (Ferraro & Taylor as settled) | Potter & Sanders (2012) dispute the key. About a third of the sample were PhD students (w1-04-01 ✓). | Line 13 above, with the caveat. |
| "The chatbot's labels are reliable", or "GPT-4 marks as well as a human (κ = .70)" | LLM agreement varies widely by task (QWK .30 to .87; w1-02-29 ~). The κ .70 figure is abstract-only (w1-02-28 ~). A meta-analysis found decoder models agree less (w1-02-30 ~). None of this is our chatbot on our labels. | "The chatbot labels the behaviour. We check its labels against two humans and report agreement per feature." |
| "A 'secure' Verify means the student checked" | In simulation, one unprompted "I checked" makes Verify secure (p = 0.82). With 15% label noise, 11–16% of students without the skill end "secure" (w1-02-32 ✓; simulation, synthetic students). | "Verify rests partly on what students report. How AI works is scored by our server alone." End the demo on How AI works. |
| "DfE compliant" | eduX partly meets the standards. There are gaps in safeguarding alerts, data rights and security (report 09). | "We mapped every DfE standard, named an owner for each and ranked our fixes." |
| "A 16-year-old can use this today", or showing a minor on claude.ai | claude.ai consumer is 18+ (w1-05-02 ✓). No tested under-18 route exists. | Lines 19–20 above. |
| "Our students reach AILit Advanced" | AILit levels aren't tied to age (w1-02-01 ✓). Verify reaches Intermediate at best until the justification tick exists. | "Our levels are skill levels for this course, mapped to AILit's progressions." |
| "Threshold concepts are proven to matter" | It is a theory label. The one quantitative test found little change over a semester (w1-04-03 ✓, w1-04-04 ~). | "Opportunity cost is the best-evidenced hard idea." |
| "Friction won EduX Oceania" (or naming it) | Only search snippets; it isn't in the official gallery (w1-01-08 ~). | Don't name it. |
| "The EU AI Act requires pupils' AI literacy" | Article 4 concerns staff of providers and deployers (w1-02-14 ~). | Business plan only, as a possible buyer of assessment. |
| Revenue scenarios as a forecast | They are a ceiling on our own estimates and our £8 price (our choice). | "Even at full uptake, one subject is a small business. Growth means more subjects." |
| "Three students, three plans" | The captures show two plans; the third student differs only in history (demo-plan). | "Same question, two students, two plans." |
| "The chatbot invented that link" (unless it did on camera) | The link report in the storyboard is scripted. | Caption: "Scripted demo: the student reports a dead link." |

## (c) Deck outline: 4 minutes, 8 slides

**Criteria.** The rules page publishes one explicit criterion: how well the solution addresses the chosen problem (w1-01-02 ✓). It also asks teams to show who the idea helps and how it could work in practice, and to explain its educational value (w1-01-03 ✓). There are no weights. Tags: **P** = problem fit (assessing), **D** = defining (from the challenge title; re-check once the brief is pasted), **W** = who it helps, **H** = how it works in practice, **E** = educational value. One idea per slide and few words on each (w1-07-08 ~, a practitioner opinion).

| # | Time | Slide | On screen (few words) | Spoken (key line) | Criteria | Claims used |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:20 | **The problem** | A chatbot answer with a confident source link | "Sixth-formers already ask chatbots for facts. Whether they can tell when it's wrong is invisible to everyone, including them." | P | 4, 8 |
| 2 | 0:20–0:50 | **What we mean by AI literacy** | The one-sentence definition (report 02); AILit anchors; "out of scope" line | Definition, then: "AI literacy isn't tool use, so we don't count use." | D | 1, 2, 3, 5 |
| 3 | 0:50–1:20 | **How we assess it** | 3 skills × 3 levels, each an observable behaviour; "scored from normal study" | "Ask, Verify, How AI works. Each is a thing students do, scored when it happens." | P, D | 6, 7, 12 |
| 4 | 1:20–2:00 | **See it work** | Four stills or a 20-second clip: vague question → Verify task → bad link → how-AI-works check → the record | "The moment the chatbot fails is the moment to learn why. Each wrong option is a real misconception." | P, E | 12, 19 |
| 5 | 2:00–2:30 | **Why it teaches** | One check; misconception distractors; one point at a time | "Every wrong option comes from evidence. Our default is one point, then a check, as DfE's standards ask." | E | 13 or 14, 16 |
| 6 | 2:30–3:00 | **How far to trust our scores** | Validity argument: what we have / what we'd gather; evidence counts; κ = __ if the Wednesday study runs | "We don't claim a validated test. Here's our validity argument and the pilot that tests it." | P, E | 9, 10, 11 |
| 7 | 3:00–3:30 | **Who it helps, how it runs** | Architecture (school chatbot → eduX → plan); the works-with line; teacher-view mock labelled "mock-up"; under-18 route | "No AI model calls. Tested with claude.ai. For under-18s, a school-managed chatbot; Copilot Studio first." | W, H | 17, 18, 20, 22 |
| 8 | 3:30–4:00 | **Next** | Merge, OAuth, Copilot Studio test, a feasibility pilot; one market line; team roles | "First a feasibility pilot, not a learning claim. Here's who does what." | H | 21, 24 |

Keep the safety points (wellbeing signpost, no training on pupil data, key revocation) for Q&A, unless the build team lands them on Wednesday.
