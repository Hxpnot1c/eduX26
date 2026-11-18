# Pitch notes: what we can say, what we must not say, and the deck

Waves 1, 2 and 3. Every claim below comes from a finding in `findings.csv`, checked by one blind verifier. ✓ = confirmed against the source. ~ = broadly right with a stated problem; we use a ~ finding only when its caveat is built into the wording. Our own measurements are labelled and have not been verifier-checked. Numbers we chose are marked "our choice". Simulation results are labelled "simulation: synthetic students".

Use the wording as written. If you shorten a line, keep the caveat.

**What changed in wave 5.**
- **Five new avoid rows, marked (w5):** "gaming-proof", "the checks can't be gamed by form", "cheaper than Sparx on Microsoft", "label agreement shown" before the real study, and "we show skipped tasks".
- **Two lines that are true only with a patch in** (both recommended, verification pending): "A reported dead link counts as checking, but secure needs a real check" needs 0009b. "Picking an option straight after being shown never makes a part secure; secure needs an answer in your own words or a later check" needs 0010b. Check the build before you say either ([wednesday-build-list](wednesday-build-list.md) steps 5d–5e).
- **New Q&A 11: "Microsoft takes 4.5× your revenue",** with the honest answer (§d).
- **After the competition:** [roadmap.md](roadmap.md) §5 has a one-slide version (≤ 80 words) and §6 five Q&A answers ("What happens after the competition?", "Can a 16-year-old use it?", "Will you show it improves grades?", "How will you know the scores mean anything?", "Who pays?"). Everything there is "our plan".

**What changed in wave 2.**
- **New positioning.** Lead with AI-literacy evidence from real use. Gemini now tracks progress across sessions and gives teachers insights (w2-08-01 ✓, w2-08-02 ✓). So the old moat line, "hosts shape one conversation; eduX keeps a learner model across sessions", is gone. What we offer instead is a learner model the school owns, across chatbots: a head start, not a moat.
- **New claims.** Lines 27–42 are new.
- **Rewritten claims.** Lines 17, 18 and 20 are rewritten.
- **New things to avoid.** Section (b) has 14 new rows, marked (w2).

**What changed in wave 3.**
- **New problem statement (frame D).** "Teenagers feel confident with AI, but confidence doesn't show whose AI literacy is real, and nobody can see the difference." Slide 1 now leads with a performance result. Reasons and alternatives: [01](01-competition-fit.md).
- **Revised deck.** §(c) is replaced by an 8-slide outline with one sentence and one ✓ number per slide (from `work/w3/w3-01.md`, with fixes below).
- **New §(d): the 10 likeliest expo questions,** with 30-second answers. Each gives the caveat first, then what it enables.
- **Lines rewritten:** 13 ("every wrong option" is not true: when a part has one misconception, the chatbot writes the third option) and the "labels are reliable" avoid row (agreement is now reported pooled per skill, not per feature).
- **Section (b) has new rows, marked (w3).**

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
| 13 | **Rewritten (w3).** "Our wrong options come from real misconceptions. On one classic opportunity-cost question, only about one in five economists and economics PhD students picked the intended answer, and economists still argue about the key. The wrong ideas are common and sticky, which is why we build checks from them." | w1-04-01 (04) | ✓ (the key dispute rests on Potter & Sanders 2012, not separately verified, so the caveat stays in the line) |
| 14 | "In 2022, 36% of UK adults thought a fall in inflation meant prices were falling. That is a distractor we use." | w1-04-07 (04) | ✓ (UK adults, not students) |
| 15 | "Misconceptions survive teaching. On a US college test, one wrong idea about productive capacity fell only from 43% to 32% after a whole principles course." | w1-04-05 (04) | ✓ (US college) |
| 16 | "England's product safety standards for AI learning tools say not to hand over final answers by default, and to track offloading. eduX's default is one point, then a check, and it flags when a student asks to be shown." | w1-09-01 (09) | ✓ (say "follows this default", never "compliant": "just show me" still skips the attempt) |

