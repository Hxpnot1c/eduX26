# Overnight research

This folder holds research to make eduX a stronger entry for Cambridge EduX 2026, Challenge 1 ("Beneath the Surface: Defining and Assessing AI Literacy"). It builds on the personalisation review in [`../personalisation.md`](../personalisation.md) and does not repeat it.

Read [`MORNING-BRIEF.md`](MORNING-BRIEF.md) first, then [`wednesday-build-list.md`](wednesday-build-list.md) and [`pitch-script.md`](pitch-script.md).

## Files
| file | what it holds |
|---|---|
| [`MORNING-BRIEF.md`](MORNING-BRIEF.md) | One page: Wednesday's five actions, pitch points, risks, what changed |
| [`wednesday-build-list.md`](wednesday-build-list.md) | Wednesday's build as a tested patch series (fast-forward 05e, then 0001–0005): for each step what it fixes on camera, the apply and test commands with expected results, hours, owner, what is lost if skipped; the 16:30 freeze, 18:00 gate, cut line and known residuals. Home report for the `w4-fix-*` findings |
| [`pitch-script.md`](pitch-script.md) | Word-for-word video voiceover (Plan A, and Plan B in §1b) with shot timings and captions, deck speaker notes, the expo leave-behind, every number → finding id → mark, and what we couldn't say. Edited after the wave-4 pitch red team |
| [`pitch-notes.md`](pitch-notes.md) | Claims we can make (exact wording, finding id, mark), claims to avoid, and an 8-slide deck outline |
| [`01-competition-fit.md`](01-competition-fit.md) | What the EduX rules ask for, how eduX scores against each criterion, the defining-half gap, and the competition after Gemini's catch-up |
| [`02-ai-literacy-assessment.md`](02-ai-literacy-assessment.md) | Our definition, the AILit crosswalk, the validity argument, the scoring simulation on the 05e branch, the missing-data rule, what chatbots get wrong with sources, and the label-agreement study design |
| [`02a-label-agreement-protocol.md`](02a-label-agreement-protocol.md) | Ready-to-run protocol for the label-agreement study: 40 draft messages (to be rewritten by the team), the key, rater instructions, pass rule and reporting template |
| [`03-learning-science.md`](03-learning-science.md) | Learning-science ideas not yet used: contrasting cases, self-marking, diagram practice, in-session relearning, nudges |
| [`04-economics-education.md`](04-economics-education.md) | Gateway ideas, evidence-based misconceptions, 30 draft pack rows, the MCQ give-away, a content error, and the 9EC0 mark tally |
| [`05-product-features.md`](05-product-features.md) | Which chatbots can reach eduX, at what age and on which plan; authentication; the teacher-view spec and its alarm rule |
| [`06-settings-simulation.md`](06-settings-simulation.md) | Synthetic-student simulations of the course learner model: three bugs, the proposal's settings, the alarms, the pitch chart, and the decay-clock asymmetry with its fixes |
| [`09-safety-ethics.md`](09-safety-ethics.md) | The DfE product safety standards matrix, offloading evidence, the DPO's objections checked against the code, and ranked fixes |
| [`demo-plan.md`](demo-plan.md) | Video storyboard (Plan A and Plan B), live expo script, checklists, bugs to fix before filming, and the pitch chart |
| [`business-plan.md`](business-plan.md) | Market, buyers, pricing anchored on procurement records, competitors, distribution and cost risk, regulation, evaluation plan |
| [`judge-panel.md`](judge-panel.md) | Red-team objections from six personas in three waves, the status of each, and open questions for wave 4 |
| [`findings.csv`](findings.csv) | Every verified finding (✓ or ~), with its home report in `area_report`. ✗ findings are dropped |
| `sims/` | Course learner-model simulation scripts, results and demo captures (synthetic students, example pack only) |
| [`sims/literacy/`](sims/literacy/README.md) | The AI-literacy scoring simulation on the 05e branch's learner code: a replica validated against the real code, the grid search and the final check (report 02) |
| [`sims/teacher/`](sims/teacher/results.md) | The teacher-view misconception alarm: exact binomial and clustering simulation of the flag rule (report 05) |
| [`sims/decay/`](sims/decay/README.md) | The decay-clock asymmetry on economics parts: deterministic cases, fixes (a)–(c) and a 960-student population run on the real learner code (report 06, wave 3) |
| [`sims/demo-05e/`](sims/demo-05e/README.md) | Scripted rehearsal of the Plan A literacy episode against the 05e branch's own MCP server, with captures and a per-turn digest (demo plan, wave 3). Not claude.ai captures |
| `sims/fixes/` | Wave 4: the fix scouts' diffs, probes and measurement scripts (core bugs, focus, Verify scoring, MCQ give-away, decay), with before/after results. Superseded for building by `combined/` |
| [`sims/fixes/combined/`](sims/fixes/combined/README.md) | **The tested patch series** 0001–0005 (plus a 0003 variant for when 0002 is skipped) that the build list applies, the integration verifier's conflict notes, harness scripts and per-step results (check_mcp 74/74 after each step) |
| `work/` | Briefs for scouts, verifiers, panel, writers and fix scouts; scout notes, verifier marks and panel files for waves 1–4 (`w1/`–`w4/`). Wave 4: fix-scout notes, the integration verifier (`verify-Q.json`), the market and Microsoft notes (`w4-08.md`, `verify-R.json`) and the pitch red team (`panel-pitch.md`) |

