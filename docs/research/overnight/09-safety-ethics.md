# 09 · Safety and ethics: DfE standards, offloading evidence, equity, and data protection for schools

Waves 1–3 (overnight 17–18 Nov 2026). Sources:
- Wave 1: w1-09-* in `work/w1/w1-08.md` (marks in `verify-C.json`), w1-05-* (`verify-A.json`), and a read of the eduX code on branch `research/overnight`.
- Wave 2: `work/w2/w2-09.md` (usage, offloading, equity; marks in `verify-E.json`), `work/w2/w2-05.md` and `w2-05t.md` (routes, keys, teacher view), and the DPO's wave-2 objections in `work/w2/panel-investor-dpo.md`.
- Wave 3: `work/w3/w3-09.md` (lawful basis, roles, retention, DPIA, contract, safeguarding, rights; marks in `verify-L.json`) and the DPO section of `work/w3/panel-investor-dpo.md`.

> **Data protection sections are not legal advice.** They summarise official guidance for a student team. A school's DPO and, where needed, a solicitor check anything here before a school relies on it.

We changed no code. **Every fix here is a recommendation; none is built.** On 18 Nov, `main` and `build/06-demo` still read the key only from `?key=` in `edux/server.py`. There is no delete, export, revoke, key hashing or retention code on either branch (panel DPO w3).

