# Business plan: market, buyers, pricing and evaluation

Wave 1 (overnight 17–18 Nov 2026). Sources: scout notes `work/w1/w1-08.md` (market, buying, evaluation) and `work/w1/w1-05.md` (chatbot access), verifier marks `verify-C.json` (w1-08-*, w1-09-*) and `verify-A.json` (w1-05-*), and the investor panel. Each finding was checked by one blind verifier. Numbers we chose are marked "our choice"; numbers we derived are "our estimate".

**This plan replaces one line from w1-08.** w1-08 rec 2 suggested saying eduX runs inside Gemini on Google school accounts. That is false: Gemini custom apps (MCP) are for users aged 18+, in the US, on personal accounts; school accounts are excluded (w1-05-09 ✓). It is used nowhere below.

## Summary
- **Market: small but growing, England only for now.** A level Economics had 46,365 provisional entries in England in 2026, up 10.7% (w1-08-01 ✓). That is about 90k students on the course at any time (our estimate). Edexcel's share is unpublished.
- **Revenue ceiling, not a forecast:** at £8 per student per year (our choice), all Edexcel Economics students in England would bring £0.2–0.4m a year, depending on Edexcel's share (our estimate). On one subject and board, this is a small business. It grows only by adding subjects, boards and an AI-literacy assessment.
- **Who buys:** the Economics department, with sign-off from the school business manager. Schools make most technology decisions themselves (56%) or with their trust or LA (31%). 95% of leaders cite budget as a barrier (w1-08-03 ✓).
- **Pricing (our choice):** £8 per student per year, minimum £250, students always free. That keeps a department well under DfE's £10k "low value" band, so no tender is needed (w1-08-06 ~).
- **Biggest risk: distribution.** eduX runs inside other companies' chatbots, and none has a tested route for a UK 16–17-year-old. claude.ai is 18+ (w1-05-02 ✓); Gemini custom apps are excluded on school accounts (w1-05-09 ✓). Microsoft Copilot Studio is the one documented per-student route, and it is untested (w1-05-11 ✓, w1-05-13 ~).
- **Cost advantage:** eduX makes no AI model calls, so its marginal cost is hosting. The school's chatbot carries the model cost.
- **Evidence: none yet.** First a feasibility pilot (3–5 schools), which cannot detect learning effects. Then a school-randomised efficacy trial. Even 100 schools detect only about 0.18 SD, two to three times a Khanmigo-sized effect (our calculation; w1-08-08 ✓, w1-09-08 ~).
- **What an investor wants for a second meeting:** a 17-year-old using eduX on a real school tenant, a full 9EC0 pack with measured build hours, three priced letters of intent, and a named technical lead who stays (panel: investor).

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | Remove every "runs inside Gemini" or "any chatbot" line. Use the works-with line from [05](05-product-features.md) ("Tested with claude.ai; ChatGPT and Copilot Studio not yet tested") with the 18+ footnote | pitch, video | S | yes | w1-05-09 ✓, w1-05-02 ✓ |
| 2 | Market slide: 46,365 England entries (+10.7%), about 90k students (our estimate), Edexcel 30/40/50% scenarios, revenue shown as a ceiling, flagged "England only" | pitch | S | yes | w1-08-01 ✓, w1-08-02 ✓ |
| 3 | Pricing line: £8 per student per year, minimum £250, students free (our choice), under the £10k band | pitch | S | yes | w1-08-03 ✓, w1-08-05 ✓, w1-08-06 ~, w1-08-07 ✓ |
| 4 | Cost line: no model calls, so marginal cost is hosting | pitch | S | yes | product design (no finding) |
| 5 | Evaluation slide: feasibility → efficacy; MDES table with the small-sample column; "pilot cannot show learning" | pitch | S | yes | w1-08-08 ✓, w1-09-08 ~ |
| 6 | Distribution answer for Q&A: adults and teachers today; Copilot Studio next (untested); OAuth after | pitch Q&A | S | yes | w1-05-03 ✓, w1-05-11 ✓, w1-05-13 ~ |
| 7 | One competitor line on a slide ("Seneca won't sell to one department; Up Learn charges families"); full table in this plan | pitch | S | yes | w1-08-07 ✓ |
| 8 | Name roles and post-competition commitment on the team slide | pitch | S | yes | panel: investor #5 |
| 9 | DPIA template and one-page safety statement for pilot schools | business plan | M | no | w1-09-01 ✓ to w1-09-06 ✓ |
| 10 | Copilot Studio end-to-end test in a school tenant; find credit cost per call | build | M | no | w1-05-11 ✓, w1-05-13 ~ |