### Who it helps, how it works in practice
| # | Wording | Source | Mark |
|---|---|---|---|
| 17 | **Rewritten.** "eduX never calls an AI model itself, so our own running cost is hosting. The school still pays its chatbot provider. On Microsoft Copilot Studio that means Copilot Credits per turn, and we're confirming the amount with Microsoft." | architecture; w2-05-06 (05, business plan) | ~ the credit rates are confirmed. Wave 3 confirmed US$0.01 (£0.0075) per credit and 5 credits per tool call (w3-08m-06 ✓, -07 ✓). Never quote the old US$84 estimate; if pressed, use the (w3) cost row |
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
| 39 | "We tested our own AI-literacy scoring on our real code. Simulation: with the settings we propose, a synthetic student with no skill is shown 'secure' at a weekly read in under 1% of cases. Even in the chat, 5% or fewer ever see it, with up to 20% of the chatbot's labels wrong at random." | w2-02-01, w2-02-02, w2-02-08 (02) | ✓ (simulation: synthetic students, example pack; the settings are proposed, not yet set; 4–7% if the chatbot labels leniently) |
| 40 | Chart caption: "eduX tested its own alarms. With evidence-based settings, 'secure but not known on exam day' fell from 76% to 55%, and parts truly secure rose from 3.9 to 4.7 of 9." | w1-06-04, w1-06-05 (06) | ✓ (simulation: synthetic students, 9-part example pack, far scenario; not a learning result; always show both panels) |

### New in wave 2: competitors, stated fairly
| # | Wording | Source | Mark |
|---|---|---|---|
| 41 | "Gemini now tracks progress: study notebooks since June 2026, and teacher insights in Google Classroom since November. For Google schools, that's free. We don't sell to Google schools. eduX gives a school evidence of how pupils ask and check, from real chatbot use, and a learner model the school owns across chatbots. That's a head start, not a moat, and it isn't validated yet." | w2-08-01, w2-08-02 (business plan) | ✓ (Gemini notebooks for under-18 school accounts were promised "in the coming weeks"; rollout not confirmed) |
| 42 | "OpenAI added in-chat quizzes to ChatGPT in September. We found no public evidence of progress tracking. Anthropic's Claude for Teachers is US-only and already connects to tools like Eedi." | w2-08-03, w2-08-04, w2-08-05 (business plan) | ✓ (absence after search, not proof: never say "ChatGPT can't") |

## (b) Claims to avoid

