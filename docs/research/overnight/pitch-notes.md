# Pitch notes: what we can say, what we must not say, and the deck

Waves 1 and 2. Every claim below comes from a finding in `findings.csv`, checked by one blind verifier. ✓ = confirmed against the source. ~ = broadly right with a stated problem; we use a ~ finding only when its caveat is built into the wording. Our own measurements are labelled and have not been verifier-checked. Numbers we chose are marked "our choice". Simulation results are labelled "simulation: synthetic students".

Use the wording as written. If you shorten a line, keep the caveat.

**What changed in wave 2.**
- **New positioning.** Lead with AI-literacy evidence from real use. Gemini now tracks progress across sessions and gives teachers insights (w2-08-01 ✓, w2-08-02 ✓). So the old moat line, "hosts shape one conversation; eduX keeps a learner model across sessions", is gone. What we offer instead is a learner model the school owns, across chatbots: a head start, not a moat.
- **New claims.** Lines 27–42 are new.
- **Rewritten claims.** Lines 17, 18 and 20 are rewritten.
- **New things to avoid.** Section (b) has 14 new rows, marked (w2).

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
| 17 | **Rewritten.** "eduX never calls an AI model itself, so our own running cost is hosting. The school still pays its chatbot provider. On Microsoft Copilot Studio that means Copilot Credits per turn, and we're confirming the amount with Microsoft." | architecture; w2-05-06 (05, business plan) | ~ the credit rates are confirmed; the US$0.01-per-credit price and the billing unit for an MCP call are not. Never quote the US$84 estimate as fact |
| 18 | **Rewritten.** "Built on the open Model Context Protocol. Tested with claude.ai on an adult account. Microsoft Copilot Studio documents MCP support; we haven't tested it yet." | w1-05-01, w2-05-03 (05) | ✓ |
| 19 | Caption: "Filmed on an adult team member's account. claude.ai consumer plans are 18+. Students under 18 would use a school-managed chatbot." | w1-05-02 (05) | ✓ |
| 20 | **Rewritten.** "For pupils, the documented route is Microsoft 365 Education. In K-12 tenants, Copilot Chat is off by default for 13–17s. The school switches it on and adds eduX through Copilot Studio. It's documented, and testing it is our next step." | w2-05-03, w2-05-04 (05) | ✓ (say "documented route, pilot next", never "works today") |
| 21 | "There were 46,365 A level Economics entries in England in 2026, up 10.7%." | w1-08-01 (business plan) | ✓ (England only) |
| 22 | "73% of secondary teachers think pupils have used generative AI for homework. Only 34% of secondary schools had a policy on safe use of AI." | w1-08-04 (business plan) | ✓ (teachers' perceptions, not measured use) |
| 23 | "A department licence would sit well under the £10,000 level where DfE buying guidance asks for multiple quotes." | w1-08-06 (business plan) | ~ the bands are confirmed; we don't claim anything about frameworks |
| 24 | "Even a 100-school trial could detect only about 0.17 of a standard deviation. So our first pilot measures feasibility, not learning." | w1-08-08 (business plan) | ✓ (our calculation, large-sample multiplier; the small-sample figure of 0.18 is ours and unchecked) |

### Our own measurements (not verifier-checked; label them)
| # | Wording | Source |
|---|---|---|
| 25 | "In our test runs, the server answered each turn in about 14 milliseconds, with no network calls." Caption: "our test run, synthetic students". | `sims/demo-captures/` (demo-plan) |
| 26 | "All 51 automated checks pass." Say which build: `main` without 05e, unless re-run on the merged build. | `sims/demo-captures/check_mcp_output.txt` (demo-plan) |

### New in wave 2: the problem, measured on real teenagers
Lead with performance evidence, then the usage figures with their bases (researcher w2 #3).

| # | Wording | Source | Mark |
|---|---|---|---|
| 27 | "Ofcom, 2026: about half of UK teenagers felt confident spotting AI-generated content. A quarter of those confident teenagers then failed Ofcom's test." | w2-09-04 (09) | ✓ (52% confident; 25% *of the confident* failed. It was an image-identification test, not checking chatbot answers: say "spotting AI content") |
| 28 | "In the National Literacy Trust's 2025 survey, 70.6% of 16–18s had used generative AI. Of those users, about half (52.0%) use it weekly or more." | w2-09-01 (02) | ~ the 52.0% is a share of 16–18 AI users, not of all 16–18s. Opt-in schools, about 4,900 aged 16–18 |
| 29 | "Among 16–18s who use it monthly, the commonest uses are homework help (70.4%) and asking questions (69.7%); 45.5% use it to summarise texts." | w2-09-01 (02) | ~ base: monthly users aged 16–18 |
| 30 | Only as a set-up for line 6: "58.5% of 16–18s who had heard of generative AI say they check what it tells them. That's self-report, which is why we watch what students do." | w2-09-02 (02) | ✓ (base: those who had heard of generative AI; self-report, no behavioural check) |

### New in wave 2: chatbots and sources
| # | Wording | Source | Mark |
|---|---|---|---|
| 31 | "With no web search, chatbots invent references. In 2023, 55% of GPT-3.5's and 18% of GPT-4's citations in written literature reviews didn't exist." | w2-02-30 (02) | ✓ (2023 models; academic references) |
| 32 | "With search on, the failure changes. GPT-4o with web search invented no links, but about 30% of its statements weren't backed by the pages it cited." | w2-02-34 (02) | ✓ (800 medical questions; model behaviour, not students) |
| 33 | "So we teach one thing that is true either way: a cited source may not exist, or may not say what was claimed. Check it." | 02 "How AI works content"; w2-02-30, w2-02-34 | our design, on ✓ findings |
| 34 | "Published medical papers misquote their sources about one time in four too. So eduX teaches checking, not distrust of AI." | w2-02-44 (02) | ✓ (25.4% of quotations; meta-analysis of 28 studies. Don't imply chatbots are as good as humans: the tasks differ) |
| 35 | "When a student pushes back and the chatbot changes its answer, that isn't proof either way. In one benchmark, rebuttals moved models to a correct answer 44% of the time and to a wrong one 15% of the time." | w2-02-38 (02) | ✓ (SycEval; rates differ a lot across models: never quote one rate for "chatbots") |

### New in wave 2: offloading, exam fit and our own tests
| # | Wording | Source | Mark |
|---|---|---|---|
| 36 | "In a randomised trial with about 1,000 Turkish high-school students, unrestricted GPT-4 raised practice scores 48% but cut unassisted exam scores 17%. A guarded tutor version avoided the harm." | w2-09-08 (09) | ✓. **Limits, say if asked:** maths, four sessions, 2023, randomised by class. The guarded tutor gave *no* exam gain. Use it only for "guarded beats unguarded", never for "AI tutors improve learning" |
| 37 | "About two-thirds of A level Economics marks are level-marked. Multiple choice is about 3.5%. Our multiple-choice checks are the diagnostic way in, not exam practice for the levelled two-thirds." | w2-04-02 (04) | ✓ (our tally of the June 2025 Edexcel 9EC0 mark schemes: about 34% point-marked, 66% level-marked) |
| 38 | "We set difficulty for learning, not for time on the app. In two large online experiments, the easiest version of a maths game kept players longest and taught slowest." | w2-03-12 (03) | ~ abstract only; about 10,000 and 70,000 players; engagement and learning moved in opposite directions |
| 39 | "We tested our own AI-literacy scoring on our real code. Simulation: with the settings we propose, a synthetic student with no skill is shown 'secure' at a weekly read in under 1% of cases. Even in the chat, at most 3% ever see it, with up to 20% of the chatbot's labels wrong at random." | w2-02-01, w2-02-02, w2-02-08 (02) | ✓ (simulation: synthetic students, example pack; the settings are proposed, not yet set; 4–7% if the chatbot labels leniently) |
| 40 | Chart caption: "eduX tested its own alarms. With evidence-based settings, 'secure but not known on exam day' fell from 76% to 55%, and parts truly secure rose from 3.9 to 4.7 of 9." | w1-06-04, w1-06-05 (06) | ✓ (simulation: synthetic students, 9-part example pack, far scenario; not a learning result; always show both panels) |

### New in wave 2: competitors, stated fairly
| # | Wording | Source | Mark |
|---|---|---|---|
| 41 | "Gemini now tracks progress: study notebooks since June 2026, and teacher insights in Google Classroom since November. For Google schools, that's free. We don't sell to Google schools. eduX gives a school evidence of how pupils ask and check, from real chatbot use, and a learner model the school owns across chatbots. That's a head start, not a moat, and it isn't validated yet." | w2-08-01, w2-08-02 (business plan) | ✓ (Gemini notebooks for under-18 school accounts were promised "in the coming weeks"; rollout not confirmed) |
| 42 | "OpenAI added in-chat quizzes to ChatGPT in September. We found no public evidence of progress tracking. Anthropic's Claude for Teachers is US-only and already connects to tools like Eedi." | w2-08-03, w2-08-04, w2-08-05 (business plan) | ✓ (absence after search, not proof: never say "ChatGPT can't") |

## (b) Claims to avoid

| Don't say | Why | Say instead |
|---|---|---|
| **(w2)** "Hosts shape one conversation; eduX keeps a learner model across sessions", "our learner model is the moat", "only eduX tracks progress" | Gemini tracks progress across sessions and reports to teachers (w2-08-01 ✓, w2-08-02 ✓). BKT and misconception distractors aren't proprietary. | Line 41: "a head start, not a moat". |
| **(w2)** "A compliance product for AI Act Article 4", "deployers will license our instrument" | The Commission says Article 4 does not require measuring staff's AI knowledge and needs no certificate (w2-08-09 ✓). Article 4 covers staff, not pupils. | Nothing in the pitch. In Q&A: "AI-literacy evidence is for the school's teaching, not for compliance." |
| **(w2)** Wang & Fan (2025), "ChatGPT has a large effect on learning (g = 0.87)" | Retracted on 22 April 2026 (w2-09-13 ✓). | Line 36, with its limits. |
| **(w2)** MIT's "Your brain on ChatGPT", "AI rots your brain", "makes students dumber" | Unreviewed arXiv preprint; 54 participants, 18 in session 4. Its authors reject the "dumber" reading (w2-09-11 ✓). | Line 36. |
| **(w2)** Gerlich (2025) as proof that AI use causes weaker critical thinking | A correlational survey-and-interview study, since corrected (w2-09-12 ~). | Line 36, or nothing. |
| **(w2)** "52% of 16–18s use AI weekly" | 52.0% is a share of 16–18 *AI users*, not of all 16–18s (w2-09-01 ~). | Line 28, with the base. |
| **(w2)** "58.5% of teens check AI answers" as evidence of behaviour | Self-report, and the base is those who had heard of generative AI (w2-09-02 ✓). The deck says self-report is weak, so this would contradict it. | Line 30, only as the set-up for line 6. |
| **(w2)** "Running eduX costs schools nothing", "zero running cost", "cheaper than a chatbot" on Copilot | On Copilot Studio the school pays Copilot Credits per turn. Our rough estimate is up to about US$84 per student per year, and it rests on an unverified rate (w2-05-06 ~). | Line 17. |
| **(w2)** Le Chat (Mistral) as a route for pupils or schools, or a Le Chat logo | Consumer terms for personal use, with parental permission for minors and no school contract (w2-05-01 ~). It can't go in a school DPIA (DPO w2 #1). | "Adults only," if asked. Line 20 for pupils. |
| **(w2)** "AI tutors improve learning" (citing Bastani) | The guarded tutor in Bastani et al. avoided harm but gave no exam gain (w2-09-08 ✓). | Line 36: "guarded beats unguarded". |
| **(w2)** "It searched a database and picked the wrong entry" taught as a misconception, on screen or in the deck | With search on, it is often the true account: about a quarter to a third of citations or statements aren't backed by the page cited (w2-02-33 ~, w2-02-34 ✓). | Line 33. |
| **(w2)** "A How AI works level", "secure in How AI works" | In simulation, the rolled-up level ranks no-skill students above strong ones (AUC 0.40–0.44; w2-02-05 ~). | "Per-part results: checked n, right m, and the wrong ideas still held." |
| **(w2)** "Pooling across sets catches 8–9 misconceptions in 10" | Our pooling calculation wasn't saved to the repo and no verifier has rerun it ([05](05-product-features.md)). | "In one set of 12, it catches a misconception held by about half the class, not one held by a third" (w2-05-29 ✓, simulation). |
| **(w2)** Self-label rates as "how often the chatbot is wrong" or "how often it caves" | `conflict_flagged` under-fires on confident errors, and `pushback_changed` also fires on corrections (w2-02-38 ✓, w2-02-41 ✓). | "The chatbot labels the moment. We're auditing its labels against scripts." |
| "Students stopped using Khanmigo when it refused to give answers." | The trial doesn't support it (w1-09-08 ~, abstract only). It is still in the 05e step doc, line 7. | "We give full answers to research questions so students practise checking a real answer. Course questions follow DfE's hint-first default." If you cite the trial: "small gains, about 0.06–0.08 SD per school year, US middle-school maths (abstract)". |
| "Works with Gemini", "works with any chatbot", "school-ready", Gemini or Copilot logos | Gemini custom apps are 18+, US-only and personal accounts; school accounts are excluded (w1-05-09 ✓). Copilot Studio is untested. `text/format/gemini.md` existing is not support. | Line 18. |
| "A validated AI-literacy assessment" or "validated test" | No agreement study, no pilot, no external correlation yet (report 02). | Line 11. |
| "Stealth assessment" | Ask and Verify are overt tasks, and the how-AI-works check is an open question. Nothing is hidden. | "Embedded assessment: scored from moments in normal study." "Unobtrusive" fits only the scoring of the questions students already ask. |
| "eduX improves learning" or "raises grades", or any learning gain | We have measured none. Simulations use synthetic students and are not evidence about learning. | "We haven't measured learning yet. Here's the pilot design, and why it measures feasibility first." |
| "Economists don't understand opportunity cost" (Ferraro & Taylor as settled) | Potter & Sanders (2012) dispute the key. About a third of the sample were PhD students (w1-04-01 ✓). | Line 13, with the caveat. |
| "The chatbot's labels are reliable", or "GPT-4 marks as well as a human (κ = .70)" | LLM agreement varies widely by task (QWK .30 to .87; w1-02-29 ~). The κ .70 figure is abstract-only (w1-02-28 ~). A meta-analysis found decoder models agree less (w1-02-30 ~). None of this is our chatbot on our labels. Without outside feedback, self-correction made GPT-3.5 worse on one benchmark (w2-02-41 ✓). | "The chatbot labels the behaviour. We check its labels against two humans and report agreement per feature." |
| "A 'secure' Verify means the student checked" | Verify rests partly on what students report. A student who restates the reply scores a correct Verify moment about as often as a partial checker (49% vs 44%; w2-02-04 ~, simulation). | "Verify rests partly on what students report. How AI works is scored by our server alone." End the demo on How AI works. |
| "DfE compliant" | eduX partly meets the standards. There are gaps in safeguarding alerts, data rights and security (report 09). | "We mapped every DfE standard, named an owner for each and ranked our fixes." |
| "A 16-year-old can use this today", or showing a minor on claude.ai | claude.ai consumer is 18+ (w1-05-02 ✓). No tested under-18 route exists. | Lines 19–20. |
| "Our students reach AILit Advanced" | AILit levels aren't tied to age (w1-02-01 ✓). Verify reaches Intermediate at best until the justification tick exists. | "Our levels are skill levels for this course, mapped to AILit's progressions." |
| "Threshold concepts are proven to matter" | It is a theory label. The one quantitative test found little change over a semester (w1-04-03 ✓, w1-04-04 ~). | "Opportunity cost is the best-evidenced hard idea." |
| "Friction won EduX Oceania" (or naming it) | Only search snippets; it isn't in the official gallery (w1-01-08 ~). | Don't name it. |
| "The EU AI Act requires pupils' AI literacy" | Article 4 concerns staff of providers and deployers (w1-02-14 ~). It requires no measurement or certificate (w2-08-09 ✓). | Nothing. |
| Revenue scenarios as a forecast | They are a ceiling on our own estimates and our price (our choice: £5 per student, trust tier £3). | "Even at full uptake, one subject is a small business. Growth means more subjects." |
| "Three students, three plans" | The captures show two plans; the third student differs only in history (demo-plan). | "Same question, two students, two plans." |
| "The chatbot invented that link" (unless it did on camera) | The source report in the storyboard is scripted. | Caption: "Scripted demo: the student reports a mismatched source." |

## (c) Deck outline: 4 minutes, 8 slides

**Criteria.** The rules page publishes one explicit criterion: how well the solution addresses the chosen problem (w1-01-02 ✓). It also asks teams to show who the idea helps and how it could work in practice, and to explain its educational value (w1-01-03 ✓). There are no weights. Tags: **P** = problem fit (assessing), **D** = defining (from the challenge title; re-check once the brief is pasted), **W** = who it helps, **H** = how it works in practice, **E** = educational value. One idea per slide and few words on each (w1-07-08 ~, a practitioner opinion).

**Positioning (wave 2).** The deck leads with AI-literacy evidence from real use: performance before self-report, and behaviour scored in normal study. The school-owned learner model, which works across chatbots, comes in as a head start on slide 7, not as a moat. Gemini gets a fair mention there.

| # | Time | Slide | On screen (few words) | Spoken (key line) | Criteria | Claims used |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:25 | **The problem, measured** | "Confident ≠ correct" with Ofcom's figure; NLT usage with its base | "Half of teenagers feel confident spotting AI content, and a quarter of those fail the test. Seven in ten 16–18s have used these tools. Nobody sees whether they check." | P | 27, 28, 8 |
| 2 | 0:25–0:50 | **What we mean by AI literacy** | The one-sentence definition (report 02); AILit anchors; the "out of scope" line | Definition, then: "AI literacy isn't tool use, so we don't count use." | D | 1, 2, 3, 5 |
| 3 | 0:50–1:20 | **Assessed from real use** | 3 skills, each an observable behaviour; Ask and Verify levels with evidence counts; How AI works as per-part results; "embedded, not a quiz" | "Self-ratings barely track skill, and even 58.5% 'I check' is self-report. So we score what students do, when it happens." | P, D | 6, 7, 12, 30 |
| 4 | 1:20–1:55 | **See it work** | Four stills or a 20-s clip: vague question → Verify task → a source that doesn't say it → how-AI-works check → the record. Caption: "web search off" | "Search off, chatbots invent sources. Search on, they cite real pages that don't say it. We teach what's true either way: check the source says it." | P, E | 31–34, 19 |
| 5 | 1:55–2:20 | **How far to trust our scores** | Validity argument: what we have / what we'd gather; κ = __ if the Wednesday study runs; the two-panel chart "eduX tested its own alarms" | "We don't claim a validated test. We tested our scoring on our own code, with synthetic students, and here's the pilot that tests it on real ones." | P, E | 9, 10, 11, 39, 40 |
| 6 | 2:20–2:45 | **Why it teaches** | One check with misconception distractors; "two-thirds of marks are levelled"; "guarded beats unguarded" | "Every wrong option comes from evidence. Our checks are the diagnostic way in. And the best trial says a guarded tutor avoids the harm an unguarded one does." | E | 13 or 14, 16, 36, 37 |
| 7 | 2:45–3:25 | **Who it helps, how it runs, why not Gemini** | School chatbot → eduX → plan; "documented route: Microsoft 365 Education, pilot next"; teacher-view mock (class patterns, groups ≥ 6, AI literacy in bands, opt-in; labelled "mock-up"); "a head start, not a moat" | "No AI model calls on our side. Gemini tracks progress inside Google. We give the school its own evidence of how pupils ask and check, across chatbots." | W, H | 17, 18, 20, 41, 42 |
| 8 | 3:25–4:00 | **Next** | Merge, sign-in, a Copilot Studio test, a feasibility pilot; £5 per student per year (our choice); team roles | "First a feasibility pilot, not a learning claim. Here's who does what." | H | 21, 24 |

Keep these for Q&A unless the build team lands them on Wednesday: the safety points (wellbeing signpost, no training on pupil data, key revocation), the Copilot cost estimate, and the Bastani limits.