## 1. Market (England-only figures flagged)

| Figure | Value | Scope | Source |
|---|---|---|---|
| A level Economics entries, 2026 (provisional) | 46,365 (2025: 41,880; +10.7%) | **England only**; entries at 15 Apr 2026 | w1-08-01 ✓ |
| All A level entries, 2026 | 845,485 | **England only** | w1-08-01 ✓ |
| Students on the course at any time | about 85–95k (2 cohorts) | England; **our estimate** | from w1-08-01 ✓ |
| State schools with sixth-form places | 1,979 schools, 544,667 places (May 2025) | **England only**; mainstream state; excludes 16–19-only institutions | w1-08-02 ✓ |
| Colleges | about 35 sixth-form colleges and 156 general FE colleges | England; AoC sector list, not official statistics | w1-08-02 ✓ |
| Centres that teach Economics | unknown | Ofqual stopped publishing centre-type figures from 2025 | w1-08-02 ✓ |
| Edexcel share of Economics | unpublished | — | scout search (no source found) |

**Scenarios (our estimate, £8 per student per year, our choice):**

| Edexcel share | Students | Revenue if every one paid |
|---|---|---|
| 30% | about 27k | about £216k |
| 40% | about 36k | about £288k |
| 50% | about 45k | about £360k |

This is a ceiling. Real revenue is a fraction of it. Wales and Northern Ireland mostly use other boards (our estimate, not checked). The UK-wide JCQ figure was not extracted. Growth means more subjects and boards through new course packs, not a higher price.

## 2. Buyers and how schools buy

- **Budget is the barrier.** 95% of leaders cite budget constraints and 93% the high cost of technology (w1-08-03 ✓). *England, LA-maintained and academy schools; colleges and independent schools excluded.*
- **Decisions are local.** 56% of technology decisions are made at school level and 31% jointly with the trust or LA. In secondary academies a school–trust mix is most common (46%). 87% of teachers say their school has a policy for choosing classroom technology, and 56% are guided by it but can make their own choices (w1-08-03 ✓). So a head of department can propose a small tool.
- **Pupil AI is a hard sell.** Leaders plan to invest in AI for teachers far more often than for pupils (58% vs 20%). 73% of secondary teachers think pupils used GenAI for homework; 77% of secondary leaders whose pupils could use GenAI reported problems, mostly plagiarism (67%). Only 34% of secondaries had an AI-use policy (w1-08-04 ✓). *England; teachers' perceptions, not measured pupil use.* So pitch eduX as a way to make pupils' existing chatbot use safer and visible, not as "AI for pupils".
- **Spend is small.** LA-maintained secondaries spent £128 per pupil a year on all ICT learning resources in 2024-25 (w1-08-05 ✓). *England, LA-maintained schools only; most secondaries are academies and are not included.*
- **Buying thresholds.** DfE treats purchases under £10k as low value, £10–40k as medium (at least three quotes) and over £40k as high (w1-08-06 ~). DfE-approved frameworks such as G-Cloud 14 exist for software; that they can be used "at any value" is the scout's inference, not DfE's words (verifier). Schools' own finance rules may be stricter.

**Buyer:** the head of Economics proposes; the school business manager signs. In a multi-academy trust, also brief the trust's digital lead (w1-08-03 ✓).

## 3. Pricing (our choice, with reasoning)

**Department licence: £8 per student per year, minimum £250 a year, invoiced annually. Students never pay. A free student tier always remains.**

Why:
1. **Fits a department budget without a tender.** A large department of 100 students pays £800, far under the £10k low-value band (w1-08-06 ~).
2. **Small next to what schools already spend.** £8 is about 6% of the £128 per pupil that LA-maintained secondaries spend on all ICT learning resources, and it applies only to Economics students (w1-08-05 ✓).
3. **Margins hold at that price.** eduX makes no AI model calls, so its cost per student is hosting, not tokens.
4. **A gap competitors leave.** Seneca licenses Premium only to whole schools or year groups, never one department (w1-08-07 ✓).
5. **No family payments.** Per-student consumer pricing (Up Learn charges £79.99–£104.99 a month, w1-08-07 ✓) puts cost on families. Steering learners to paid options conflicts with DfE std 13 (see the matrix in [09](09-safety-ethics.md)).