## Summary
- **eduX partly meets the DfE Generative AI product safety standards** (w1-09-01 ✓ to w1-09-03 ✓). It meets the anti-manipulation standards. The gaps are safeguarding, data rights and key security, and after three waves every fix is still a plan. The DPO signs off controls, not recommendations (DPO w3 #1).
- **Offloading: the best evidence is one RCT.** In Bastani et al. (about 1,000 Turkish high-school maths students), unguarded GPT-4 raised practice scores by 48% but cut the unassisted exam by 17%. A guarded tutor **avoided the harm but showed no exam gain** (w2-09-08 ✓). Say "avoided harm", never "improved learning". The rest of the "AI makes you think less" literature is weak: an unreviewed preprint (w2-09-11 ✓), a correlational survey (w2-09-12 ~), and a meta-analysis **retracted on 22 April 2026** (w2-09-13 ✓).
- **How UK 16–18s use AI, and the equity gap (self-report, opt-in sample).** 70.6% have used generative AI (w2-09-01 ~). 58.5% say they check its output (w2-09-02 ✓). FSM and non-FSM pupils use AI equally, but FSM pupils more often just copy (30.0% vs 24.0%) (w2-09-03 ✓). The gap is in quality of use, not access. Never read "no evidence" as "low literacy", and never profile by FSM, SEND or EAL.
- **Lawful basis: the school's public task (UK GDPR Art 6(1)(e)).** The ICO says legitimate interests isn't available to a public authority doing its tasks, and its school-app example rejects consent because of the power imbalance (w3-09-01 ✓). DfE warns that public task "will not be appropriate" for optional features (w3-09-03 ✓). So the learner model and the class view are core teaching. **AI-literacy scores sit under public task only where the school teaches AI literacy; otherwise they are off by default.** This is our reading of general guidance: no document names learning analytics specifically.
- **Roles: the school is the controller. Microsoft and eduX are separate processors to it.** Microsoft says connector traffic to non-Microsoft systems is the agent maker's responsibility, and the agent maker is the school (w3-09-05 ✓). So **the school signs eduX's DPA directly**. eduX is not Microsoft's sub-processor. No DfE or ICO template DPA exists (w3-09-03 ✓, w3-09-04 ~), so eduX writes its own from the ICO's Art 28 list.
- **Retention and rights.** The default is end of course plus one term, then delete (our choice), with **no anonymise-and-keep** for eduX's own use. Pupils have access and rectification. Erasure runs through an **objection to the school** (Art 21). **Portability doesn't apply under public task** (w3-09-15 ✓, w3-09-19 ✓). The DfE "25th birthday" rule is for the school's own pupil record, not for eduX (w3-09-07 ✓).
- **Safeguarding minimum:** signpost to the school's configured DSL contact, store nothing, and send no alerts until a route is in the contract. **Rec 13 is revised: no per-student wellbeing count.** A `wellbeing_concern` label is possible health data (Art 9) even in transit. The likely condition is DPA 2018 Sch 1 para 18 (w3-09-20 ✓). Storing nothing is minimisation, not a lack of lawful basis.
- **Still open:** who controls the pilot's research data (DPO w3 #2), and two code gaps. `call_log.error` can store chatbot-supplied text, and the demo's `remove_students()` doesn't delete `call_log` rows (w3-09-17 ✓). The teacher-view rule is unchanged (coordinator): per-student completion only as a school opt-in; levels, AI-literacy scores, offloading and draft counts never per student.

## Ranked recommendations

All are for the build team or the pitch. File paths are where the change lands. Numbers are kept from wave 2 so that other reports' references still hold. Recs 20–21 are new in wave 3.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **Delete "use what you already know about the student"** from `text/style.md:3` and `docs/build/steps/05b-one-call-per-turn.md:111`. Fall back to a neutral everyday example. | build | S | yes | panel: DPO w1 #5 |
| 2 | **Offloading evidence line for the pitch:** "In a 1,000-student RCT, unguarded GPT-4 raised practice scores 48% but cut exam scores 17%. A guarded tutor avoided the harm." Footnote: Turkish high-school maths, 2023, GPT-4; the guarded tutor showed no exam gain. | pitch, video | S | yes | w2-09-08 ✓, w2-09-09 ✓ |
| 3 | **"Never cite" list in the deck checklist:** Wang & Fan 2025 (retracted); "Your Brain on ChatGPT" (unreviewed, small); Gerlich as causal; "AI rots your brain". | pitch | S | yes | w2-09-11 ✓, w2-09-12 ~, w2-09-13 ✓ |
| 4 | **Under-18 wording:** caption the demo as an adult account. No 16–17-year-old on a consumer chatbot. **No Le Chat on any pupil-facing slide**; if asked, "adults only". | video, pitch | S | yes | w1-05-02 ✓, w2-05-01 ~; DPO w2 #1 |
| 5 | **Accept the key in an `Authorization: Bearer` header** (`edux/server.py`). Keep `?key=` only for adult ChatGPT testing. | build | S | yes, after filming | w2-05-08 ✓, w2-05-10 ✓, w2-05-11 ✓ |
| 6 | **Hash keys.** Store SHA-256 and look up by hash (`learner.py:91–94, 104–105`). After filming, or make `seed --reset` keep the stored hash. | build | S | yes, after filming | panel: DPO w1 #2 |
| 7 | **`revoke-key` and `rotate-key` commands** in `edux/cli.py`. | build | S | yes, after filming | panel: DPO w1 #2 |
| 8 | **`delete-student`, `delete-school` and `export-student` commands.** Loop over **every table with a `student_id` column**, so later migrations are covered automatically. **Include `call_log`**, which `demo.remove_students()` misses today (`demo.py:277`). Delete events and derived state together: `rebuild_state` would recreate derived tables from events. Export as JSON with a plain-English key and without the key itself. **Call it an "access export", never "portability".** It helps the school answer a subject access request within one month and get its data back at contract exit. | build (`edux/cli.py`) | S | yes | w3-09-03 ✓, w3-09-15 ✓, w3-09-17 ✓; DPO w3 #1 |
| 9 | **Retention default** (schedule below; our choice) in the build docs, the DPA and the safety statement: **end of course plus one term, then delete**. No anonymise-and-keep for eduX's own use unless the school gives a separate written instruction. `offered_misconception_ids`, if built: clear after 28 days. Pitch line: "Our retention period is in the contract." | build docs, DPA, pitch | S | yes | w3-09-06 ~, w3-09-07 ✓, w3-09-10 ✓, w3-09-11 ✓ |
| 10 | **Pseudonymous default ids and no free text in `call_log`.** Random ids, not name slugs (`learner.py:90–91`). Store an error code plus at most 80 characters in `call_log.error`, with no echoed request values (`edux/server.py:141–167`). Never call ids, bands or exports "anonymous": they stay personal data to eduX and the school, who can re-link them. | build | S | yes, after filming | w3-09-17 ✓, w3-09-18 ~; DPO w1 #2 |
| 11 | **Score AI literacy fairly, and only where it's lawful.** (a) Show levels as "not enough evidence yet" until 3 moments (our choice); ignored tasks are missing, not 0; never infer off-platform AI use; score Ask features regardless of spelling, grammar or language (EAL). (b) **AI-literacy scoring is off by default.** It switches on only when the school confirms at setup that AI literacy is part of its taught curriculum and records that in its DPIA. Class-level aggregates only, in bands, groups of 6 or more, never per pupil. This is a product default; the demo on an adult account can still show it. | build (settings, `edux/`, `text/`), DPA | S | yes (doc); build maybe | w2-09-01 ~, w2-09-03 ✓, w3-09-01 ✓, w3-09-02 ✓, w3-09-03 ✓ |
| 12 | **Transparency and rights lines** in the student's progress text: "What your teacher sees" (wording in [05](05-product-features.md) rec 6), and "To see, correct or delete what eduX holds, ask your school's data protection officer." eduX never answers a pupil's request directly. It helps the school within 5 working days (our choice), inside the school's one-month deadline. | build (`text/`), DPA | S | yes | w3-09-15 ✓, w3-09-19 ✓; DPO w2 #4 |
| 13 | **Wellbeing signpost, revised: persist nothing per student.** Keep a `wellbeing_concern` label and a stop-and-signpost move. On that turn record nothing in `exchange_log`: no flag, no count. At most a server-wide daily counter with no student id, for the safety statement. Signpost text names a trusted adult and the school's configured DSL contact, mentions Childline or Shout as crisis services, and never says "keep this between us". The school's DPIA names an Art 9 condition for the label in transit (likely Sch 1 para 18) and its DPO confirms whether an appropriate policy document is needed. | build (`edux/plan.py`, `text/moves/`), DPIA | S | yes, if time | w3-09-12 ✓, w3-09-13 ✓, w3-09-20 ✓; DPO w3 #3 |
| 14 | **Light friction on "just show me":** with no attempt yet, show a guided example with the last step left to the student. The follow-up check is skippable. | build | M | yes, if time | w1-09-01 ✓ |
| 15 | **Safety-slide and Q&A lines now; DSL field later.** Say: "Not legal advice. The school is the controller and its lawful basis is public task, as for its other teaching tools. eduX is its processor under our DPA; Microsoft is its processor under its M365 terms. A disclosure gets a signpost to the school's DSL contact, and we store nothing." Build later: the DSL contact as a required school-config field, confirmed at onboarding. | pitch now; build later | S | pitch yes | w1-09-02 ✓, w3-09-01 ✓, w3-09-05 ✓, w3-09-12 ✓ |
| 16 | **Processor-chain diagram for the Copilot route:** pupil → school's Microsoft tenant (Microsoft, processor under M365 terms) → eduX (processor under eduX's DPA, signed by the school) → eduX's hosting sub-processor (named, UK or EU). Open items: whether Microsoft's Product Terms cover custom-connector traffic, and whether teen protections cover custom MCP agents. | business plan | M | no | w2-05-03 ✓, w2-05-13 ✓, w3-09-05 ✓; DPO w2 #2, w3 #4 |
| 17 | **School pack: one-page DPA and one-page DPIA starter**, from the outline and the Art 28 checklist below, marked "draft, for the school's DPO". The ICO's audits found many edtech providers weak on contracts, DPIAs and retention (w3-09-06 ~, secondary figures), and schools lack the resources to negotiate (w3-09-16 ✓). A ready pack saves DPO time. | business plan | M | no (text started here) | w3-09-03 ✓, w3-09-04 ~, w3-09-14 ✓ |
| 18 | **Entra sign-in for pilots** (M), then an OAuth broker (L). See [05](05-product-features.md). | build later | M / L | no | w2-05-05 ✓, w2-05-07 ✓ |
| 19 | **DSL alert route** (a content-free flag to the DSL within an agreed time), **only once a school contracts for it** (KCSIE para 368). | build later | L | no | w1-09-02 ✓, w3-09-12 ✓, w3-09-13 ✓ |
| 20 | **Settle the pilot-research controller before any research data is collected** (see below). A second DPIA section that names the research controller, its Art 6 basis, the ethics approval and a separate notice. `STORE_PROMPTS=1` or donated messages only after that. | business plan, pilot | M | no | DPO w3 #2 |
| 21 | **Watch the ICO's planned edtech code** and the ICO's Art 28 page (under review after the DUAA). Re-check the DPA when either changes. | later | S | no | w3-09-04 ~, w3-09-06 ~ |