| Don't say | Why | Say instead |
|---|---|---|
| **(w5)** "Gaming-proof", "you can't game it", "cheap tricks don't work" | In simulation, every cheap deviation we tried except vague questions out-earned honest work in level per minute (w5-06g-01 ~). Even with the wave-6 counters (0009b, 0010b), guessers still gain "developing", a student who has done one real check can then report dead links freely, and pasting the shown point back reaches secure if the chatbot ticks literally ([06](06-settings-simulation.md)). | With 0009b in: "A reported dead link counts as checking, but secure needs a real check." With 0010b in: "Picking an option straight after being shown never makes a part secure." Otherwise: "We red-teamed our own scoring and fixed the worst exploit first." |
| **(w5)** "The checks can't be gamed by form", "our MCQs resist test-wiseness" | 0004 removed the punctuation and longest-option cues (0.96 → 0.28; w4-fix-mcq-1 ✓), but created a middle-length cue: dropping the longest and shortest options gets 58% right against about 31% chance (w5-06g-05 ~, simulation). With 0010b, cue-guessing no longer makes parts secure (4.4 → 0, verification pending), but the cue itself remains. | "We fixed the give-aways we found; our audit found a new length cue, and fixing it in the pack is next." |
| **(w5)** "Cheaper than Sparx", "affordable as homework software" on Microsoft | One eduX call costs the school about £0.0375 in Copilot Credits. Even if eduX were free, staying at Sparx's top estimate (£2.80) allows only 75 calls a student a year (w5-08u-01 ✓; w2-08-06 ✓). | "We don't compete on price. We compete on what the school learns about how its pupils use AI." |
| **(w5)** "Label agreement shown", "the chatbot labels agree with humans", or any κ from the dry run | The only agreement numbers so far compare a Claude proxy labeller with a Claude-written key: a pipeline test, not agreement evidence (w5-02s-01 ~). | Before the study: "We're checking those labels against two humans." After it: the 02a §3 template, with n and CI. |
| **(w5)** "We show which tasks a student skipped" | The skip counter recorded about 2% of ignored tasks in simulation, because a new question replaces a pending task without a skip (w5-06g-07 ~). | Nothing, until the 1-line fix is built and tested. Over the mock-up: "this is the design". |
| **(w3)** "Free on Microsoft", "students use it free through Copilot", "the free route" | Students without an M365 Copilot licence are billable. The "no charge" column covers licensed users under their own identity, and its framing is employee-facing (w3-08m-05 ~, w3-08m-13 ✓). Microsoft's own pages disagree on whether a pro-code declarative agent is free for unlicensed users; that is a test, not a claim (w3-08m-09 ✓). | Line 17. If pressed: "about £22.50 per student per year on our central assumption of 600 turns, range £11–108. That's our estimate on assumed turn counts, and we'll measure real turns in the pilot" (w3-08m-13 ✓). |
| **(w3)** "Anonymous teacher view", "anonymised data", "anonymous class reports" | Hashed keys, random ids and k ≥ 6 bands are minimisation, not anonymisation. Pseudonymous data is still personal data (ICO; w3-09-18 ~: data can be anonymous only in the hands of others who lack the key). | "Class-level only, groups of 6 or more, never names or chats." |
| **(w3)** "Preregistrations are underspecified, a Data Colada review shows", or citing Data Colada post 119 for anything about our study | The post doesn't say that. It critiques another paper's verdict on AsPredicted preregistrations (w3-02e-14 ✗). | Nothing. "We committed the protocol, messages and key to git before anyone labelled." |
| **(w3)** "κ = .7 on 40 messages gives ±.22", a per-feature κ as a headline, or "our labels are validated" | Each label sees only its own subset, so a single feature has n ≈ 18, about ±.33. The pass rule passes a bot with true κ = .6 about 40–50% of the time (w3-02e-01 ✓, -06 ✓). | "Pooled per skill: κ = __ (95% CI __–__; n decisions); humans with each other: κ = __. Synthetic messages, team-written with AI help, one chatbot. A first check, not a validation." Template wording in [02a](02a-label-agreement-protocol.md) §3. |
| **(w3)** "A student can't chat their way to secure", or "a part is known only once it's been checked" | On `main`, 14 exchanges with no check take a part to secure (.763), and it never decays (w3-06-06 ~, simulation). A prerequisite never answered can reach "developing" through propagation (w3-06-05 ✓). | Only after [06](06-settings-simulation.md) rec 10 is built: "A part only counts as known once the student has got it right. Until then it says *not yet shown*." |
| **(w3)** "Our levels rank students correctly", or a ranking of students on any slide | On `main`, a never-right student reads above a right-at-least-once student in 0.82–1.00 of pairs by day 30 (w3-06-03 ✓, simulation: synthetic students, example pack). | Nothing until the decay fix ([06](06-settings-simulation.md) recs 9–10) is built. No slide ranks students. |
| **(w3)** "Supports SEND / dyslexia-friendly / accessible to all", "eduX narrows attainment gaps" | eduX controls neither fonts nor rendering, and font claims fail (w3-05-11 ~). Evidence on who gains from tutoring software is mixed, and uptake is unmeasured (w3-05-14 ~, -15 ~). No 16–18 SEN or EAL rate is published in the sources read. | "Untimed checks, one point at a time, formulas in words for read-aloud: choices for every student, not a SEND label." On equity: "the school can compare usage by its own groups." |
| **(w3)** "One in five sixth-formers has SEN" | 14.8% SEN support and 6.0% EHC plans are for all pupils in England's schools, not 16–18s (w3-05-01 ✓). | "In England's schools, about one in five pupils has SEN." |
| **(w3)** "Judges are biased, so…", or citing the judging studies on a slide | They are from grant, admissions and investor settings, not expo judging, and several were read as abstracts only (w3-01-01 ~ to -13 ~). They shape how we present; they aren't claims for the deck. | Nothing on slides. |
| **(w3)** "eduX plugs into the chatbot your school already uses", "runs in any school chatbot" | The only documented school route is Copilot Studio, untested (line 20). The same overclaim as "works with any chatbot". | "A plug-in built on the open MCP standard. Copilot Studio documents MCP support; whether 16–17-year-olds can reach a custom agent is unconfirmed (w3-08m-04 ✓ risk note), and testing it is next." |
| **(w2)** "Hosts shape one conversation; eduX keeps a learner model across sessions", "our learner model is the moat", "only eduX tracks progress" | Gemini tracks progress across sessions and reports to teachers (w2-08-01 ✓, w2-08-02 ✓). BKT and misconception distractors aren't proprietary. | Line 41: "a head start, not a moat". |
| **(w2)** "A compliance product for AI Act Article 4", "deployers will license our instrument" | The Commission says Article 4 does not require measuring staff's AI knowledge and needs no certificate (w2-08-09 ✓). Article 4 covers staff, not pupils. | Nothing in the pitch. In Q&A: "AI-literacy evidence is for the school's teaching, not for compliance." |
| **(w2)** Wang & Fan (2025), "ChatGPT has a large effect on learning (g = 0.87)" | Retracted on 22 April 2026 (w2-09-13 ✓). | Line 36, with its limits. |
| **(w2)** MIT's "Your brain on ChatGPT", "AI rots your brain", "makes students dumber" | Unreviewed arXiv preprint; 54 participants, 18 in session 4. Its authors reject the "dumber" reading (w2-09-11 ✓). | Line 36. |
| **(w2)** Gerlich (2025) as proof that AI use causes weaker critical thinking | A correlational survey-and-interview study, since corrected (w2-09-12 ~). | Line 36, or nothing. |
| **(w2)** "52% of 16–18s use AI weekly" | 52.0% is a share of 16–18 *AI users*, not of all 16–18s (w2-09-01 ~). | Line 28, with the base. |
| **(w2)** "58.5% of teens check AI answers" as evidence of behaviour | Self-report, and the base is those who had heard of generative AI (w2-09-02 ✓). The deck says self-report is weak, so this would contradict it. | Line 30, only as the set-up for line 6. |
| **(w2)** "Running eduX costs schools nothing", "zero running cost", "cheaper than a chatbot" on Copilot | On Copilot Studio the school pays Copilot Credits per turn. Wave 3 replaced the old US$84 estimate: about £22.50 per student per year in the central case, range £11–108 (w3-08m-13 ✓, our estimate on assumed turn counts). See the (w3) "free on Microsoft" row. | Line 17. |
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
| "The chatbot's labels are reliable", or "GPT-4 marks as well as a human (κ = .70)" | LLM agreement varies widely by task (QWK .30 to .87; w1-02-29 ~). The κ .70 figure is abstract-only (w1-02-28 ~). A meta-analysis found decoder models agree less (w1-02-30 ~). None of this is our chatbot on our labels. Without outside feedback, self-correction made GPT-3.5 worse on one benchmark (w2-02-41 ✓). | **Rewritten (w3).** "The chatbot labels the behaviour. We check its labels against two blind humans and report agreement pooled per skill, with a confidence interval and the humans' agreement with each other." Only after the study has run; otherwise "we're checking". |
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