**The investor's objection stands:** "heads of department will propose it" often gets cut by business managers in year two (panel: investor #3). Answer it with evidence (priced letters of intent, usage data), not price.

## 4. Competitors (fair table; public pages, 17 Nov 2026)

| Product | What it does | Price (public) | Tracks knowledge per topic? | Assesses AI literacy? | Fair comparison with eduX | Verified? |
|---|---|---|---|---|---|---|
| Seneca | Free revision platform; Premium adds knowledge gaps and mocks; Premium AI+ adds an AI tutor and marking | School Sync free for 12 months, then £646 ex VAT/yr (over 600 pupils); Premium per student by quote, whole school or year group only | Yes | Not described | Huge reach and A level Economics content. Can't be bought by one department. | ✓ (w1-08-07 ✓) |
| Up Learn | A level video lessons, quizzes, retrieval, tutors | £79.99/month Core, £104.99/month Master; schools by quote | Yes | Not described | Complete A level Economics content (AQA, Edexcel) that eduX lacks. eduX is cheaper per student. | ✓ (w1-08-07 ✓) |
| Khanmigo | AI tutor on Khan Academy content | Learners $4/month; teachers free; districts on request | Yes (Khan mastery system) | Not described | Large library and an RCT: small gains, about 0.06–0.08 SD per school year, US middle-school maths (w1-09-08 ~). UK not on its pricing page. | Vendor page, not verified |
| ChatGPT Study Mode / Gemini Guided Learning / Claude learning mode | Socratic modes in the chatbot | Included in the chatbot | Not described | Not described | They shape one conversation. eduX keeps a learner model across sessions, tied to the exam date. **They are also the hosts eduX runs inside, and could ship memory quickly** (investor #2). | Secondary / vendor pages, not verified |
| Eedi | Maths diagnostic questions whose wrong answers map to misconceptions | Not public | Yes, by misconception | No | The closest relative (misconception distractors). Reports trials (own claims). Maths only. | Vendor page, not verified |
| CENTURY Tech | AI-adaptive learning, mainly English, maths, science | Home from £8.33/month | Progress data | Not described | No A level Economics found. | Vendor page, not verified |
| Oak Aila | Free lesson-planning assistant for teachers | Free | n/a | No | Teacher tool, not student-facing. Its public safety write-up is a model for ours. | Vendor page, not verified |

**Fair overall:** every competitor except eduX has shipped content at scale, and Khanmigo and Eedi have trial evidence. eduX's novelty is the architecture (a plan server under the school's chatbot, with no model calls) plus AI-literacy assessment from normal work. Neither has been evaluated. No public product was found that tracks 9EC0 knowledge per part *and* assesses AI literacy (absence after three searches, not proof).