Each finding appears in the findings table of one report only: its home report, given in `area_report`. Other reports cite it by id and link to that report.

## Method
Waves 1–3 each ran in four stages (wave 4 changed this; see below):
- **Scouts.** Six to eight scouts each research one question.
- **Blind verifiers.** Each claim is checked by one blind verifier, who sees only the claim and its source.
- **Red team.** A panel of six personas attacks the product.
- **Editor.** An editor rewrites the reports, the pitch notes and this index.

**Wave 4 was a build wave.** Fix scouts wrote diffs against the 05e branch and measured each one on copies of the code. An integration verifier then stacked them into one patch series, merged the conflicts by hand and reran every check and headline number after each step. A single pitch red team (judge, teacher, student) attacked the script; the six-persona panel did not run. One scout (w4-08) fetched Ofqual and Microsoft sources directly.

Marks: ✓ confirmed against the source; ~ broadly supported, with a stated problem; ✗ dropped.

| | findings | ✓ | ~ | ✗ |
|---|---|---|---|---|
| Wave 1 (verifier sets A–D, I) | 109 | 75 | 34 | 0 |
| Wave 2 (verifier sets E–H, J) | 121 | 63 | 58 | 0 |
| Wave 3 (verifier sets K–P) | 108 | 70 | 38 | 1 |
| Wave 4 (verifier sets Q, R) | 19 | 16 | 3 | 0 |
| **Total** | **357** | **224** | **133** | **1** |

The findings column counts kept findings only (✓ + ~), so the ✗ column is extra. The one ✗ is w3-02e-14 (a misread blog post), listed in [pitch-notes](pitch-notes.md) as a claim to avoid.

The wave-1 morning brief counted 97 findings. The 12 simulation findings (w1-06) were verified after it was written.

Labels used throughout: "our choice" marks a number we chose. "Simulation: synthetic students" marks a simulated result. Neither is evidence about real students.

Panel status words (from wave 2): **answered** = a fix is built or a document answers it; **recommended** = a fix is recommended but not built; **partly**; **open**.

