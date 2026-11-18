# 01 · Competition fit: Cambridge EduX 2026 UK, AI literacy

Wave 1. Sources: scout note `work/w1/w1-01.md` with verifier marks `verify-A.json`; the judges panel (`panel-judges.md`); the competition-relevant parts of the other wave-1 scout notes (marks in `verify-B/C/D.json`). Marks: ✓ confirmed, ~ broadly supported with a stated problem. Findings marked ✗ are left out.

**Facts set by the coordinator, which override the scout notes:**
- **Step 05e is built but not merged.** Step 05e (AI-literacy coaching: Ask, Verify, How AI works) is built on branch `build/05e-literacy-coaching`, 14 commits ahead of `main`, and pushed. We checked this with `git rev-list` and `merge-base`. Scout notes that say "not built", or that count 10 commits (w1-01-13 ✓), are out of date.
- **No published rubric, and the brief is still missing.** The official rules page publishes no rubric or weights (w1-01-02 ✓). The Challenge 1 brief page renders in the browser and could not be fetched, so the team must paste it into the repo on Wednesday.

## Summary
- **There is one explicit criterion: fit to the chosen problem.** The rules add three implied ones: educational value, a working prototype on video, and, at the expo, "who it helps" and "how it works in practice". There are no weights, and complex code earns nothing (w1-01-02 ✓, w1-01-03 ✓).
- **The assessing half is built, but only on its branch.** Step 05e scores Ask, Verify and How AI works from moments in normal study. The branch is not merged to `main`, and `seed-demo` gives no student any AI-literacy history, including on the branch: `edux/cli.py` is unchanged there.
- **The biggest gap is the video.** All seven sections of `docs/demo-script.md` show economics personalisation, and none shows AI literacy (w1-01-13 ✓). The red team's verdict was "a revision tutor with AI literacy attached".
- **The defining half is missing as a deliverable.** Today it is three rows in a CSV and a one-line topic description. There is no definition slide, no levels written as behaviours, no scope and no framework mapping. [02](02-ai-literacy-assessment.md) holds the definition and slide text.
- **The credible framework anchor is the final OECD–EC AILit Framework (2026),** with 4 domains and 19 competences (w1-02-01 ✓). eduX covers parts of 8 competences and none in full; the crosswalk is in [02](02-ai-literacy-assessment.md).
- **Prior winners point towards assessing thinking.** The 2025 grand champion was an oral assessment of critical thinking (w1-01-07 ✓). Friction, which prompts verification and reports to educators, is reported as an Oceania winner, but only through search snippets, and the official gallery doesn't name it (w1-01-08 ~).
- **Who can use it, honestly.** The filmed client (claude.ai consumer) is 18+ (w1-05-02 ✓). Say so on screen, and name the school route.
- **Drop the Khanmigo line.** The 05e step doc (line 7) still says refused students stopped using Khanmigo. The trial does not support this (w1-09-08 ~). The fix lives in [09](09-safety-ethics.md) rec 11.

## Ranked recommendations
Ranks 1–10 can be done before Thursday 23:59.

