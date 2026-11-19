# 05 · Product features: which chatbots can reach eduX, how students sign in, the teacher view, and accessibility

Waves 1, 2 and 3 (overnight 17–18 Nov 2026). Sources:
- Wave 1: `work/w1/w1-05.md`, marks in `verify-A.json`.
- Wave 2: `work/w2/w2-05.md` (routes and authentication, w2-05-01 to -14, marks in `verify-E.json`); `work/w2/w2-05t.md` (teacher view, w2-05-20 to -34, marks in `verify-G.json`); simulation `sims/teacher/results.md`; panels `panel-teacher-student.md` and `panel-investor-dpo.md`.
- Wave 3: `work/w3/w3-05.md` (accessibility, SEND, EAL, low bandwidth and equity, w3-05-01 to -17), marks in `verify-L.json`. The verifier re-audited the MCQ options and the readability figures and corrected both (applied below).
- Wave 4 (compatibility notes only): `work/w4/w4-08.md`, marks in `verify-R.json`. Whether pupils can reach a custom agent in Copilot, and Microsoft's new Study and Learn-only switch. These findings live in the [business plan](business-plan.md) and are cited here by id. The MCQ give-away fix is now a tested patch (0004 in [wednesday-build-list.md](wednesday-build-list.md)).

Vendor pages were read on 17–18 Nov 2026. OpenAI help pages returned 403, so those claims rest on search snippets and are marked "snippet". Each finding has one blind verifier mark.

**Coordinator facts used here.** 05e (AI-literacy coaching) is built on its branch, not merged. Per-student *completion* may be a school opt-in, default off. Per-student levels, AI-literacy scores, offloading and draft counts are never shown. Class-level AI literacy appears only in bands, for groups of 6 or more, and only on opt-in.

## Summary
- **No route for a UK 16–17-year-old has been tested.** The only tested client is claude.ai, used on an adult's account. Consumer claude.ai is 18+ (w1-05-02 ✓).
- **The one documented school route is Microsoft 365 Education plus a Copilot Studio agent. It is untested.**
  - Copilot Chat is off by default for learners aged 13–17. An admin turns it on by setting the tenant to K-12 and each student's age group to NotAdult (w2-05-04 ✓).
  - Copilot Studio agents can call a remote MCP server. The key can be sent as a header or a query parameter, or the agent can use OAuth 2.0 (w2-05-03 ✓).
  - **Whether a school's custom agent reaches 13–17s is implied, not stated.** Microsoft's K-12 pages name only Copilot Chat, Study and Learn and Notebooks for learners (w4-08-02 ✓).
  - **A new admin switch can close the route per school.** Microsoft is rolling out an opt-in "Study and Learn-only mode", mid-November to mid-December 2026. It limits students to Microsoft's tutor: with it on, they can't select other agents, and the agent store is among the surfaces affected (MC1548047, read on a third-party mirror; w4-08-01 ~).
    - **Our inference:** with the switch off, students can reach some other agents. The post doesn't say whether that includes org-published MCP agents.
  - Each student turn costs the school Copilot Credits: 5 credits per MCP tool call at US$0.01 (£0.0075) per credit. That is about £22.50 per student per year in the central case, range £11–108 (our estimate on assumed turn counts; w3-08m-06 ✓, -07 ✓, -13 ✓). It replaces the wave-2 US$84 estimate (w2-05-06 ~). See the [business plan](business-plan.md).
- **No other client gives a school route for pupils.**
  - Mistral Le Chat is a personal-account route only. Its terms allow 13+ with parental permission (w2-05-01 ~), and the account owner can add a custom MCP server (w2-05-02 ✓). But it is a consumer contract with no school data processing agreement (DPA), so **a school can't deploy it or put it in a DPIA.** Keep it off every pupil-facing slide.
  - ChatGPT, Claude and Gemini give no under-18 route. ChatGPT for Teachers is for US staff only, and whether teen accounts can add MCP isn't documented (w2-05-14 ~, snippet). Gemini school accounts take only named partner integrations.
- **Authentication: none of the fixes is built.** `edux/server.py` still reads only `?key=` (lines 55–57, 86–89). The plan:
  - **S:** accept the key in an `Authorization: Bearer` header.
  - **M:** sign in through the school's Microsoft Entra, with eduX checking tokens (Copilot Studio only).
  - **L:** a full OAuth broker that works with every client.

  A key in the URL conflicts with IETF guidance (w2-05-10 ✓), NCSC guidance (w2-05-11 ✓) and the MCP spec's ban on tokens in the query string (w2-05-05 ✓). DfE's standards don't address it (w2-05-12 ✓).
- **Teacher view: hand teachers an action, not a watch list.** Dashboards alone have no shown effect on attainment (w2-05-23 ~). ASSISTments' teacher reports came bundled with hints and training, and the report part wasn't isolated (w2-05-20 ~, w2-05-21 ~).
  - The proposed screen is one page: misconceptions to reteach, each with a starter MCQ, plus the weakest parts.
  - Rules: k = 6, shares in bands, one 14-day window, no names (all our choice).
  - It is not built. Show it as a static mock.
  - **The flag rule can't see moderate problems in small classes.** For a set of 12, a misconception held by half the class is flagged 27–56% of the time. One held by 35% is flagged only 7–18% of the time (simulation: synthetic students, `sims/teacher/results.md` §6).
    - Pooling across sets *may* lift the "half the class" case to about 0.8–0.9, and doesn't help the 35% case unless the threshold is lowered (our calculation, below). **Not reproduced in repo:** the pooling script was run in scratchpad only and not saved, so treat these figures as unchecked.
    - Say plainly: "It catches big shared misconceptions, not moderate ones."
- **The panel's other feature asks are still unbuilt:** numeric, chain and essay-plan tasks, a class focus, and per-student completion. Only wording and mock-ups fit before Thursday.
- **Two accessibility bugs in code, both S fixes (wave 3).**
  - **The MCQ gives its answer away by form.** When a part has no mark points, `plan._points` (`edux/plan.py:376`) uses the node's *description* as the point, so the description becomes the correct option. That happens in 7 of the example pack's 9 parts. The description is a topic label, not an answer ("Calculating PED from percentage changes…"). The correct option is also longer than every distractor in 7 of 9 parts (w3-05-08 ~, verifier's count). **Fix:** never use the node description as an option; keep the mark point as the key (commit `f0a1c36` on `main` made the point, not the exemplar, the right option on purpose), matched to its distractors in length and punctuation; skip the MCQ when a part has no points; warn at ingest. **Wave 4 built and tested this as patch 0004 (code plus drafted pack rows):** a testwise student who knows nothing falls from 0.96 to 0.28 against chance 0.31 (simulation; w4-fix-mcq-1 ✓). The pack rows still need an economist's read ([wednesday-build-list.md](wednesday-build-list.md) step 4). This doesn't contradict [04](04-economics-education.md): where the key is a point, it is a short fragment with no full stop (04's captures); where a part has no points, the description fallback makes it the longest option (w3-05). Both give the answer away.
  - **"Shorter replies" doesn't reach the teaching step.** The profile's `answer_length` changes `style.max_words`, but `teach_point` still sends `max_words = 80` (`edux/plan.py:403`). So the chatbot gets two conflicting caps.
- **Accessibility: universal, student-chosen supports beat SEND labels, and uptake is the equity risk (wave 3).**
  - Need is common. 14.8% of pupils in England's schools have SEN support and 6.0% an EHC plan (w3-05-01 ✓). 16.6–25.5% of GCSE/AS/A level candidates have 25% extra time (w3-05-03 ✓).
  - eduX already has no timers, one point per message and formulas in words, which suits read-aloud. Read-aloud helps students with reading disabilities (d = 0.35; w3-05-05 ✓). Glossaries are the only English-learner accommodation with a significant (small) effect (w3-05-09 ~).
  - Evidence on who gains is mixed, and nobody measured **uptake**, the likelier way a gap widens (w3-05-14 ~, -15 ~).
  - **No 16–18 SEN or EAL rate is published** in the sources read, so we can't size the sixth-form need (w3-05-01 ✓, -02 ✓).

## Ranked recommendations

