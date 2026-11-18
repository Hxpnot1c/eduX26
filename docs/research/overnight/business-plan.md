# Business plan: market, buyers, pricing, competitors and evaluation

Waves 1 and 2 (overnight 17–18 Nov 2026). Sources:
- Wave 1: `work/w1/w1-08.md`, `work/w1/w1-05.md`; marks in `verify-C.json` and `verify-A.json`.
- Wave 2: `work/w2/w2-08.md` (marks in `verify-H.json`) and `work/w2/w2-05.md` (cost and routes; marks in `verify-E.json`); the investor and DPO panel (`work/w2/panel-investor-dpo.md`).

Each finding has one blind verifier mark. Labels: "our choice" marks numbers we chose; "our estimate" marks numbers we derived.

**Wave 2 changes three things from wave 1:**
1. The "hosts shape one conversation" moat line is gone. Gemini now tracks progress across sessions.
2. The AI Act Article 4 revenue line is gone. Article 4 needs no measurement and no certificate.
3. The price is re-anchored to what schools actually pay.

Two scout-note lines stay out: "eduX runs inside Gemini on school accounts" (false: w1-05-09 ✓) and the target market "or ChatGPT/Claude" for pupils (w2-08 rec 3), because neither host has an under-18 route (see [05](05-product-features.md)).

## Summary
- **Gemini has caught up on tracking.** Study notebooks (25 Jun 2026) track progress per learning objective across sessions (w2-08-01 ✓). Guided Learning in Google Classroom gives teachers progress insights, rolling out globally from 3 Nov 2026 after a pilot in three UK Ark schools (w2-08-02 ✓). **"eduX keeps a learner model across sessions" is no longer a moat.** What remains is a *head start*: AI-literacy evidence from real chatbot use, plus a learner model the school owns that can work across chatbots. Neither is validated, and only claude.ai is tested.
- **Target market for pupils: schools on Microsoft 365 Education that switch on Copilot Chat for 16–17-year-olds.** It is the only documented school route, it is untested, and it is off by default (w2-05-04 ✓). Google schools are out: eduX can't plug in (w1-05-09 ✓), and they get tracking free. The share of English sixth forms on M365 with learner Copilot enabled is unknown, which is the investor's first question.
- **What schools actually pay: two public records.**
  - Dixons Academies Trust paid Sparx £25,250 ex VAT for a year of Sparx Maths, about £1.80–£2.80 per pupil (our estimate, a lower bound; w2-08-06 ✓).
  - Essex County Council pays Century-Tech about £22,950 a year for an FE platform (w2-08-07 ✓).
- **Re-anchored price (our choice):** £5 per student per year for a department, minimum £100. A trust tier is £3 per student. Students never pay. Wave 1's £8 was three to four times Sparx's per-pupil price at trust scale. Reasoning in §3.
- **The cost risk is Microsoft's, not ours.** Each Copilot Studio turn costs the school Copilot Credits.
  - Our estimate is about **US$84 per student per year**, more than ten times our licence. That rests on a US$0.01-per-credit rate we never verified, on an unconfirmed billing unit and on a turn volume we chose (w2-05-06 ~).
  - "No model calls" lowers *our* cost, not the school's total.