## Data protection for a school adopting eduX (not legal advice)

### Lawful basis
- **Public task, for core teaching.** The learner model and the opt-in class view support the school's education functions. The ICO's school-app example chooses public task over consent (w3-09-01 ✓). "Necessary" means there is no reasonable, less intrusive way, and public task covers only the school's own tasks (w3-09-02 ✓).
- **AI-literacy scores only where the school teaches AI literacy.** DfE says public task won't cover optional features outside official duties (w3-09-03 ✓). So AI-literacy scoring is off by default (rec 11).
- **Profiling.** The learner model and AI-literacy levels are profiling. They are not "significant decisions" as long as nothing feeds setting, grades or predictions (personalisation CSV 6-05, 6-06). A DPIA is required: profiling children and offering them online services are on the ICO's high-risk list, and AI counts as innovative technology (w3-09-14 ✓).
- **Children's code standard 12 binds eduX directly only where it acts as a controller** (CSV 6-02). As a processor it is out of scope, but it designs to standard 12 anyway: core profiling on, non-core off by default.

### Roles
- **Controller:** the school.
- **Processors, separately to the school:** Microsoft, under the school's M365 terms; eduX, under eduX's DPA, which the school signs directly. Microsoft puts connector traffic to non-Microsoft systems on the agent maker, which is the school (w3-09-05 ✓). We have not read Microsoft's Product Terms.
- **eduX's sub-processor:** its hosting provider, named, with a UK or EU location, authorised in advance.
- **Consumer chatbot accounts** make the vendor a controller with no school contract. They are not a pupil route (rec 4).

### Retention (our choice unless marked)

| Data | Keep | Then |
|---|---|---|
| `student`, `student_profile`, events (`exchange_log`, `evidence_log`) and derived tables | **End of course plus one term**. That is shorter than DfE's "2 terms after the pupil leaves" rule for primary MIS data, the nearest official anchor (w3-09-07 ✓). The school can delete earlier at any time | `delete-student`. The school exports first if it wants a copy in its own record |
| Message text | **Not stored** (`STORE_PROMPTS=0`) | — |
| `issued_plan` | Overwritten each turn; cleared after 14 days with no turn | Delete |
| `call_log` | 90 days | Delete row |
| `offered_misconception_ids` (if built) | 28 days | Clear |
| Backups | Rolling 35 days | Deleted rows put "beyond use" until rotation (w3-09-15 ✓) |
| Contract end | Export to the school, then delete within 30 days, with written confirmation (DfE asks schools to require this, w3-09-03 ✓) | Comparators: Seneca and Century work on 30 days (w3-09-11 ✓) |

- **No anonymise-and-keep.** Sparx keeps data 2 years after a user is inactive, then keeps anonymised usage data for research. Eedi's adult notice allows de-identified data for research and commercial use (w3-09-10 ✓). Anonymising pupil data for a provider's own use is controller processing (ICO audits, w3-09-06 ~). eduX doesn't do it.
- **The 25-year rule is the school's.** DfE says secondary pupil records are kept until the 25th birthday (w3-09-07 ✓); the IRMS academies toolkit gives 25 years from date of birth and says data kept for analysis should be anonymised (w3-09-08 ~). eduX is not the pupil record. One council's schedule keeps internal exam results for current year + 5 years, which the school can apply to its own exported copy (w3-09-09 ~).

### Rights under public task
- **Access (Art 15) and rectification (Art 16) apply.** `export-student` serves access requests. `check_me` lets a pupil contest a level.
- **Objection (Art 21) is the route to erasure.** It is qualified under public task: the pupil objects to the school, which must stop unless it shows compelling legitimate grounds. If the objection is upheld, eduX deletes on the school's instruction (w3-09-19 ✓). Erasure is not absolute where processing is necessary for a public task, but children's requests get particular weight (w3-09-15 ✓).
- **No portability (Art 20).** It covers only consent and contract (w3-09-15 ✓).
- **Requests go through the school** (rec 12). Whether 16–17-year-olds use their rights themselves depends on competence; we assume they can.

