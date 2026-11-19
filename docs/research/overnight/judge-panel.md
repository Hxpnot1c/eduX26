# Judge panel (red team)

Each wave, six personas attack eduX: investor, teacher, AI-literacy researcher, DPO, student and EduX judges. They work from that wave's scout notes and verifier marks. This file condenses their verdicts and objections and says whether each objection is answered yet.

**Status key (from wave 2, applied to all waves).**
- *answered*: a fix is built, or a document answers the objection.
- *recommended*: we recommend a fix, but it isn't built.
- *partly*: part of the objection is met (by a document, a built piece or a recommendation), part is not.
- *open*: nothing addresses it.
- *recommended (tested diff ready)*: added in wave 4. A patch in `sims/fixes/combined/` (0001–0005, on the 05e export) fixes the objection and was tested by simulation or scripted turns, with `check_mcp` 74/74 after each step (w4-fix-combined-1 ✓). It isn't merged or built, so it is not *answered*. Where a tested diff covers only part of an objection, the status is unchanged and the row carries a "Wave 4:" note. Wave 5 extends the series with 0006–0010 (stuck ladder and review requests, labelling text, Ask guard, broken-link counter, show-then-answer counter); the whole series 0001–0010 applies with offsets only and passes `check_mcp` 74/74 at every step (w5-fix-combined-2 ✓). The same rule applies, with "Wave 5:" notes.
- *recommended (tested diff ready, verified)*: added in wave 6 for the gaming objections. The wave-6 diffs (0009b, 0010b, 0011) stop the cheap strategy the objection names in simulation, and a blind verifier reran those numbers on fresh trees (verifiers U and V, all ✓). Nothing is merged, so it is still not *answered*. Unlike the wave-4 rule, a row gets this status when the diffs cover its main exploit; the residuals no diff covers are named in the row's "Wave 6:" note.

"05 rec 6" means rank 6 in that report's Ranked recommendations. "w2-05 rec 3" means rank 3 in that wave-2 scout note, and "w3-07 rec 5" the same for a wave-3 note. Rows marked "Wave 3:", "Wave 4:" or "Wave 5:" were refreshed after that wave. "Patch 0003" means `sims/fixes/combined/0003-…diff`.