- **Government funds competitors.** The DSIT/DfE AI Tutoring Tools Pioneer Programme gave eight suppliers £300k each, including Pearson, Eedi and Google (w2-08-08 ✓). It targets Years 9–10, not A level.
- **No buyer is required to pay for AI-literacy assessment.** The Commission says Article 4 needs no measurement and no certificate (w2-08-09 ✓). We drop any compliance-product pitch.
- **Evidence: none yet.** The pilot can't show learning. Even 100 schools detect only about 0.18 SD (our calculation; w1-08-08 ✓).

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **Moat slide and Q&A:** "Google now tracks progress inside Google. eduX gives the school its own evidence of how pupils use AI (asking and checking) from real use, and a learner model the school owns across chatbots. A head start, not a moat; not yet validated." Never say again that the hosts "shape one conversation". | pitch, video | S | yes | w2-08-01 ✓, w2-08-02 ✓, w2-08-03 ✓, w2-08-05 ✓ |
| 2 | **Target-market line:** "Sixth forms on Microsoft 365 Education. Google schools get tracking free and can't plug us in." Add: "share of sixth forms with learner Copilot on: unknown; finding out is our first job." | pitch, §8 | S | yes | w2-05-04 ✓, w1-05-09 ✓, w2-08-01 ✓ |
| 3 | **Price line:** £5 per student per year, minimum £100; trust tier £3; students free (our choice). When asked "Sparx costs a trust £2–3": "Our trust tier matches that; a single A level department pays a little more because it is small." | pitch, §3 | S | yes | w2-08-06 ✓, w2-08-07 ✓ |
| 4 | **Cost line, honest version:** "eduX makes no model calls, so our margin is hosting. On Microsoft the school also pays Copilot Credits. Our rough estimate is up to about US$84 per student per year, unconfirmed; we're asking Microsoft and designing for fewer, cheaper calls." | pitch Q&A, §3 | S | yes | w2-05-06 ~ |
| 5 | **Drop every Article 4 "compliance" or "licence the instrument" line.** Keep AI-literacy evidence as value to the school (teacher insight) and possibly to awarding bodies (a task bank), not as a compliance product. | pitch, §4, §10 | S | yes | w2-08-09 ✓ |
| 6 | **Competitor rows:** split "study modes" into Gemini (tracking + Classroom insights), ChatGPT (in-chat quizzes, no tracking found), Claude (US teachers only, connectors to Eedi and ASSISTments). Add the Pioneer Programme. | §4, pitch Q&A | S | yes | w2-08-01 ✓ to w2-08-05 ✓, w2-08-08 ✓ |
| 7 | **Distribution answer for Q&A:** adults and teachers today. Sixth-formers next, through Copilot Studio in a Microsoft school tenant (untested). Entra sign-in for pilots. | pitch Q&A | S | yes | w2-05-03 ✓, w2-05-04 ✓ |
| 8 | **Evaluation slide:** feasibility → efficacy; the MDES table; "a pilot cannot show learning". | pitch | S | yes | w1-08-08 ✓ |
| 9 | **Name roles and post-competition commitment** on the team slide. | pitch | S | yes | panel: investor w1 #5 |
| 10 | **Ask Microsoft** whether an MCP tool call bills as one agent action, and whether Agent Builder agents avoid charges. Price a cheaper configuration per student per term. | business plan | S (human email) | no | w2-05-06 ~ |
| 11 | **Copilot Studio end-to-end test** on a real school tenant with a 17-year-old test account. | build | M | no | w2-05-03 ✓, w2-05-04 ✓ |
| 12 | **DPIA starter, DPA template and processor-chain diagram** for pilot schools. | business plan | M | no | w2-05-12 ✓; panel: DPO w2 #2 |
| 13 | **Watch the Pioneer Programme's Reading Room standard** and align eduX's safety and tracking documents with it once published. | later | M | no | w2-08-08 ✓ |

## 1. Market (England-only figures flagged)

| Figure | Value | Scope | Source |
|---|---|---|---|
| A level Economics entries, 2026 (provisional) | 46,365 (2025: 41,880; +10.7%) | **England only** | w1-08-01 ✓ |
| Students on the course at any time | about 85–95k (2 cohorts) | England; **our estimate** | from w1-08-01 ✓ |
| State schools with sixth-form places | 1,979 schools, 544,667 places (May 2025) | **England only**; mainstream state | w1-08-02 ✓ |
| Colleges | about 35 sixth-form colleges, 156 general FE colleges | England; AoC list | w1-08-02 ✓ |
| Edexcel share of Economics | unpublished | — | no source found |
| Share of sixth forms on M365 Education with learner Copilot enabled | **unknown** | — | open question (investor w2) |

**Revenue ceiling (our estimate, at the re-anchored prices, our choice):**

| Edexcel share | Students | At £5 (department) | At £3 (trust tier) |
|---|---|---|---|
| 30% | about 27k | about £135k | about £81k |
| 40% | about 36k | about £180k | about £108k |
| 50% | about 45k | about £225k | about £135k |

This is a ceiling, not a forecast. It assumes every Edexcel student pays. In practice the reachable market is only the schools on Microsoft 365 that turn on learner Copilot, an unknown fraction. On one subject and one board this is a small business. Growth comes from more subjects and boards, not a higher price.