### DPIA outline (the school owns it; rec 17)
1. **Why a DPIA:** profiling children, plus AI as innovative technology (w3-09-14 ✓).
2. **Description:** revision tutoring for A level Economics, plus optional AI-literacy feedback. Data: pseudonymous id, per-part knowledge estimates, labels of each message, check answers. No message text by default. No SEND, FSM or EAL data. Flow as in rec 16. Retention as above.
3. **Lawful basis:** public task. Name which features are core and which are not. An Art 9 condition for the in-transit wellbeing label (likely Sch 1 para 18, w3-09-20 ✓). The DPO confirms whether an appropriate policy document is needed. Consent is not used.
4. **Necessity and proportionality:** one call per message; minimum fields; non-core features off; teacher view opt-in, class bands, k ≥ 6.
5. **Risks to children:** wrong levels or labels; unfair AI-literacy scores for EAL pupils; a teacher reading levels as grades; a leaked key; a disclosure not reaching the DSL; chatbot vendor terms; pressure to over-use.
6. **Measures:** recs 5–13 and 15; the school's filtering and monitoring review covers the chatbot (w3-09-13 ✓).
7. **Sign-off:** DPO advice recorded; pupils' views sought (for example the sixth-form council); review after one term, or when eduX changes its processing.

### Art 28 checklist for eduX's DPA (ICO, w3-09-04 ~)
The contract states the **processing details**: subject, duration, nature and purpose, data types and data subjects. In eduX's case that means tutoring for the named course; pupils 16–18 and teachers; fields listed per table; the contract term plus the exit period. Then the ICO's **eight** compulsory terms:

| # | ICO term | eduX's DPA says |
|---|---|---|
| 1 | Documented instructions | The school's settings and setup form. No pooling across schools; no tuning on live data |
| 2 | Confidentiality | Named team members only; access logged |
| 3 | Security (Art 32) | Hashed keys, TLS, UK/EU hosting, encrypted backups; breach notice to the school within 24 hours (our choice) |
| 4 | Sub-processors | Hosting provider named; prior written authorisation; changes notified in advance |
| 5 | Data subjects' rights | Export and delete commands; response within 5 working days (our choice) |
| 6 | Assisting the controller | Security, breaches, DPIA and ICO consultation: DPIA pack and incident template supplied |
| 7 | End of contract | Return (JSON export), then delete within 30 days, including backups on rotation; written confirmation |
| 8 | Audits and information | This document, the schema and a yearly self-assessment; audits on reasonable notice |
| + | Added, not ICO-compulsory | Safeguarding terms per KCSIE para 368 (signpost behaviour, DSL contact, no message storage); no AI training or commercial use; no anonymise-and-keep |

The ICO offers no template and points to the Danish SCCs, which the EDPB approved. Its page is under review after the Data (Use and Access) Act 2025 (w3-09-04 ~).

### Safeguarding minimum
- **The duties are the school's.** KCSIE (September 2026 edition) says a contractor's safeguarding duties are whatever the school writes into the contract (para 368). It also says data protection law does not prevent sharing to keep children safe (para 63). Generative AI is now in its online-risk categories (w3-09-13 ✓).
- **DfE's standards expect** a DSL contact at setup confirmed by the supplier, a tiered response from signpost to flag, flags that don't show the content, no secrecy language, and a published crisis protocol (w3-09-12 ✓).
- **eduX's minimum:** the signpost move naming the school's configured DSL contact (recs 13, 15); store nothing; no per-student wellbeing flag or count; a one-paragraph crisis protocol in the safety statement; **no alerts until the school and eduX agree a route and a timescale in the contract** (rec 19).
- **Why no alerts yet:** not data protection (para 63). eduX has no agreed route, timescale or 24/7 cover, and the host and the school's monitoring already see the message. An alert nobody acts on is worse than a clear signpost.

