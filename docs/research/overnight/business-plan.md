# Business plan: market, buyers, pricing, unit economics, competitors, copyright and evaluation

Waves 1–4 (overnight 17–18 Nov 2026). Sources:
- Wave 1: `work/w1/w1-08.md`, `work/w1/w1-05.md`; marks in `verify-C.json` and `verify-A.json`.
- Wave 2: `work/w2/w2-08.md` (marks in `verify-H.json`) and `work/w2/w2-05.md` (cost and routes; marks in `verify-E.json`); the investor and DPO panel (`work/w2/panel-investor-dpo.md`).
- Wave 3: `work/w3/w3-08m.md` (Microsoft channel and billing; marks in `verify-K.json`), `work/w3/w3-08c.md` (copyright and Pearson; marks in `verify-N.json`), and the investor section of `work/w3/panel-investor-dpo.md`. The DPO section of that panel is answered in [09](09-safety-ethics.md).
- Wave 4: `work/w4/w4-08.md` (Edexcel's share from Ofqual's market report; whether pupils can reach a custom agent in Copilot), marks in `verify-R.json`. Web search was unavailable: every source was fetched directly (Ofqual's data tables, Microsoft Learn, and Message Center posts read on a third-party mirror).

Each finding has one blind verifier mark. Labels: "our choice" marks numbers we chose; "our estimate" marks numbers we derived.

**Wave 3 changes four things:**
1. **The cost to the school is recomputed from verified Microsoft rates.** It is about £22.50 per student per year in the central case, with a range of £11–108 (our estimate). It replaces the wave-2 US$84 headline, which is now the conservative case.
2. **The unit economics are stated plainly.** Microsoft would take about four times what we take from the same student, and the school has to switch on metered billing to use us at all (§3).
3. **A copyright section is added (§6).** It is not legal advice. It sets what we can say and use today and what needs a licence.
4. **Microsoft's own tutor is now a competitor.** Study and Learn is free and preselected for K-12 students with Copilot Chat on (w3-08m-04 ✓).

**Wave 4 changes three things:**
1. **The market row is filled from Ofqual.** In England in 2024–25, Pearson Edexcel Economics A (9EC0) had 21,005 of 40,795 A level Economics certificates: 51.5% (our arithmetic; w4-08-07 ✓, w4-08-08 ✓). The 30/40/50% scenarios are gone. The ceiling is about £239k a year at £5 (our estimate; w4-08-10 ✓).
2. **A new channel condition.** Microsoft is adding an admin switch that limits students to the Study and Learn agent (MC1548047; w4-08-01 ~). A school that turns it on can't use eduX.
3. **Growth comes through Pearson subjects more than other boards.** Pearson leads in Business, Politics and Maths (w4-08-09 ✓), and AQA bans AI use of its material (w3-08c-10 ✓).

Two scout-note lines stay out: "eduX runs inside Gemini on school accounts" (false: w1-05-09 ✓) and the target market "or ChatGPT/Claude" for pupils (w2-08 rec 3), because neither host has an under-18 route (see [05](05-product-features.md)). The internal "8–30% of sixth forms" guess in w3-08m is also left out: none of its inputs is measured.

## Summary
- **The school pays Microsoft more than it pays us.** On Copilot Studio each `tutor_turn` is an MCP tool call, billed at 5 Copilot Credits in Microsoft's own estimator (w3-08m-06 ✓). A credit costs US$0.01, or £0.0075, pay-as-you-go (w3-08m-07 ✓). Central case: about **£22.50 per student per year**, range **£11–108** (our estimate, assumptions in §3; w3-08m-13 ✓). Against our £5 licence, Microsoft gets about 82% of the school's spend.
- **The billing switch is the school's, and it is off by default.** Pay-as-you-go must be switched on by IT and paid from the tenant's Azure subscription, not the department budget (w3-08m rec 7; panel investor w3 #1). The "free route" is unproven: whether licensed users are exempt is unclear for students (w3-08m-05 ~), and Microsoft's pages disagree on whether a developer-built agent is metered (w3-08m-09 ✓).
- **Gemini and Microsoft both ship free tutoring now.** Gemini tracks progress across sessions (w2-08-01 ✓) and gives teachers insights in Classroom (w2-08-02 ✓). Microsoft's Study and Learn is preselected for K-12 students (w3-08m-04 ✓). What remains for eduX is a *head start*, not a moat: AI-literacy evidence from real chatbot use, and a 9EC0 learner model the school owns across chatbots. Neither is validated, and only claude.ai is tested.
- **Target market: schools on Microsoft 365 Education that switch on Copilot Chat for 16–17-year-olds.** It is the only documented school route, it is untested, and it is off by default (w2-05-04 ✓, w3-08m-04 ✓). No Microsoft page says outright that a school's custom agent works for 13–17s (w4-08-02 ✓). A new admin switch, opt-in, can lock students to Study and Learn and closes the channel in any school that turns it on (w4-08-01 ~). No official survey counts Microsoft vs Google schools (w3-08m-01 ✓).
- **The 9EC0 market is known now, and it is small.** 21,005 A level certificates in England in 2024–25, 51.5% of A level Economics, and growing: up 42% in four years (our arithmetic; w4-08-08 ✓). On about 48k students across two cohorts, the revenue ceiling is about £239k a year at £5 and about £143k at £3 (our estimate; w4-08-10 ✓). That is a ceiling, not a forecast.
- **Re-anchored price (our choice):** £5 per student per year for a department, minimum £100; a trust tier at £3. Students never pay. It sits near the only real school price we have: Sparx Maths at about £1.80–£2.80 per pupil at trust scale (w2-08-06 ✓).
- **Copyright limits the content moat as well as the risk** (§6, not legal advice). The UK education exceptions are non-commercial only (w3-08c-01 ✓). The lawful base is the DfE's openly licensed subject content plus our own words (w3-08c-05 ✓), and anyone can build on that. Say: "Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson."
- **No buyer is required to pay for AI-literacy assessment.** Article 4 of the AI Act needs no measurement and no certificate (w2-08-09 ✓). Government funds competitors through the Pioneer Programme, including Pearson (w2-08-08 ✓).
- **Evidence: none yet.** The pilot can't show learning. Even 100 schools detect only about 0.17 SD (our calculation, large-sample multiplier; w1-08-08 ✓).

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **Moat slide and Q&A:** "Google and Microsoft now ship free tutors inside their own tools. eduX gives the school its own evidence of how pupils use AI (asking and checking) from real use, and a 9EC0 learner model the school owns across chatbots. A head start, not a moat; not yet validated." Never say again that the hosts "shape one conversation". | pitch, video | S | yes | w2-08-01 ✓, w2-08-02 ✓, w2-08-05 ✓, w3-08m-04 ✓ |
| 2 | **Target-market line:** "Sixth forms on Microsoft 365 Education. No official survey counts Microsoft vs Google schools; how many have learner Copilot on isn't published, and finding out is our first pilot task." Don't imply a percentage. If pushed: "Teacher Tapp finds about four in five teachers use Outlook", labelled a teacher-level proxy. | pitch, §1 | S | yes | w3-08m-01 ✓, w3-08m-03 ~, w2-05-04 ✓ |
| 3 | **Price line:** £5 per student per year, minimum £100; trust tier £3; students free (our choice). When asked "Sparx costs a trust £2–3": "Our trust tier matches that; a single A level department pays a little more because it is small." | pitch, §3 | S | yes | w2-08-06 ✓, w2-08-07 ✓ |
| 4 | **Cost line, honest version:** "eduX makes no model calls, so our own cost is hosting. On Microsoft the school also pays Microsoft: 5 credits per eduX call at about 0.75p a credit. At 20 course messages a week that's about £22.50 a student a year, roughly £7.50 a term, on top of our £5. The range is £11 to £108, depending on use. We recommend pay-as-you-go with a monthly cap per class." Don't say a licensed student costs nothing. | pitch Q&A, §3 | S | yes | w3-08m-05 ~, w3-08m-06 ✓, w3-08m-07 ✓, w3-08m-13 ✓ |
| 5 | **Drop every Article 4 "compliance" or "licence the instrument" line.** Keep AI-literacy evidence as value to the school (teacher insight) and possibly to awarding bodies (a task bank), not as a compliance product. | pitch, §4, §10 | S | yes | w2-08-09 ✓ |
| 6 | **Competitor rows:** Gemini (tracking + Classroom insights), **Microsoft Study and Learn (free, preselected for K-12, teacher-assignable from Nov 2026)**, ChatGPT (in-chat quizzes, no tracking found), Claude (US teachers only, connectors to Eedi and ASSISTments), and the Pioneer Programme. | §4, pitch Q&A | S | yes | w2-08-01 ✓ to w2-08-05 ✓, w2-08-08 ✓, w3-08m-04 ✓ |
| 7 | **Distribution answer for Q&A:** adults and teachers today. Sixth-formers next, through a Copilot Studio agent in a Microsoft school tenant, untested. "Microsoft's own posts imply students can choose other agents unless the school locks them to Study and Learn. No Microsoft page says outright that a school's custom agent works for 13–17s, and we haven't tested it. We know of no public UK case of Copilot Studio agents for pupils; our search was limited." | pitch Q&A | S | yes | w2-05-03 ✓, w3-08m-04 ✓, w3-08m-12 ~, w4-08-01 ~, w4-08-02 ✓ |
| 7a | **Market row and slide 8 (Ofqual, England, certificates, 2024–25):** "9EC0: 21,005 of 40,795 A level Economics certificates (51.5%); Pearson incl. Economics B 55.9%; AQA 36.6%; OCR 5.9%; WJEC/Eduqas 1.5%." Replace the 30/40/50% scenarios with one ceiling: about 23,900 a cohort, about 48k students, about £239k at £5 and £143k at £3 (our estimate). Always say "England" and "certificates"; never use Pearson's 55.9% as ours. | §1, pitch | S | yes | w4-08-07 ✓, w4-08-08 ✓, w4-08-10 ✓ |
| 7b | **Add the Study and Learn-only switch as a channel condition** (§1 chain, §7 risk register, §8 pilot filter). Q&A line: "Microsoft now lets a school limit pupils to its own tutor. A school that does that can't use eduX, or any other agent. We're for schools that want a 9EC0-specific tutor and evidence of how pupils use AI." | §1, §7, §8, pitch Q&A | S | yes | w4-08-01 ~ |
| 7c | **Growth sentence:** "Growth comes from more Pearson subjects (Business 52%, Politics 78%, Maths 72% of A level certificates) more than from other boards: AQA, the second Economics board, bans AI use of its material." Add that this deepens dependence on Pearson, which builds its own AI tutoring. | §1, §6, pitch Q&A | S | yes | w4-08-09 ✓, w3-08c-10 ✓, w2-08-08 ✓ |
| 7d | **Deployment checklist for IT:** approve the eduX agent in the Agent Registry; don't apply Block Agents to it; allow it for the Year 12–13 group; leave Study and Learn-only mode off for that group. | 05, §2 | S | yes (text) | w4-08-04 ✓, w4-08-06 ✓, w4-08-01 ~ |
| 8 | **Evaluation slide:** feasibility → efficacy; the MDES table; "a pilot cannot show learning". | pitch | S | yes | w1-08-08 ✓ |
| 9 | **Name roles and post-competition commitment** on the team slide. | pitch | S | yes | panel: investor w1 #5 |
| 10 | **Copyright wording on the title or closing slide and the video end card:** "Built for Pearson Edexcel A level Economics A (9EC0). Not affiliated with or endorsed by Pearson." No Pearson logo, "official", "approved", "examiner-written" or "partner". No Pearson PDF page, question text or mark-scheme text in the public video. | pitch, video | S | yes | w3-08c-09 ✓, w3-08c-12 ✓, w3-08c-13 ✓ |
| 11 | **Pack audit: open-access series only.** Use only papers, mark schemes and examiner reports that Pearson has made public (June 2025 and earlier as of Nov 2026). Never anything reached through a teacher's Edexcel Online login. Note `access: public, downloaded <date>` in the private pack's `sources.csv`. Keep any key wording short, standard and acknowledged. | pack (private), demo | S | yes | w3-08c-03 ✓, w3-08c-06 ✓, w3-08c-07 ✓ |
| 12 | **"Is this legal?" Q&A answer** (§6). Add the DfE open subject content as the named spine of the knowledge graph, with OGL attribution. | pitch Q&A, pack | S (line) / M (pack) | line yes | w3-08c-04 ~, w3-08c-05 ✓ |
| 13 | **Deployment defaults for any Copilot pilot:** standard harness; GPT-5 chat or another standard-rate model, never a reasoning model; pay-as-you-go with a per-agent monthly cap, not a credit pack. (The build steps live in [05](05-product-features.md); its writer owns that change.) | business plan, build docs | S | yes (text) | w3-08m-07 ✓, w3-08m-10 ✓, w3-08m-14 ✓ |
| 14 | **Ask Microsoft (human email, after Thursday):** (i) is a declarative agent with an MCP plugin, used by an unlicensed Copilot Chat user in an education tenant, metered? (ii) can K-12 NotAdult learners use third-party or custom agents? (iii) which harness do new Copilot Studio agents default to? (iv) does the "employee-facing agents only" footnote on the education add-ons page exclude agents built for K-12 students? (v) with Study and Learn-only mode off, can a NotAdult learner use an org-published Copilot Studio agent with an MCP tool? (vi) do the teen protections apply to that agent? Also ask whether the licensed-user exemption covers students, and ask a pilot school's admin to read MC1537656 (admin-only). | business plan | S | no | w3-08m-05 ~, w3-08m-09 ✓, w3-08m-10 ✓, w4-08-01 ~, w4-08-05 ✓, w4-08-11 ~ |
| 15 | **Tenant test that settles the free-route question.** In a school tenant with pay-as-you-go **off**, an admin deploys a developer-built declarative agent with the eduX MCP action. An unlicensed 17-year-old test account uses it. If it answers, it isn't metered. Record credits in the cost dashboards. | build / pilot | M | no | w3-08m-09 ✓ |
| 16 | **Copilot Studio end-to-end test** on a real school tenant with a 17-year-old test account, and the real turn count from one class. Check that the agent appears in the agent store for a NotAdult account and answers; then switch Study and Learn-only mode on and confirm it disappears. Screenshot both. | build | M | no | w2-05-03 ✓, w3-08m-04 ✓, w4-08-01 ~, w4-08-06 ✓ |
| 17 | **Written permission request to Pearson after the competition** (Copyright Manager), separate from any **endorsement application in 2027** (Publisher Relations). A UK IP solicitor reviews the pack process and pitch wording **before we charge anyone**. | business plan | S to write; L overall | no | w3-08c-06 ✓, w3-08c-08 ✓, w3-08c-09 ✓ |
| 18 | **School pack: DPA, DPIA starter and processor-chain diagram.** Outline and Art 28 checklist are now drafted in [09](09-safety-ethics.md); the finished documents aren't written. | business plan | M | no | w2-05-12 ✓; panel: DPO w2 #2, w3 |
| 19 | **Watch the Pioneer Programme's Reading Room standard** and align eduX's safety and tracking documents with it once published. | later | M | no | w2-08-08 ✓ |

## 1. Market (England-only figures flagged)

| Figure | Value | Scope | Source |
|---|---|---|---|
| A level Economics entries, 2026 (provisional) | 46,365 (2025: 41,880; +10.7%) | **England only** | w1-08-01 ✓ |
| Students on the course at any time | about 85–95k (2 cohorts), all boards | England; **our estimate** | from w1-08-01 ✓ |
| State schools with sixth-form places | 1,979 schools, 544,667 places (May 2025) | **England only**; mainstream state | w1-08-02 ✓ |
| Colleges | about 35 sixth-form colleges, 156 general FE colleges | England; AoC list | w1-08-02 ✓ |
| A level Economics certificates by board, 2024–25 | 40,795 in all: Pearson 22,825 (55.9%), AQA 14,940 (36.6%), OCR 2,410 (5.9%), WJEC/Eduqas 620 (1.5%) | **England only**; certificates (results awarded, Oct 2024–Sep 2025), not entries; rounded to 5 | w4-08-07 ✓ (Ofqual market report, Table 10) |
| **9EC0 (Edexcel Economics A) alone** | **21,005 certificates, 51.5%** of A level Economics (our arithmetic). Pearson's 55.9% includes Economics B (9EB0, 1,820). Up from 14,760 in 2020–21 (+42%); share up from 44.8% | England only; certificates | w4-08-08 ✓ (Table 1; shares and growth are our arithmetic) |
| 9EC0 students on the course | about 23,900 a cohort, about 48k across two cohorts | England; **our estimate**: the 2025 certificate share applied to the 46,365 entries of 2026; Year 12 assumed the same size as Year 13 | w4-08-10 ✓ |
| Microsoft vs Google schools | **No official count.** DfE's Technology in Schools survey doesn't ask. Context only: 99% of secondary IT leads report Windows devices and 33% ChromeOS, which is not platform share | England state schools; not FE or sixth-form colleges | w3-08m-01 ✓ |
| Teacher-level proxy | About four in five teachers use Outlook, just over one in five Gmail | England teachers, all phases | w3-08m-03 ~ (the article doesn't date this sentence or tie it to the Nov–Dec 2025 sample) |
| Paid AI add-ons | Since Jan 2023, 34% of IT leads bought increased-capability licences for existing education software; 51% bought none of the AI options listed | England state schools, IT leads, n = 489 | w3-08m-02 ✓ |
| Share of sixth forms with learner Copilot on | **unknown, not published** | — | open question (investor w2, w3) |

**Revenue ceiling (our estimate, at the re-anchored prices, our choice).** The wave-1 to wave-3 scenarios (30/40/50% Edexcel share) are replaced by Ofqual's figure:

| 9EC0 students (England, 2 cohorts) | At £5 (department) | At £3 (trust tier) | Source |
|---|---|---|---|
| about 48k (51.5% of 46,365 entries × 2) | **about £239k a year** | **about £143k a year** | w4-08-10 ✓ (our estimate) |

This is a ceiling, not a forecast. It assumes the 2025 certificate share holds for 2026 entries, that Year 12 is as large as Year 13, and that every 9EC0 student in England pays. Wales and Northern Ireland are not counted.

**The chain of channel conditions.** In practice the reachable market is only the 9EC0 schools that pass every link of this chain, an unknown fraction:
1. are on Microsoft 365 Education;
2. turn on learner Copilot for Year 12–13;
3. **don't lock students to Study and Learn** (the new opt-in switch, MC1548047; w4-08-01 ~);
4. let custom agents through (approve ours in the Agent Registry, don't block agents; w4-08-04 ✓, w4-08-06 ✓);
5. switch on metered billing.

On one subject and one board this is a small business.

**Growth path: more Pearson subjects, not more boards** (our inference).
- AQA, the second Economics board (36.6%), bans AI use of its material (w3-08c-10 ✓). OCR and Eduqas together hold about 7% (w4-08-07 ✓).
- Pearson leads in other large A levels (w4-08-09 ✓; England, certificates, 2024–25):

  | Subject | Pearson's share of certificates |
  |---|---|
  | Politics | 77.6% (15,675 of 20,195) |
  | Mathematics | 72.4% (73,010 of 100,835) |
  | Further mathematics | 69.8% (12,630 of 18,080) |
  | Business | 52.3% (21,320 of 40,755) |

- Each subject needs its own pack and its own copyright check (§6).
- Every one of them deepens our dependence on Pearson, which also builds its own AI tutoring (w2-08-08 ✓).

## 2. Buyers and how schools buy

- **Budget is the barrier.** 95% of leaders cite budget constraints (w1-08-03 ✓).
- **Decisions are local.** 56% of technology decisions are made at school level and 31% with the trust or LA (w1-08-03 ✓). A head of department can propose a small tool.
- **Pupil AI is a hard sell.** Leaders plan to invest in AI for teachers far more often than for pupils (58% vs 20%). 77% of secondary leaders whose pupils could use GenAI reported problems, mostly plagiarism (w1-08-04 ✓). Half of schools bought none of the AI licences DfE asked about (w3-08m-02 ✓). So pitch eduX as making pupils' existing chatbot use safer and visible.
- **Real purchases are direct awards.** Both records found were "below threshold, without competition":
  - Sparx Maths for Dixons: £25,250 ex VAT, 1 Sep 2025 to 31 Aug 2026 (w2-08-06 ✓).
  - Century-Tech for Essex: £68,850 inc VAT over three years (w2-08-07 ✓).

  So trusts and councils do buy adaptive platforms by direct award at about £20–25k a year. Notices of £30k or more inc VAT appear on Find a Tender. No records were found for Up Learn, Seneca or Eedi (not found by these methods, which is not proof of absence).
- **Buying thresholds.** DfE treats purchases under £10k as low value, £10–40k as medium (three quotes) and over £40k as high (w1-08-06 ~).

**Buyers: there are two budgets.** The head of Economics proposes and the school business manager signs our licence. On Microsoft, **the IT admin is a second buyer**: they switch on learner Copilot, build the agent and approve it in the Agent Registry (w4-08-06 ✓), keep Study and Learn-only mode off for Year 12–13 (w4-08-01 ~), switch on pay-as-you-go and pay Microsoft for the credits. In a trust, also brief the digital lead.

## 3. Pricing and unit economics

### Our price (our choice)

**Department licence: £5 per student per year, minimum £100 (covers up to 20 students). Trust tier: £3 per student per year across five or more schools. Students never pay.** All three numbers are our choice.

Why £5, not wave 1's £8:
1. **Anchor on what schools pay, not on budget shares.** Wave 1 set £8 as about 6% of the £128 per pupil that LA-maintained secondaries spend on ICT learning resources (w1-08-05 ✓). That was a share of a budget, not a market price. The best real price we have is Sparx Maths at about £1.80–£2.80 per pupil per year at trust scale (our estimate on an assumed headcount, a lower bound; w2-08-06 ✓).
2. **The trust tier matches Sparx; the department price sits above it.** A department has tens of students, and setup, the DPA and support cost us about the same per school (our assumption).
3. **A low minimum keeps £5 the real price.** A department of 20 or more pays £5 per student; one of 10 pays £10. Department sizes are our assumption.
4. **Well under the £10k low-value band,** so no tender is needed (w1-08-06 ~).
5. **No family payments.** Charging families conflicts with DfE std 13 (no steering learners to paid options) and hurts equity ([09](09-safety-ethics.md)).

**Test the price with priced letters of intent, not argument.** The investor's objection stands until three heads of Economics sign one, with the credit cost shown next to our price.

### What the school pays Microsoft (our estimate on verified rates)

**What is verified** (rates, not the per-student total):
- An agent tool invocation, with MCP listed explicitly, costs **5 credits** in Microsoft's Copilot Credit estimator, which adds no generative-answer charge to a tool message (w3-08m-06 ✓).
- The billing page charges a generative answer at 2 credits and an agent action at 5 on the standard harness (w3-08m-05 ~).
- Pay-as-you-go is **US$0.01 per credit, £0.0075** in Azure's GBP price list, effective 1 Sep 2025. A prepaid pack is **£153.80 (US$200) for 25,000 credits a month** (w3-08m-07 ✓). The GBP figure is Azure's currency conversion, not a separate UK price.

**Assumptions behind our estimate (all ours):**
- One `tutor_turn` per course message. Turns per student per year are **our choice**: 300, 600 (central: 20 a week × 30 weeks) or 1,200.
- 5 credits a turn follows the estimator. If the 2-credit generative-answer charge also applies, it is 7. Two tool calls in a turn is 12.
- The **standard harness**. The newer Copilot harness bills tokens and tools, and bills from build time (w3-08m-10 ✓).
- A **non-reasoning model**. A reasoning model adds 10 credits per 1,000 tokens; Microsoft's own example is 141–461 credits for one message (w3-08m-14 ✓).
- A student **without** a Microsoft 365 Copilot licence.
- List prices, ex VAT. VAT treatment for schools is not checked. No education discount was found.

| Case | Turns / student / year (our choice) | Credits / turn | Credits / year | £ / year (PAYG) | US$ / year | £ / term |
|---|---|---|---|---|---|---|
| Low | 300 | 5 | 1,500 | 11.25 | 15 | 3.75 |
| **Central** | **600** | **5** | **3,000** | **22.50** | **30** | **7.50** |
| Conservative (the wave-2 figure) | 1,200 | 7 | 8,400 | 63.00 | 84 | 21.00 |
| High | 1,200 | 12 | 14,400 | 108.00 | 144 | 36.00 |
| Reasoning model (avoid) | 600 | ≥ 141 | ≥ 84,600 | ≥ 634 | ≥ 846 | ≥ 211 |
| Student with an M365 Copilot licence | any | **unclear** | — | — | — | — |

Arithmetic checked by the verifier (w3-08m-13 ✓). The per-student figures are **our estimate**; no school has been billed yet.

**The licensed-user exemption is unclear for students.** The billing page says there's no charge when a user with an M365 Copilot licence runs the agent under their own identity. The verifier notes that this footnote is framed as employee-facing use, and other footnotes add exceptions (w3-08m-05 ~). The academic licence is about US$18 a user a month (unverified, wave 2), far above metered use anyway. **Don't say a licensed student costs nothing.**

**Pack or pay-as-you-go?** A pack works out at £0.00615 a credit only if every credit is used. It beats pay-as-you-go only above about 20,500 credits a month (£153.80 ÷ £0.0075, our arithmetic). A class of 20 in the central case uses about 6,000 a month over 10 active months, and a department of 60 about 18,000. Both are below breakeven. Pack credits don't roll over, and other agents share the pool. **Recommend pay-as-you-go with a per-agent monthly cap** (w3-08m-07 ✓).

### Unit economics, confronted

| Per student per year, central case | Paid to | Paid from |
|---|---|---|
| £5.00 | eduX (our licence, our choice) | the department or school budget |
| about £22.50 (range £11–108) | Microsoft (Copilot Credits, our estimate) | the tenant's Azure subscription, run by IT |
| **about £27.50 in all (range about £16–113)** | | |

- **Microsoft earns about 4.5 times what we do on our own customer** (panel investor w3 #1). Microsoft's share is about 82% of the school's spend in the central case (our arithmetic).
- **Who pays: the school, from two budgets.** The department pays us. IT pays Microsoft. The credit cost is a finance-office decision, not a department line, and that is the harder sale.
- **Pay-as-you-go is off by default.** A school has to switch on metered billing before eduX can run at all (w3-08m rec 7; panel investor w3 #1; this default is not a separately verified finding). Every pilot school needs an IT admin willing to do it.
- **Our margin is still hosting only,** because eduX makes no model calls. That is true, and it doesn't lower the school's total. Never say "zero running cost" or "cheaper than a chatbot".
- **Our price can't fix this.** Cutting £5 to £0 still leaves £22.50. Raising it adds to a total that already worries a business manager.
- **What can move the total:**
  1. fewer calls: eduX only on course messages, never on chit-chat (the central case already assumes this);
  2. a standard-rate model and the standard harness;
  3. a monthly cap per class: about 6,000 credits, **about £45 a month for a class of 20** in the central case (our arithmetic). That is the number the investor asked for;
  4. the free route, if it exists. One Microsoft table lists custom actions in Copilot Chat with no usage-based billing, but two other Microsoft pages say custom-agent use is pay-as-you-go (w3-08m-09 ✓). **Test it (rec 15). Don't pitch it.**
- **Not a route: Agent Builder.** It skips the generative-answer charge, but it can't author actions that call external services, so it can't call MCP (w3-08m-08 ✓).
- **The investor's test:** the real turn count from one class, and a priced cap per class. Until then the honest answer is "£11–108, central £22.50", not "maybe zero".

## 4. Competitors (public pages, 17–18 Nov 2026)

| Product | What it does | Price (public or procured) | Tracks progress across sessions? | Assesses AI literacy? | Fair comparison with eduX |
|---|---|---|---|---|---|
| **Gemini study notebooks** | Splits a goal into 100+ objectives grouped by topic; diagnostic quiz; progress dashboard | Included | **Yes** (w2-08-01 ✓). School accounts incl. under-18s were promised "in the coming weeks" (June 2026); rollout not confirmed | Not described | Tracks progress from a student's uploads inside Google. eduX tracks against a teacher-reviewed 9EC0 map and measures AI-use behaviour, but can't run on Google school accounts at all |
| **Guided Learning in Google Classroom** | Teacher-assigned Guided Learning on course materials, with progress insights | Included | **Yes, teacher-facing** (w2-08-02 ✓). UK pilot: Ark, 3 schools, 4 weeks; measured perceptions, not attainment | Not described | A direct competitor for teacher visibility, free to Google schools |
| **Microsoft Study and Learn** | Microsoft's own learning agent in Copilot Chat; preselected when enabled K-12 students open Copilot Chat; teacher assignment "available to all in November 2026" | Included | Not described in the sources read | Not described | **A free default the student is already in, on our target channel** (w3-08m-04 ✓). eduX's difference is the 9EC0 learner model and AI-literacy evidence, not tutoring as such |
| ChatGPT study mode / quizzes | Socratic mode; in-chat interactive quizzes (Sept 2026) | Included | None found as of Nov 2026 (w2-08-03 ✓). Absence after search, not proof | Not described | Say "we found no public evidence", not "ChatGPT can't" |
| Claude learning mode / Claude for Teachers | Socratic style for adults; US teacher tools, free to verified US K-12 educators to 30 Jul 2028 | Free for US teachers | No student tracking described; connectors to Eedi, ASSISTments and others (w2-08-04 ✓, w2-08-05 ✓) | No | Precedent that learner-model tools plug into hosts. It helps credibility and weakens novelty |
| Sparx Maths | Maths homework, ages 11–16 | Dixons: £25,250 ex VAT/yr; about £1.80–£2.80 per pupil (our estimate; w2-08-06 ✓) | Yes | No | Proven and cheap at scale. Not A level |
| CENTURY Tech | Adaptive platform with its own content | Essex FE: £68,850 inc VAT over 3 years (w2-08-07 ✓) | Yes | Not described | No A level Economics found |
| Eedi | Misconception-based diagnostic questions | US pricing seen only in a snippet (not used) | Yes, by misconception | No | The closest relative. Now a Pioneer supplier and a Claude connector |
| Khanmigo | AI tutor on Khan content | Learners $4/month or $44/year; teachers free; no UK (w2-08-12 ✓) | Yes (Khan mastery) | Not described | Large library and an RCT (0.06–0.08 SD per year, US maths; w1-09-08 ~). No A level Economics |
| Seneca | Free revision; Premium by quote, whole school or year group only | School Sync £646 ex VAT/yr after 12 free months (w1-08-07 ✓) | Yes | Not described | Huge reach and A level Economics. Describes its courses as written by "senior examiners" (w3-08c-13 ✓); we can't say that (§6) |
| Up Learn | A level video lessons, quizzes; "exam-board specific" courses (w3-08c-13 ✓) | £79.99–£104.99 a month consumer; schools by quote (w1-08-07 ✓) | Yes | Not described | Complete content eduX lacks |
| Barton Peveril's own tools | A sixth-form college's own LLM front end and assistant inside its Google tenancy, paid per token, free to students; about 5,000 students trained in AI literacy | Self-built | Not described | Training, not assessment | Practitioner self-report; user counts inconsistent (w3-08m-11 ✓). A possible later MCP channel, not a pivot |
| Regulated AI qualifications | 44 on the Ofqual register with "artificial intelligence" in the title; none from AQA, OCR or Pearson (w2-08-10 ✓) | Fees not on the register | n/a | Certify taught skills | eduX gathers evidence from normal study; it is not a qualification |
| **AI Tutoring Tools Pioneer Programme** | DSIT/DfE R&D contracts: Medly AI, Zero Gravity, Learn Anything, Flint, Pearson, ElevenLabs, Eedi, Google UK | £300k ex VAT each, 29 Jun 2026 to 31 Mar 2027 (w2-08-08 ✓) | One eligible product type is progress tracking | — | Years 9–10, disadvantaged schools. Not A level |

**Fair overall:** every competitor has shipped content or reach at scale. Google and Microsoft now give tutoring away inside their own tools. eduX's honest difference is narrow:
1. **AI-literacy evidence (Ask, Verify) from pupils' real chatbot use.** We found no other product that does this (absence after search, not proof). Where the school doesn't teach AI literacy, these scores are off by default ([09](09-safety-ethics.md)), which narrows the offer further.
2. **A learner model the school owns, independent of the host.** Today that independence is a design, not a fact: only claude.ai is tested.

Both are unvalidated head starts, not a moat (coordinator wording).

**Moat question (investor w1 #2, w2 #3, w3 #4).**
- (a) **A pack pipeline** that turns a specification into parts and misconceptions in days, with teacher review. It stands, unbuilt at full scale. Wave 3 weakens it: the lawful spine is open DfE content plus our own words (w3-08c-05 ✓), which anyone can build, including Pearson. What's left is speed and cost per pack, unmeasured.
- (b) **"A validated AI-literacy instrument that boards or AI Act Art. 4 deployers would license."** Dropped: Article 4 needs no measurement or certificate (w2-08-09 ✓). What's left is a possible task bank for awarding bodies or PISA-style tasks (w2-08-11 ✓), speculative and with no buyer named.

**Pearson.** 9EC0's awarding body is a Pioneer supplier building its own AI tutoring (w2-08-08 ✓). The investor asks why Pearson would license to us, or what stops it copying the pack. Our only answers are host-neutrality and the hours per pack, and both are unproven.

## 5. Distribution: the under-18 chatbot route

Full table in [05](05-product-features.md).

| Route | Under-18 in UK? | Custom MCP? | School can deploy and put in a DPIA? | Status |
|---|---|---|---|---|
| **M365 Education + Copilot Studio agent** | Copilot Chat for 13–17 only after the admin sets K-12 + NotAdult, with an A1/A3/A5 student licence; off by default (w2-05-04 ✓, w3-08m-04 ✓). **No Microsoft page says outright that custom agents reach NotAdult learners**: the learners pages list only Copilot Chat, Study and Learn and Notebooks (w4-08-02 ✓). Microsoft's own tutor for 13+ is a declarative agent, the same type a school builds (w4-08-03 ✓). An opt-in admin switch, rolling out mid-Nov to mid-Dec 2026, limits students to Study and Learn; with it on, they can't use other agents (MC1548047, read on a third-party mirror; w4-08-01 ~) | Yes. Key in a header or query, or OAuth 2.0 (w2-05-03 ✓); a developer-built declarative agent can also call MCP (w3-08m-09 ✓) | Yes, on paper | **Untested. The target channel.** About £22.50 per student per year in credits, central (our estimate, §3) |
| Mistral Le Chat (personal) | 13+ with parental permission (w2-05-01 ~) | Yes (w2-05-02 ✓) | **No**: consumer terms, no DPA | Personal only; not a pupil route we offer |
| claude.ai consumer | No, 18+ (w1-05-02 ✓) | Yes | n/a | Tested on an adult account |
| claude.ai Team / Enterprise / Education | Unconfirmed (w1-05-03 ✓) | Yes | Unclear | Ask Anthropic |
| ChatGPT Teens / Edu / for Teachers | Teens: auto-placed, MCP undocumented. For Teachers: US staff only (w2-05-14 ~, snippet) | Unclear | No | Untested |
| Gemini for Education | Yes, restricted | **No** custom MCP (w1-05-09 ✓) | n/a | Not possible |
| A college's own LLM front end | Depends on the college | Unknown | Yes, if the college contracts | Later channel to note (w3-08m-11 ✓) |

**What we say:** adults (including Year 13s who have turned 18) and teachers can use eduX on their own accounts today. The first school channel is a Microsoft Copilot Studio agent, untested. "Microsoft's own posts imply students can choose other agents unless the school locks them to Study and Learn. No Microsoft page says outright that a school's custom agent works for 13–17s, and we haven't tested it." The first part is **our inference** from MC1548047, which says only that students in the locked mode can't use "other agents"; it doesn't name custom MCP agents (w4-08-01 ~). Don't cite the add-ons page's "employee-facing agents only" footnote either way: the page is partly stale and its meaning is unclear (w4-08-05 ✓); it is a question for Microsoft (rec 14). We know of no public UK case of Copilot Studio agents for pupils (w3-08m-12 ~: a negative search, and the Harris Federation event page doesn't say its agents are staff-only). Nobody has tested a 16–17-year-old on a real school tenant, which is the investor's first test.

## 6. Copyright and the exam-board route

> **This is not legal advice.** It is a summary of primary law and published policies, written by non-lawyers for planning. **Before eduX charges anyone, a UK IP solicitor reviews the course-pack process and the pitch wording.**

**The law, briefly:**
- **The education and research exceptions are non-commercial only.** These are research and private study (s.29, with s.178), illustration for instruction (s.32, which covers setting and answering exam questions) and educational copying (s.36, at most 5% of a work in 12 months, and not where a licence is available). They protect a teacher's own classroom use, not a paid service (w3-08c-01 ✓).
- **Text and data analysis (s.29A) is non-commercial research only,** and the copy can't be passed on or used for another purpose. A pack built under a research exception during the competition can't simply become the product (w3-08c-02 ✓).
- **Quotation (s.30(1ZA)) is the one exception a business can use.** It needs fair dealing, no more than the purpose requires, and acknowledgement (title and author). A contract can't override it (w3-08c-03 ✓). Systematic quotation across every mark scheme may still not be "fair".
- **Ideas and facts are free; wording and selection are not.** Infringement covers a "substantial part", taken directly or indirectly (s.16(3)). A specification's content list may be protected as a selection and arrangement (s.3A). Exam papers were held to be protected literary works in 1916 (w3-08c-04 ~: the case rests on a secondary summary; the judgment was not read).
- **The law isn't moving our way.** The government's March 2026 report dropped a broad opt-out TDM exception as its preferred option and left AI licensing to the market (w3-08c-11 ✓). Plan on licences, not a coming exception.

**Pearson's own rules:**
- Specifications, past papers and mark schemes **may not be copied or made available electronically without permission**. Only approved centres have a standing exemption: within the centre, free, on a non-public intranet, unaltered, kept at most 5 years after the series (w3-08c-06 ✓). We don't assume a school's exemption extends to eduX.
- **Papers, mark schemes and examiner reports are restricted to Pearson centres for 12 months after each series** ("normally"; it can be longer), then open access from August for the previous summer's series (w3-08c-07 ✓). As of Nov 2026, June 2025 and earlier are public. **Examiner reports are free to download, not free to reuse** (this corrects wave 1's "freely downloadable", w1-04-08 ✓).
- **Pearson's UK legal notice reserves text and data mining and AI-training rights** (w3-08c-08 ✓). Whether it governs downloads from the qualifications site is unconfirmed. Treat AI extraction from Pearson PDFs as needing permission once eduX is commercial.

**Two separate Pearson routes. Don't mix them up:**
1. **Copyright permission** (Copyright Manager; copyrightPQS@pearson.com on the policy pages, copyright@pearson.com in the publication policy). Ask after the competition, item by item: may an AI model process public papers and mark schemes to build a private own-words pack; may students see short acknowledged key wordings; may a school supply its centre copies to eduX as its processor; on what terms and fee (w3-08c-06 ✓, w3-08c-07 ✓).
2. **Endorsement** (Publisher Relations, endorsement policy v1.9). It covers print and digital resources, is open and non-exclusive, and checks accuracy against the specification or the part a resource supports. **It does not grant copyright permission.** Endorsed resources must not be called "official" or imply examiner input (w3-08c-09 ✓). Apply in 2027 at the earliest, once a teacher-reviewed pack covers a defined part of 9EC0 (Theme 1, say). Present eduX as a host-neutral layer that complements Pearson's own tutoring, and expect Pearson to compete.

**A lawful spine.** The DfE's *GCE AS and A level subject content for economics* (2014) is Crown copyright under the **Open Government Licence v3.0**. It sets the areas of study that make up **60% of any A level economics specification** (w3-08c-05 ✓). Build the knowledge graph on it plus our own breakdown into parts, with attribution. Keep `spec_ref` as a bare pointer to 9EC0 sections, and don't copy the specification's headings or their order as node names. The other 40% must be our own words.

**Other boards.** AQA bans any use of its material to train AI tools, and bars it from any third-party work with AI-generated parts. It grants only a limited number of print and eBook permissions (w3-08c-10 ✓). OCR's pages say nothing on AI. **No AQA or OCR material without written permission**, and never claim "works for any board".

**Licensing bodies don't cover us.** The CLA Schools Licence is held for schools and keeps copies within the institution. The CLA Generative AI licence covers only content that rights holders opt in, and we don't know whether Pearson has (w3-08c-14 ✓).

**What we can say and do (not legal advice):**

| Act | Status | Basis |
|---|---|---|
| "Built for Pearson Edexcel 9EC0. Not affiliated with or endorsed by Pearson." | **OK now**, with no logo and no "official", "approved", "partner" or "examiner-written" | TMA s.11(2)(c), honest practices (w3-08c-12 ✓); endorsement rules (w3-08c-09 ✓) |
| Refer to a question by series, paper and number, and link to Pearson's public page | **OK now** (a fact, not expression) | w3-08c-04 ~, w3-08c-06 ✓ |
| Own-words notes, concepts, misconceptions, marks, command words | **OK now**, if they don't mirror the specification's wording or arrangement | w3-08c-04 ~, w3-08c-05 ✓ |
| Short key wording from a mark scheme, shown with acknowledgement | **Uncertain**: quotation may cover it; systematic use weighs against fairness | w3-08c-03 ✓ |
| Close paraphrase of question or mark-scheme text | **Uncertain to infringing** | w3-08c-04 ~ |
| **Needs a licence:** a whole paper, mark scheme or specification shown to students; AI extraction from Pearson PDFs into a commercial pack; any AQA material | **Needs permission** | w3-08c-01 ✓, w3-08c-02 ✓, w3-08c-06 ✓, w3-08c-08 ✓, w3-08c-10 ✓ |
| Material from the 12-month restricted window, reached through a teacher's login | **Don't** | w3-08c-07 ✓ |
| A school supplies its own copies to eduX | **Uncertain**: ask Pearson | w3-08c-06 ✓ |

**Comparators use the same register.** Seneca, Up Learn and Oak describe alignment to boards, not partnership (w3-08c-13 ✓). Oak's newer content is under the OGL and may be used commercially; we didn't check whether Oak has A level economics.

**Pitch answer to "is this legal?" (draft):** "We store no Pearson text in the product. The pack is our own notes, built on the DfE's openly licensed subject content and pointing to 9EC0 section numbers. Any short exam wording is quoted with its source. We use only papers Pearson has made public. Showing past-paper questions would need Pearson's permission, and we'd ask for it separately from endorsement. We're not affiliated with Pearson."

**Partnership precedent.** Oak's MCP server and Claude for Teachers' Eedi and ASSISTments connectors show that education tools travel this way (w1-05-14 ~, w2-08-05 ✓). A partner awarding body could use eduX evidence for a small L1/L2 AI award (speculative; w2-08-10 ✓).

## 7. Regulation and risks

| Risk | What applies | Our response | Source |
|---|---|---|---|
| Under-18 access | claude.ai 18+; DfE tells schools to follow age limits; no Microsoft page says outright that custom agents reach K-12 learners | Microsoft school tenant only for pupils; demo on an adult account, said on screen; ask Microsoft (rec 14) | w1-05-02 ✓, w2-05-04 ✓, w3-08m-04 ✓, w4-08-02 ✓ |
| **Study and Learn-only mode** | An admin switch (opt-in; "no action is required") limits A1/A3/A5 students to Microsoft's tutor; with it on, students can't select other agents, including from the agent store. Rolls out mid-Nov to mid-Dec 2026, "in response to customer demand". Read on a third-party mirror of the Message Center | Treat it as a channel condition: any school that turns it on is closed to eduX. Pilot filter (§8). Q&A line (rec 7b). Tenant test with the switch on and off (rec 16). It could shrink the channel in exactly the schools that care most about productive struggle | w4-08-01 ~ |
| **Host cost (Copilot Credits)** | About £22.50 per student per year central, £11–108 (our estimate on verified rates); pay-as-you-go off by default | Standard model and harness; fewer calls; per-class cap; test the free route | w3-08m-06 ✓, w3-08m-07 ✓, w3-08m-13 ✓ |
| **Competitor capture** | Gemini tracking and Microsoft Study and Learn, free; Pearson, Eedi and Google funded by the Pioneer Programme | Lead on AI-literacy evidence and the 9EC0 learner model; track the Reading Room standard | w2-08-01 ✓, w2-08-08 ✓, w3-08m-04 ✓ |
| **Copyright** | Non-commercial exceptions; Pearson's restrictions and TDM reservation; AQA's AI ban | §6; solicitor before charging; permission request after the competition | w3-08c-01 ✓ to w3-08c-10 ✓ |
| DfE product safety standards | Partly met; gaps in safeguarding and data rights | Fixes ranked in [09](09-safety-ethics.md); **none built yet** | w1-09-01 ✓ to w1-09-03 ✓ |
| UK GDPR, Children's code | Public task; DPIA; Art 28 contract; retention | School pack outlined in [09](09-safety-ethics.md) (rec 18) | [09](09-safety-ethics.md) |
| Key security | Key in the URL, stored in plaintext | Header (S), hash and revoke (S), Entra (M); none built | w2-05-10 ✓, w2-05-11 ✓ |
| AI Act Art. 4 | No measurement, no certificate needed | **Not a revenue line** | w2-08-09 ✓ |
| Content accuracy | Every pack row is `draft` | Teacher review queue before any pilot | panel: teacher w1 #3 |
| Team continuity | One committer | Name roles and commitment | panel: investor w1 #5 |

**Never claim "DfE compliant".**

## 8. Go-to-market (our choice)

1. **Now to March 2027: recruit 3–5 pilot Economics departments** through the team's own networks (no contact made). Criteria:
   - Edexcel 9EC0;
   - **a Microsoft 365 Education tenant whose IT admin will switch on Copilot Chat for Year 12–13, build the agent, and switch on pay-as-you-go with a per-class cap** (about £45 a month for a class of 20, central; our estimate);
   - **the school does not plan to switch on Study and Learn-only mode for Year 12–13** (w4-08-01 ~), and IT will approve the agent in the Agent Registry (w4-08-06 ✓);
   - a DSL willing to review the safety statement.

   Year 13s who are 18+ may use their own accounts meanwhile. Google Workspace schools are not pilot candidates, unless they run their own LLM front end (later).
2. **Free pilot for one term.** The school signs eduX's DPA and runs a DPIA from our outline ([09](09-safety-ethics.md)).
3. **From September 2027: department licence** at £5 per student, minimum £100, and a trust tier at £3 (our choice). Every quote shows the expected credit cost next to our price.
4. **Lead message:** "Teaches your pupils to check what AI tells them, inside the Copilot your school already runs, and tracks their 9EC0 knowledge." Class-level AI-literacy evidence is an extra only for schools that teach AI literacy (off by default; [09](09-safety-ethics.md)). It answers the plagiarism problem leaders report (w1-08-04 ✓).
5. **Pilot measures:** engagement and fidelity, the teacher's use of the starter MCQ and re-check accuracy ([05](05-product-features.md)), and **the credits actually billed per student**. None of this is learning.

## 9. Evaluation plan

**Stage 1: feasibility pilot (3–5 schools, one term).** It cannot detect learning. With 5 schools the MDES is about 1.5 SD (our calculation). Outcomes: usage, fidelity, teacher time, credits billed, safety signposts, acceptability, data quality. A one-page pilot plan with preregistered progression criteria is drafted in `work/w3/w3-02e.md` §2. Its research uses need a named controller and ethics approval first ([09](09-safety-ethics.md)).

**Stage 2: efficacy trial, randomised by school.** Primary outcome: learning, on a blind-marked test of 9EC0-style items including extended writing. Secondary: an AI-literacy task score. Covariate: GCSE prior attainment. An independent evaluator and a funder such as EEF.

**MDES (our calculation).** Assumptions (our choice): ICC 0.15, R² = 0.5, 20 students per school, half the schools treated, 80% power, 5% two-sided.

| Schools | MDES, multiplier 2.8 (w1-08-08 ✓) | Small-sample multiplier (our calculation) |
|---|---|---|
| 5 | 0.78 | about 1.49 |
| 20 | 0.39 | 0.41 |
| 40 | 0.27 | 0.28 |
| 60 | 0.22 | 0.23 |
| 100 | 0.17 | 0.18 |

A realistic edtech effect is small: Khanmigo's was 0.06–0.08 SD per year (w1-09-08 ~). The ASSISTments bundle gave g = 0.18 in US grade 7 maths (w2-05-20 ~, secondary), and dashboards alone show no attainment effect (w2-05-23 ~). **Never present a pilot as showing learning gains.** The investor's point stands: learning evidence is 2028 at best, beyond a seed runway (investor w3 #5).

## 10. What would make the investor take a second meeting

The wave 3 verdict: "Still no, but this is the first wave that gives me numbers I can model, and the numbers are not good." The investor's conditions, merged across waves:
1. **A 17-year-old using eduX on a real Microsoft school tenant, end to end**, with a date and a tenant. Or Microsoft's written yes that K-12 NotAdult learners can use custom agents.
2. **The total cost per student, all in:** "£5 to us plus about £22.50 to Microsoft, capped at £X per class per month", with the real turn count from one class. The free route tested, not assumed.
3. **The size of the channel:** how many English sixth forms and colleges run M365 with learner Copilot on. Today: not published.
4. **An answer to "why pay twice when Study and Learn is free?"**: a teacher who chose eduX over it for 9EC0 and for AI-literacy evidence.
5. **One paying buyer for AI-literacy evidence** (a school, trust or awarding body). Article 4 no longer supplies one.
6. **Three priced letters of intent** from heads of Economics, with the business manager named, at the re-anchored price and with the credit cost shown.
7. **An answer to "what stops Pearson copying the pack?"**: hours and error rate per pack on a full 9EC0 pack. *(Edexcel's share is now answered: 9EC0 had 51.5% of A level Economics certificates in England in 2024–25; w4-08-08 ✓.)*
8. **Spring results against preregistered criteria**, labelled feasibility and use, with paid renewals.
9. **The team:** a named technical lead and post-competition commitment. 05e is built on its branch but not merged; merge it.

**Q&A lines the investor wants (wave 3):**
- *Total cost per student?* "£5 to us plus about £22.50 to Microsoft in our central estimate, £11–108 depending on use. We recommend a cap of about £45 a month per class of 20."
- *Can a 16-year-old reach a custom agent?* Only "Microsoft confirmed it on [date]" or "a test account did" counts. Today: "not yet tested".
- *Why pay twice when Study and Learn is free?* "Study and Learn doesn't know 9EC0 and doesn't report AI literacy to the school."
- *What stops Pearson copying the pack?* "Our cost per pack in hours, and host-neutrality." Both unproven.
- *What does spring prove?* "Feasibility and use, against criteria we registered in advance. Not learning."

## Later (not before Thursday)
- Microsoft: the three questions in rec 14; the tenant test (rec 15); the real cost per student per term once a pilot bills.
- The share of English sixth forms with learner Copilot on. Routes: a DfE FOI, Microsoft's or Google's UK education teams, or regional broadband consortia data.
- 9EC0's share of the **2026 entries** (Ofqual's provisional entries don't split by board; the next market report, about March 2027, will), and 9EC0 numbers in Wales and Northern Ireland (Qualifications Wales, CCEA; not read). The 2024–25 certificate share is answered (w4-08-08 ✓).
- How many UK schools will turn on Study and Learn-only mode. Nothing is published; ask Microsoft UK Education or the pilot schools.
- What MC1537656 ("Copilot access configuration for your education tenant", 4 Nov 2026) says. Only tenant admins can read it (w4-08-11 ~).
- Sixth-formers' real turns per week in published usage data (Sparx, Seneca, Khanmigo), to tighten the turn assumption.
- Do any UK schools enable Copilot pay-as-you-go for students, and under what cap?
- Colleges with their own LLM front end as a later MCP channel (w3-08m-11 ✓).
- Pearson: the permission request and its fee (rec 17); whether the TDM reservation covers the qualifications site; whether Pearson opted into the CLA Generative AI licence; whether any team member or advising teacher is a Pearson examiner (Pearson's author policy would then apply).
- Whether a student competition entry counts as "non-commercial" for ss.29 and 29A while the team writes a business plan. Not answered; don't assert either way.
- Whether Gemini study notebooks have reached UK under-18 school accounts. Dixons' 11–16 headcount. School quotes for Up Learn, Seneca and Eedi.
- When the Pioneer Reading Room standard is published. PISA 2029 MAIL dates (unverified; don't quote dates).
- Ask Anthropic and Mistral about under-18 members on school plans (human contact).

## Considered and rejected
- **"Hosts shape one conversation; eduX keeps a learner model across sessions."** False for Gemini since June 2026 (w2-08-01 ✓).
- **Keeping US$84 as the headline.** It assumed 40 turns a week and 7 credits a turn. The estimator bills an MCP call at 5 credits, and our central volume is 20 a week (w3-08m-06 ✓, w3-08m-13 ✓). It stays as the conservative row.
- **Pitching a free route** (licensed students, or a developer-built declarative agent). The licensed-user footnote is framed for employees (w3-08m-05 ~), and Microsoft's pages conflict on the agent route (w3-08m-09 ✓). Test it; don't claim it.
- **Agent Builder as the cheap route.** It can't call external services (w3-08m-08 ✓).
- **A Copilot Credit pack for a pilot.** Below breakeven at department scale; credits expire monthly; the pool is shared (w3-08m-07 ✓).
- **Using Windows device share, or Schoolzone's "55% Teams vs 38% Classroom" snippet, as the Microsoft share.** Devices aren't tenancy (w3-08m-01 ✓); the snippet's survey is unknown.
- **Publishing a Fermi number for sixth forms with learner Copilot on.** No input is measured.
- **Using Pearson's 55.9% as eduX's share.** It includes Economics B (9EB0), which eduX doesn't cover; use 51.5% for 9EC0 (w4-08-08 ✓).
- **Treating certificates as entries, or applying the England share UK-wide.** Different series; Ofqual covers England only. Applying the 2025 share to 2026 entries is labelled our estimate.
- **"Microsoft confirms custom agents work for pupils."** No page says so; MC1548047 only implies that some other agents are reachable when the switch is off (w4-08-01 ~).
- **Reading the add-ons page's "employee-facing agents only" footnote as a ban.** The page is partly stale and ambiguous (w4-08-05 ✓); asked as a question instead.
- **Adding AS (8EC0) or Economics B to the market.** AS is small; 9EB0 is a different specification and pack.
- **Relying on s.32, s.36 or s.29A for the product, or on the CLA Schools Licence.** Non-commercial or school-held (w3-08c-01 ✓, w3-08c-02 ✓, w3-08c-14 ✓).
- **"The school brings its own papers" as a clean licence route.** The centre exemption requires use within the centre and unaltered originals (w3-08c-06 ✓). A question for Pearson, not a route.
- **Seneca-style "written by senior examiners" wording.** Pearson's endorsement policy forbids implying examiner input (w3-08c-09 ✓).
- **Art. 4 deployers licensing the instrument.** No measurement or certificate is required (w2-08-09 ✓).
- **Keeping £8.** Anchored on a budget share, not a price paid (w2-08-06 ✓).
- **Raising the price, or cutting it to absorb the credit cost.** Up Learn's public prices are consumer prices. Cutting ours can't offset Microsoft's charge.
- **Targeting Google schools, or "ChatGPT/Claude schools" for pupils** (w2-08 rec 3). No under-18 route; Google schools get tracking free.
- **Le Chat as a channel.** A school can't contract for it (DPO w2 #1).
- **Per-student consumer pricing.** Puts cost on families; conflicts with DfE std 13.
- **Third-party price aggregators** (Sparx "£600", Century "£2,760", Khanmigo "$10–35", Eedi US tiers). Unverified.
- **Claiming "nobody is building this".** The Pioneer Programme funds eight suppliers.
- **Planning an efficacy trial ourselves.** It needs 60–100 schools and an independent evaluator.

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| Microsoft earns 4.5× what we do; PAYG off by default; a finance-office decision | Investor w3 #1 | **Partly**: cost recomputed on verified rates and confronted in §3; per-class cap priced on paper. **Open**: no real turn count, no school billed |
| "Free route" rests on contested pages | Investor w3 #2 | **Partly**: not pitched; tenant test and Microsoft email recommended (recs 14–15), not done |
| The channel may not exist for custom agents | Investor w3 #3; w2 #2; w1 #1 | **Open**: implied, not stated (w4-08-01 ~, -02 ✓); a new opt-in switch can close it per school; channel size not published |
| Edexcel's share of Economics | Investor w3 (ask #7) | **Answered**: 9EC0 51.5% of certificates, England 2024–25 (w4-08-08 ✓); ceiling recomputed |
| Copyright removes the content moat; AQA bans AI use | Investor w3 #4; w2 #4 | **Partly**: §6 sets the lawful route and what needs a licence. **Open**: no answer to "what stops Pearson copying it" |
| Evidence takes too long for a seed runway | Investor w3 #5 | **Partly**: pilot framed as feasibility with preregistered criteria; learning evidence is years away |
| Cost story contradicts itself (US$84 vs "no model calls") | Investor w2 #1 | **Partly**: replaced by verified rates and an honest total; "zero running cost" barred |
| Moats weaker; Art. 4 gone | Investor w2 #3; w1 #2 | **Partly**: reframed as a head start. **Open**: no buyer for AI-literacy evidence |
| Price unanchored | Investor w2 #5 | **Partly**: re-anchored (our choice); no letters of intent |
| "Runs inside Gemini" | Investor w1 #1 | **Answered**: removed |
| Team | Investor w1 #5 | **Recommended**: roles to name (rec 9) |
| Processor chain for a DPIA | DPO w1 #1, w2 #2, w3 #4 | **Partly**: roles, DPIA outline and Art 28 checklist drafted in [09](09-safety-ethics.md); no finished DPA or diagram |

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
| w2-08-01 | Gemini study notebooks: 100+ objectives, diagnostic quiz, progress dashboard | official document (vendor) | 18+ personal first | adoption | ✓ |
| w2-08-02 | Guided Learning in Classroom with teacher progress insights; Ark pilot in 3 UK schools | official document (vendor) | UK secondary pilot | adoption | ✓ |
| w2-08-03 | OpenAI Sept 2026: in-chat quizzes; no tracking mentioned | official document | ChatGPT users | adoption | ✓ |
| w2-08-04 | Claude for Teachers: US K-12 educators only, free to 30 Jul 2028 | official document | US educators | adoption / policy | ✓ |
| w2-08-05 | Claude for Teachers connectors include Eedi, ASSISTments | official document | US educators | adoption | ✓ |
| w2-08-06 | Dixons → Sparx Maths £25,250 ex VAT, direct award | official document | England MAT, ages 11–16 | cost | ✓ (per-pupil figure is our estimate) |
| w2-08-07 | Essex → Century-Tech £68,850 inc VAT, 3 years, FE | official document | England council, FE | cost | ✓ |
| w2-08-08 | Pioneer Programme: 8 × £300k incl. Pearson, Eedi, Google; Years 9–10 | official document | England state secondary | policy / cost | ✓ |
| w2-08-09 | EC: Art. 4 needs no measurement and no certificate | official document | EU deployers (staff) | policy | ✓ |
| w2-08-10 | 44 Ofqual AI qualifications; none from AQA/OCR/Pearson | official document | England | policy | ✓ |
| w2-08-11 | AILit feeds the PISA 2029 Innovative Domain | official document | 15-year-olds | policy | ✓ |
| w2-08-12 | Khanmigo $4/month or $44/year; teachers free; no UK | practitioner | US | cost | ✓ |
| w3-08m-01 | TiS 2024–25 doesn't measure M365 vs Google; secondary IT leads: Windows 99%, ChromeOS 33% | official document (survey) | England state schools; no FE or colleges | adoption | ✓ |
| w3-08m-02 | Since Jan 2023: 34% bought increased-capability licences, 10% generic AI, 7% GenAI education tools, 51% none | official document (survey) | England state schools, IT leads, n = 489 | adoption / cost | ✓ |
| w3-08m-03 | About four in five teachers use Outlook, over one in five Gmail | correlational (weighted panel; secondary write-up) | England teachers | adoption | ~ the sentence isn't dated or tied to the Nov–Dec 2025 sample |
| w3-08m-04 | Copilot Chat off by default for 13–17 in K-12 tenants; Study and Learn preselected; teacher assignment Nov 2026 | official document (vendor) | 13–17, M365 K-12 tenants (global) | policy / adoption | ✓ |
| w3-08m-05 | Standard harness: generative answer 2 credits, agent action 5; no charge for licensed users under their own identity | official document | Copilot Studio tenants | cost | ~ "no charge only when licensed" too strong; footnote framed as employee use; other exemptions apply |
| w3-08m-06 | Estimator: each tool invocation incl. MCP = 5 credits; no generative charge on tool messages; 1 credit = US$0.01 | official document (vendor estimator) | Copilot Studio agents | cost | ✓ |
| w3-08m-07 | PAYG US$0.01 / £0.0075 per credit from 1 Sep 2025; pack US$200 / £153.80 for 25,000 a month | official document | Microsoft tenants (list prices) | cost | ✓ |
| w3-08m-08 | Agent Builder can't author actions that call external services | official document | M365 tenants | policy / cost | ✓ |
| w3-08m-09 | Declarative agents can call MCP; Microsoft's pages conflict on whether unlicensed users are billed | official document (internally conflicting) | M365 tenants | cost / policy | ✓ |
| w3-08m-10 | Three harnesses; the Copilot harness bills tokens and tools from build time | official document | Copilot Studio tenants | cost | ✓ |
| w4-08-01 | MC1548047: opt-in admin switch limits A1/A3/A5 students to Study and Learn; no other agents; agent store affected; mid-Nov to mid-Dec 2026 | official document (third-party mirror) | education tenants, worldwide | policy | ~ read on a mirror only; "off by default" not stated verbatim ("no action is required"; admins opt in) |
| w4-08-02 | K-12 pages: NotAdult 13–17 can use Copilot Chat, Study and Learn, Notebooks; no mention of custom agents | official document (rests on omission) | 13–17, K-12 tenants, worldwide | policy | ✓ |
| w4-08-03 | Study and Learn is a declarative agent for learners 13+ | official document | learners 13+, worldwide | policy | ✓ |
| w4-08-04 | Education security page lists Block Agents and Block Agent Creation; 2025 blog: manage access to custom agents | official document | education tenants, worldwide | policy | ✓ |
| w4-08-05 | Add-ons page: Agents rows footnoted "employee-facing agents only"; partly stale | official document (ambiguous) | education tenants | policy | ✓ |
| w4-08-06 | Org-published agents need admin approval in the Agent Registry; admins can block or assign | official document | M365 tenants | policy | ✓ |
| w4-08-07 | A level Economics certificates 2024–25: 40,795; Pearson 55.9%, AQA 36.6%, OCR 5.9%, WJEC 1.5% | official document | England, certificates | adoption | ✓ |
| w4-08-08 | 9EC0 21,005 certificates (51.5%, derived); 14,760 → 21,005 since 2020–21 (+42%) | official document (our arithmetic) | England, certificates | adoption | ✓ |
| w4-08-09 | Pearson's share: Business 52.3%, Politics 77.6%, Maths 72.4%, Further maths 69.8% | official document | England, certificates | adoption | ✓ |
| w4-08-10 | About 23,900 9EC0 candidates a cohort, 48k students; ceiling about £239k at £5, £143k at £3 | official document plus our estimate | England | cost / adoption (ceiling) | ✓ (rests on two stated assumptions) |
| w4-08-11 | MC1537656 "Copilot access configuration for your education tenant" exists; admin-only content | official document (stub) | education tenants | policy | ~ third-party mirror listing only |
| w3-08m-11 | Barton Peveril: own LLM tools in its Google tenancy, per-token, free to students; ~5,000 trained | practitioner (self-report) | England sixth-form college, 16–18 | engagement / adoption | ✓ (Google tenancy from the 2025 article; user counts unreconciled) |
| w3-08m-12 | No public English case of Copilot Studio agents for students found | practitioner (negative search) | English schools and trusts | adoption | ~ "not student-facing" is an inference; a negative can't be fully confirmed |
| w3-08m-13 | Central £22.50 (US$30) per student per year; range £11.25–£108 | official rates + our estimate | UK M365 students without Copilot licences | cost | ✓ (arithmetic; turn volumes are assumptions; £0 for licensed users rests on an employee-framed footnote) |
| w3-08m-14 | Reasoning models +10 credits per 1,000 tokens; 141–461 credits per message; GPT-5 chat is standard-rate | official document | Copilot Studio tenants | cost | ✓ |
| w3-08c-01 | ss.29, 32, 36 non-commercial only; private study excludes commercial (s.178) | official document (statute) | UK | policy | ✓ |
| w3-08c-02 | s.29A: non-commercial research only; copy can't be passed on or reused | official document (statute) | UK | policy | ✓ |
| w3-08c-03 | s.30(1ZA) quotation: not limited to non-commercial; can't be contracted out | official document (statute) | UK | policy | ✓ |
| w3-08c-04 | Substantial part (s.16(3)); databases (s.3A, reg.13); exam papers protected (1916) | official document; case via secondary | UK | policy | ~ statute confirmed; case only via a secondary summary |
| w3-08c-05 | DfE economics subject content under OGL v3; 60% of any A level spec; ≥ 20% Level 2 maths | official document | England A level specs | policy | ✓ |
| w3-08c-06 | Pearson: no copying without permission; narrow centre exemption (≤ 5 years, within centre) | official document | Pearson qualifications | policy | ✓ |
| w3-08c-07 | Pearson v2.3: papers, mark schemes, examiner reports restricted to centres for 12 months, then open | official document | Pearson GCSE, A level, IAL | policy | ✓ ("normally" 12 months) |
| w3-08c-08 | Pearson UK legal notice reserves TDM and AI-training rights | official document | Pearson UK web content | policy | ✓ |
| w3-08c-09 | Pearson endorsement policy v1.9: open, non-exclusive; no "official"; no implied examiner input | official document | publishers for Pearson qualifications | policy | ✓ |
| w3-08c-10 | AQA bans AI training and AI-generated third-party works; OCR silent on AI | official document | AQA, OCR | policy | ✓ |
| w3-08c-11 | UK Mar 2026 report: opt-out TDM exception no longer preferred; no intervention in licensing | official document | UK | policy | ✓ |
| w3-08c-12 | TMA s.11(2)(c): referring to a mark to show intended purpose, honest practices | official document (statute) | UK | policy | ✓ |
| w3-08c-13 | Seneca, Up Learn, Oak describe alignment, not partnership; Oak post-2022 content under OGL | practitioner (vendor pages) | UK secondary and A level | adoption / policy | ✓ |
| w3-08c-14 | CLA Schools Licence held for schools, copies within institution; CLA GenAI licence opt-in only | official document (licensor) | UK schools; AI developers | policy | ✓ |

Also cited here; each sits in its home report's table: w2-05-01 ~, w2-05-02 ✓, w2-05-03 ✓, w2-05-04 ✓, w2-05-06 ~ (superseded as the headline by w3-08m-13), w2-05-10 ✓, w2-05-11 ✓, w2-05-12 ✓, w2-05-14 ~, w2-05-20 ~, w2-05-23 ~, w1-05-02 ✓, w1-05-03 ✓, w1-05-09 ✓, w1-05-14 ~ ([05](05-product-features.md)); w1-09-01 ✓ to w1-09-03 ✓, w1-09-08 ~ ([09](09-safety-ethics.md)); w1-04-08 ✓ ([04](04-economics-education.md)).