## 2. Buyers and how schools buy

- **Budget is the barrier.** 95% of leaders cite budget constraints (w1-08-03 ✓).
- **Decisions are local.** 56% of technology decisions are made at school level and 31% with the trust or LA (w1-08-03 ✓). A head of department can propose a small tool.
- **Pupil AI is a hard sell.** Leaders plan to invest in AI for teachers far more often than for pupils (58% vs 20%). 77% of secondary leaders whose pupils could use GenAI reported problems, mostly plagiarism (w1-08-04 ✓). So pitch eduX as making pupils' existing chatbot use safer and visible.
- **Real purchases are direct awards.** Both records found were "below threshold, without competition":
  - Sparx Maths for Dixons: £25,250 ex VAT, 1 Sep 2025 to 31 Aug 2026 (w2-08-06 ✓).
  - Century-Tech for Essex: £68,850 inc VAT over three years (w2-08-07 ✓).

  So trusts and councils do buy adaptive platforms by direct award at about £20–25k a year. Notices of £30k or more inc VAT appear on Find a Tender, so a deal that size will be public. No records were found for Up Learn, Seneca or Eedi (not found by these methods, which is not proof of absence).
- **Buying thresholds.** DfE treats purchases under £10k as low value, £10–40k as medium (three quotes) and over £40k as high (w1-08-06 ~).

**Buyer:** the head of Economics proposes and the school business manager signs. In a trust, also brief the digital lead. On Microsoft, **the IT admin is a third gatekeeper**: they switch on learner Copilot and pay for the credits.

## 3. Pricing (our choice, with reasoning)

**Department licence: £5 per student per year, minimum £100 (covers up to 20 students). Trust tier: £3 per student per year across five or more schools. Students never pay.** All three numbers are our choice.