**The moat question** (investor #2): BKT and misconception distractors are not proprietary. Two things the hosts are unlikely to build: (a) a pack pipeline that turns a specification into parts and misconceptions in days, with teacher review; (b) a validated AI-literacy instrument that boards or schools would license. Neither exists yet.

## 5. Distribution risk: the under-18 chatbot route

eduX needs a chatbot that (i) allows a 16–17-year-old in the UK and (ii) can call a custom MCP server. No tested option meets both today.

| Route | Under-18 in UK? | Custom MCP? | Status |
|---|---|---|---|
| claude.ai consumer | No, 18+ (w1-05-02 ✓) | Yes (w1-05-01 ✓) | Tested on an adult account only |
| claude.ai Team/Enterprise held by a school | Unconfirmed (w1-05-03 ✓) | Yes, admin-added | Ask Anthropic (human contact) |
| ChatGPT personal (teens) | 13+ with parental permission (w1-05-08 ~, snippet) | Plan support unclear; Pro read/fetch only (w1-05-06 ~, snippet) | Untested |
| ChatGPT Edu | No page found | "Full MCP" (snippet) | Untested |
| Gemini for Education | Gemini app can be enabled for under-18s (w1-09-04 ✓) | **No** on school accounts (w1-05-09 ✓) | Not possible |
| Microsoft Copilot Studio agent in a school tenant | Copilot Chat for learners 13+, off by default, admin-enabled (w1-05-13 ~) | Yes, per-user API key as query parameter (w1-05-11 ✓) | **Untested; first channel to try.** Copilot Credit cost unknown |

**What we say:** adults (including Year 13s who have turned 18) and teachers can use eduX on their own accounts today. The first school channel is Microsoft Copilot Studio, untested. OAuth (not built) unlocks admin-installed connectors more widely (w1-05-07 ✓, w1-05-12 ✓). Nobody tested a 16–17-year-old on a real school tenant, which is the investor's first test.

## 6. Partnerships and copyright route (Pearson)

**What we do now (fact):**
- Course packs are written in our own words. No Pearson specification text, past papers, mark schemes or examiner reports are reproduced, only summarised (project rule, `work/BRIEF.md`).
- Pearson's 9EC0 examiner reports for 2023–2025 are freely downloadable from Pearson's site (w1-04-08 ✓, existence check). Misconception distractors draw on summaries of them.
- No tutor2u content is reused.
- The exam structure (three written papers, weighted 35/35/30) rests on secondary sources; check it against the specification before it goes on a slide (w1-09-07 ✓, verifier did not check the structure).

**What we propose (our proposal, not researched; no contact made):**
- Ask Pearson, as the awarding body, whether it would license specification wording and past-paper items for in-pack use, or co-badge a reviewed pack. This would make packs faster to build and easier for teachers to trust.
- Until then, keep packs in our own words and add teacher review before any row leaves `draft` (panel: teacher #3 found a wrong correction in `externality_tax_eval_m1`).
- Oak National Academy ships its curriculum as an MCP server to teachers through Claude and ChatGPT (w1-05-14 ~). It is precedent that UK education content can travel this way, and a possible partner for content in other subjects.

**Open questions:** Pearson's terms for using its materials in commercial software; whether Pearson runs any partner programme for this; the cost and hours of a full reviewed 9EC0 pack (investor Q4).

## 7. Regulation and risks

| Risk | What applies | Our response | Source |
|---|---|---|---|
| Under-18 access via chatbot terms | claude.ai 18+; DfE tells schools to follow AI tools' age limits | School-managed tenant only; demo on adult account, said on screen | w1-05-02 ✓, w1-09-05 ✓ |
| DfE Generative AI product safety standards | 13 sections; eduX partly meets, with gaps in safeguarding alerts and data rights | Safety matrix with owner column; fixes ranked in `09-safety-ethics.md` | w1-09-01 ✓ to w1-09-03 ✓ |
| UK GDPR and ICO Children's code | DPIA, data minimisation, profiling off by default, rights tools | Data processing agreement per school; DPIA template; delete/export commands to build | `09-safety-ethics.md` |
| Safeguarding (KCSIE; filtering and monitoring standards) | Schools must name generative AI in their filtering and monitoring review | One-paragraph note for each pilot school's review | w1-09-06 ✓ |
| Assessment malpractice | JCQ and Ofqual AI rules cover coursework and NEA; 9EC0 is exam-only (check the spec) | Low direct risk; a disclosure feature is needed if eduX adds NEA subjects | w1-09-07 ✓ |
| Content accuracy | Every pack row is `draft`; a teacher found an error | Teacher review queue and measured error rate before any pilot | panel: teacher #3 |
| Host dependence | Vendors change MCP terms often (README ChatGPT route already out of date) | Test before claiming; build OAuth; watch Copilot Studio | w1-05-05 ✓ |
| Key security | Keys sit in URLs and are stored in plaintext | Hash, revoke, rotate; OAuth later | [09](09-safety-ethics.md) recs 3–4, 15 |
| Team continuity | All build commits from one committer | Name roles and post-competition commitment | panel: investor #5 |

**Never claim "DfE compliant".** It isn't true, and DfE asks products not to overstate impact (see [09](09-safety-ethics.md)).

## 8. Go-to-market for a student team (our choice)

1. **Now to March 2027: recruit 3–5 pilot Economics departments** through the team's own schools and teacher networks (no contact made). Criteria:
   - Edexcel 9EC0;
   - **a Microsoft 365 education tenant with Copilot Chat for learners enabled**, so Copilot Studio can be tested (untested route; w1-05-11 ✓, w1-05-13 ~); or Year 13 students who are 18+ on their own accounts;
   - a DSL willing to review the safety statement.
2. **Free pilot for one term.** The school signs a data processing agreement and runs a DPIA from our template. eduX acts only on the school's instructions.
3. **From September 2027: department licence** at £8 per student per year, minimum £250 (our choice). Head of department proposes, business manager signs.
4. **Trust-wide deals and framework listings** (for example G-Cloud) only after efficacy evidence, as deals pass £10–40k (w1-08-06 ~).
5. **Lead message:** "Makes your pupils' existing chatbot use visible and safer, and measures AI literacy", answering the plagiarism problem leaders already report (w1-08-04 ✓).

## 9. Evaluation plan

**Stage 1: feasibility pilot (3–5 schools, one term).** It cannot detect learning. With 5 schools and the assumptions below, the minimum detectable effect is about 1.5 SD (our calculation, small-sample multiplier). Outcomes: usage, fidelity (calls per study session, share of turns that follow the plan), teacher time, safety signposts, acceptability, data quality. Deliverable: a draft AI-literacy task set, to be validated later; no validated instrument exists for 16–18s.

**Stage 2: efficacy trial, randomised by school (department).** Primary outcome: learning, on a blind-marked Economics test of 9EC0-style items, including extended writing (teacher Q&A #5). Secondary: AI-literacy task score. Covariate: GCSE prior attainment. Independent evaluator and a funder such as EEF.

**Minimum detectable effect size (our calculation).** Assumptions, all our choice: ICC 0.15, R² = 0.5 at both levels, 20 students per school, half the schools treated, 80% power, 5% two-sided. w1-08-08 ✓ used the large-sample multiplier 2.8. The verifier noted that with few schools the multiplier is larger (about 2.98 at 20 schools). Below we use t-based multipliers with (schools − 3) degrees of freedom.

| Schools | MDES, multiplier 2.8 (w1-08-08 ✓) | MDES, small-sample multiplier (our calculation) |
|---|---|---|
| 5 | 0.78 (our calculation) | about 1.49 |
| 20 | 0.39 | 0.41 |
| 40 | 0.27 | 0.28 |
| 60 | 0.22 | 0.23 |
| 80 | 0.19 | 0.20 |
| 100 | 0.17 | 0.18 |

**What this means:** a realistic edtech effect is small. Khanmigo's was about 0.06–0.08 SD per school year, in US middle-school maths, with 14 of 18 control schools using other edtech (w1-09-08 ~, abstract only). Even 100 schools detect only about 0.18 SD, two to three times that. So a trial is powered to detect a large effect or to rule one out, not to find a Khanmigo-sized one. More students per school, a stronger covariate, or a pooled multi-subject trial would help. The ICC and R² are assumptions to check against EEF guidance. Randomising students within schools needs fewer pupils but invites contamination; it suits feasibility only (scout note w1-08).

**Never present a pilot as showing learning gains.**

## 10. What would make an investor take a second meeting (panel: investor)

1. **A 17-year-old using eduX on a real school tenant, end to end.** Most likely Copilot Studio in a Microsoft school tenant.
2. **A full 9EC0 pack** (not `example-mini`), with measured build hours and a teacher-review error rate. Then show the second subject costs far less than the first.
3. **Three priced letters of intent** from heads of Economics, with the business manager named.
4. **A moat the hosts won't build:** the pack pipeline, or a validated AI-literacy instrument that boards or AI Act Art. 4 deployers would license.
5. **One pilot class's usage data**, labelled as engagement, not learning.
6. **The team:** a named technical lead, roles, and time committed after the competition. 05e (AI-literacy coaching) is built on its branch but not merged; merge it.

## Later (not before Thursday; for the business plan and Q&A)
- Get the UK-wide JCQ Economics entries and any board split.
- Ask Anthropic about under-18 members on school-held Team or Enterprise plans (human contact).
- Ask Pearson about licensing specification wording and past-paper items.
- Check what UK schools pay for Up Learn, Eedi or Seneca Premium (for example on Contracts Finder).
- Measure the hours for a full 9EC0 pack and a teacher's review time per part.
- Check BESA market data and the Procurement Act 2023 thresholds.
- Find out who would pay for AI-literacy assessment (boards, AI Act Art. 4 deployers), and at what price.

## Considered and rejected
- **Per-student consumer pricing (Up Learn style):** puts cost on families, conflicts with DfE std 13 on steering learners to paid options, and hurts equity.
- **Whole-school licence (Seneca style):** eduX is one subject; the department is the buyer (w1-08-03 ✓).
- **The w1-08 rec 2 line placing eduX inside Gemini on school accounts:** false (w1-05-09 ✓).
- **Piloting in Google Workspace schools (w1-08 GTM criterion):** Gemini school accounts can't add custom MCP (w1-05-09 ✓).
- **Claiming "DfE compliant":** not true; gaps remain.
- **Sizing the market from sixth forms × class size:** no official count of centres teaching Economics (w1-08-02 ✓).
- **Using tutor2u's UK entry figure:** secondary source, and the brief bars reusing tutor2u.
- **Planning an efficacy trial ourselves:** needs 60–100 schools and an independent evaluator.

## Panel objections this report answers or leaves open

| Objection (investor unless stated) | Status |
|---|---|
| #1 Distribution runs through competitors; no under-18 route | **Partly**: honest wording and a named first channel; access itself unsolved |
| #1 "Runs inside Gemini" is false | **Answered**: removed |
| #2 Feature, not a company | **Open**: two possible moats named; neither exists |
| #3 Willingness to pay; small prize | **Partly**: sized honestly as a ceiling; no letters of intent yet |
| #4 No content and no evidence | **Partly**: only `example-mini`; the evaluation is a plan (rec 5) |
| #5 Team | **Partly**: roles to name before Thursday (rec 8) |
| Teacher #3: content accuracy | **Partly**: the wrong row is corrected and new rows stay drafts ([04](04-economics-education.md) recs 2–3); review queue later |
| DPO #1: no processor chain for a DPIA | **Partly**: data processing agreement and DPIA template planned; tenant unconfirmed |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-08-01 | England A level Economics entries 41,880 (2025) → 46,365 (2026), +10.7%; 845,485 total | official document | England, all ages | adoption | ✓ |
| w1-08-02 | 1,979 state schools, 544,667 sixth-form places (May 2025); centre-type data no longer published | official document (AoC: practitioner) | England, state mainstream | adoption | ✓ |
| w1-08-03 | 95% budget barrier, 93% cost; decisions 56% school, 31% school+trust/LA; 87% policy exists | official document (survey) | England state schools; colleges, independent excluded | adoption | ✓ |
| w1-08-04 | 44% teachers use GenAI; AI investment for teachers vs pupils 58% vs 20%; 73% think pupils used it for homework; 34% secondaries have a policy | official document (survey) | England state schools | adoption / policy | ✓ |
| w1-08-05 | LA-maintained secondaries: £128/pupil ICT learning resources, £301 non-ICT, £8,351 total (2024-25) | official document | England LA-maintained secondaries only | cost | ✓ |
| w1-08-06 | DfE buying bands: <£10k low, £10–40k medium (3 quotes), >£40k high; software frameworks listed | official document | England schools | policy | ~ "frameworks at any value" is an inference |
| w1-08-07 | Seneca School Sync £646/yr after 12 free months; Premium whole school/year group only; Up Learn £79.99/£104.99 a month | practitioner (vendor page) | UK | cost | ✓ |
| w1-08-08 | MDES 0.39/0.27/0.22/0.19/0.17 at 20/40/60/80/100 schools (multiplier 2.8) | simulation (analytic) | hypothetical English Y12–13 | learning (planned) | ✓ (small-sample multiplier gives about 0.41 at 20 schools) |

Also cited here; each sits in its home report's table: w1-09-07 ✓ ([09](09-safety-ethics.md)), w1-09-08 ~ ([09](09-safety-ethics.md)), w1-05-02 ✓ ([05](05-product-features.md)), w1-05-09 ✓ ([05](05-product-features.md)), w1-05-11 ✓ ([05](05-product-features.md)), w1-05-13 ~ ([05](05-product-features.md)), w1-05-14 ~ ([05](05-product-features.md)), w1-04-08 ✓ ([04](04-economics-education.md)).