| rank | recommendation | lands in | effort | before Thu? | rests on |
|---|---|---|---|---|---|
| 1 | **Paste the brief.** First thing on Wednesday, someone opens the UK challenge page in a browser and pastes all five sections (Problem Overview, Challenge Statement, Target Users, Scope & Focus, Desired Outcomes) and the setter's name into `docs/research/overnight/challenge-brief.md`. Then re-check the criteria table below against Desired Outcomes. | pitch, video | S | yes | w1-01-04 ✓ |
| 2 | **Merge 05e and build the video around one AI-literacy episode of about 75 s.** (a) A vague research question gets a full sourced answer plus an Ask task. (b) The student reports that a link didn't say what was claimed, and gets a correction plus a how-AI-works check. (c) A wrong pick names the misconception. (d) Progress shows Ask, Verify and How AI works. Cut demo-script sections 4, 6 and 7 from the video and keep them for the expo. | build, video | M | yes | w1-01-13 ✓; panel-judges |
| 3 | **"What we mean by AI literacy" slide:** the definition, three scored skills as behaviours, the AILit crosswalk, and what is out of scope. The text is in [02](02-ai-literacy-assessment.md), "Definition and competency model". | pitch, video opening | S | yes | w1-02-01 ✓, w1-02-02 ✓, w1-02-03 ✓ |
| 4 | **Rubric slide (3 skills × 3 levels)**, each cell an observable behaviour, taken from the 05e new/developing/secure texts. | pitch | S | yes | w1-01-03 ✓ |
| 5 | **Seed one demo student with AI-literacy history.** Give them several earlier research questions with few features, one Verify task, and one held "searched a database and picked the wrong entry" misconception (m2), so progress shows a path and not an empty section. This touches `edux/cli.py seed-demo`, so the build team owns it. With web search on, m2 may be the true account of a bad link ([02](02-ai-literacy-assessment.md) rec 7), so film with web search off, as the [demo plan](demo-plan.md) says. | build, demo | S–M | yes | w1-01-13 ✓; [02](02-ai-literacy-assessment.md) rec 7 |
| 6 | **Fix the give-away MCQ wording before recording.** Economics pack: the correct option has no full stop and is shorter, in 6 of 6 option sets ([04](04-economics-education.md) rec 1, our count). Literacy pack: the distractors use absolute words ("always", "only", "on purpose") while the correct options hedge with "can" ([02](02-ai-literacy-assessment.md) rec 3). | course pack (team) | S | yes | [04](04-economics-education.md) rec 1; [02](02-ai-literacy-assessment.md) rec 3 |
| 7 | **Validity-honesty slide:** what we have (fixed rules, server-scored MCQs, an evidence-centred design) and what we'd gather (agreement with humans, a pilot against an external test). Slide text in [02](02-ai-literacy-assessment.md). | pitch | S | yes | w1-02-33 ~; w1-02-20 ✓ to w1-02-22 ✓ |
| 8 | **"Who it helps / how it works in practice" slide.** Students get the checks inside their usual chatbot, with no extra model calls. Teachers get a **mock** class view: skill levels and the commonest misconceptions, aggregated, never chats. Say "adult team account" on screen. Today it reaches over-18s and teachers; next comes Microsoft Copilot Studio, then OAuth. | pitch, video caption | S | yes (mock) | w1-01-03 ✓; w1-05-02 ✓; w1-01-08 ~ |
| 9 | **Drop the Khanmigo-refusal justification from the deck.** Justify "never withhold research answers" on design grounds: checking is practised on a real, full answer. Course questions stay hint-first, in line with the DfE standard (w1-09-01 ✓). The doc fix is [09](09-safety-ethics.md) rec 11. | pitch | S | yes | w1-09-08 ~; w1-09-01 ✓ |
| 10 | **Expo kit.** A laptop running the server locally, one pre-seeded student, a reset step between judges, a recorded fallback of the literacy segment, and one printed rubric page. At least one member must be onsite at Homerton on 20 Nov. | demo | S | yes | w1-01-02 ✓, w1-01-05 ✓ |
| 11 | **A real teacher view** (class-level literacy levels and misconceptions, privacy checklist §5). | build | L | no | w1-01-08 ~ |
| 12 | **OAuth and a school-tenant route** for under-18s. | build | L | no | w1-05-02 ✓ |

## Criteria table
The rows come from what the rules page actually publishes (w1-01-02 ✓, w1-01-03 ✓). "Defining" comes from the challenge title, which no public page we reached confirms: the brief has not yet been pasted. The red-team scores are the panel's guesses, not the judges'.