**Coordinator facts.**
- Step 05e (Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and not merged. Scout notes that say "not built" are stale.
- As of wave 2, none of the wave-1 code fixes is built on `main`. `edux/server.py` still reads only `?key=` (no bearer header). Delete, export, retention, key hashing and revocation, and the DSL route are plans. The `text/style.md` line "use what you already know about the student" is still on `main`.
- Per-student data for teachers (wave-2 decision): per-student *completion* (did checks or didn't, this week) may be a school opt-in, default off, as in Sparx. Per-student *levels*, AI-literacy scores, offloading and draft counts are never shown per student. Class-level AI literacy is shown only in bands, for groups of at least 6, and only if the school opts in. This removes draft and offloading counts from the teacher view and settles the w2-09 rec 4 vs w2-05t conflict.
- For the video, web search is off, and "searched a database and picked the wrong entry" is not taught as a misconception (with search on it is often true; w2-02h).
- As of wave 3 (code checked on 18 November), `main` and `build/06-demo` still read only `?key=` in `edux/server.py`. Neither branch has `delete-student`, `export-student`, key hashing or a bearer header. No wave-3 fix is built.

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
| 2 | It is easy to game. The correct option is a fragment and the distractors are full sentences. Distractors come from other points. Explain-backs can be pasted. | recommended (tested diff ready, verified) | [04](04-economics-education.md) rec 1 and [demo plan](demo-plan.md) rec 2 recommend option-form pack edits (not made). Pasted explain-backs are not addressed. Wave 3: worse than thought. The correct option is the longest in 7 of 9 parts (w3-05-08 ~). w3-05 rec 1 (an exemplar as the key) is unbuilt. Wave 4: the option-form fix is a tested diff (patch 0004; w4-fix-mcq-1 ✓). Pasted explain-backs are still not addressed. Wave 5: a gaming simulation found a new cue after 0004: dropping the longest and shortest options gets 58% of MCQs right against about 31% chance (w5-06g-05 ~; not fixed, later pack work). Patch 0010 stops "just show me, then match" reaching secure (9 → 0 parts) at a real cost to honest students (w5-fix-counter-c1 ~). Pasted explain-backs are still not addressed, so the status stays. Wave 6: 0011 spreads the key's length rank, so the middle-length guess falls from 0.536 to 0.286 on the option sets (chance 0.312) and from 4.4 to 0.2 false-secure parts in play (w6-len-3 ✓, w6-len-4 ✓). 0010b stops "show me, then pick" reaching secure (9 → 0) at a small honest cost (3.6 → 3.4 parts; w6-c1b-1 ✓, w6-c1b-2 ✓). 0009b's text line tells the chatbot not to tick a pasted repeat of its reply. Residuals: the sequence cue (point-2/3 keys are the one new option; 100% on 11 sets), and pasted explain-backs still reach secure under a literal labeller (C3x 9.0, C4 3.8 parts; 0 under a skeptical one). |
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
| 1 | Scoring contradicts coaching. Ask 2/4 counts as wrong in BKT, yet `ask_min_features = 2` treats it as good enough. Precise questions fail without a prompt ritual. Ignored tasks are scored 0 when they should be missing data. | recommended | [02](02-ai-literacy-assessment.md) recs 2 and 4. The wave-2 simulation backs `ask_min_features = 3`, not `correct_share = 0.5` (w2-02-03 ~), and ignored = missing (w2-02 recs 1–2). Synthetic students only; not on the branch yet. Wave 4: ignored = missing is a tested diff for literacy tasks and checks (patch 0003; w4-fix-verify-1 ✓). The Ask thresholds are unchanged, so the status stays. |
| 2 | Verify measures restating, not checking. The "opened" tick can't be observed. Ticks 2–4 can be met by repeating the chatbot's reply. The source is one the chatbot proposed. | partly | [02](02-ai-literacy-assessment.md) recs 5–6; w2-09 rec 2 (check a summary against the course notes, which the reply doesn't contain). The "opened" tick stays unobservable. Wave 5: restating the reply makes Verify secure under a literal labeller and never under a skeptical one (w5-06g-06 ~). The text line that models the skeptical labeller ("tick only what the student found on the source itself") is in neither 0007 nor 0009. No status change. Wave 6: that line is now in 0009b (never tick what only repeats the chatbot's reply, a point it just showed, or its citation). Copying the citation's publisher and date (L1d) now reaches Verify secure in 0% of runs under both labellers (w6-c2b-1 ✓). The "opened" tick is still unobservable, and how a real chatbot follows the line is untested, so the status stays *partly*. |
| 3 | Items don't fit their triggers. `fabrication` fires even with `web_access`. `pushback_changed` fires when the student was right. Distractors carry absolute cues. One wrong click marks a misconception as "held". | partly | [02](02-ai-literacy-assessment.md) recs 3 and 7; w2-02h recs 1–4 rewrite fabrication and agreement points and split off misattribution. Two picks before "held" is later. |
| 4 | The assessed system writes its own evidence. The chatbot self-labels `conflict_flagged`, `pushback_changed` and `web_access`. | recommended | [02](02-ai-literacy-assessment.md) rec 8 (κ study); w2-02h recs 5–6 (treat `conflict_flagged` as a biased sample; a scripted audit of five failure modes). Not run. Wave 5: patch 0007 rewrites the label definitions and 0008 stops a mislabelled answer writing Ask 0 (w5-fix-labels-1 ✓, w5-fix-guard-1 ✓). The w5-02s label dry run is Claude vs Claude, not agreement evidence (w5-02s-03 ~). No real-chatbot label rate is measured, so the status stays. |
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
| 1 | No lawful chatbot route for under-18s, so there is no processor chain for a DPIA. | partly | Wave 2 documents a school-managed route: Copilot Studio in a K-12 Microsoft 365 tenant (w2-05-03, -04 ✓; w2-05 rec 1). No DPA, no processor diagram, not tested. Wave 3: the school's lawful basis is public task (w3-09-01 ✓), and w3-09 gives an Art 28 checklist (the ICO lists 8 compulsory terms; w3-09-04 ~). Still no signed DPA and no test. |
| 2 | The key works like a password: it sits in a URL, is stored in plaintext (`edux/learner.py`) and can't be rotated or revoked. Ids are name slugs. | recommended | [09](09-safety-ethics.md) recs 3, 4, 7 (hash, revoke/rotate, pseudonymous ids); w2-05 rec 3 (bearer header). None built: `edux/server.py` still reads only `?key=`. OAuth is later (w2-05 recs 8–9). |
| 3 | Every message reaches eduX word for word, with no route for a safeguarding disclosure. | recommended | [09](09-safety-ethics.md) recs 8 (wellbeing signpost) and 10 (DSL contact at setup). Not built. The alert route is later (rec 14). |
| 4 | No retention period, no erasure and no subject-access export. | recommended | [09](09-safety-ethics.md) recs 5–6 (`delete-student`, `export-student`, a written retention default). Not built. Wave 3: w3-09 writes a retention schedule (end of course plus one term, our choice). Delete and export are still unbuilt. |
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
| 3 | The MCQs are easy to game. The short option is the right one. "Yeah I checked" makes Verify secure. An ignored task scores 0. | recommended (tested diff ready, verified) | [04](04-economics-education.md) rec 1, [02](02-ai-literacy-assessment.md) recs 3, 4, 6; w2-02 rec 1 (`ail_unprompted` guess 0.20). All S, none made. Wave 4: tested diffs cover the short-option cue (patch 0004; w4-fix-mcq-1 ✓) and ignored task = skip, not 0 (patch 0003; w4-fix-verify-1 ✓). "Yeah I checked" (self-report) is not addressed, so the status stays. Not merged. Wave 5: a bare "the link is broken" report made Verify secure for 100% of simulated gamers. Patch 0009 cuts that to 0% (honest 65% → 59%; w5-fix-counter-c2 ~). But plain "yeah I checked" self-report was not simulated, and a new middle-length MCQ cue gets 58% against 31% chance (w5-06g-05 ~), so the status stays. Wave 6: 0009b replaces 0009. "The link is broken" gamers go 100% → 0% Verify secure (held at developing), at an honest cost within noise (64% → 62%; w6-c2b-1 ✓, w6-c2b-2 ✓). 0011 removes the middle-length cue (57% → 19% right in play; w6-len-4 ✓). Residuals: plain "yeah I checked" is still not simulated, a student who has done one real check can then report dead links freely (L1c), and the sequence cue remains. |
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
| 3 | Why believe a "secure" Verify? Self-report, unvalidated labels, and 11–16% of students without the skill end "secure" under label noise. | partly | [02](02-ai-literacy-assessment.md) recs 5, 6, 8, 9, 12; [demo plan](demo-plan.md) rec 10; w2-02 recs 1, 7 (settings and a minimum-moments rule, simulation only). Nothing changed on the branch. Wave 3: reporting a dead link *lowers* Verify (w3-07-c5 ✓). Wave 4: a tested diff makes a reported dead page or mismatch raise Verify to .748 (developing) and makes an ignored task a skip (patch 0003; w4-fix-verify-1 ✓). It relies on the chatbot sending `source_conflict`. Self-report and label noise remain. Wave 5: patch 0009 stops a bare dead-link claim reaching secure (100% → 0% of simulated gamers; w5-fix-counter-c2 ~), and 0007/0008 tighten the labels (w5-fix-labels-1 ✓, w5-fix-guard-1 ✓). Label noise and self-report remain unmeasured on a real chatbot. Wave 6: 0009b replaces 0009. A report can't lift Verify to secure before one real check (gamers 100% → 0%), and all eight Plan A takes stay developing (0.740; w6-c2b-1 ✓, w6-planA ✓). Self-report and label noise remain, so the status stays *partly*. |
| 4 | Your students can't legally use the chatbot you filmed. | partly | [05](05-product-features.md) recs 1–2 and [demo plan](demo-plan.md) rec 3 (works-with line, adult-account caption) are wording. The K-12 Copilot route is documented, not tested (w2-05). |
| 5 | Your assessment gives the answer away (the correct option differs in form). | recommended (tested diff ready) | [04](04-economics-education.md) rec 1, [02](02-ai-literacy-assessment.md) rec 3 and [demo plan](demo-plan.md) rec 2 (pack edits, S). Not made; needs an owner on Wednesday. Wave 3: the correct option is the longest in 7 of 9 parts (w3-05-08 ~); w3-05 recs 1 and 4. Wave 4: patch 0004 (code plus pack) drops a testwise student who knows nothing from a 0.96 hit rate to 0.28 against chance 0.31 (w4-fix-mcq-1 ✓; simulation: synthetic students, example pack). The new pack rows need an economist's read. Not merged. |

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

Wave 3 changed no wave-1 status. It added evidence to five wave-1 rows (marked "Wave 3:").

---

## Wave 2

Sources: w2-02, w2-02h, w2-03, w2-04, w2-05, w2-05t, w2-08, w2-09 and verifier sets E–H and J (no ✗ marks). Two personas per panel file (`work/w2/panel-*.md`). Where a coordinator decision settles part of an objection, the status says so.

### Investor (UK/EU edtech seed)

**Verdict:** Still no, and wave 2 made it worse. The best-funded host now tracks progress and is out of reach. The one school route makes the school pay Microsoft several times our licence. The AI Act compliance buyer has gone.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | The cost story contradicts itself. The business plan defends £8 with "no model calls", but on Copilot Studio the school pays about US$84 per student per year in credits (our estimate, on an unopened US$0.01 rate; w2-05-06 ~). Whether an MCP call bills as an agent action is unconfirmed. At 125% enforcement, agents stop mid-term. | partly | w2-05 recs 5 and 10 flag it and ask Microsoft. Business plan §3 still claims a cost advantage. Wave 3: w3-08m recomputes the cost at about £22.50 per student per year (central), with a range of £11–108 (our estimate; w3-08m-13). It replaces US$84. Billing for unlicensed students is still contested (w3-08m-05 ~). |
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
| 2 | Copilot: who processes what, under which contract? Messages leave Microsoft through a connector to eduX. Do Microsoft's 13–17 protections (w2-05-13 ✓) cover custom agents and third-party MCP? | partly | w2-05 rec 1; business plan rec 9 (DPIA template). No processor diagram or DPA. Wave 3: w3-09 adds a DPIA outline and a roles line. Microsoft makes connector traffic the agent maker's responsibility (w3-09-05 ✓), and its Product Terms are still unread. |
| 3 | The child still holds a long-lived secret. A bearer header beats a URL, but a 16-year-old still pastes a password-equivalent into Copilot until Entra sign-in. Keeping `?key=` for ChatGPT goes against RFC 6750 (w2-05-10 ✓). | recommended | w2-05 recs 3 and 8; [09](09-safety-ethics.md) recs 3–4. None built. |
| 4 | Teacher view: minimisation, not anonymity. k = 6, bands and the "never anonymous" wording are good, but class AI-literacy aggregates need a lawful basis and pupils must be told. The new `offered_misconception_ids` log must be shown to be necessary. | partly | w2-05t recs 2, 5, 6; the coordinator decision (opt-in, bands, k ≥ 6). No privacy-notice line or retention period for the new column. Wave 3: w3-09 rec 8 rests class AI literacy on public task only if the school teaches AI literacy, recorded in its DPIA. Unbuilt. |
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
| 1 | Your demo corrects a true belief. Shot 4c marks "searched a source database and picked the wrong entry" as wrong. With search on, about 25–30% of citations or statements aren't backed by their source (w2-02-33 ~, -34 ✓). | recommended | w2-02h recs 1–2; coordinator decision (search off for the video, m2 not taught). Storyboard shots 4c–4d and the seed are not yet rewritten. Wave 3: m2 is still in all 26 fabrication option sets on the branch (w3-07-c7 ✓). |
| 2 | "Why not Gemini?" Study notebooks track objectives across sessions, and Classroom gives teachers progress insights, piloted in UK schools (w2-08-01, -02 ✓). | partly | w2-08 recs 1–3; coordinator fact (lead with AI-literacy evidence plus a school-owned model across chatbots). The deck doesn't use it yet. |
| 3 | Only the student sees the assessment. The teacher-view mock shows no AI-literacy levels. | recommended | w2-05t recs 1, 6; coordinator decision allows one opt-in, banded, k ≥ 6 class row per skill. Not in the mock yet. |
| 4 | Cost contradicts the pitch. On the only school-managed under-18 route, the school pays about US$0.07 a turn and about US$84 per student per year (our estimates, ~). | partly | w2-05 rec 5 (business plan only, not the pitch). Wave 3: about £22.50 per student per year (central), £11–108 (our estimate; w3-08m-13). |
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
| 3 | Mixed bases and self-report in the motivation. The 52% weekly figure is a share of AI users (w2-09-01 ~). The deck calls self-report weak, then motivates the problem with self-reported checking. | partly | Fix wanted: lead with Ofcom's performance result (a quarter of confident teens failed; w2-09-04 ✓) and give each NLT base. Wave 3 (open → partly): frame D now leads with that result (w3-01). The caption must say it was an AI-image test, not fact-checking (wave-3 judges #3). |
| 4 | Bastani is used beyond its reach. It is Turkish high-school maths. The guarded tutor caused no harm and no gain. The "about −0.2 SD" figure is our calculation. | partly | w2-09 rec 1 wording; use it only for "guarded beats unguarded". |
| 5 | Missing data and evidence counts aren't changed. Ignored task = 0 is still on the branch. A 3-moment minimum (our choice) is low against the 8–12 that w1-02-31 ✓ suggests. | recommended | w2-02 recs 2, 7 and w2-09 rec 5 (S, unbuilt); NAEP and PISA not-reached handling backs ignored = missing (w2-02-11, -12 ~). Wave 4: ignored = missing is a tested diff (patch 0003; w4-fix-verify-1 ✓). The minimum-moments rule is not, so the status stays. |

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

Of 30 objections, 0 are answered, 6 recommended, 22 partly and 2 open (DPO #1, Le Chat on a pupil slide; student #5, no tested route). At wave 2 the count was 21 partly and 3 open. Wave 3 moved researcher #3 from open to partly (frame D). Coordinator decisions move four objections up a step from the panel's own rating (judges #1 and #3, teacher #5, student #3). Themes:

- **One school route, untested and costly.** Raised by the investor, DPO, judges and student. Copilot Studio in a K-12 tenant is documented; credit cost and teen protections for custom agents are unconfirmed.
- **The moat is gone; lead with AI-literacy evidence.** Raised by the investor and judges.
- **Self-labels and self-report.** Raised by the researcher and judges. Each new moment adds a chatbot-assigned label.
- **Nothing is built.** Raised by the DPO, teacher and researcher. Wave-1 and wave-2 fixes are plans.

---

## Wave 3

Sources: w3-01, w3-02e, w3-05, w3-06, w3-07 (our Plan A rehearsal by simulation), w3-08c, w3-08m and w3-09, with verifier sets K–P. One finding is ✗ and not used: w3-02e-14 (preregistration templates). Two personas per panel file (`work/w3/panel-*.md`).
- Two of the panel files were written before verify-L, -O and -P came in, so they call w3-02e, w3-05 and w3-07 unverified. Their claims are cited here with the current marks: w3-07-c1 to -c7 (simulation: synthetic students, example pack), w3-05-08 ~ and w3-02e-04 ~.
- Some panel ratings are regraded to the status key. A fix that is only recommended is *recommended* even where a panel said "yes" or "no". This applies to teacher #2 and #3, researcher #2 and #4, student #2, investor #3 and DPO #5.

### EduX judges (Challenge 1)

**Verdict:** Shortlist, not winner. The video is choreographed around scoring that punishes the behaviour it assesses. Fix that, not the slides.

**Re-scores (1–5).** Criteria are inferred from the rules page; the brief is still not pasted. Each line runs from the wave-2 plan, to wave-3 "before Thursday: yes" recs only, to those recs plus the "maybe" build fixes:
- problem fit 4 → 4 → 4 (5 if the brief matches frame D);
- definition 4 → 4 → 4;
- prototype on video 3 → 3 (2 live at the expo) → 4;
- educational value 4 → 3 → 4;
- who it helps 3 → 3 → 3;
- how it works in practice 4 → 3 → 4.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Catching a fake link lowers Verify. A dead page ticks 2 of 4 points, so Verify falls from .30 to .14. Moving on also scores 0. A mismatch raises it to .748, but only with a rewritten option set (w3-07-c5 ✓). An assessment that penalises its target behaviour is invalid, not noisy. | recommended (tested diff ready, verified) | Filming workaround: the mismatch line, or no Verify record after a dead-page take ([demo plan](demo-plan.md); w3-07 recs 2, 5). The scoring fix (w3-07 rec 5, 02 rec 6) is unbuilt and marked "maybe". Wave 4 is redesigning Verify scoring. Wave 4: patch 0003 scores a found dead page or mismatch as 1, so Verify goes .30 → .748 (developing) instead of .14; an ignored task is a skip; a matched check is graded (a,c,d .636 vs a,b,c,d .748) (w4-fix-verify-1 ✓). Verify now ends developing in all six Plan A takes (w4-fix-combined-1 ✓). Relies on the `source_conflict` label. Not merged. Wave 5: with 0009 (broken-link counter), a bare dead-page report earns no Verify evidence, so five of the eight Plan A takes (final_ticks_ad, plan_now, then_ped, clean, clean_ticks_ad) end Verify new (0.300). Only final and recommended (a,c,d) end developing, at 0.636 not .748. 0007's a,d rule for dead links and 0009 pull against each other (w5-fix-counter-c2 ~). Use the "the page says 9.1%, not 11.1%" line, or skip 0009. Wave 6: resolved by 0009b, which replaces 0009. A found dead page or mismatch still scores 1 and is capped at developing until one real check. All eight takes, the dead-page and a,d-ticked lines included, end Verify developing at 0.740 (w6-planA ✓). Still relies on `source_conflict`. |
| 2 | The demo works only if we avoid ordinary words. On example-mini, "give", "link", "ONS", "first", "cost", "different" and "shows" each pull a course part into focus. "Give me sources" turns the episode into a PED quiz (w3-07-c3 ✓). The expo demo is unscripted. | recommended (tested diff ready) | w3-07 rec 1 (focus-safe lines) is a workaround. The fix, "literacy turns never set a course focus" (w3-07 rec 4), is unbuilt; wave 4 is working on it. Wave 4: patch 0002 (a research or other turn never sets the focus) cuts false focus from 15/43 to 3/43 (holdout 9/18 → 3/18), at the cost of right focus 16/21 → 14/21 (w4-fix-focus-1 ✓; scripted turns, example pack). The 3 residual cases need the resolver name-gate, which is not in the series. Not merged. |
| 3 | The slide-1 evidence doesn't match the claim. Ofcom tested spotting AI-made images, not checking a chatbot's claim. And "nobody can see the difference" applies to us too, because Verify is partly self-report on labels the chatbot assigns. | answered | w3-01 (frame D) flags both points. A caption reading "AI-made images" is recommended, not yet on the slide. The brief is still unpasted. Wave 4: [pitch script](pitch-script.md) (w4-01) always calls Ofcom an image test, says "a quarter of those confident", and drops "nobody can see the difference". The brief is still unpasted. |
| 4 | The record misreads. How AI works shows "new" straight after the lesson (w3-07-c7 ✓). In economics, a part answered right once reads below one answered wrong and never right after 8.5 days (w3-06-01 ✓). Pooled AUC against truth is 0.48–0.59 (w3-06-08 ✓; simulation: synthetic students, example pack). | recommended (tested diff ready) | w3-06 recs 1–2 (decay towards the prior, plus "not yet shown"); [demo plan](demo-plan.md) rec 13 (per-part counts). Unbuilt; the decay fix is in progress in wave 4. Wave 4: patch 0005 (decay towards the prior; Ask and Verify floor 0) lifts week-8 How AI works AUC (none vs strong) from 0.51/0.31 to 0.85/0.88 (MCAR/MNAR, ignored = missing), and talk-only drops from .763 to .300 (w4-fix-core-4 ✓; simulation: synthetic students, example pack; prediction, not learning). "New straight after the lesson" was not re-tested. Optional; merge by 15:30 or after filming. |
| 5 | The economics checks still give the answer away. In 7 of 9 parts the correct option is the node description (a topic label), and in 7 of 9 it is the longest option (w3-05-08 ~). | recommended (tested diff ready) | w3-05 rec 1 (an exemplar as the key) and rec 4 (three options). Unbuilt, "yes"; wave 4 is fixing it. Wave 4: patch 0004, 0.96 → 0.28 testwise hit rate against chance 0.31 (w4-fix-mcq-1 ✓). Not merged. |

**Q&A, with the answer wanted:**
1. *"Type 'give me sources on the cost of living'."* It stays on the literacy task, live.
2. *"A student reports a dead link. What happens to Verify?"* "It counts as checking."
3. *"Your κ: who wrote the messages and who labelled them?"* "We rewrote half of them, and Claude labelled. It's a screen, not validation. Our rule passes a chatbot with true κ .6 only 38–50% of the time (w3-02e-06 ✓)."
4. *"Why does an image test show this?"* "It shows that confidence isn't competence. It is not a fact-checking test."
5. *"Why does it say 'new' after the lesson?"* "One answer is thin evidence. Here's the count."

### Student (Year 13, Edexcel Economics, uses ChatGPT)

**Verdict:** Still no. He can't log in (he's 17 and his school uses Google), and most of wave 3 is about making the video look right. The accessibility fixes are the first changes aimed at him.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | My normal words break it. I type "give me sources" and "what's the cost of…" every day. You've banned those words from your own demo because they turn my question into an elasticity quiz (w3-07-c3 ✓). | recommended (tested diff ready) | w3-07 rec 4 is unbuilt and marked "maybe"; wave 4 is working on the focus fix. Wave 4: patch 0002, false focus 15/43 → 3/43 (w4-fix-focus-1 ✓). Not merged. |
| 2 | Being honest lowers my score. Reporting a dead link lowers Verify, and saying "ok" scores 0 (w3-07-c5 ✓). So I'll learn to type "yeah it matched". | recommended (tested diff ready) | w3-07 rec 5 and 02 rec 6 (unbuilt). Wave 4 is redesigning Verify scoring. Wave 4: patch 0003, a reported dead link now raises Verify to .748, and "ok" is a skip, not 0 (w4-fix-verify-1 ✓). Not merged. |
| 3 | "Shorter replies" doesn't reach the teaching. I ask for 50 words and the teaching step still says 80. | recommended | w3-05 rec 2 (S, "yes"), unbuilt. A student-chosen "plain words" option is w3-05 rec 3 (M, needs a migration). |
| 4 | The right answer sounds like the spec heading and is usually the longest, so I'd pick it without reading (w3-05-08 ~). | recommended (tested diff ready) | w3-05 recs 1 and 4, unbuilt; wave 4 is fixing it. Wave 4: patch 0004 (w4-fix-mcq-1 ✓). Not merged. |
| 5 | The levels feel random. Right once, and three days later it's "new" again. Chat with no check, and it says "secure" for months (14 exchanges give .763; w3-06-06 ~). After the lesson, How AI works still says "new". | recommended (tested diff ready) | w3-06 recs 1–3, unbuilt; the decay fix is in progress. Wave 4: patch 0005; talk-only reads .300 (new), not .763 (secure), at day 0 and day 90 (w4-fix-core-4 ✓). Not merged. |

**Q&A, with the answer wanted:**
1. *If I ask for sources on the cost of living, do I get quizzed on PED?* "No. Here it is."
2. *If I catch a fake link, does my score go up?* "Yes. Catching it is the skill."
3. *Who wrote your test messages?* "An AI drafted them and we rewrote half. The pilot uses real messages, including pasted text and screenshots."
4. *Does it time me?* "Never. Speed is never evidence" (w3-05 rec 7). That matters with 25% extra time.
5. *What do I log in with this term?* A named school route that has been tested.

He liked three things: no timers, "plain words" as his own choice (never inferred and never shown to the teacher), and three options instead of four.

### Teacher (Head of Economics, state sixth form)

**Verdict:** Not yet. The record misreads the pupils she worries about most: the honest checker and the fluent talker. She'd trial it in Year 12 once fix (b) and the Verify scoring are in.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | "Give me sources" turns into an indirect-tax lesson: OBR and IFS as sources, then a PED prerequisite MCQ (w3-07-c3 ✓). This is a classroom bug, and the demo's word ban hides it. | recommended (tested diff ready) | w3-07 rec 1 is a workaround; rec 4 is "maybe". Wave 4 is working on the focus fix. Wave 4: patch 0002 (w4-fix-focus-1 ✓). Not merged. |
| 2 | The record punishes honest checking and rewards chat. A dead page lowers Verify from .30 to .14, and moving on scores 0 (w3-07-c5 ✓). Fourteen talk-only exchanges reach .763 (w3-06-06 ~). An `untested` review is queued, but does it ever fire? | recommended (tested diff ready, verified) | Fix (b) (w3-06 rec 2) covers talk-only. w3-07 rec 5 is "maybe", and ignored = missing (02 rec 4) is unbuilt. None is built or tested. Wave 4: patch 0003 (dead page .14 → .748; ignored = skip; w4-fix-verify-1 ✓) and patch 0005 (talk-only .763 → .300; w4-fix-core-4 ✓). Whether the `untested` review fires was not checked. Not merged. Wave 5: under 0009 a bare dead-page report scores no evidence (neither .14 nor .748), so the dead-page part of this row depends on keeping or skipping 0009 (w5-fix-counter-c2 ~). Wave 6: 0009b replaces 0009; a dead-page report scores 1 and reads developing (0.740; w6-planA ✓). The talk-only part needs 0005, which is now optional, and the `untested` review was still not checked. |
| 3 | A prerequisite gets skipped where the calculation marks are. Six right answers on `ped_values` lift a never-answered `ped_formula` to .527 for good, so its prerequisite check never fires (w3-06-05 ✓). | recommended (tested diff ready) | w3-06 rec 2, unbuilt. Wave 4: patch 0005; a never-answered prerequisite reads .300 (new), not .440, and the next-day plan is a prerequisite check (w4-fix-core-4 ✓). Not merged. |
| 4 | The pilot's cost to her department isn't counted. Who rates 100 real messages, maps mock items to parts, writes the DPIA and the consent letters, and runs the think-alouds? January to March is mock marking. | open | w3-02e §2 logs her time (RQ6) but gives no hours per task. |
| 5 | The items still don't look like her subject. E07 turns "evaluate a pollution tax" into a 3-point checklist. The MCQ key is a topic label and is the longest option in 7 of 9 parts (w3-05-08 ~). "Shorter replies" sends two word caps. | partly | w3-05 recs 1, 2 (with 04 rec 1) cover the MCQ key and the cap. Nothing addresses E07 (drop it or mark it "illustrative"). Wave 4: the MCQ key is a tested diff (patch 0004; w4-fix-mcq-1 ✓). E07 and the double word cap are not addressed. |

**Q&A, with the answer wanted:**
1. *A pupil catches a fake link. Does the record go up?* "Yes. Here is the test."
2. *Can a pupil chat their way to secure?* "No. Nothing counts until it's answered right; until then it says 'not yet shown'."
3. *My student types "give me sources on inflation". What does it teach?* "Inflation, with ONS sources. Research turns never set a course focus. Built and tested."
4. *Which pupils, which term, who rates?* "Year 12, spring; the team rates; under 15 minutes a week for you."
5. *Does extra time matter?* "No. Nothing is timed, and a test keeps it so."

She liked "not yet shown" (it is how she talks to pupils), the "never say eduX raised grades" rule, and no timers. Between 16.6% and 25.5% of candidates have 25% extra time (w3-05-01 to -03).

### AI-literacy researcher (measurement)

**Verdict:** The best-specified agreement study she has seen from a student team, but agreement is not validity. As captured, the Verify rule penalises the behaviour it claims to measure. She'd back the protocol, not yet the scores.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Agreement would certify an invalid rule. Item V06 (page not found) is in the study. Bot and humans can agree perfectly on ticks a and d, which then *lower* Verify (w3-07-c5 ✓). Also, 3/4 and 4/4 score the same, because scoring is binary at .67. | partly | w3-07 rec 5 is "maybe"; 02 rec 5 is a redesign. Wave 4 is redesigning Verify scoring. Reporting the server's decision, not only the ticks, is not yet in the protocol. Wave 4: the scoring part is a tested diff: V06 ticks now raise Verify, and 3/4 vs 4/4 on a matched check differ (.636 vs .748) (patch 0003; w4-fix-verify-1 ✓). Reporting the server's decision in the protocol is still not done. |
| 2 | The study skips the self-labels that wave 2 attacked. `conflict_flagged` and `pushback_changed` are dropped, and `source_conflict` is descriptive only, with 2 positives (w2-02-41 ✓). | recommended | 02 rec 19 (scripted audit with per-host trigger rates), unbuilt. w3-02e doesn't cover it. Wave 5: 0007 defines `source_conflict` (a different figure counts) and 0009 logs a bare report with `source_conflict` but scores it as no evidence. No per-host trigger rate yet (see open question 31). |
| 3 | The study is too weak to show much. The pass rule passes a κ = .6 chatbot only 38–50% of the time (w3-02e-06 ✓). Verify rests on 8 message clusters, which is too few for a stable cluster bootstrap. The items are Claude-drafted and tested on Claude. | partly | w3-02e recs 1–5 (call it "screening", rewrite half the messages, fix the pass rule in advance). Cold-written Verify items and a second host are not planned. Wave 5: the analysis script (`sims/agreement/analyse.py`) runs end to end (w5-02s-01 ~). The dry run is Claude vs Claude, not agreement evidence, and found 29 of 33 disagreements came from ambiguous definitions (w5-02s-03 ~). Most of those are clarified by patch 0007. No human or second-host run yet, so the status stays. |
| 4 | The decay asymmetry may explain why How AI works ranks backwards (AUC .40 on the branch). Fix (c) raises economics AUC from 0.48–0.59 to 0.62–0.71, but it redefines p (w3-06-08 ✓; simulation: synthetic students, example pack). Spacing hides the asymmetry only within about 30 days of the exam, not 14 (w3-06-02 ~). | recommended (tested diff ready) | w3-06 rec 7 (re-run the literacy AUC under the fix), "maybe". Wave 4 is running it. Wave 4: re-run done. All the AUC gain comes from patch 0005: branch rule 0.44/0.40 → 0.77/0.90, ignored = missing 0.51/0.31 → 0.85/0.88; about ±0.05 at N = 60 (w4-fix-core-4 ✓; simulation: synthetic students, example pack). Not merged. |
| 5 | The pilot can progress without validity evidence. Only RQ1, RQ3 and RQ9 must be green, and RQ4 isn't required. RQ5's rise in Ask features may be compliance with prompts. RQ3 uses only consented or donated messages. | open | Wanted: RQ4 as a progression criterion; RQ5 scored on first drafts and unprompted questions only. |

**Q&A, with the answer wanted:**
1. *Is a reported dead link evidence for or against Verify?* "For. The rule is fixed and tested."
2. *Which scoring labels does your study not test?* "The self-labels on the bot's own replies. Here is the per-host audit plan."
3. *Your rule passes κ = .6 about half the time. What will you claim?* "Screening only: n, CI and the human ceiling."
4. *What is one Verify task worth?* "One piece of evidence. Below 3 moments we show 'not enough evidence' (02 rec 12)."
5. *How is RQ5 not prompt compliance?* "We score only unprompted first questions."

### Investor (UK/EU edtech seed)

**Verdict:** Still no, but this is the first wave with numbers he can model, and they are not good. Microsoft takes about £22.50 per student and we take £5. The channel may have no door for custom agents, and a free Microsoft tutor is already preselected inside it.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Microsoft earns about 4.5 times what we do from our own customer: about £22.50 against a £5 licence, and up to £108 (w3-08m-13, our estimate on 600 turns, our choice). Pay-as-you-go is off by default, so adopting us is a finance-office decision. | partly | w3-08m recs 1, 2, 5 (cost table, cap). No measured turn count. Wave 4: the market ceiling is about 23,900 9EC0 candidates a cohort, about £143k–239k a year at £3–5 (w4-08-10 ✓, our estimate). |
| 2 | The "free route" rests on contested pages. "No charge only when licensed" is too strong (w3-08m-05 ~), and Microsoft's pages disagree on billing unlicensed students (w3-08m-09 ✓). Until tested, the cost is £11–108, not "maybe zero". | partly | w3-08m recs 3, 7, 8 (tenant test); none done. |
| 3 | The channel may not exist for us. The learner Copilot page lists only Microsoft's own experiences, and custom agents for under-18 learners are undocumented (w3-08m-04 ✓). "Four in five teachers on Outlook" is a proxy (w3-08m-03 ~). | recommended | w3-08m rec 8: ask Microsoft in writing, or test with a 17-year-old account. Not sent. Wave 4: still unconfirmed. Microsoft's K-12 pages don't mention custom agents for 13–17s (w4-08-02 ✓); admins can block or allow agents (w4-08-04, -06 ✓); the education addons page marks agent rows "employee-facing agents only" (w4-08-05 ✓, ambiguous); and a new admin opt-in mode limits students to Study and Learn (w4-08-01 ~, read on a mirror). |
| 4 | Copyright removes the content moat as well as the risk. The lawful spine is DfE OGL content plus our own words (w3-08c-05 ✓), which anyone can build. AQA bans AI use of its material (w3-08c-10 ✓). | partly | w3-08c recs 6–9. No cost per pack. |
| 5 | Evidence takes too long for a seed runway. The pilot shows feasibility, not learning. Learning needs an efficacy trial of about 100 schools (w3-02e rec 7): 2028 at best. | partly | w3-02e rec 8 (RAG thresholds registered in advance). |

**Q&A, with the answer wanted:**
1. *Total cost per student, all in?* "£5 to us plus about £22.50 to Microsoft, capped at £X per class per month."
2. *Can a 16-year-old reach a custom agent?* "Microsoft confirmed it on [date]", or "a test account did".
3. *Why pay twice when Study and Learn is free?* "It doesn't know 9EC0 and doesn't report AI literacy to the school."
4. *What stops Pearson copying the pack?* Hours per pack, and host-neutrality.
5. *What does spring prove?* "Feasibility and use against criteria we registered in advance. Not learning."

### DPO (multi-academy trust)

**Verdict:** On paper, the first pack she could take to her board: public task, an Art 28 checklist, a retention schedule and a signpost that stores nothing. Still not approvable. None of it is in code, and the pilot brings back stored messages and a second purpose.

| # | Objection | Status | By |
|---|---|---|---|
| 1 | Still unbuilt after three waves. Delete, export, key hashing and the bearer header are absent. Free text in `call_log` isn't fixed (w3-09-17 ✓). The retention period has no job to run it. | recommended | w3-09 recs 2–4, 9 (plans). |
| 2 | The pilot's RQ3 brings back stored messages (consented or donated), links mock results and runs a GLAT/AILIT-S test. Who controls the research data, on what basis? Public task doesn't obviously cover a student team's research. | partly | w3-02e §2 treats research as a non-core use, but names no controller and no basis. |
| 3 | The Art 9 condition falls on the school. The wellbeing label is health data in transit, which needs Sch 1 para 18 (w3-09-20 ✓) and possibly an appropriate policy document (w3-09-13 ✓). | partly | w3-09 rec 5. No drafted policy paragraph, and no test that nothing persists. |
| 4 | The connector is hers to answer for. Microsoft makes connector traffic the agent maker's responsibility, and the agent maker is the school (w3-09-05 ✓). Nobody has read the Product Terms, and teen protections for custom agents are still unknown. | partly | w3-09 rec 1 and the DPIA outline. No processor-chain diagram naming the hosting sub-processor. |
| 5 | AI literacy under public task depends on the school's curriculum, but the switch is a setup tick-box. | recommended | w3-09 rec 8 (default off, plus a DPIA line), unbuilt. |

**Q&A, with the answer wanted:**
1. *Show me the delete.* "Live: `delete-student 42`. Events, derived tables and `call_log` go now; backups age out in 35 days."
2. *Who controls the pilot research data?* A named institution, under its ethics approval, with a separate notice.
3. *What is stored when a pupil discloses?* "Nothing. Here's the database diff for that turn."
4. *Who is the hosting sub-processor, and where?* A name and a UK or EU region.
5. *Is the export "portability"?* "No. Under public task it's an access export."

### Wave 3 at a glance

Of 30 objections, 0 are answered, 13 recommended, 15 partly and 2 open (teacher #4, the pilot's cost to a department; researcher #5, progression without validity evidence). Nothing new is built, so no objection is answered. Wave 3 changed one earlier status (wave-2 researcher #3, open → partly) and added evidence to eleven earlier rows (five from wave 1, six from wave 2). Themes:

- **The Verify rule penalises honest checking.** Raised by the judges, student, teacher and researcher (w3-07-c5 ✓). This is the top fix before any agreement figure is quoted. Wave 4 is redesigning Verify scoring.
- **Ordinary words take over the literacy episode.** Raised by the judges, student and teacher (w3-07-c3 ✓). The line card is a workaround; the build fix is in progress.
- **The record misreads.** Decay ranks right-once below never-right, talk alone reaches secure, and the MCQ key gives itself away. Raised by all four non-business personas. All are recommended and unbuilt; the decay and MCQ fixes are in progress.
- **Cost and channel are now numbers, and the numbers are weak.** The investor's points: £22.50 to Microsoft per student, and an undocumented door for custom agents.
- **Paper compliance, no code.** The DPO's point: the documents are approvable in shape, but delete and export are still plans, and the pilot needs a named research controller.

---

## Wave 4: the pitch script

Sources: the pitch panel (`work/w4/panel-pitch.md`) on [pitch-script.md](pitch-script.md) §1–3 (video, deck, leave-behind), checked against [demo plan](demo-plan.md) Plans A and B, the [Wednesday build list](wednesday-build-list.md) and the morning brief. Three personas: EduX judges, a sixth-form economics teacher and a Year 12–13 student. Also used: w4-08 (Microsoft channel and market; verify-R) and the fix series (w4-fix-*; integration verifier Q).

Word counts after all the line edits below: video about 310 (limit 360), deck 514, or 533 with the slide-6 add-on (limit 560), leave-behind 222, or 225 on Plan B (limit 250).

Every line edit below is **recommended**: the panel proposed it and the editor has not yet applied it to the script. A row becomes *answered* once [pitch-script.md](pitch-script.md) carries the edit.

### EduX judges (Challenge 1), watching cold after many teams

**Verdict:** Shortlist on Plan A. It is the first version that opens on AI literacy and defines it inside 30 seconds. Two lines contradict the deck, and that costs trust. "Confidence isn't skill" plus "eduX assesses AI literacy where it happens" lands in the first 20 s, though the screen shows an inflation answer while the voice talks about images. Attention drops on slide 3 (two correlations back to back) and slide 5.

| # | Objection | Status | By (line edit) |
|---|---|---|---|
| 1 | "The sharper question counts as evidence" (4b): evidence of what? Slide 5 then turns to a maths RCT and exam mark splits, which reads as "a revision tutor again". | recommended | 4b → "That sharper question already scores as Ask." (6 → 7 words; the student's edit, student #2 below). |
| 2 | Overclaim: video 4d says "Every moment is evidence", while slide 6 says "One moment is weak evidence". | recommended | 4d → "Each moment adds evidence." (4 → 4) |
| 3 | Overclaim: "Each wrong option is a *known* wrong idea" (4c). The options are our design, not a published misconception inventory. | recommended | 4c → "Each wrong option names a wrong idea about chatbots." (10 → 9) |
| 4 | Doubted number: the slide-6 add-on, "5% or fewer". w2-02-08 ✓ gives ≤ 5% only when ignored tasks are treated as MNAR; it was 7% and 6% in the MCAR lenient cell. As spoken, it is wrong in a cell we ran. | recommended | → "In our main simulation, 5% or fewer no-skill synthetic students were ever shown secure; 7% in one harsher setting." (16 → 19) |
| 5 | Slide 4's "about 30% of GPT-4o's statements weren't backed by the pages it cited" drops the population. | recommended | Add "on medical questions" (+3 words; restores w2-02-34 ✓). |

### Sixth-form economics teacher

**Verdict:** Interested, not convinced. She'd want to see the teacher view and the mark-scheme fit working, and neither is shown. The Ofcom figure lands (she has seen it in the news), but "assesses AI literacy" sounds like one more thing to assess. Attention drops at shot 6's terminal montage and at slide 8's "0.17 of a standard deviation", unless that is framed as "we won't claim gains".

| # | Objection | Status | By (line edit) |
|---|---|---|---|
| 1 | "The server scores the letter itself" (4d): which letter? | recommended | → "Our server marks the student's answer, not the chatbot." (10 → 9) |
| 2 | Slide 5 implies the opposite of the truth. The checks are MCQs, which serve the point-marked third, yet the line says they are "a way in" because two-thirds of marks are level-marked. A 9EC0 teacher spots it at once. | recommended | → "So eduX teaches one point, then checks. Those checks cover the point-marked third of Pearson Edexcel 9EC0; the level-marked two-thirds come next." (28 → 22; w2-04-02 ✓, 34% / 66%) |
| 3 | Overclaim: slide 8, "46,365 … That's who we start with." The figure is all boards in England; eduX is built for 9EC0 only. | recommended | → "There were 46,365 A level Economics entries in England in 2026, across all boards. We start with Edexcel." (17 → 19). Wave 4 also has a 9EC0 figure: 21,005 certificates in 2024–25, 51.5% of the subject (w4-08-08 ✓). |
| 4 | Doubted number: "Only 34% of secondary schools". The finding is England state schools, 2025 (w1-08-04 ✓), and "in England" isn't said. | recommended | Slide 7: add "in England" (+2). |

### Year 12–13 student, 17

**Verdict:** "Would I use it? Only if it still answers me." The script never says plainly that it does. "Half of teens feel confident" lands ("that's me"); "image test" gets a shrug ("I don't use ChatGPT for images"). Attention drops from 1:46: the split-screen elasticity shot and the terminal montage are for adults.

| # | Objection | Status | By (line edit) |
|---|---|---|---|
| 1 | The script never says it answers me first. | recommended | 4a: "The chatbot answers with sources…" → "The chatbot answers in full, with sources, then sets an Ask task" (+2; the plan really does answer first). |
| 2 | "Ask task" and "Verify task" sound like homework on top of homework, and "counts as evidence" sounds like surveillance. | recommended | 4b → "That sharper question already scores as Ask." (same edit as judges #1). The "task" wording is not changed. |
| 3 | Overclaim: "the student sees the wrong idea they still hold". It comes from one tap on one question and reads as a label on them. | recommended | 4d → "And the student sees which wrong idea to recheck." (10 → 9) |
| 4 | Doubted number: "18% of references… in a 2023 study". "That's old GPT-4." | open | The panel proposes no edit. Wanted: say the model and year aloud, or pair it with a 2025–26 figure. |
| 5 | Missing: "no time pressure" (w3-05-03 ✓) would land with students but isn't in the script. | recommended | Q&A only. |

### Number check and Plan B

Every number in §1–3 traces to a ✓ row; there are no ~ or ✗ ids. Five uses drift from the ✓ claim text, all **recommended**: the four edits above (judges #4 and #5, teacher #3 and #4), plus slide 5's "maths students", which w2-09-08's claim text doesn't say. Add "maths" to the claim or drop the word.

If the 18:00 gate fails and Plan B is filmed (all **recommended**):
1. No Plan B words exist in the script; §1 is Plan A only. Splice: script shots 1–3 (0:00–0:40), Plan B 4a–4c (0:40–1:44), shot 5 (1:44–2:04), shots 6–7 unchanged.
2. "This student now asks to be shown the answer three times out of four" is not a finding (a synthetic history). → "This synthetic student now mostly asks to be shown the answer".
3. Delete "And it brings back what they were shown before" if reviews-due (build item 2(c)) was cut.
4. Plan B 4c: "Each wrong option is a real misconception." → "Each wrong option names a wrong idea."
5. Shot 7: "Now a slip becomes a lesson…" → "Next, …". Drop the 4d caption "How AI works: scored by our server". Shot 2's footer becomes "built on a branch, being merged".
6. Deck: slide 4 shows the designed options card labelled "on our branch" ("On our branch, when a student reports…"); add "(on our branch)" to slide 6 and the leave-behind's How AI works row; drop the slide-6 add-on.
7. If 05e is merged but the chatbot mislabels, "built on a branch" is false; say "built; filmed from captures".
8. Expect the prototype score to stay at 3. Problem fit loses most, because no AI-literacy moment is shown live on video.

### What wave 4 changed in earlier rows

The fix series (`sims/fixes/combined/`, patches 0001–0005 on the 05e export) answers in testing several objections from waves 1 and 3. Nothing is merged or built, so none is *answered*.

| Fix (finding) | Measured result (simulation or scripted turns, example pack) | Earlier rows now *recommended (tested diff ready)* |
|---|---|---|
| 0001 clamp, stuck once, quiz-me (w4-fix-core-1 ✓, -2 ✓, -3 ~) | No crash after 200 right answers (max p 0.999); stuck prerequisite plans 12/14 → 1/14; the exact "Quiz me on what's due" prompt gives the due review, but a paraphrase doesn't | none (no earlier panel row) |
| 0002 focus side turn (w4-fix-focus-1 ✓) | False focus 15/43 → 3/43; holdout 9/18 → 3/18 | W3 judges #2, student #1, teacher #1 |
| 0003 Verify scoring (w4-fix-verify-1 ✓) | Reported dead page or mismatch: Verify .143 → .748; ignored = skip | W3 judges #1, student #2, teacher #2 (with 0005) |
| 0004 MCQ give-away (w4-fix-mcq-1 ✓) | Testwise hit rate 0.96 → 0.28 against chance 0.31 | W1 judges #5; W3 judges #5, student #4 |
| 0005 decay (w4-fix-core-4 ✓) | Talk-only .763 → .300; How AI works AUC 0.51/0.31 → 0.85/0.88 | W3 judges #4, student #5, teacher #3, researcher #4 |

- Thirteen earlier rows move to *recommended (tested diff ready)*: one from wave 1, twelve from wave 3.
- One moves to *answered*: wave-3 judges #3 (slide-1 evidence), by a document. The pitch script calls Ofcom an image test and drops "nobody can see the difference".
- Nine rows get a "Wave 4:" note but keep their status, because the tested diff covers only part of the objection or the evidence is still unconfirmed: W1 student #3, judges #3, teacher #2, researcher #1; W2 researcher #5; W3 teacher #5, researcher #1, investor #1 and #3.

New caveats from the fixes, not yet raised by a persona:
- A student who keeps failing now gets seven reteach-only plans in a row with no question (w4-fix-core-2 ✓).
- The Verify fix does nothing if the chatbot leaves out `source_conflict` (w4-fix-verify-1 ✓).
- Patches 0004 and 0005 change what is on camera: the m2 option text and the seeded demo levels (w4-fix-combined-1 ✓).

### Wave 4 at a glance

- **New pitch objections:** 14 from three personas (5 judges, 4 teacher, 5 student). Thirteen are *recommended* (line edits ready); one is *open* (student #4, the 2023 figure). There are also 8 Plan B items, all *recommended*.
- **Pitch themes:** lines that contradict the deck ("every moment is evidence"); numbers whose population got dropped (England, medical questions, all boards, the MNAR condition); and the student's "does it still answer me?".
- **Earlier rows:** the tested fix series moves 13 rows to *recommended (tested diff ready)*, and wave 4 answers one by a document. The biggest wave-3 theme, "the Verify rule penalises honest checking", now has a tested fix. It still needs merging, and the chatbot must send the `source_conflict` label.

---

## Wave 5: no new panel

There was no persona panel this wave. Wave 5 tested five more patches (0006–0010 in `sims/fixes/combined/`, integration verifier S), simulated students gaming the scoring rules (w5-06g), dry-ran the label study (w5-02s) and modelled unit economics (w5-08u). The rows below record what that changes. Nothing is merged or built, so nothing becomes *answered*.

### What wave 5 changed in earlier rows

| Fix (finding) | Measured result (simulation or scripted turns, example pack) | Earlier rows affected |
|---|---|---|
| 0006 stuck ladder (w5-fix-stuck-1 ✓) | Always-failing student: longest bare-reteach run 23 → 0, no-MCQ run 24 → 1, stop/switch offer never → turn 8. Under 0010, a student who fails only explain-backs never gets the offer in 40 turns | none (no persona row). It answers wave-4 caveat 1 below and open question 22 |
| 0006 review requests, "what's due" (w5-fix-reviews-1 ✓) | Review asks served 1/18 → 18/18 in-sample, 0/12 ordinary messages stolen. Held-out paraphrases 2/10 by patterns. With a perfect `asks_for_reviews` label: 28/28. With an always-true label: 8/18 stolen | none (no persona row). Open question 23 is *partly* met |
| 0007 labelling text, 0008 Ask guard (w5-fix-labels-1 ✓, w5-fix-guard-1 ✓) | False Ask 0.0 on Verify answers labelled research 3/3 → 0/3. Plan A final_research Ask new → developing | Wave-5 notes only (label reliability is unmeasured): W1 researcher #4, W1 judges #3, W3 researcher #2 and #3 |
| 0009 broken-link counter (w5-fix-counter-c2 ~) | "Link is broken" gamers' Verify secure 100% → 0%; honest 65% → 59%. Five Plan A takes now end Verify new | Wave-5 notes: W1 student #3, W1 judges #3, W3 judges #1, W3 teacher #2 |
| 0010 show-then-answer counter (w5-fix-counter-c1 ~) | "Show me + match" 9 → 0 secure parts; always-"A" false-secure 57% → 17%. Honest in-session secure parts 3.6 → 1.4, first secure 2.4 → 12.0 min | Wave-5 note: W1 teacher #2 |

**No row changes status this wave.** Each "students will game it" or "labels are unreliable" row has a part that no wave-5 diff covers:
- W1 teacher #2: pasted explain-backs.
- W1 student #3: plain "yeah I checked".
- W1 researcher #2: restating the reply. The text line is in neither 0007 nor 0009.
- The label rows: no human or real-chatbot agreement figure.

The stuck loop and "what's due" have tested diffs but no persona row. They were wave-4 caveats and open questions 22–23.

New caveats from the wave-5 fixes, not yet raised by a persona:
- 0007 tells the chatbot to tick a,d on a dead link. 0009 treats a,d alone as no evidence. A chatbot that follows 0007 therefore gives an honest dead-link finder nothing (w5-fix-counter-c2 ~).
- 0010 slows "secure" for honest students and, with 0006, removes the stop/switch offer for students who fail only explain-backs (w5-fix-counter-c1 ~, w5-fix-stuck-1 ✓).
- **Don't put "gaming-proof" on a slide.** Even after 0009 and 0010, guessers out-earn honest students in level steps per minute; the gain is now mostly "developing" (w5-06g, simulation). The safe line is "cheap tricks no longer reach secure".
- The skip counter records about 2% of ignored literacy tasks, so "we show skipped tasks" is not true yet (w5-06g-07 ~).

### Wave 6: no new panel

Wave 6 replaced the two wave-5 counters with fairer ones (0009b, 0010b) and added 0011 (MCQ option length rank). Blind verifier U confirmed all 7 counter claims. Verifier V confirmed 0011's apply, ingest warnings, testwise and gaming numbers, and flagged two economics rows (w6-len-econ ~). Simulation throughout: synthetic students or scripted turns, example pack. Nothing is merged or built, so nothing becomes *answered*.

| Fix (finding) | Measured result | Rows changed |
|---|---|---|
| 0009b dead-link report cap (w6-c2b-1 ✓, w6-c2b-2 ✓, w6-planA ✓) | "Link is broken" gamers' Verify secure 100% → 0% (developing 0.740); honest 64% → 62% (N = 300); all 8 Plan A takes developing 0.740 | W1 student #3, W3 judges #1, W3 teacher #2 → *recommended (tested diff ready, verified)*; notes on W1 researcher #2 and W1 judges #3 (still *partly*) |
| 0010b show-then-pick cap (w6-c1b-1 ✓, w6-c1b-2 ✓, w6-c1b-3 ✓) | Show/teach + pick gamers 9 → 0 parts secure; honest 3.6 → 3.4 parts (first secure 2.4 → 8.9 effort-min); stop/switch offer back for open-only failers (turn 19) | W1 teacher #2 → *recommended (tested diff ready, verified)* |
| 0011 MCQ length rank (w6-len-1 to -4 ✓, w6-len-econ ~) | Middle-length guess 0.536 → 0.286 (chance 0.312) on the option sets, 57% → 19% right in play; ingest warnings for the 9EC0 pack | W1 teacher #2, W1 student #3 |

Still **not** covered: the sequence cue; pasted explain-backs under a literal labeller; L1c (one real check, then free reports); plain "yeah I checked"; real-chatbot label rates. **Still never say "gaming-proof".** The safe lines are "cheap tricks don't reach secure in our simulation" and "options are written to the same length".

---

## Open questions for wave 6

**Status of the earlier list** (numbering as in wave 5):

| # | Question (short) | Status |
|---|---|---|
| 1 | [J] Labels Claude sends on the four Plan A lines | open: Wednesday dry run (build item 9). The w5-02s dry run used a Claude proxy on scripted messages, not the real chatbot on Plan A |
| 2 | [S, T] Trigger words in real research questions; wrong course part on 100 real messages | partly: the focus fix cuts false focus to 3/43 on scripted turns (w4-fix-focus-1 ✓); real-message frequency still open |
| 3 | [J] Whom the brief names as the user of the assessment | open: paste the brief on Wednesday |
| 4 | [J, R] How AI works AUC above 0.5 under the decay fix | **done**: 0.85/0.88 with ignored = missing (w4-fix-core-4 ✓; simulation) |
| 5 | [S] Do students report fewer failures when reporting lowers a score? | **done (by design)**: reporting now raises Verify (w4-fix-verify-1 ✓). The incentives literature was not searched. |
| 6 | [R] Cluster-bootstrap CI coverage for κ with 8–16 clusters | open |
| 7 | [R] Published LLM-vs-human κ for question-quality features | open |
| 8 | [R] Does an unprompted-feature Ask score separate novice and practised personas? | open |
| 9 | [T] After fix (b), does `untested` fire and pull a talk-only part down? | partly: talk-only now reads .300 (w4-fix-core-4 ✓); the `untested` review was not checked |
| 10 | [S] Does a plain-claim MCQ cut testwise success? | **done**: 0.96 → 0.28 against chance 0.31 (w4-fix-mcq-1 ✓; tested with four options, the three-option setting was not applied) |
| 11 | [I] Can NotAdult learners invoke custom declarative agents? | partly: K-12 pages don't mention custom agents (w4-08-02 ✓); admin agent controls exist (w4-08-04, -06 ✓); the addons footnote is ambiguous (w4-08-05 ✓); unconfirmed |
| 12 | [I] UK schools with Copilot pay-as-you-go for students | open |
| 13 | [D] Do the Product Terms or DPA cover custom-connector traffic to third-party MCP? | open |
| 14 | [D] Does a Sch 1 para 18 signpost need an appropriate policy document? | open |
| 15 | [I] Edexcel 9EC0 share of A level Economics in England | **done**: 21,005 of 40,795 certificates, 51.5% (w4-08-07, -08 ✓) |
| 16 | [I] Weekly turns per sixth-former, from published usage data | open |
| 17 | [D] Data controller and Art 6 basis for a student team's pilot research | open |
| 18 | [T] Teacher-hours per school for RQ3, RQ8 and the DPIA | open |

**Wave-5 additions** (from the pitch panel, the fix verifiers and w4-08). Tags as before, plus [B] build verifier.

| # | Question (short) | Status |
|---|---|---|
| 19 | [J, T, S] After the wave-4 line edits, does every deliverable stay within its word limit, and does every number still match its ✓ claim text? | open |
| 20 | [S] A 2025–26 figure for fabricated or unsupported references beside the 2023 "18%" | open |
| 21 | [B] Does the run script reproduce the whole fix series end to end on a clean 05e checkout? | open: the series rebuilds an identical tree with `patch -p1` and `git am --keep-cr` (w5-fix-combined-2 ✓). `harness/run_w5s.sh` is transcribed from the commands run, but has not been run end to end as one script |
| 22 | [B, T] Fix the reteach-only loop for a student who keeps failing | **done (tested diff)**: patch 0006 stuck ladder; bare-reteach run 23 → 0, stop/switch offer at turn 8 (w5-fix-stuck-1 ✓). Caveat: under 0010 the open-only failer gets no offer (see 30). Wave 6: with 0010b instead, the offer comes back at turn 19 (w6-c1b-3 ✓) |
| 23 | [B, J] Should "quiz me" match paraphrases, without matching too much? | partly: patch 0006 adds an `asks_for_reviews` label plus patterns; in-sample 18/18, held-out patterns 2/10, perfect label 28/28 (w5-fix-reviews-1 ✓). The real chatbot's label rate is untested (see 31) |
| 24 | [B, S] Does the resolver name-gate (Fix 2) remove the last 3/43 false-focus cases? | open |
| 25 | [R, J] How often does Claude (and a second host) send `source_conflict`? | open: folded into 31 |
| 26 | [T] Economist sign-off on the 9EC0 pack rows from patch 0004 | open |
| 27 | [I, D] What does MC1537656 say? | open |
| 28 | [I] Does the "employee-facing agents only" footnote bar school-built agents for students; do schools turn on Study and Learn-only mode? | open |

**New for wave 6** (from the wave-5 fix verifiers and the gaming simulation). Wave-6 status first, then the original wording.

| # | Question (short) | Status |
|---|---|---|
| 29 | [B, J] 0009 vs 0007 on dead links | **done (tested diff, verified)**: 0009b replaces 0009; a dead-link report scores 1, capped at developing until one real check; all 8 Plan A takes end developing 0.740 (w6-planA ✓, w6-c2b-1 ✓). Verify no longer depends on the chatbot ticking c; it still depends on `source_conflict` (see 31) |
| 30 | [B, T, S] What 0010 costs honest students | **done (tested diff, verified)**: 0010b gives 3.4 parts secure against 3.6 (0010: 1.4) and restores the stop/switch offer (turn 19), but the first secure part takes 8.9 effort-minutes instead of 2.4 (w6-c1b-2 ✓, w6-c1b-3 ✓). No on-camera shot shows a part going secure from picks in one sitting (shot 5 shows first moves only) |
| 31 | [R, J, B] Real chatbot label rates for `asks_for_reviews` and `source_conflict` | **open**: Wednesday dry run. 0010b now also relies on the chatbot not ticking pasted repeats (0009b's text line) |
| 32 | [T, J] The option-length cue after 0004 | **partly**: 0011 spreads the key's length rank (middle 0.536 → 0.286, chance 0.312; in play 57% → 19%; w6-len-3 ✓, w6-len-4 ✓, in-sample) and adds ingest warnings. The point-order (sequence) cue remains: a point-2/3 key is the one option not in the previous check (100% on 11 sets). Needs point-specific misconceptions (later) |

29. [B, J] **0009 vs 0007 on dead links.** 0007 tells the chatbot to tick a,d for a link that won't load. 0009 scores a bare dead-link report (a,d) as no evidence. Five Plan A takes end Verify new (w5-fix-counter-c2 ~). Choose one: give a found dead link partial credit, change 0007's tick rule, or accept that a dead link alone earns nothing and film only the "the page says 9.1%, not 11.1%" line. Also check that the real chatbot ticks c on that line.
30. [B, T, S] **What 0010 costs honest students.** Honest in-session secure parts drop 3.6 → 1.4 and the first secure comes at 12.0 min instead of 2.4 (w5-fix-counter-c1 ~), and the stop/switch offer no longer reaches a student who fails only explain-backs. Is there a cap that blocks "show me + match" with a smaller honest cost? Does any on-camera shot outside Plan A show a part going secure within one sitting?
31. [R, J, B] **Real chatbot label rates for `asks_for_reviews` and `source_conflict`.** 0006's review fix works with a perfect label (28/28), and 0009/0003 depend on `source_conflict`. Neither rate is measured on Claude or a second host. Replaces 25.
32. [T, J] **The option-length cue after 0004.** Dropping the longest and shortest options gets 58% of course MCQs right against about 31% chance, which gives 4.4 false-secure parts (w5-06g-05 ~). How should ingest or the pack spread the key's length rank? Until then, no claim that the options resist cue-guessing.
