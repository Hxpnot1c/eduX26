# Overnight research

This folder holds research to make eduX a stronger entry for Cambridge EduX 2026, Challenge 1 ("Beneath the Surface: Defining and Assessing AI Literacy"). It builds on the personalisation review in [`../personalisation.md`](../personalisation.md) and does not repeat it.

Read [`MORNING-BRIEF.md`](MORNING-BRIEF.md) first.

## Files
| file | what it holds |
|---|---|
| [`MORNING-BRIEF.md`](MORNING-BRIEF.md) | One page: Wednesday's five actions, pitch points, risks, what changed |
| [`pitch-notes.md`](pitch-notes.md) | Claims we can make (exact wording, finding id, mark), claims to avoid, and an 8-slide deck outline |
| [`01-competition-fit.md`](01-competition-fit.md) | What the EduX rules ask for, how eduX scores against each criterion, and the defining-half gap |
| [`02-ai-literacy-assessment.md`](02-ai-literacy-assessment.md) | Our definition, the AILit crosswalk, the validity argument, the reliability maths, and scoring problems on the 05e branch |
| [`04-economics-education.md`](04-economics-education.md) | Gateway ideas, evidence-based misconceptions, 30 draft pack rows, the MCQ give-away and a content error |
| [`05-product-features.md`](05-product-features.md) | Which chatbots can reach eduX, at what age and on which plan, and the features the panel asked for |
| `06-*.md` (simulation) | **Not ready yet.** Synthetic-student simulations of the course learner model; scripts are in `sims/` |
| [`09-safety-ethics.md`](09-safety-ethics.md) | The DfE product safety standards matrix, the DPO's objections checked against the code, and ranked fixes |
| [`demo-plan.md`](demo-plan.md) | Video storyboard (Plan A and Plan B), live expo script, checklists, and bugs found while capturing |
| [`business-plan.md`](business-plan.md) | Market, buyers, pricing, competitors, distribution risk, regulation, evaluation plan |
| [`judge-panel.md`](judge-panel.md) | Red-team objections from six personas and whether each is answered yet |
| [`findings.csv`](findings.csv) | Every verified finding (✓ or ~), with its home report in `area_report`. ✗ findings are dropped |
| `sims/` | Simulation scripts, results and demo captures (synthetic students, example pack only) |
| `work/` | Briefs for scouts, verifiers, panel and writers; wave-1 scout notes, verifier marks and panel files |

Each finding appears in the findings table of one report only: its home report, given in `area_report`. Other reports cite it by id and link to that report.

## Method
Each wave runs in four stages:
- **Scouts.** Six to eight scouts each research one question.
- **Blind verifiers.** Each claim is checked by one blind verifier, who sees only the claim and its source. Four verifiers ran in wave 1.
- **Red team.** A panel of six personas attacks the product.
- **Editor.** An editor rewrites the reports, the pitch notes and this index.

Marks: ✓ confirmed against the source; ~ broadly supported, with a stated problem; ✗ dropped. Wave 1 produced 97 findings: 67 ✓, 30 ~ and 0 ✗.

Labels used throughout: "our choice" marks a number we chose. "Simulation: synthetic students" marks a simulated result. Neither is evidence about real students.

## Methods used so far
| question area | wave 1 methods | not reached in wave 1 |
|---|---|---|
| 01 Competition fit | The official EduX site (HTML and its scripts); Luma listings and organiser galleries; web search; framework sites; repo and git inspection | The Challenge 1 brief (renders only in a browser); the Oceania deck (needs sign-in); the Monash Friction page (403) |
| 02 Defining and assessing AI literacy | Primary framework documents (AILit, UNESCO, Long & Magerko, CAR, Ofqual, DfE), read from PDFs; OpenAlex and arXiv; psychometric validation studies and one exploratory meta-analysis; first-principles psychometrics (Spearman–Brown, attenuation, Fisher z); a BKT simulation; a code review of the 05e branch | Full texts of AILIT-S, AILQ and Chiu et al. (abstracts only); JCQ detail (image-only PDF) |
| 04 Economics education | Primary research PDFs (Ferraro & Taylor, TUCE-4, Shanahan et al.); nine 9EC0 examiner reports, summarised only; citation chaining from the Economics Network handbook; cross-field concept inventories and stock–flow studies; our own count of the demo captures | TEL-4 high-school data (unreadable fonts); Busom & Lopez-Mayan full text |
| 05 Product features | Vendor help centres and terms (Anthropic, OpenAI, Google, Microsoft, Oak); web search limited to vendor domains; search snippets where a page returned 403; repo reading | Live tests on ChatGPT, Copilot Studio or any school tenant (read-only rule) |
| 06 Simulation | A synthetic-student harness running the real `tutor_turn` code on the example pack (`sims/`) | In progress; report not ready |
| 07 Demo (→ `demo-plan.md`) | The product run offline (`capture_demo.py`, `check_mcp.py`); multimedia-learning meta-analyses (abstracts and secondary sources); practitioner guides (YC, Paul Graham, hackathon guides); cross-field checklists (surgery, aviation) | claude.ai message limits (needs a login); an end-to-end run of 05e in claude.ai |
| 08 Market and business (→ `business-plan.md`) | Official statistics (Ofqual, DfE capacity, CFR spend data); the DfE Technology in Schools survey; gov.uk buying guidance; competitors' public pages and terms; first-principles MDES maths | UK-wide JCQ entries; Edexcel's share; what schools actually pay competitors |
| 09 Safety and ethics | DfE standards and guidance (gov.uk); vendor terms; a code read of `edux/` and `text/` against the DPO's objections | KCSIE detail for components; NCSC guidance on keys in URLs |
| All areas | Red-team panel: investor, teacher, AI-literacy researcher, DPO, student, EduX judges | — |