## Methods used so far
| question area | wave 1 methods | wave 2 methods added | wave 3 methods added | wave 4 methods added | still not reached |
|---|---|---|---|---|---|
| 01 Competition fit | The official EduX site (HTML and its scripts); Luma listings and organiser galleries; web search; framework sites; repo and git inspection | No new scout. Consistency edit from 02, 05 and the business plan | **Judging and persuasion research** (order effects, grant-review agreement, pitch-voice and preparedness studies, narrative vs statistical evidence; Europe PMC and OpenAlex abstracts, PMC full texts) | — | The Challenge 1 brief (renders only in a browser); the Oceania deck (needs sign-in); the Monash Friction page (403) |
| 02 Defining and assessing AI literacy | Primary framework documents (AILit, UNESCO, Long & Magerko, CAR, Ofqual, DfE); OpenAlex and arXiv; psychometric validation studies; first-principles psychometrics; a BKT simulation; a code review of the 05e branch | **Simulation of the 05e branch** (a replica validated against the real learner code, a grid search, an N = 1,000 check, lenient-labelling stress test); **psychometric missing-data literature** (NAEP technical documentation; PISA practice via Robitzsch 2021); **LLM-evaluation literature** (citation audits, sycophancy and self-correction papers, arXiv and PMC full texts); **journalism fact-checking taxonomy** (Wardle, Tow Center/CJR, EBU); **survey grey literature** (NLT, Ofcom, OUP, DfE PPLV, Pew, Internet Matters) | **STARD and agreement statistics** (κ standard errors, Donner–Eliasziw sample size, Gwet's AC1, GRRAS); a Monte Carlo power check of the pass rule; EEF padlock and pilot guidance (PDFs) | **Patch-and-rerun on the 05e branch:** the Verify scoring fix measured on scripted episodes; How AI works AUC rerun on the real learner code with the decay patch (`lit_real.py`) | OECD PISA technical reports (403); real per-chatbot label error rates; per-host trigger rates |
| 03 Learning science (new in wave 2) | — | OpenAlex abstracts by DOI; meta-analyses on contrasting cases, self-grading, drawing, relearning, productive failure, generation and implementation intentions; code reads of `plan.py` and `service.py`; cross-field links: psychometrics/CAT exposure control, game design, behavioural economics, surgical checklists | No new scout | — | EEF pages (403, secondary only); several binary PDFs |
| 04 Economics education | Primary research PDFs (Ferraro & Taylor, TUCE-4, Shanahan et al.); nine 9EC0 examiner reports, summarised only; citation chaining; cross-field concept inventories; our count of the demo captures | **Exam mark-scheme tallies** (June 2025 9EC0 mark schemes, point vs level marks, numbers only); **CS-education Parsons problems**; writing-to-learn meta-analyses; ERIC and OpenAlex abstracts | No new scout. Consistency edit from 05 (MCQ key) | A testwise-student audit of every MCQ before and after the drafted pack rows (`testwise.py`) | TEL-4 high-school data; whether chain tasks raise levelled essay marks |
| 05 Product features | Vendor help centres and terms; web search limited to vendor domains; repo reading | Vendor admin docs (Copilot Studio, Entra, Microsoft message centre, Mistral); standards (IETF RFC 6750, NCSC, DfE cyber standards, MCP authorization spec); a code check of the `mcp` SDK; learning-analytics dashboard reviews; **epidemiological surveillance analogy and simulation** (Farrington's minimum-count rule; exact binomial and beta-binomial runs in `sims/teacher/`); **disclosure-control standards** (DfE, NHS HES, ICO, ONS) | **Accessibility:** DfE SEN and EAL statistics, Ofqual access arrangements, Equality Act Schedules 10 and 13, WCAG 2.2, accommodation meta-analyses; a readability computation and a distractor audit of the example pack | **Direct fetch of Microsoft Learn** pages (education guide table of contents) and Message Center posts via a third-party mirror's published index | Live tests on Copilot Studio or any school tenant (read-only rule); OpenAI help pages (403); the pooling calculation is not saved in the repo |
| 06 Simulation | A synthetic-student harness running the real `tutor_turn` code on the example pack (`sims/`) | The report was written after the wave-1 runs (findings w1-06): deterministic bug probes, detector and decay sweeps, a partial rerun by the verifier | **Decay simulation** (`sims/decay/`): first-principles crossing times, deterministic cases and a paired 960-student population run of three fixes, with rebuild determinism checks; a reliability-engineering analogy | **Patch-and-rerun** of the clamp, step-back, quiz-me and decay fixes on copies of the 05e branch (`probes_w4.py`, `check_mcp.py`); focus fix measured on a 64-line test set and an 18-line holdout | `sensitivity.py` not run; a full 9EC0 pack |
| 07 Demo (→ `demo-plan.md`) | The product run offline; multimedia-learning meta-analyses; practitioner guides; cross-field checklists | No new scout. Consistency edit from 02 and 06 | **Scripted demo rehearsal** (`sims/demo-05e/`): the Plan A episode driven against the 05e branch's MCP server with scripted labels; resolver probes; `check_mcp.py` on two settings copies | **Integration verification:** five patches stacked on the 05e export, conflicts merged by hand, check_mcp and the six Plan A takes rerun after each step; every single skip tested | An end-to-end run of 05e in claude.ai |
| 08 Market and business (→ `business-plan.md`) | Official statistics; the DfE Technology in Schools survey; gov.uk buying guidance; competitors' public pages; first-principles MDES maths | **Procurement records via Find a Tender** (OCDS API) and the Contracts Finder API; the Ofqual Register API; vendor announcements (Google, Anthropic, OpenAI, Khan); the European Commission AI-literacy Q&A | **Microsoft pricing:** the Azure Retail Prices API and the Copilot Credit estimator, MS Learn billing pages; the DfE Technology in Schools PDF. **Copyright:** legislation (CDPA, database regulations, Trade Marks Act), IPO guidance and **exam-board policy documents** (Pearson, AQA), CLA licences | **Direct fetch of Ofqual tables** (the annual qualifications market report's ODS data tables, found via the gov.uk content API); JCQ returned 403 | What schools pay for Up Learn, Seneca or Eedi; the share of sixth forms with learner Copilot on |
| 09 Safety and ethics | DfE standards and guidance; vendor terms; a code read of `edux/` and `text/` | **Survey grey literature** shared with 02; the Bastani RCT full text (PMC); retraction and preprint status checks | **ICO, KCSIE and IRMS guidance:** ICO lawful-basis, children, rights, DPIA and Art 28 pages; DfE data protection toolkit; KCSIE 2026 full text; the IRMS academies retention toolkit; competitors' privacy pages | — | KCSIE detail for components; the Internet Matters and Ofcom PDFs (blocked or binary) |
| All areas | Red-team panel: six personas | Red-team panel: six personas in three paired files | Red-team panel: six personas in three paired files. **The shared web-search budget ran out during wave 3**; later work uses code, simulation and direct fetches only | **Pitch red team** (three personas: judge, teacher, student) against the script, with a number check against `findings.csv`. No web search; direct fetches only | — |

## Open questions

### Wave-1 questions, with wave-2 status
Status: **done** = a finding or report answers it; **partly** = part answered; **open** = not yet researched; **blocked** = needs a human or access we don't have.

| # | question | raised by | status |
|---|---|---|---|
| 1 | Can UK 16–17-year-olds use a custom remote MCP server today, and through which product and setting? Under what DPA? | investor, DPO | **partly**: Copilot Studio in a K-12 Microsoft 365 tenant is documented (w2-05-03 ✓, w2-05-04 ✓); untested; the DPA and teen protections for custom agents are open (wave-3 Q4–5) |
| 2 | Does a per-student key in a URL meet the DfE security standard and NCSC guidance? What is the minimum sign-in that Copilot Studio and claude.ai accept? | DPO | **done** in [05](05-product-features.md): it conflicts with IETF, NCSC and the MCP spec; DfE is silent (w2-05-05 ✓, -10 ✓, -11 ✓, -12 ✓). The header fix is not built |
| 3 | What does the Challenge 1 brief say, and does eduX's scope match it? | judges | **blocked**: needs a human to paste the brief |
| 4 | Can a 75-second literacy segment run end to end on the merged 05e build in claude.ai without a retake? | judges | **open**: Wednesday's 18:00 gate |
| 5 | Which BKT settings for literacy parts keep a student without the skill below "secure" under label noise? | judges, researcher, student | **done** (simulation: synthetic students): three settings, no code ([02](02-ai-literacy-assessment.md) rec 2; w2-02-02 ✓, -08 ✓) |
| 6 | How do embedded assessments treat non-response without scoring disengagement as low skill? | researcher, student | **done**: treat ignored tasks as missing (NAEP, PISA; w2-02-11 ✓, -12 ~). Not built |
| 7 | How accurately do Claude and ChatGPT self-label `pushback_changed`, `conflict_flagged` and `web_access` across about 20 scripted transcripts? | researcher | **open**: audit designed ([02](02-ai-literacy-assessment.md) rec 19), not run |
| 8 | In chatbots with web search, what share of bad citations are misattribution rather than invention? | researcher | **partly**: with search on, about a quarter to a third of citations or statements are unsupported, with few invented links (w2-02-33 ~, -34 ✓); no figure for claude.ai on UK data |
| 9 | Do question-feature checklists predict better verification, or are they rituals? | researcher | **open**: only indirect evidence (w2-09-15 ~) |
| 10 | What share of UK 16–18-year-olds' chatbot use is homework help rather than factual lookup? | student | **done**: among monthly users aged 16–18, 70.4% homework help, 69.7% asking questions, 45.5% summarising (w2-09-01 ~) |
| 11 | For each 9EC0 paper, what share of marks is point-marked and what share level-marked? | teacher | **done**: about 34% point-marked, 66% level-marked, 3.5% MCQ (w2-04-02 ✓) |
| 12 | Do server-scorable tasks (chains, missing links, diagram shifts) predict or improve extended-writing marks? | teacher, student | **partly**: cross-field evidence only (Parsons problems, writing-to-learn; w2-04-04 ~ to -09 ~); no economics test |
| 13 | In voluntary tutoring tools, does question-before-answer cut return use compared with answer-then-check? | student | **open** |
| 14 | How long does a teacher take to review one part's rows, and how often are drafted corrections wrong? | teacher, investor | **open** (one error in nine parts; no rate) |
| 15 | What do UK economics teachers want from a teacher view? What is the smallest report within the privacy checklist? | teacher, judges | **partly**: one-screen spec, alarm rule and coordinator decision in [05](05-product-features.md); no teacher asked |
| 16 | Do visible usage stats, and the chance a teacher sees them, change teenagers' honesty or make them switch tools? | student | **open** |
| 17 | How long do comparable UK edtech providers keep pupil records after a pupil leaves? | DPO | **open**: [09](09-safety-ethics.md) rec 9 proposes our own default; comparable providers not checked |
| 18 | Under KCSIE 2026 and the DfE standards, what must a component do with a disclosure it processes but doesn't store? | DPO | **open**: [09](09-safety-ethics.md) recs 13, 15, 19 propose a signpost and a DSL route; KCSIE not checked |
| 19 | Did any host's study mode announce cross-session progress per topic in 2026? | investor | **done**: yes, Gemini (w2-08-01 ✓, -02 ✓); none found for ChatGPT (w2-08-03 ✓) |
| 20 | What do UK schools actually pay for Up Learn, Eedi or Seneca Premium? | investor | **partly**: procurement records for Sparx and Century (w2-08-06 ✓, -07 ✓); none found for Up Learn, Eedi or Seneca |
| 21 | Who buys AI-literacy assessment in the UK and EU, and at what price? | investor | **partly**: Article 4 requires no measurement (w2-08-09 ✓), so no compliance buyer; no other buyer named |

### Wave-3 questions, with wave-3 status (from [`judge-panel.md`](judge-panel.md))
Raised by the wave-2 panel. Tags: [I] investor, [D] DPO, [J] judges, [R] researcher, [T] teacher, [S] student.

| # | question | raised by | status |
|---|---|---|---|
| 1 | How many English sixth forms and colleges run Microsoft 365 A3/A5 with learner Copilot enabled for 13–17s? | I | partly: no official survey measures it (w3-08m-01 ✓); 34% of IT leads invested in increased-capability licences (w3-08m-02 ✓) |
| 2 | Does an MCP tool call in Copilot Studio bill as an agent action, and does an Agent Builder agent avoid it? | I, J | partly: Microsoft's estimator bills an MCP call at 5 credits (w3-08m-06 ✓); Agent Builder can't call external services (w3-08m-08 ✓); pages conflict on pro-code agents for unlicensed users (w3-08m-09 ✓) |
| 3 | Have Gemini study notebooks reached UK under-18 school accounts? | I | open |
| 4 | Do Microsoft's 13–17 Copilot protections apply to Copilot Studio custom agents and their MCP tools? | D | open: undocumented (carried to wave-4 Q11 and Q13) |
| 5 | Is there a DfE or ICO template DPA for an MCP plug-in behind a school's Microsoft 365 tenant? | D | done: none found; eduX writes its own from the ICO's Art 28 list (w3-09-03 ✓, -04 ~; [09](09-safety-ethics.md)) |
| 6 | What lawful basis do UK schools use for pupil-level analytics shared with teachers? | D | done: public task (Art 6(1)(e)), our reading of general ICO and DfE guidance; AI-literacy scores only where the school teaches it (w3-09-01 ✓, -03 ✓; [09](09-safety-ethics.md)) |
| 7 | Do any trusts or awarding bodies buy AI-literacy assessment, and at what price? | I | open |
| 8 | What do the brief's Desired Outcomes say about who uses the assessment? | J | blocked: needs a human to paste the brief |
| 9 | How often does claude.ai with search on misattribute citations on UK economic data? | J | open |
| 10 | What is per-host agreement between `source_conflict` / `pushback_changed` and a script, across five scripted failure modes? | R | open (audit designed: [02](02-ai-literacy-assessment.md) rec 19) |
| 11 | How many literacy moments does a typical student generate per week, per host? | R | open |
| 12 | Do NLT's checking items have a published base and wording that allow the 58.5% to be quoted correctly? | R | partly: the verifier found the base (those who had heard of generative AI; w2-09-02 ✓); the item wording is not checked |
| 13 | Do 16–18s disclose pasted AI text less when disclosing it triggers a task? | S | open |
| 14 | Across past 9EC0 8- and 12-markers, how often would a monopsony or "depends on elasticity" answer conflict with a C1 or C4 key? | T | open |
| 15 | Do faded-chain tasks raise blind-levelled analysis marks on economics essays? | T | open |
| 16 | How long does reviewing one C4 item take, and how often is its key disputed? | T | open |
| 17 | Can chatbot image input reliably label a photographed diagram's shift and direction for server scoring? | S | open |
| 18 | What flag rate does the alarm rule give if pooled across 2–4 sets of 10–16 students? | T | partly: [05](05-product-features.md) has a calculation, but it is not reproduced in the repo |
| 19 | Does a skippable within-session re-ask keep accuracy gains without cutting return use? | S | open |

### Wave-4 questions (from [`judge-panel.md`](judge-panel.md))
From the wave-3 panel: 18 after merging. Status after wave 4 (the tested patch series in [`wednesday-build-list.md`](wednesday-build-list.md), the Ofqual and Microsoft fetches in the [business plan](business-plan.md)). Patch results are simulations: synthetic students or scripted turns, example pack.

| # | question | raised by | status |
|---|---|---|---|
| 1 | In a claude.ai dry run, which labels does Claude send on the four Plan A lines? | J | open: Wednesday's dry run (build list item 9) |
| 2 | How often do real 16–18 research questions contain the resolver's trigger words, and how often does it pick the wrong part? | S, T | partly: patch 0002 cuts false focus on a 43-line test set from 15 to 3 (w4-fix-focus-1 ✓); real-student frequency still open |
| 3 | Whom do the brief's Desired Outcomes name as the user of the assessment? | J | blocked: needs a human to paste the brief |
| 4 | Under the decay fix, does How AI works AUC on the 05e branch rise above 0.5 (from .40)? | J, R | **done**: 0.85/0.88 with patch 0005 (none vs strong, N = 60, simulation; w4-fix-core-4 ✓) |
| 5 | When reporting a failed check lowers a score, do students report fewer failures? | S | partly: patch 0003 removes the penalty (a found problem scores Verify 1; w4-fix-verify-1 ✓); the behaviour question is not tested |
| 6 | With 8–16 message clusters, how well does a cluster-bootstrap CI for κ keep its coverage? | R | open |
| 7 | What published LLM-vs-human κ figures exist for question-quality features? | R | open |
| 8 | Does an unprompted-feature Ask score separate novice and practised personas? | R | open |
| 9 | After fix (b), does the `untested` review fire and pull a talk-only part back down? | T | **done**: with patch 0005 a talk-only part reads 0.300 (new), not 0.763 (secure), and a never-answered prerequisite gets a check (w4-fix-core-4 ✓) |
| 10 | Does a three-option, plain-claim MCQ cut right answers without the economics? | S | partly: four-option plain-claim keys (patch 0004) bring a testwise student to chance, 0.28 vs 0.31 (w4-fix-mcq-1 ✓); the three-option variant was not adopted |
| 11 | Can K-12 learners in "not adult" accounts invoke custom or third-party declarative agents in Copilot Chat? | I | partly: implied, not stated; an opt-in Study and Learn-only switch blocks other agents (w4-08-01 ~, -02 ✓); needs Microsoft or a tenant test |
| 12 | Do any UK schools switch on Copilot pay-as-you-go for students, and under what cap? | I | open |
| 13 | Do Microsoft's Product Terms or DPA cover Copilot Studio custom-connector traffic to third-party MCP servers? | D | open |
| 14 | Does a school relying on DPA 2018 Sch 1 para 18 for a chatbot signpost need an appropriate policy document? | D | open |
| 15 | What share of A level Economics entries in England go to Edexcel (9EC0)? | I | **done** for certificates: 21,005, 51.5% in 2024–25 (w4-08-08 ✓); the 2026 entries split is not published yet |
| 16 | How many turns a week do sixth-formers send to a course tutor, by published usage data? | I | open |
| 17 | In a university team's school pilot, who is the data controller, and which Art 6 basis applies? | D | open |
| 18 | How many teacher-hours do the pilot's RQ3, RQ8 and DPIA steps take per school? | T | open |
