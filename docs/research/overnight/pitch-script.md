# Pitch script: video voiceover, deck speaker notes, expo leave-behind

The words the team records on Wednesday and Thursday. Written in wave 4 (scout note `work/w4/w4-01.md`) and edited only for consistency with the other reports. Build order and the cut line are in [`wednesday-build-list.md`](wednesday-build-list.md); the shot list and expo script are in [`demo-plan.md`](demo-plan.md); the claims we can and can't make are in [`pitch-notes.md`](pitch-notes.md).

**Rules these scripts follow**
- Every number spoken or captioned is marked ✓ in `findings.csv`. Ids go in the source column only, never in the spoken text.
- Design counts ("three skills") are our design, not findings. Table 4 lists them so it is complete.
- Every "claim to avoid" in `pitch-notes.md` §(b) is respected. Banned words: "stealth", "validated", any "works with any chatbot" line, any Gemini line, any learning-gain line, "compliant".
- Wherever the exam board is named, the same deliverable carries: **"Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson."**

**The slide-1 fix (judges' objection 3).** Ofcom's test asked teenagers to spot an AI-made **image**. It did not test checking a chatbot's claim. So:
- Ofcom is used only for "confidence isn't skill", and it is always called an image test.
- The share is always "a quarter **of those confident**", never "a quarter of teens".
- The fact-checking motive comes from separate ✓ numbers about chatbots' own sourcing errors (w2-02-30, w2-02-34). Those numbers measure models, not students, and the scripts word them that way.
- "Nobody can see the difference" is dropped. Our Verify skill is partly self-report, so we don't claim to see everything.

**Summary**
- The video voiceover is 311 words over 2:30, built on the as-captured Plan A shot list (w3-07). The literacy episode runs 0:40–1:46 (66 s).
- It opens with frame D and says what eduX is within 16 s, following the judging-noise advice: the student moment plus one sentence.
- Captions carry the key claims in eight words or fewer, plus the caveats: adult account, web search off, scripted source report.
- Shot 4c has two versions. The **mismatch line** needs the rewritten option set (02 rec 3). The **dead-page fallback** comes with three restrictions: don't hold on the options, don't show Verify in 4d, never say "each wrong option…".
- The deck notes come to 513 words over 8 slides (529 with the slide-6 add-on). Each slide leads with one ✓ number or one demo moment.
- The leave-behind is 222 words.
- This script makes no new findings. Every number in it is a ✓ finding in [`findings.csv`](findings.csv), our design or our calculation (§4).
- **Two lines depend on Wednesday's build** ([`wednesday-build-list.md`](wednesday-build-list.md)). Shot 4c's mismatch version needs the rewritten options (item 5). The slide-6 add-on needs the literacy settings (item 6). If either falls below the cut line, use the fallback given here.

---

## 1. Video voiceover (2:30, ≤ 360 words)

**Before every take** (from w3-07):
- reset the demo student, then open a new chat;
- turn web search off;
- check that the four driver lines are on a card, verbatim;
- keep the console visible.

**Driver lines** (as captured; they avoid the trigger words "give", "link", "ONS", "first", "cost", "different" and "shows"):
- 4a: `what was inflation like?`
- 4b: `What was UK CPI inflation in 2022, and why did it change? Sources please.`
- 4c, mismatch (needs the rewritten options): `I opened it and the page says <X>, not <Y>.`
- 4c, dead page (fallback, branch options): `I clicked it and the page doesn't exist.`
- 4d: `How am I doing at asking and checking AI answers?`

**Burned in on every chatbot frame:** "Adult team account · synthetic demo student".

**Full adult-account caption.** Show it for the whole of 0:00–0:16 and again on the end card:
> **Filmed on an adult team member's account. claude.ai consumer plans are 18+. Students under 18 would use a school-managed chatbot.**

Pace: about 150 words a minute, i.e. 2.5 words a second at most per shot. Fewer is fine.

| Time | Shot (corner keyword) | Screen | Voiceover (word for word) | On-screen captions (≤ 8 words each) | Source |
|---|---|---|---|---|---|
| 0:00–0:16 | **1. Confident ≠ skilled** | claude.ai, adult account. The 4a question and the start of a confident, sourced answer. Freeze. | "About half of UK teenagers feel confident spotting AI-made content. A quarter of those confident teens failed Ofcom's AI-image test. Confidence isn't skill. eduX assesses AI literacy where it happens: while students study with a chatbot." | "Confident isn't the same as skilled" · "1 in 4 confident teens failed an image test" · small: "Ofcom 2026, UK teens, AI-made images" · full adult-account caption | w2-09-04 ✓; w1-05-02 ✓ (adult caption) |
| 0:16–0:30 | **2. AI literacy, defined** | Rubric card: three rows (Ask, Verify, How AI works), each with an observable behaviour per level. Footer: "Scored from moments in normal study, not a quiz." | "Our definition: knowing when and how far to trust a chatbot, shown in what students do. Three skills. Ask a checkable question. Verify a claim against a source. Know why chatbots fail." | "Knowing when, and how far, to trust it" · "Ask · Verify · How AI works" · "Anchored to the OECD–EC AILit Framework" | definition: 02 (our design); anchor: w1-02-01 ✓, w1-02-03 ✓ |
| 0:30–0:40 | **3. How it works** | Diagram: student → school chatbot → eduX → plan → reply. "No AI model" on the eduX box. | "eduX plugs into the school's chatbot. Each message, it returns a plan from fixed rules. It never calls an AI model." | "Fixed rules. No AI model calls." | architecture (our design) |
| 0:40–0:54 | **4a. Ask** | Driver types 4a. The reply answers with sources, then sets the Ask task: add a time period. Highlight the task line. | "A vague question: what was inflation like? The chatbot answers with sources, then sets an Ask task: add a time period." | "Ask: is the question checkable?" · "Web search off" | w3-07 shot 4a (our simulation, not ✓; no number used) |
| 0:54–1:06 | **4b. Verify** | Driver types 4b (four features). The reply answers with sources, then the Verify task: open the source and say which month the figure is for. | "The sharper question counts as evidence. Now a Verify task: open the source and say which month the figure is for." | "Verify: check one figure at its source" | w3-07 shot 4b |
| 1:06–1:30 | **4c. How AI works** (mismatch version) | Driver types the mismatch line. The reply says checking found a problem and corrects the claim. Then the four-option question from the **rewritten** set. Highlight box on the options. The student picks "a reference naming a publisher and a date is probably real". The reply names that idea and corrects it. | "The student reports the page says something else. That's the moment to learn why. One question, four options. Each wrong option is a known wrong idea about chatbots. They pick: a source with a publisher and date is probably real. The reply corrects it. A cited source may not exist, or may not say what was claimed. Check it." | "Web search off" · "Scripted demo: student reports a mismatched source" · "Why did the source fail?" · "A source may not say what's claimed" | w3-07 shots 4c, 4c′; lesson: 02 (our design, on w2-02-30 ✓, w2-02-34 ✓; no number spoken) |
| 1:06–1:30 | **4c. How AI works** (dead-page fallback, branch options only) | Driver types the dead-page line. **Don't hold on the four options:** the branch set still contains m2. Cut from the question to the reply after the wrong pick (m1, "copied a page that was later deleted"). | "The student reports the link is dead. That's the moment to learn why. This student guesses the page was deleted. The reply corrects it: a cited source may not exist at all. So check it." | "Web search off" · "Scripted demo: student reports a dead link" · "Why did the source fail?" · "A cited source may not exist" | w3-07 rec 2 |
| 1:30–1:46 | **4d. The record** | Driver types 4d. `get_my_progress`, AI-literacy section. Highlight the "still held" line, **not** a How AI works level. After a dead-page take, **don't show Verify** (it falls). If the reply leads with economics, cut to the console row for the how-AI-works part. | "The student asks how they're doing. Every moment is evidence. The server scores the letter itself, not the chatbot's opinion. And the student sees the wrong idea they still hold." | "The record: evidence from real study" · "How AI works: scored by our server" | w3-07 recs 6–7; pitch-notes line 12 (our design) |
| 1:46–2:04 | **5. Same question, two students** | Split screen. Both type "How do I calculate price elasticity of demand?". Left, `demo-secure`: an intuition question. Right, `demo-weak`: a check on the definition, then last time's mistake corrected. Hold on the first line of each reply, not the options. | "The same engine teaches the course. Same question, two synthetic students. One gets an intuition question. The other gets a check on the idea it builds on, and last time's mistake corrected." | "Same question, two students, two plans" · "Two synthetic demo students" | demo-plan shot 5 (captured) |
| 2:04–2:16 | **6. How it runs** | Silent terminal montage, under 3 s a shot. Crop out or blur the console timing figure and the check counts; caption no number from the screen. Connector URL with the key blurred. "Sample course pack". | "It runs on a laptop. The school's chatbot does the writing; eduX returns the plan. Built on the open Model Context Protocol, tested with claude.ai on an adult account." | "Open protocol (MCP)" · "Tested on claude.ai, adult account" | w1-05-01 ✓; pitch-notes line 18 (w2-05-03 ✓) |
| 2:16–2:30 | **7. What could be** | Back to the opening chat, now with the how-AI-works question in place. End card. | "Same chatbot. Now a slip becomes a lesson in how AI works, and a record the student can see. For under-18s, the next step is a school-managed chatbot. That's eduX." | End card: "eduX · AI literacy, assessed where it happens" · team names · **"Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson."** · full adult-account caption | w1-05-02 ✓; business plan rec 10 (disclaimer) |

**Word count:** 311 words, counting the mismatch version of 4c (the dead-page version is shorter). No shot is above 2.5 words a second; 4c and 6 are at about 2.4–2.5, so read those two briskly or let the picture run on a beat.

**Notes for the edit**
- **The 4c figures.** The live figures typed in 4c (`<X>`, `<Y>`) appear on screen as footage. Never narrate or caption them.
- **If the ONS link really is broken** or really mismatches on the take, you may use it. Keep the caption "Scripted demo" off only in that case. Even then, never say the chatbot invented it.
- **Mismatch version: Verify must have three points ticked.** Use it only if 4c is sent as the Verify answer with points a, c and d. Otherwise the record shows Verify falling (w3-07); in that case, don't show Verify in 4d.
- **The board.** The end card is the only place the video names the board, and it carries the disclaimer.

---

## 2. Deck speaker notes (4 minutes, ≤ 560 words)

One idea per slide. Plain words: keep technical names (BKT, MCP, evidence-centred design) off the slides and in Q&A. Say each population caveat aloud where it is written. The "Lead" line is what the slide shows first.

### Slide 1 · Confident isn't skilled (0:00–0:25)
**Lead:** "1 in 4": of the UK teenagers confident they could spot AI-made content, a quarter failed Ofcom's image test. **Source:** w2-09-04 ✓.

> "Ofcom tested UK teenagers this year. About half felt confident spotting AI-made content. A quarter of those confident teens then failed an AI-image test. It was a test of images, not of checking facts. But it shows confidence isn't skill, and asking students won't tell you who has it. eduX assesses AI literacy where it happens: while students study with a chatbot."

### Slide 2 · What we mean by AI literacy (0:25–0:55)
**Lead:** "19 competences" (AILit). **Source:** w1-02-01 ✓, w1-02-02 ✓, w1-02-03 ✓. **On slide:** the definition, the three skills, "out of scope".

> "We anchor to the OECD–European Commission AILit Framework: four domains, 19 competences. AILit says AI literacy is not the same as using AI tools. So we never count use. Our definition: knowing when and how far to trust a chatbot, shown in what students do. Three skills: Ask, Verify, and How AI works. Ethics and building AI are out of scope."

### Slide 3 · Why we watch, not ask (0:55–1:20)
**Lead:** "r = 0.21". **Source:** w1-02-25 ✓ (120 German adults), w1-02-23 ✓ (university students).

> "Why watch instead of ask? In one study of 120 German adults, self-rated AI literacy correlated only 0.21 with a knowledge test. In another, with university students, a 20-question test predicted performance on an AI-assisted task. A self-report scale did not. So each skill is scored when the student does it, in normal study."

### Slide 4 · See it work (1:20–2:00)
**Lead (demo moment):** a 20-second clip of 4c–4d, captioned "Scripted demo · web search off · adult team account". **Source:** w2-02-30 ✓, w2-02-34 ✓ (model behaviour, not students).

> "Here, a student reports that a page doesn't say what the chatbot claimed. eduX asks one question on why, and records the answer. Why that lesson? With search off, GPT-4 invented 18% of its references in a 2023 study. With search on, about 30% of GPT-4o's statements weren't backed by the pages it cited. So we teach one thing that is true either way: check that the source says it."

### Slide 5 · Why it teaches (2:00–2:30)
**Lead:** "−17%". **Source:** w2-09-08 ✓; w2-04-02 ✓. **Slide footer:** "Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson."

> "In a randomised trial with about 1,000 Turkish high-school maths students, unrestricted GPT-4 raised practice scores 48% but cut unassisted exam scores 17%. A guarded tutor avoided that harm, though it didn't raise exam scores either. So eduX teaches one point, then checks. Wrong options come from misconceptions. These checks are a way in: about two-thirds of marks in Pearson Edexcel 9EC0 are level-marked."

### Slide 6 · How far to trust our scores (2:30–3:00)
**Lead:** "About 12 moments per skill" (our calculation). **Source:** w1-02-31 ✓, w1-02-21 ✓, w1-02-22 ✓. *If the label-agreement study (build list item 11) is dropped rather than postponed, change "we're checking those labels" to "next, we check those labels".*

> "One moment is weak evidence. By our calculation, a stable level needs about a dozen moments per skill. So we show the evidence count and call early levels provisional. Only How AI works is scored by our server alone. Ask and Verify rest on the chatbot's labels and on what students report, and we're checking those labels against two humans. Our pilot's bar: published embedded assessments reached correlations of about 0.4 with outside tests."

*Add this only if the three literacy settings are merged on Wednesday (w2-02-08 ✓, simulation):* "In simulation with synthetic students, 5% or fewer students with no skill were ever shown secure."

### Slide 7 · Who it helps, how it runs (3:00–3:30)
**Lead:** "34%". **Source:** w1-08-04 ✓ (teachers' perceptions), w1-05-02 ✓, w2-05-04 ✓, w2-05-03 ✓. **On slide:** a teacher-view mock-up, labelled "mock-up".

> "Only 34% of secondary schools had a policy on safe AI use, while 73% of secondary teachers think pupils have used generative AI for homework. eduX never calls an AI model; the school still pays its chatbot provider. We tested on claude.ai, adults only. For pupils, the documented route is Microsoft 365 Education, where Copilot Chat is off by default for 13- to 17-year-olds. Schools add eduX through Copilot Studio. That's documented, not yet tested."

### Slide 8 · Next (3:30–4:00)
**Lead:** "46,365". **Source:** w1-08-01 ✓ (England, all boards), w1-08-08 ✓ (our calculation). **On slide:** team roles.

> "There were 46,365 A level Economics entries in England in 2026. That's who we start with. Next: merge, sign-in, a Copilot Studio test, then a feasibility pilot. It is not a learning claim: even a 100-school trial could detect only about 0.17 of a standard deviation, by our calculation. Here's who does what."

**Word count:** 513 spoken words without the slide-6 add-on, and 529 with it. Both are under 560, leaving room for pauses.

---

## 3. Expo leave-behind (one page, ≤ 250 words)

Print this on A4 with a QR code to the video in the corner.

> **eduX: AI literacy, assessed where it happens**
>
> **The problem.** About half of UK teenagers feel confident spotting AI-made content. A quarter of those confident teens failed Ofcom's AI-image test (2026). Confidence isn't skill.
>
> **Our definition.** For a 16–18-year-old studying with a chatbot: knowing when and how far to trust it, shown in what they do. Anchored to the OECD–EC AILit Framework.
>
> | Skill | What we observe | Scored by |
> |---|---|---|
> | Ask | a question that can be checked: idea, place, period, sources | the chatbot's labels, our fixed rules |
> | Verify | names the source, says what it says, whether it matched | the chatbot's labels and the student's report |
> | How AI works | picks why a source failed, from four options | our server alone |
>
> **How it runs.** eduX plugs into a school's chatbot over the open Model Context Protocol. It never calls an AI model. Tested on claude.ai with an adult account (18+). For pupils: Microsoft 365 Education with Copilot Studio is documented, not yet tested.
>
> **How far to trust the scores.**
> - We have: fixed scoring rules, evidence counts, provisional early levels.
> - We will gather: the chatbot's labels checked against two humans, and a pilot correlated with an outside AI-literacy test.
>
> **What we don't claim.** No learning gain yet. Not a finished test.
>
> Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson.
>
> [QR: video] · [team names, contact]

**Word count:** 222 words, including the table and the footer.

---

## 4. Every number used → finding id → mark

V = video, D = deck, L = leave-behind.

| Number as used | Where | Finding id | Mark | Caveat to keep |
|---|---|---|---|---|
| "about half" of UK teens confident spotting AI-made content (52%) | V1, D1, L | w2-09-04 | ✓ | UK teenagers; Ofcom 2026 |
| "a quarter" / "1 in 4" of those confident failed the test (25%) | V1, D1, L | w2-09-04 | ✓ | **of the confident**; an AI-image test, not fact-checking |
| 18+ (claude.ai consumer plans); "under-18s" | V caption, V7, L | w1-05-02 | ✓ | consumer terms |
| 4 domains, 19 competences (AILit) | D2 | w1-02-01 | ✓ | final 2026 framework |
| "not the same as using AI tools" (no number) | D2 | w1-02-02 | ✓ | — |
| 0.21 correlation, 120 German adults | D3 | w1-02-25 | ✓ | adults, Germany |
| 20-question test predicted an AI-assisted task; self-report didn't | D3 | w1-02-23 | ✓ | university students |
| 18% of GPT-4's references invented, 2023 | D4 | w2-02-30 | ✓ | 2023 models, search off, academic references |
| about 30% of GPT-4o's statements unsupported, search on | D4 | w2-02-34 | ✓ | 800 medical questions; models, not students |
| about 1,000 students; practice +48%; exam −17% | D5 | w2-09-08 | ✓ | Turkish high school, maths; guarded tutor gave no exam gain |
| about two-thirds of 9EC0 marks level-marked | D5 | w2-04-02 | ✓ | our tally of the June 2025 mark schemes |
| about a dozen (12) moments per skill | D6 | w1-02-31 | ✓ | our calculation |
| correlations of about 0.4 with external tests | D6 | w1-02-21, w1-02-22 | ✓ | US school students; convergent validity |
| 5% or fewer no-skill students ever shown secure (conditional) | D6 add-on | w2-02-08 | ✓ | simulation, synthetic students; settings proposed |
| 34% of secondary schools had an AI-use policy | D7 | w1-08-04 | ✓ | England state schools, 2025 |
| 73% of secondary teachers think pupils used GenAI for homework | D7 | w1-08-04 | ✓ | teachers' perceptions |
| Copilot Chat off by default for 13–17s | D7 | w2-05-04 | ✓ | K-12 tenants |
| Copilot Studio documents MCP support | D7, V6 (implied), L | w2-05-03 | ✓ | untested by us |
| claude.ai supports custom MCP connectors (no number) | V6 | w1-05-01 | ✓ | — |
| 46,365 A level Economics entries, England, 2026 | D8 | w1-08-01 | ✓ | entries, England only, all boards |
| about 0.17 SD with 100 schools | D8 | w1-08-08 | ✓ | our calculation; large-sample multiplier |
| four options (how-AI-works check) | V4c, L | — | our design | — |
| three skills | V2, D2, L | — | our design | — |
| 16–18-year-old (target group) | L | — | our design | — |
| 9EC0 (course code) | V end card, D5, L | — | identifier | disclaimer carried |

---

## 5. What I wanted to say but couldn't (not ✓, or ruled out)

| Wanted to say | Why not |
|---|---|
| "Seven in ten 16–18s have used generative AI; 52% weekly" | w2-09-01 is ~; also 52.0% is a share of users only. If a usage figure is needed, "66% of 16–17s use AI" (w2-09-04 ✓) is available. |
| "In 2025, almost half of 3,000+ chatbot news answers had a significant issue" | w2-02-36 is ✓ and allowed. I left it out for word budget and to keep slide 4 on the lesson's own numbers. It can replace the 18%/30% line if the team prefers, worded as chatbots' errors, not students'. |
| "A turn takes about 14 ms" / "median 10 ms" | Our own measurements (demo-plan, w3-07), not verifier-checked. Video shot 6 crops the figure. |
| "All 51 (or 74/74) automated checks pass" | Our own measurement; not ✓. |
| κ from Wednesday's label-agreement study | Not run yet, so not in findings.csv. Slide 6 says "we're checking those labels against two humans" with no number. |
| "£5 per student per year; trust tier £3" | Our choice, not a finding. It can go on slide 8 only labelled "our choice"; I kept it out of the spoken script. |
| "About £22.50 a student a year in Copilot credits", "5 credits per call" | Now ✓ (w3-08m-06, -07, -13), but £22.50 is our estimate on assumed turn counts, and it is a cost the school pays Microsoft, not a pitch point. Keep it for Q&A: "about £22.50 per student per year on our central estimate, £11–108 depending on use" ([business plan](business-plan.md)). Never quote the old US$84 estimate. |
| "≤ 3% with 20% random label errors" (the wave-2 morning brief's wording, now corrected in every report) | The ✓ claim text for w2-02-08 says "at or below 5% in every noise cell". The script uses that, and only conditionally. |
| "0.18 SD" (small-sample figure) | Unchecked; w1-08-08 ✓ is 0.17. |
| "Gemini tracks progress; we don't sell to Google schools" | Gemini is banned from these scripts by the task, even though w2-08-01/02 are ✓. Keep it for Q&A (pitch-notes line 41, minus "across chatbots"). |
| "A learner model the school owns across chatbots", "whichever chatbot a school uses" | The task's no-any-chatbot rule. Only one client (claude.ai) is tested. |
| "We don't claim a validated test" (pitch-notes line 11) | Contains the banned word. Said instead as "not a finished test". |
| "Nobody can see the difference" (frame D) | The panel noted that Verify is partly self-report, so we can't see everything either. |
| "The guarded tutor raised practice 127%" | w2-09-08 ✓, but it invites a learning-gain reading. Left out. |
| 36% of UK adults read falling inflation as falling prices | w1-04-07 ✓; dropped for time. Spare Q&A line. |
| Judging-noise statistics (68% vs 32% by narrator's voice, NIH reviewer disagreement) | w3-01-03 and -05 are ✓, but they come from grant and investor settings, not expo judging, and pitch-notes bans them from slides. Used only as advice (short captions), never as a claim. |
| Verify 0.748 / 0.14, How AI works AUC 0.40 | Our simulations (w3-07, w2-02-05 ~). Not for the scripts. |
| "Catching a fake link raises your Verify score" | False on the branch today: a dead page lowers Verify (w3-07). Hence the 4d restriction. |
| "The chatbot invented that link" | The source report is scripted unless a real failure happens on camera. |
| "76% → 55% secure-but-not-known" chart | w1-06-04 ✓ (simulation). Left out for time and to keep one number per slide; available for slide 6 if the team swaps it in. |