## Open questions
Merged from the six panels ([`judge-panel.md`](judge-panel.md)). Status: **open** = not yet researched; **in progress** = partly covered, with work under way; **done** = a finding answers it; **blocked** = needs a human or access we don't have.

| # | question | raised by | status |
|---|---|---|---|
| 1 | Can UK 16–17-year-olds use a custom remote MCP server today, and through which product and setting (ChatGPT Edu, ChatGPT teen accounts, Copilot Chat for learners, a school-managed tenant)? Under what DPA and data residency? | investor, DPO | in progress (05 maps the documented routes; none tested; the Anthropic question needs a human) |
| 2 | Does a per-student key in a URL meet the DfE security standard and NCSC guidance? What is the minimum OAuth that Copilot Studio and claude.ai Team accept? | DPO | open |
| 3 | What does the Challenge 1 brief say (Desired Outcomes, Target Users), and does eduX's scope match it? | judges | blocked (needs a human to paste the brief) |
| 4 | Can a 75-second literacy segment run end to end on the merged 05e build in claude.ai without a retake? What breaks? | judges | open (Wednesday's 18:00 gate) |
| 5 | Which BKT settings for literacy parts (prior, learn rate, slip, decay) keep a simulated student without the skill below "secure" under 15% label noise? | judges, researcher, student | open (w1-02-32 ✓ simulated only the current settings) |
| 6 | How do embedded and stealth assessments treat non-response without scoring disengagement as low skill? | researcher, student | open (02 rec 4 proposes "missing"; literature not searched) |
| 7 | How accurately do Claude and ChatGPT self-label `pushback_changed`, `conflict_flagged` and `web_access` across about 20 scripted transcripts? | researcher | open |
| 8 | In chatbots with web search, what share of bad citations are retrieval misattribution rather than invention? | researcher | open |
| 9 | Do question-feature checklists predict better verification, or are they rituals? | researcher | open |
| 10 | What share of UK 16–18-year-olds' chatbot use is homework help rather than factual lookup? | student | open |
| 11 | For each 9EC0 paper, what share of marks is point-marked and what share level-marked? Which skills do the examiner reports link most to lost marks? | teacher | open |
| 12 | Do server-scorable tasks (ordering a chain of reasoning, finding the missing link, choosing the diagram shift) predict or improve extended-writing marks? Does MCQ retrieval improve essay marks compared with essay practice? | teacher, student | open |
| 13 | In voluntary tutoring tools, does question-before-answer cut return use compared with answer-then-check? | student | open |
| 14 | How long does a teacher take to review one part's rows, and how often are drafted economics corrections wrong? How long does a full 9EC0 pack take? | teacher, investor | open (one error found in nine parts; no rate) |
| 15 | What do UK economics teachers want from a teacher view? What is the smallest report within the privacy checklist in personalisation.md §5? | teacher, judges | open |
| 16 | Do visible usage stats, and the chance a teacher sees them, change teenagers' honesty or make them switch tools? | student | open |
| 17 | How long do comparable UK edtech providers keep pupil records after a pupil leaves? | DPO | open |
| 18 | Under KCSIE 2026 and the DfE standards, what must a component do with a disclosure it processes but doesn't store? | DPO | open |
| 19 | Did any host's study mode announce cross-session progress per topic in 2026? | investor | open |
| 20 | What do UK schools actually pay for Up Learn, Eedi or Seneca Premium (e.g. Contracts Finder)? | investor | open (list prices only: w1-08-07 ✓) |
| 21 | Who buys AI-literacy assessment in the UK and EU (exam boards, AI Act Art. 4 deployers), and at what price? | investor | open |