## (c) Deck outline: 4 minutes, 8 slides (revised in wave 3)

This replaces the wave-2 outline. It comes from `work/w3/w3-01.md` §3 with four fixes:
- slide 5 no longer says "every wrong option";
- slide 7 no longer says "plugs into the chatbot a school already uses";
- slide 6 uses the agreement number only if the Wednesday study runs;
- no slide leads with a ~ number.

Only ✓ numbers from `findings.csv` lead a slide. Our own captures (14 ms, 51/51) are not ✓ and don't lead.

**Criteria tags** (w1-01-02 ✓, w1-01-03 ✓; no weights):
- **P**: problem fit (assessing);
- **D**: defining (from the title; re-check once the brief is pasted);
- **W**: who it helps;
- **H**: how it works in practice;
- **E**: educational value.

**Delivery rules** ([01](01-competition-fit.md) recs 15–17):
- Speak each number's population caveat out loud.
- Keep BKT, MCP, "evidence-centred design" and "stealth" off the slides.
- Caption key claims in 8 words or fewer.

| # | Time | Slide | The sentence | Lead number (✓ id) | Spoken caveat | Criteria |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:25 | **Confident isn't competent** | "About half of teens feel confident spotting AI-made content, and one in four of those couldn't, so we assess what students do, not what they say." | **1 in 4.** Of teens confident they could identify AI-generated content (52%), 25% failed Ofcom's image test (w2-09-04 ✓; line 27) | "UK 13–17s, Ofcom 2026; an AI-image test, not fact-checking" | P |
| 2 | 0:25–0:55 | **What we mean by AI literacy** | "For a sixth-former studying with a chatbot, AI literacy is knowing when and how far to trust it, shown in what they do while they work." | **19.** The final OECD–EC AILit Framework has 4 domains and 19 competences, and says AI literacy isn't tool use (w1-02-01 ✓, w1-02-02 ✓; lines 1–2). We score three skills from it | "We cover parts of 8, none in full; ethics and creating AI are out of scope" | D |
| 3 | 0:55–1:20 | **Why we observe, not ask** | "Asking students how AI-literate they are tells you little, so Ask, Verify and How AI works are each scored when the student does them." The 3 × 3 rubric is the visual | **r = .21.** Self-rated AI literacy vs a knowledge test (w1-02-25 ✓; line 6). Back-up: a 20-item test predicted AI-assisted work and self-report did not (w1-02-23 ✓; line 7) | "120 German adults" | P, D |
| 4 | 1:20–2:00 | **See it work** (20-s clip or four stills) | "The moment a chatbot gets something wrong is the moment we teach why, and the moment we record what the student did." | **Almost half.** Of 3,000+ chatbot answers about the news, almost half had a significant issue (w2-02-36 ✓) | "EBU study, 18 countries incl. UK, 2025; news questions". Caption: "scripted demo, web search off" | P, E |
| 5 | 2:00–2:30 | **Why it teaches** | "Unguarded chatbots can make practice look better and exams worse, so eduX teaches one point at a time and builds its wrong options from real misconceptions." | **−17%.** Unrestricted GPT-4 raised practice scores 48% but lowered unassisted exam scores 17%; a guarded tutor avoided the harm (w2-09-08 ✓; line 36) | "One Turkish high school, maths; the guarded tutor didn't raise exam scores either" | E |
| 6 | 2:30–3:00 | **How far to trust our scores** | "One moment is weak evidence, so we show the evidence count, call early levels provisional, and test against an external measure." | **About 12** observed moments per skill for reliability .70 (w1-02-31 ✓, our calculation; line 10). Bar to beat: r ≈ .40, what published embedded assessments reached against external tests (w1-02-21 ✓, -22 ✓; line 9) | "Our calculation"; "US school students, convergent validity, not learning". Add the simulation line (39) only if the settings land, and the κ line only if the Wednesday study ran ([02a](02a-label-agreement-protocol.md) §3) | P, E |
| 7 | 3:00–3:30 | **Who it helps, how it runs** | "eduX is a plug-in a school's chatbot can call. Microsoft Copilot Studio documents MCP support; whether 16–17-year-olds can reach a custom agent is unconfirmed, and we're asking Microsoft. The teacher class view (bands, groups of 6 or more, never chats) is a labelled mock-up today." | **34%.** Only 34% of secondary schools had an AI-use policy, while 73% of secondary teachers thought pupils had used GenAI for homework (w1-08-04 ✓; line 22) | "Teachers' perceptions, not measured use"; "filmed on an adult team member's account" (w1-05-02 ✓; lines 19–20) | W, H |
| 8 | 3:30–4:00 | **Next** | "Our first users are the 46,365 A level Economics entrants in England, and we start with a feasibility pilot, not a learning claim." | **46,365.** A level Economics entries in England, 2026 (w1-08-01 ✓; line 21). Keep 0.17 SD (w1-08-08 ✓; line 24) for Q&A 10 | "England only" | H |