**Rec numbers in wave 3.** Ranks 1–10 keep their numbers (other reports cite them). Wave 3 adds ranks 11–21. The old 11 (Entra sign-in) is now 22 and the old 12 (teacher view as code) is now 23. Ranks 1–19 can be done before Thursday 23:59; 20 is "maybe"; 21–23 come later.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on findings |
|---|---|---|---|---|---|
| 1 | **"Works with" line** (below): tested with claude.ai on an adult account; Microsoft 365 Education via Copilot Studio is the documented school route, untested. No Le Chat, Gemini or Copilot logos. | pitch, video | S | yes | w1-05-02 ✓, w2-05-03 ✓, w2-05-04 ✓, w2-05-01 ~ |
| 2 | **Video caption:** "Filmed on a team member's adult claude.ai account. Pupils would use their school's Microsoft Copilot." Never show a 16–17-year-old on a consumer chatbot. | video | S | yes | w1-05-02 ✓, w2-05-04 ✓ |
| 3 | **Deployment slide, 4 icons:** K-12 tenant → NotAdult age group → Copilot Studio agent with the eduX tool → publish to the Year 12–13 group. Label it "documented route, pilot next", not "works today". | pitch | S | yes | w2-05-03 ✓, w2-05-04 ✓, w2-05-13 ✓ |
| 4 | **Static teacher-view mock** (spec below), with a corner tag "illustrative class data", about 8 s in the video after the student's wrong answer. Voice-over: "Teachers see what to reteach, never who said what." | video, pitch | S | yes | w2-05-23 ~, w2-05-26 ~, w2-05-29 ✓ |
| 5 | **Build: accept `Authorization: Bearer <key>`** next to `?key=` in `_key_from_scope` and `require_student` (`edux/server.py`). The README should tell users of claude.ai, Copilot Studio and Le Chat to put the key in a header. Keep `?key=` only for ChatGPT, which can't send custom keys. Do it after filming, or keep both so demo URLs still work. | build | S | yes, after filming | w2-05-02 ✓, w2-05-03 ✓, w2-05-08 ✓, w2-05-09 ~, w2-05-10 ✓ |
| 6 | **"What your teacher sees" line** in the student's progress text: "Your teacher sees class patterns from groups of 6 or more. Never your chats, your levels, your AI-literacy scores, or how often you asked AI to write for you. If your school turns it on, they also see whether you did checks this week." Build team edits `text/`. | build | S | yes | coordinator decision; w2-05-34 ✓; student panel #3 |
| 7 | **Q&A answer, "Is a key in a URL secure?"** "No. It's a stop-gap. It conflicts with NCSC and IETF guidance. We're moving it to a header, then to school sign-in through Entra. DfE's standards ask for unique credentials, which ours are." Never say "DfE-compliant" or "non-compliant". | pitch Q&A | S | yes | w2-05-10 ✓, w2-05-11 ✓, w2-05-12 ✓ |
| 8 | **Q&A answer, "Is the teacher view blind in my set of 12?"** "Partly, yes. It catches a misconception held by about half the class, not one held by a third. Pooling across your sets should help the big ones (our calculation, not reproduced in repo). For the rest, it says 'nothing flagged', not 'all clear'." | pitch Q&A | S | yes | w2-05-29 ✓, w2-05-30 ✓; pooling: our calculation, not reproduced in repo |
| 9 | **Adult test of Le Chat Free** with a bearer header. Note whether each write tool asks for confirmation. If it works, the slide may say "also tested on Le Chat (adult account)". Never present it as a pupil route. | build/test | S | yes | w2-05-01 ~, w2-05-02 ✓ |
| 10 | Build: `readOnlyHint: true` on `get_my_progress`, and fix the README's ChatGPT route (carried from wave 1). | build | S | yes | w1-05-05 ✓ |
| 11 | **Correct MCQ option in plain claim form (wave 3).**<br>• **Never use the node `description` as an option.** It is the fallback in `_points` (`edux/plan.py:376` on `main`) and it is a topic label, not an answer.<br>• **Keep the mark point as the key, not the exemplar.** Commit `f0a1c36` on `main` made the point the right option on purpose. Match it to its distractors in length and punctuation (a full sentence with a full stop, within 0.7–1.3× the median distractor length; our choice, as in [04](04-economics-education.md) rec 1).<br>• At ingest, warn "check has no answerable correct option" for a part with misconceptions but no mark point. Until it has one, the planner skips the MCQ check for that part and uses explain-back.<br>• Also warn when the correct option is over 1.5× its part's median distractor length (our choice).<br>• **Before filming,** add mark points for the demo parts.<br>• A wave-4 scout is testing this fix (in progress). | build, course pack | S | yes | w3-05-08 ~ |
| 12 | **Make "shorter replies" reach the teaching step.** For `teach_point` (`edux/plan.py:403`), set `max_words = min(settings.points.max_words, profile answer_length)`, passing the profile in as `style()` does. Then add to `text/tools/update_my_profile.md`: "answer_length: e.g. 50 if they want shorter replies". | build, `text/` | S | yes | w3-05-04 ~; w3-05-12 ~ (weak) |
| 13 | **Option count and guess rate move together.** Three options are as good as four or five in item statistics (Rodriguez 2005; w3-05-07 ~). Most example-pack checks already show 3 options: when a part has one misconception, the chatbot writes a third (`min_distractors = 2`). Set `mcq.max_options = 3` (our choice). Then set the `mcq_check` guess to match the options shown, about .33 rather than .25. Better, build guess = 1/n options (`mcq_guess_from_options`, [06](06-settings-simulation.md) Later), because an always-"A" guesser already hits 32–34% on 3-option checks (w1-06-10 ~). A chatbot-written third option is a further form cue; the rec 11 length warning can't see it. **Caveat:** most checks fall inside the 30-minute "immediate" window and are scored with the immediate guess (.30), so the `mcq_check` guess matters little until that window shrinks (w1-06-07 ✓). Changing it also shifts the economics posteriors simulated in [06](06-settings-simulation.md), so rerun those sims after any change. | settings | S | yes | w3-05-07 ~; w1-06-10 ~ |
| 14 | **No timers, stated and guarded.** eduX never times a check or uses response speed as evidence. Call-log timings are diagnostics only. So a student with 25% extra time in exams is not penalised. Add a design note, and a test that latency never enters the learner model. Pitch/Q&A line: "no time pressure, for everyone". | pitch, docs, build (test) | S | yes | w3-05-03 ✓, -04 ~ |
| 15 | **Read-aloud friendly.** `text/format/default.md` already writes formulas in words, which suits device read-aloud. Offer `format=plain` as a student choice, not only per client. Video line: "works with your device's read-aloud". Don't claim eduX is a reading support. | build, video | S | yes (video line) | w3-05-05 ✓ |
| 16 | **Readability check on student-facing pack text, and shorter move sentences.**<br>• At ingest, warn on any sentence over 25 words (ASD-STE100's limit for descriptive text) in `notes.summary`, `misconceptions.correction`, `nodes.intuition` and mark-point `exemplar`. Report pooled FK grade per topic. Warn only, because FK is unstable on short texts.<br>• Split the long sentences in `text/moves/*.md`. These are chatbot-facing, so the gain is in instruction-following, not student reading (plausible, untested). | build (ingest), `text/moves/` | S | yes | w3-05-13 ~, -16 ~ |
| 17 | **Accessibility statement for schools (one page).** Cover which WCAG 2.2 criteria eduX controls and which the chatbot vendor controls, the universal options (shorter replies, untimed checks, read-aloud-friendly format, plain words if built), and how they help the school's own Equality Act duties (Schedule 10 accessibility plan; the anticipatory duty in FE, Schedule 13). Never imply eduX makes a school compliant. | business plan, pitch Q&A | S | yes | w3-05-17 ✓ |
| 18 | **Equity: name uptake as the gap, and let the school check it.** Pitch/Q&A: "The evidence on who gains from tutoring software is mixed. The likelier gap is who uses it, so the school can compare usage by its own FSM and SEND flags." Per-student usage minutes and checks answered are already in the school export. eduX never holds those flags. | pitch, business plan | S | yes | w3-05-14 ~, -15 ~ |
| 19 | **Low-bandwidth line.** Add one sentence to `text/format/chatgpt.md` and `claude.md`: "If the student says the connection is slow, describe diagrams in words." A result is about 600 tokens; what costs time is the extra round trip per turn and drawn charts (first principles, not measured). | `text/format/` | S | yes | first principles (w3-05 §Low bandwidth) |
| 20 | **Student-chosen "plain words" option, never a SEND label.** Add `plain_words` (bool) to `update_my_profile`, sent in `style`. Add to `text/style.md`: "If style.plain_words: sentences under 15 words, everyday words, each course term explained the first time." It is student-supplied, never inferred, never shown to teachers and never exported. It needs a profile column (migration). | build, `text/` | M | maybe | w3-05-09 ~, -10 ~, -13 ~ |
| 21 | **Glossary view.** `get_my_progress` lists the course terms met so far, each with a one-line plain definition. This is the evidence-backed English-learner support (a glossary), on demand, for everyone. | build | M | no | w3-05-09 ~, -10 ~ |
| 22 | **Entra sign-in for pilots (option B below).** eduX acts as a resource server using the installed `mcp` SDK's `TokenVerifier` and `AuthSettings`. It checks the Entra token's audience, and the student id is a hash of `tid`+`oid`. | build | M | no | w2-05-05 ✓, w2-05-07 ✓ |
| 23 | **Teacher view as code:** a `[teacher_view]` settings block, an `offered_misconception_ids` log, and one server-side aggregation. Off unless the school turns it on. | build | M | no | w2-05-28 ✓ to w2-05-34 ✓ |

## Chatbot compatibility table

Status meanings:
- **tested**: run end to end by the team.
- **documented, untested**: a vendor route exists that we haven't run.
- **personal only**: allowed for a minor, but on the minor's own consumer account, outside any school contract.
- **not possible**: vendor docs rule it out.

| Client / setting | Custom remote MCP? | Who adds it | Auth eduX can use | Under-18 in UK? | School can deploy and put in a DPIA? | Status |
|---|---|---|---|---|---|---|
| **M365 Copilot Chat (K-12 tenant) + Copilot Studio agent** | Yes, Streamable HTTP only (w2-05-03 ✓) | A staff agent maker; IT turns on Copilot Chat for learners | None; an API key in a **header or query**, supplied by each user; or OAuth 2.0 (dynamic discovery, dynamic or manual) (w2-05-03 ✓) | 13–17 once an admin sets the tenant to K-12 and the age group to NotAdult; off by default; under-13s blocked; A1/A3/A5 student licence (w2-05-04 ✓). No Microsoft page says outright that a custom agent reaches NotAdult learners (w4-08-02 ✓). **An opt-in admin switch (Study and Learn-only mode) blocks all other agents for students** (w4-08-01 ~, read on a third-party mirror). Teen safety protections switch on automatically from mid-Oct 2026, and the notice doesn't say whether they cover custom MCP agents (w2-05-13 ✓, read on a third-party mirror) | **Yes, on paper.** The school is controller under its M365 terms, and eduX would be a processor under its own DPA. Power Platform data policies govern MCP access (w2-05-03 ✓) | **Documented, untested.** Billed in Copilot Credits per turn (w2-05-06 ~) |
| M365 Copilot (paid licence) + MCP plugin / declarative agent | Yes (w1-05-12 ✓) | Global or AI admin | OAuth only. DCR needs a client secret, and DCR isn't available on Entra-protected servers (w2-05-07 ✓) | Unclear for students | Possibly; about US$18 per user per month (academic), which is more than metered credits at our volume | Untested |
| **Mistral Le Chat Free / Pro / Student** | Yes; on these plans the account owner is the admin (w2-05-02 ✓) | The user | None, a bearer or basic header, or OAuth 2.1 with DCR (w2-05-02 ✓) | 13+ with parental permission. The help page says permission is required; the consumer terms say "where required". UK not named (w2-05-01 ~: the terms are for consumers "outside the EEA") | **No.** Consumer terms, personal capacity only, no DPA. The school is not the controller | **Personal only**; untested. Adults may test it |
| Mistral Le Chat Team / Enterprise | Docs don't say who administers connectors | — | As above | Commercial terms allow minors only with "legally adequate consent" (w2-05-02 ✓) | Unclear; needs a sales or legal answer | Untested |
| claude.ai Free / Pro / Max | Yes (w1-05-01 ✓) | The user | OAuth (Claude's published identity is "Recommended", or DCR, or your own client ID); fixed request headers; "No sign in" (w2-05-09 ~). `?key=` works in team testing but isn't documented | **No, 18+** (w1-05-02 ✓) | n/a | **Tested** (adult account only) |
| claude.ai Team / Enterprise / Education | Yes, admin-added (w1-05-01 ✓) | Owner | As above | No page grants an exception; Education is framed for universities (w1-05-03 ✓, w1-05-04 ✓) | Unclear; ask Anthropic | Untested |
| Claude for Teachers | Partner connectors only | US district | n/a | Educators only, "consistent with" 18+ (w2-08-04 ✓) | n/a | **Not possible** for students |
| Claude API in a partner's chat app | The API's MCP connector can call remote servers | The partner | Partner's choice | Anthropic lets organisations serve minors through API products with safeguards (w1-05-03 ✓) | Possibly, through the partner | Someone else must build the app. eduX itself never calls a model |
| ChatGPT personal / Teens | Custom MCP plan support unclear (w1-05-06 ~, snippet). Teens: not documented | The user | OAuth (CIMD preferred, DCR or predefined; PKCE S256 required) or no auth. It **can't send custom API keys** (w2-05-08 ✓), so `?key=` works only as a no-auth secret URL | 13–17 placed in ChatGPT for Teens since 18 Aug 2026 (w2-05-14 ~, snippet) | No | Untested |
| ChatGPT Edu / for Teachers | Edu: admins enable (snippet) | Admin | As above | Edu appears to be for universities. For Teachers: US K-12 staff, "not offered to students" (w2-05-14 ~, snippet) | No page found for UK schools | Not a school route |
| Gemini app / Gemini for Education | Consumer custom apps are US, 18+, personal accounts only (w1-05-09 ✓). School accounts: Sept 2026 added only named partner MCP integrations, admin-controlled (Workspace Updates blog, 15 Sep 2026; not a numbered finding) | — | — | Gemini can be enabled for under-18s, but without custom MCP | n/a | **Not possible** |
| Gemini Enterprise (Business) | Yes, Pre-GA (w1-05-10 ✓) | Admin | OAuth or no auth | Not a school product | n/a | Untested |
| Oak MCP (for comparison) | Oak runs a **server**, shipped to teachers as a Claude connector and a ChatGPT plugin (w1-05-14 ~) | — | OAuth | Teachers | — | Precedent, not a client |

### "Works with" line for the pitch
> **Built on the open Model Context Protocol (MCP). Tested with claude.ai. For pupils, the documented route is the school's own Microsoft 365 Education tenant through Copilot Studio; we haven't tested it yet.**
>
> If asked whether pupils can reach it: *"Microsoft's own posts imply students can choose other agents unless the school locks them to Study and Learn. No Microsoft page says outright that a school's custom agent works for 13–17s, and we haven't tested it."* (w4-08-01 ~, w4-08-02 ✓). Say "imply"; never "Microsoft confirms".
>
> Footnote: *Demo filmed on a team member's adult claude.ai account. claude.ai consumer plans are 18+.*

If asked "Who can use this on Monday?": "Adults, including Year 13s who have turned 18, and teachers, on their own accounts. Sixth-formers next, through a Microsoft school tenant, once we've piloted it."

If asked about Le Chat: "Its terms let a 13-year-old with a parent's permission add a server. But that's a personal consumer account outside any school contract, so we don't offer it to pupils."

**Don't say:** "works with any chatbot", "school-ready", "runs inside Gemini", or anything that names Le Chat as a route for pupils.

## Deployment story (Microsoft school; from Microsoft docs, untested by us)

1. **Licences.** Students hold A1, A3 or A5 student licences (w2-05-04 ✓).
2. **Tenant type.** The Global Admin sets the Microsoft Education Tenant Identifier to K-12.
3. **Year 12–13 only.** Set their age group to NotAdult, with the consent value. Under-13s stay blocked. Microsoft's teen protections apply automatically (w2-05-13 ✓). **Leave Study and Learn-only mode off for this group**: with it on, students can't use any other agent (w4-08-01 ~).
4. **Data policy.** Allow the eduX connector in the Power Platform data policies (w2-05-03 ✓).
5. **Agent.** A staff maker builds "eduX Economics" in Copilot Studio and adds eduX under Tools → Model Context Protocol. Auth: the API key in a header now, or OAuth Manual against the school's Entra app later. Paste in eduX's chatbot instructions. **Pick a non-reasoning model**: a reasoning model adds 10 credits per 1,000 tokens (w2-05-06 ~).
6. **Cost cap.** Allocate credits to the environment or link pay-as-you-go, and set a monthly limit for the agent. Prepaid tenants are blocked at 125% of capacity (w2-05-06 ~).
7. **Publish.** Release the agent to the Year 12–13 Economics security group in Teams and Copilot Chat.
   - An agent the organisation publishes needs an admin's approval in the Agent Registry before users can reach it (w4-08-06 ✓).
   - Don't apply Block Agents to it, and allow it for the Year 12–13 group (w4-08-04 ✓).
8. **Paperwork.**
   - A DPIA and a record of processing (DfE standards; w2-05-12 ✓).
   - A DPA naming eduX as processor.
   - A diagram of the processor chain (DPO wave 2 #2): pupil → Microsoft (the school's M365 terms) → eduX (eduX DPA).
   - The "what your teacher sees" line (rec 6).

**Open:** whether an MCP tool call bills as one agent action (5 credits); whether Microsoft's teen protections reach custom MCP agents; whether an Agent Builder agent avoids generative-answer charges; whether a NotAdult learner can use an org-published MCP agent when Study and Learn-only mode is off; and what the "Applies to employee-facing agents only" footnote on Microsoft's education add-ons page means for student agents (w4-08-05 ✓; the page is partly stale, so it is a question, not a ban). These questions need Microsoft's answer or a real tenant test. Two Microsoft pages conflict: the en-GB marketing page says Copilot Chat is for "higher education students aged 13 and older", while MS Learn covers K-12 learners aged 13–17. We rely on MS Learn (w2-05-04 ✓).

## Authentication plan (none built)

| Option | What it is | Works with | Effort | Status |
|---|---|---|---|---|
| **A. Header key** | Accept `Authorization: Bearer <key>`. Keep `?key=` only for ChatGPT. Hash keys and add revoke/rotate ([09](09-safety-ethics.md) recs 6–7) | claude.ai, Copilot Studio, Le Chat (w2-05-02 ✓, -03 ✓, -09 ~) | **S** (1–2 h in `edux/server.py`) | Recommended, not built |
| **B. School Entra sign-in** | The school registers an Entra app. Copilot Studio uses Manual OAuth with that client. eduX validates Entra JWTs (issuer = school tenant, audience = eduX), publishes Protected Resource Metadata, and returns 401 with `WWW-Authenticate`. Student id = hash of `tid`+`oid` | Copilot Studio only. Entra has no DCR, no CIMD and no `code_challenge_methods_supported`, so spec-strict clients may refuse it (w2-05-07 ✓) | **M** (half to one day: the `mcp` SDK's `TokenVerifier` + `AuthSettings`, `pyjwt`, tests). Untested against Entra v2 audience handling | Recommended for the first pilot, not built |
| **C. OAuth broker** | A managed or self-hosted authorization server with CIMD, DCR (now deprecated in the MCP spec), PKCE S256 metadata, federated to the school's Entra or Google | All clients (w2-05-05 ✓, w2-05-08 ✓) | **L** (2–4 days, plus vendor DPA and DPIA updates) | Later, when a non-Microsoft school asks |

eduX's own duties under the MCP spec (w2-05-05 ✓) apply to B and C:
- Accept tokens only from the header, never from the query string.
- Check each token's audience.
- Never pass a token on.

Don't build eduX's own authorization server. It is L effort with high security risk.

## Teacher view

### Evidence: what helps teachers act
- **Dashboards alone:** a 38-study review found no evidence of better achievement. Effects on participation were larger, but participation is engagement, not learning (w2-05-23 ~, abstract only). Teacher-facing dashboards are mostly prototypes evaluated by self-report (w2-05-24 ~, higher education).
- **ASSISTments (Maine RCT), a bundle:** online homework with hints, teacher reports and teacher training. US grade 7 maths, 2,850 students.
  - g = 0.18 overall and 0.29 for low-prior students (w2-05-20 ~). The g values and the TerraNova test name come from secondary summaries (Blueprints, Evidence for ESSA). The abstract is primary.
  - 45 schools were randomised and 43 analysed; one school withdrew before assignment.
  - A follow-up found g = 0.22 and no significant mediation through teachers' targeted homework review (w2-05-21 ~, secondary).
- **ASSISTments (North Carolina replication):** ES ≈ +0.10 on the grade 8 state maths test, a year after the programme ended (w2-05-22 ~, secondary).
  - About 6,000 students were analysed; 9,073 is the enrolment.
  - WWC reports a non-significant result on a second grade 8 test.

  **So we can't say "teacher dashboards raise grades".** We can say: "Online homework with teacher reports raised maths scores in a US trial."
- **Lumilo:** real-time analytics glasses for teachers improved learning in 18 US middle-school classes (w2-05-25 ~, abstract). Press coverage (a different Hechinger article from the one first cited) reports that more than half the gain came from teachers wearing glasses with the analytics off. Being watched is an active ingredient. eduX's view is asynchronous and shouldn't claim this effect.
- **How teachers use dashboards:** they read them through what they already know and respond with feedback and extra instruction (w2-05-26 ~; unverified, the papers couldn't be opened). Dashboard-prompted feedback was more balanced than human-prompted feedback (teacher-initiated or in reply to students), most of all for low-ability students (w2-05-27 ~, abstract only). **So put the action, a starter MCQ, next to the signal.**

### Coordinator decision on per-student data

| Data | Shown to the teacher? |
|---|---|
| Per-student **completion** ("did checks this week: yes / no") | **School opt-in, default off**, like Sparx. Needs a privacy-notice line and the school's lawful basis in its DPIA |
| Per-student levels, `p_known`, AI-literacy scores, offloading, draft counts | **Never** (coordinator decision) |
| Chats, minutes, fatigue, confidence | Never (w2-05t spec and personalisation §5) |
| Class-level misconceptions and weak parts | Yes, with k = 6, banded, one window, when the school turns the view on |
| Class-level AI literacy | Only in bands, groups of 6 or more, opt-in |

This settles the clash between w2-09 rec 4 and w2-05t: draft and offloading counts are **not** in the teacher view. The teacher panel's ask for completion is met as an opt-in. Their wish to see levels per student is not.

### Flag rule (our choice) and what it can't detect

**Rule (our choice):** flag a misconception when **at least 6 distinct students AND at least 40%** of students offered that distractor picked it on their first attempt, over a **14-day window**, recomputed once a week (w2-05-29 ✓).
- Background pick rate 15%: false alarms 0.1–1.0% per evaluation, or 0.1–1.2 expected false flags a term across 10 misconceptions.
- Very attractive distractors (25% background): false alarms 1.4–10.7% per evaluation, about 2–13 a term (w2-05-30 ✓).
- Clustering within a class raises false alarms (w2-05-30 ✓). CUSUM was worse and is rejected.

Simulation: synthetic students, parameters our choice.

**Small classes (teacher panel #4).** The teacher quoted 5% and 33% detection for a set of 12. Those are the 1-week figures. The recommended 2-week rule does better, but it is still weak:

| Set | Share doing checks each week | Detect 50% prevalence | Detect 35% prevalence |
|---|---|---|---|
| 12 | 50% | 0.27 | 0.07 |
| 12 | 80% | 0.56 | 0.18 |
| 14 | 50% | 0.44 | 0.13 |
| 14 | 80% | 0.74 | 0.32 |

Rows for 12 from `sims/teacher/results.md` §6. Rows for 14 are our calculation with the same model.

**Pooling (our calculation; simulation: synthetic students). Not reproduced in repo.** The script behind this table was not saved to `sims/teacher/`, and `sims/teacher/results.md` has no pooling section. No verifier has rerun it. Don't quote these figures in the pitch until someone saves and reruns the script.
- Model: the same exact binomial as `sims/teacher/misconception_alarm.py`, with pooled class size n and an effective attempt share 1 − (1 − a)^w over w weeks. Students are independent, with no clustering. The script was run in scratchpad only and not saved to the repo.
- Results for sets of 12:

| Pooled | Rule | FA per evaluation, 15% background | FA, 25% background | Detect 50% | Detect 35% |
|---|---|---|---|---|---|
| 1 set, 4-week window | k=6, 40% | 0.003–0.005 | 0.04–0.05 | 0.53–0.61 | 0.17–0.21 |
| 2 sets (24), 2 weeks | k=6, 40% | 0.002–0.006 | 0.05–0.09 | 0.81–0.83 | 0.30–0.34 |
| 3 sets (36), 2 weeks | k=6, 40% | ≤ 0.001 | 0.03–0.05 | 0.86–0.89 | 0.28–0.30 |
| 4 sets (48), 2 weeks | k=6, 40% | ≤ 0.001 | 0.01–0.03 | 0.89–0.92 | 0.25–0.27 |
| 2–4 sets, 2 weeks | k=6, **30%** | 0.004–0.039 | 0.21–0.29 | 0.93–1.00 | 0.61–0.75 |

Ranges span 50% and 80% of students doing checks each week.

**What this means, plainly (if the unreproduced figures hold):**
- **Pooling 2–4 sets catches a misconception held by half the students** about 8–9 times in 10.
- **With a 40% threshold, pooling never catches one held by 35%.** As the pool grows, the observed share settles near 35%, below the threshold, so detection *falls*.
- **Dropping the threshold to 30% when pooled** catches the 35% case 6–7 times in 10. The cost is false alarms of 0.4–4% per evaluation at a 15% background (about 0.5–5 a term across 10 misconceptions). For attractive distractors it is 21–29%, which is useless without the per-misconception `alarm_share` override (w2-05t rec 7).
- **A longer window (4 weeks) helps a little** and makes flags slower and staler.

**Proposal (our choice, not built):**
- Offer **department pooling** as a school opt-in. It needs a written school instruction, since pooling within a school is a `w_cross` decision and pooling across schools is ruled out (personalisation §5). With it: x = 30% and k = 6, plus a per-misconception `alarm_share`. Shown to the head of department as "across your Year 12 sets".
- Caveats on pooling:
  - It mixes sets with different teachers, so one set's problem is diluted.
  - Clustering will raise false alarms above these figures (w2-05-30 ✓).
  - The flag no longer says which set has the problem.
- For a single small set with no pooling, the screen should say **"nothing flagged" and never "no problems"**. The pitch should say: "It catches big shared misconceptions, not moderate ones."

### Spec and mock: one screen (all rules our choice)

```
+--------------------------------------------------------------------------------+
| eduX · Class 12E Economics · last 14 days · 17 students linked                  |
| You see class patterns only: no chats, no levels, no AI-literacy scores.        |
| Names appear only in section 3, if your school has switched it on.             |
+--------------------------------------------------------------------------------+
| 1. MISCONCEPTIONS TO TACKLE (flagged: >= 6 students and >= 40% of those asked)  |
|  ! "A tax removes the externality completely"     Externalities: taxes         |
|    about half of those asked picked this · 6-9 students (low evidence)         |
|    [ Starter MCQ: preview / print ]   [ Mark as addressed ]                    |
|  ! "Price elasticity = slope of the demand curve" PED                          |
|    most of those asked picked this · 10-14 students                            |
|    [ Starter MCQ: preview / print ]   [ Mark as addressed ]                    |
|  Nothing flagged does not mean no problems: with this many students, only      |
|  misconceptions held by about half the class are reliably caught.              |
|  [ Pool with your other Year 12 sets: needs school setting ]                   |
+--------------------------------------------------------------------------------+
| 2. WEAKEST PARTS (share of students who worked on it and are not yet secure)  |
|   Part                          Not yet secure    Students    Last evidence     |
|   Negative externalities: tax   most              10-14       2 days ago        |
|   PED and total revenue         about half        15+         this week         |
|   Monetary policy transmission  about half        6-9 (low evidence) 5 days ago |
|   Market failure types          too few students (<6) worked on it            |
+--------------------------------------------------------------------------------+
| 3. COMPLETION THIS WEEK (only if your school has switched this on)             |
|   Did checks: 11 students · Didn't: 6 students   [ list names ]                 |
+--------------------------------------------------------------------------------+
| 4. COURSE-PACK ROWS TO REVIEW: 4 rows flagged by students or checks             |
+--------------------------------------------------------------------------------+
| Never shown: individual levels, chats, time on task, offloading, draft counts, |
| fatigue, confidence, AI-literacy scores. Updated weekly (Sunday).              |
+--------------------------------------------------------------------------------+
```

Rules behind it:
- **One window, weekly.** One 14-day window, recomputed weekly on a fixed day. There is no date picker. Overlapping windows let figures be subtracted from each other.
- **Counts in bands.** Counts appear as bands (6–9, 10–14, 15+). Shares appear as words: "some" is 40–49% (part rows only), "about half" is 50–69%, "most" is 70% and above. "All" is never shown. A count of 5 or fewer is never shown, which matches DfE performance tables (w2-05-31 ✓). DfE publishes no fixed rule and works case by case (w2-05-32 ✓). NHS HES rounds and stars small counts (w2-05-33 ✓).
- **Minimised, not anonymous.** The ICO says k-anonymity fails against background knowledge, and a teacher has plenty (w2-05-34 ✓). So this is minimised personal data, not anonymous data. **Never say "anonymous".**
- **Below-threshold items** are not listed and get no counts. The screen says only that a quiet result isn't an all-clear.
- **Starter MCQ.** It reuses the server-built check for that misconception, the action the evidence points to. "Mark as addressed" resets the window and gives a before/after re-check in pilots.
- **Completion (section 3) appears only on school opt-in.** It shows did / didn't, never scores. Section 4 lists course-pack content rows, not student drafts.
- **"Not yet secure"** means `p_known` is below the mastery threshold among students with evidence in the window. It is not a grade prediction.
- **Pilot measure:** whether the teacher used the starter, and the class's re-check accuracy two weeks later. That is engagement and near-transfer, not attainment (w2-05-23 ~, w2-05-24 ~).

**For the video:** a static rendering with "illustrative class data". The seeded demo has one student, so real numbers would be suppressed anyway.

**Data the view needs (DPO wave 2 #4):** log `offered_misconception_ids` on check rows, so the share has the right denominator.
- Retention (our choice): drop the column's values after 28 days, two windows. The rest of the row follows the general retention default in [09](09-safety-ethics.md).
- Necessity: without it, the denominator overcounts and the rule under-flags.
- Not built.

## Other product features the panels asked for

| Ask | Who | Status | Proposal (our choice) | Before Thursday? |
|---|---|---|---|---|
| Per-student completion | Teacher wave 2 #4 | Not built | School opt-in, default off (coordinator) | Mock only |
| Pooling across sets | Teacher wave 2 #4 | Not built | Department opt-in, x = 30% (above; figures not reproduced in repo) | No; Q&A wording yes |
| "Does my teacher see I asked it to write my essay?" | Student wave 2 #3 | Draft counts were proposed for the teacher report (w2-09 rec 4) | **No, never.** Rec 6 wording | Wording yes |
| Exam practice beyond MCQs (numeric, chain, essay plan) | Teacher #1; student #5 (wave 1) | Not built; step 07 not built | Rule-scored numeric and chain tasks; essay-plan scaffold with no mark. See [04](04-economics-education.md) | No (slide yes) |
| Answer first when rushed | Student #1 (wave 1) | "Just show me" skips the attempt | Guided example with the last step left to the student, skippable check ([09](09-safety-ethics.md) rec 14) | Build team decides Wed |
| Class focus ("externalities, due Friday") | Teacher #5 (wave 1) | Not built | A focus topic and deadline the planner prefers | No |
| A tested school route | Student wave 2 #5; investor wave 2 #2 | None | Copilot Studio test on a real tenant | No |

## Accessibility, SEND, EAL, low bandwidth and equity (wave 3)

### Who needs what (official statistics)
- **SEN, schools in England, 2025/26.** 14.8% of pupils (1,319,780) have SEN support and 6.0% (538,547) an EHC plan. Speech, language and communication is the commonest primary need for SEN support (25.7%); autism is the commonest for EHC plans (33.5%) (w3-05-01 ✓).
- **Post-16 EHC plans.** Of 718,838 EHC plans in January 2026, 100,800 (14.0%) are held in FE and post-16 settings, 79,500 of them in sixth-form and FE colleges (w3-05-01 ✓).
- **EAL.** 21.6% of pupils (19.3% in secondary) have a first language other than English. That is a language-exposure marker, not proficiency (w3-05-02 ✓).
- **Exam access arrangements, 2024/25** (Ofqual, official statistics in development). 16.6–25.5% of GCSE, AS and A level candidates had approved 25% extra time, and 4.8–7.7% a reader or computer reader (w3-05-03 ✓).
- **The 16–18 data gap.** None of these releases gives an SEN-support or EAL rate for 16–18-year-olds. The SEN release says only that the shares keep falling after compulsory school age. FE uses a different, self-declared measure (ILR), which isn't comparable. So we can't size need in sixth forms. Say "schools in England", never "16–18s", for these figures. Pulling the age-by-phase tables is open.
- **What follows.** Slow reading and a need for extra time are common, not rare. Speech-and-language needs and autism point to literal, consistent, short wording.

### What eduX already does (code reading)
- **No timers.** No response-latency signal enters the learner model; call-log timings are diagnostics only.
- **Short, one-point teaching.** One point per message, under a word cap.
- **Terms explained.** A known-terms block, plus instructions rule 9: explain unlisted terms in plain words.
- **Read-aloud-friendly text.** `text/format/default.md` writes formulas in words.

These are universal-design choices, not SEND features. Frame them as "high-quality teaching for all", in line with the EEF's SEND guidance (w3-05-06 ~; that guidance's strategy list was read from secondary summaries only).

### Two gaps in code
1. **The MCQ correct option differs in form from its distractors** (w3-05-08 ~; the verifier re-audited the pack with the `plan.py` logic).
   - `plan._points` (`edux/plan.py:376`) falls back to the node `description` when a part has no mark points. The example pack has mark points for only 2 of its 9 parts with misconceptions. So in **7 of 9 parts** the correct option is the description, a topic label such as "Calculating PED from percentage changes in quantity demanded and price."
   - In the other 2 it is mark-scheme wording ("States that…").
   - Correct options run 10–18 words and distractors 6–15. **The correct option is longer than every distractor of its part in 7 of 9 parts.** Only `ped_formula` and `pes_formula` are exceptions (verifier's count; the scout said 6).
   - Item-writing guidance asks for options homogeneous in form and similar in length (Haladyna, Downing & Rodriguez 2002). A test-wise student can pick the answer without the economics. That inflates mastery and adds reading for weak readers.
   - **Fix (rec 11):** never the description; keep the point as the key with matched length and punctuation; an ingest warning; skip the MCQ for parts with no mark point. A wave-4 scout is testing it.
   - **Consistent with wave 1, for a different option source.** [04](04-economics-education.md) counted the opposite cue in its demo captures: the correct option was a short point fragment with no full stop (6 of 6 sets). Both are true: a point used as the key is too short and unpunctuated; the description fallback is too long. Both give the answer away, and the fix above covers both.
2. **`answer_length` doesn't reach `teach_point`** (`edux/plan.py:403`; we confirmed it in code: `service.py:202` uses `answer_length` for `style.max_words`, while `plan.py:403` passes `settings.points.max_words`). The profile option overrides `style.max_words`, but `teach_point`'s `data.max_words` is fixed at `points.max_words = 80`. A student who asks for 50 words sends the chatbot two caps, and the code doesn't show which one the model obeys (rec 12).

### What the evidence supports (all outside the UK and outside 16–18 unless stated)

| support | evidence | population | outcome | use in eduX |
|---|---|---|---|---|
| Read-aloud / text-to-speech | d = 0.35 [0.14, 0.56], 23 group-design studies; within-subject 0.15 vs between-subject 0.61 (w3-05-05 ✓) | grade 3 to postsecondary, reading disabilities, mostly US | learning (comprehension while supported) | rec 15 |
| Three options, not four | Little or no change in difficulty, discrimination or reliability (Rodriguez 2005; w3-05-07 ~, abstract only; we don't quote a study count) | mostly school-age test takers, US | prediction (item quality) | rec 13, with the guess change |
| Glossaries for English learners | Of 7 accommodations, only dictionaries or glossaries had a significant, small effect; none threatened validity (w3-05-09 ~, abstract only) | US K–12 English learners | learning (test performance) | recs 20–21 |
| Explicit academic vocabulary | 20-week RCT, 14 schools, N = 2,082; larger effects for non-English home language and weak vocabulary (w3-05-10 ~) | US grade 6; a review found no UK studies for 14–18 | learning | name and define each term the first time (fits rule 9) |
| No time pressure | Accommodations raised scores more for students with disabilities (0.30) than for peers (0.17); timing 0.47 (w3-05-04 ~; a dissertation) | US, mixed ages | test scores under accommodation | rec 14 |
| "Dyslexia fonts" | Dyslexie font gave no benefit vs Arial; extra letter spacing and short lines helped subsets (w3-05-11 ~) | Dutch, Italian, French children; US high-school students (short lines) | reading speed and accuracy | make no font claims; eduX doesn't control rendering |
| Segmenting | small-to-medium gains on retention and transfer (w3-05-12 ~; snippet only, and the prior-knowledge moderator is unconfirmed) | mostly adults, multimedia | learning | consistent with one point per message; don't sell as a SEND or ADHD feature |

### Readability (heuristic Flesch–Kincaid; w3-05-13 ~)
- **Student-facing text.** Pooled note summaries come out at FK grade 8.4 (reading ease 60, about 14 words per sentence). That is inside WCAG 2.2's "lower secondary" band (7–9 years of school). The verifier reproduced this.
- **Chatbot-facing move texts (`text/moves/*.md`).**
  - On the verifier's rerun, they pool at **FK grade 10.4 with 25.2 words per sentence**, and **5 of the 11 files** average over 25 words per sentence (`answer_brief.md` exactly 25.0).
  - The scout got 8.8, 23.6 and 4 files. The figures depend on how the markdown is stripped before counting, so use the stricter ones.
  - Students never see these texts. Shorter sentences there are for instruction clarity, not student readability.
- **The 25-word threshold** is the sentence limit for descriptive text in aviation's Simplified Technical English (ASD-STE100), written for non-native readers (w3-05-16 ~, via a secondary summary; an analogy, with no comprehension data).
- **FK is crude.** It is unstable below about 100 words, and our syllable counter can differ from standard tools by about a grade. Never publish a "reading age" as a quality badge.

### Equity: uptake is the gap to watch
- **Who gains is mixed.** An intelligent-tutoring meta-analysis found at most small effects on K–12 maths (g = 0.01–0.09) and smaller effects for low achievers (w3-05-14 ~). The ASSISTments RCT (43 Maine schools, 2,850 grade 7 students) found the biggest gains for low prior attainers (g = 0.18 overall, from a secondary summary). But every student there had a school laptop (w3-05-15 ~).
- **Neither study measured uptake**, meaning who actually uses the tool. With bring-your-own-device and voluntary use, that is the likelier way a gap widens.
- **eduX should neither claim to narrow gaps nor profile students.** The school can compare usage by its own flags (rec 18).

### Low bandwidth and offline (first principles, not measured)
- `results.max_chars = 2400` is about 600 tokens, or 2.4 KB per turn. A 30-turn session moves well under 0.2 MB of eduX text.
- What costs time is elsewhere:
  - the extra model → MCP → model round trip per turn (one call per turn is already the right design);
  - drawn diagrams (Python charts in ChatGPT, inline SVG in Claude);
  - the chatbot app itself, which eduX can't change.
- eduX can't work offline, because the chatbot needs the network. Missed days are absorbed by the review queue, not lost.

## Later (not before Thursday; for the business plan and Q&A)
- **Copilot Studio end to end** in a Microsoft education tenant, with a 17-year-old test account under the school's control. Questions to answer:
  - Does an MCP call bill as one agent action?
  - Do teen protections cover the agent?
  - Does Agent Builder avoid the generative-answer charge?
- **Options B, then C** of the authentication plan.
- **Teacher view build:** `[teacher_view]` settings (`min_students = 6`, `min_share = 0.40`, `pooled_min_share = 0.30`, `window_days = 14`, `first_attempt_only = true`, weekly recompute; all our choice). Also the `alarm_share` override per misconception, the `offered_misconception_ids` migration, and opt-in completion.
- **Calibrate the background pick rate** from the first pilot's check data. We assumed 15% (25% as a stress case).
- **Check the ONS SRS "below 10" threshold** (snippet only, w2-05-32 ✓ note). If confirmed, k = 10 would leave most sets of 12–16 seeing nothing, so pooling would be the only option.
- **Ask** Mistral (Team or Enterprise for UK schools), Microsoft (billing unit) and Anthropic (under-18 members on school plans). These need a human, not an agent.
- **Numeric, chain and essay-plan tasks**; class focus.
- **Accessibility follow-ups (wave 3).**
  - Pull 16–18 SEN and EAL rates from the age-by-phase tables, and FE's self-declared measure (ILR), labelled as not comparable.
  - Read the EEF SEND guidance PDF at source.
  - Test whether Claude, ChatGPT and Copilot render maths so that NVDA and VoiceOver read it correctly.
  - UK data poverty for 16–18s, and the share who study mainly on phones.
  - Find an English uptake-gap study of an edtech tool by disadvantage.
  - Build the glossary view (rec 21) and plain words (rec 20) if they miss Thursday.

## Considered and rejected
- **Le Chat as a pupil route** (w2-05 rec 2 put it on the slide). It is a personal consumer account with no DPA, so a school can't deploy it or name it in a DPIA (DPO wave 2 #1). Adults may test it.
- **Per-student levels or AI-literacy scores in the teacher view.** That is non-core profiling of minors, it is what the student panel fears, and there is no evidence that per-student displays raise attainment (w2-05-23 ~). Ruled out by the coordinator.
- **Draft or offloading counts in the teacher report** (w2-09 rec 4). They would teach students to hide AI use, which wipes out Verify evidence (student wave 2 #3). Ruled out by the coordinator.
- **CUSUM across weeks.** In the simulation, 66–91% of terms gave at least one false signal across 10 misconceptions (w2-05-30 ✓).
- **k = 5.** It detects more in sets of 12, but it shows counts of exactly 5, which DfE suppresses (w2-05-31 ✓). A school's DPIA could choose it.
- **Exact percentages or "n of m".** They make differencing easy (w2-05-34 ✓).
- **Pooling across schools.** Ruled out by personalisation §5.
- **Entra as the authorization server for all clients.** It lacks DCR, CIMD and S256 metadata (w2-05-07 ✓).
- **Building our own authorization server this week.** L effort, high security risk.
- **The M365 Copilot licence route for students.** About US$216 per student per year (US$18 a month), which is more than our metered estimate.
- **ChatGPT Edu as the school route.** Nothing we read offers it to UK secondary schools.
- **Claiming "DfE-compliant" or "non-compliant" for the key.** DfE doesn't address it (w2-05-12 ✓).
- **A SEND or EAL flag that changes teaching (wave 3).** It breaks the privacy checklist ("no SEND, EAL or demographic data in eduX") and labels minors. Universal options the student chooses get most of the benefit without profiling.
- **Inferring reading difficulty from message length or spelling.** That is profiling by proxy, and native language and disability are under-studied in algorithmic bias.
- **A dyslexia font or coloured background.** No benefit in the font test (w3-05-11 ~), and eduX doesn't control the chatbot's rendering.
- **Readability caps on `text/moves/*.md` as an accessibility measure.** Students never see those texts. Kept only as a clarity tidy-up (rec 16).
- **Timed quick-fire checks for engagement.** They conflict with the extended-time population (w3-05-03 ✓).
- **Runtime simplification of notes by an LLM.** The server never calls a model, and simplified English alone showed no significant effect for English learners (w3-05-09 ~).
- **Fixed option order.** The per-asking shuffle in `plan.ask_mcq` stops students memorising letters on re-asks. All the pack's options are statements, so numeric ordering has no use yet.

## Panel objections this report answers or leaves open

| Objection | Panel | Status |
|---|---|---|
| No lawful under-18 route | DPO w1 #1; investor w2 #2; student w2 #5 | **Partly**: the documented Microsoft route and its steps are written up. **Open**: nothing is tested |
| Le Chat can't go in a DPIA | DPO w2 #1 | **Answered**: Le Chat is now "personal only", off pupil-facing slides |
| Copilot processor chain | DPO w2 #2 | **Partly**: chain stated in deployment step 8; the DPA and the teen-protection check are open |
| Child holds a long-lived secret; `?key=` | DPO w1 #2, w2 #3 | **Recommended**: header (S), hashing and revoke (S), Entra (M). None built |
| Teacher view: lawful basis, retention of the new log | DPO w2 #4 | **Partly**: minimised design, a 28-day retention proposal and the privacy line are written. The lawful basis is the school's to name; not built |
| Teacher screen blind for small sets; completion | Teacher w2 #4 | **Partly**: honest numbers, a pooling proposal (figures not reproduced in repo) and opt-in completion. Moderate misconceptions in one small set stay undetectable |
| Draft counts vs the mock | Teacher w2 #5; student w2 #3 | **Answered** by the coordinator decision: never shown |
| "Runs inside Gemini" | Investor w1 #1 | **Answered**: removed |
| Exam skills beyond MCQs | Teacher w1 #1; student w1 #5 | **Open**: roadmap only |
| Quiz instead of answer | Student w1 #1 | **Partly**: compromise proposed |
| "The correct option gives itself away" | Teacher w1 #2; student w1 #3; judges w1 #5 | **Recommended** (wave 3): rec 11 targets the cause in `plan.py:376`. The wave-1 capture count (04) and the wave-3 audit describe different cues; neither fix is made |
| SEND, EAL and slow readers | (scout-raised, wave 3) | **Recommended**: universal options (recs 12–16, 20–21) and a school accessibility statement (rec 17). No 16–18 data yet |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-05-01 | claude.ai custom connectors on Free (1), Pro, Max, Team, Enterprise; OAuth / no sign-in / headers | official document | claude.ai users | policy | ✓ |
| w1-05-02 | claude.ai consumer users must be 18+ | official document | consumers | policy | ✓ |
| w1-05-03 | Commercial terms set no age; minors guidance covers API products | official document | organisations | policy | ✓ |
| w1-05-04 | Claude for Teachers US K-12 staff only; Education framed for universities | official document | US staff; universities | policy | ✓ |
| w1-05-05 | ChatGPT custom MCP via Plugins; tools without `readOnlyHint` need confirmation | official document | ChatGPT users | policy | ✓ |
| w1-05-06 | Full MCP only on Business/Enterprise/Edu; Pro read/fetch only | official document (snippet) | ChatGPT subscribers | policy | ~ snippet only |
| w1-05-07 | ChatGPT can't present custom API keys; OAuth 2.1 + PKCE or no auth | official document | n/a | policy | ✓ |
| w1-05-08 | OpenAI Europe: 13+, parental permission under 18 | official document (snippet) | 13–17 UK/EEA | policy | ~ snippet only |
| w1-05-09 | Gemini custom apps: 18+, US, personal accounts | official document | US adults | policy | ✓ |
| w1-05-10 | Gemini Enterprise Business: custom MCP Pre-GA, OAuth or no auth | official document | business tenants | policy | ✓ |
| w1-05-11 | Copilot Studio: remote MCP; none, API key or OAuth | official document | M365 tenants | policy | ✓ |
| w1-05-12 | M365 Copilot federated connectors: admin; Entra SSO, OAuth or no auth | official document | M365 tenants | policy | ✓ |
| w1-05-13 | Copilot Chat for learners 13+, off by default in K-12 | official document | 13–17 in M365 Education | policy | ~ superseded by w2-05-04 ✓ |
| w1-05-14 | Oak ships an MCP server to teachers | official / practitioner | UK teachers | adoption | ~ also a ChatGPT plugin |
| w2-05-01 | Mistral: 13+, parental permission; consumer terms "where required", personal capacity | official document | consumers 13+ | policy | ~ terms are for consumers outside the EEA (not "EU"); help page and terms differ |
| w2-05-02 | Le Chat: account owner is admin on Free/Pro/Student; none, bearer/basic or OAuth 2.1 DCR; commercial terms on minors | official document | Le Chat users | policy | ✓ (product now called "Work", with "Chat (legacy)") |
| w2-05-03 | Copilot Studio MCP: Streamable only; none, API key (header or query, user-supplied) or OAuth 2.0 | official document | M365 tenants | policy | ✓ |
| w2-05-04 | K-12: Copilot Chat off by default for 13–17, blocked under 13; K-12 + NotAdult; A1/A3/A5 | official document | 13–17 in M365 Education | policy | ✓ (en-GB marketing page conflicts) |
| w2-05-05 | MCP spec: PRM, audience check, no tokens in query, S256; DCR deprecated (2026-07-28) | official document | n/a | policy | ✓ |
| w2-05-06 | Copilot Credits: 1/2/5/10; reasoning +10 per 1,000 tokens; 125% enforcement; about US$84/student/yr | official document + our estimate | Copilot Studio tenants | cost | ~ US$0.01/credit not on the cited page; per-student cost is our estimate. The US$84 figure is superseded by w3-08m-13 ✓ (about £22.50, range £11–108; business plan) |
| w2-05-07 | Entra: no DCR for MCP; discovery lacks registration endpoint and S256 metadata | official document | Microsoft tenants | policy | ✓ |
| w2-05-08 | ChatGPT OAuth: CIMD, DCR or predefined; S256 required; no custom API keys | official document | ChatGPT developers | policy | ✓ |
| w2-05-09 | claude.ai: sign-in options; OAuth client choices; fixed headers | official document | claude.ai users | policy | ~ published identity is "Recommended", not default |
| w2-05-10 | RFC 6750: query-string bearer tokens SHOULD NOT be used | official document | n/a | policy | ✓ |
| w2-05-11 | NCSC: don't use API keys; prefer signed JWTs, short-lived credentials | official document | UK organisations | policy | ✓ |
| w2-05-12 | DfE cyber standards: unique credentials; MFA for staff, not students; DPIA; URL keys not addressed | official document | England schools | policy | ✓ |
| w2-05-13 | MC1509805: teen protections from mid-Oct 2026 for Copilot apps and agents "where applicable" | official document (mirror) | 13–17 in Microsoft tenants | policy | ✓ (third-party mirror) |
| w2-05-14 | ChatGPT for Teachers US staff only; teens auto-placed since 18 Aug 2026; teen MCP undocumented | official document (snippet) | US staff; 13–17 | policy | ~ snippet only |
| w2-05-20 | ASSISTments Maine RCT: g = 0.18, 0.29 low-prior; 2,850 grade 7 | RCT | US grade 7 | learning | ~ 45 randomised, 43 analysed; g and test name from secondary sources |
| w2-05-21 | Follow-up: g = 0.22; no significant mediation through homework review | RCT (mediation) | US grade 7 | learning | ~ secondary only |
| w2-05-22 | NC replication: ES ≈ +0.10 on grade 8 test | RCT | US grades 7–8 | learning | ~ secondary; about 6,000 analysed (9,073 enrolled); WWC: second test n.s. |
| w2-05-23 | 38-study review: no evidence dashboards improve achievement; participation effects larger | systematic review | mixed | learning / engagement | ~ abstract only |
| w2-05-24 | 50 teacher-facing dashboards: mostly prototypes, self-report evaluation | systematic review | higher education | adoption | ~ abstract only |
| w2-05-25 | Lumilo glasses improved learning; more than half the gain from glasses alone | RCT (small) | US middle school | learning | ~ abstract; "more than half" is from a different Hechinger article |
| w2-05-26 | Teachers consult dashboards 8.3 times a lesson; act through feedback | correlational | Dutch primary | adoption | ~ unverified (papers not opened) |
| w2-05-27 | Dashboard-prompted feedback balanced task/process | correlational | K-12 | teacher behaviour | ~ comparison is human-prompted, not teacher-initiated only; abstract only |
| w2-05-28 | Farrington: no alarm with fewer than 5 reports in 4 weeks | analogy (method) | surveillance data | method | ✓ |
| w2-05-29 | k=6/40%/2-week rule: FA 0.1–1.0%; detects 50% prevalence 27–85% | simulation | synthetic classes 12–25 | prediction | ✓ (rerun matches) |
| w2-05-30 | Weak spots: 25% background, clustering, CUSUM | simulation | synthetic | prediction | ✓ (CUSUM "x10 cells" is an approximation) |
| w2-05-31 | DfE suppresses measures for 5 or fewer pupils | official document | England schools | policy | ✓ |
| w2-05-32 | DfE confidentiality policy: no numeric thresholds, case by case | official document | England | policy | ✓ |
| w2-05-33 | NHS HES: 1–7 starred, rounding to 5 | official document | England hospital data | policy | ✓ |
| w2-05-34 | ICO: no single formula; k-anonymity fails against background knowledge | official document | UK | policy | ✓ |
| w3-05-01 | SEN 14.8% / EHC 6.0% (2025/26); SLCN 25.7%, autism 33.5%; 100,800 EHC plans in FE and post-16 | official document | schools in England; EHC plans 0–25 | policy (prevalence) | ✓ |
| w3-05-02 | EAL 21.6% (19.3% secondary); no post-16 figure | official document | schools in England | policy (prevalence) | ✓ |
| w3-05-03 | 25% extra time for 16.6–25.5% of GCSE/AS/A level candidates; reader 4.8–7.7% | official document (in development) | candidates in England, all ages | policy | ✓ |
| w3-05-04 | Accommodations: ES 0.30 (disabilities) vs 0.17; timing 0.47; extra-time review inconclusive | meta-analysis (dissertation) | mostly US | test scores | ~ full text 403; Gregg & Nelson via reference lists only |
| w3-05-05 | Read-aloud/TTS d = 0.35 [0.14, 0.56] for reading disabilities | meta-analysis | grade 3 to postsecondary, mostly US | learning | ✓ (paper says 22 studies in text, 23 in its table) |
| w3-05-06 | EEF SEND guidance: five recommendations, high-quality teaching for all | practitioner | mainstream schools, England | policy | ~ via nasen; the five strategies from practitioner summaries only |
| w3-05-07 | Three options optimal (80 years of research) | meta-analysis | mostly US school-age | prediction (item quality) | ~ abstract only; study count not confirmed |
| w3-05-08 | Example pack: 7 of 9 correct options are the node description; correct option longer than every distractor | our code and pack audit | example pack | prediction (test-wiseness cue) | ~ longer in 7 of 9 parts, not 6 |
| w3-05-09 | Only glossaries/dictionaries had a significant (small) effect for English learners | meta-analysis | US K–12 English learners | learning | ~ abstract only |
| w3-05-10 | Academic-vocabulary RCT (N = 2,082) helped most for non-English home language; no UK 14–18 studies | RCT + systematic review | US grade 6; mixed | learning | ~ review points via search summary only |
| w3-05-11 | Dyslexie font no benefit; spacing and short lines help subsets | experiments | children; US high-school (short lines) | reading | ~ Kuster and Zorzi at abstract level |
| w3-05-12 | Segmenting: small-to-medium retention and transfer effects | meta-analysis | mostly adults | learning | ~ prior-knowledge moderator not confirmed |
| w3-05-13 | Notes FK 8.4; move texts long-sentenced | our analysis | example pack | readability (proxy) | ~ moves pool at FKGL 10.4, 25.2 words per sentence, 5 files over 25 |
| w3-05-14 | ITS g = 0.01–0.09 on K–12 maths; less for low achievers | meta-analysis | US K–12 maths | learning | ~ abstract only |
| w3-05-15 | ASSISTments RCT: gains, larger for low prior attainers (g = 0.18) | RCT | US grade 7, 1:1 laptops | learning | ~ g from SRI summary; full paper not read |
| w3-05-16 | ASD-STE100: 20/25-word sentence limits, about 900 approved words | practitioner (analogy) | technical writers | policy | ~ via Wikipedia; standard not checked |
| w3-05-17 | Equality Act Sch 10 (accessibility plans) and Sch 13 (FE duty to disabled students generally) | official document | England, Wales, Scotland | policy | ✓ |

Also cited here; each sits in its home report's table: w2-08-04 ✓ ([business plan](business-plan.md)); w1-06-10 ~ ([06](06-settings-simulation.md)).
