# 01 · Competition fit: Cambridge EduX 2026 UK, AI literacy

Waves 1 and 3, with a wave-2 consistency edit. Sources: scout note `work/w1/w1-01.md` with verifier marks `verify-A.json`; wave-3 scout note `work/w3/w3-01.md` (how judges decide, a red team of our problem statement, the deck and expo Q&A) with verifier marks `verify-K.json` (w3-01-*); the judges panel (`panel-judges.md`); the competition-relevant parts of the other wave-1 scout notes (marks in `verify-B/C/D.json`). Wave 2 added no 01 scout note; this edit brings 01 into line with the wave-2 reports ([02](02-ai-literacy-assessment.md), [05](05-product-features.md), [business plan](business-plan.md)) and the wave-2 panel (`work/w2/panel-judges-researcher.md`). Marks: ✓ confirmed, ~ broadly supported with a stated problem. Findings marked ✗ are left out (none in wave 3). **Wave-3 caveat:** none of the judging studies looks at education hackathons or expo judging. Their evaluators are skating juries, MBA interviewers, grant reviewers, investors and online panels, so everything drawn from them is a transfer, and is marked as one. The revised slide outline and the 10 expo Q&A answers live in [pitch-notes](pitch-notes.md), not here.

**Facts set by the coordinator, which override the scout notes:**
- **Step 05e is built but not merged.** Step 05e (AI-literacy coaching: Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and pushed. We checked this with `git rev-list` and `merge-base`. Scout notes that say "not built", or that count 10 commits (w1-01-13 ✓), are out of date.
- **No published rubric, and the brief is still missing.** The official rules page publishes no rubric or weights (w1-01-02 ✓). The Challenge 1 brief page renders in the browser and could not be fetched, so the team must paste it into the repo on Wednesday.
- **(Wave 2) Gemini has caught up on tracking.** Study notebooks track progress across sessions (25 Jun 2026), and Google Classroom gives teachers progress insights (from 3 Nov 2026) (w2-08-01 ✓, w2-08-02 ✓). The line "hosts shape one conversation; eduX keeps a learner model across sessions" is no longer true. Lead with AI-literacy evidence from real use, plus a school-owned learner model that works across chatbots, and call it a head start, not a moat.
- **(Wave 2) Web search is off for the video, and the "searched a database and picked the wrong entry" option (m2) is never taught as a misconception.** With search on it is often the true account (w2-02-33 ~, w2-02-34 ✓).

## Summary
- **There is one explicit criterion: fit to the chosen problem.** The rules add three implied ones: educational value, a working prototype on video, and, at the expo, "who it helps" and "how it works in practice". There are no weights, and complex code earns nothing (w1-01-02 ✓, w1-01-03 ✓). The 2025 grand champion was an oral assessment of critical thinking (w1-01-07 ✓).
- **The assessing half is built, but only on its branch, and the video shows none of it.** Step 05e scores Ask, Verify and How AI works from moments in normal study. The branch is not merged to `main`, and `seed-demo` gives no student any AI-literacy history. All seven sections of `docs/demo-script.md` show economics personalisation (w1-01-13 ✓). The red team's verdict was "a revision tutor with AI literacy attached".
- **The defining half is missing as a deliverable.** Today it is three rows in a CSV and a one-line topic description. The credible anchor is the final OECD–EC AILit Framework (2026): 4 domains, 19 competences (w1-02-01 ✓). eduX covers parts of 8 competences and none in full. [02](02-ai-literacy-assessment.md) holds the definition, the slide text and the crosswalk.
- **Competition has moved (wave 2).** Gemini tracks progress across sessions and reports it to teachers in Classroom, free to Google schools (w2-08-01 ✓, w2-08-02 ✓). Microsoft's Study and Learn is free and preselected for K-12 students (w3-08m-04 ✓). eduX's honest difference is narrow: AI-literacy evidence from real chatbot use, and a learner model the school owns across chatbots. Both are an unvalidated head start, not a moat.
- **Honest wording.** The filmed client (claude.ai consumer) is 18+ (w1-05-02 ✓), so say so on screen and name the school route. Drop the Khanmigo line: the 05e step doc still says refused students stopped using Khanmigo, and the trial doesn't support it (w1-09-08 ~).
- **Judges are noisy, and the noise is not about content (wave 3; transferred from other settings).** In a replicated NIH review, 43 reviewers showed no agreement on the same 25 applications (w3-01-03 ✓). An identical pitch was funded by 68% of online viewers with a man's voice and 32% with a woman's (w3-01-05 ✓). Running order and daily quotas shift scores too (w3-01-01 ~, -02 ~). We can't control any of that. We can make the content legible without a judge's goodwill: the challenge's own words on slide 1, claims as captions, and a page they take away.
- **Recommended problem statement (frame D, pending the pasted brief):** *"Teenagers feel confident with AI, but confidence doesn't show whose AI literacy is real, and nobody can see the difference."* The follow-on line: "eduX assesses AI literacy where it happens: in the moments a chatbot gets something wrong during study."
  - It keeps the challenge's noun, answers the wave-2 researcher's "you motivate with self-report", and claims no more than we score.
  - It leads with a performance result: a quarter of confident teens failed Ofcom's AI-image test (w2-09-04 ✓).
- **How to present (wave 3).**
  - Show established methods in a new place, not a new science. Evaluators marked down highly novel proposals and those close to their own field (w3-01-04 ✓).
  - Show preparation, not passion (w3-01-06 ~).
  - Answer each risk question caveat first, then say what the product makes possible (w3-01-07 ~).
  - Use plain words on slides (w3-01-12 ~), one number per claim, and one student's moment as the frame (w3-01-10 ~).

## Ranked recommendations
Ranks 1–11 keep their wave-1 numbers (other reports cite recs 2–5). Wave 3 adds ranks 12–18. The old 12 (real teacher view) is now 19 and the old 13 (Entra sign-in) is now 20. Ranks 1–18 can be done before Thursday 23:59.

| rank | recommendation | lands in | effort | before Thu? | rests on |
|---|---|---|---|---|---|
| 1 | **Paste the brief.** First thing on Wednesday, someone opens the UK challenge page in a browser and pastes all five sections (Problem Overview, Challenge Statement, Target Users, Scope & Focus, Desired Outcomes) and the setter's name into `docs/research/overnight/challenge-brief.md`. Then re-check the criteria table below against Desired Outcomes. | pitch, video | S | yes | w1-01-04 ✓ |
| 2 | **Merge 05e and build the video around one AI-literacy episode of about 75 s.** (a) A vague research question gets a full sourced answer plus an Ask task. (b) The student reports that a link didn't say what was claimed, and gets a correction plus a how-AI-works check. (c) A wrong pick names the misconception. (d) Progress shows Ask and Verify levels, and How AI works as per-part counts ("checked n, right m") plus the wrong ideas still held, not as a level ([02](02-ai-literacy-assessment.md) rec 6). Cut demo-script sections 4, 6 and 7 from the video and keep them for the expo. | build, video | M | yes | w1-01-13 ✓; panel-judges |
| 3 | **"What we mean by AI literacy" slide:** the definition, three scored skills as behaviours, the AILit crosswalk, and what is out of scope. The text is in [02](02-ai-literacy-assessment.md), "Definition and competency model". | pitch, video opening | S | yes | w1-02-01 ✓, w1-02-02 ✓, w1-02-03 ✓ |
| 4 | **Rubric slide (3 skills × 3 levels)**, each cell an observable behaviour, taken from the 05e new/developing/secure texts. The rubric may describe How AI works in levels of behaviour, but the product and video report it as per-part counts, because the rolled-up level ranks students backwards in simulation ([02](02-ai-literacy-assessment.md) rec 6). | pitch | S | yes | w1-01-03 ✓; w2-02-05 ~ |
| 5 | **Seed one demo student with AI-literacy history.** Give them several earlier research questions with few features, one Verify task, and one held how-AI-works wrong idea taken from [02](02-ai-literacy-assessment.md)'s rewritten set (for example "a reference with a journal and year is probably real"), so progress shows a path and not an empty section. **Never seed or teach m2** ("searched a database and picked the wrong entry"): with search on it is often true. Film with web search off and caption it. The point taught is that a cited source may not exist, or may not say what was claimed ([02](02-ai-literacy-assessment.md) recs 3 and 7). This touches `edux/cli.py seed-demo`, so the build team owns it. | build, demo | S–M | yes | w1-01-13 ✓; w2-02-33 ~, w2-02-34 ✓; [02](02-ai-literacy-assessment.md) recs 3, 7 |
| 6 | **Fix the give-away MCQ wording before recording.** Economics pack: the correct option has no full stop and is shorter, in 6 of 6 captured option sets ([04](04-economics-education.md) rec 1, our count). Wave 3 found the opposite cue on the current `plan.py` path. When a part has no mark point, the correct option is the node description, and it is longer than every distractor in 7 of 9 parts ([05](05-product-features.md) rec 11; w3-05-08 ~). Either way the form gives the answer away, so check the build you film. Literacy pack: the distractors use absolute words ("always", "only", "on purpose") while the correct options hedge with "can" ([02](02-ai-literacy-assessment.md) rec 3). | course pack (team) | S | yes | [04](04-economics-education.md) rec 1; [02](02-ai-literacy-assessment.md) rec 3 |
| 7 | **Validity-honesty slide:** what we have (fixed rules, server-scored MCQs, an evidence-centred design) and what we'd gather (agreement with humans, a pilot against an external test). Slide text in [02](02-ai-literacy-assessment.md). | pitch | S | yes | w1-02-33 ~; w1-02-20 ✓ to w1-02-22 ✓ |
| 8 | **"Who it helps / how it works in practice" slide.** Students get the checks inside their usual chatbot, with no extra model calls. Teachers get a **mock** class view: misconceptions to reteach and the weakest parts, aggregated, groups of 6 or more, never chats. Class-level AI literacy appears only in bands, and only if the school opts in; never per student ([05](05-product-features.md) rec 4). Say "adult team account" on screen. Today it reaches over-18s and teachers. For under-18s, Microsoft 365 Education via Copilot Studio is the documented school route, untested, and Copilot Chat is off by default for 13–17s ([05](05-product-features.md) recs 1–3). | pitch, video caption | S | yes (mock) | w1-01-03 ✓; w1-05-02 ✓; w2-05-03 ✓, w2-05-04 ✓ |
| 9 | **Drop the Khanmigo-refusal justification from the deck.** Justify "never withhold research answers" on design grounds: checking is practised on a real, full answer. Course questions stay hint-first, in line with the DfE standard (w1-09-01 ✓). The 05e step-doc line needs a one-line team edit; no report's ranked list owns it. | pitch | S | yes | w1-09-08 ~; w1-09-01 ✓ |
| 10 | **Expo kit.** A laptop running the server locally, one pre-seeded student, a reset step between judges, a recorded fallback of the literacy segment, and one printed rubric page. At least one member must be onsite at Homerton on 20 Nov. | demo | S | yes | w1-01-02 ✓, w1-01-05 ✓ |
| 11 | **"Why not Gemini?" answer, slide and Q&A.** "Gemini now tracks progress inside Google, and Classroom shows teachers progress. We don't sell to Google schools. eduX gives a school evidence of how pupils ask and check, from real chatbot use, and a learner model the school owns across chatbots. A head start, not a moat; not yet validated." Never say the hosts "shape one conversation". | pitch | S | yes | w2-08-01 ✓, w2-08-02 ✓, w2-08-03 ✓; [business plan](business-plan.md) rec 1 |
| 12 | **Replace the slide-1 and video-opening problem line with frame D** (below). Once `challenge-brief.md` is pasted, check its *Desired Outcomes*. If it centres on teachers or on schools needing a way to assess, keep the problem sentence and change the follow-on line to "…and gives schools a way to assess it from normal study". Keep within the k ≥ 6 band rule for anything a teacher sees. | pitch slide 1, video 0:00–0:15 | S | yes | w2-09-04 ✓, w1-02-25 ✓, w1-01-02 ✓; w3-01-03 ✓, -04 ✓ |
| 13 | **Use the revised 8-slide outline** in [pitch-notes](pitch-notes.md) §(c). One sentence and one ✓ number per slide. Speak each number's population caveat out loud ("UK teens", "one Turkish high school, maths", "synthetic students"). | pitch | S–M | yes | w1-07-01 ✓ (analogy); see pitch-notes |
| 14 | **Q&A drill: two 20-minute rounds on Wednesday evening**, using the 10 answers in [pitch-notes](pitch-notes.md) §(d). Each answer gives the caveat first, then what it enables. Rotate who answers; the person who built a part answers for it. Spend this time before more slide polish. | expo | S | yes | w3-01-06 ~, -07 ~, -08 ~ |
| 15 | **Plain-word pass on slides and voiceover.** Keep these words off the slides: BKT, Bayesian, MCP, evidence-centred design, stealth, rollup, slip/guess. Say instead: "the rules that update what we think a student knows", "a plug-in the school's chatbot calls", "scored from moments in normal study". Keep the technical names for Q&A. | pitch, video | S | yes | w3-01-12 ~ |
| 16 | **Key claims as short on-screen captions** (8 words or fewer) at the moment they are spoken: the definition, the skill names, the number, "adult team account", "scripted: web search off". Then the content doesn't depend on who presents or how. Don't caption whole sentences. **Choose presenters by who knows the part best and has rehearsed most**, never by voice, gender or looks. | video, pitch | S | yes | w3-01-05 ✓; w1-07-01 ✓ (signalling 0.70, redundancy 0.10; lab learners, analogy) |
| 17 | **First 15 s of the video: the student moment, plus one sentence on what eduX is.** Not the logo and not the architecture. | video | S | yes | w1-07-07 ✓ (practitioner); w3-01-13 ~ (impressions form fast; says nothing about accuracy) |
| 18 | **Anchor the novelty, and leave a record.**<br>• Name the lineage on the definition and trust slides in plain words: "the evidence-centred design method used in published game-based assessments" (w1-02-21 ✓, -22 ✓) and "anchored to the OECD–EC AILit Framework" (w1-02-01 ✓).<br>• Extend rec 10's printed page into a one-page leave-behind: the problem sentence, the definition, the 3 × 3 rubric, the validity "have / will gather" list, the works-with line and a QR code to the video. Judges who score late in the day, or deliberate afterwards, need a record. | pitch, expo | S | yes | w3-01-04 ✓; w3-01-02 ~, -03 ✓ (inference) |
| 19 | **A real teacher view** (privacy checklist §5; spec in [05](05-product-features.md)). | build | L | no | w2-05-23 ~, w2-05-29 ✓ |
| 20 | **Entra sign-in and a tested school-tenant route** for under-18s. | build | M–L | no | w1-05-02 ✓, w2-05-03 ✓, w2-05-04 ✓ |

## Criteria table
The rows come from what the rules page actually publishes (w1-01-02 ✓, w1-01-03 ✓). "Defining" comes from the challenge title, which no public page we reached confirms: the brief has not yet been pasted. The red-team scores are the panel's guesses, not the judges'.

| criterion (source) | what eduX has | rating | fix | red-team score (1–5) |
|---|---|---|---|---|
| Addresses the chosen problem: **assessing** AI literacy (Judging) | 05e on its branch: three skills, evidence-centred design, BKT evidence types, how-AI-works MCQs built from misconceptions, triggered at real failure moments | **Partial.** Strong in design, built, but not merged and not on video. Scoring problems in report 02. | Merge; fix the scoring rules in report 02; give it the main shot in the video (rec 2) | 2 |
| Addresses the chosen problem: **defining** AI literacy (title; brief not yet pasted) | Part ids and one-line descriptions in `ingest/ai_literacy/nodes.csv` | **Missing** as a deliverable | Definition, rubric, crosswalk and scope slides (recs 3–4) | (in the above) |
| Working prototype in a 2–3 min video (Submission) | The server runs and the MCP checks pass (our capture run: 51/51, 14 ms median, no network calls; not verified; see the [demo plan](demo-plan.md)). `demo-script.md` has no literacy moment. | **Partial:** the prototype works, but the video plan shows the wrong thing | Literacy episode (rec 2), seeded history (rec 5), MCQ wording (rec 6), the three crash and loop bugs fixed before filming ([06](06-settings-simulation.md) recs 1–3) | 2 |
| Educational value explained (Submission) | Learning-science grounding in `research.md`; lateral reading can be taught (Wineburg et al. 2022, already in `research.md`) | **Partial:** no evidence yet that our scores mean what they claim; the Khanmigo line is unsupported | Validity slide (rec 7); drop Khanmigo (rec 9) | 3 |
| Who it helps (Central Themes) | Students see progress. There is no teacher view. The filmed client is 18+. Gemini now gives Google schools progress tracking and teacher insights free (w2-08-01 ✓, w2-08-02 ✓). | **Partial** | Mock teacher view and honest access wording (rec 8); the Gemini answer (rec 11); real view later (rec 12) | 2 |
| How it could work in practice (Central Themes) | It plugs into the school's existing chatbot, makes no model calls, uses fixed rules, and has teacher-editable trusted sources | **Partial** (wave 2 downgrade): the only documented under-18 route, Copilot Studio, is untested, and there the school pays Microsoft Copilot Credits per turn (our rough estimate, unverified: w2-05-06 ~) | One clear slide (rec 8). Note the open items: sign-in, under-18 access, credit cost, ChatGPT's per-call confirmations ([05](05-product-features.md)) | 3 |
| Expo: judges visit, watch demos, ask questions (Judging) | Connector and tunnel set-up (step 06) | **Partial** | Expo kit (rec 10) | n/a |
| Complex code not required (Judging) | A lot of engineering | **Over-delivered.** The risk is spending video time on architecture. | Lead with the student moment; show the server for 10 s at most | n/a |
| Interdisciplinary teams encouraged (Central Themes) | Four economics students | **Partial** | Present the team as subject experts building on learning science; don't claim a mix we don't have | n/a |

## How judges decide, and what we do about it (wave 3)

Every study below is from another setting. Each row gives its population, and the last column is our transfer to EduX.

| finding | evaluators | what we do |
|---|---|---|
| 43 reviewers rating the same 25 NIH applications showed no agreement on quality (ICC 0, α 0.024) (w3-01-03 ✓) | US grant reviewers | Don't make judges infer fit. Use the challenge's words on slide 1, the definition on slide 2, and repeat both on the leave-behind (recs 12, 18) |
| An identical pitch was funded by 68.33% of viewers with a male voice and 31.67% with a female one. At three US competitions, men were about 60% more likely to win (OR 1.57) (w3-01-05 ✓) | online adults; investor judges | Let the content carry itself as on-screen captions (rec 16). **Never** choose or swap presenters on gender, voice or looks |
| Skaters later in a randomised first round scored higher in both rounds (w3-01-01 ~, abstract only) | international skating judges | Low actionability: we can't pick expo order. Make the stand self-explanatory at any time of day |
| Interviewers who had already rated several applicants highly that day were less likely to rate the next one highly (w3-01-02 ~, abstract only) | MBA interviewers, over 9,000 interviews | A leave-behind page, so late or deliberating judges can recover specifics (rec 18) |
| Evaluators randomly assigned to proposals (2,130 pairs) scored highly novel proposals, and those closest to their own expertise, lower (w3-01-04 ✓) | university grant evaluators | Present established methods in a new place (rec 18). Expect the AI-literacy expert to judge slides 3 and 6 hardest; keep those to ✓ wording |
| Perceived preparedness, not displayed passion, moved funding decisions (w3-01-06 ~, abstract only) | VCs and finance professionals; lab participants | Rehearsed, honest Q&A (rec 14) |
| Founders asked prevention-focused questions raised less; answering them with promotion-focused answers raised more (w3-01-07 ~, abstract only) | TechCrunch Disrupt investors and founders | Each answer: caveat first, then what it enables. Never pivot past the caveat |
| Randomised pitch training at four competitions fitted an option-value model of investor interest (w3-01-08 ~, abstract only). That training helped only good pitches comes from secondary summaries | aspiring founders, experienced investors | Polish helps only real substance: merge 05e and film the literacy episode first, then polish the deck |
| In Nigeria's YouWiN! competition, judges' scores explained under 2% of later outcome variation and didn't predict outcomes for non-winners, though they did help predict employment for winners. Machine learning didn't beat simple models (w3-01-09 ~; **the scout overstated it**, and the verifier read only a secondary summary) | business-plan judges | Judges score what they see on the day. Make the fit visible in 4 minutes; keep the business case for Q&A |
| Statistics moved beliefs and attitudes more; narratives moved intentions more (w3-01-10 ~, abstract only) | health-campaign audiences, adults | One ✓ number per claim, with one student's moment as the frame. "Stories beat lists" is not a settled finding |
| More narrative abstracts were cited more, an effect tied to journal identity (w3-01-11 ✓) | climate-science abstracts | Weak support only. Don't cite it on a slide |
| Needlessly complex words, and a hard-to-read font, lowered judged intelligence (w3-01-12 ~, abstract only) | US university students | Plain-word pass (rec 15) |
| Strangers' ratings of under-30-second silent clips predicted end-of-semester teacher ratings (w3-01-13 ~, abstract only; r = .76 not checked) | US college students rating teachers | Open the video on the student moment (rec 17). Impressions form fast; this doesn't show they're right |

**No controlled study compares a live demo with slides for judges, or studies hackathon or expo judging outcomes.** The scout found none. "The video is the demo" rests on practitioner advice (w1-07-11 ✓).

## Problem statement: frame D and the alternatives (wave 3)

**What we say now** (pitch-notes slide 1): "Sixth-formers already ask chatbots for facts. Whether they can tell when it's wrong is invisible to everyone, including them."

**Keep the noun "AI literacy"; change what sits under it.** The one explicit criterion is fit to the chosen problem (w1-01-02 ✓), and the challenge title names "Defining and Assessing AI Literacy". But every Challenge 1 team shares the noun, and a framework-first opening is a list, not a problem.

| | statement | strongest ✓ evidence | problem with it | fit to "Beneath the Surface: Defining and Assessing AI Literacy" |
|---|---|---|---|---|
| A (current) | "Sixth-formers ask chatbots for facts; whether they can tell when it's wrong is invisible to everyone, including them." | w1-02-27 ✓ (US, 52% fooled by a video); w2-02-36 ✓ | Good, but "invisible to them" has no number, and "ask for facts" is narrow | good on "beneath", implicit on "assessing" |
| B (offloading) | "Students use AI for homework; nobody can see whether they're thinking." | w2-09-08 ✓ (unguarded GPT-4: practice +48%, exam −17%); w1-08-04 ✓ (73% of secondary teachers *think* pupils used it for homework) | **Overclaims.** Homework literacy moments (`summarise`, `ai_output_pasted`, `draft`) aren't built, and eduX doesn't "see thinking": Ask and Verify rest on chatbot labels and student reports. It also invites "show me a learning gain" | strong on "beneath", weak on "AI literacy" |
| C (failure moment) | "A chatbot's answer looks the same whether it's right or wrong; AI literacy is what a student does in that moment, and that's where we assess it." | w2-02-36 ✓ (almost half of 3,000+ news answers had a significant issue) | True to the design, but it describes the product more than a problem, and doesn't say whose problem it is | strong on "assessing" |
| **D (say vs do; recommended)** | **"Teenagers feel confident with AI, but confidence doesn't show whose AI literacy is real, and nobody can see the difference."** Follow-on: "eduX assesses AI literacy where it happens: in the moments a chatbot gets something wrong during study." | w2-09-04 ✓ (52% of teens confident; 25% of those failed an AI-image test); w1-02-25 ✓ (self-rated AI literacy r = .21 with a knowledge test); w1-02-23 ✓ (a performance test predicted AI-assisted work; self-report didn't) | Ofcom's test was spotting an AI-made image, not checking a chatbot's claim, so say "spotting AI content". "Where it happens" is true of the triggers. It must not become "we see what they do": Verify is partly self-report, and only How AI works is scored by the server alone | **Best.** "Surface" = confidence and self-report; "beneath" = behaviour at failure moments; "assessing" is in the sentence; "defining" follows on slide 2 |

**Why D.**
- It *is* the assessment problem: self-report doesn't track competence, so you have to observe behaviour.
- It fixes the contradiction the wave-2 researcher raised: the old slide 1 motivated with self-report, then slide 3 said self-report is weak.
- It keeps the noun and claims no more than we score.

**Conditional on the pasted brief.** If the *Problem Overview* or *Desired Outcomes* centres on teachers, or on schools needing a way to assess, keep the sentence and change the follow-on line (rec 12). If it centres on dependence or offloading, use B's evidence (w2-09-08 ✓) on the "why it teaches" slide, not slide 1.

## How to present (wave 3)
- **Established methods in a new place.** Name the lineage in plain words on the slides: evidence-centred design as used in published game-based assessment, and the AILit Framework (rec 18). Frame eduX as known parts in a new setting, not a new science (w3-01-04 ✓).
- **Caveat, then what it enables.** Every Q&A answer opens with the honest limit and then turns to something real: the pilot design, the rule that limits the risk, the per-part results (w3-01-07 ~). Our honesty rules come first: never answer a risk question with a promise.
- **Preparation over polish.** Two Q&A drill rounds on Wednesday evening (rec 14; w3-01-06 ~).
- **One idea and one ✓ number per slide, with one student moment as the frame** (w3-01-10 ~; w1-07-01 ✓ for coherence and signalling, lab learners, analogy). The "one number" rule itself is practitioner advice.
- **Plain words on slides; technical names in Q&A** (rec 15; w3-01-12 ~).
- **Claims on screen as short captions** (rec 16; w3-01-05 ✓).
- **The 10 likeliest expo questions with 30-second answers, and the revised 8-slide outline,** are in [pitch-notes](pitch-notes.md) §(c) and §(d). They are ranked EduX-judge and researcher questions first, investor questions last.

## Defining AI literacy: what we under-deliver
**What exists.** The definition is only implicit:
- **Content rows.** Three skill parts and four how-AI-works parts in `ingest/ai_literacy/nodes.csv` (branch).
- **A topic line.** "Using AI chatbots well for study: asking precise questions and checking what they say."
- **What is missing.** There is no stated definition, no levels written as behaviours, no scope, and no link to a framework.

A brief titled "Defining and Assessing" asks for both halves. Today we deliver about one and a half.

**What the judges would ask (panel-judges Q1):** "Define AI literacy in one sentence."

**The fix.** One slide with the definition, the three scored skills written as behaviours, the AILit crosswalk and what is out of scope. The wording, the crosswalk and the framework notes live in [02](02-ai-literacy-assessment.md) ("Definition and competency model" and "Framework crosswalk"); use them as written. Two points matter for competition fit:
- **Use the names the video shows.** The progress output on screen says `ask`, `verify` and `how_ai_works`, so the slide should too.
- **Answer the judges' first question in one sentence.** "Knowing when and how far to trust a chatbot, shown in what students do while they work" ([02](02-ai-literacy-assessment.md)).

## Later (not before Thursday; for the business plan and Q&A)
- **A real teacher view.** Misconceptions and weakest parts for groups of 6 or more; class AI literacy in bands, opt-in; per-student completion only as a school opt-in, default off; never chats, levels or AI-literacy scores per student (coordinator decision; [05](05-product-features.md)).
- **Sign-in, and a tested school route for under-18s.** Copilot Studio in a K-12 Microsoft 365 tenant is documented (w2-05-03 ✓, w2-05-04 ✓), untested, and costs the school Copilot Credits ([05](05-product-features.md), [business plan](business-plan.md)).
- **If the UK setter is Cambridge University Press & Assessment,** align the definition slide's language with its AI-literacy material. Its Oceania involvement is confirmed (w1-01-09 ✓). For the UK it is unknown.
- **Prize details.** None are published for the UK edition. Don't quote the Oceania prizes as UK prizes (w1-01-06 ✓).

## Considered and rejected
- **Using another hackathon's rubric as a proxy.** It would mean inventing criteria (w1-01-02 ✓).
- **Treating the Oceania Challenge 1 (higher-education assessment) as ours.** It was a different edition with different numbering.
- **A standalone AI-literacy quiz to "prove" the assessment.** It contradicts the embedded design. An external test belongs in a validity pilot, not in the product (report 02).
- **Building a real teacher dashboard before Thursday.** One build day is not enough. Use a mock, labelled as a mock.
- **Naming Friction on a slide.** Its page returned 403, and the official gallery doesn't list it (w1-01-08 ~).
- **"Hosts shape one conversation; eduX keeps a learner model across sessions" as a moat.** False for Gemini since June 2026 (w2-08-01 ✓).
- **Frame B (offloading) as the headline (wave 3).** It is the sharper sentence, but it claims homework moments that aren't built and "seeing thinking" we can't do, and it invites a learning-gain question we can't answer. Its evidence moves to the "why it teaches" slide.
- **Leading slide 1 with 58.5% of 16–18s who say they check (w2-09-02 ✓) or 73% of teachers (w1-08-04 ✓).** Both are self-report or perception, which contradicts slide 3. The 73% moves to slide 7 as context.
- **Leading with fabricated citations from 2023 (w2-02-30 ✓).** Judges will call it dated. EBU 2025 (w2-02-36 ✓) is current and includes the UK.
- **Using serial-position findings to order slides or ask for a late expo slot.** They concern order across contestants, and we can't control expo order (w3-01-01 ~).
- **Choosing a presenter by voice, gender or looks.** A fairness risk, and not what the evidence supports doing (w3-01-05 ✓).
- **"1 in 4 beats 25%" or "stories beat lists" as evidence.** The first rests on a meta-analysis of a different task, read only through secondary sources. The second is mixed (w3-01-10 ~). We use both as style, not as findings.
- **Huang & Pearce (2015) on investor gut feel.** Only secondary summaries were readable; too weak to build on.
- **Monroe's motivated sequence and the pyramid principle.** Practitioner frameworks, with no controlled tests on evaluators found.
- **The 2025 AILit draft names ("Designing AI") or a competence count of 22.** The final framework has 19 competences and the domain Shape AI (w1-01-10 ~, w1-02-01 ✓).

## Panel objections this report answers or leaves open
| objection (panel) | status |
|---|---|
| "A revision tutor, not an AI-literacy entry" (judges 1) | **Partly**: met only if recs 2–3 land and Plan A passes the gate. Then literacy opens the video and is its main shot. |
| "Where is your definition?" (judges 2) | **Answered** by a document: the definition, rubric and crosswalk text in [02](02-ai-literacy-assessment.md) (slides: recs 3–4). |
| "Why believe a 'secure' Verify?" (judges 3; researcher 2, 4) | **Partly.** There is a validity slide (rec 7). The scoring fixes and the agreement study are in report 02; the BKT settings are not changed yet. |
| "Your students can't legally use the chatbot you filmed" (judges 4) | **Partly.** Honest captions and route wording (rec 8); no tested under-18 route; sign-in is later. |
| "Your assessment gives the answer away" (judges 5; student 3) | **Recommended** (rec 6), not done. Nobody owns it yet: assign it on Wednesday. |
| "Your demo corrects a true belief" (m2; judges w2 #1) | **Recommended**: rec 5 and the [demo plan](demo-plan.md) now teach "the source may not exist or may not say what was claimed" with search off. Not filmed yet. |
| "Why not Gemini?" (judges w2 #2; investor w1 #2, w2 #3) | **Partly**: honest head-start wording (rec 11); no moat and no validation. |
| "You motivate the problem with self-report, then say self-report is weak" (researcher w2 #3) | **Answered** in wording: frame D leads with Ofcom's performance result (rec 12; pitch-notes slide 1). |
| "The free Microsoft tutor is already in the channel" (investor w3 #3; Study and Learn) | **Partly**: fair mention in the summary and pitch-notes Q&A 8; no tested route and no priced cap. |
| "No teacher view" (judges, criterion 4) | **Partly:** a mock only. |
| "I'd never see the literacy part; it's only on research questions" (student 2) | **Partly.** Three of the four how-AI-works triggers fire on any turn, not only research turns (branch code). Ask and Verify are research-only. Literacy moments inside homework are not designed. |
| "Decide / just-show-me feels like being watched" (student 4) | **Partly, and a tension.** A scout proposed "Decide" as a fourth scored skill; [02](02-ai-literacy-assessment.md) rejects it. The trend stays unscored and visible to the student only. If it goes on a slide, say who sees it. |
| "Answer-first mode", "help with 25-markers" (student 1, 5) | **Out of scope here.** See [05](05-product-features.md) (answer-first compromise; honest essay answer) and [09](09-safety-ethics.md) rec 14. |

## Findings
| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-01-01 | UK edition: a 2–3 min video and a 4-min pitch deck, due Thu 19 Nov 2026, 11:59 PM GMT | official document | EduX UK entrants | policy | ✓ |
| w1-01-02 | Judging is on fit to the chosen problem; no complex code needed; expo-style; no rubric or weights | official document | EduX UK entrants | policy | ✓ |
| w1-01-03 | Teams should show the idea, who it helps and how it works in practice, and explain its educational value | official document | EduX UK entrants | policy | ✓ |
| w1-01-04 | Four exploration areas; briefs have five fixed sections, Desired Outcomes among them | official document | EduX UK entrants | policy | ✓ |
| w1-01-05 | Open entry; at least one member onsite at Homerton on 20 Nov; interdisciplinary teams encouraged; team owns its IP | official document | EduX UK entrants | policy | ✓ |
| w1-01-06 | No UK prizes published; Luma says cash and AI tokens "to be revealed"; Oceania prizes differ | official document | EduX UK and Oceania | policy | ✓ |
| w1-01-07 | 2025 grand champion: oral assessment of critical thinking; Oceania 2026 winners listed without descriptions | official document | adult entrants | adoption (awards) | ✓ |
| w1-01-08 | Friction (Monash TAILER Lab) reported as an Oceania winner; prompts verification; reports to educators | practitioner (secondary) | higher education, Australia | adoption | ~ page 403; snippets only; not in the official gallery |
| w1-01-09 | Oceania challenge setters included Cambridge University Press & Assessment | official document | EduX Oceania | policy | ✓ |
| w1-01-10 | AILit: four domains (Engage, Create, Manage, Shape) | official document | school students, EU/OECD | policy | ~ the count is 19 in the final framework, not "unresolved" |
| w1-01-11 | UNESCO students' framework: 12 competencies, 4 dimensions, 3 levels | official document | school students, worldwide | policy | ~ secondary only (use w1-02-06 ✓ instead) |
| w1-01-12 | Long & Magerko: evaluate / communicate and collaborate / use as a tool; 17 competencies | theory | general learners | policy | ~ via secondary review (use w1-02-07 ✓ instead) |
| w1-01-13 | 05e on its branch, not on `main`; demo script has no literacy moment; seed-demo has no literacy history | repo inspection | n/a | adoption (build status) | ✓ (commit count now 14, per coordinator) |
| w3-01-01 | Later skaters in a randomised first round scored higher in both rounds | quasi-experimental | international skating judges | adoption (scores) | ~ abstract only |
| w3-01-02 | Interviewers who had rated several applicants highly that day rated the next lower | correlational (archival) | MBA interviewers, US | adoption (ratings) | ~ abstract only; US setting not in abstract |
| w3-01-03 | 43 reviewers, 25 NIH applications: no agreement (ICC 0, α 0.024) | quasi-experimental | US grant reviewers | adoption (scores) | ✓ |
| w3-01-04 | Randomised evaluators (2,130 pairs) scored novel proposals and those close to their expertise lower | RCT (random assignment) | university grant evaluators, US | adoption (scores) | ✓ |
| w3-01-05 | Identical pitch funded 68.33% (male voice) vs 31.67% (female); men OR 1.57 to win at 3 competitions | RCT + correlational | US online adults; investor judges | adoption (funding) | ✓ |
| w3-01-06 | Preparedness, not passion, moved funding decisions | lab experiment + field study | VCs, finance professionals | adoption (funding) | ~ abstract only; populations not verified |
| w3-01-07 | Prevention questions cut funding; promotion answers raised it | correlational + RCT | US pitch-event founders and investors | adoption (funding) | ~ abstract only |
| w3-01-08 | Randomised pitch training fitted an option-value model of investor interest | RCT | US founders and investors | adoption (continued interest) | ~ abstract only; the quality interaction is secondary |
| w3-01-09 | YouWiN! judges' scores and ML predicted later outcomes poorly | correlational | Nigerian entrepreneurs and judges | prediction | ~ **overstated**: scores explain under 2% of variation and are not significant for non-winners, but help predict employment for winners (secondary summary) |
| w3-01-10 | Statistics move beliefs and attitudes more; narratives move intentions more | meta-analysis | adults, health campaigns | interest/motivation | ~ abstract only |
| w3-01-11 | 732 climate abstracts: narrative style cited more, tied to journal identity | correlational | scientific abstracts | adoption (citations) | ✓ |
| w3-01-12 | Needless complexity and hard fonts lowered judged intelligence | RCT (lab) | US university students | interest/motivation | ~ abstract only |
| w3-01-13 | Under-30-second silent clips predicted end-of-semester teacher ratings | correlational | US college students | prediction | ~ abstract only; r = .76 not checked |

Also cited here; each sits in its home report's table: w3-05-08 ~ ([05](05-product-features.md)); w3-08m-04 ✓ (wave-3 note `work/w3/w3-08m.md`, mark in `verify-K.json`); w1-02-21 ✓, w1-02-22 ✓, w1-02-23 ✓, w1-02-27 ✓, w2-02-30 ✓, w2-02-36 ✓, w2-09-02 ✓, w2-09-04 ✓ ([02](02-ai-literacy-assessment.md)); w2-09-08 ✓ ([09](09-safety-ethics.md)); w1-07-01 ✓, w1-07-07 ✓, w1-07-11 ✓; w1-08-04 ✓ ([business plan](business-plan.md)); w2-02-05 ~, w2-02-33 ~, w2-02-34 ✓ ([02](02-ai-literacy-assessment.md)); w2-05-03 ✓, w2-05-04 ✓, w2-05-06 ~, w2-05-23 ~, w2-05-29 ✓ ([05](05-product-features.md)); w2-08-01 ✓ to w2-08-05 ✓ ([business plan](business-plan.md)); w1-02-01 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-02 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-03 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-05 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-25 ✓ ([02](02-ai-literacy-assessment.md)), w1-05-02 ✓ ([05](05-product-features.md)), w1-09-01 ✓ ([09](09-safety-ethics.md)), w1-09-08 ~ ([09](09-safety-ethics.md)).