**Changes from the wave-2 outline.**
- Slide 1 leads with a performance result, not self-report or teacher perception (wave-2 researcher #3).
- Slide 3 is now "observe, not ask", and the rubric moves into its visual.
- Slide 4 carries a frequency number, so the demo isn't a numberless interlude.
- Slide 5 swaps the economics distractor statistic for the guarded-vs-unguarded result. The 36% inflation line (line 14) moves to the spare Q&A answer.
- The validity slide's "eduX tested its own alarms" chart (line 40) and the Gemini line (41) move to Q&A (Q8) and the leave-behind.

Keep these for Q&A unless the build team lands them on Wednesday: the safety points (wellbeing signpost, no training on pupil data, key revocation), the Copilot cost estimate, and the Bastani limits.

## (d) The 10 likeliest expo questions, with 30-second answers (wave 3)

These are deduplicated from `judge-panel.md`, with EduX-judge and researcher questions ranked first and investor questions last. Each answer is about 75 words: the honest caveat first, then what it enables ([01](01-competition-fit.md); w3-01-07 ~). Only ✓ numbers are used. They come from `work/w3/w3-01.md` §4, corrected for Q2, Q6, Q7, Q8 and Q9. Drill them in two 20-minute rounds on Wednesday evening, and let the person who built each part answer for it.

1. **"Define AI literacy in one sentence. What's left out?"**
   "Knowing when and how far to trust a chatbot, shown in what a student does while they work. It's anchored to the OECD–EC AILit Framework, which says literacy isn't tool use (w1-02-02 ✓). We score three skills: asking checkable questions, verifying claims against a named source, and knowing why chatbots fail. Ethics, creating with AI and building AI are deliberately out of scope. We cover parts of eight AILit competences and none in full."

2. **"How do you know a student actually checked?"**
   "We don't see clicks. Verify rests partly on what the student reports and on the chatbot's labels, so an unprompted 'I checked' doesn't make anyone secure. How AI works is the part our server scores alone, from multiple-choice checks built on real misconceptions. We're checking the chatbot's labels against two blind human raters, pooled per skill, and we report how well the humans agree with each other too."
   - If the Wednesday study ran, give its number with n and CI ([02a](02a-label-agreement-protocol.md) §3).
   - Say "weighted lower" only if the 0.20 guess setting is merged.

3. **"Isn't this an economics revision tutor with AI literacy bolted on?"**
   "It started as one, and the economics is still the study context. But the video is the AI-literacy episode: a research question, a Verify task, a chatbot failure, a check on why it failed, and the record. Economics gives us real moments when students lean on a chatbot. The literacy parts sit in their own pack, separate from the economics content, so the same moments can arise in any subject."

4. **"Why not just give them a 20-question AI-literacy test?"**
   "A test is good at what students know about AI, and we'd use one, GLAT or AILIT-S, to validate ours. But self-ratings track real knowledge poorly (r = .21; w1-02-25 ✓), and a test is a one-off. We score what students do at the moment a chatbot fails during real study, repeatedly, so the student sees change over a term, not one snapshot."

5. **"Is it valid? What's your evidence?"**
   "It isn't validated yet, and we don't claim it is. What we have: fixed scoring rules, evidence counts on every level, and early levels marked provisional, because a stable level needs about a dozen moments (our calculation, w1-02-31 ✓). The pilot correlates our scores with an external test. Published embedded assessments reached about r = .40 (w1-02-21 ✓, -22 ✓). That's our bar."

6. **"Which 16-year-old can use this on Monday, on what?"**
   "None yet, honestly. claude.ai is 18+ (w1-05-02 ✓), which is why the video caption says adult account. eduX is a plug-in built on the open MCP standard. Microsoft Copilot Studio documents MCP support with the per-student key we use (w1-05-11 ✓). But whether 16–17-year-olds can reach a custom agent at all is unconfirmed, and we're asking Microsoft. Testing that, and school sign-in, is the next build."

7. **"What does a teacher see?"**
   "Today, a mock-up, and it's labelled as one. The design shows class-level patterns only: the commonest misconceptions and the weakest parts, for groups of six or more, and AI literacy only in bands if the school opts in. Never chats, names or per-student AI-literacy scores. A teacher might see that most of the set read a PED of −0.4 as elastic, and that becomes a ten-minute lesson starter."
   - Never say "anonymous" (avoid row, w3).

8. **"Gemini, ChatGPT and Microsoft already have study modes. Why you?"**
   "They're good. Gemini now tracks objectives across sessions (w2-08-01 ✓), and Microsoft's Study and Learn is free and preselected for school students (w3-08m-04 ✓). Two differences. Theirs live inside one vendor; eduX is one plug-in, and the school owns the learner model. And none we've found assesses AI literacy itself: what a student does when the chatbot is wrong. That's the part we built, and it's a head start, not a moat."

9. **"The chatbot labels its own failures. What if it never admits one?"**
   "Then no check fires, and that's a real limit: the trigger is a label the chatbot assigns itself. Models are bad at catching their own errors without outside feedback (w2-02-41 ✓). So we've designed a scripted audit of five failure modes per chatbot, to measure how often each one misses ([02](02-ai-literacy-assessment.md) rec 19). A student can also report a failure themselves: 'this link doesn't say that' starts the same check."

10. **"Does it improve learning or grades?"**
    "We haven't measured that, and we won't claim it. Even a 100-school trial could detect only about 0.17 of a standard deviation (our calculation, w1-08-08 ✓). So the first pilot tests feasibility: do students meet failure moments, do the scores hold up against a test, do teachers use the view? The design follows what the best trial found: guarded help didn't harm exam scores; unguarded help did (w2-09-08 ✓)."

11. **"Microsoft takes 4.5× your revenue." (wave 5)**
    "Yes. In our central case Microsoft's meter is about £22.50 a student a year against our £5, and we show it rather than hide it (w5-08u-01 ✓). Each call costs the school about 4p. It's not our margin; our own cost is hosting, because eduX never calls a model. The school can cap a class of 20 at about £65 a month in term (w5-08u-04 ✓). Not calling eduX on chit-chat cuts calls by a few per cent in our model; we'll measure the real figure in the first class. The honest objection isn't the ratio: Microsoft's own Study and Learn is free. A school pays only if it values a learner model it owns and evidence of how its pupils use AI, and neither is validated yet."
    - Don't say "it might be free"; the declarative-agent route is a tenant test, not a claim. Don't promise a saving above about a fifth: that is our model on a chosen message mix.

**Spare, if asked: "Your multiple-choice options give the answer away."**
- If the fix landed on Wednesday: "They did. We fixed the option form before filming." Don't add "so they can't be gamed now": a middle-length cue remains (w5-06g-05 ~).
- If not: "We found it in our own audit, and it's the first fix" ([05](05-product-features.md) rec 11; [04](04-economics-education.md) rec 1).
- Then add: "And the wrong options themselves are real: 36% of UK adults read falling inflation as falling prices" (w1-04-07 ✓, UK adults; line 14).
