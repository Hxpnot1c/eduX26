# 09 · Safety and ethics: DfE standards, the DPO's objections, and what to fix first

Wave 1 (overnight 17–18 Nov 2026). Sources: the w1-09-* findings in `work/w1/w1-08.md`, verifier marks in `verify-C.json` (one blind verifier per id), chatbot access findings from `work/w1/w1-05.md` (`verify-A.json`), the trust DPO's panel objections, and a read of the eduX code on branch `research/overnight` (file and line references below). We changed no code. Every fix here is a recommendation for the build team.

## Summary
- **eduX partly meets the DfE Generative AI product safety standards** (updated 19 Jan 2026; w1-09-01 ✓ to w1-09-03 ✓). It meets the anti-manipulation standards: no streaks, and stopping is offered neutrally. It partly meets cognitive development: one point at a time with checks, but "just show me" skips the attempt.
- **Three gaps matter most:** no safeguarding route (no DSL contact at setup, no signpost, no alert), no data-rights tools (no retention period, erasure or export), and weak key security.
- **The key works like a password, sits in the URL and is stored in plaintext.** It is read from `?key=` (`edux/server.py:55–57`), stored as is (`edux/learner.py:91–94`) and looked up as is (`learner.py:104–105`). There is no revoke or rotate command. Default ids are made from the student's name (`learner.py:90–91`) and written to `call_log` (`edux/service.py:467`).
- **Every message reaches eduX word for word** (`docs/build/reference/tools-and-context.md:38`, `text/tools/tutor_turn.md:2`), because the server matches it to the course (`service.py:245`). `STORE_PROMPTS=0` (default, `learner.py:283`) stops storage, not processing. So eduX can receive a disclosure of abuse or self-harm and has no route for it.
- **One instruction widens profiling.** `text/style.md` is sent to the chatbot with the first `tutor_turn` of each session (line 1), and line 3 tells it to "use what you already know about the student" when no interests are set. That pulls in the vendor's memory of a minor, outside any DPIA. The same rule is in `docs/build/steps/05b-one-call-per-turn.md:111`. Deleting it is the cheapest fix of all.
- **There is no lawful under-18 chatbot route yet** (w1-05-02 ✓, w1-05-09 ✓, w1-09-04 ✓). Without one, a DPO can't name the processor chain in a DPIA.
- **Most fixes are small.** Six can be done on Wednesday: drop the style line, pseudonymous ids, hashed keys, revoke/rotate, delete/export commands and a written retention default. Add a wellbeing signpost step if time allows. OAuth and a DSL alert route are later.
- **One tension to state, not settle:** DfE asks for per-learner offloading and usage reports, while our Children's code checklist keeps them off by default. The school, as controller, decides in its DPIA.

## Ranked recommendations