| criterion (source) | what eduX has | rating | fix | red-team score (1–5) |
|---|---|---|---|---|
| Addresses the chosen problem: **assessing** AI literacy (Judging) | 05e on its branch: three skills, evidence-centred design, BKT evidence types, how-AI-works MCQs built from misconceptions, triggered at real failure moments | **Partial.** Strong in design, built, but not merged and not on video. Scoring problems in report 02. | Merge; fix the scoring rules in report 02; give it the main shot in the video (rec 2) | 2 |
| Addresses the chosen problem: **defining** AI literacy (title; brief not yet pasted) | Part ids and one-line descriptions in `ingest/ai_literacy/nodes.csv` | **Missing** as a deliverable | Definition, rubric, crosswalk and scope slides (recs 3–4) | (in the above) |
| Working prototype in a 2–3 min video (Submission) | The server runs and the MCP checks pass (our capture run: 51/51, 14 ms median, no network calls; not verified; see the [demo plan](demo-plan.md)). `demo-script.md` has no literacy moment. | **Partial:** the prototype works, but the video plan shows the wrong thing | Literacy episode (rec 2), seeded history (rec 5), MCQ wording (rec 6) | 2 |
| Educational value explained (Submission) | Learning-science grounding in `research.md`; lateral reading can be taught (Wineburg et al. 2022, already in `research.md`) | **Partial:** no evidence yet that our scores mean what they claim; the Khanmigo line is unsupported | Validity slide (rec 7); drop Khanmigo (rec 9) | 3 |
| Who it helps (Central Themes) | Students see progress. There is no teacher view. The filmed client is 18+. | **Partial** | Mock teacher view and honest access wording (rec 8); real view later (rec 11) | 2 |
| How it could work in practice (Central Themes) | It plugs into the school's existing chatbot, makes no model calls, uses fixed rules, and has teacher-editable trusted sources | **Strong** | One clear slide (rec 8). Note the open items: OAuth, under-18 access, ChatGPT's per-call confirmations ([05](05-product-features.md)) | 3 |
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
- **A real teacher view.** Class-level levels and misconceptions only; never chats; off by default unless the school turns it on (privacy checklist §5).
- **OAuth, and a documented school route for under-18s.** Microsoft Copilot Studio is the best documented today (w1-05-11 ✓, [05](05-product-features.md)).
- **If the UK setter is Cambridge University Press & Assessment,** align the definition slide's language with its AI-literacy material. Its Oceania involvement is confirmed (w1-01-09 ✓). For the UK it is unknown.
- **Prize details.** None are published for the UK edition. Don't quote the Oceania prizes as UK prizes (w1-01-06 ✓).

## Considered and rejected
- **Using another hackathon's rubric as a proxy.** It would mean inventing criteria (w1-01-02 ✓).
- **Treating the Oceania Challenge 1 (higher-education assessment) as ours.** It was a different edition with different numbering.
- **A standalone AI-literacy quiz to "prove" the assessment.** It contradicts the embedded design. An external test belongs in a validity pilot, not in the product (report 02).
- **Building a real teacher dashboard before Thursday.** One build day is not enough. Use a mock, labelled as a mock.
- **Naming Friction on a slide.** Its page returned 403, and the official gallery doesn't list it (w1-01-08 ~).
- **The 2025 AILit draft names ("Designing AI") or a competence count of 22.** The final framework has 19 competences and the domain Shape AI (w1-01-10 ~, w1-02-01 ✓).

## Panel objections this report answers or leaves open
| objection (panel) | status |
|---|---|
| "A revision tutor, not an AI-literacy entry" (judges 1) | **Partly**: answered only if recs 2–3 land and Plan A passes the gate. Then literacy opens the video and is its main shot. |
| "Where is your definition?" (judges 2) | **Answered** by the definition, rubric and crosswalk slides (recs 3–4). |
| "Why believe a 'secure' Verify?" (judges 3; researcher 2, 4) | **Partly.** There is a validity slide (rec 7). The scoring fixes and the agreement study are in report 02; the BKT settings are not changed yet. |
| "Your students can't legally use the chatbot you filmed" (judges 4) | **Answered** in wording (rec 8). The build (OAuth) is later. |
| "Your assessment gives the answer away" (judges 5; student 3) | **Answered** if rec 6 is done before recording. Nobody owns it yet: assign it on Wednesday. |
| "No teacher view" (judges, criterion 4) | **Partly:** a mock only. |
| "I'd never see the literacy part; it's only on research questions" (student 2) | **Partly.** Three of the four how-AI-works triggers fire on any turn, not only research turns (branch code). Ask and Verify are research-only. Literacy moments inside homework are not designed. |
| "Decide / just-show-me feels like being watched" (student 4) | **Partly, and a tension.** A scout proposed "Decide" as a fourth scored skill; [02](02-ai-literacy-assessment.md) rejects it. The trend stays unscored and visible to the student only. If it goes on a slide, say who sees it. |
| "Answer-first mode", "help with 25-markers" (student 1, 5) | **Out of scope here.** See [05](05-product-features.md) (answer-first compromise; honest essay answer) and [09](09-safety-ethics.md) rec 9. |

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

Also cited here; each sits in its home report's table: w1-02-01 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-02 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-03 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-05 ✓ ([02](02-ai-literacy-assessment.md)), w1-02-25 ✓ ([02](02-ai-literacy-assessment.md)), w1-05-02 ✓ ([05](05-product-features.md)), w1-09-01 ✓ ([09](09-safety-ethics.md)), w1-09-08 ~ ([09](09-safety-ethics.md)).
