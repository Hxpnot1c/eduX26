# Judge panel (red team)

Each wave, six personas attack eduX: investor, teacher, AI-literacy researcher, DPO, student and EduX judges. They work from that wave's scout notes and verifier marks. This file condenses their verdicts and objections and says whether each objection is answered yet.

**Status key.** *answered*: a ranked recommendation that can land before Thursday fully meets the objection (most are not yet made). *partly*: a recommendation fixes the wording or plans the fix, but the product or evidence doesn't change enough before Thursday. *open*: no recommendation addresses it. "05 rec 6" means rank 6 in that report's Ranked recommendations.

**Coordinator fact.** Step 05e (Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and not merged. Scout notes that say "not built" or "only a slice could be built" are stale; the plan is to merge 05e ([01](01-competition-fit.md) rec 2).

---

## Wave 1

### Investor (UK/EU edtech seed)

**Verdict:** Would not back it as it stands. Clever architecture, but it is sold through its competitors to buyers who don't pay for pupil AI. A second meeting needs three things: a real 9EC0 pack, a working school tenant for under-18s, and a named payer.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Distribution runs through competitors, and none confirms access for a UK 16–17-year-old (claude.ai 18+; Gemini custom apps 18+, US-only; ChatGPT teen MCP unconfirmed). w1-08 rec 2's "runs inside Gemini for Education" line contradicts w1-05. | partly | [05](05-product-features.md) recs 1–3 (works-with line, caption, Q&A answer); [business plan](business-plan.md) rec 1 removes the Gemini line. Wording only: no tested under-18 route. |
| 2 | A feature, not a company: the hosts could ship per-topic memory in Study Mode or Guided Learning. BKT and misconception distractors aren't proprietary. | open | [business plan](business-plan.md) §4 names two candidate moats (the pack pipeline, a validated AI-literacy instrument). Neither exists. |
| 3 | Willingness to pay is weak: about £8 per student, £0.2–0.4m a year serviceable (our estimate), and only 20% of leaders plan pupil AI spend. | partly | [business plan](business-plan.md) recs 2–3 size the market as a ceiling and set a price (our choice). No priced letters of intent. |
| 4 | No content and no evidence. The only pack is `example-mini`. There's no efficacy data. AI-literacy scores need 12–20 moments, decay in 2 days, and one self-report makes Verify secure. | partly | [business plan](business-plan.md) rec 5 (evaluation slide); [02](02-ai-literacy-assessment.md) recs 8, 9, 12 (validity work). Plans, not evidence. |
| 5 | Team: one committer in a "team of four", and no AI-literacy history in `seed-demo`. | partly | [business plan](business-plan.md) rec 8 (name roles and commitment); [01](01-competition-fit.md) rec 5 (seed literacy history). |

**Q&A, with the answer wanted:**
1. *Which 16-year-old can legally use this on Monday, and on what?* A named Year 12 student on a school Copilot tenant, tested end to end.
2. *OpenAI adds memory to Study Mode tomorrow. What's left?* The pack pipeline or the AI-literacy instrument, with a cost per specification.
3. *Who signs the invoice, from which budget?* A role, a price and one school that said yes.
4. *How long does a full 9EC0 pack take, and who checks it?* Measured hours plus a teacher review.
5. *Who writes code after the competition?* A named person with committed time.

### Teacher (Head of Economics, state sixth form)

**Verdict:** Not as it stands. It drills definitions and formulas, which carry few 9EC0 marks. It doesn't train chains of analysis, applied diagrams or evaluation. Would trial it for Year 12 recall only, with a teacher view.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | It teaches recognition, not what the exam rewards: every check is a 4-option MCQ, and level-marked answers wait in unbuilt step 07. | partly | [04](04-economics-education.md) recs 6, 8 (contrast edges, unfamiliar transfer cases); [05](05-product-features.md) rec 7 (honest essay answer). Step 07 is not built. |
| 2 | It is easy to game. The correct option is a fragment and the distractors are full sentences. Distractors come from other points. Explain-backs can be pasted. | partly | [04](04-economics-education.md) rec 1 and [demo plan](demo-plan.md) rec 2 fix option form; [04](04-economics-education.md) rec 1 gives each point its own misconception. Pasted explain-backs are not addressed. |
| 3 | Content accuracy: every row is `draft`, one correction is already wrong (`externality_tax_eval_m1`), and there's no review step. | partly | [04](04-economics-education.md) rec 2 corrects the row; [04](04-economics-education.md) rec 3 keeps new rows as drafts until a teacher signs off. No review queue or error rate yet. |
| 4 | No teacher view, and usage reports are off by default. | partly | [05](05-product-features.md) rec 6 (mock-up, labelled); [09](09-safety-ethics.md) rec 13 (aggregate report, later). |
| 5 | Doesn't fit lessons: no class focus topic or deadline, the chatbot will still write the 25-marker, and students can't use the demo chatbot. | partly | [05](05-product-features.md) rec 3 (route answer); [09](09-safety-ethics.md) rec 9 (light friction on "just show me"). Class focus is Later in [05](05-product-features.md). |

**Q&A, with the answer wanted:**
1. *Walk a student through a 9-mark tax-incidence question.* They write it and get a level and a next step for each strand, or an honest "not built yet".
2. *How many hours to build the full pack, and who signs it off?* A number, a teacher-approval step and an error rate from review.
3. *What stops a student picking the shortest option?* An audit of option form plus a simulated shortest-option guesser.
4. *What do I see on Monday?* A class summary of weak parts and misconceptions, with no chats and groups of at least 5.
5. *Is there evidence on grades, not MCQ scores?* "None yet", plus a pilot with a blind-marked essay outcome (business plan §9).

### AI-literacy researcher (measurement)

**Verdict:** Would back it as teaching, not yet as an *assessment* of AI literacy. The construct is narrow. The evidence is self-report or labelled by the chatbot. Some scoring rules contradict the coaching.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Scoring contradicts coaching. Ask 2/4 counts as wrong in BKT, yet `ask_min_features = 2` treats it as good enough. Precise questions fail without a prompt ritual. Ignored tasks are scored 0 when they should be missing data. | partly | [02](02-ai-literacy-assessment.md) recs 2 and 4 (Ask threshold; ignored = missing), both S, not yet made. Precise two-feature questions still fail until rec 13 (core + bonus), which is after Thursday. |
| 2 | Verify measures restating, not checking. The "opened" tick can't be observed. Ticks 2–4 can be met by repeating the chatbot's reply. The source is one the chatbot proposed. | partly | [02](02-ai-literacy-assessment.md) recs 5–6 (a task the reply can't answer, an accept/revise/reject tick, damped self-reports). The "opened" tick stays unobservable. |
| 3 | Items don't fit their triggers. `fabrication` fires even with `web_access`. `pushback_changed` fires when the student was right. Distractors carry absolute cues. One wrong click marks a misconception as "held". | partly | [02](02-ai-literacy-assessment.md) recs 3 and 7 (wording, web-access condition) before Thursday; recs 14–15 (`pushback_correct`, two picks before "held") later. |
| 4 | The assessed system writes its own evidence. The chatbot self-labels `conflict_flagged`, `pushback_changed` and `web_access`. | partly | [02](02-ai-literacy-assessment.md) rec 8 (κ study, student-message labels only). The self-label audit is later (README open question 7). |
| 5 | The claim outruns the construct. Evidence comes only from rare `research` turns, and 05e still carries the withdrawn Khanmigo line. | answered | [02](02-ai-literacy-assessment.md) recs 1, 9, 12 (narrow named construct, "embedded", evidence counts); [09](09-safety-ethics.md) rec 11 removes the Khanmigo line. |

**Q&A, with the answer wanted:**
1. *Define AI literacy. What's out?* Critical use of chatbot output for study (AILit Engage 2–3, Manage 1). Ethics and creation are coached or out of scope.
2. *How do you know they opened the source?* "We don't. That tick is downweighted, and the other ticks need facts that aren't in the reply."
3. *How reliable is an Ask level after a week?* "Provisional. We show evidence counts, and a level needs about 8–12 moments."
4. *What if the chatbot never admits failing?* "Then no check fires. Here is our per-chatbot audit of self-labelling and its miss rate."
5. *What external measure validates it?* GLAT or AILIT-S for How AI works, a civic-online-reasoning task for Verify, and a preregistered pilot with N ≥ 62, expecting r ≈ .3–.4.

### DPO (trust data protection officer)

**Verdict:** Not approvable as is. Would approve a pilot within a term if objections 1–4 are fixed.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | No lawful chatbot route for under-18s, so there is no processor chain for a DPIA. | partly | [05](05-product-features.md) recs 1–3 and [09](09-safety-ethics.md) rec 2 fix the wording, not the route. |
| 2 | The key works like a password: it sits in a URL, is stored in plaintext (`edux/learner.py`) and can't be rotated or revoked. Ids are name slugs. | partly | [09](09-safety-ethics.md) recs 3, 4, 7 (hash, revoke/rotate, pseudonymous ids; all S). The key stays in the URL until OAuth ([09](09-safety-ethics.md) rec 15). |
| 3 | Every message reaches eduX word for word, with no route for a safeguarding disclosure. | partly | [09](09-safety-ethics.md) recs 8 (wellbeing signpost) and 10 (DSL contact at setup). The alert route is later ([09](09-safety-ethics.md) rec 14). |
| 4 | No retention period, no erasure and no subject-access export. | answered | [09](09-safety-ethics.md) recs 5–6 (`delete-student`, `export-student`, a written retention default; all S). |
| 5 | Profiling of minors. `text/style.md`'s "use what you already know about the student" pulls in vendor memory. AI-literacy levels in a teacher view must be off by default. | answered | [09](09-safety-ethics.md) rec 1 deletes the `style.md` line; [05](05-product-features.md) rec 6 keeps AI-literacy levels out of the default teacher view. |

**Q&A, with the answer wanted:**
1. *Which chatbot does a 16-year-old use, under whose contract?* A named school tenant with a DPA, not consumer accounts.
2. *A pupil's URL is posted on Snapchat. Now what?* "One command revokes it. Keys are hashed. OAuth by [date]."
3. *A student discloses abuse mid-revision. What happens?* Teaching stops, the DSL route is signposted, host monitoring flags it, and eduX keeps only a count.
4. *Who is the controller, and where is the data hosted?* The school is the controller and eduX is a processor. Hosting is in the UK or EEA, with no pooling across schools.
5. *What can a teacher see about one child?* Progress levels with evidence counts only. Nothing else by default.

### Student (Year 13, Edexcel Economics, uses ChatGPT for homework)

**Verdict:** No as it is. Would try it once, then go back to ChatGPT. Would use it before mocks if it gave exam practice rather than a quiz on every message.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | I ask a question and get a quiz, and the same question is re-asked. | partly | [05](05-product-features.md) ("answer first when rushed") and [09](09-safety-ethics.md) rec 9: a guided example with a skippable check. A tension with DfE std 10. |
| 2 | I'd never see the AI-literacy part: only research questions trigger it, and homework never does. | partly | Three of four how-AI-works checks fire on any turn ([02](02-ai-literacy-assessment.md)). Ask and Verify stay research-only; homework moments are Later in [02](02-ai-literacy-assessment.md). |
| 3 | The MCQs are easy to game. The short option is the right one. "Yeah I checked" makes Verify secure. An ignored task scores 0. | answered | [04](04-economics-education.md) rec 1 and [02](02-ai-literacy-assessment.md) rec 3 (option form and wording), [02](02-ai-literacy-assessment.md) rec 6 (damp "I checked"), [02](02-ai-literacy-assessment.md) rec 4 (ignored = missing). All S. |
| 4 | It feels like being watched ("answers drop after 35 minutes", my just-show-me share). | partly | "Decide" stays unscored ([02](02-ai-literacy-assessment.md)); "only you see this" wording ([05](05-product-features.md)); teacher reports off by default. |
| 5 | It doesn't help with 15- and 25-mark essays. | open | [05](05-product-features.md) rec 7 gives an honest answer and a roadmap only. |

**Q&A, with the answer wanted:**
1. *Can I just get the answer?* "Yes. Say you're rushed, and the check comes after and can be skipped."
2. *Who sees my "Decide" or "answers drop" stats?* "Only you, unless the school switches it on, and you'd be told."
3. *What stops me spotting the right option?* "All options match in length and style. Here's one."
4. *I'm 17. How do I even log in?* "Through the school's chatbot, not a personal Claude account."
5. *How does this help my 25-marker?* A concrete essay feature, not "later".

### EduX judges (Challenge 1)

**Verdict:** No as it stands. A capable economics revision tutor with AI literacy attached at the end; the video shows elasticity of demand, not AI literacy being defined or assessed. Scores (1–5): problem fit 2, educational value 3, working prototype on video 2, who it helps 2, how it works in practice 3. *Single biggest lift:* merge 05e and rebuild the video around one 75-second AI-literacy episode, which would likely lift problem fit and prototype to 4.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | This is a revision tutor, not an AI-literacy entry. | partly | [01](01-competition-fit.md) rec 2 and [demo plan](demo-plan.md) recs 1, 4 (merge 05e; a 72-s literacy episode). Answered only if Plan A passes the gate. |
| 2 | Where is your definition? | answered | [02](02-ai-literacy-assessment.md) rec 1 and [01](01-competition-fit.md) recs 3–4 (definition, rubric and crosswalk slides). |
| 3 | Why believe a "secure" Verify? Self-report, unvalidated labels, and 11–16% of students without the skill end "secure" under label noise. | partly | [02](02-ai-literacy-assessment.md) recs 5, 6, 8, 9, 12; [demo plan](demo-plan.md) rec 10 (end on How AI works). BKT settings unchanged until the build team acts. |
| 4 | Your students can't legally use the chatbot you filmed. | answered | [05](05-product-features.md) recs 1–2 and [demo plan](demo-plan.md) rec 3 (works-with line, adult-account caption). Wording only; see DPO #1 for the route. |
| 5 | Your assessment gives the answer away (the correct option differs in form). | answered | [04](04-economics-education.md) rec 1, [02](02-ai-literacy-assessment.md) rec 3 and [demo plan](demo-plan.md) rec 2 (pack edits, S). Needs an owner on Wednesday. |

**Q&A, with the answer wanted:**
1. *Define AI literacy in one sentence.* "Knowing when and how far to trust a chatbot, shown in what students do when it is wrong."
2. *How do you know a student actually checked?* "We don't see clicks. Verify is self-report and graded lower. Only How AI works is scored by the server. Here is our plan to measure agreement with a teacher."
3. *What does a teacher see?* Class-level skill levels and the most common misconceptions, never chats. Show a mock-up and label it as one.
4. *Which school could use this on Monday?* "Over-18s and teachers today. Microsoft schools through Copilot Studio next. OAuth is our next build."
5. *Why not a 20-question test?* "Tests measure what students say about AI. We assess what they do with it while they work. GLAT or AILIT-S is how we'd validate it."

### Wave 1 at a glance

Of 30 objections, 7 are answered, 21 partly answered and 2 open (investor #2, the moat; student #5, essays). Most "answered" items depend on the build team making small fixes on Wednesday. Three themes recur across personas:

- **Under-18 access.** Raised by the investor, teacher, DPO, student and judges. Every fix so far changes wording only.
- **Gameable or weak literacy evidence.** Raised by the teacher, researcher, student and judges. It covers option form, self-reported checks, ignored tasks scored 0, and chatbot self-labels.
- **No teacher view.** Raised by the teacher and judges. The student and DPO both warn about how one would be built.

---

## Open questions for wave 2

The merged list of 21 questions, each with its status and the persona that raised it, is in [README.md](README.md#open-questions).