All are for the build team. File paths are where the change lands.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **Delete "use what you already know about the student"** from `text/style.md:3` (and the 05b step doc, line 111). Fall back to a neutral everyday example. | build (`text/style.md`) | S | yes | panel: DPO #5 |
| 2 | **Under-18 wording:** caption the demo as an adult team member's account; no 16–17-year-old on consumer claude.ai; no Gemini claim. | video, pitch | S | yes | w1-05-02 ✓, w1-05-09 ✓, w1-09-04 ✓ |
| 3 | **Hash keys.** Store SHA-256 of the key and look up by hash (`learner.py:91–94, 104–105`). The key is random (`token_urlsafe(16)`), so an unsalted fast hash is enough. Do this **after the video is filmed**, or make `seed --reset` copy the stored hash across: reset keeps demo keys so connector URLs keep working (`demo.py`), and a hashed key can't be printed again. | build (`edux/learner.py`, `edux/demo.py`) | S | yes, after filming | panel: DPO #2 |
| 4 | **Revoke and rotate commands** in `edux/cli.py`: `revoke-key <id>` and `rotate-key <id>` (prints the new URL once). Don't rotate demo students' keys before filming. | build | S | yes, after filming | panel: DPO #2 |
| 5 | **`delete-student` and `export-student` commands.** Reuse the table list in `demo.remove_students()` (`exchange_log`, `evidence_log`, `student_profile`, `issued_plan`, derived tables, `call_log` too). Export as JSON. | build (`edux/cli.py`) | S | yes | panel: DPO #4; ICO standard 15 |
| 6 | **Write a retention default** into the docs and safety statement: delete at end of course plus one term (the DPO's suggestion; our choice to adopt it), run by `delete-student`. | build docs | S | yes | panel: DPO #4 |
| 7 | **Pseudonymous default ids:** random ids, not name slugs, so names don't reach `call_log`. Keep `display_name` only where needed. | build (`edux/learner.py:90–91`) | S | yes | panel: DPO #2 |
| 8 | **Wellbeing signpost step.** New label `this_message.wellbeing_concern` (bool). When true, the server returns one step, `signpost`: stop teaching, supportive and non-validating wording, point to a trusted adult and the school's DSL route, no course content. Store a count only, never the text. The host's crisis handling stays primary. | build (`edux/plan.py`, `text/moves/`) | S | yes, if time on Wed | w1-09-02 ✓ |
| 9 | **Light friction on "just show me".** With no attempt yet on the point, `show` becomes a guided example: every step but the last, which the student completes. After an attempt or a reteach, show in full. Keep the `offloading` flag. This answers DfE std 10 without forcing an MCQ; it conflicts with the student panel's "answer first" ask, so make the follow-up check skippable. | build (`edux/plan.py`, `text/moves/show*.md`) | M | yes (Wed), if time | w1-09-01 ✓ |
| 10 | **DSL contact at setup:** a required field in school config; refuse to activate a school without one. One sentence in the pitch now. | pitch now; build later | S | pitch yes | w1-09-02 ✓ |
| 11 | **Rewrite the 05e "Why" bullet** (05e is built on its branch, not merged): cite DfE std 10 and Oreopoulos & Low (2026) accurately; drop the withdrawn "students stopped when refused answers" claim. | build docs | S | yes | w1-09-08 ~ |
| 12 | **One-page DPIA starter and safety statement** (purpose, owner matrix, data held, retention, `STORE_PROMPTS=0`, filtering-review paragraph). | business plan | M | no | w1-09-01 ✓ to w1-09-06 ✓ |
| 13 | **Aggregate teacher report** (class-level offloading and minutes), off by default, switched on by the school. | build later | M | no | w1-09-01 ✓, w1-09-02 ✓ |
| 14 | **DSL alert route** (email or webhook to the school's DSL within an agreed time). | build later | L | no | w1-09-02 ✓ |
| 15 | **OAuth 2.1** to replace keys in URLs. | build later | L | no | w1-05-07 ✓ |

## DfE Generative AI product safety standards matrix

Source: DfE, *Generative AI: product safety standards*, updated 19 Jan 2026 (w1-09-01 ✓, w1-09-02 ✓, w1-09-03 ✓). Expectations are paraphrased. eduX is one component, not the whole product: it never generates text, so the chatbot vendor ("host") owns some rows.

**Status** (eduX's part only): **meets** / **partly** / **gap**; **n/a** where only the host or school can act. **Owner:** eduX, host (the school's chatbot vendor), or school.

| # | Expectation (paraphrased) | eduX status | Owner | Concrete product response |
|---|---|---|---|---|
| 1 | State the purpose; don't overstate impact | partly | eduX | One-paragraph purpose (9EC0, ages 16–18, revision and homework plan). No efficacy claims until a pilot. |
| 2 | Use cases clear to buyers | partly | eduX | Pitch and README state the use cases. |
| 3 | Filtering of harmful content, across the whole conversation and devices | n/a | host + school | Deploy only in school-provisioned chatbots covered by the school's filtering. eduX returns only course-pack text and fixed moves. |
| 4 | Activity logs | partly | host; eduX logs labels | `exchange_log` stores labels, the offloading flag and evidence. Message text only if `STORE_PROMPTS=1` (default 0). Chat logs stay with the host. |
| 4 | Alert supervisors to harmful content | n/a | host | — |
| 4 | DSL contact at setup; alert on safeguarding disclosures; high-risk alerts in an agreed time | **gap** | school + host; eduX can add | Fix 8 (signpost step) and fix 10 (DSL field at setup). Alert route later (fix 14). |
| 4 | Report each learner's usage duration | gap (deliberate) | eduX + school | Sessions are derived from events. Reporting is off by default under our Children's code checklist; the school decides in its DPIA. |
| 5 | Security: authentication, permissions, testing before release | **gap** | eduX (server); host (model) | Plaintext key in the URL, no revoke. Fixes 3 and 4 (hash, revoke/rotate) now; OAuth later (fix 15). `settings_hash` records the version. |
| 6 | Privacy notice, DPIA, Children's code, no commercial use of data | partly | eduX + school | Checklist in `personalisation.md` §5; no model training. DPIA template, retention and erasure missing (fixes 5, 6, 12). |
| 7 | Don't use learner inputs commercially or for training | meets (eduX) | eduX; host for the vendor | eduX stores no student text by default and trains no model. Free consumer chatbots may train on inputs, a reason to use school tiers (w1-09-05 ✓). |
| 8 | Child-centred design; testing with children | gap | eduX | Pilot includes student testing, with consent, through the school. |
| 9 | Risk assessment, complaints route, published policies | gap | eduX | One-page risk assessment and a complaints email in the safety statement. |
| 10 | No final answers or full solutions by default; progressive disclosure; full solution only after a real attempt; friction before answer modes | **partly** | eduX (plan) + host (behaviour) | Default teaching is one point plus an MCQ check (meets). "Just show me" skips the attempt: fix 9. Research questions get full answers. DfE's named exception is reviewing prior knowledge; treating research answers as information is *our reading*, not DfE's words. |
| 10 | Track and report offloading | partly | eduX | The `offloading` flag is tracked per exchange (this sits under Cognitive development, not Monitoring, per the verifier). Nothing reported to teachers yet (fix 13). |
| 10 | Expert oversight; plan for impact on child development | gap | eduX | The evaluation plan (`business-plan.md` §9) doubles as the impact plan. |
| 11 | No anthropomorphism; task-bounded; no relationship-building | partly | host + eduX text | Server rule "never claim to be a teacher"; moves are task-bounded. The persona is the host's. |
| 11 | Default time limits; hard limits lifted only by a teacher | partly | host + school | `offer_stop` on fatigue is advisory. eduX can't enforce a hard limit, because the chatbot can answer without calling it. Say so. |
| 11 | Don't change responses to prolong engagement | meets | eduX | No streaks or rewards; stopping offered neutrally, progress kept. |
| 12 | Detect distress; tiered response always pointing to human help; published crisis protocol | gap | host primarily; eduX can add a tier | Fix 8. Never infer emotion into the learner model (personalisation checklist). |
| 13 | No sycophancy, flattery, pressure, dark patterns or steering to paid options | meets (eduX) | eduX + host | Feedback names misconceptions without praise inflation. No paid student tier. The `ail_how_agreement` part teaches students about sycophancy. |

**Never claim "DfE compliant".** For the safety slide, cut this to six rows: 10 (partly), 11 manipulation (meets), 4 safeguarding (gap, closing), 5 security (gap, closing), 3 filtering (host), 7 no training (meets).

**Other guidance:**
- **DfE generative AI guidance** (updated 12 Aug 2025): schools must follow AI tools' age limits; pupils' work must not train models without permission (w1-09-05 ✓).
- **Filtering and monitoring standards** (updated 16 Sep 2026): schools must cover generative AI in their at-least-annual review. Give each pilot school a one-paragraph note: what eduX sees, stores and returns (w1-09-06 ✓).
- **JCQ and Ofqual AI rules** cover coursework and NEA. 9EC0 is exam-only by secondary sources, so they barely touch eduX (w1-09-07 ✓; check the spec).

## The DPO's objections, checked against the code

| # | Objection | What the code shows | Fix |
|---|---|---|---|
| 1 | No lawful chatbot route for under-18s, so no processor chain for a DPIA | claude.ai consumer is 18+ (w1-05-02 ✓); Gemini custom apps excluded on school accounts (w1-05-09 ✓); Copilot Studio is the one documented per-user route, untested (w1-05-11 ✓) | Fix 2 (wording now); Copilot Studio test and data processing agreement later. Name the school as controller and eduX as processor, hosted in the UK or EEA, no pooling across schools. |
| 2 | Key works like a password, sits in a URL, stored in plaintext; no revoke; ids are name slugs | Key from `?key=` (`server.py:55–57`, `:85–92`); `secrets.token_urlsafe(16)` stored raw (`learner.py:91–94`); lookup `WHERE key = ?` (`learner.py:104–105`); no revoke/rotate anywhere in `edux/`; id is a slug of `display_name` plus 4 hex chars (`learner.py:90–91`), written to `call_log` (`service.py:467`). The access log is off (`server.py:206`), which helps. | Fixes 3, 4, 7; OAuth later |
| 3 | Every message reaches eduX word for word; no safeguarding route | `message` is "the student's message, word for word" (`tools-and-context.md:38`; `text/tools/tutor_turn.md:2`). The server uses it to find the course part (`service.py:245`). `STORE_PROMPTS` defaults to 0 (`learner.py:283`), so text isn't stored, but it is processed. | Fixes 8 and 10; host monitoring named as the primary route; alert later |
| 4 | No retention period, no erasure, no subject-access export | Logs are append-only and treated as the source of truth. The only deletes are for demo students (`edux/demo.py:270–281`) and for derived rows before a rebuild (`learner.py:897–907`). No `delete-student` or `export-student` command exists. | Fixes 5 and 6 |
| 5 | Profiling of minors, widened by one instruction | `text/style.md:1–3`: the style block is sent to the chatbot with the first `tutor_turn` of each session, and line 3 says "use what you already know about the student". Also in `docs/build/steps/05b-one-call-per-turn.md:111`. AI-literacy levels in a teacher view would be non-core profiling. | Fix 1; teacher view off by default, with no AI-literacy levels (see `05-product-features.md`) |

## Later (not before Thursday; for the business plan and Q&A)
- Fixes 12–15 above.
- **Message minimisation:** have the chatbot send topic terms instead of the full message, so eduX never receives disclosures. This trades off matching quality; test it first.
- **A daily-minutes setting** that returns only `offer_stop` once a school limit is passed. Still advisory, because the host can answer without eduX (w1-09-03 ✓).
- **Answers to the DPO's open questions:** which UK school tenants allow 16–17-year-olds and custom MCP, under what DPA; whether a key in a URL meets DfE and NCSC guidance; what KCSIE 2026 expects of a component that processes but doesn't store a disclosure.
- **Q&A answers** the DPO wants to hear: "A pupil's URL leaks?" Revoke with one command; keys hashed; OAuth on the roadmap. "A student types a disclosure mid-revision?" Teaching stops, the DSL route is signposted, the host's monitoring flags it, eduX keeps a count. "What can a teacher see about one child?" Progress levels with evidence counts only; no chats; nothing else by default.

## Considered and rejected
- **Storing chat text to support safeguarding alerts:** conflicts with data minimisation and the Children's code. Keep detection in the host; eduX keeps a count.
- **Hard time limits enforced by eduX:** impossible, because the chatbot can answer without calling eduX. Advisory only, and say so.
- **Claiming "DfE compliant":** untrue; gaps remain, and DfE asks products not to overstate.
- **Forcing an MCQ before every "just show me":** novices gain from worked examples (personalisation review rows 2-01, 2-16); a guided example is lighter friction.
- **Inferring emotion or distress into the learner model:** excluded by the personalisation §5 checklist. The signpost is a one-turn response, not a profile.
- **Per-learner usage and offloading reports on by default:** DfE asks for them, but they are non-core profiling of minors. Off by default; the school decides in its DPIA.
- **Gemini for Education as the safe school route (a scout proposal in w1-08):** its school accounts can't add custom MCP (w1-05-09 ✓).

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| No lawful under-18 route / processor chain | DPO #1 | **Partly**: wording fixed; route untested |
| Plaintext key in URL, no revoke, name-slug ids | DPO #2 | **Partly**: fixes 3, 4, 7 (all S) answer storage, revocation and ids; the key stays in the URL until OAuth (fix 15) |
| Verbatim messages, no safeguarding route | DPO #3 | **Partly**: signpost and DSL field (S); alert route open |
| No retention, erasure or export | DPO #4 | **Answered** by fixes 5 and 6 (S); not yet made |
| "Use what you already know about the student" | DPO #5 | **Answered** by fix 1 (S); not yet made |
| Feels like being watched | Student #4 | **Partly**: reports off by default; "only you see this" wording |
| Quiz instead of answer | Student #1 | **Partly**: a tension with DfE std 10; fix 9 is the compromise |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-09-01 | DfE std: no final answers by default, progressive disclosure, attempt first, friction before answer modes, track and report offloading | official document | learner-facing GenAI products, England | policy | ✓ |
| w1-09-02 | DfE std: DSL contact at setup, alert on disclosures, high-risk alerts in agreed time, tiered distress response to human help, per-learner duration | official document | England | policy | ✓ (offloading tracking sits under Cognitive development) |
| w1-09-03 | DfE std: default and hard time limits, no anthropomorphism, no engagement-prolonging changes | official document | England | policy | ✓ |
| w1-09-04 | claude.ai consumer 18+ and trains on inputs unless opted out; Workspace for Education admins can enable the Gemini app for under-18s with restrictions | official document | UK users | policy | ✓ (no custom MCP on school accounts: w1-05-09 ✓) |
| w1-09-05 | DfE GenAI guidance: follow age limits; free tools may train on inputs; pupils' work not used for training without permission | official document | England schools | policy | ✓ |
| w1-09-06 | Filtering and monitoring standards: SLT scopes GenAI use; annual review covers GenAI products | official document | England schools and colleges | policy | ✓ |
| w1-09-07 | JCQ/Ofqual AI rules cover coursework/NEA; 9EC0 exam-only (secondary source) | official document | England / UK centres | policy | ✓ (structure not checked) |
| w1-09-08 | 05e cites a withdrawn Khanmigo claim; trial found small gains | RCT | US middle schools, maths | learning | ~ abstract only; 0.06–0.08 SD per year; author Nina Low |

Also cited here; each sits in its home report's table: w1-05-02 ✓ ([05](05-product-features.md)), w1-05-07 ✓ ([05](05-product-features.md)), w1-05-09 ✓ ([05](05-product-features.md)), w1-05-11 ✓ ([05](05-product-features.md)).
