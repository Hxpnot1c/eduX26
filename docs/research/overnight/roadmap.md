# w6-08r · After the competition: a 12-month roadmap (Dec 2026 – Nov 2027)

**Method.** This note brings together what waves 1–5 already found. It adds no new web research. Sources: [MORNING-BRIEF](../../MORNING-BRIEF.md), [business plan](../../business-plan.md), [02](../../02-ai-literacy-assessment.md), [02a](../../02a-label-agreement-protocol.md), [05](../../05-product-features.md), [09](../../09-safety-ethics.md), [judge panel](../../judge-panel.md), `docs/build/steps/later.md`, the pilot plan in `work/w3/w3-02e.md` §2, and the wave-5 notes `w5-06g` (gaming) and `w5-08u` (unit economics). Factual numbers come only from ✓ rows in `findings.csv`, cited by id. Numbers marked "our choice", "our estimate" or "our calculation" are ours.

**Conventions.**
- **Everything in the roadmap is "our plan".** It is not a commitment from any school, from Microsoft or from Pearson, and none of them has been contacted.
- Objections are cited as *persona wave #n*, for example "DPO w3 #2" means wave 3, DPO persona, objection 2 in the [judge panel](../../judge-panel.md).
- Effort: S under 2 h, M about half a day, L more.
- Each success criterion is a pass/fail test we can run ourselves and show.

## Summary
- **Our plan has four gates, each with a written pass test.** If a gate fails, the plan says which work stops. No later quarter assumes an earlier gate passed.
  - **G1, 31 Jan 2027: the route gate.** A NotAdult test account in a real school's Microsoft 365 Education tenant reaches an eduX Copilot Studio agent. If it doesn't, there is no pupil pilot.
  - **G2, mid-April 2027: the pilot-ready gate.** Safety code merged, DPAs signed, research controller named, preregistration lodged.
  - **G3, end July 2027: the pilot result,** reported against criteria registered in advance.
  - **G4, 30 Nov 2027: the payer gate.** Priced commitments from pilot schools.
