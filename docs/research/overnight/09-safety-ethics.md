# 09 · Safety and ethics: DfE standards, offloading evidence, equity, and the DPO's objections

Waves 1 and 2 (overnight 17–18 Nov 2026). Sources:
- Wave 1: w1-09-* in `work/w1/w1-08.md` (marks in `verify-C.json`), w1-05-* (`verify-A.json`), and a read of the eduX code on branch `research/overnight`.
- Wave 2: `work/w2/w2-09.md` (usage, offloading, equity; marks in `verify-E.json`), `work/w2/w2-05.md` and `w2-05t.md` (routes, keys, teacher view), and the DPO's wave-2 objections in `work/w2/panel-investor-dpo.md`.

We changed no code. **Every fix here is a recommendation; none is built.** On 18 Nov, `edux/server.py` still reads the key only from `?key=` (lines 55–57, 86–89). There is no delete, export, revoke or retention code.

## Summary
- **eduX partly meets the DfE Generative AI product safety standards** (w1-09-01 ✓ to w1-09-03 ✓). It meets the anti-manipulation standards. The gaps are safeguarding (no DSL route), data rights (no retention, erasure or export) and key security. Every fix is a plan, not code (DPO wave 2 #5).
- **Offloading: the best evidence is one RCT.** Bastani et al. ran it with about 1,000 Turkish high-school maths students (w2-09-08 ✓).
  - Unguarded GPT-4 raised practice scores by 48% but cut the unassisted exam by 17%, about −0.2 SD (our calculation).
  - A guarded tutor raised practice by 127% and **avoided the harm, but showed no exam gain**.
  - Say "avoided harm". Never say "improved learning".
- **The rest of the "AI makes you think less" literature is weak.**
  - "Your Brain on ChatGPT" is an unreviewed preprint with 18 adults in its key session (w2-09-11 ✓).
  - Gerlich (2025) is correlational (w2-09-12 ~).
  - The Wang & Fan meta-analysis (g = 0.867) was **retracted on 22 April 2026. Never cite it** (w2-09-13 ✓).
  - Lab RCTs show AI improving the *product* without improving knowledge (w2-09-10 ~).
- **How UK 16–18s use AI (self-report, opt-in sample):**
  - 70.6% have used generative AI, and about half of those use it weekly. The 52% weekly figure is a share of users, not of all 16–18s (w2-09-01 ~).
  - 58.5% say they check its output and 10.0% say they just copy it (w2-09-02 ✓).
  - A quarter of teens who felt confident at spotting AI content failed Ofcom's test (w2-09-04 ✓). Confidence is not skill.
- **Equity: the gap is in quality of use, not access.**
  - FSM and non-FSM pupils use AI equally (66.7% vs 67.0%). FSM pupils more often just copy (30.0% vs 24.0%) and less often feel able to write a good prompt (w2-09-03 ✓).
  - In the US, 20% of teens in households under $30k do all or most schoolwork with chatbots, against 7% at $75k+ (w2-09-07 ✓, not UK).
  - So eduX must never read "no evidence" as "low literacy", must keep the Ask score language-light, and must never profile by FSM, SEND or EAL.
- **The DPO's wave-2 points:**
  - Le Chat is a consumer contract and can't go in a school's DPIA.
  - On Copilot, the processor chain must be drawn: Microsoft under the school's M365 terms, eduX under its own DPA.
  - The teacher view needs a lawful basis named by the school and a privacy-notice line.
  - The new `offered_misconception_ids` log needs a retention period. We propose 28 days (our choice).
- **Teacher view (coordinator decision):** per-student completion is a school opt-in, default off. Levels, AI-literacy scores, offloading and draft counts are never shown per student. Offloading and draft counts are not in the teacher view at all. DfE's per-learner usage and offloading reports therefore stay a **deliberate, stated gap**.
- **Most fixes are small and can be done on Wednesday:**
  - delete the "use what you already know" line;
  - pseudonymous ids;
  - hashed keys and revoke/rotate;
  - a bearer header;
  - delete/export commands;
  - a written retention default.

## Ranked recommendations

All are for the build team or the pitch. File paths are where the change lands.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **Delete "use what you already know about the student"** from `text/style.md:3` and `docs/build/steps/05b-one-call-per-turn.md:111`. Fall back to a neutral everyday example. | build | S | yes | panel: DPO w1 #5 |
| 2 | **Offloading evidence line for the pitch:** "In a 1,000-student RCT, unguarded GPT-4 raised practice scores 48% but cut exam scores 17%. A guarded tutor avoided the harm." Footnote: Turkish high-school maths, 2023, GPT-4; the guarded tutor showed no exam gain. | pitch, video | S | yes | w2-09-08 ✓, w2-09-09 ✓ |
| 3 | **"Never cite" list in the deck checklist:** Wang & Fan 2025 (retracted); "Your Brain on ChatGPT" (unreviewed, small); Gerlich as causal; "AI rots your brain". If a judge asks: "early, small or retracted; we rely on RCTs like Bastani." A grep on 18 Nov found no Wang & Fan citation in `docs/`; check the deck too. | pitch | S | yes | w2-09-11 ✓, w2-09-12 ~, w2-09-13 ✓ |
| 4 | **Under-18 wording:** caption the demo as an adult account. No 16–17-year-old on a consumer chatbot. **No Le Chat on any pupil-facing slide**; if asked, "adults only". | video, pitch | S | yes | w1-05-02 ✓, w2-05-01 ~; DPO w2 #1 |
| 5 | **Accept the key in an `Authorization: Bearer` header** (`edux/server.py` `_key_from_scope`, `require_student`). Keep `?key=` only for adult ChatGPT testing, since ChatGPT can't send custom keys. ChatGPT is not a pupil route. | build | S | yes, after filming | w2-05-08 ✓, w2-05-10 ✓, w2-05-11 ✓ |
| 6 | **Hash keys.** Store SHA-256 and look up by hash (`learner.py:91–94, 104–105`). Do it after filming, or make `seed --reset` copy the stored hash so demo connector URLs keep working. | build | S | yes, after filming | panel: DPO w1 #2 |
| 7 | **`revoke-key` and `rotate-key` commands** in `edux/cli.py`. | build | S | yes, after filming | panel: DPO w1 #2 |
| 8 | **`delete-student` and `export-student` commands.** Reuse the table list in `demo.remove_students()`. Export as JSON. | build | S | yes | panel: DPO w1 #4, w2 #5 |
| 9 | **Retention default in the docs and safety statement** (our choice): end of course plus one term, run by `delete-student`. For `offered_misconception_ids`, if added: clear values after 28 days (two teacher-view windows). | build docs | S | yes | panel: DPO w1 #4, w2 #4 |
| 10 | **Pseudonymous default ids** (random, not name slugs), so names don't reach `call_log`. | build (`learner.py:90–91`) | S | yes | panel: DPO w1 #2 |
| 11 | **Score fairly:** show AI-literacy levels as "not enough evidence yet" until 3 moments (our choice). Record ignored tasks as missing, not 0. Never infer off-platform AI use. Tell the chatbot to score Ask features regardless of spelling, grammar or language (EAL). | build (`edux/`, `text/`) | S | yes | w2-09-01 ~, w2-09-03 ✓; see [02](02-ai-literacy-assessment.md) |
| 12 | **"What your teacher sees" line** in the student's progress text (wording in [05](05-product-features.md) rec 6). It serves as the privacy-notice line for the teacher view. | build (`text/`) | S | yes | panel: DPO w2 #4; student w2 #3 |
| 13 | **Wellbeing signpost step.** A new label `wellbeing_concern`. When true, the server stops teaching and points to a trusted adult and the school's DSL route. Store a count only. | build (`edux/plan.py`, `text/moves/`) | S | yes, if time | w1-09-02 ✓ |
| 14 | **Light friction on "just show me":** with no attempt yet, show a guided example with the last step left to the student. The follow-up check is skippable. | build | M | yes, if time | w1-09-01 ✓ |
| 15 | **DSL contact at setup:** say it in the pitch now; build it later as a required school-config field. | pitch now; build later | S | pitch yes | w1-09-02 ✓ |
| 16 | **Processor-chain diagram and DPA template for the Copilot route**: pupil → Microsoft (the school's M365 terms) → eduX (eduX DPA, processor to the school). Include an open item: whether Microsoft's teen protections cover custom MCP agents. | business plan | M | no | w2-05-03 ✓, w2-05-13 ✓; DPO w2 #2 |
| 17 | **DPIA starter and one-page safety statement**: purpose, owner matrix, data held, retention, `STORE_PROMPTS=0`, a filtering-review paragraph, and the teacher-view lawful-basis line for the school to fill in. | business plan | M | no | w1-09-01 ✓ to w1-09-06 ✓ |
| 18 | **Entra sign-in for pilots** (M), then an OAuth broker (L). See [05](05-product-features.md). | build later | M / L | no | w2-05-05 ✓, w2-05-07 ✓ |
| 19 | **DSL alert route** (email or webhook to the DSL in an agreed time). | build later | L | no | w1-09-02 ✓ |

## Offloading: what the evidence supports

| Study | Design and population | What it found | Outcome type | How to use it |
|---|---|---|---|---|
| **Bastani et al. 2025, PNAS** (w2-09-08 ✓, w2-09-09 ✓) | Preregistered RCT; about 1,000 students in about 50 grade 9–11 classes at a Turkish high school; randomised by class; four 90-minute maths sessions; Fall 2023; GPT-4 | **GPT Base:** practice +48%; unassisted exam −0.054 on a 0–1 scale (SE 0.022), −17%, about −0.2 SD (our calculation). **GPT Tutor (guarded):** practice +127%; exam −0.004 (SE 0.013), not significant: **no harm, no gain**. GPT Base was right only 51% of the time. In session 1, 67% of GPT Base students' first messages asked for the answer or repeated the question (37% for Tutor). Tutor students thought they had done better on the exam | Learning (same-day exam); engagement (logs); perception | Headline evidence for "a guarded tutor, not an answer machine". Not UK, not economics, not current models |
| Kestin et al. 2025 (w2-09-14 ✓) | Crossover RCT; 194 Harvard physics undergraduates | Structured AI tutor beat in-class active learning: 0.63 (linear), more by quantile regression; immediate test only | Learning | Structure decides whether AI helps. Don't say "doubled learning" |
| Fan et al. 2025, BJET (w2-09-10 ~) | Lab RCT; 117 university students | The ChatGPT group improved essay scores most, with no significant difference in knowledge gain or transfer. Comparison groups: human expert, writing-analytics tools, no extra tool (not a checklist; verifier) | Task product vs learning | "Lab studies" only. AI improves the product, not the learning |
| Darvishi et al. 2024 (w2-09-15 ~) | RCT; 1,625 university students, 10 courses | Students relied on rather than learned from AI prompts. Self-monitoring checklists partly filled the gap. (That quality "fell" on removal is implied, not stated in the abstract) | Task performance | Supports making the student do the check |
| Kosmyna et al., "Your Brain on ChatGPT" (w2-09-11 ✓) | arXiv preprint (v2 31 Dec 2025), unreviewed; 54 adults, 18 in session 4 | EEG and recall differences. The authors' FAQ rejects "dumber" and "brain rot" readings | Neural engagement; recall | **Don't cite** |
| Gerlich 2025 (w2-09-12 ~) | Mixed-method survey and interviews; 666 adults; corrected Sept 2025 | Negative correlation between AI use and critical thinking, mediated by offloading (r not checked) | Self-reported critical thinking | **Don't cite as causal** |
| Wang & Fan 2025 (w2-09-13 ✓) | Meta-analysis, g = 0.867 | **Retracted 22 April 2026** (Nature Retraction Note, *Humanities and Social Sciences Communications*), "discrepancies in the meta-analysis" | — | **Never cite** |

**What this means for eduX:**
- The plan server is a guardrail of the GPT Tutor kind. The evidence says guardrails remove harm, not that they add learning.
- So the pitch can say: "Unguarded chatbots can harm learning; eduX keeps the student doing the work."
- It must not say: "eduX improves learning."
- Bastani's students also misjudged their own learning, which supports moving `p_known` only on evidence, never on self-report.

## Equity

| Gap | Figure | Population | Implication for eduX |
|---|---|---|---|
| Use by FSM | 66.7% vs 67.0% (w2-09-03 ✓) | UK 13–18, NLT opt-in schools | Access isn't the gap. Guided use is the offer to state schools |
| "Just copy" by FSM | 30.0% vs 24.0% (w2-09-03 ✓) | as above | Own-first and Verify moments help most where copying is commonest. Population-level argument only; **never profile by FSM** |
| Prompt confidence by FSM | 38.9% vs 44.0% (w2-09-03 ✓) | as above | Keep the Ask score language-light (rec 11) |
| Income, US | 20% (<$30k) vs 7% ($75k+) do all or most schoolwork with chatbots (w2-09-07 ✓) | US teens 13–17, Pew probability panel | Heaviest offloading sits with lower-income teens. Business-plan argument, labelled US |
| Vulnerable children | 50% vs 31% say a chatbot is like a friend; 50% of vulnerable users vs 40% overall have no concerns about following its advice (w2-09-16 ✓, primary PDF) | UK 9–17, Internet Matters | Verify moments matter more for them and must stay one line and skippable. **Don't single out SEND students** |
| Social grade, younger children | ABC1 vs C2DE "to learn" 52% vs 34%; private vs state 52% vs 18% among 8–12s (w2-09-17 ✓) | UK 8–12 and 8–17, **not 16–18** | Context only; wrong age for the pitch |
| Non-users | About 30% of 16–18s haven't used generative AI (w2-09-01 ~) | UK 16–18 | Missing evidence is missing, not low (rec 11) |

Gender gaps are small: girls use AI more for homework, boys more often weekly, and checking is the same (w2-09-03 ✓). No UK survey we found splits checking by SEND or EAL.

**Detecting AI-written work is out of scope.** Detectors are biased against non-native writers (personalisation review row 6-14).

## DfE Generative AI product safety standards matrix

Source: DfE, *Generative AI: product safety standards*, updated 19 Jan 2026 (w1-09-01 ✓ to w1-09-03 ✓). Expectations are paraphrased. eduX never generates text, so the host owns some rows. **Every "fix" below is unbuilt.**

| # | Expectation (paraphrased) | eduX status | Owner | Product response |
|---|---|---|---|---|
| 1 | State the purpose; don't overstate impact | partly | eduX | Purpose paragraph. No efficacy claims; Bastani's guarded tutor avoided harm, it didn't add learning |
| 3 | Filtering across the whole conversation | n/a | host + school | Deploy only in school-provisioned chatbots. Microsoft's teen protections apply to Copilot apps "where applicable" (w2-05-13 ✓); coverage of custom agents unknown |
| 4 | Activity logs | partly | host; eduX logs labels | `exchange_log` stores labels and the offloading flag. Message text only if `STORE_PROMPTS=1` (default 0) |
| 4 | DSL contact at setup; alert on disclosures | **gap** | school + host; eduX can add | Recs 13, 15; alert route later (rec 19) |
| 4 | Report each learner's usage duration | **gap (deliberate)** | eduX + school | Not shown per student (w2-05t spec and personalisation §5). Stated as a gap, not hidden |
| 5 | Security: authentication, permissions | **gap** | eduX | `?key=` in plaintext, no revoke. Recs 5–7 (S), Entra (M), broker (L). The key conflicts with NCSC and IETF guidance (w2-05-10 ✓, w2-05-11 ✓). DfE's cyber standards don't address URL keys (w2-05-12 ✓) |
| 6 | Privacy notice, DPIA, Children's code | partly | eduX + school | Checklist in personalisation §5; recs 8, 9, 12, 17 |
| 7 | No commercial use or training on learner inputs | meets (eduX) | eduX; host | eduX stores no student text by default and trains nothing |
| 8 | Child-centred design; testing with children | gap | eduX | Pilot student testing through the school |
| 9 | Risk assessment, complaints route | gap | eduX | Safety statement (rec 17) |
| 10 | No full answers by default; attempt first; friction | **partly** | eduX + host | One point plus an MCQ check meets it. "Just show me" skips the attempt (rec 14). Bastani supports this standard directly (w2-09-08 ✓) |
| 10 | Track and report offloading | partly: **tracked; reporting is a deliberate gap** | eduX | The `offloading` flag is tracked per exchange. Offloading and draft counts are not in the teacher view (coordinator decision): showing them would teach students to hide AI use |
| 11 | No anthropomorphism; no engagement-prolonging | meets / partly | host + eduX | No streaks; stopping offered neutrally; time limits advisory only |
| 12 | Detect distress; tiered response to human help | gap | host primarily | Rec 13 |
| 13 | No sycophancy, dark patterns, paid steering | meets (eduX) | eduX + host | No paid student tier |

**Never claim "DfE compliant".** For the safety slide, use six rows: 10 (partly), 11 (meets), 4 safeguarding (gap, closing), 5 security (gap, closing), 3 filtering (host), 7 no training (meets).

**Other guidance:** schools must follow AI tools' age limits (w1-09-05 ✓); filtering and monitoring reviews must cover generative AI (w1-09-06 ✓); JCQ and Ofqual AI rules barely touch an exam-only course (w1-09-07 ✓).

## The DPO's objections, waves 1 and 2

| # | Objection | What the code or docs show | Fix | Status |
|---|---|---|---|---|
| w1 #1 | No lawful under-18 route; no processor chain | claude.ai 18+ (w1-05-02 ✓). The Copilot route is documented and untested (w2-05-03 ✓, w2-05-04 ✓) | Copilot Studio test; rec 16 | Partly |
| w1 #2, w2 #3 | Key is a long-lived secret in a URL, in plaintext; name-slug ids | `server.py:55–57, 86–89` read only `?key=`. Raw storage and lookup at `learner.py:91–94, 104–105`. No revoke. Ids from names (`learner.py:90–91`). The access log is off (`server.py:203`) | Recs 5–7, 10; Entra (M) | Recommended |
| w1 #3 | Every message reaches eduX; no safeguarding route | Message passed word for word (`tools-and-context.md:38`); not stored by default (`STORE_PROMPTS=0`) | Recs 13, 15, 19 | Recommended |
| w1 #4 | No retention, erasure or export | No `delete-student` or `export-student` | Recs 8, 9 | Recommended |
| w1 #5 | "Use what you already know about the student" | `text/style.md:3` | Rec 1 | Recommended |
| **w2 #1** | **Le Chat can't go in a DPIA** | Consumer terms, "personal capacity", parental permission "where required", UK not named (w2-05-01 ~); no DPA | Off all pupil-facing material; adults-only testing (rec 4) | **Answered** in the reports ([05](05-product-features.md)) |
| **w2 #2** | **Copilot: who processes what?** | The school's agent sends each turn from Microsoft to eduX. Power Platform data policies govern MCP access (w2-05-03 ✓). Teen protections cover Copilot apps and agents "where applicable" (w2-05-13 ✓) | Q&A: "eduX is your processor under our DPA; Microsoft under your existing M365 terms." Diagram and DPA (rec 16); test teen-protection coverage | Partly |
| **w2 #4** | **Teacher view: lawful basis; pupils told; necessity and retention of `offered_misconception_ids`** | Not built. The design is minimised: k = 6, bands, one window, never "anonymous" (w2-05-34 ✓) | The school names the lawful basis in its DPIA (we haven't researched which basis UK schools use). Pupils are told by the progress-text line (rec 12). The log is needed for the right denominator; values cleared after 28 days (rec 9, our choice). Class AI literacy only in bands, groups of 6 or more, opt-in | Partly |
| **w2 #5** | **Wave-1 fixes are unbuilt** | Confirmed: no delete, export, retention, revoke or header code | Recs 5–10 are S and fit Wednesday | **Open** until merged |

**Q&A answers the DPO wants to hear:**
- *What can a teacher see about one child?* "Nothing about how well they're doing. If the school switches it on, whether they did checks this week. Never levels, AI-literacy scores, chats or how often they asked AI to write for them."
- *Can a teacher identify a pupil from a band?* "Counts of 5 or fewer are never shown, shares are banded, and 'all' is never shown. It is minimised, not anonymous."
- *A pupil's key leaks?* Today: "We can't yet revoke it; that's a one-command fix we're making." After recs 6–7: "Revoke with one command; keys are hashed."
- *Why mention Le Chat?* "We don't, to pupils. Adults only."

## Later (not before Thursday)
- Recs 16–19.
- **Message minimisation:** the chatbot sends topic terms instead of the full message. That trades off matching quality; test it first.
- **Advisory daily-minutes setting** that returns only `offer_stop` once a school limit is passed.
- **Open questions:** whether Microsoft's teen protections cover Copilot Studio custom MCP agents; whether a DfE or ICO template DPA exists for a plug-in behind a school's M365 tenant; which lawful basis UK schools use for pupil analytics shared with teachers; whether Kosmyna et al. pass peer review.

## Considered and rejected
- **Citing Wang & Fan, Kosmyna, or Gerlich as causal.** Retracted, unreviewed, or correlational (w2-09-11 ✓, w2-09-12 ~, w2-09-13 ✓).
- **Saying the guarded tutor improved learning.** Its exam effect was null (w2-09-08 ✓).
- **Draft or offloading counts in the teacher report** (w2-09 rec 4; wave 1 rec 13, class-level offloading report). Students would hide AI use, and the Verify evidence would disappear (student w2 #3). Ruled out by the coordinator.
- **Per-student levels or AI-literacy scores for teachers.** Non-core profiling of minors; ruled out.
- **Profiling or adapting by FSM, SEND or EAL.** The equity data are population-level arguments only.
- **Detecting AI-written work.** Biased against non-native writers.
- **Storing chat text for safeguarding.** Conflicts with minimisation; detection stays with the host.
- **Hard time limits enforced by eduX.** Impossible; the host can answer without calling eduX.
- **Using the Turing "52% private vs 18% state" figure in the pitch.** Ages 8–12 (w2-09-17 ✓).
- **Refusing to draft essays.** Conflicts with 05e "never a barrier". Bastani's tutor still helped, with hints first.
- **Claiming "DfE compliant".** Untrue.

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| No lawful under-18 route / processor chain | DPO w1 #1, w2 #2 | **Partly**: route documented, chain stated; untested; DPA not written |
| Key in URL, plaintext, no revoke, name-slug ids | DPO w1 #2, w2 #3 | **Recommended**: recs 5–7, 10 (S); Entra (M). None built |
| Verbatim messages, no safeguarding route | DPO w1 #3 | **Recommended**: recs 13, 15; alert route open |
| No retention, erasure or export | DPO w1 #4 | **Recommended**: recs 8, 9 (S), not built |
| "Use what you already know about the student" | DPO w1 #5 | **Recommended**: rec 1 (S), not built |
| Le Chat can't go in a DPIA | DPO w2 #1 | **Answered**: removed from pupil-facing material |
| Teacher view lawful basis, notice, retention | DPO w2 #4 | **Partly**: design, notice line and 28-day retention proposed; lawful basis is the school's |
| Wave-1 fixes unbuilt | DPO w2 #5 | **Open** |
| Does my teacher see I asked it to write my essay? | Student w2 #3 | **Answered**: never (coordinator decision); progress line (rec 12) |
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
| w2-09-01 | NLT 2025: 70.6% of 16–18s used GenAI; 52.0% weekly; monthly users: homework 70.4%, questions 69.7%, summarise 45.5% | correlational (survey) | UK 13–18, opt-in schools; 4,920 aged 16–18 | adoption | ~ 52% weekly is a share of 16–18 AI users, not all 16–18s |
| w2-09-02 | 58.5% of 16–18s check AI output, 10.0% just copy (13–16: 40.9%, 26.8%) | correlational (self-report) | as above | engagement (self-report) | ✓ |
| w2-09-03 | FSM use 66.7 vs 67.0%; copy 30.0 vs 24.0%; prompt confidence 38.9 vs 44.0% | correlational | as above; FSM n = 8,002 | adoption / engagement | ✓ |
| w2-09-04 | Ofcom 2026: 66% of 16–17s use AI; 25% of confident teens failed the image test | official document (survey) | UK 8–17 | adoption; prediction | ✓ |
| w2-09-05 | OUP: 47% confident they can tell if AI is true; 48% want teacher support | practitioner (survey) | UK 13–18 | adoption / self-rated | ✓ |
| w2-09-06 | DfE PPLV: 62% of 16–19s cite false information, 53% "takes away the need to think" | official document | England | attitudes | ✓ |
| w2-09-07 | Pew: 20% (<$30k) vs 7% ($75k+) do all or most schoolwork with chatbots | correlational (probability panel) | US 13–17 | adoption | ✓ |
| w2-09-08 | Bastani: GPT Base practice +48%, exam −17%; GPT Tutor practice +127%, exam n.s. | RCT (preregistered) | Turkish grades 9–11, maths | learning | ✓ |
| w2-09-09 | GPT Base correct 51%; first messages answer-seeking 67% vs 37%; Tutor students overrated their exam performance | RCT (log analysis) | as above | engagement; perception | ✓ |
| w2-09-10 | Fan: ChatGPT improved essay scores, not knowledge gain or transfer | RCT (lab) | 117 university students | product vs learning | ~ abstract only; comparisons were expert, analytics and no-tool control, not a checklist |
| w2-09-11 | Kosmyna: unreviewed preprint, 54 / 18 adults; authors reject "dumber" readings | quasi-experimental | US adults | neural engagement | ✓ |
| w2-09-12 | Gerlich: negative AI use – critical thinking correlation; corrected | correlational | 666 adults | self-reported critical thinking | ~ abstract only; mixed-method; r not checked |
| w2-09-13 | Wang & Fan meta-analysis (g = 0.867) retracted 22 Apr 2026 | official document (retraction note) | mixed | learning | ✓ (Nature Retraction Note read) |
| w2-09-14 | Kestin: structured AI tutor beat active learning, 0.63 | RCT (crossover) | 194 US undergraduates | learning | ✓ |
| w2-09-15 | Darvishi: students relied on AI prompts; checklists partly helped | RCT | 1,625 university students | task performance | ~ abstract only; "fell" implied, not stated |
| w2-09-16 | Internet Matters: vulnerable children treat chatbots as friends (50 vs 31%) | practitioner (survey) | UK 9–17 | adoption / trust | ✓ (primary PDF read) |
| w2-09-17 | Turing: private 52% vs state 18% among 8–12s; ABC1 vs C2DE | correlational | UK 8–12, 8–17 | adoption | ✓ |
| w2-09-18 | HEPI 2026: 94% of undergraduates use GenAI for assessed work; 12% paste AI text | official document (poll) | UK undergraduates | adoption | ✓ |

Also cited here; each sits in its home report's table: w1-05-02 ✓, w2-05-01 ~, w2-05-03 ✓, w2-05-04 ✓, w2-05-05 ✓, w2-05-07 ✓, w2-05-08 ✓, w2-05-10 ✓, w2-05-11 ✓, w2-05-12 ✓, w2-05-13 ✓, w2-05-34 ✓ ([05](05-product-features.md)).
