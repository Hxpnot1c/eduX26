# 05 · Product features: which chatbots can reach eduX, and what users asked for

Wave 1 (overnight 17–18 Nov 2026). Sources: scout notes `work/w1/w1-05.md`, verifier marks `verify-A.json` (w1-05-*), and the panel's teacher, student and DPO objections. All vendor pages were read on 17 Nov 2026. Where an OpenAI page returned 403, the claim rests on a search snippet and is marked "snippet". Each w1-05 finding was checked by one blind verifier (A); no second mark exists for these ids.

## Summary
- **No vendor page gives a confirmed route for a UK 16–17-year-old to use eduX today.** claude.ai consumer plans are 18+ (w1-05-02 ✓). Anthropic's commercial terms say nothing about age (w1-05-03 ✓). Claude for Teachers is US-only and "not for students" (w1-05-04 ✓).
- **Tested client: claude.ai, on an adult's account.** The `?key=` URL works in the team's testing, but Anthropic doesn't document it as an auth method (w1-05-01 ✓).
- **Gemini is not possible for UK students.** Custom apps (MCP) need a user who is 18+, in the US, on a personal account. Work and school accounts are excluded (w1-05-09 ✓). Don't claim eduX runs inside Gemini on school accounts.
- **Microsoft Copilot Studio is the best-documented school route, but untested.** It is the only vendor that documents an API key sent as a query parameter and supplied by each user (w1-05-11 ✓). Copilot Chat for learners aged 13–17 is off by default in school tenants until an IT admin turns it on (w1-05-13 ~). Billing for agents with MCP tools is unconfirmed.
- **ChatGPT is untested, and the README route is out of date.** Custom MCP is added from Plugins → Add custom MCP server (w1-05-05 ✓). Full MCP appears to need Business, Enterprise or Edu; Pro is read/fetch only (w1-05-06 ~, snippet only). Teens are allowed with parental permission (w1-05-08 ~, snippet), but whether teen accounts can add MCP is unknown.
- **ChatGPT asks the user to confirm every eduX call,** because no eduX tool has `readOnlyHint` (w1-05-05 ✓). Marking `get_my_progress` read-only is a quick fix.
- **OAuth is what unlocks school deployment.** Gemini Enterprise, Microsoft federated connectors and ChatGPT accept only OAuth or no auth, not custom API keys (w1-05-07 ✓, w1-05-10 ✓, w1-05-12 ✓). The DPO also wants it, because a key in a URL works like a password (see [09](09-safety-ethics.md)).
- **The panel's feature asks:** a teacher view of class weak points, exam-style work beyond MCQs (numeric and essay planning), and a "just show me" that doesn't feel like a quiz. None is built. They are proposals for the roadmap; only wording and mock-ups fit before Thursday.

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | Use the "works with" line above on the pitch's architecture slide. No Gemini or Copilot logos. | pitch | S | yes | w1-05-01 ✓, w1-05-02 ✓, w1-05-09 ✓, w1-05-11 ✓ |
| 2 | Caption the video: "Filmed on a team member's adult claude.ai account. Students would use their school's chatbot." Never show or imply a 16–17-year-old on consumer claude.ai. | video | S | yes | w1-05-02 ✓ |
| 3 | Prepare the Q&A answer to "Which 16-year-old can use this Monday?": adults and teachers today; Copilot Studio in a Microsoft school tenant next (untested); OAuth after. | pitch Q&A | S | yes | w1-05-03 ✓, w1-05-11 ✓, w1-05-13 ~ |
| 4 | Build team: add `readOnlyHint: true` to `get_my_progress` in `edux/server.py`. Leave `tutor_turn` and `update_my_profile` as writes, because they record events. | build | S | yes | w1-05-05 ✓ |
| 5 | Build team: fix the README's ChatGPT section. Route: Plugins → "+" → Add custom MCP server, Authentication = No authentication. Expect a confirmation on write tools. Remove "needs a paid plan" unless re-tested on that plan. | build docs | S | yes | w1-05-05 ✓, w1-05-06 ~ |
| 6 | Show a teacher-view mock-up (class level, groups of at least 5, no chats, AI-literacy levels off by default) on a roadmap slide. Say "not built". | pitch | S | yes | panel (teacher #4, DPO #5) |
| 7 | Prepare the honest essay answer: "Essay levels aren't built; numeric, chain and essay-plan tasks are next, all scored by rules." | pitch Q&A | S | yes | panel (teacher #1, student #5) |
| 8 | Put OAuth on the roadmap slide as the unlock for school tenants and admin-installed connectors. | pitch | S | yes (slide) | w1-05-07 ✓, w1-05-10 ✓, w1-05-12 ✓ |
| 9 | Hash keys and add revoke/rotate (details in [09](09-safety-ethics.md) recs 3–4). Do it after the video is filmed, or make `seed --reset` keep the stored hash, so demo connector URLs keep working. | build | S | yes, after filming | panel (DPO #2) |
| 10 | Keep `text/format/gemini.md`, but don't advertise Gemini. | pitch | S | yes | w1-05-09 ✓ |

## Chatbot compatibility table (with verifier corrections)

Status: **tested** = run end to end by the team; **untested** = documented route exists, not run; **not possible** = vendor docs rule it out for eduX's users or design. "Min age (UK)" is the vendor's minimum for that product in the UK.

| Client | Remote MCP support | Plans | Admin needed? | Auth eduX can use | Min age (UK) | Status |
|---|---|---|---|---|---|---|
| claude.ai Free / Pro / Max (and Ultra) | Yes, "custom connectors" (w1-05-01 ✓) | Free (1 custom connector only), Pro, Max; the page now also lists Ultra (verifier note) | No: the user adds it | OAuth, "No sign in" or fixed headers are documented. `?key=` in the URL is **not documented** but works in team testing | **18** (w1-05-02 ✓); accounts with under-18 signals are disabled, with Yoti age checks | **Tested** (adult team member's account only) |
| claude.ai Team / Enterprise | Yes (w1-05-01 ✓) | Team, Enterprise | **Yes**: an Owner or Primary Owner adds it; on Enterprise, a custom role with the right permission can too (verifier note) | As above, plus admin-set headers | **Unconfirmed**: commercial terms set no age and are "not for consumer use"; minors guidance covers API products only (w1-05-03 ✓) | Untested; under-18 use unconfirmed |
| Claude for Education | Connectors listed as admin feature (w1-05-04 ✓) | University plan | Yes | Unconfirmed for custom connectors | Unconfirmed; framed for universities | Untested |
| Claude for Teachers | Partner connectors only | Verified **US** K-12 staff | District admin | n/a | "Not for students" (w1-05-04 ✓) | **Not possible** for students |
| ChatGPT Free / Go / Plus | **Unconfirmed**; the help-page snippet names only Pro, Business and Enterprise/Edu (w1-05-06 ~) | Plus not named | No (user adds it from Plugins) | OAuth 2.1 or no auth. ChatGPT "cannot present custom API keys", so `?key=` works only as a no-auth secret URL (w1-05-07 ✓) | 13, with parent/guardian permission under 18; teens go to ChatGPT for Teens (w1-05-08 ~, snippet) | Untested; teen MCP access unknown |
| ChatGPT Pro | Read/fetch only (w1-05-06 ~, snippet) | Pro | No | As above | As above | Untested; unannotated tools count as writes, so `tutor_turn` may be blocked |
| ChatGPT Business / Enterprise / Edu | "Full MCP" (w1-05-06 ~, snippet) | Business, Enterprise, Edu | **Yes**: on Business only admins/owners create and publish | As above. ChatGPT now also presents an OpenAI-managed client certificate that servers can verify (verifier note on w1-05-07 ✓) | Edu for UK under-18 pupils: no page found | Untested |
| Gemini app (consumer) | Yes, "custom apps" (w1-05-09 ✓) | Not stated | No | OAuth (DCR or manual credentials); no-auth and query keys not mentioned | **18, and US only**, personal account | **Not possible** in the UK |
| Gemini for Education / Workspace for Education | **No**: custom apps not available on work or school accounts (w1-05-09 ✓) | n/a | n/a | n/a | Admin can enable the Gemini app for under-18s with restricted features (w1-09-04 ✓), but without custom MCP | **Not possible** |
| Gemini Enterprise (Business edition) | Yes, Pre-GA; off by default (w1-05-10 ✓) | Business edition | Yes, team admin | OAuth 2.0 or no auth; no API key | Not a school product | Untested; needs OAuth |
| Microsoft 365 Copilot federated connector | Yes (w1-05-12 ✓) | Needs an M365 Copilot licence per user | Yes: Global or AI Administrator | Entra SSO, OAuth 2.0 or no auth; one base URL, so no per-student key | Unconfirmed | **Not possible** with per-student keys; possible after OAuth |
| Microsoft Copilot Studio agent (in Teams / Copilot Chat) | Yes, Streamable HTTP; SSE dropped after Aug 2025 (w1-05-11 ✓) | Copilot Studio, billed in Copilot Credits (snippet) | Yes: an agent maker builds it; IT enables Copilot Chat for learners | None, **API key as header or query parameter supplied by the agent's user**, or OAuth 2.0 (w1-05-11 ✓) | 13; off by default in K-12 tenants; admin sets age groups (w1-05-13 ~: source is MS Learn "Enable Copilot Chat for learners", 3 Sep 2026, not the blog) | **Untested**; student billing unconfirmed |
| Microsoft Copilot (consumer) | No documented route | n/a | n/a | n/a | 13+ (snippet) | Not possible (no route found) |
| Oak Aila; NotebookLM / Gemini Notebook; Khanmigo | No MCP client support found (absence, unconfirmed) | — | — | — | — | Not possible (no client) |
| Oak MCP (for comparison) | Oak runs an MCP **server**, shipped to teachers as a Claude connector **and** a ChatGPT plugin (w1-05-14 ~: verifier found the ChatGPT version) | — | IT may need to enable it | OAuth | Teachers; warns not to enter pupil data | Precedent, not a client |

### "Works with" line for the pitch (truthful)
> **Built on the open Model Context Protocol (MCP). Tested with claude.ai. ChatGPT and Microsoft Copilot Studio document MCP support; we haven't tested them yet.**
>
> Footnote: *Demo filmed on a team member's adult claude.ai account. claude.ai consumer plans are 18+. For under-18s, eduX needs a school-managed chatbot; we are adding OAuth.*

No Gemini or Copilot logos, and no "school-ready", "works with any chatbot" or "runs inside Gemini" claim (w1-05-09 ✓). If asked "Who can use this on Monday?": adults (including Year 13s who have turned 18) and teachers on their own accounts today; Microsoft school tenants via Copilot Studio next, the one documented per-user key route (untested); OAuth after that.

## Product features the panel asked for

| Ask | Who asked | Status today | Proposal (our choice) | Before Thursday? |
|---|---|---|---|---|
| **Teacher view**: one screen of class weak parts and misconceptions, groups of at least 5, no chats | Teacher #4; DPO #5 (no AI-literacy levels by default) | Not built. Teacher usage reports are off by default (personalisation §5) | Show a **mock-up** in the pitch: class-level weak parts and top misconceptions, minimum group size 5, no message text, no per-student AI-literacy or "Decide" stats unless the school switches them on. Build later. | Mock-up yes; build no |
| **Who sees my stats?** | Student #4 | `get_my_progress` shows the student's own stats; nothing goes to teachers | One line in `get_my_progress` and the pitch: "Only you see this unless your school switches on a class report, and you'd be told." Wording for the build team. | Yes (wording) |
| **Exam practice beyond MCQs**: numeric questions marked per step; one "chain" task (order the links, find the missing one) | Teacher #1 | Every check is a four-option MCQ; level-marked answers wait for step 07 (not built) | Numeric and chain tasks are scored by rules, so they fit the no-model-calls design. Roadmap slide only. | No (slide yes) |
| **Essay practice**: "plan me a 25-marker" tied to the exam-question links | Student #5; Teacher Q&A #1 | Not built; step 07 not built | A planning scaffold (knowledge, analysis chain, evaluation points, diagram) that eduX checks point by point, with no level or mark. Answer in Q&A: "Essay levels aren't built; here is the plan." eduX must never give a numeric mark for level-marked work (server rule 7). | No (honest answer yes) |
| **Answer first when rushed** | Student #1 | "Just show me" gives the point and still ends with a check | **Tension:** DfE std 10 asks for no full answers by default and friction before answer modes (w1-09-01 ✓). Proposal: when rushed, show a guided example with the last step left to the student, and make the follow-up check skippable. See `09-safety-ethics.md`. | Build team decides Wed |
| **Gaming the MCQs** (short correct option; "I checked the ONS" makes Verify secure) | Teacher #2; Student #3 | Open; fixes proposed in [02](02-ai-literacy-assessment.md) recs 3–6 and [04](04-economics-education.md) rec 1 | Match option form and length; "I checked" needs a detail; an ignored task gives no evidence, not 0. Covered by other area reports. | See [02](02-ai-literacy-assessment.md) and [04](04-economics-education.md) |
| **Set a class focus** ("externalities, due Friday") | Teacher #5 | eduX picks the next part itself | A class focus topic and deadline the planner prefers. Later. | No |
| **Key handling**: hash keys, revoke and rotate, pseudonymous ids, OAuth date | DPO #2 | Keys stored in plaintext (`edux/learner.py:91–94`), looked up in plaintext (`learner.py:104–105`), read from `?key=` (`edux/server.py:55–57`). Ids are made from the student's name (`learner.py:90–91`) | See `09-safety-ethics.md` fixes 3, 4 and 7. OAuth on the roadmap slide. | Hashing and revoke: yes, after filming (S each) |
| **AI literacy in homework, not only research questions** | Student #2 | 05e (built on its branch, not merged) gives literacy tasks on research questions | Add a Verify moment in homework ("which line of that answer would you check against your notes?"). Listed under Later in [02](02-ai-literacy-assessment.md). | No |

## Later (not before Thursday; for the business plan and Q&A)
- **OAuth 2.1 with PKCE.** It is what ChatGPT, Gemini Enterprise and Microsoft federated connectors accept for anything beyond no-auth (w1-05-07 ✓, w1-05-10 ✓, w1-05-12 ✓). Effort L.
- **End-to-end test on Copilot Studio** in a Microsoft education tenant with Copilot Chat for learners enabled. Find out the Copilot Credit cost per `tutor_turn` (w1-05-11 ✓, w1-05-13 ~).
- **Teacher view** (class level, off by default, switched on by the school). **Class focus topic and deadline.**
- **Numeric questions marked per step, chain tasks, essay-plan scaffold.** Step 07 (level-marked answers) after that.
- **Ask Anthropic** whether school-held Team or Enterprise plans may include under-18 members. This needs a human contact, not an agent (w1-05-03 ✓).
- **Test ChatGPT Plus and a teen account** with an adult on Plus first (w1-05-06 ~, w1-05-08 ~).

## Considered and rejected
- **Film ChatGPT as the main client.** Plan support is unclear, every write tool asks for confirmation, and the docs moved recently (w1-05-05 ✓, w1-05-06 ~).
- **"Works with Gemini" because `text/format/gemini.md` exists.** Custom apps are US-only, 18+ and personal-account-only (w1-05-09 ✓).
- **A scout line (w1-08 rec 2) placing eduX inside Gemini on school accounts.** False: school accounts can't add custom apps (w1-05-09 ✓).
- **Claim Claude for Education covers UK schools.** It is framed for universities; the K-12 offer is US teachers only (w1-05-04 ✓).
- **Treat Oak as a client.** Oak runs a server, not a client (w1-05-14 ~).
- **A pure answer-first mode with no check.** It conflicts with DfE std 10 (w1-09-01 ✓). A guided example with a skippable check is the compromise.
- **AI-literacy levels in the default teacher view.** That is non-core profiling of minors; the DPO wants it off by default (panel DPO #5).

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| No lawful chatbot route for under-18s | DPO #1; investor #1; student Q4 | **Partly answered**: truthful wording, Copilot Studio named as the documented route. Access itself is not solved: no tested under-18 route exists. |
| "Runs inside Gemini" is false | Investor #1 | **Answered**: line removed everywhere (w1-05-09 ✓). |
| I can't see anything (teacher view) | Teacher #4 | **Partly**: mock-up now, build later. |
| Recognition, not exam skills | Teacher #1; student #5 | **Partly** for teacher #1 (see [04](04-economics-education.md) recs 6, 8); **open** for student #5: roadmap only, essay features not built. |
| Quiz instead of answer | Student #1 | **Partly**: compromise proposed, constrained by DfE std 10. |
| Feels like being watched | Student #4 | **Partly**: "only you see this" wording; teacher view off by default. |
| Key in URL, plaintext | DPO #2 | **Partly**: hash and revoke proposed (S); OAuth later. |
| Lesson fit / class focus | Teacher #5 | **Partly**: class focus is later; route and friction answers in recs 3 and 9 above. |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-05-01 | claude.ai custom connectors on Free (1 only), Pro, Max, Team, Enterprise (also Ultra); Team needs Owner; auth OAuth / no sign-in / headers | official document | all claude.ai users | policy | ✓ |
| w1-05-02 | claude.ai consumer users must be 18+; accounts with minor signals disabled; Yoti verification | official document | consumer users; excludes 16–17 | policy | ✓ |
| w1-05-03 | Commercial terms set no age, "not for consumer use"; minors guidance covers API products only | official document | organisations | policy | ✓ |
| w1-05-04 | Claude for Teachers: verified US K-12 educators only, not for students; Education guide is for universities | official document | US K-12 staff; universities | policy | ✓ |
| w1-05-05 | ChatGPT adds custom MCP via Plugins; OAuth or no auth; tools without `readOnlyHint` need confirmation | official document | ChatGPT users | policy | ✓ |
| w1-05-06 | Full MCP only on Business/Enterprise/Edu; Pro read/fetch only; Business admins publish | official document (snippet) | ChatGPT subscribers | policy | ~ snippet only (403); article slug now 12584461-connecting-custom-mcp-servers-in-chatgpt |
| w1-05-07 | ChatGPT can't present custom API keys; OAuth 2.1 + PKCE or no auth | official document | n/a | policy | ✓ (now also an OpenAI-managed client certificate) |
| w1-05-08 | OpenAI Europe terms: 13+, parental permission under 18; under-18s placed in ChatGPT for Teens | official document (snippet) | 13–17, UK/EEA | policy | ~ snippet only (403) |
| w1-05-09 | Gemini custom apps: 18+, US, personal accounts, English, History on | official document | US adults | policy | ✓ |
| w1-05-10 | Gemini Enterprise Business: custom MCP, Pre-GA, StreamableHTTP, OAuth or no auth, off by default | official document | business tenants | policy | ✓ |
| w1-05-11 | Copilot Studio: remote MCP over Streamable; auth none, API key (header or query, user-supplied) or OAuth | official document | M365 / Power Platform tenants | policy | ✓ |
| w1-05-12 | M365 Copilot federated connectors: Global/AI admin; Entra SSO, OAuth or no auth; Copilot licence per user | official document | M365 tenants | policy | ✓ |
| w1-05-13 | Copilot Chat for learners 13+, off by default in K-12, admin-enabled; shared-data agents pay-as-you-go | official document | students 13+ in M365 Education tenants | policy | ~ "off by default" rests on MS Learn "Enable Copilot Chat for learners" (3 Sep 2026), not the cited blog |
| w1-05-14 | Oak ships its MCP server to teachers as a Claude connector; warns against pupil data; Aila has no MCP | official / practitioner | UK teachers | adoption / policy | ~ Oak also ships a ChatGPT plugin (same day) |

Also cited here; each sits in its home report's table: w1-09-01 ✓ ([09](09-safety-ethics.md)), w1-09-04 ✓ ([09](09-safety-ethics.md)).
