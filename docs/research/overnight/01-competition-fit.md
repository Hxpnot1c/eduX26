# 01 · Competition fit: Cambridge EduX 2026 UK, AI literacy

Wave 1, with a wave-2 consistency edit. Sources: scout note `work/w1/w1-01.md` with verifier marks `verify-A.json`; the judges panel (`panel-judges.md`); the competition-relevant parts of the other wave-1 scout notes (marks in `verify-B/C/D.json`). Wave 2 added no 01 scout note; this edit brings 01 into line with the wave-2 reports ([02](02-ai-literacy-assessment.md), [05](05-product-features.md), [business plan](business-plan.md)) and the wave-2 panel (`work/w2/panel-judges-researcher.md`). Marks: ✓ confirmed, ~ broadly supported with a stated problem. Findings marked ✗ are left out.

**Facts set by the coordinator, which override the scout notes:**
- **Step 05e is built but not merged.** Step 05e (AI-literacy coaching: Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and pushed. We checked this with `git rev-list` and `merge-base`. Scout notes that say "not built", or that count 10 commits (w1-01-13 ✓), are out of date.
- **No published rubric, and the brief is still missing.** The official rules page publishes no rubric or weights (w1-01-02 ✓). The Challenge 1 brief page renders in the browser and could not be fetched, so the team must paste it into the repo on Wednesday.
- **(Wave 2) Gemini has caught up on tracking.** Study notebooks track progress across sessions (25 Jun 2026), and Google Classroom gives teachers progress insights (from 3 Nov 2026) (w2-08-01 ✓, w2-08-02 ✓). The line "hosts shape one conversation; eduX keeps a learner model across sessions" is no longer true. Lead with AI-literacy evidence from real use, plus a school-owned learner model that works across chatbots, and call it a head start, not a moat.
- **(Wave 2) Web search is off for the video, and the "searched a database and picked the wrong entry" option (m2) is never taught as a misconception.** With search on it is often the true account (w2-02-33 ~, w2-02-34 ✓).

## Summary
- **There is one explicit criterion: fit to the chosen problem.** The rules add three implied ones: educational value, a working prototype on video, and, at the expo, "who it helps" and "how it works in practice". There are no weights, and complex code earns nothing (w1-01-02 ✓, w1-01-03 ✓).
- **The assessing half is built, but only on its branch.** Step 05e scores Ask, Verify and How AI works from moments in normal study. The branch is not merged to `main`, and `seed-demo` gives no student any AI-literacy history, including on the branch: `edux/cli.py` is unchanged there.
- **The biggest gap is the video.** All seven sections of `docs/demo-script.md` show economics personalisation, and none shows AI literacy (w1-01-13 ✓). The red team's verdict was "a revision tutor with AI literacy attached".
- **The defining half is missing as a deliverable.** Today it is three rows in a CSV and a one-line topic description. There is no definition slide, no levels written as behaviours, no scope and no framework mapping. [02](02-ai-literacy-assessment.md) holds the definition and slide text.
- **The credible framework anchor is the final OECD–EC AILit Framework (2026),** with 4 domains and 19 competences (w1-02-01 ✓). eduX covers parts of 8 competences and none in full; the crosswalk is in [02](02-ai-literacy-assessment.md).
- **Prior winners point towards assessing thinking.** The 2025 grand champion was an oral assessment of critical thinking (w1-01-07 ✓). Friction, which prompts verification and reports to educators, is reported as an Oceania winner, but only through search snippets, and the official gallery doesn't name it (w1-01-08 ~).
- **Who can use it, honestly.** The filmed client (claude.ai consumer) is 18+ (w1-05-02 ✓). Say so on screen, and name the school route.
- **Drop the Khanmigo line.** The 05e step doc (line 7) still says refused students stopped using Khanmigo. The trial does not support this (w1-09-08 ~). No report's ranked list owns the doc fix now; it is a one-line team edit, and rec 9 below keeps it out of the deck.
- **Competition has moved (wave 2).** Gemini tracks progress across sessions and reports it to teachers in Classroom, free to Google schools (w2-08-01 ✓, w2-08-02 ✓). We found no public evidence that ChatGPT tracks progress (w2-08-03 ✓; absence after search, not proof). Claude for Teachers is US-only and already connects to Eedi and ASSISTments (w2-08-04 ✓, w2-08-05 ✓). eduX's honest difference is narrow: AI-literacy evidence (Ask, Verify) from real chatbot use, and a learner model the school owns across chatbots. Both are an unvalidated head start, not a moat ([business plan](business-plan.md) rec 1).

## Ranked recommendations
Ranks 1–11 can be done before Thursday 23:59.

| rank | recommendation | lands in | effort | before Thu? | rests on |
|---|---|---|---|---|---|
| 1 | **Paste the brief.** First thing on Wednesday, someone opens the UK challenge page in a browser and pastes all five sections (Problem Overview, Challenge Statement, Target Users, Scope & Focus, Desired Outcomes) and the setter's name into `docs/research/overnight/challenge-brief.md`. Then re-check the criteria table below against Desired Outcomes. | pitch, video | S | yes | w1-01-04 ✓ |
| 2 | **Merge 05e and build the video around one AI-literacy episode of about 75 s.** (a) A vague research question gets a full sourced answer plus an Ask task. (b) The student reports that a link didn't say what was claimed, and gets a correction plus a how-AI-works check. (c) A wrong pick names the misconception. (d) Progress shows Ask and Verify levels, and How AI works as per-part counts ("checked n, right m") plus the wrong ideas still held, not as a level ([02](02-ai-literacy-assessment.md) rec 6). Cut demo-script sections 4, 6 and 7 from the video and keep them for the expo. | build, video | M | yes | w1-01-13 ✓; panel-judges |
| 3 | **"What we mean by AI literacy" slide:** the definition, three scored skills as behaviours, the AILit crosswalk, and what is out of scope. The text is in [02](02-ai-literacy-assessment.md), "Definition and competency model". | pitch, video opening | S | yes | w1-02-01 ✓, w1-02-02 ✓, w1-02-03 ✓ |
| 4 | **Rubric slide (3 skills × 3 levels)**, each cell an observable behaviour, taken from the 05e new/developing/secure texts. The rubric may describe How AI works in levels of behaviour, but the product and video report it as per-part counts, because the rolled-up level ranks students backwards in simulation ([02](02-ai-literacy-assessment.md) rec 6). | pitch | S | yes | w1-01-03 ✓; w2-02-05 ~ |
| 5 | **Seed one demo student with AI-literacy history.** Give them several earlier research questions with few features, one Verify task, and one held how-AI-works wrong idea taken from [02](02-ai-literacy-assessment.md)'s rewritten set (for example "a reference with a journal and year is probably real"), so progress shows a path and not an empty section. **Never seed or teach m2** ("searched a database and picked the wrong entry"): with search on it is often true. Film with web search off and caption it. The point taught is that a cited source may not exist, or may not say what was claimed ([02](02-ai-literacy-assessment.md) recs 3 and 7). This touches `edux/cli.py seed-demo`, so the build team owns it. | build, demo | S–M | yes | w1-01-13 ✓; w2-02-33 ~, w2-02-34 ✓; [02](02-ai-literacy-assessment.md) recs 3, 7 |
| 6 | **Fix the give-away MCQ wording before recording.** Economics pack: the correct option has no full stop and is shorter, in 6 of 6 option sets ([04](04-economics-education.md) rec 1, our count). Literacy pack: the distractors use absolute words ("always", "only", "on purpose") while the correct options hedge with "can" ([02](02-ai-literacy-assessment.md) rec 3). | course pack (team) | S | yes | [04](04-economics-education.md) rec 1; [02](02-ai-literacy-assessment.md) rec 3 |
| 7 | **Validity-honesty slide:** what we have (fixed rules, server-scored MCQs, an evidence-centred design) and what we'd gather (agreement with humans, a pilot against an external test). Slide text in [02](02-ai-literacy-assessment.md). | pitch | S | yes | w1-02-33 ~; w1-02-20 ✓ to w1-02-22 ✓ |
| 8 | **"Who it helps / how it works in practice" slide.** Students get the checks inside their usual chatbot, with no extra model calls. Teachers get a **mock** class view: misconceptions to reteach and the weakest parts, aggregated, groups of 6 or more, never chats. Class-level AI literacy appears only in bands, and only if the school opts in; never per student ([05](05-product-features.md) rec 4). Say "adult team account" on screen. Today it reaches over-18s and teachers. For under-18s, Microsoft 365 Education via Copilot Studio is the documented school route, untested, and Copilot Chat is off by default for 13–17s ([05](05-product-features.md) recs 1–3). | pitch, video caption | S | yes (mock) | w1-01-03 ✓; w1-05-02 ✓; w2-05-03 ✓, w2-05-04 ✓ |
| 9 | **Drop the Khanmigo-refusal justification from the deck.** Justify "never withhold research answers" on design grounds: checking is practised on a real, full answer. Course questions stay hint-first, in line with the DfE standard (w1-09-01 ✓). The 05e step-doc line needs a one-line team edit; no report's ranked list owns it. | pitch | S | yes | w1-09-08 ~; w1-09-01 ✓ |
| 10 | **Expo kit.** A laptop running the server locally, one pre-seeded student, a reset step between judges, a recorded fallback of the literacy segment, and one printed rubric page. At least one member must be onsite at Homerton on 20 Nov. | demo | S | yes | w1-01-02 ✓, w1-01-05 ✓ |
| 11 | **"Why not Gemini?" answer, slide and Q&A.** "Gemini now tracks progress inside Google, and Classroom shows teachers progress. We don't sell to Google schools. eduX gives a school evidence of how pupils ask and check, from real chatbot use, and a learner model the school owns across chatbots. A head start, not a moat; not yet validated." Never say the hosts "shape one conversation". | pitch | S | yes | w2-08-01 ✓, w2-08-02 ✓, w2-08-03 ✓; [business plan](business-plan.md) rec 1 |
| 12 | **A real teacher view** (privacy checklist §5; spec in [05](05-product-features.md)). | build | L | no | w2-05-23 ~, w2-05-29 ✓ |
| 13 | **Entra sign-in and a tested school-tenant route** for under-18s. | build | M–L | no | w1-05-02 ✓, w2-05-03 ✓, w2-05-04 ✓ |

## Criteria table
The rows come from what the rules page actually publishes (w1-01-02 ✓, w1-01-03 ✓). "Defining" comes from the challenge title, which no public page we reached confirms: the brief has not yet been pasted. The red-team scores are the panel's guesses, not the judges'.

| criterion (source) | what eduX has | rating | fix | red-team score (1–5) |
|---|---|---|---|---|
| Addresses the chosen problem: **assessing** AI literacy (Judging) | 05e on its branch: three skills, evidence-centred design, BKT evidence types, how-AI-works MCQs built from misconceptions, triggered at real failure moments | **Partial.** Strong in design, built, but not merged and not on video. Scoring problems in report 02. | Merge; fix the scoring rules in report 02; give it the main shot in the video (rec 2) | 2 |
| Addresses the chosen problem: **defining** AI literacy (title; brief not yet pasted) | Part ids and one-line descriptions in `ingest/ai_literacy/nodes.csv` | **Missing** as a deliverable | Definition, rubric, crosswalk and scope slides (recs 3–4) | (in the above) |
| Working prototype in a 2–3 min video (Submission) | The server runs and the MCP checks pass (our capture run: 51/51, 14 ms median, no network calls; not verified; see the [demo plan](demo-plan.md)). `demo-script.md` has no literacy moment. | **Partial:** the prototype works, but the video plan shows the wrong thing | Literacy episode (rec 2), seeded history (rec 5), MCQ wording (rec 6), the three crash and loop bugs fixed before filming ([06](06-settings-simulation.md) recs 1–3) | 2 |
| Educational value explained (Submission) | Learning-science grounding in `research.md`; lateral reading can be taught (Wineburg et al. 2022, already in `research.md`) | **Partial:** no evidence yet that our scores mean what they claim; the Khanmigo line is unsupported | Validity slide (rec 7); drop Khanmigo (rec 9) | 3 |
| Who it helps (Central Themes) | Students see progress. There is no teacher view. The filmed client is 18+. Gemini now gives Google schools progress tracking and teacher insights free (w2-08-01 ✓, w2-08-02 ✓). | **Partial** | Mock teacher view and honest access wording (rec 8); the Gemini answer (rec 11); real view later (rec 12) | 2 |
| How it could work in practice (Central Themes) | It plugs into the school's existing chatbot, makes no model calls, uses fixed rules, and has teacher-editable trusted sources | **Partial** (wave 2 downgrade): the only documented under-18 route, Copilot Studio, is untested, and there the school pays Microsoft Copilot Credits per turn (our rough estimate, unverified: w2-05-06 ~) | One clear slide (rec 8). Note the open items: sign-in, under-18 access, credit cost, ChatGPT's per-call confirmations ([05](05-product-features.md)) | 3 |
| Expo: judges visit, watch demos, ask questions (Judging) | Connector and tunnel set-up (step 06) | **Partial** | Expo kit (rec 10) | n/a |
| Complex code not required (Judging) | A lot of engineering | **Over-delivered.** The risk is spending video time on architecture. | Lead with the student moment; show the server for 10 s at most | n/a |
| Interdisciplinary teams encouraged (Central Themes) | Four economics students | **Partial** | Present the team as subject experts building on learning science; don't claim a mix we don't have | n/a |

## Defining AI literacy: what we under-deliver
**What exists.** The definition is only implicit:
- **Content rows.** Three skill parts and four how-AI-works parts in `ingest/ai_literacy/nodes.csv` (branch).
- **A topic line.** "Using AI chatbots well for study: asking precise questions and checking what they say."
- **What is missing.** There is no stated definition, no levels written as behaviours, no scope, and no link to a framework.

A brief titled "Defining and Assessing" asks for both halves. Today we deliver about one and a half.

**What the judges would ask (panel-judges Q1):** "Define AI literacy in one sentence."

**The fix.** One slide with the definition, the three scored skills written as behaviours, the AILit crosswalk and what is out of scope. The wording, the crosswalk and the framework notes live in [02](02-ai-literacy-assessment.md) ("Definition and competency model" and "Framework crosswalk"); use them as written. Two points matter for competition fit:
- **Use the names the video shows.** The progress output on screen says `ask`, `verify` and `how_ai_works`, so the slide should too.
- **Answer the judges' first question in one sentence.** "Knowing when and how far to trust a chatbot, shown in what students do while they work" ([02](02-ai-literacy-assessment.md)).

## Later (not before Thursday; for the business plan and Q&A)
- **A real teacher view.** Misconceptions and weakest parts for groups of 6 or more; class AI literacy in bands, opt-in; per-student completion only as a school opt-in, default off; never chats, levels or AI-literacy scores per student (coordinator decision; [05](05-product-features.md)).
- **Sign-in, and a tested school route for under-18s.** Copilot Studio in a K-12 Microsoft 365 tenant is documented (w2-05-03 ✓, w2-05-04 ✓), untested, and costs the school Copilot Credits ([05](05-product-features.md), [business plan](business-plan.md)).
- **If the UK setter is Cambridge University Press & Assessment,** align the definition slide's language with its AI-literacy material. Its Oceania involvement is confirmed (w1-01-09 ✓). For the UK it is unknown.
- **Prize details.** None are published for the UK edition. Don't quote the Oceania prizes as UK prizes (w1-01-06 ✓).

## Considered and rejected
- **Using another hackathon's rubric as a proxy.** It would mean inventing criteria (w1-01-02 ✓).
- **Treating the Oceania Challenge 1 (higher-education assessment) as ours.** It was a different edition with different numbering.
- **A standalone AI-literacy quiz to "prove" the assessment.** It contradicts the embedded design. An external test belongs in a validity pilot, not in the product (report 02).
- **Building a real teacher dashboard before Thursday.** One build day is not enough. Use a mock, labelled as a mock.
- **Naming Friction on a slide.** Its page returned 403, and the official gallery doesn't list it (w1-01-08 ~).
- **"Hosts shape one conversation; eduX keeps a learner model across sessions" as a moat.** False for Gemini since June 2026 (w2-08-01 ✓).
- **The 2025 AILit draft names ("Designing AI") or a competence count of 22.** The final framework has 19 competences and the domain Shape AI (w1-01-10 ~, w1-02-01 ✓).

## Panel objections this report answers or leaves open
| objection (panel) | status |
|---|---|
| "A revision tutor, not an AI-literacy entry" (judges 1) | **Partly**: met only if recs 2–3 land and Plan A passes the gate. Then literacy opens the video and is its main shot. |
| "Where is your definition?" (judges 2) | **Answered** by a document: the definition, rubric and crosswalk text in [02](02-ai-literacy-assessment.md) (slides: recs 3–4). |
| "Why believe a 'secure' Verify?" (judges 3; researcher 2, 4) | **Partly.** There is a validity slide (rec 7). The scoring fixes and the agreement study are in report 02; the BKT settings are not changed yet. |
| "Your students can't legally use the chatbot you filmed" (judges 4) | **Partly.** Honest captions and route wording (rec 8); no tested under-18 route; sign-in is later. |
| "Your assessment gives the answer away" (judges 5; student 3) | **Recommended** (rec 6), not done. Nobody owns it yet: assign it on Wednesday. |
| "Your demo corrects a true belief" (m2; judges w2 #1) | **Recommended**: rec 5 and the [demo plan](demo-plan.md) now teach "the source may not exist or may not say what was claimed" with search off. Not filmed yet. |
| "Why not Gemini?" (judges w2 #2; investor w1 #2, w2 #3) | **Partly**: honest head-start wording (rec 11); no moat and no validation. |
| "No teacher view" (judges, criterion 4) | **Partly:** a mock only. |
| "I'd never see the literacy part; it's only on research questions" (student 2) | **Partly.** Three of the four how-AI-works triggers fire on any turn, not only research turns (branch code). Ask and Verify are research-only. Literacy moments inside homework are not designed. |
| "Decide / just-show-me feels like being watched" (student 4) | **Partly, and a tension.** A scout proposed "Decide" as a fourth scored skill; [02](02-ai-literacy-assessment.md) rejects it. The trend stays unscored and visible to the student only. If it goes on a slide, say who sees it. |
| "Answer-first mode", "help with 25-markers" (student 1, 5) | **Out of scope here.** See [05](05-product-features.md) (answer-first compromise; honest essay answer) and [09](09-safety-ethics.md) rec 14. |

## Findings
| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-01-01 | UK edition: a 2–3 min video and a 4-min pitch deck, due Thu 19 Nov 2026, 11:59 PM GMT | official document | EduX UK entrants | policy | ✓ |
| w1-01-02 | Judging is on fit to the chosen problem; no complex code needed; expo-style; no rubric or weights | official document | EduX UK entrants | policy | ✓ |
| w1-01-03 | Teams should show the idea, who it helps and how it works in practice, and explain its educational value | official document | EduX UK entrants | policy | ✓ |
| w1-01-04 | Four exploration areas; briefs have five fixed sections, Desired Outcomes among them | official document | EduX UK entrants | policy | ✓ |
| w1-01-05 | Open entry; at least one member onsite at Homerton on 20 Nov; interdisciplinary teams encouraged; team owns its IP | official document | EduX UK entrants | policy | ✓ |
| w1-01-06 | No UK prizes published; Luma says cash and AI tokens "to be revealed"; Oceania prizes differ | official document | EduX UK and Oceania | policy | ✓ |
| w1-01-07 | 2025 grand champion: oral assessment of critical thinking; Oceania 2026 winners listed without descriptions | official document | adult entrants | adoption (awards) | ✓ |
| w1-01-08 | Friction (Monash TAILER Lab) reported as an Oceania winner; prompts verification; reports to educators | practitioner (secondary) | higher education, Australia | adoption | ~ page 403; snippets only; not in the official gallery |
| w1-01-09 | Oceania challenge setters included Cambridge University Press & Assessment | official document | EduX Oceania | policy | ✓ |
| w1-01-10 | AILit: four domains (Engage, Create, Manage, Shape) | official document | school students, EU/OECD | policy | ~ the count is 19 in the final framework, not "unresolved" |
| w1-01-11 | UNESCO students' framework: 12 competencies, 4 dimensions, 3 levels | official document | school students, worldwide | policy | ~ secondary only (use w1-02-06 ✓ instead) |
| w1-01-12 | Long & Magerko: evaluate / communicate and collaborate / use as a tool; 17 competencies | theory | general learners | policy | ~ via secondary review (use w1-02-07 ✓ instead) |
| w1-01-13 | 05e on its branch, not on `main`; demo script has no literacy moment; seed-demo has no literacy history | repo inspection | n/a | adoption (build status) | ✓ (commit count now 14, per coordinator) |

Also cited here; each sits in its home report's table: w2-02-05 ~, w2-02-33 ~, w2-02-34 ✓ ([02](02-ai-literacy-assessment.md)); w2-05-03 ✓, w2-05-04 ✓, w2-05-06 ~, w2-05-23 ~, w2-05-29 ✓ ([05](05-product-features.md)); w2-08-01 ✓ to w2-08-05 ✓ ([business plan](business-plan.md)); w1-02-01 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-02 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-03 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-05 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-25 ✓ ([02](02-ai-literacy-assessment.md)), w1-05-02 ✓ ([05](05-product-features.md)), w1-09-01 ✓ ([09](09-safety-ethics.md)), w1-09-08 ~ ([09](09-safety-ethics.md)).