- **We move the pilot to the summer term (late April to mid-July 2027), with Year 12 classes.** Two reasons: January to March is mock-marking season (teacher w3 #4), and an ethics review plus per-school DPIAs won't be done by January. Our own university exams (May–June) fall inside the pilot, so the build work is front-loaded into the December–January and July–August vacations.
- **The product work is mostly S-effort fixes that are already specified,** listed in the order the DPO asked for them: bearer header, key hashing and revocation, delete and export, a retention job, and a signpost that stores nothing (09 recs 5–10, 13). Entra sign-in (M), the teacher view (M) and step 07 checks and templates (L) come after.
- **The evidence work fixes the two open objections against the pilot.**
  - RQ4, the AI-literacy test correlation, becomes a progression criterion. RQ5 is scored only on unprompted questions (researcher w3 #5).
  - Each pilot task gets an owner and an hour budget, and the team does most of them (teacher w3 #4).
- **The content work keeps to what we're allowed to do.**
  - The knowledge graph is built on the DfE's OGL subject content plus our own words (w3-08c-05 ✓).
  - Themes 1–2 are fully reviewed by an economist before the pilot. Themes 3–4 follow by November.
  - We record hours per part and errors per 100 rows, because the investor asked what stops Pearson copying the pack (investor w3 #4).
- **The business work keeps its promises small.**
  - Send a permission request to Pearson, then an endorsement *application*. Applying is not the same as being endorsed.
  - A DPA template, and 3–5 pilot schools on Microsoft 365.
  - A pricing test in the autumn, with Microsoft's credit cost shown beside our price.
  - The objections still open afterwards are listed in §4. The moat (investor w1 #2) is still open.
- **We never promise a learning gain within the 12 months.** Even a 100-school trial detects only about 0.17 SD (w1-08-08 ✓). The pilot shows whether eduX is feasible and used, nothing more.

## 1. Constraints we plan around (our plan)

| Constraint | What it means for the plan |
|---|---|
| Four economics students, part-time. Exams in May–June 2027 | A budget of about 4 h a week each in term, 0 in exam weeks, and more in the December–January and July–August vacations (our choice). One named on-call person per pilot week. The pilot must run without daily team input |
| Microsoft is the only documented school route for under-18s, and it is untested | Copilot Chat is off by default for 13–17s (w2-05-04 ✓). The K-12 pages don't mention custom agents (w4-08-02 ✓). An opt-in admin switch can lock students to Study and Learn (w4-08-01 ~). G1 tests the route before anything depends on it |
| The school pays Microsoft per call | 5 credits per MCP call (w3-08m-06 ✓). About £22.50 per student per year in the central case, £11.25–£108 by use (w3-08m-13 ✓, our estimate). Every quote and pilot report shows this cost |
| Copyright | UK education exceptions are non-commercial (w3-08c-01 ✓). Pearson restricts copying (w3-08c-06 ✓). So the pack is our own words on the DfE OGL spine, and a solicitor reviews it before we charge anyone (business plan rec 17) |
| Research on minors | The research controller is still unnamed (DPO w3 #2). BERA consent rules apply (w3-02e-13 ✓). Until the controller is named, the pilot is feasibility-only, using eduX's ordinary logs |
| The learning-evidence horizon | A 3–5-school pilot rates 0 padlocks on the EEF's MDES scale (w3-02e-09 ✓). An efficacy trial needs an independent evaluator. We don't run one ourselves |

## 2. Gates (our plan)

| Gate | Date | Pass test | If it fails |
|---|---|---|---|
| **G1 Route** | 31 Jan 2027 | A Year 12–13 test account (NotAdult) in a real school tenant finds and uses an org-published eduX agent, with Study and Learn-only mode off. With the mode on, the agent disappears. We screenshot both and record the credits metered for 10 calls (business plan recs 15–16) | No pupil pilot. We fall back to adult Year 13s on their own accounts, plus one college with its own LLM front end as a research partner (w3-08m-11 ✓ shows this route exists). The DPA, DPIA and pack work continues |
| **G2 Pilot-ready** | 16 Apr 2027 | Four things: patches P1–P3 and S1 merged with tests passing; at least 3 schools with a signed DPA, DPIA and IT checklist; a research controller and ethics approval named in writing; OSF preregistration lodged | Start with the schools that are ready (2 is amber under RQ1). Without a controller, run feasibility only: RQ1, 2, 6, 7 and 9, and drop RQ3, 4 and 8 |
| **G3 Pilot result** | 31 Jul 2027 (data), 15 Oct 2027 (report) | The RAG table against the preregistration, with every deviation logged | Amber means adapt and re-pilot in spring 2028. Red on RQ9 (safety) stops the pilot at once |
| **G4 Payer** | 30 Nov 2027 | At least 2 of the pilot schools sign a priced letter of intent or a paid renewal, with the business manager named and the credit cost shown (target 3; our choice) | Re-price, or keep eduX as a free research tool and stop the business plan |

## 3. Milestones by quarter (all our plan)

Columns: **ID**, **milestone**, **success criterion** (pass/fail), **depends on**, **answers** (objection by persona and wave), **effort**.

### Q1: December 2026 – February 2027 (the route and the safety code)

| ID | Milestone | Success criterion | Depends on | Answers | Effort |
|---|---|---|---|---|---|
| **P1** | Merge 05e and the tested patch series to `main`. Wave 4 0001–0005 first (w4-fix-combined-1 ✓), then the wave-5 diffs 0006–0010 (stuck ladder, labels text, Ask guard, broken-link counter, show-then-answer counter), each re-tested | `check_mcp` passes after every patch on `main`. The fix harness re-runs on `main` with the same results as on the export: Verify on a dead page .748 (w4-fix-verify-1 ✓); testwise MCQ success at or below chance (w4-fix-mcq-1 ✓) | None | Judges w1 #1, #5; researcher w3 #1; teacher w3 #1–3; student w3 #1, #2, #4, #5 | M |
| **P1b** | Close the two cheap exploits found by the gaming sim: "the link is broken" and "just show me, then match" (`w5-06g`; simulation, no ✓ claims) | Re-run `sims/gaming/` on `main`. No cheap strategy earns more displayed level per effort-minute than honest play on Verify (our test) | P1 (0009, 0010) | Student w1 #3; teacher w1 #2 | S–M |
| **P2** | Bearer header; `?key=` only behind an adult-ChatGPT flag; SHA-256 key hashing; `revoke-key` and `rotate-key`; random ids; no free text in `call_log.error` (09 recs 5–7, 10) | A test shows a URL key is refused when the flag is off. The database holds no plaintext key. A revoked key fails on the next call. A `call_log` row holds an error code and at most 80 characters | None | DPO w1 #2, w2 #3 (partly, until P5), w3 #1 | S ×4 |
| **P3** | `delete-student`, `delete-school`, `export-student` ("access export", never "portability"), and a retention job: end of course plus one term, `call_log` kept 90 days (all our choice; 09 recs 8–9) | Scripted test: after a delete, no row with that `student_id` remains in any table, `call_log` included, and `rebuild_state` doesn't bring any back. The export is JSON without the key. The retention job deletes rows past their date in a test database | None | DPO w1 #4, w2 #5, w3 #1 | S–M |
| **S1** | Safeguarding signpost: a `wellbeing_concern` label leads to stop-and-signpost naming the school's DSL contact. Nothing persists per student, and the DSL contact is a required field at setup (09 recs 13, 15) | The database diff for a signpost turn is empty, apart from at most a server-wide daily counter with no id (the DPO's own test, DPO w3 Q&A 3). Setup fails without a DSL contact | P1 | DPO w1 #3, w3 #3 (our side; the Art 9 condition stays with the school) | S |
| **S2** | Delete the "use what you already know about the student" line. AI-literacy scoring off by default, switched on only when the school confirms it teaches AI literacy (09 recs 1, 11) | Grep finds the line nowhere. A new school's AI-literacy scoring is off until the setup tick is set and recorded | P1 | DPO w1 #5, w3 #5 | S |
| **B1** | **G1 route test.** A pilot school's IT admin runs business plan rec 16, and we send Microsoft the questions in rec 14 | G1 as in §2, by 31 Jan | A school admin willing to help (human contact; none made yet) | Investor w1 #1, w2 #2, w3 #2–3; student w2 #5; judges w1 #4; DPO w1 #1 | M |
| **B2** | Recruit 3–5 Edexcel 9EC0 departments on Microsoft 365, using the business plan §8 filter (Copilot for Year 12–13; Study and Learn-only mode off; IT will approve the agent; a DSL will review) | At least 3 written expressions of interest by 28 Feb | B1 (G1) | Investor w1 #1, w3 #3 | M (human time) |
| **S3** | **DPA template and DPIA pack**: a one-page DPA covering all 8 ICO Art 28 terms (w3-09-04 ~), a DPIA starter (09 outline), a processor-chain diagram naming the hosting sub-processor and its UK or EU region, a one-paragraph crisis protocol, and the IT checklist (business plan rec 7d) | Every ICO term maps to a clause. One school DPO reads the pack, and we log and answer their questions. Pass: no blocking question left open | None (B1 for the diagram) | DPO w1 #1, w2 #2, w3 #4; investor w1 #1 | M |
| **E1** | Name the **research controller**: ask a supervising university department to sponsor ethics review and act as controller for the research uses (RQ3, 4, 8) | Controller, Art 6 basis and ethics approval named in writing by 31 Mar. If not, the pilot is feasibility-only (G2) | Human contact | DPO w3 #2 | M |
| **E2** | **Label checks before real messages.** (a) If the Wednesday study didn't run: the synthetic agreement study (02a), with at least 20 messages rewritten by the team, 5–10 cold items, and the server's decision reported, not only the ticks. (b) A self-label audit: about 20 scripted transcripts per host, including how often `source_conflict` fires on a dead page or a mismatch (02 rec 19). (c) A second host, Copilot, once G1 passes | For each skill: κ with its 95% CI, the human–human ceiling and n, all reported. Firing rate of `source_conflict` per host. "Pass" means only what 02a §1.6 says, and we report that the rule is weak (w3-02e-06 ✓) | P1; B1 for (c) | Researcher w1 #4, w2 #1–2, w3 #1–3 | M |
| **C1** | **DfE OGL spine.** Map every node to the DfE economics subject content, with OGL attribution. `spec_ref` stays a bare pointer to 9EC0, and no 9EC0 headings or ordering are copied (business plan rec 12) | Every node has a DfE content reference or an "own words" flag. A checklist shows no 9EC0 heading reused as a node name | None | Investor w3 #4 (partly) | M |
| **C2** | **Pearson copyright permission request**, kept separate from endorsement, item by item as in business plan §6 | Sent by 31 Jan. The reply, or no reply, is logged. The own-words pack doesn't wait on it | None | Investor w3 #4; teacher w1 #3 (indirectly) | S |
| **T1** | Name roles (technical lead, content lead, evidence lead, schools and DPO lead) and post-competition hours in the README | Published by 15 Dec | None | Investor w1 #5 | S |

### Q2: March – May 2027 (pilot-ready, then live)

| ID | Milestone | Success criterion | Depends on | Answers | Effort |
|---|---|---|---|---|---|
| **C3** | **Themes 1–2 pack, every row reviewed by an economist.** We take these to be the themes Year 12 is taught; to confirm with the pilot teachers. Rows stay `draft` until a teacher or economist approves them. The wave-4 MCQ rows are in scope | 100% of the rows the pilot can reach are `approved`. We record hours per part and errors found per 100 rows (investor w3 ask #7) | C1 | Teacher w1 #3, w2 #2, w3 #5; investor w1 #4 | L |
| **P4** | **Entra sign-in** (05 option B): eduX as a resource server checking the Entra token's audience; student id = hash of `tid`+`oid` | Pilot students sign in with their school account and never paste a key. Tests refuse a token with the wrong audience and any token in the query string (w2-05-05 ✓) | G1, P2 | DPO w2 #3 | M |
| **P5** | **Teacher view v1** (05 rec 23): opt-in, k ≥ 6, shares in bands, a 14-day window, a starter MCQ per flagged misconception, no AI-literacy rows unless S2 is on. The "what your teacher sees" line goes into the student text | Off by default. A synthetic test shows no cell under 6 students. On screen it says "nothing flagged", never "all clear". In the pilot, each teacher opens it at least once a fortnight (RQ7 log) | P1, P3 | Teacher w1 #4; judges w2 #3; DPO w2 #4; student w1 #4; teacher w2 #4 (partly: it catches big shared misconceptions only, w2-05-29 ✓) | M |
| **E3** | **OSF preregistration** of the w3-02e §2 plan, with two changes (our plan): **RQ4 completed is a progression criterion**, meaning the external test given to at least 62 consenting students and r reported with its CI (no bar on r itself); **RQ5 is scored on unprompted questions and first drafts only** | The registration timestamp is earlier than the first live pilot turn | E1 for RQ3/4/8 | Researcher w3 #5; investor w3 #5 | S–M |
| **E4** | **Teacher-hours budget per pilot task** (our choice): the team does the message rating, the mapping of mock items to parts, the DPIA draft and the consent letters. The teacher's own time is the weekly 2-minute log plus one interview | The RQ6 log shows no more than 15 min a week net per teacher (green, our choice). Each task has a named owner before G2 | B2 | Teacher w3 #4 | S |
| **B3** | Sign DPAs. Schools complete their DPIAs. IT runs the checklist: approve in the Agent Registry, no Block Agents, allow the Year 12–13 group, Study and Learn-only mode off (w4-08-06 ✓, w4-08-04 ✓) | G2: at least 3 schools ready by 16 Apr | S3, G1 | DPO w1 #1, w2 #2 | M |
| **B4** | Per-class Copilot spending cap set at the peak-month figure: about £65 a month in a full-term month for a class of 20, not £45 (w5-08u; our estimate). The call-count logging is switched on (w5-08u rec 5) | Every pilot school has a cap and a named payer before go-live | B3 | Investor w2 #1, w3 #1; judges w2 #4 | S |
| **E5** | **Pilot starts after Easter** (late April 2027): Year 12 classes, 10 weeks, a single arm, an EEF-style feasibility study (w3-02e-11 ✓) | RQ1 green: at least 3 schools live by week 3, tool-call errors under 2% (our choice) | G2 | Investor w1 #4 (partly) | — |

### Q3: June – August 2027 (finish the pilot, then the summer build)

| ID | Milestone | Success criterion | Depends on | Answers | Effort |
|---|---|---|---|---|---|
| **E6** | **RQ3: label agreement on real messages.** 100 consented or donated, de-identified messages. Our plan changes w3-02e §2 to cut teacher time: two team raters label all 100, a teacher labels a 30-message subset, and we log the client and model version on every exchange | For Ask and answer scoring: κ with its 95% CI and the human ceiling. About ±.16 half-width is expected near 80 decisions (w3-02e-01 ✓). Every message is deleted after rating, and the deletion is logged | E1, E3 | Researcher w1 #4, w3 #3; judges w1 #3 | M |
| **E7** | **RQ4: convergent check with a short AI-literacy test,** given outside the product before and after the pilot. GLAT is a 20-item test with α .80 (w1-02-23 ✓). AILIT-S is the shorter option (w1-02-24 ~; its licence and fit for 16–18s to be checked). Add one COR lateral-reading task for Verify, scored by two humans | At least 62 completers (our calculation). Pearson r with a Fisher-z CI, reported whatever its value. Other embedded assessments correlated about .36–.41 with outside measures (w1-02-21 ✓, w1-02-22 ✓) | E1, E3 | Researcher w1 #5, w2 #3; judges w1 #3; investor w1 #4 | M |
| **E8** | RQ8: mock results by topic, used only to test **prediction** (does "secure" on a part match mock items on it?). The school does the pseudonymising | An AUC with a bootstrap CI, labelled as prediction. Never "raised grades" | E1 | Investor w1 #4 (partly) | S |
| **P6** | **Step 07 checks and templates** (`later.md`): levels per strand (KAA and evaluation), never a numeric mark, a readiness checklist, question templates seeded per student, and Section A MCQ templates in our own words. Built in the summer vacation | A teacher levels 20 answers per strand, independently. We report exact and within-one-level agreement, labelled a small sample. No numeric mark appears in any test transcript. Templates stay `draft` until approved | C3 | Teacher w1 #1, w2 #1, w2 #3, w3 #5; student w1 #5 | L |
| **C4** | **Source audit.** Pearson opens each summer series to the public after 12 months (w3-08c-07 ✓), so June 2026 papers become usable from August 2027. Nothing reached through a teacher's login | `sources.csv` records `access: public` and a date on every row | C3 | Investor w3 #4 | S |
| **B5** | A UK IP solicitor reviews the pack process and the pitch wording, **before anyone is charged** (business plan rec 17) | A written review is on file before the first invoice | C1–C3 | Investor w3 #4 | M (cost) |

### Q4: September – November 2027 (report, price, apply)

| ID | Milestone | Success criterion | Depends on | Answers | Effort |
|---|---|---|---|---|---|
| **E9** | **Feasibility report** against the preregistration: RAG per RQ, deviations, attrition. Code published, data not. Every result is labelled feasibility, engagement, measurement or prediction, never learning | Published by 15 Oct (G3). Progression to an efficacy-trial *proposal* only if RQ1, RQ3 and RQ9 are green, RQ4 is completed and nothing is red | E5–E8 | Investor w3 #5; researcher w3 #5 | M |
| **E10** | If G3 passes: approach an independent evaluator or funder about an efficacy trial. A 100-school trial detects about 0.17 SD (w1-08-08 ✓) | An expression of interest sent. Nothing more is promised | E9 | Investor w1 #4, w3 #5 | S |
| **B6** | **Pricing test.** A department licence at £5 per student, minimum £100, and a trust tier at £3 (business plan; our choice). Each quote shows the expected Copilot credit cost from the school's own pilot data | G4: at least 2 priced commitments with the business manager named (target 3) | E9, B5 | Investor w1 #3, w2 #5, w3 #1; investor's asks #2, #6, #8 (business plan §10) | M |
| **C5** | **Full 9EC0 pack**: Themes 3–4 reviewed as in C3 | All four themes `approved` by 30 Nov. We publish hours per pack and the error rate | C3 | Investor w1 #4, w3 #4 | L |
| **C6** | **Pearson endorsement application** for the reviewed Themes 1–2 resource. We re-read the policy after its June 2027 review first (w3-08c-09 ✓). It is never called "official" and never implies examiner input | Application submitted with an accuracy checklist against the specification. Success means submitted, not endorsed | C3, B5 | Investor w3 #4; judges (credibility) | M |
| **S4** | DPIA pack v2 after one term's review: retention job evidence, signpost diff, incident log. We watch the ICO's planned edtech code and its Art 28 page (09 rec 21) | Every pilot school's DPO signs off the term review | E5 | DPO w3 #1, #4 | S |
| **P7** | Teacher view v2 only if pilot data supports it: pooling across sets, and per-student completion as a school opt-in. OAuth broker (05 option C) **only if** a non-Microsoft school asks | A decision recorded with its data | E9 | Teacher w2 #4 | M / L |

## 4. Objection coverage after the roadmap (our assessment)

| Objection | Milestones | After the roadmap |
|---|---|---|
| No tested under-18 route (student w2 #5; investor w1 #1, w2 #2, w3 #3; judges w1 #4; DPO w1 #1) | B1 (G1), B3, P4 | Answered if G1 passes. If it fails, answered honestly: no pupil route |
| Key in the URL, no delete, export or retention (DPO w1 #2, #4, w2 #3, #5, w3 #1) | P2, P3, P4 | Answered in code, with tests to show |
| No safeguarding route (DPO w1 #3, w3 #3) | S1, S3 | Answered on our side. Alerts stay out until a school contracts for them (09 rec 19) |
| Research controller for the pilot (DPO w3 #2) | E1 | Answered, or the research questions are dropped |
| Pilot can progress without validity evidence (researcher w3 #5) | E3, E7 | Answered: RQ4 is a progression criterion |
| Pilot's cost to the department (teacher w3 #4) | E4, pilot moved out of mock season | Answered by an hour budget and the RQ6 log |
| Labels unchecked; study weak; one host (researcher w1 #4, w2 #1–2, w3 #2–3; judges w1 #3) | E2, E6 | Partly: real messages and a second host, still a small sample |
| Recognition, not exam skills (teacher w1 #1, w2 #1, w3 #5; student w1 #5) | P6 | Partly: levels per strand, never a mark. Only small-sample agreement evidence |
| Content accuracy (teacher w1 #3, w2 #2) | C3, C5 | Answered by review status, with the hours and error rate published |
| Willingness to pay; price (investor w1 #3, w2 #5, w3 #1) | B4, B6 (G4) | Tested, not assumed |
| Evidence too slow (investor w3 #5) | E9, E10 | Still true. The roadmap only makes it honest: feasibility in 2027, learning later |
| **Moat** (investor w1 #2; w2 #3) | C5's hours and error rate, E7 | **Still open.** The roadmap produces evidence and a pack cost, not a moat |
| Funded rivals; Study and Learn is free (investor w2 #4; business plan §10 ask #4) | B6 | **Still open** unless a pilot teacher chooses eduX over Study and Learn and says why (RQ7) |

## 5. One-slide version (≤ 80 words)

> **After the competition (our plan, Dec 2026 – Nov 2027)**
> **January:** a test student account reaches eduX in a school's Copilot, or no pupil pilot.
> **Spring:** keys out of URLs, delete and export, a safeguarding signpost; Themes 1–2 reviewed by an economist; DPA and DPIA pack.
> **Summer term:** a preregistered feasibility pilot in 3–5 Edexcel departments: use, label agreement on real messages, correlation with an AI-literacy test. Not learning.
> **Autumn:** full 9EC0 pack, priced offer, Pearson endorsement application.

(78 words, including the title.)

## 6. Q&A: "What happens after the competition?" (≤ 60 words each)

Factual numbers come only from ✓ findings. Plan targets and dates are our plan.

1. **"Will you keep going, and what's first?"**
   "Yes. Our plan has four gates with pass tests written now. January: a student test account reaches eduX through a school's Copilot, or we don't pilot with pupils. April: keys out of URLs, delete and export, a safeguarding signpost. Summer term: a preregistered pilot. Autumn: a priced offer."
   *(48 words; no factual numbers)*

2. **"Can a 16-year-old actually use it?"**
   "Not tested yet. Copilot Chat is off by default for 13–17s, and the school switches it on (w2-05-04 ✓). Microsoft's K-12 pages don't mention custom agents (w4-08-02 ✓). So our first milestone, by end of January, is a test account in a real school tenant. If it fails, there's no pupil pilot."
   *(52 words)*

3. **"Will you show it improves grades?"**
   "Not within a year, and we won't claim it. Even a 100-school trial detects only about 0.17 SD (w1-08-08 ✓). Our pilot is a feasibility study with success indicators registered in advance, as EEF guidance advises (w3-02e-11 ✓). Learning evidence needs an independent trial afterwards."
   *(45 words)*

4. **"How will you know the AI-literacy scores mean anything?"**
   "Two pilot checks. First, the chatbot's labels against human raters on real, consented messages. Second, the levels against an outside test such as GLAT, a 20-item test with α .80 (w1-02-23 ✓). Similar embedded assessments correlated about .36–.41 with outside measures (w1-02-21 ✓, w1-02-22 ✓). Completing that correlation is a progression criterion."
   *(52 words)*

5. **"Who pays, and is the market big enough?"**
   "Departments, from September, at a price we'll test. The school also pays Microsoft about £22.50 a student a year in our central estimate, £11.25–£108 depending on use (w3-08m-13 ✓), and every quote will show it. 9EC0 had 21,005 certificates in England in 2024–25, 51.5% of A level Economics (w4-08-08 ✓)."
   *(50 words)*

## 7. Considered and rejected
- **Piloting in the spring term (January to March), as the business plan has it.** Ethics review, DPIAs and G1 can't be done by January, and January to March is mock marking (teacher w3 #4). We moved it to the summer term. The cost is that the pilot overlaps our own exams.
- **Promising endorsement, or an efficacy trial within the 12 months.** Neither is in our control. The criteria are "application submitted" and "expression of interest sent".
- **An OAuth broker in 2027 by default.** It is L effort and only needed for non-Microsoft schools, which we aren't targeting (05 option C).
- **Two teacher raters for all 100 real messages** (w3-02e §2 as written). This is the teacher-time cost that teacher w3 #4 objects to. Team raters plus a teacher subset is our compromise. It weakens the claim, so we will say so.
- **A per-student wellbeing count, or DSL alerts.** 09 revised this to store nothing, with no alerts until a contract sets the route (09 rec 13, 19).
- **Other exam boards in 2027.** AQA bans AI use of its material (w3-08c-10 ✓). Growth would come from other Pearson subjects later (w4-08-09 ✓), not this year.

## 8. Methods and open questions
- **Methods:** synthesis of the overnight reports, the judge panel and `later.md`, with marks checked against `findings.csv`. No web search and no simulation run.
- **Open questions:**
  - Does a NotAdult account reach an org-published MCP agent? (G1 answers it.)
  - Do Microsoft's Product Terms cover custom-connector traffic? (DPO w3 #4; open question 13.)
  - Which department would act as research controller? (E1.)
  - Is AILIT-S licensed and suitable for 16–18s? (E7.)
  - Will pilot schools leave Study and Learn-only mode off? (w4-08-01 ~.)
  - How many calls does a student make in a week? (B4 logging answers it.)