Why we moved from £8:
1. **Anchor on what schools pay, not on budget shares.** Wave 1 set £8 as about 6% of the £128 per pupil that LA-maintained secondaries spend on ICT learning resources (w1-08-05 ✓). That was a share of a budget, not a market price. The best real price we have is Sparx Maths at about £1.80–£2.80 per pupil per year at trust scale (our estimate on an assumed headcount, a lower bound; w2-08-06 ✓). It is also a single-subject product, which makes it comparable. The investor called £8 "unanchored" (panel w2 #5).
2. **The trust tier matches Sparx; the department price sits above it.** An A level Economics department has tens of students, not a whole 11–16 cohort. Setup, the DPA and support cost us about the same per school whatever its size (our assumption). So a small department pays about twice the trust rate. Sparx is proven at scale and we are not, so we don't price above that.
3. **A low minimum keeps £5 the real price.** Wave 1's £250 minimum would have made a department of 20–30 pay £8–£12.50 per student, back above the old £8. A £100 minimum means a department of 20 or more pays £5 per student, and a very small one (10 students) pays £10. Typical department sizes are our assumption; no source gives them.
4. **Well under the £10k low-value band,** so no tender is needed (w1-08-06 ~).
5. **The school's real cost on Microsoft is the credits.** If our estimate holds, the school pays Microsoft about US$84 per student per year against £5 to us (w2-05-06 ~). A higher eduX price would add to a total that already worries a business manager. A lower one can't fix it. The fix is fewer and cheaper calls (below).
6. **No family payments.** Charging families conflicts with DfE std 13 (no steering learners to paid options) and hurts equity ([09](09-safety-ethics.md)).

**Test the price with priced letters of intent, not argument.** The investor's objection stands until three heads of Economics sign one.

### Cost to the school on Microsoft (our estimate, unverified rate)

| Item | Figure | Status |
|---|---|---|
| Credits per `tutor_turn` | about 7 (2 generative answer + 5 agent action) | **Our estimate.** Unconfirmed whether an MCP call bills as one agent action (w2-05-06 ~) |
| Price per credit | US$0.01 pay-as-you-go | **Unverified**: not on the cited Microsoft page; from a search summary (w2-05-06 ~) |
| Turns per student | 40 a week × 30 weeks = 1,200 a year | **Our choice** |
| Per student per year | **about US$84** | Our estimate. If the MCP call is not billed as an action, about US$24 (2 credits a turn, our arithmetic) |
| Reasoning model | +10 credits per 1,000 tokens; Microsoft's example: 141–461 credits for one message (w2-05-06 ~) | Avoid; pick a non-reasoning model |
| Prepaid tenants | blocked at 125% of capacity unless pay-as-you-go is linked (w2-05-06 ~) | Agents can stop mid-term; set a cap |
| M365 Copilot licence instead | US$18 per user per month academic, about US$216 a year | Dearer than metered use at our volume |

**Cheaper configuration to price (later):**
- a non-reasoning model;
- calling eduX only on course messages, not every message;
- an Agent Builder agent, if it avoids generative-answer charges (unconfirmed);
- a monthly cap per agent.

Give the business manager a cost per student per term once Microsoft confirms the billing unit.

## 4. Competitors (public pages, 17–18 Nov 2026)

| Product | What it does | Price (public or procured) | Tracks progress across sessions? | Assesses AI literacy? | Fair comparison with eduX |
|---|---|---|---|---|---|
| **Gemini study notebooks** | Splits a goal into 100+ objectives grouped by topic (Strengths / Focus areas / Not started); diagnostic quiz; progress dashboard | Included | **Yes** (w2-08-01 ✓). School accounts incl. under-18s were promised "in the coming weeks" (June 2026); rollout not confirmed | Not described | Tracks progress from a student's uploads inside Google. eduX tracks against a teacher-reviewed spec map and measures AI-use behaviour, but can't run on Google school accounts at all |
| **Guided Learning in Google Classroom** | Teacher-assigned Guided Learning on course materials, with progress insights | Included | **Yes, teacher-facing** (w2-08-02 ✓). UK pilot: Ark, 3 schools, 4 weeks; measured perceptions, not attainment. A Tokyo university RCT (vendor-reported, adults) found 8.1 vs 5.3 pp | Not described | A direct competitor for teacher visibility, free to Google schools |
| ChatGPT study mode / quizzes | Socratic mode; in-chat interactive quizzes (Sept 2026) | Included | None found as of Nov 2026 (w2-08-03 ✓). Absence after search, not proof | Not described | Say "we found no public evidence", not "ChatGPT can't" |
| Claude learning mode / Claude for Teachers | Socratic style for adults; US teacher tools, free to verified US K-12 educators to 30 Jul 2028 | Free for US teachers | No student tracking described; connectors to Eedi, ASSISTments and others (w2-08-04 ✓, w2-08-05 ✓) | No | Precedent that learner-model tools plug into hosts. It helps credibility and weakens novelty |
| Sparx Maths | Maths homework, ages 11–16 | Dixons: £25,250 ex VAT/yr; about £1.80–£2.80 per pupil (our estimate; w2-08-06 ✓) | Yes | No | Proven and cheap at scale. Not A level |
| CENTURY Tech | Adaptive platform with its own content, mainly English, maths, science | Essex FE: £68,850 inc VAT over 3 years (w2-08-07 ✓) | Yes | Not described | No A level Economics found |
| Eedi | Misconception-based diagnostic questions | US pricing seen only in a snippet (not used) | Yes, by misconception | No | The closest relative. Now a Pioneer supplier and a Claude connector |
| Khanmigo | AI tutor on Khan content | Learners $4/month or $44/year; teachers free; districts on request; no UK (w2-08-12 ✓) | Yes (Khan mastery) | Not described | Large library and an RCT (0.06–0.08 SD per year, US maths; w1-09-08 ~). No A level Economics |
| Seneca | Free revision; Premium by quote, whole school or year group only | School Sync £646 ex VAT/yr after 12 free months (w1-08-07 ✓) | Yes | Not described | Huge reach and A level Economics; can't be bought by one department |
| Up Learn | A level video lessons, quizzes | £79.99–£104.99 a month consumer; schools by quote (w1-08-07 ✓) | Yes | Not described | Complete content eduX lacks |
| Regulated AI qualifications | 44 on the Ofqual register with "artificial intelligence" in the title; none from AQA, OCR or Pearson. Small vocational awards, e.g. SIAS L1 study skills (12 h), NCFE L2 AI for the Workplace (w2-08-10 ✓) | Fees not on the register | n/a | Certify taught skills | eduX gathers evidence from normal study; it is not a qualification |
| **AI Tutoring Tools Pioneer Programme** | DSIT/DfE R&D contracts: Medly AI, Zero Gravity, Learn Anything, Flint, Pearson, ElevenLabs, Eedi, Google UK | £300k ex VAT each, 29 Jun 2026 to 31 Mar 2027 (w2-08-08 ✓) | One eligible product type is "a system for tracking and synthesising student progress" | — | Years 9–10, disadvantaged schools: 3–4 partner schools per supplier, at least 500 Year 9–10 pupils in total across them. Not A level. Its standard will be shared through a Reading Room |

**Fair overall:** every competitor has shipped content or reach at scale, and several have trial evidence. Gemini now does cross-session tracking free for Google schools. eduX's honest difference is narrow:
1. **AI-literacy evidence (Ask, Verify) from pupils' real chatbot use.** We found no other product that does this (absence after search, not proof).
2. **A learner model the school owns, independent of the host.** Today that independence is a design, not a fact: only claude.ai is tested.

Both are unvalidated head starts, not a moat (coordinator wording).

**Moat question (investor w1 #2, w2 #3).** Wave 1 named two moats:
- (a) A pack pipeline that turns a specification into parts and misconceptions in days, with teacher review. It stands, unbuilt at full scale.
- (b) "A validated AI-literacy instrument that boards or AI Act Art. 4 deployers would license." **Dropped.** The Commission says Article 4 "does not entail an obligation to measure" staff knowledge and needs no certificate (w2-08-09 ✓). Article 4 also covers staff, not pupils.

What's left of (b) is a possible task bank for awarding bodies or PISA-style tasks (the AILit framework feeds PISA 2029's innovative domain, w2-08-11 ✓). That is speculative, with no buyer named.

**Pearson.** 9EC0's awarding body is a Pioneer supplier building its own AI tutoring (w2-08-08 ✓). The investor asks why Pearson would license to us. Our only answers are host-neutrality and the cost and time per pack, and both are unproven.

## 5. Distribution: the under-18 chatbot route

Full table in [05](05-product-features.md).

| Route | Under-18 in UK? | Custom MCP? | School can deploy and put in a DPIA? | Status |
|---|---|---|---|---|
| **M365 Education + Copilot Studio agent** | 13–17 after the admin sets K-12 + NotAdult; off by default (w2-05-04 ✓) | Yes. Key in a header or query, or OAuth 2.0 (w2-05-03 ✓) | Yes, on paper | **Untested. The target channel.** Costs credits per turn (w2-05-06 ~) |
| Mistral Le Chat (personal) | 13+ with parental permission (w2-05-01 ~) | Yes (w2-05-02 ✓) | **No**: consumer terms, personal capacity, no DPA | Personal only; not a pupil route we offer |
| claude.ai consumer | No, 18+ (w1-05-02 ✓) | Yes | n/a | Tested on an adult account |
| claude.ai Team / Enterprise / Education | Unconfirmed (w1-05-03 ✓) | Yes | Unclear | Ask Anthropic |
| ChatGPT Teens / Edu / for Teachers | Teens: auto-placed, MCP undocumented. For Teachers: US staff only (w2-05-14 ~, snippet) | Unclear | No | Untested |
| Gemini for Education | Yes, restricted | **No** custom MCP (w1-05-09 ✓) | n/a | Not possible |

**What we say:** adults (including Year 13s who have turned 18) and teachers can use eduX on their own accounts today. The first school channel is Microsoft Copilot Studio, untested. Sign-in moves from keys to a header, then to the school's Entra (none built; [05](05-product-features.md)). Nobody has tested a 16–17-year-old on a real school tenant, which is the investor's first test.

## 6. Partnerships and copyright route (Pearson)

**What we do now (fact):**
- Course packs are written in our own words. No Pearson specification text, past papers, mark schemes or examiner reports are reproduced, only summarised.
- Examiner reports are freely downloadable from Pearson (w1-04-08 ✓), and misconception distractors draw on summaries of them.
- No tutor2u content is reused.

**What we propose (no contact made):**
- Ask Pearson whether it would license specification wording and past-paper items, or co-badge a reviewed pack. Pearson is now building its own AI tutoring (w2-08-08 ✓), so expect it to be a competitor as much as a partner.
- Oak's MCP server and Claude for Teachers' Eedi and ASSISTments connectors show that education tools travel this way (w1-05-14 ~, w2-08-05 ✓).
- **A qualification route (speculative):** a partner awarding body could use eduX evidence as portfolio evidence for a small L1/L2 AI award (w2-08-10 ✓).

## 7. Regulation and risks

| Risk | What applies | Our response | Source |
|---|---|---|---|
| Under-18 access | claude.ai 18+; DfE tells schools to follow age limits | Microsoft school tenant only for pupils; demo on an adult account, said on screen | w1-05-02 ✓, w2-05-04 ✓ |
| **Host cost (Copilot Credits)** | About US$84 per student per year (our estimate, unverified rate); 125% enforcement | Ask Microsoft; non-reasoning model; fewer calls; agent cap | w2-05-06 ~ |
| **Competitor capture** | Gemini tracking free for Google schools; Pearson, Eedi and Google funded by the Pioneer Programme | Target Microsoft schools; lead on AI-literacy evidence; track the Reading Room standard | w2-08-01 ✓, w2-08-02 ✓, w2-08-08 ✓ |
| DfE product safety standards | Partly met; gaps in safeguarding and data rights | Fixes ranked in [09](09-safety-ethics.md); **none built yet** | w1-09-01 ✓ to w1-09-03 ✓ |
| UK GDPR, Children's code | DPIA, minimisation, profiling off by default | DPA per school, DPIA starter, processor-chain diagram (rec 12) | [09](09-safety-ethics.md) |
| Key security | Key in the URL, stored in plaintext | Header (S), hash and revoke (S), Entra (M); none built | w2-05-10 ✓, w2-05-11 ✓ |
| AI Act Art. 4 | No measurement, no certificate needed | **Not a revenue line** | w2-08-09 ✓ |
| Content accuracy | Every pack row is `draft` | Teacher review queue before any pilot | panel: teacher w1 #3 |
| Team continuity | One committer | Name roles and commitment | panel: investor w1 #5 |

**Never claim "DfE compliant".**

## 8. Go-to-market (our choice)

1. **Now to March 2027: recruit 3–5 pilot Economics departments** through the team's own networks (no contact made). Criteria:
   - Edexcel 9EC0;
   - **a Microsoft 365 Education tenant whose IT admin will switch on Copilot Chat for Year 12–13 and build the agent**, with a budget line or cap for credits;
   - a DSL willing to review the safety statement.

   Year 13s who are 18+ may use their own accounts meanwhile. Google Workspace schools are not pilot candidates.
2. **Free pilot for one term.** The school signs a DPA and runs a DPIA from our template.
3. **From September 2027: department licence** at £5 per student, minimum £100, and a trust tier at £3 (our choice).
4. **Lead message:** "Shows you how your pupils use AI, and teaches them to check it, inside the Copilot your school already runs." It answers the plagiarism problem leaders report (w1-08-04 ✓).
5. **Pilot measures:** engagement and fidelity, the teacher's use of the starter MCQ and re-check accuracy ([05](05-product-features.md)), and the credits actually billed per student. None of this is learning.

## 9. Evaluation plan

**Stage 1: feasibility pilot (3–5 schools, one term).** It cannot detect learning. With 5 schools the MDES is about 1.5 SD (our calculation). Outcomes: usage, fidelity, teacher time, credits billed, safety signposts, acceptability, data quality.

**Stage 2: efficacy trial, randomised by school.** Primary outcome: learning, on a blind-marked test of 9EC0-style items including extended writing. Secondary: an AI-literacy task score. Covariate: GCSE prior attainment. An independent evaluator and a funder such as EEF.

**MDES (our calculation).** Assumptions (our choice): ICC 0.15, R² = 0.5, 20 students per school, half the schools treated, 80% power, 5% two-sided.

| Schools | MDES, multiplier 2.8 (w1-08-08 ✓) | Small-sample multiplier (our calculation) |
|---|---|---|
| 5 | 0.78 | about 1.49 |
| 20 | 0.39 | 0.41 |
| 40 | 0.27 | 0.28 |
| 60 | 0.22 | 0.23 |
| 100 | 0.17 | 0.18 |

A realistic edtech effect is small: Khanmigo's was 0.06–0.08 SD per year (w1-09-08 ~). The best nearby evidence on teacher reports is the ASSISTments bundle, g = 0.18 in US grade 7 maths (w2-05-20 ~, secondary), and dashboards alone show no attainment effect (w2-05-23 ~). **Never present a pilot as showing learning gains.**

## 10. What would make the investor take a second meeting

The wave 2 verdict was "still no, and worse". The investor's conditions, merged across waves:
1. **A 17-year-old using eduX on a real Microsoft school tenant, end to end**, with a date and a tenant ("anything else counts as a no").
2. **The total cost to the school per student**: our licence plus Microsoft's *confirmed* credit charge, in writing, plus a cheaper configuration priced per student per term.
3. **The size of the channel:** how many English sixth forms and colleges run M365 A3/A5 with learner Copilot on.
4. **One paying buyer for AI-literacy evidence** (a school, trust or awarding body). Article 4 no longer supplies one.
5. **Three priced letters of intent** from heads of Economics, with the business manager named, at the re-anchored price.
6. **An answer to "why would Pearson license to you?"**: cost and hours per pack, measured on a full 9EC0 pack with a teacher-review error rate.
7. **One pilot class's usage data**, labelled as engagement.
8. **The team:** a named technical lead and post-competition commitment. 05e is built on its branch but not merged; merge it.

## Later (not before Thursday)
- Microsoft: the billing unit for MCP calls; Agent Builder; a cost per student per term.
- The share of English sixth forms with learner Copilot enabled.
- Whether Gemini study notebooks have reached UK under-18 school accounts, and whether teachers see per-student data.
- Dixons' 11–16 headcount, to tighten the Sparx per-pupil range. School quotes for Up Learn, Seneca and Eedi.
- When the Pioneer Reading Room standard is published.
- PISA 2029 MAIL dates and UK participation (unverified; don't quote dates).
- Ask Anthropic and Mistral about under-18 members on school plans (human contact).

## Considered and rejected
- **"Hosts shape one conversation; eduX keeps a learner model across sessions."** False for Gemini since June 2026 (w2-08-01 ✓).
- **Art. 4 deployers licensing the instrument.** No measurement or certificate is required (w2-08-09 ✓).
- **Keeping £8.** Anchored on a budget share, not a price paid; three to four times Sparx per pupil (w2-08-06 ✓).
- **Raising the price to Up Learn's.** Its public prices are consumer prices.
- **Targeting Google schools, or "ChatGPT/Claude schools" for pupils** (w2-08 rec 3). No under-18 route on either; Google schools get tracking free.
- **Le Chat as a channel.** A school can't contract for it (DPO w2 #1).
- **Per-student consumer pricing.** Puts cost on families; conflicts with DfE std 13.
- **Third-party price aggregators** (Sparx "£600", Century "£2,760", Khanmigo "$10–35", Eedi US tiers). Unverified.
- **Claiming "nobody is building this".** The Pioneer Programme funds eight suppliers.
- **Planning an efficacy trial ourselves.** It needs 60–100 schools and an independent evaluator.

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| Cost story contradicts itself (US$84 credits vs "no model calls") | Investor w2 #1 | **Partly**: the cost is stated honestly and flagged unverified; Microsoft not yet asked; cheaper configuration not priced |
| Market shrunk to one channel | Investor w2 #2; w1 #1 | **Partly**: target named as M365 schools; channel size unknown; route untested |
| Moats weaker; Art. 4 gone | Investor w2 #3; w1 #2 | **Partly**: the Art. 4 line is dropped and the moat is reframed as a head start. **Open**: no buyer for AI-literacy evidence |
| Funded rivals; Pearson | Investor w2 #4 | **Open**: named honestly; no answer to "why license to us" |
| Price unanchored | Investor w2 #5 | **Partly**: re-anchored to procurement records (our choice); no letters of intent |
| "Runs inside Gemini" | Investor w1 #1 | **Answered**: removed |
| Team | Investor w1 #5 | **Recommended**: roles to name (rec 9) |
| Processor chain for a DPIA | DPO w1 #1, w2 #2 | **Recommended**: DPA, DPIA starter and chain diagram (rec 12), not written |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-08-01 | England A level Economics entries 41,880 → 46,365 (+10.7%) | official document | England | adoption | ✓ |
| w1-08-02 | 1,979 state schools, 544,667 sixth-form places | official document | England, state | adoption | ✓ |
| w1-08-03 | 95% budget barrier; decisions 56% school, 31% with trust/LA | official document (survey) | England state schools | adoption | ✓ |
| w1-08-04 | AI investment for teachers vs pupils 58% vs 20%; 77% of leaders report problems | official document (survey) | England state schools | adoption / policy | ✓ |
| w1-08-05 | LA-maintained secondaries: £128/pupil ICT learning resources | official document | England LA-maintained | cost | ✓ |
| w1-08-06 | DfE buying bands <£10k / £10–40k / >£40k | official document | England schools | policy | ~ "frameworks at any value" is an inference |
| w1-08-07 | Seneca School Sync £646/yr; Up Learn £79.99/£104.99 a month | practitioner | UK | cost | ✓ |
| w1-08-08 | MDES 0.39 → 0.17 at 20 → 100 schools | simulation (analytic) | hypothetical | learning (planned) | ✓ (small-sample multiplier larger) |
| w2-08-01 | Gemini study notebooks: 100+ objectives, labels, diagnostic quiz, progress dashboard; school accounts promised | official document (vendor) | 18+ personal first | adoption | ✓ |
| w2-08-02 | Guided Learning in Classroom rolling out globally with teacher progress insights; Ark pilot in 3 UK schools | official document (vendor) | UK secondary pilot; Tokyo undergraduates (RCT) | adoption; RCT learning (vendor-reported) | ✓ |
| w2-08-03 | OpenAI Sept 2026 newsletter: in-chat quizzes; no tracking mentioned | official document | ChatGPT users | adoption | ✓ |
| w2-08-04 | Claude for Teachers: US K-12 educators only, 18+, free to 30 Jul 2028 | official document | US educators | adoption / policy | ✓ |
| w2-08-05 | Claude for Teachers connectors include Eedi, ASSISTments | official document | US educators | adoption | ✓ |
| w2-08-06 | Dixons → Sparx Maths £25,250 ex VAT, direct award, 2025-26 | official document | England MAT, ages 11–16 | cost | ✓ (per-pupil figure is our estimate) |
| w2-08-07 | Essex → Century-Tech £68,850 inc VAT, 3 years, FE | official document | England council, FE | cost | ✓ |
| w2-08-08 | Pioneer Programme: 8 × £300k incl. Pearson, Eedi, Google; Years 9–10 | official document | England state secondary | policy / cost | ✓ (500 pupils is a total across partner schools) |
| w2-08-09 | EC: Art. 4 needs no measurement and no certificate; Omnibus amended it | official document | EU deployers (staff) | policy | ✓ |
| w2-08-10 | 44 Ofqual AI qualifications; none from AQA/OCR/Pearson | official document | England | policy | ✓ |
| w2-08-11 | AILit feeds the PISA 2029 Innovative Domain | official document | 15-year-olds | policy | ✓ |
| w2-08-12 | Khanmigo $4/month or $44/year; teachers free; no UK | practitioner | US | cost | ✓ |

Also cited here; each sits in its home report's table: w2-05-01 ~, w2-05-02 ✓, w2-05-03 ✓, w2-05-04 ✓, w2-05-06 ~, w2-05-10 ✓, w2-05-11 ✓, w2-05-12 ✓, w2-05-14 ~, w2-05-20 ~, w2-05-23 ~, w1-05-02 ✓, w1-05-03 ✓, w1-05-09 ✓, w1-05-14 ~ ([05](05-product-features.md)); w1-09-01 ✓ to w1-09-03 ✓, w1-09-08 ~ ([09](09-safety-ethics.md)); w1-04-08 ✓ ([04](04-economics-education.md)).
