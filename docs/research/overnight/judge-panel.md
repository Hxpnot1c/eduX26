# Judge panel (red team)

Each wave, six personas attack eduX: investor, teacher, AI-literacy researcher, DPO, student and EduX judges. They work from that wave's scout notes and verifier marks. This file condenses their verdicts and objections and says whether each objection is answered yet.

**Status key (from wave 2, applied to both waves).**
- *answered*: a fix is built, or a document answers the objection.
- *recommended*: we recommend a fix, but it isn't built.
- *partly*: part of the objection is met (by a document, a built piece or a recommendation), part is not.
- *open*: nothing addresses it.

"05 rec 6" means rank 6 in that report's Ranked recommendations. "w2-05 rec 3" means rank 3 in that wave-2 scout note.

**Coordinator facts.**
- Step 05e (Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and not merged. Scout notes that say "not built" are stale.
- As of wave 2, none of the wave-1 code fixes is built on `main`. `edux/server.py` still reads only `?key=` (no bearer header). Delete, export, retention, key hashing and revocation, and the DSL route are plans. The `text/style.md` line "use what you already know about the student" is still on `main`.
- Per-student data for teachers (wave-2 decision): per-student *completion* (did checks or didn't, this week) may be a school opt-in, default off, as in Sparx. Per-student *levels*, AI-literacy scores, offloading and draft counts are never shown per student. Class-level AI literacy is shown only in bands, for groups of at least 6, and only if the school opts in. This removes draft and offloading counts from the teacher view and settles the w2-09 rec 4 vs w2-05t conflict.
- For the video, web search is off, and "searched a database and picked the wrong entry" is not taught as a misconception (with search on it is often true; w2-02h).

---

## Wave 1

Statuses below were re-checked in wave 2 against the new key. Wave 1 had called seven objections "answered" because a small fix was ranked for Wednesday. Only one (the definition) is answered by a document. The rest are now "recommended" or "partly", because the fixes aren't built.

### Investor (UK/EU edtech seed)

**Verdict:** Would not back it as it stands. Clever architecture, but it is sold through its competitors to buyers who don't pay for pupil AI. A second meeting needs three things: a real 9EC0 pack, a working school tenant for under-18s, and a named payer.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Distribution runs through competitors, and none confirms access for a UK 16–17-year-old (claude.ai 18+; Gemini custom apps 18+, US-only; ChatGPT teen MCP unconfirmed). w1-08 rec 2's "runs inside Gemini for Education" line contradicts w1-05. | partly | [05](05-product-features.md) recs 1–3 and [business plan](business-plan.md) rec 1 fix the wording. Wave 2 documents a K-12 Microsoft Copilot Studio route (w2-05 rec 1), but it is untested. |
| 2 | A feature, not a company: the hosts could ship per-topic memory in Study Mode or Guided Learning. BKT and misconception distractors aren't proprietary. | open | Worse in wave 2: Gemini now tracks progress across sessions (w2-08-01, -02 ✓). w2-08 recs 1–2 reword it as a "head start", not a moat. No moat exists yet. |
| 3 | Willingness to pay is weak: about £8 per student, £0.2–0.4m a year serviceable (our estimate), and only 20% of leaders plan pupil AI spend. | partly | [business plan](business-plan.md) recs 2–3 size the market and set a price (our choice); w2-08 rec 4 adds a trust tier. No priced letters of intent. |
| 4 | No content and no evidence. The only pack is `example-mini`. There's no efficacy data. AI-literacy scores need 12–20 moments, decay in 2 days, and one self-report makes Verify secure. | partly | [business plan](business-plan.md) rec 5 (evaluation slide); [02](02-ai-literacy-assessment.md) recs 8, 9, 12; w2-02 recs 1, 4 (settings and a 14-day half-life, simulation only). Plans, not evidence. |
| 5 | Team: one committer in a "team of four", and no AI-literacy history in `seed-demo`. | recommended | [business plan](business-plan.md) rec 8 (name roles and commitment); [01](01-competition-fit.md) rec 5 (seed literacy history). |

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
| 1 | It teaches recognition, not what the exam rewards: every check is a 4-option MCQ, and level-marked answers wait in unbuilt step 07. | partly | Wave 2 counts the marks (about 66% level-marked, MCQ about 3%; w2-04-02 ✓) and proposes chain checks C1–C5 (w2-04 recs 2–3). [05](05-product-features.md) rec 7 gives an honest essay answer. Step 07 is not built. |
| 2 | It is easy to game. The correct option is a fragment and the distractors are full sentences. Distractors come from other points. Explain-backs can be pasted. | partly | [04](04-economics-education.md) rec 1 and [demo plan](demo-plan.md) rec 2 recommend option-form pack edits (not made). Pasted explain-backs are not addressed. |
| 3 | Content accuracy: every row is `draft`, one correction is already wrong (`externality_tax_eval_m1`), and there's no review step. | recommended | [04](04-economics-education.md) rec 2 corrects the row; rec 3 keeps new rows as drafts until a teacher signs off. No review queue or error rate yet. |
| 4 | No teacher view, and usage reports are off by default. | recommended | Wave 2 specifies a one-screen, k = 6 class view (w2-05t recs 1, 4, 6) and a labelled mock-up. Not built. |
| 5 | Doesn't fit lessons: no class focus topic or deadline, the chatbot will still write the 25-marker, and students can't use the demo chatbot. | partly | [05](05-product-features.md) rec 3 (route answer); [09](09-safety-ethics.md) rec 9 (light friction); w2-09 rec 4 ("your point first" before a draft). Class focus is Later. |

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
| 1 | Scoring contradicts coaching. Ask 2/4 counts as wrong in BKT, yet `ask_min_features = 2` treats it as good enough. Precise questions fail without a prompt ritual. Ignored tasks are scored 0 when they should be missing data. | recommended | [02](02-ai-literacy-assessment.md) recs 2 and 4. The wave-2 simulation backs `ask_min_features = 3`, not `correct_share = 0.5` (w2-02-03 ~), and ignored = missing (w2-02 recs 1–2). Synthetic students only; not on the branch yet. |
| 2 | Verify measures restating, not checking. The "opened" tick can't be observed. Ticks 2–4 can be met by repeating the chatbot's reply. The source is one the chatbot proposed. | partly | [02](02-ai-literacy-assessment.md) recs 5–6; w2-09 rec 2 (check a summary against the course notes, which the reply doesn't contain). The "opened" tick stays unobservable. |
| 3 | Items don't fit their triggers. `fabrication` fires even with `web_access`. `pushback_changed` fires when the student was right. Distractors carry absolute cues. One wrong click marks a misconception as "held". | partly | [02](02-ai-literacy-assessment.md) recs 3 and 7; w2-02h recs 1–4 rewrite fabrication and agreement points and split off misattribution. Two picks before "held" is later. |
| 4 | The assessed system writes its own evidence. The chatbot self-labels `conflict_flagged`, `pushback_changed` and `web_access`. | recommended | [02](02-ai-literacy-assessment.md) rec 8 (κ study); w2-02h recs 5–6 (treat `conflict_flagged` as a biased sample; a scripted audit of five failure modes). Not run. |
| 5 | The claim outruns the construct. Evidence comes only from rare `research` turns, and 05e still carries the withdrawn Khanmigo line. | partly | The narrow named construct is documented ([02](02-ai-literacy-assessment.md) recs 1, 9, 12). Removing the Khanmigo line ([09](09-safety-ethics.md) rec 11) is a recommendation; wave 2 adds homework moments (w2-09 recs 2–4), not built. |

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
| 1 | No lawful chatbot route for under-18s, so there is no processor chain for a DPIA. | partly | Wave 2 documents a school-managed route: Copilot Studio in a K-12 Microsoft 365 tenant (w2-05-03, -04 ✓; w2-05 rec 1). No DPA, no processor diagram, not tested. |
| 2 | The key works like a password: it sits in a URL, is stored in plaintext (`edux/learner.py`) and can't be rotated or revoked. Ids are name slugs. | recommended | [09](09-safety-ethics.md) recs 3, 4, 7 (hash, revoke/rotate, pseudonymous ids); w2-05 rec 3 (bearer header). None built: `edux/server.py` still reads only `?key=`. OAuth is later (w2-05 recs 8–9). |
| 3 | Every message reaches eduX word for word, with no route for a safeguarding disclosure. | recommended | [09](09-safety-ethics.md) recs 8 (wellbeing signpost) and 10 (DSL contact at setup). Not built. The alert route is later (rec 14). |
| 4 | No retention period, no erasure and no subject-access export. | recommended | [09](09-safety-ethics.md) recs 5–6 (`delete-student`, `export-student`, a written retention default). Not built. |
| 5 | Profiling of minors. `text/style.md`'s "use what you already know about the student" pulls in vendor memory. AI-literacy levels in a teacher view must be off by default. | partly | The teacher-view rule is decided (coordinator decision above; w2-05t spec). Deleting the `style.md` line ([09](09-safety-ethics.md) rec 1) is recommended; the line is still on `main`. |

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
| 1 | I ask a question and get a quiz, and the same question is re-asked. | partly | [05](05-product-features.md) ("answer first when rushed") and [09](09-safety-ethics.md) rec 9. Wave 2 adds a within-session re-ask (w2-03 rec 3), which brings the complaint back (see wave-2 student #1). |
| 2 | I'd never see the AI-literacy part: only research questions trigger it, and homework never does. | recommended | w2-09 recs 2–4 add homework moments (`summarise`, `ai_output_pasted`, `draft`). Not built. |
| 3 | The MCQs are easy to game. The short option is the right one. "Yeah I checked" makes Verify secure. An ignored task scores 0. | recommended | [04](04-economics-education.md) rec 1, [02](02-ai-literacy-assessment.md) recs 3, 4, 6; w2-02 rec 1 (`ail_unprompted` guess 0.20). All S, none made. |
| 4 | It feels like being watched ("answers drop after 35 minutes", my just-show-me share). | partly | "Decide" stays unscored; teacher reports off by default; per-student levels and draft counts never shown (coordinator decision). w2-05t rec 2 tells students what the teacher sees (not built). |
| 5 | It doesn't help with 15- and 25-mark essays. | recommended | w2-04 proposes chain checks C1–C5 and a plan-skeleton step (recs 2, 3, 9). Step 07 is not built. |

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
| 1 | This is a revision tutor, not an AI-literacy entry. | partly | 05e is built on its branch, not merged. [01](01-competition-fit.md) rec 2 and [demo plan](demo-plan.md) recs 1, 4 (merge; a 72-s literacy episode) are not filmed. |
| 2 | Where is your definition? | answered | [02](02-ai-literacy-assessment.md) rec 1 and [01](01-competition-fit.md) recs 3–4 (definition, rubric and crosswalk, documented). |
| 3 | Why believe a "secure" Verify? Self-report, unvalidated labels, and 11–16% of students without the skill end "secure" under label noise. | partly | [02](02-ai-literacy-assessment.md) recs 5, 6, 8, 9, 12; [demo plan](demo-plan.md) rec 10; w2-02 recs 1, 7 (settings and a minimum-moments rule, simulation only). Nothing changed on the branch. |
| 4 | Your students can't legally use the chatbot you filmed. | partly | [05](05-product-features.md) recs 1–2 and [demo plan](demo-plan.md) rec 3 (works-with line, adult-account caption) are wording. The K-12 Copilot route is documented, not tested (w2-05). |
| 5 | Your assessment gives the answer away (the correct option differs in form). | recommended | [04](04-economics-education.md) rec 1, [02](02-ai-literacy-assessment.md) rec 3 and [demo plan](demo-plan.md) rec 2 (pack edits, S). Not made; needs an owner on Wednesday. |

**Q&A, with the answer wanted:**
1. *Define AI literacy in one sentence.* "Knowing when and how far to trust a chatbot, shown in what students do when it is wrong."
2. *How do you know a student actually checked?* "We don't see clicks. Verify is self-report and graded lower. Only How AI works is scored by the server. Here is our plan to measure agreement with a teacher."
3. *What does a teacher see?* Class-level skill levels and the most common misconceptions, never chats. Show a mock-up and label it as one.
4. *Which school could use this on Monday?* "Over-18s and teachers today. Microsoft schools through Copilot Studio next. OAuth is our next build."
5. *Why not a 20-question test?* "Tests measure what students say about AI. We assess what they do with it while they work. GLAT or AILIT-S is how we'd validate it."

### Wave 1 at a glance

Re-checked against the wave-2 key, the 30 objections stand at 1 answered (judges #2, the definition), 12 recommended, 16 partly and 1 open (investor #2, the moat, now weaker). Student #5 (essays) moved from open to recommended because w2-04 proposes concrete chain checks. Three themes recur:

- **Under-18 access.** Raised by the investor, teacher, DPO, student and judges. Wave 2 found one documented school route (Copilot Studio, K-12 tenant), still untested.
- **Gameable or weak literacy evidence.** Raised by the teacher, researcher, student and judges. The fixes are small settings and pack edits. None is made yet.
- **No teacher view.** Raised by the teacher and judges. Wave 2 specified one, and the coordinator settled what it shows.

---

## Wave 2

Sources: w2-02, w2-02h, w2-03, w2-04, w2-05, w2-05t, w2-08, w2-09 and verifier sets E–H and J (no ✗ marks). Two personas per panel file (`work/w2/panel-*.md`). Where a coordinator decision settles part of an objection, the status says so.

### Investor (UK/EU edtech seed)

**Verdict:** Still no, and wave 2 made it worse. The best-funded host now tracks progress and is out of reach. The one school route makes the school pay Microsoft several times our licence. The AI Act compliance buyer has gone.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | The cost story contradicts itself. The business plan defends £8 with "no model calls", but on Copilot Studio the school pays about US$84 per student per year in credits (our estimate, on an unopened US$0.01 rate; w2-05-06 ~). Whether an MCP call bills as an agent action is unconfirmed. At 125% enforcement, agents stop mid-term. | partly | w2-05 recs 5 and 10 flag it and ask Microsoft. Business plan §3 still claims a cost advantage. |
| 2 | The market has shrunk to one channel. Google schools are out and get tracking free (w2-08-01, -02 ✓). ChatGPT and Claude have no under-18 route. Le Chat is a consumer account. Microsoft K-12 tenants must switch Copilot on for 13–17s, and it is off by default (w2-05-04 ✓). | partly | w2-05 recs 1, 2, 4 and w2-08 rec 3: wording plus an adult test. |
| 3 | Both moats are weaker. Gemini ends the "one conversation" line. EU AI Act Article 4 needs no measurement or certificate (w2-08-09 ✓), so the compliance buyer is gone. | partly | w2-08 recs 1, 2, 7 give honest "head start" wording. No buyer. |
| 4 | Funded rivals sit inside the programme. The Pioneer Programme gave £300k each to eight suppliers, including Pearson, Eedi and Google (w2-08-08 ✓). It targets Years 9–10, not A level. | partly | w2-08 rec 6 (text only). |
| 5 | The price is unanchored. £8 is three to four times our estimate of what a large trust pays per pupil for Sparx Maths (about £1.80–2.80, a lower bound). | partly | w2-08 rec 4 adds a trust tier, with no figure. |

**Q&A, with the answer wanted:**
1. *What does a school pay in total per student on Copilot?* "£X licence plus Microsoft's confirmed £Y; here's the email."
2. *Google gives this free in Classroom. Why switch?* "We don't sell to Google schools. Our market is N% of sixth forms."
3. *Who pays for AI-literacy evidence now that Article 4 needs no certificate?* A named school or trust that said yes.
4. *Pearson has £300k and the specification. Why you?* Our cost and time per pack, and host-neutrality.
5. *Is the Copilot route tested?* "Yes, on [date], a 17-year-old on tenant X." Anything else counts as a no.

### DPO (multi-academy trust)

**Verdict:** Not approvable yet, but closer. Copilot gives a contract chain that works on paper. The teacher view is the first design she could sign off. Every safety control is still a plan, not code.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Le Chat can't go in any DPIA. It is a consumer contract for personal use, with parental permission "where required" and no school controller (w2-05-01 ~). Putting it on a pupil-facing slide invites families to sign up outside the school's contract. | open | w2-05 rec 2 puts it on the slide. The fix wanted: drop it as an under-18 route, or say "adults only". |
| 2 | Copilot: who processes what, under which contract? Messages leave Microsoft through a connector to eduX. Do Microsoft's 13–17 protections (w2-05-13 ✓) cover custom agents and third-party MCP? | partly | w2-05 rec 1; business plan rec 9 (DPIA template). No processor diagram or DPA. |
| 3 | The child still holds a long-lived secret. A bearer header beats a URL, but a 16-year-old still pastes a password-equivalent into Copilot until Entra sign-in. Keeping `?key=` for ChatGPT goes against RFC 6750 (w2-05-10 ✓). | recommended | w2-05 recs 3 and 8; [09](09-safety-ethics.md) recs 3–4. None built. |
| 4 | Teacher view: minimisation, not anonymity. k = 6, bands and the "never anonymous" wording are good, but class AI-literacy aggregates need a lawful basis and pupils must be told. The new `offered_misconception_ids` log must be shown to be necessary. | partly | w2-05t recs 2, 5, 6; the coordinator decision (opt-in, bands, k ≥ 6). No privacy-notice line or retention period for the new column. |
| 5 | Wave-1 fixes are unbuilt. Delete, export, retention and the DSL route were marked "answered", but the code has none of them. | recommended | [09](09-safety-ethics.md) recs 5, 6, 8, 10. Wave-1 statuses corrected above. |

**Q&A, with the answer wanted:**
1. *On Copilot, who is our processor?* "eduX, under your DPA; Microsoft under your existing M365 terms."
2. *Does Microsoft's teen safety cover your agent?* "Tested: yes or no, and here's how."
3. *Can a teacher identify a pupil from a band?* "Counts of 5 or fewer are never shown. Shares are banded, and 'all' is never shown."
4. *Why mention Le Chat to 16-year-olds?* "We don't. It's adults only."
5. *How long is `offered_misconception_ids` kept?* A number and a deletion job.

### EduX judges (Challenge 1)

**Verdict:** Would shortlist it if the Wednesday plan lands, but not as a winner. The plan turns a revision tutor into an AI-literacy entry, but its centrepiece demo teaches a "misconception" that is often true. Re-scores (1–5; criteria inferred from the rules page, brief not yet pasted), w1 → Wednesday plan → plus wave-2 S recs: problem fit 2 → 3 → 4; definition 4 → 4; prototype on video 2 → 3 → 3; educational value 3 → 3 → 4; who it helps 2 → 3 → 3; how it works in practice 3 → 3 → 4.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Your demo corrects a true belief. Shot 4c marks "searched a source database and picked the wrong entry" as wrong. With search on, about 25–30% of citations or statements aren't backed by their source (w2-02-33 ~, -34 ✓). | recommended | w2-02h recs 1–2; coordinator decision (search off for the video, m2 not taught). Storyboard shots 4c–4d and the seed are not yet rewritten. |
| 2 | "Why not Gemini?" Study notebooks track objectives across sessions, and Classroom gives teachers progress insights, piloted in UK schools (w2-08-01, -02 ✓). | partly | w2-08 recs 1–3; coordinator fact (lead with AI-literacy evidence plus a school-owned model across chatbots). The deck doesn't use it yet. |
| 3 | Only the student sees the assessment. The teacher-view mock shows no AI-literacy levels. | recommended | w2-05t recs 1, 6; coordinator decision allows one opt-in, banded, k ≥ 6 class row per skill. Not in the mock yet. |
| 4 | Cost contradicts the pitch. On the only school-managed under-18 route, the school pays about US$0.07 a turn and about US$84 per student per year (our estimates, ~). | partly | w2-05 rec 5 (business plan only, not the pitch). |
| 5 | How much of the 2:30 is real? Teacher view, C1/C3 items and some shots are mock-ups. | partly | [demo plan](demo-plan.md) rec 1 (cap mocks at about 15 s, labelled; Plan B if the gate fails). |

**Q&A, with the answer wanted:**
1. *Is "picked the wrong entry" wrong?* "Sometimes it's right. We teach that a cited source may not exist or may not say what was claimed. Which applies depends on whether it searched."
2. *Gemini tracks progress. Why you?* "Inside Google only, with no AI-literacy evidence. We serve other schools and measure Ask and Verify from real use."
3. *What does a teacher do with AI-literacy data?* "Class bands, groups of 6 or more, only if the school opts in. Never individuals."
4. *Your MCQs are 3% of the marks.* "Yes. They're the diagnostic way in. Chain and evaluation checks come next (w2-04), shown as a mock."
5. *Which 17-year-old, at what cost?* "A K-12 Copilot Studio agent, about 7 credits a turn; documented, piloting next."

### AI-literacy researcher (measurement)

**Verdict:** Stronger as teaching, and more honest about its triggers. Still not an assessment whose scores she'd interpret, because every trigger is a label the chatbot assigns to itself.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | The triggers are a biased sample. `web_access` records a capability, not an action; models falsely claim tool use (w2-02-43 ✓). `conflict_flagged` under-fires on confident errors (w2-02-41 ✓, -42 ~). Opportunities differ by host. | partly | w2-02h recs 3 and 6 (a deployment-level `searched` setting; a scripted audit), both "maybe" before Thursday. No per-host opportunity rates. |
| 2 | New moments add more self-labels. `summarise`, `ai_output_pasted` and `draft` are classified by the chatbot. Summarise does check against our notes, which answers wave-1 "Verify measures restating". | partly | w2-09 recs 2–4; include the new labels in the w2-02h rec 6 audit before scoring them. |
| 3 | Mixed bases and self-report in the motivation. The 52% weekly figure is a share of AI users (w2-09-01 ~). The deck calls self-report weak, then motivates the problem with self-reported checking. | open | Fix wanted: lead with Ofcom's performance result (a quarter of confident teens failed; w2-09-04 ✓) and give each NLT base. |
| 4 | Bastani is used beyond its reach. It is Turkish high-school maths. The guarded tutor caused no harm and no gain. The "about −0.2 SD" figure is our calculation. | partly | w2-09 rec 1 wording; use it only for "guarded beats unguarded". |
| 5 | Missing data and evidence counts aren't changed. Ignored task = 0 is still on the branch. A 3-moment minimum (our choice) is low against the 8–12 that w1-02-31 ✓ suggests. | recommended | w2-02 recs 2, 7 and w2-09 rec 5 (S, unbuilt); NAEP and PISA not-reached handling backs ignored = missing (w2-02-11, -12 ~). |

**Q&A, with the answer wanted:**
1. *Your fabrication point: true with search on?* "We've rewritten it so it's true either way, and we're splitting misattribution off as its own part."
2. *If the chatbot changes its answer, was the student right?* "We don't judge that. The item teaches that a change doesn't show which answer is right (w2-02-38 ✓)."
3. *How often does each host fail to trigger a check?* "Here's our scripted audit, per host."
4. *Does a non-user score low?* "No. Missing isn't zero, and below N moments we show 'not enough evidence'."
5. *External validity?* "AILIT-S or GLAT for How AI works, and a civic-online-reasoning task for Verify, in a preregistered pilot."

Wording problems she flagged: w2-09 rec 8 says "stealth", which pitch-notes bans; ASSISTments g = 0.18 (w2-05-20 ~) rests on secondary sources and measures a bundle.

### Teacher (Head of Economics, state sixth form)

**Verdict:** Closer, not yet. The marks are counted honestly, but everything aimed at the levelled two-thirds is a mock-up or a later.md entry. Would trial it in Year 12 for diagnosis if the teacher screen works for a set of 14.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | The tally proves my point, and the build hasn't moved. About 66% of marks are level-marked and MCQ is about 3% (w2-04-02 ✓). The levelled side gets a pitch line, a mock-up and a doc edit; `ask_mcq` has no stem field. | partly | w2-04 recs 1–3. Wanted: one working C1 item, or the pitch saying "diagnostic only today". |
| 2 | The worked examples would penalise my best students. C1 runs care-worker minimum wages through the competitive model, not monopsony. C4 keys a sentence as "extends" when it can weigh. | partly | Wave-1 [04](04-economics-education.md) rec 3 keeps rows draft until sign-off. No rule yet for C4/C5 keys or an "also defensible" option. |
| 3 | Selection still counts towards mastery. C3 never makes anyone draw; C2 ordering transfers weakly; selection overstates production (w2-04-14 ~). | recommended | w2-04 rec 6 (selection at half weight, our choice; never "ready for levelled"). Not before Thursday. |
| 4 | The teacher screen is blind at my class size. In simulation (k = 6, 40% share), a set of 12 where half the class holds a misconception flags in 5% of class-weeks when half do checks and 33% when 80% do. I also need to know who isn't doing it. | partly | Coordinator decision allows per-student completion as a school opt-in, default off. Pooling across sets is still open. |
| 5 | The draft moment still writes the 25-marker, and w2-09 sent draft counts to the teacher while the w2-05t mock said they weren't shown. | partly | Coordinator decision: draft and offloading counts are never in the teacher view. The draft moment still ends in prose, not a plan skeleton (w2-04 rec 9 is later). |

**Q&A, with the answer wanted:**
1. *Show me a C1 item running.* Live, or "mock-up; stem field in step 07".
2. *Who signs off a keyed evaluation sentence?* A named teacher, a queue and a "contestable" flag.
3. *What does self-marking teach about levels?* "A checklist for 4- and 8-markers only, never on 25-markers."
4. *What will I see for my set of 14 this term?* Expected flags.
5. *Why will contrasting cases work here?* d = .50 across 57 experiments (cross-field; w2-03-01 ~), and the confusable pairs actually in the pack.

### Student (Year 13, Edexcel Economics, uses ChatGPT)

**Verdict:** Better. The chain and "which sentence evaluates" work is what he needs. But he still can't log in, and half the new things add steps at 10pm.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | You're bringing back the re-asked question: "relearn in session" re-asks a missed part up to twice (w2-03 rec 3). | partly | w2-03 rec 3 uses fresh distractors, a gap of at least one exchange and never when fatigued. Skipping and saying why aren't covered. |
| 2 | "Check the summary against your notes" means eduX's notes, not mine. I summarise BBC articles and my teacher's slides (45.5% of monthly users aged 16–18 summarise; w2-09-01 ~). | partly | w2-09 rec 2 defines the trigger but not the off-course case. Wanted: fire only on course material, otherwise "check one line against the original". |
| 3 | Why would I ever say "ChatGPT said…" if owning up gets me a task? And a count of my "write it for me" requests was going to my teacher. | partly | Coordinator decision: draft counts are never shown per student (w2-05t rec 2 says so in the progress text). Not decided: pasted text never penalised and optional to check. |
| 4 | Self-marking: I'll tick everything, and it costs a turn. | partly | w2-03 rec 2 (once per session, not when fatigued). Wanted: skippable, and showing where I disagreed with the marking. |
| 5 | I still can't use it. I'm 17, Claude is 18+, my school is on Google, and Le Chat needs a parent's permission and is untested. | open | Wording only (w2-05 recs 1–2). Wanted: one tested school route, named. |

**Q&A, with the answer wanted:**
1. *Can I skip the re-ask?* "Yes, one tap, and you'll still see it on a later day."
2. *Can I send a photo of my diagram?* "Yes, the chatbot can read it and check which curve moved; we're testing whether that's reliable."
3. *Does my teacher see that I asked it to write my essay?* "No. Never per student. Here's the sentence in your progress page."
4. *Will the missing-link questions be in the app before my mocks?* An honest date.
5. *58.5% say they check AI. Do you believe that?* "No. It's self-report, which is why we watch what students do."

### Wave 2 at a glance

Of 30 objections, 0 are answered, 6 recommended, 21 partly and 3 open (DPO #1, Le Chat on a pupil slide; researcher #3, self-report and mixed bases in the motivation; student #5, no tested route). Coordinator decisions move four objections up a step from the panel's own rating (judges #1 and #3, teacher #5, student #3). Themes:

- **One school route, untested and costly.** Raised by the investor, DPO, judges and student. Copilot Studio in a K-12 tenant is documented; credit cost and teen protections for custom agents are unconfirmed.
- **The moat is gone; lead with AI-literacy evidence.** Raised by the investor and judges.
- **Self-labels and self-report.** Raised by the researcher and judges. Each new moment adds a chatbot-assigned label.
- **Nothing is built.** Raised by the DPO, teacher and researcher. Wave-1 and wave-2 fixes are plans.

---

## Open questions for wave 3

Merged and deduplicated from the six wave-2 personas (20 questions, 19 after merging). Tags: [I] investor, [D] DPO, [J] judges, [R] researcher, [T] teacher, [S] student. Wave-2 questions are in [README.md](README.md#open-questions).

**Routes, cost and contracts**

1. [I] How many English sixth forms and colleges run Microsoft 365 A3/A5 with learner Copilot enabled for 13–17s?
2. [I, J] Does an MCP tool call in Copilot Studio bill as an agent action, and does an Agent Builder agent avoid it?
3. [I] Have Gemini study notebooks reached UK under-18 school accounts?
4. [D] Do Microsoft's 13–17 Copilot protections (MC1509805) apply to Copilot Studio custom agents and their MCP tools?
5. [D] Is there a DfE or ICO template DPA for an MCP plug-in behind a school's Microsoft 365 tenant?
6. [D] What lawful basis do UK schools use for pupil-level analytics shared with teachers? The coordinator decision narrows this to opt-in per-student *completion* only, plus banded class-level AI literacy (k ≥ 6). Levels, AI-literacy scores, offloading and draft counts are never shown per student.

**Market**

7. [I] Do any trusts or awarding bodies buy AI-literacy assessment, and at what price?
8. [J] What do the brief's Desired Outcomes say about who uses the assessment? (The team must paste the brief into the repo on Wednesday.)

**AI-literacy measurement**

9. [J] How often does claude.ai with search on misattribute citations on UK economic data?
10. [R] What is per-host agreement between `source_conflict` / `pushback_changed` and a script, across the five scripted failure modes?
11. [R] How many literacy moments does a typical student generate per week, per host?
12. [R] Do NLT's checking items have a published base and wording that allow the 58.5% to be quoted correctly?
13. [S] Do 16–18s disclose pasted AI text less when disclosing it triggers a task?

**Economics content and checks**

14. [T] Across past 9EC0 8- and 12-markers, how often would a monopsony or "depends on elasticity" answer conflict with a C1 or C4 key?
15. [T] Do faded-chain tasks raise blind-levelled analysis marks on economics essays?
16. [T] How long does reviewing one C4 item take, and how often is its key disputed?
17. [S] Can chatbot image input reliably label a photographed diagram's shift and direction for server scoring?

**Teacher view and student experience**

18. [T] What flag rate does the alarm rule give if pooled across 2–4 sets of 10–16 students?
19. [S] Does a skippable within-session re-ask keep accuracy gains without cutting return use?