### The pilot-research controller question (open)
The pilot plan (`work/w3/w3-02e.md` §2) adds research uses: storing messages for consenting students (`STORE_PROMPTS=1`) or using donated messages, linking mock results, and running an AI-literacy test. Public task doesn't obviously cover a student team's research (DPO w3 #2). Before any research data is collected, an answer must name:
- **the research controller:** the school, a university department, or the team under one;
- **its Art 6 basis** (and Art 9, if any special-category data could arise);
- **the ethics approval:** which committee, given a mixed Cambridge/LSE team;
- **a separate notice and opt-in** for 16–17-year-olds, with parental information. Non-consenters use eduX for learning only.

We don't pick an answer here. Until it is settled, the pilot runs as feasibility on eduX's ordinary logs only.

## Offloading: what the evidence supports

| Study | Design and population | What it found | Outcome type | How to use it |
|---|---|---|---|---|
| **Bastani et al. 2025, PNAS** (w2-09-08 ✓, w2-09-09 ✓) | Preregistered RCT; about 1,000 students in about 50 grade 9–11 classes at a Turkish high school; four 90-minute maths sessions; GPT-4 | **GPT Base:** practice +48%; unassisted exam −17%, about −0.2 SD (our calculation). **GPT Tutor (guarded):** practice +127%; exam not significant: **no harm, no gain**. 67% of GPT Base students' first messages asked for the answer (37% for Tutor). Tutor students overrated their exam performance | Learning (same-day exam); engagement; perception | Headline evidence for "a guarded tutor, not an answer machine". Not UK, not economics, not current models |
| Kestin et al. 2025 (w2-09-14 ✓) | Crossover RCT; 194 Harvard physics undergraduates | Structured AI tutor beat in-class active learning: 0.63; immediate test only | Learning | Structure decides whether AI helps |
| Fan et al. 2025, BJET (w2-09-10 ~) | Lab RCT; 117 university students | ChatGPT improved essay scores, with no difference in knowledge gain or transfer | Task product vs learning | AI improves the product, not the learning |
| Darvishi et al. 2024 (w2-09-15 ~) | RCT; 1,625 university students | Students relied on rather than learned from AI prompts; self-monitoring checklists partly helped | Task performance | Supports making the student do the check |
| Kosmyna et al. (w2-09-11 ✓) | Unreviewed preprint; 54 adults, 18 in session 4 | EEG and recall differences; authors reject "brain rot" readings | Neural engagement; recall | **Don't cite** |
| Gerlich 2025 (w2-09-12 ~) | Survey and interviews; 666 adults | Negative correlation between AI use and critical thinking | Self-reported critical thinking | **Don't cite as causal** |
| Wang & Fan 2025 (w2-09-13 ✓) | Meta-analysis, g = 0.867 | **Retracted 22 April 2026** | — | **Never cite** |

**What this means for eduX:** the plan server is a guardrail of the GPT Tutor kind. The evidence says guardrails remove harm, not that they add learning. Say "Unguarded chatbots can harm learning; eduX keeps the student doing the work." Never say "eduX improves learning." Move `p_known` only on evidence, never on self-report.

## Equity

| Gap | Figure | Population | Implication for eduX |
|---|---|---|---|
| Use by FSM | 66.7% vs 67.0% (w2-09-03 ✓) | UK 13–18, opt-in schools | Access isn't the gap. Guided use is the offer to state schools |
| "Just copy" by FSM | 30.0% vs 24.0% (w2-09-03 ✓) | as above | Own-first and Verify moments help most where copying is commonest. **Never profile by FSM** |
| Prompt confidence by FSM | 38.9% vs 44.0% (w2-09-03 ✓) | as above | Keep the Ask score language-light (rec 11) |
| Income, US | 20% (<$30k) vs 7% ($75k+) do all or most schoolwork with chatbots (w2-09-07 ✓) | US teens 13–17 | Business-plan argument, labelled US |
| Vulnerable children | 50% vs 31% say a chatbot is like a friend (w2-09-16 ✓) | UK 9–17 | Verify moments stay one line and skippable. **Don't single out SEND students** |
| Social grade, younger children | Private vs state 52% vs 18% among 8–12s (w2-09-17 ✓) | UK 8–12, **not 16–18** | Context only |
| Non-users | About 30% of 16–18s haven't used generative AI (w2-09-01 ~) | UK 16–18 | Missing evidence is missing, not low (rec 11) |

**Detecting AI-written work is out of scope.** Detectors are biased against non-native writers (personalisation review row 6-14).

## DfE Generative AI product safety standards matrix

Source: DfE, *Generative AI: product safety standards*, updated 19 Jan 2026 (w1-09-01 ✓ to w1-09-03 ✓, w3-09-12 ✓). Expectations are paraphrased. **Every "fix" below is unbuilt.**

| # | Expectation (paraphrased) | eduX status | Owner | Product response |
|---|---|---|---|---|
| 1 | State the purpose; don't overstate impact | partly | eduX | No efficacy claims |
| 3 | Filtering across the whole conversation | n/a | host + school | Microsoft's teen protections apply "where applicable" (w2-05-13 ✓); coverage of custom agents unknown |
| 4 | Activity logs | partly | host; eduX logs labels | Message text only if `STORE_PROMPTS=1` (default 0) |
| 4 | DSL contact at setup; alert on disclosures | **gap** | school + host; eduX can add | Signpost and DSL contact (recs 13, 15); alerts only when contracted (rec 19) |
| 4 | Report each learner's usage duration | **gap (deliberate)** | eduX + school | Not shown per student (coordinator decision) |
| 5 | Security: authentication, permissions | **gap** | eduX | `?key=` in plaintext, no revoke. Recs 5–7, 10 |
| 6 | Privacy notice, DPIA, Children's code | partly | eduX + school | Lawful basis, roles, retention, DPIA outline and Art 28 checklist drafted above; recs 8–12, 17 unbuilt |
| 7 | No commercial use or training on learner inputs | meets (eduX) | eduX; host | No message text stored by default; no training; no anonymise-and-keep (rec 9) |
| 8 | Child-centred design; testing with children | gap | eduX | Pilot student testing through the school |
| 9 | Risk assessment, complaints route | gap | eduX | Safety statement (rec 17) |
| 10 | No full answers by default; attempt first; friction | **partly** | eduX + host | "Just show me" skips the attempt (rec 14) |
| 10 | Track and report offloading | partly: **tracked; reporting is a deliberate gap** | eduX | Not in the teacher view (coordinator decision) |
| 11 | No anthropomorphism; no engagement-prolonging | meets / partly | host + eduX | No streaks; stopping offered neutrally |
| 12 | Detect distress; tiered response to human help | gap | host primarily | Rec 13 (signpost, store nothing); a crisis protocol in the safety statement |
| 13 | No sycophancy, dark patterns, paid steering | meets (eduX) | eduX + host | No paid student tier |

**Never claim "DfE compliant".** For the safety slide, use six rows: 10 (partly), 11 (meets), 4 safeguarding (gap, closing), 5 security (gap, closing), 3 filtering (host), 7 no training (meets).

**Other guidance:** schools must follow AI tools' age limits (w1-09-05 ✓); filtering and monitoring reviews must cover generative AI (w1-09-06 ✓, w3-09-13 ✓); JCQ and Ofqual AI rules barely touch an exam-only course (w1-09-07 ✓).

## The DPO's objections, waves 1–3

| # | Objection | What the code or docs show | Fix | Status |
|---|---|---|---|---|
| w1 #1 | No lawful under-18 route; no processor chain | claude.ai 18+ (w1-05-02 ✓). The Copilot route is documented and untested (w2-05-03 ✓, w2-05-04 ✓) | Roles stated above; diagram (rec 16) | Partly |
| w1 #2, w2 #3 | Key in a URL, in plaintext; name-slug ids | `server.py` reads only `?key=`; raw key storage; no revoke | Recs 5–7, 10; Entra (M) | Recommended |
| w1 #3 | Every message reaches eduX; no safeguarding route | Message passed word for word; not stored by default | Recs 13, 15, 19 | Recommended |
| w1 #4 | No retention, erasure or export | No `delete-student` or `export-student` | Recs 8, 9 | Recommended |
| w1 #5 | "Use what you already know about the student" | `text/style.md:3` | Rec 1 | Recommended |
| w2 #1 | Le Chat can't go in a DPIA | Consumer terms; no DPA (w2-05-01 ~) | Off all pupil-facing material (rec 4) | **Answered** in the reports |
| w2 #2 | Copilot: who processes what? | Microsoft puts connector traffic on the agent maker (w3-09-05 ✓) | Two processors to the school; school signs eduX's DPA (rec 16) | Partly: Product Terms unread |
| w2 #4 | Teacher view: lawful basis, notice, retention | Not built; minimised design (w2-05-34 ✓) | Public task for core teaching (w3-09-01 ✓); notice line (rec 12); 28-day retention (rec 9) | Partly |
| w2 #5 | Wave-1 fixes unbuilt | Confirmed | Recs 5–10 | **Open** until merged |
| **w3 #1** | **Still unbuilt after three waves; `call_log` free text; retention has no job** | No delete, export, hashing or header on `main` or `build/06-demo`. `remove_students()` skips `call_log` (w3-09-17 ✓) | Recs 8–10 | **Open** |
| **w3 #2** | **The pilot reintroduces stored messages and a second purpose; who is the research controller?** | Pilot plan names no controller | Rec 20 | **Open** |
| **w3 #3** | **The Art 9 condition is put on the school** | The label is processed in transit even if nothing is stored | Rec 13; a drafted policy-document paragraph for the school pack; a test that nothing persists on that turn | Recommended |
| **w3 #4** | **The connector is the school's to answer for** | Microsoft: the agent maker's responsibility (w3-09-05 ✓) | Rec 16 with the Product Terms clause and a named hosting sub-processor | Partly |
| **w3 #5** | **AI literacy under public task depends on the curriculum** | A setup tick-box | Default off; DPIA line (rec 11) | Recommended: unbuilt |

**Q&A answers the DPO wants to hear:**
- *What can a teacher see about one child?* "Nothing about how well they're doing. If the school switches it on, whether they did checks this week. Never levels, AI-literacy scores, chats or how often they asked AI to write for them."
- *Show me the delete.* Today: "Not built yet; it's a one-command fix that also covers `call_log`." After rec 8: a live `delete-student`.
- *What is stored when a pupil discloses?* "Nothing. The turn writes no row." (After rec 13, show the database diff.)
- *Is the export portability?* "No. Public task, so it's an access export."
- *Who controls the pilot research data?* Today: "Not yet settled; no research data until it is" (rec 20).
- *Can a teacher identify a pupil from a band?* "Counts of 5 or fewer are never shown, shares are banded. It is minimised, not anonymous."

## Later (not before Thursday)
- Recs 16–21.
- **Message minimisation:** the chatbot sends topic terms instead of the full message. Test the matching cost first.
- **Advisory daily-minutes setting** that returns only `offer_stop` once a school limit is passed.
- **Open questions:**
  - Do Microsoft's Product Terms or DPA cover traffic from Copilot Studio custom connectors to third-party MCP servers? Do teen protections cover custom MCP agents?
  - Who is the controller when a university student team runs research in a school pilot, and on which Art 6 basis?
  - Does a school need an appropriate policy document when it relies on Sch 1 para 18 for a chatbot signpost?
  - The ICO audit report's figures from the primary PDF (only a secondary summary was readable, w3-09-06 ~).
  - When the ICO's statutory edtech code is due.
  - Whether Kosmyna et al. pass peer review.
- **Answered in wave 3:** the lawful basis schools use (public task, w3-09-01 ✓). Whether a template DPA exists: none found from DfE or the ICO (w3-09-03 ✓, w3-09-04 ~).

## Considered and rejected
- **Citing Wang & Fan, Kosmyna, or Gerlich as causal.** Retracted, unreviewed, or correlational (w2-09-11 ✓, w2-09-12 ~, w2-09-13 ✓).
- **Saying the guarded tutor improved learning.** Its exam effect was null (w2-09-08 ✓).
- **Legitimate interests or consent as the school's basis.** Legitimate interests isn't available to a public authority doing its tasks; consent fails on the power imbalance and withdrawal would break the learner model (w3-09-01 ✓).
- **Calling the export "data portability".** Art 20 doesn't apply under public task (w3-09-15 ✓).
- **Keeping data until the pupil's 25th birthday "like the pupil record".** That rule is the school's; eduX duplicating it would breach storage limitation (w3-09-07 ✓).
- **Anonymise-and-keep (the Sparx and Eedi model).** It makes eduX a controller for that use and adds a DPIA burden for little benefit at our scale (w3-09-06 ~, w3-09-10 ✓).
- **A per-student wellbeing flag or count (rec 13 as written in wave 2).** A condition probably exists (Sch 1 para 18), so the objection is not lawfulness. A stored flag is inferred health data that eduX can't act on, which fails minimisation (w3-09-20 ✓).
- **Automated DSL alerts now.** Data protection isn't the barrier (KCSIE para 63); the lack of an agreed route and cover is (w3-09-13 ✓).
- **Storing messages for safeguarding.** Conflicts with the DfE standard's minimum data (w3-09-12 ✓).
- **Claiming a DfE- or ICO-approved DPA.** None exists that we could find.
- **Draft or offloading counts in the teacher report; per-student levels or AI-literacy scores for teachers.** Ruled out by the coordinator.
- **Profiling or adapting by FSM, SEND or EAL.** The equity data are population-level arguments only.
- **Detecting AI-written work.** Biased against non-native writers.
- **Hard time limits enforced by eduX.** The host can answer without calling eduX.
- **Refusing to draft essays.** Conflicts with 05e "never a barrier".
- **Claiming "DfE compliant".** Untrue.

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| No lawful under-18 route / processor chain | DPO w1 #1, w2 #2 | **Partly**: roles and lawful basis stated; route untested; DPA not written |
| Key in URL, plaintext, no revoke, name-slug ids | DPO w1 #2, w2 #3 | **Recommended**: recs 5–7, 10. None built |
| Verbatim messages, no safeguarding route | DPO w1 #3 | **Recommended**: recs 13, 15; alerts only when contracted |
| No retention, erasure or export | DPO w1 #4 | **Recommended**: recs 8, 9; schedule written, nothing built |
| "Use what you already know about the student" | DPO w1 #5 | **Recommended**: rec 1 |
| Le Chat can't go in a DPIA | DPO w2 #1 | **Answered**: removed from pupil-facing material |
| Teacher view lawful basis, notice, retention | DPO w2 #4 | **Partly**: public task named; notice line and retention proposed |
| Wave-1 fixes unbuilt | DPO w2 #5, w3 #1 | **Open** |
| Pilot research controller and stored messages | DPO w3 #2 | **Open**: rec 20 |
| Art 9 condition put on the school | DPO w3 #3 | **Recommended**: rec 13 and a policy-document paragraph |
| Connector responsibility | DPO w3 #4 | **Partly**: rec 16; Product Terms unread |
| AI literacy under public task | DPO w3 #5 | **Recommended**: default off (rec 11), not built |
| Does my teacher see I asked it to write my essay? | Student w2 #3 | **Answered** by the coordinator decision (never shown); the progress line saying so is **recommended** (rec 12), not built |
| Quiz instead of answer | Student w1 #1 | **Partly**: rec 14 compromise |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-09-01 | DfE std: no final answers by default, attempt first, friction, track and report offloading | official document | England | policy | ✓ |
| w1-09-02 | DfE std: DSL at setup, disclosure alerts, distress response, per-learner duration | official document | England | policy | ✓ |
| w1-09-03 | DfE std: time limits, no anthropomorphism, no engagement-prolonging | official document | England | policy | ✓ |
| w1-09-04 | claude.ai 18+; Gemini for under-18s with restrictions | official document | UK | policy | ✓ |
| w1-09-05 | DfE GenAI guidance: follow age limits; no training on pupils' work | official document | England | policy | ✓ |
| w1-09-06 | Filtering and monitoring reviews cover GenAI | official document | England | policy | ✓ |
| w1-09-07 | JCQ/Ofqual AI rules cover coursework/NEA | official document | England / UK | policy | ✓ |
| w1-09-08 | Khanmigo trial: small gains | RCT | US middle-school maths | learning | ~ abstract only; 0.06–0.08 SD per year |
| w2-09-01 | NLT 2025: 70.6% of 16–18s used GenAI; 52.0% weekly | correlational (survey) | UK 13–18, opt-in schools | adoption | ~ 52% weekly is a share of users, not all 16–18s |
| w2-09-02 | 58.5% of 16–18s check AI output, 10.0% just copy | correlational (self-report) | as above | engagement (self-report) | ✓ |
| w2-09-03 | FSM use 66.7 vs 67.0%; copy 30.0 vs 24.0%; prompt confidence 38.9 vs 44.0% | correlational | as above | adoption / engagement | ✓ |
| w2-09-04 | Ofcom 2026: 66% of 16–17s use AI; 25% of confident teens failed the image test | official document (survey) | UK 8–17 | adoption; prediction | ✓ |
| w2-09-05 | OUP: 47% confident they can tell if AI is true | practitioner (survey) | UK 13–18 | self-rated | ✓ |
| w2-09-06 | DfE PPLV: 62% of 16–19s cite false information | official document | England | attitudes | ✓ |
| w2-09-07 | Pew: 20% (<$30k) vs 7% ($75k+) do most schoolwork with chatbots | correlational (probability panel) | US 13–17 | adoption | ✓ |
| w2-09-08 | Bastani: GPT Base practice +48%, exam −17%; GPT Tutor practice +127%, exam n.s. | RCT (preregistered) | Turkish grades 9–11, maths | learning | ✓ |
| w2-09-09 | GPT Base correct 51%; answer-seeking 67% vs 37%; Tutor students overrated exam | RCT (log analysis) | as above | engagement; perception | ✓ |
| w2-09-10 | Fan: ChatGPT improved essays, not knowledge gain | RCT (lab) | 117 university students | product vs learning | ~ abstract only |
| w2-09-11 | Kosmyna: unreviewed preprint, 54 / 18 adults | quasi-experimental | US adults | neural engagement | ✓ |
| w2-09-12 | Gerlich: negative AI use – critical thinking correlation | correlational | 666 adults | self-reported critical thinking | ~ abstract only |
| w2-09-13 | Wang & Fan meta-analysis retracted 22 Apr 2026 | official document | mixed | learning | ✓ |
| w2-09-14 | Kestin: structured AI tutor beat active learning, 0.63 | RCT (crossover) | 194 US undergraduates | learning | ✓ |
| w2-09-15 | Darvishi: students relied on AI prompts | RCT | 1,625 university students | task performance | ~ abstract only |
| w2-09-16 | Internet Matters: vulnerable children treat chatbots as friends | practitioner (survey) | UK 9–17 | adoption / trust | ✓ |
| w2-09-17 | Turing: private 52% vs state 18% among 8–12s | correlational | UK 8–12 | adoption | ✓ |
| w2-09-18 | HEPI 2026: 94% of undergraduates use GenAI for assessed work | official document (poll) | UK undergraduates | adoption | ✓ |
| w3-09-01 | ICO: legitimate interests not for public authorities' tasks; school app example rejects consent, uses public task | official document | UK; schools | policy | ✓ |
| w3-09-02 | ICO: public task needs a basis in law; "necessary" = no less intrusive way; own tasks only | official document | UK public authorities | policy | ✓ |
| w3-09-03 | DfE edtech: public task won't cover optional features; role per feature; non-core off; deletion incl. backups; DPIA for profiling; no template DPA | official document | England schools | policy | ✓ |
| w3-09-04 | ICO Art 28 compulsory terms; no template; Danish SCCs; page under review | official document | UK | policy | ~ the ICO lists 8 compulsory terms, not 9 |
| w3-09-05 | Microsoft: connectors to non-Microsoft systems are the agent maker's responsibility | official document (vendor) | Copilot Studio tenants | policy | ✓ |
| w3-09-06 | ICO edtech audits (28 providers): ~70% controller for some processing, ~70% unclear retention, >40% no DPIA, ~70% weak contracts | official document (via secondary) | UK edtech providers | policy | ~ figures from a law-firm summary; primary PDF not machine-readable |
| w3-09-07 | DfE: primary MIS 2 terms after leaving; secondary records to 25th birthday; CP files to 25th or 75th | official document | England schools | policy | ✓ |
| w3-09-08 | IRMS academies toolkit: pupil record 25 years from date of birth; analysis data anonymised | practitioner | England academies | policy | ~ the "31 years for SEN" figure was not found and is dropped |
| w3-09-09 | One council schedule: pupils' work current year + 1; internal exam results current year + 5 | practitioner (council document) | England (Enfield) | policy | ~ the document doesn't say it is IRMS-based |
| w3-09-10 | Sparx: 2 years after inactive, then anonymised for research; Eedi: two school years | practitioner | UK pupils | policy | ✓ |
| w3-09-11 | Seneca: no period stated, deletion within 30 days on request; Century: 30-day grace before deletion | practitioner | UK pupils | policy | ✓ |
| w3-09-12 | DfE standards: DSL at setup, tiered response, content-free flags, minimum data, no secrecy language, crisis protocol | official document | England | policy | ✓ |
| w3-09-13 | KCSIE 2026: para 63 sharing allowed; para 368 contractors per contract; GenAI in online risks | official document (statutory guidance) | England schools | policy | ✓ (September 2026 edition; the 1 Sept in-force date wasn't seen in the PDF) |
| w3-09-14 | ICO high-risk list: children's profiling and online services; AI with another criterion | official document | UK | policy | ✓ |
| w3-09-15 | Portability only for consent or contract; erasure limited under public task; backups beyond use | official document | UK | policy | ✓ |
| w3-09-16 | Schools carry growing data burdens; can't realistically negotiate with large edtech | practitioner (qualitative reports) | UK state schools | policy | ✓ ("unrealistic" is a paraphrase) |
| w3-09-17 | `call_log.error` can store chatbot-supplied values; `remove_students()` skips `call_log` | theory (code inspection) | n/a | policy (minimisation) | ✓ |
| w3-09-18 | ICO anonymisation: identifiability is a spectrum; motivated-intruder test; pseudonymised data is personal data | official document | UK | policy | ~ the ICO adds that the same data can be anonymous in the hands of someone without the key |
| w3-09-19 | Right to object applies under public task; stop unless compelling grounds | official document | UK | policy | ✓ |
| w3-09-20 | DPA 2018 Sch 1 para 18: safeguarding of children and individuals at risk | official document (statute) | UK under-18s | policy | ✓ |

Also cited here; each sits in its home report's table: w1-05-02 ✓, w2-05-01 ~, w2-05-03 ✓, w2-05-04 ✓, w2-05-05 ✓, w2-05-07 ✓, w2-05-08 ✓, w2-05-10 ✓, w2-05-11 ✓, w2-05-13 ✓, w2-05-34 ✓ ([05](05-product-features.md)).
