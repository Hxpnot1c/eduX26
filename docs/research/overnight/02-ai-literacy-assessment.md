# 02 · Defining and assessing AI literacy

Waves 1 and 2. Sources:
- **Wave 1 scout notes.** `work/w1/w1-02a.md` (framework crosswalk; marks in `verify-D.json`) and `work/w1/w1-02b.md` (validity and reliability; marks in `verify-B.json`).
- **Wave 2 scout notes.**
  - `work/w2/w2-02.md`: a scoring simulation on the 05e branch's real learner code, plus the literature on missing responses. Marks in `verify-J.json`.
  - `work/w2/w2-02h.md`: what chatbots actually get wrong with sources and pushback, and whether they can label it themselves. Marks in `verify-E.json`, ids w2-02-30 to -45.
  - `work/w2/w2-09.md`: how UK 16–18s use chatbots, and new literacy moments. Marks in `verify-E.json`.
- **Panels.** Wave 1: researcher and student. Wave 2: `panel-judges-researcher.md` and `panel-teacher-student.md`.
- **Branch.** `build/05e-literacy-coaching`, read-only in `/home/vishnu/edux26`.

Marks: ✓ confirmed; ~ broadly supported, with the stated problem. Findings marked ✗ are left out (none in this area). Simulation results are labelled "simulation: synthetic students".

**Coordinator's facts, which override the scout notes.**
- Step 05e is **built on its branch, 14 commits ahead of `main`, and not merged**.
- For the video, web search is off. Even so, the "searched a database and picked the wrong entry" option (m2) must not be taught as a misconception, because with search on it is often true (w2-02-33 ~, w2-02-34 ✓).
- Teachers never see per-student AI-literacy levels, scores, offloading or draft counts. Class-level AI literacy is shown only in bands, for groups of 6 or more, and only if the school opts in.

## Summary
- **What we measure is narrow, and we should say so.** Ask, Verify and How AI works cover parts of AILit Engage 2 and 3 and part of Create 3. No AILit competence is fully covered (w1-02-01 ✓, w1-02-03 ✓, w1-02-04 ~). Only the how-AI-works letter is scored by the server alone. Everything else rests on labels the chatbot assigns, or on what the student says they did.
- **A chatbot can't reliably label its own failures.**
  - Without outside feedback, self-correction cut GPT-3.5 from 75.8% to 38.1% on one benchmark (w2-02-41 ✓).
  - Confidence stated in words is overconfident (w2-02-42 ~).
  - Models have claimed to use tools they didn't have (w2-02-43 ✓).
  - So whether search was on should come from a school setting, not from the chatbot. Labels where the chatbot judges its own correctness (`conflict_flagged`, a proposed `pushback_correct`) are weak evidence.
- **The simulation runs on our real code, and the risk is the level shown in the chat, not the weekly read** (simulation: synthetic students).
  - On the branch, a no-skill student is shown "secure" at a weekly read in at most 1% of cases.
  - The risk is the level shown in the chat right after a lucky moment. Up to 13–15% of no-skill students see Ask "secure" at some point when the chatbot labels leniently (w2-02-01 ✓, w2-02-02 ✓).
  - Three setting changes, with no code, cut that to at most 3% at 20% random label errors, and 4–7% under lenient labelling (w2-02-08 ✓). The three: `ask_min_features` = 3, `ail_question` guess .30 and `ail_unprompted` guess .20.
  - Never lower `correct_share` to 0.5 (w2-02-03 ~).
- **The How AI works level ranks students backwards.** At week 8, no-skill students rank above strong ones: AUC 0.40 when ignoring is tied to skill, 0.44 when it isn't (w2-02-05 ~).
  - The cause is the decay clock: 05e starts it only at a part's first correct answer (`edux/learner.py:433-434, 692-695`).
  - Show per-part counts, not a level. The same asymmetry may affect economics parts.
- **Settings can't fix Verify.** A student who restates the reply scores a correct Verify moment about as often as a partial checker: 49% vs 44% (w2-02-04 ~). Only a task that asks for something the reply doesn't contain fixes this. The new "summarise" moment does that, because the student checks against the course notes.
- **With search off, chatbots invent sources. With search on, they mostly misattribute.**
  - Search off: 55% (GPT-3.5) and 18% (GPT-4) of references were invented in 2023 (w2-02-30 ✓). 2025 audits with search status not reported found 19.9% invented (w2-02-31 ~) and 39.8% wrong or invented (w2-02-32 ~).
  - Search on: about a quarter to a third of citations or statements weren't backed by the real page cited (w2-02-33 ~, w2-02-34 ✓).
  - So the fabrication point must be true either way, and m2 goes.
- **Many answer changes under pushback are corrections.** In SycEval, 43.52% of rebuttals moved a model to a correct answer and 14.66% to an incorrect one (w2-02-38 ✓). Flip rates range from 17.5% to 97.3% across 2026 models (w2-02-39 ~). The agreement point must not imply that the student was wrong to push back.
- **Ignored tasks are missing, not wrong.**
  - NAEP treats items a student never reached as never presented (w2-02-11 ✓). PISA has not scored not-reached items as wrong since 2015 (w2-02-12 ~).
  - Show the skip count beside the level.
  - Reliability still needs about 12 moments per skill (w1-02-31 ✓). So claim a validity argument and "embedded assessment", not a validated test.

## Ranked recommendations
"Branch" means `build/05e-literacy-coaching`, which the build team owns. This report edits no code, settings or pack files. Ranks 1–18 can be done before Thursday 23:59. Ranks 19–22 are "maybe". Ranks 23–27 come after Thursday.

**Rec numbers changed in wave 2.** [01](01-competition-fit.md), the [demo plan](demo-plan.md) and [09](09-safety-ethics.md) cite wave-1 numbers. The mapping:
- 1–5 and 8–12 keep their numbers.
- Old 6 is now part of 2.
- Old 7 (film with search off so that correcting m2 is true) is **superseded**. It becomes 7 (m2 is never taught as a misconception) and 20 (key the part on whether a search happened).
- Old 13 → 23, old 14 → 24 (replaced), old 15 → 25, old 16 → 21.

| rank | recommendation | lands in | effort | before Thu? | rests on |
|---|---|---|---|---|---|
| 1 | **Definition and competency-model slide** (text below). [01](01-competition-fit.md) links here and doesn't repeat it. | pitch, video | S | yes | w1-02-01 ✓, w1-02-02 ✓, w1-02-07 ✓ |
| 2 | **Three settings in the branch's `settings.toml`, with no code** (snippet below):<br>• `literacy.ask_min_features = 3`<br>• `ail_question` guess .20 → .30<br>• `ail_unprompted` guess .10 → .20<br>Keep `ail_task` at slip .10 / guess .15 while the half-life is 2 days. **Never set `correct_share = 0.5`**: 83% of no-skill students would then be shown Ask "secure" at some point. Raising `ask_min_features` to 3 alone isn't enough: no-skill in-chat secure is then 3.4–4.6% at 10% noise, but 8–10% at 20%. | settings (branch) | S | yes | w2-02-03 ~, w2-02-08 ✓, w1-02-32 ✓ |
| 3 | **Rewrite the how-AI-works options in `ingest/ai_literacy/misconceptions.csv`.**<br>• Make the fabrication and agreement points true whatever happened behind the scenes (see "How AI works content").<br>• Drop m2 ("searched a source database and picked the wrong entry") and the absolute agreement distractor ("only… when").<br>• Every new set must pass the cue check before it goes in the csv: hedging on both sides, no absolute words ("always", "only", "on purpose"), lengths matched within a few characters, no full stops, and no "X or Y" correct option that is also the longest. | course pack (branch) | S | yes | w2-02-33 ~, -34 ✓, -38 ✓, -39 ~; branch data |
| 4 | **Record an ignored task or check as missing, not 0.**<br>• In `service._literacy_followup` and `_how_ai_works`, write a `literacy_ignored` engagement event instead of `ail_task 0` or `ail_how 0`.<br>• Show "tasks done: n of m" beside the level, so skipping can't quietly protect a level.<br>• Still score attempts: a reply of "idk" scores whatever ticks it showed.<br>• An Ask task should count as done when the student asks a research question later in the same session, not only in the very next message. On the branch it otherwise scores 0 about 2.7 times per no-skill student over 10 weeks. | build (branch) | S | yes, if the build team has time | w2-02-07 ✓, w2-02-11 ✓, w2-02-12 ~, w2-02-13 ~, w2-02-14 ~ |
| 5 | **Change the Verify task, not its settings.**<br>• Ask for something the reply doesn't contain (e.g. "what does the page give for the month before?").<br>• Add a fifth tick, "decided to accept, revise or reject, and why", and require it for secure.<br>• Downweight tick 1 ("opened the source"), which can't be observed. | course pack, text (branch) | S | yes | w2-02-04 ~, w1-02-03 ✓ |
| 6 | **Don't show a How AI works level.** Show per part "checked n, right m" and the wrong ideas still held.<br>• The rollup never reaches secure for anyone in 10 weeks.<br>• It ranks students backwards (rank 21 softens this, but doesn't remove the cause).<br>• Pitch: say "per-part results", not "level". | build (progress), pitch | S | yes | w2-02-05 ~ |
| 7 | **The demo never teaches m2 as a misconception, and it shows a correct pushback.**<br>• Film with web search off and caption it.<br>• In shots 4c–4d the student should pick a different wrong idea from the rewritten set (rec 3), not m2.<br>• Don't seed a held m2. Today 01 rec 5 and demo-plan shots 4c–4d still use it; their owners need to change them.<br>• Add a moment where the student correctly challenges a wrong number. The check that follows asks how to tell a correction from giving in ("check the notes"), not whether the student was wrong. | demo, seed (`edux/cli.py seed-demo`) | S | yes (after rec 3) | coordinator; w2-02-33 ~, -34 ✓, -38 ✓ |
| 8 | **Check the chatbot's labels against humans.**<br>• Hand-write 40 synthetic research questions (0–4 features) and 20 Verify replies (0–4 ticks).<br>• Two team members tick them blind against a one-page rubric.<br>• Get the chatbot's labels through the real MCP, and report Cohen's κ per feature with 95% CIs.<br>• κ ≥ .60 counts as usable for low-stakes formative use (our choice).<br>• Don't generate the messages with the model under test. | demo, pitch | M | yes (Wednesday, if time) | w1-02-28 ~, w1-02-29 ~ |
| 9 | **Validity-argument slide** (table below), filled in with whatever rec 8 produces. Call the method "embedded assessment". Never use the word "stealth" in pitch, video or product text. The tasks are overt, and pitch-notes bans the word. | pitch | S | yes | w1-02-33 ~; researcher panel (wave 2) |
| 10 | **Known-groups persona check.** Run a "novice" and a "practised" persona for 8 research turns each through the MCP, on a fresh `EDUX_DATA_DIR`, and show that their levels diverge. Say it tests the pipeline, not students. | demo | S | yes, once merged | scout note w1-02b |
| 11 | **Fix `docs/build/reference/research.md` row 29.** How AI works anchors to AILit Engage 2 (Knowledge 1.3 and 1.4), not to Shape AI. | docs | S | yes | w1-02-04 ~ |
| 12 | **Show how much evidence each level rests on.**<br>• Always show `n_moments`.<br>• Below 3 moments, show "not enough evidence yet" instead of a level, in the chat too, so one lucky moment can't show "secure".<br>• Below 8 moments, show "provisional".<br>The thresholds of 3 and 8 are our choice. 3 is low against the 8–12 moments that reliability needs, which is why "provisional" runs to 8. | build (progress, chat), pitch | S | pitch yes; build maybe | w1-02-31 ✓, w2-02-02 ✓; [09](09-safety-ethics.md) rec 11 |
| 13 | **"Why AI literacy" slide: lead with performance evidence, not self-report.**<br>• First line: a quarter of teens who felt confident at spotting AI content failed Ofcom's test (w2-09-04 ✓). Say "spotting AI content"; it was an image test, not checking chatbot answers.<br>• Then NLT, with its bases: 70.6% of 16–18s have used generative AI; 52.0% *of users* use it weekly (w2-09-01 ~); 58.5% *of those who had heard of it* say they check (w2-09-02 ✓). Call the NLT survey opt-in, about 4,900 aged 16–18.<br>• If a judge asks "do you believe 58.5%?", answer: "No. It's self-report, which is why we watch what students do." | pitch | S | yes | w2-09-01 ~, -02 ✓, -04 ✓; w1-02-25 ✓ |
| 14 | **Two pitch lines (our wording).**<br>• (a) "In simulation with the settings we propose for Wednesday, a synthetic student with no skill is shown 'secure' at a weekly read in under 1% of cases. They are ever shown it in the chat in at most 3%, with up to 20% of the chatbot's labels wrong at random, and 4–7% if the chatbot labels leniently. We checked the simulation against our real code."<br>• (b) "With web search on, many bad citations are real pages that don't say what the chatbot claims. Published medical papers misquote their sources about one time in four too, so eduX teaches checking, not distrust." | pitch, video | S | yes | w2-02-01 ✓, -02 ✓, -08 ✓; w2-02-33 ~, -34 ✓, -44 ✓ |
| 15 | **New moment, `request_type = summarise`: "check the summary against your notes".**<br>• Fire it only when the student summarises course material that eduX holds.<br>• Then the task is: "Find one point in your notes this summary leaves out or gets wrong." Score it on Verify ticks 3–4.<br>• For a news article or the teacher's slides, eduX can't check. Say "check one line against the original" and score nothing.<br>• This answers "Verify measures restating", because the answer isn't in the reply. Summarising is the third most common use among 16–18 monthly users (45.5%). | text (`tutor_turn.md`), `plan.py`, step doc §B/§D | M | yes, if 05e is merged Wednesday morning | w2-09-01 ~; student panel 2 |
| 16 | **New label `ai_output_pasted`, as an optional check that is never penalised.**<br>• When the student says "ChatGPT said…" or pastes another AI's text, offer "Which part matches your notes?". If they skip it, record nothing, not even an ignore.<br>• If they raised the doubt themselves, score `ail_unprompted`.<br>• Why: if owning up earns a task, students stop saying "ChatGPT said", and the evidence disappears (student panel 3).<br>• The label is self-reported, so don't score it beyond `ail_unprompted` until the audit (rank 19) covers it. | text, `plan.py` (branch) | S–M | yes | w2-09-01 ~; student 3; researcher 2 (wave 2) |
| 17 | **Keep Ask language-light.** Add one line to the label instructions: score features regardless of spelling, grammar or language, so EAL students don't lose Ask points. | text | S | yes | w2-09-03 ✓; [09](09-safety-ethics.md) rec 11 |
| 18 | **Don't present self-label rates as error rates.**<br>• `conflict_flagged` fires only when the chatbot notices its own mistake, so it under-fires on confident errors.<br>• `pushback_changed` fires on corrections as well as on caving in.<br>• Never quote either as "how often the chatbot is wrong" or "how often it caves". | pitch, docs | S | yes | w2-02-38 ✓, -41 ✓, -42 ~ |
| 19 | **Self-label audit of about 20 scripted transcripts, one per failure mode.**<br>• (a) The student wrongly pushes back on a correct answer.<br>• (b) The student rightly corrects a wrong one.<br>• (c) With search on, a real link that doesn't contain the claim.<br>• (d) With search off, an invented reference.<br>• (e) The chatbot claims it searched when it didn't.<br>• Plus the new `summarise` and `ai_output_pasted` labels.<br>Score `pushback_changed`, `source_conflict` and the search label against the script, per chatbot. | `scripts/` (team) | M | maybe | w2-02-37 ✓ to -43 ✓; researcher 1–2 (wave 2) |
| 20 | **Split fabrication from misattribution, keyed on whether a search happened.**<br>• `ail_how_fabrication` fires on `source_conflict` with no search.<br>• A new part, `ail_how_misattribution`, fires on `source_conflict` after a search.<br>• Take search on/off from a school deployment setting, not from the chatbot. Today's `web_access` records what the chatbot *can* do, not what it did, and it is stored only on research turns.<br>• Until this lands, rec 3's either-way wording is the safe fallback. | build (`plan.HOW_TRIGGERS`, `tutor_turn.md`, course pack) | M | maybe | w2-02-30 ✓ to -36 ✓, -43 ✓ |
| 21 | **Settings for literacy parts only (needs code).**<br>• A `[literacy]` prior .30, `learn_rate` .05 and half-life 14 days, read only for literacy parts. Changing the global keys would move economics parts too.<br>• Then `ail_task` guess .35.<br>• Effect: the How AI works AUC rises to 0.80–0.93, depending on the simulated condition. The cost is slower recognition of a student who improves. | build, settings | M | maybe | w2-02-05 ~, -06 ✓, -09 ✓, -10 ✓ |
| 22 | **New label `request_type = draft` ("write it for me"): ask for "your point first".**<br>• Before the chatbot writes, ask for the student's one-line judgement or plan. Accept "skip" after one ask. No refusal.<br>• Draft counts are **never** shown to teachers (coordinator decision), and the progress page says so.<br>• Score a new part `ail_own_first` later. | text, `plan.py` | M | label maybe; scoring no | w2-09-01 ~, w2-09-10 ~; student 3, teacher 5 |
| 23 | **Ask scored as core + bonus.** Concept + context are the core; sources and reasoning are a bonus. Then "What was UK CPI in Feb 2025?" passes. | build | M | no | researcher 1 (wave 1) |
| 24 | **A grounded pushback label, instead of `pushback_correct` as the chatbot's own judgement.** The label asks: "does the changed answer match the plan's reference or the notes?". Use it only to change the opening line ("You were right to push"). After rec 3, the agreement check is safe to fire either way. | build | M | no | w2-02-40 ~, -41 ✓, -42 ~ |
| 25 | **Two wrong picks before a misconception shows as "held".** One guess (p = .25) shouldn't label a student. | build | S–M | no | researcher 3 (wave 1) |
| 26 | **Check the decay-clock asymmetry on economics parts.** On the course parts too, a part never answered correctly doesn't decay, while one answered right does, so rankings can invert. [06](06-settings-simulation.md) didn't test this. | sims, settings | M | no | w2-02-05 ~ |
| 27 | **A "feedback" moment.** When the student asks for feedback on their writing, ask "which suggestion would you reject, and why?". This needs a new mark-point design. | design | M | no | w2-09-01 ~ |

### Settings snippet (our choice, from the simulation; not an edit)
```toml
# 02 settings proposal for the 05e branch. Synthetic-student simulation; every number is our choice.
# ---- A. Settable now: keys the 05e code already reads (rec 2) ----
[literacy]
ask_min_features = 3            # was 2: coach Ask until a question would also score as correct (3 of 4 >= 0.67)

[bkt]
correct_share = 0.67            # unchanged. Do NOT lower to 0.5 (w2-02-03)

[bkt.evidence]
ail_question = { slip = 0.15, guess = 0.30 }     # was 0.20
ail_task = { slip = 0.10, guess = 0.15 }         # unchanged while literacy uses the 2-day half-life
ail_unprompted = { slip = 0.05, guess = 0.20 }   # was 0.10: one "I checked" gives 0.70, not 0.82
ail_how = { slip = 0.10, guess = 0.25 }          # unchanged

# ---- B. Needs code: literacy-only keys (rec 21) ----
[literacy.bkt]
prior = 0.30
learn_rate = 0.05               # was 0.10 (global): no-skill floor 0.06 instead of 0.12
[literacy.decay]
base_half_life_days = 14        # was 2 (global)
[literacy.evidence]
ignored = "missing"             # rec 4
# with B in place:  ail_task = { slip = 0.10, guess = 0.35 }
```

## Definition and competency model (ours, for the slide)
> **AI literacy, for a 16–18-year-old studying with a chatbot (our definition):** knowing when and how far to trust it, shown in what they do while they work. That means:
> - asking questions it can answer and that can be checked;
> - checking the claims that matter against a source they can name, then deciding to accept, revise or reject them;
> - recognising, when it fails, why it failed: a source that doesn't exist or doesn't say what was claimed, confidence that isn't evidence, a training cut-off, an answer that changes under pushback.

Anchors:
- AILit's distinction between literacy and tool use (w1-02-02 ✓);
- AILit Engage 2–3 and Manage 1 (w1-02-03 ✓, w1-02-05 ✓);
- the Curriculum and Assessment Review's "without becoming dependent" (w1-02-11 ✓);
- Long & Magerko's definition (w1-02-07 ✓).

| skill (as shown in progress) | what we observe in chat | grade | levels (new → developing → secure) | what we cannot observe |
|---|---|---|---|---|
| **Ask** | Names the idea; gives place and period; asks for sources; asks for reasoning; rewrites after coaching | b | vague → one feature missing → precise and checkable | Whether a better question came from understanding or from copying the feedback |
| **Verify** | Names the source, publisher and date; states what the source says; says whether it matched; *accept / revise / reject and why (proposed)*; checks unprompted; *finds what a summary missed in the notes (proposed)* | b, c | doesn't check → checks when asked → checks unprompted and justifies the decision | Whether they opened the link; checking done outside the chat |
| **How AI works** | Picks the right explanation in a 4-option check at the moment of a failure | a | no level: per part, "checked n, right m" (rec 6) | Explaining it in their own words (AILit Intermediate); transfer to other tools |
| *Just-show-me trend* (student only, **not scored**) | Share of "just show me" choices over 14 days | b | — | Whether a choice reflects judgement or tiredness |
| *Responsible use* (**coached, not scored**) | One line on what not to paste and on acknowledging AI use | none | — | everything |

**Evidence grades.**
- (a) The letter in a how-AI-works check, scored by the server.
- (b) Labels the chatbot gives the student's behaviour. There is no reliability data yet (rec 8).
- (c) What the student says they did.

A fourth source sits behind all of them: the chatbot's labels about *itself*, which decide when a moment fires. Examples are `source_conflict`, `pushback_changed`, `conflict_flagged` and `web_access`. They range from fairly reliable (reporting what the student said) to weak (judging its own correctness) (w2-02-41 ✓, -42 ~, -43 ✓).

**The model is narrow on purpose.** It assesses critical use of chatbot output for study, which is close to information literacy (researcher objection 5). Three honesty lines for the pitch:
- "Only the how-AI-works letters are scored by our server alone."
- "AILit levels aren't tied to age, so we don't claim 16–18-year-olds should be Advanced" (w1-02-01 ✓).
- "eduX never marks a student down for not using AI. It scores only moments that happen in the chat, and an ignored task is missing, not wrong."

**Not adopted: "Decide" as a fourth scored skill.**
- The student panel reads it as surveillance.
- A "hint" choice isn't proof of judgement (w1-02-05 ✓).
- The progress output shows `ask`, `verify` and `how_ai_works`, so the slide should use the same names.

### Where literacy moments come from
Today Ask and Verify fire only on research turns. Three of the four how-AI-works triggers (fabrication, agreement, confidence) fire on any turn; cutoff needs a research question.

UK 16–18s mostly use chatbots for things that have no moment yet. Among 16–18 monthly users (NLT 2025, an opt-in survey; w2-09-01 ~):
- homework help 70.4%;
- asking questions 69.7%;
- summarising 45.5%;
- writing answers to homework questions 33.1%;
- feedback on writing 32.2%.

The proposed moments (recs 15, 16, 22, 27) cover these uses. Of them, summarise is the cheapest and the most valid, because the notes it is checked against are already on the server. Surveys can't tell us how often each moment would fire. That needs counts from pilot logs.

## Framework crosswalk (compact)
Status: **main** = built on `main`; **branch** = built on the 05e branch, not merged; **—** = not built. Evidence grades (a), (b) and (c) are defined in the competency model above.

**OECD–EC AILit Framework (final, 2026): 4 domains, 19 competences** (w1-02-01 ✓)

| AILit competence (abridged) | eduX | coverage | status | grade |
|---|---|---|---|---|
| Engage 1: AI's role and influence | How AI works: agreement | partly | branch | a |
| Engage 2: describe how AI does tasks, correcting misconceptions | How AI works (4 parts; misattribution part proposed, rec 20) | Basic rung only (recognition); per-part results, no level (rec 6) | branch | a |
| Engage 3: accept, revise or reject outputs | Verify | to Intermediate; Advanced needs the justification tick (rec 5) | branch | b, c |
| Engage 4–7: recommenders, energy, bias, ethics | — | missing or out of scope | — | — |
| Create 1: build on own ideas | `constructive` label, try-first | proxy | main | b |
| Create 3: direct generative AI | Ask | partly | branch | b |
| Create 2, 4: prototyping; authenticity and IP | — | out of scope; coach only (JCQ) | — | — |
| Manage 1: decide whether to use AI for the task | "just show me" share (trend) | proxy | main | b |
| Manage 2: choose an approach by how systems work | How AI works: cutoff | partly | branch | a |
| Manage 4: monitor AI use | progress trends | proxy | main | b |
| Manage 3; Shape 1–4 | — | missing or out of scope | — | — |

**Count.**
- Fully covered: 0.
- Partly: 8. Five rest on the branch (Engage 1, 2, 3; Create 3; Manage 2) and three on `main`, as proxies (Create 1; Manage 1, 4).
- Missing or out of scope: 11.

**Other frameworks, briefly:**
- **UNESCO students' framework (2024): 12 competencies.** The ethics aspect is missing (w1-02-06 ✓). It also has a privacy competency ("Safe and responsible use"); we coach on privacy and never score it, because scoring would mean logging disclosures.
- **Long & Magerko (2020).** Their three-part definition maps evaluate → Verify, communicate → Ask, use as a tool → the "just show me" trend (w1-02-07 ✓).
- **Ng et al. (2021).** Partial on 3 of 4 aspects; ethics is missing (w1-02-08 ~, abstract only).
- **Digital Promise (2024).** Its "Evaluate" means weighing AI's costs and benefits to society, not fact-checking. Don't map Verify to it (w1-02-09 ✓).
- **AI4K12.** We touch Learning and Natural Interaction only (w1-02-10 ✓).
- **England.** The Curriculum and Assessment Review says to understand how AI works and to use it without becoming dependent on it, and places AI in Computing (w1-02-11 ✓). eduX complements that inside a subject. The DfE product safety standards (13 headed sections) ask for no final answers by default and for tracking offloading (w1-02-12 ✓).
- **JCQ / Ofqual.** They cover acknowledging AI use in coursework; 9EC0 is exam-only, so coach only (w1-02-13 ✓).
- **EU AI Act Art. 4.** It concerns the staff of providers and deployers, not pupils. Business plan only (w1-02-14 ~, secondary source for the 2026 amendment).

## How AI works content: failure modes and what each part teaches
Measured failure rates, and what they mean for each part (w2-02h). None of these studies measures learning, and none involves students. All are model behaviour ("prediction").

| part (trigger) | correct idea (content, not final wording) | wrong ideas to use (content) | measured failure it teaches |
|---|---|---|---|
| **fabrication** (today: `source_conflict`; later: `source_conflict` with no search) | Until rec 20 lands: a cited source may not exist, or may not say what was claimed. After rec 20: without a search, it can write a reference that looks real but isn't. | A reference with a journal and year is probably real. It copied a page that was later deleted. *(Not m2. Not "on purpose": that is an absolute cue, and the chatbot has no intent.)* | Search off: 55% (GPT-3.5) and 18% (GPT-4) of references invented in 2023 (w2-02-30 ✓). Search status not reported: GPT-4o 19.9% in 2025 (w2-02-31 ~, abstract; the per-topic 6–29% is from the press release only); 39.8% wrong or invented across 8 free chatbots (w2-02-32 ~) |
| **misattribution** (new, rec 20: `source_conflict` after a search) | With search on, it can cite a real page that doesn't say what it claimed. | If the link opens, the page probably backs up the claim. Words in quotation marks probably came from the linked page. | 74.5% of citations supported their sentence; 51.5% of sentences fully supported (w2-02-33 ~, abstract). GPT-4o with search invented no URLs, but about 30% of statements were unsupported (w2-02-34 ✓; it also gave no sources in over 20% of responses). Wrong article, syndicated copy or broken URL (w2-02-35 ✓). |
| **agreement** (`pushback_changed`) | A changed answer after pushback doesn't show which answer is right; check the notes. | If it keeps its answer when you push back, it was probably right. Quoting a source at it probably makes the new answer more reliable. | 43.52% of rebuttals moved it to correct, 14.66% to incorrect; citation-based rebuttals gave the most wrong-way flips (w2-02-38 ✓); flip rates 17.5–97.3% across 2026 models (w2-02-39 ~, abstract); anchored facts conceded only 1.3% of the time (w2-02-40 ~, abstract) |
| **confidence** (`conflict_flagged`, no `source_conflict`) | A sure-sounding tone isn't a reliable sign it's right. | Keep the current set, after the rec 3 cue pass. | Stated confidence is overconfident (w2-02-42 ~); ChatGPT signalled low confidence in 15 of 200 answers (w2-02-35 ✓) |
| **cutoff** (research, `asks_recent`, no search) | Without a search, it answers from training text that stops at a date. | Keep the current set, after the rec 3 cue pass. | Outdated information is among the major accuracy problems in news answers (w2-02-36 ✓) |
| *details* (later; no trigger label yet) | Real sources often come back with the wrong year, author or pages. | Wrong details mean the source is made up. | 24–45% of real references had wrong details (w2-02-30 ✓, -31 ~) |

**Rules for turning this into csv rows (rec 3).**
- The table gives content, not final wording. w2-02h's draft wording fails the cue check. Its correct options are longer than the distractors and end with full stops, and one distractor says "on purpose".
- Trim each set to one clause per option, with matched length, no full stops and hedging on both sides.
- Don't use "the new answer is usually right" as a distractor. In SycEval it is arguably true (w2-02-38 ✓).
- Don't quote a single sycophancy rate for "chatbots". Rates differ about fivefold across models and change with the kind of pushback (w2-02-39 ~).
- **Sort failures the way fact-checkers do.** Fact-checkers separate fabricated, misattributed, out-of-context and outdated claims (w2-02-45 ~, secondary sources). Map fabricated → fabrication, misattributed → misattribution, outdated → cutoff. Use the same words in feedback, so the skill carries over to news.
- **Humans misquote too.** 25.4% of quotations in medical journals don't reflect the cited source (w2-02-44 ✓). "Check that the source says it" is a general skill, not a trick for spotting AI. Don't imply that chatbots are as good as humans: the tasks differ.

## Scoring simulation on the 05e branch (simulation: synthetic students)
**Method.**
- Synthetic students in five groups (none, partial, strong, improver, gamer) go through the 05e literacy flow for 10 weeks.
- The replica reproduces the branch's `edux.learner` exactly: max difference 3.3e-16 over 17,500 weekly values, 0 of 250 runs mismatched. Four scripted sessions through the real `service.tutor_turn` give the predicted evidence rows (w2-02-01 ✓).
- Every truth-model number is our choice (`sims/literacy/README.md`).
- Ignoring is either unrelated to skill ("mcar": 30% for all) or related to it ("mnar": 50/30/15% for none/partial/strong).
- "Ever secure" means shown secure at any point, including in the chat straight after a moment.

**No-skill students shown "secure"** (N = 1,000 per group per cell; `sims/literacy/results/final.md` and `final.json`):

| variant | skill | 10% noise: weekly / ever | 20% noise: ever (mnar / mcar) | lenient 20%: ever (mnar / mcar) | strong secure, wk 3–10 (10%, mnar) |
|---|---|---|---|---|---|
| branch | Ask | 0.00 / 0.03 | 0.06 / 0.08 | 0.13 / 0.15 | 0.87 |
| branch | Verify | 0.00 / 0.02 | 0.05 / 0.06 | 0.07 / 0.10 | 0.68 |
| settable now (rec 2) | Ask | 0.00 / 0.01 | 0.03 / 0.03 | 0.05 / 0.07 | 0.89 |
| settable now (rec 2) | Verify | 0.00 / 0.01 | 0.02 / 0.02 | 0.04 / 0.06 | 0.61 |
| fuller proposal (recs 2, 4, 21) | Ask | 0.00 / 0.01 | 0.02 / 0.03 | 0.07 / 0.08 | 0.94 |
| fuller proposal (recs 2, 4, 21) | Verify | 0.00 / 0.00 | 0.01 / 0.01 | 0.03 / 0.03 | 0.70 |

"Lenient" means 20% false ticks and 7% missed ones. The weekly read is at or under 0.01 in every cell, for every variant.

**What the simulation shows.**
- **The weekly read is rarely wrong. The level shown in the chat is the risk** (w2-02-02 ✓). This is the same order as wave 1's 11–16% false "secure" (w1-02-32 ✓). Wave 1 measured the estimate after a run of moments; wave 2 measures weekly reads after decay. Rec 12 holds back "secure" in the chat.
- **`correct_share` 0.5 is catastrophic.**
  - 83% of no-skill students are ever shown Ask "secure", and 23% at a weekly read.
  - 96% of partial students are shown "secure".
  - None of the 1,740 grid configurations with share 0.5 passed the ≤5% limit (w2-02-03 ~).
- **Raising `ask_min_features` to 3 alone** gives 3.4% (mnar) and 4.6% (mcar) at 10% noise, and 8–10% at 20% noise (w2-02-03 ~). The two guess changes in rec 2 bring this down to the "settable now" row.
- **What rec 2 costs.** Strong students take longer to reach Verify secure: a median of 11.8 days instead of 9.8 when ignoring is tied to skill, and 15.8 instead of 11.7 when it isn't (w2-02-08 ✓).
- **Settings can't fix Verify** (w2-02-04 ~).
  - Evidence is scarce: about 8 Verify tasks in 10 weeks for a strong student and about 3 for a no-skill one (counted under the proposal settings at 10% noise).
  - A "gamer" who restates the reply scores a correct Verify moment 49% of the time, against 44% for a partial checker.
  - Requiring all 4 ticks removes gamers, and strong students too: across those grid configurations, strong students' median share secure was about 0.045 (max 0.40).
- **How AI works is inverted** (w2-02-05 ~).
  - The rollup of four parts never reaches secure for anyone in 10 weeks.
  - At week 8, AUC no-skill vs strong is 0.40 when ignoring is tied to skill and 0.44 when it isn't. It is 0.27–0.28 with ignored = missing.
  - **The cause:** `p_now` returns the undecayed estimate while a part's clock is unset (`learner.py:433-434`), and the clock starts only at a correct answer (`learner.py:692-695`). A part never answered right sits at its floor with no decay, while a part answered right decays below it.
  - A 14-day half-life lifts the AUC to 0.80–0.93, depending on the condition, but it doesn't remove the cause. Even without decay, strong students rarely reach secure at about 0.6 checks a week (`results/how_sweep.md`). So show per-part counts (rec 6).
  - **Economics parts use the same clock** (rec 26).
- **Decay is a trade-off.** Around the selected configuration (not the branch), a half-life of 30 days instead of 2 raised strong students' Verify secure share from 0.49 to 0.74, and partial students' from 0.03 to 0.09. No decay failed the false-secure limit (w2-02-06 ✓).
- **`learn_rate` makes lucky streaks dangerous.** At .10, a no-skill student's estimate floors at about 0.12, and two correct Ask moments then reach 0.79, which is secure. At .05, the floor is 0.06 and two correct moments reach 0.62 (w2-02-10 ✓, by calculation).
- **The fuller proposal changes Ask and Verify little.** Its gain is How AI works. Its cost: an improving student shows Ask secure at week 6 in 0.17 of cases, against 0.49 under the wave-1 quick fixes (w2-02-09 ✓). How fast a level should respond to real improvement is a product decision.
- **Selection rule.** The rule was fixed before the grid, with one change after the first look, which we flag: we added "gamer Verify secure ≤ 10%" and ranked by strong hold minus partial secure. Differences of about 0.02 between the top configurations are Monte Carlo noise.

## Ignored tasks: the missing-data rule
- **What large-scale tests do.**
  - **NAEP.** Blanks at the end of a block are "not reached" and are treated as if never presented. Earlier blanks are omits: a multiple-choice omit gets credit of 1/number of options (w2-02-11 ✓; this documentation covers the 2000–01 assessments).
  - **PISA.** Since 2015, not-reached items haven't been scored as wrong; the share not reached feeds the background model (w2-02-12 ~). That omits are still scored wrong is only implied. Robitzsch reports that country means can differ across missing-data treatments, by about 5 points on average (range 1.5–12.5). He argues that validity, not model fit, should decide, and that a rule test-takers can manipulate is unfair.
  - **The rest of the literature, from abstracts only.** Neither "missing" nor "wrong" is safe when skipping is related to skill (w2-02-13 ~). Ignoring missing responses was still enough for parameter estimation in one competence-test study (w2-02-14 ~). Treating disengaged responses as uninformative improved fit and validity (w2-02-15 ~).
- **An ignored eduX task is closer to a not-reached item than to an omit.** It arrives unasked, mid-homework, and the session can end before the student replies. The branch already drops a task unscored when the session ends.
- **Rule (rec 4).** Record a `literacy_ignored` engagement event, not evidence. Show "tasks done: n of m" beside the level. Score attempts. In the pilot, check whether the ignore rate relates to level.
- **The numbers barely depend on it.** At a 14-day half-life, strong hold was 0.84 with missing vs 0.81 with zero, partial secure was 0.10 vs 0.07, and no-skill false-secure was unchanged (w2-02-07 ✓). At 30 days: 0.95/0.78 vs 0.94/0.74. So choose on validity.
- **Equity.** About 30% of 16–18s don't use generative AI at all (w2-09-01 ~). FSM pupils use it as much as others but say they "just copy" more often (30.0% vs 24.0%; w2-09-03 ✓). No evidence must never read as low literacy. Don't profile students by FSM.

## Validity argument (Kane-style, one slide)
The structure follows Kane (2013) and the five sources of evidence in the AERA/APA/NCME Standards (w1-02-33 ~).

| claim (inference) | evidence we have | threats we know of | evidence we'd gather |
|---|---|---|---|
| **Scoring:** a tick or letter means the student did it | Fixed server rules; the how-AI-works letter is scored by the server; a simulation checked against our real code (w2-02-01 ✓) | Chatbot labels unchecked; Verify can be met by restating (w2-02-04 ~); "opened" can't be seen; distractor cues; ignored = 0 on the branch | κ per feature vs two humans (rec 8) |
| **Opportunity:** moments fire when they should | Triggers in `plan.HOW_TRIGGERS` | Triggers are the chatbot's self-labels: `web_access` records capability, not action; `conflict_flagged` under-fires on confident errors; models claim tool use falsely (w2-02-41 ✓, -42 ~, -43 ✓). So opportunity rates may differ by chatbot. | Scripted audit of five failure modes, per chatbot (rec 19); search taken from a school setting (rec 20); opportunity rate reported per host |
| **Generalisation:** enough moments for a stable level | Spearman–Brown: about 12 moments for .70 (w1-02-31 ✓); simulated weekly reads rarely wrong (w2-02-02 ✓) | In-chat "secure" after a lucky moment; Verify about 8 tasks in 10 weeks for a strong student (w2-02-04 ~); How AI works ranks students backwards (w2-02-05 ~) | `n_moments`, "not enough evidence" and "provisional" (rec 12); split-half reliability of Ask in a pilot |
| **Extrapolation:** the level reflects AI literacy beyond eduX | How AI works overlaps GLAT's hallucination and cutoff items (w1-02-23 ✓); Ofcom shows confidence isn't skill (w2-09-04 ✓) | A narrow construct, close to information literacy; Ask rewards a prompt ritual; GLAT probably doesn't cover misattribution | Convergent r with GLAT or AILIT-S and one COR task (N ≥ 62; target r ≈ .3–.4); think-aloud with 5 students |
| **Use:** coaching on the level helps and doesn't harm | Formative only; answers never withheld; ignored = missing (rec 4); no per-student levels for teachers (coordinator) | A level that decays in days reads as "lost the skill" (w1-02-34 ✓); "held" after one wrong pick; honesty costs a task (student 3) | Pre/post AILIT-S in a pilot; fairness by group and by chatbot |

Slide wording (our draft): *"We don't claim a validated test. We claim a validity argument: fixed scoring rules, labels checked against humans (κ = __), levels shown with evidence counts, a simulation checked against our real code, and a pilot designed to correlate with an external AI-literacy test."*

## Reliability maths in brief
All of this is first-principles calculation (w1-02-31 ✓, recomputed by the verifier).
- **One moment.** Back-solving from GLAT (α .80, 20 items) and the Newton's Playground test (α .72, 12 items) gives ρ₁ ≈ .17. This holds only *if* a moment is as good as a carefully built MCQ item.
- **Moments needed** (Spearman–Brown):

  | ρ₁ | for .60 | for .70 | for .80 |
  |---|---|---|---|
  | .17 | 8 | 12 | 20 |
  | .12 (with label noise) | 11 | 18 | 30 |
- **Attenuation.** With reliabilities of .6 and .6 and a true correlation of .7, the observed r is about .39. That is why r ≈ .4 counts as a good result.
- **Pilot size.** r = .35 needs N ≈ 62; r = .40 needs N ≈ 47 (power .8, α .05).
- **Label noise.** ρ₁ × r_rater ≈ .17 × .70 ≈ .12, which gives the second row. Treating κ as a reliability coefficient is an approximation (our choice).
- **Agreement-study precision.** κ = .7 on 40 items gives a 95% CI of about ±.22.
- **In time.** Strong students get about 26 Ask moments and 11–14 Verify moments in 10 weeks (simulation, our usage assumption of 2–3 research questions a week). A reliable Verify level takes most of a term.

## Scoring problems in the 05e branch
We checked each problem with `git -C /home/vishnu/edux26 show origin/build/05e-literacy-coaching:<path>`. The wave-2 column shows what the simulation added.

| # | problem | what the branch shows | wave 2 | fix |
|---|---|---|---|---|
| 1 | Ask: `ask_min_features = 2` contradicts `correct_share` 0.67 | A 2-feature question counts as wrong for Ask, yet the student is moved on to Verify | Lowering the share is catastrophic; raising features to 3 works with the guess changes (w2-02-03 ~, -08 ✓) | rec 2; rec 23 later |
| 2 | An ignored task is recorded as 0 | `_literacy_followup` and `_how_ai_works` record 0 after one re-ask; a session end drops the task unscored | The numbers barely move; NAEP and PISA back "missing" (w2-02-07 ✓, -11 ✓, -12 ~) | rec 4 |
| 3 | Verify measures restating | Tick 1 can't be observed; ticks 2–4 can be met by repeating the reply; the source is from the pack's trusted list | No setting separates a gamer from a partial checker (w2-02-04 ~) | recs 5, 15 |
| 4 | Triggers don't fit their items | Fabrication fires on `source_conflict` with no search condition; `web_access` is a capability and is stored only on research turns; agreement fires on `pushback_changed` whether or not the student was right; one wrong pick marks a misconception "held" | With search on, misattribution is the common failure (w2-02-33 ~, -34 ✓); many changes are corrections (w2-02-38 ✓) | recs 3, 7, 20, 24, 25 |
| 5 | Give-away wording | The literacy distractors use absolute cues while the correct options hedge; lengths are matched, with no full stops | — | rec 3 |
| 6 | **How AI works rollup ranks students backwards (new)** | The decay clock starts only at the first correct answer (`learner.py:433-434, 692-695`) | AUC 0.40 (mnar) / 0.44 (mcar); never secure (w2-02-05 ~) | rec 6; recs 21 and 26 later |

**Also on the branch:**
- The 05e step doc still carries the withdrawn Khanmigo line (w1-09-08 ~). No report's ranked list owns the fix now: it is a one-line team edit to `docs/build/steps/05e`, and the deck must not use the line ([pitch-notes](pitch-notes.md)).
- Progress shows a level per skill, with no `n_moments`.
- `[literacy]` has no separate half-life.
- Each how-AI-works part gets at most one check per session.

## Later (not before Thursday; for the business plan and Q&A)
- **Convergent-validity pilot, preregistered.** At least 62 consenting students, with school consent and a DPIA.
  - How AI works vs GLAT or AILIT-S.
  - Verify vs one COR task, scored by two humans.
  - Ask vs a human-rated question-writing task.
  - Expect r ≈ .3–.4 (w1-02-21 ✓, w1-02-22 ✓, w1-02-23 ✓, w1-02-24 ~, w1-02-27 ✓).
  - Add a misattribution item, since GLAT probably doesn't cover it.
- **Pilot log counts.** How many `research`, `summarise`, `draft` and `ai_output_pasted` moments a student generates per week, per chatbot. Whether ignoring relates to skill (mcar vs mnar). Whether students disclose pasted AI text less once disclosure earns a task.
- **Per-chatbot audit and logging of which chatbot labelled each exchange** (fairness, measurement invariance; w1-02-30 ~).
- **Think-aloud with 5 students.** An explain-back after a how-AI-works check, to reach AILit Engage 2 Intermediate.
- **IRT calibration of the how-AI-works items.** It needs hundreds of responses per item.
- **Ask behaviour from the sycophancy work.** Teach "state the question, don't argue the answer" (w2-02-40 ~).

## Considered and rejected
- **Lowering `correct_share` to 0.5** to match `ask_min_features = 2`. It is catastrophic in simulation (w2-02-03 ~).
- **A stricter Verify (all 4 ticks).** It removes strong students as well as gamers (w2-02-04 ~).
- **No decay for literacy parts.** It fails the false-secure limit, and partial and gamer students end secure 20–34% of the time (w2-02-06 ✓).
- **Changing the global prior, `learn_rate` or half-life on Wednesday.** That would move the economics parts too.
- **`ail_task` guess .35 without the longer half-life.** Strong students then need a median of 26 days to reach Verify secure.
- **Fractional credit (1/4) for an ignored check.** In BKT a score below the threshold counts as wrong, so this equals 0.
- **Having the chatbot label which kind of source error happened, or judge whether its own change was right.** That is self-diagnosis, the weak case (w2-02-41 ✓, -42 ~, -43 ✓).
- **Kadavath-style P(True).** It needs token probabilities, which eduX never sees.
- **Dropping the agreement check.** Giving way under pushback is real and large (w2-02-37 ✓, -39 ~). The trouble was the framing.
- **Quoting one sycophancy rate, or the Tow Center's "153 of 200 wrong".** The single rate misleads (w2-02-39 ~). The Tow Center article's figures don't reconcile.
- **A "draft" or "pasted" count in the teacher view.** Excluded by coordinator decision. It also makes honesty cost the student.
- **Summarise checks against articles eduX doesn't hold.** The task can't be done, and it teaches that checking is pointless (student 2).
- **Self-report scales (MAILS, SNAIL, AILQ) as the convergent check.** MAILS correlates only r = .21 with a knowledge test (w1-02-25 ✓). Self-report vs performance r = .055 (w1-02-15 ✓, a preprint).
- **"Stealth assessment" as our label.** Ask and Verify are overt, and the pitch bans the word. Use "embedded".
- **Claiming reliability from BKT posteriors, generating agreement-study messages with the model under test, using real students before Thursday, putting GLAT items in the product, scoring ethics or privacy, mapping 16–18s to AILit "Advanced" or Verify to Digital Promise's "Evaluate", "Decide" as a scored skill.** Reasons as in wave 1. Each is either circular, unconsented or unsupported (w1-02-01 ✓, w1-02-09 ✓).

## Panel objections this report answers or leaves open
Status words: **answered** = a fix is built or a document answers it; **recommended** = a fix is recommended but not built; **partly**; **open**.

| objection | status |
|---|---|
| Judges (w2) 1: the demo corrects a true belief (m2) | **Partly.** Recs 3 and 7 retire m2 and rewrite the options. Demo-plan shots 4c–4d and 01 rec 5's seed still use m2, and their owners must change them. |
| Researcher (w2) 1: triggers are a biased sample of self-labels | **Recommended.** Recs 19 and 20 (maybe), rec 18 for the wording. |
| Researcher (w2) 2: new moments add self-labels | **Recommended.** Rec 16 doesn't score beyond `ail_unprompted` until the audit (rec 19). Rec 15 answers "Verify measures restating" for summaries of course material. |
| Researcher (w2) 3: mixed bases; motivated by self-report | **Recommended.** Rec 13: Ofcom's performance result first; NLT bases stated. |
| Researcher (w2) 5: missing data and evidence counts unchanged | **Recommended.** Recs 4 and 12; the threshold of 3 is low, so "provisional" runs to 8. |
| Researcher (w2), wording: "stealth" | **Answered** in wording here (rec 9). The word stays out of all our text. |
| Student (w2) 2: summarise checks against your notes, not mine | **Recommended.** Rec 15 fires only on course material and otherwise gives an unscored prompt. |
| Student (w2) 3: why would I say "ChatGPT said"? Draft counts to the teacher | **Recommended.** Rec 16 makes the check optional and never penalised. Draft counts are never shown to teachers (coordinator; rec 22). |
| Teacher (w2) 5: the draft moment still writes the 25-marker | **Partly.** The teacher-view conflict is settled (no draft counts). Ending the draft moment in a plan skeleton rather than prose is open; it is for [05](05-product-features.md). |
| Researcher (w1) 1: scoring contradicts coaching; ignored = 0 | **Recommended.** Recs 2 and 4, with simulation support. Not made on the branch yet. |
| Researcher (w1) 2: Verify measures restating | **Recommended.** Recs 5 and 15. The simulation shows settings can't fix it. Tick 1 stays unobservable; say so. |
| Researcher (w1) 3: items don't fit their triggers; cues; "held" after one click | **Recommended.** Recs 3, 7 and 20 before Thursday or maybe; recs 24 and 25 later. |
| Researcher (w1) 4: the assessed system writes its own evidence | **Partly.** Rec 8 covers labels of student messages; rec 19 covers self-labels. Neither is done. |
| Researcher (w1) 5: the claim outruns the construct | **Answered** in wording: a narrow, named construct; "embedded"; evidence counts (recs 1, 9, 12). |
| Student (w1) 2: "I'd never see the literacy part" | **Partly.** How-AI-works checks fire on any turn. Summarise and pasted-text moments are recommended (recs 15, 16). |
| Student (w1) 3: MCQs easy to game; "I checked" makes Verify secure; ignored = 0 | **Recommended.** Recs 2, 3 and 4. |
| Student (w1) 4: feels like being watched | **Partly.** The trend is unscored and shown to the student only. Teachers see no per-student literacy data (coordinator). |
| Judges (w1) 3: "Why believe a 'secure' Verify?" | **Partly.** A validity slide, maths and a simulation exist. The branch settings are unchanged until rec 2. |

## Findings
| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-02-01 | AILit final (2026): 4 domains, 19 competences; levels not tied to age | official document | primary and secondary, international | policy | ✓ |
| w1-02-02 | AILit: AI literacy differs from tool use | official document | as above | policy | ✓ |
| w1-02-03 | Engage 3 progression to justify accept / revise / reject | official document | as above | policy | ✓ |
| w1-02-04 | Engage 2: describe how AI works | official document | as above | policy | ~ links to Knowledge 1.3 and 1.4; 3.2 goes with Engage 3–4 |
| w1-02-05 | Manage 1: decide whether to use AI; Manage 4: monitor use | official document | as above | policy | ✓ |
| w1-02-06 | UNESCO 2024: 12 competencies; privacy under "Safe and responsible use" | official document | school students, international | policy | ✓ |
| w1-02-07 | Long & Magerko: evaluate / communicate / use | theory | general learners | policy | ✓ |
| w1-02-08 | Ng et al. 2021: four aspects | theory | mixed | policy | ~ abstract only |
| w1-02-09 | Digital Promise "Evaluate" = societal costs and benefits | practitioner | PK–12, US | policy | ✓ |
| w1-02-10 | AI4K12 Five Big Ideas | practitioner | K–12, US | policy | ✓ |
| w1-02-11 | CAR (Nov 2025): understand AI, use it without dependence | official document | England | policy | ✓ |
| w1-02-12 | DfE GenAI product safety standards | official document | England | policy | ✓ (13 headed sections) |
| w1-02-13 | JCQ: unacknowledged AI use is malpractice | official document | England KS4/KS5 | policy | ✓ |
| w1-02-14 | EU AI Act Art. 4 duty on providers and deployers | official document | EU | policy | ~ secondary sources for the 2026 amendment |
| w1-02-15 | Self-report vs performance r = .055 | meta-analysis (preprint) | workplace adults | prediction | ✓ |
| w1-02-20 | Newton's Playground r = .22–.40 with a pretest | correlational | 167 US grade 8–9 | prediction | ✓ |
| w1-02-21 | Use Your Brainz game-based embedded assessment r = .40 / .41 | correlational | 55 US 7th graders | prediction | ✓ |
| w1-02-22 | Physics Playground r = .36 / .40 | correlational | US students, n = 263 | prediction | ✓ |
| w1-02-23 | GLAT: 20 items, α = .80; predicts AI-assisted task performance | correlational | HE students | prediction | ✓ |
| w1-02-24 | AILIT-S: 10 items, under 5 min | correlational | university students | prediction | ~ abstract only |
| w1-02-25 | MAILS self-report r = .21 with a knowledge test | correlational | 120 German adults | prediction | ✓ |
| w1-02-26 | AILQ; Chiu et al. 25 MCQs | correlational | Hong Kong secondary | prediction | ~ abstracts only |
| w1-02-27 | COR: under 2% Mastery on four of six tasks | correlational (descriptive) | 3,446 US high-school students | learning (performance level) | ✓ |
| w1-02-28 | GPT-4 few-shot marking κ = .70 vs human .75 | correlational | ages 5–16 | prediction | ~ abstract only |
| w1-02-29 | LLM agreement varies by task | correlational | mixed | prediction | ~ Chamieh confirmed; the Jiang & Bosch .677 not verified |
| w1-02-30 | Autoscoring meta-analysis: decoder LLMs agree less | meta-analysis (preprint) | mostly K–12 | prediction | ~ 890 = configurations × 10 items; −0.37 on the Fisher-z scale; bias from one illustrative output |
| w1-02-31 | ρ₁ ≈ .17; about 12 moments for .70 | theory (calculation) | n/a | prediction | ✓ |
| w1-02-32 | BKT simulation: 2 correct → secure; one unprompted → 0.82; 11–16% false secure | simulation (synthetic students) | 20,000 per cell | prediction | ✓ |
| w1-02-33 | Kane's argument-based validation; the Standards' five sources | theory | n/a | policy (method) | ~ abstracts and secondary |
| w1-02-34 | Literacy parts use the 2-day half-life: about 0.22 a week after one success | theory (design review) | n/a | prediction | ✓ |
| w2-02-01 | The replica matches the 05e learner exactly; the flow matches `tutor_turn` | simulation (software check) | synthetic students | prediction | ✓ |
| w2-02-02 | Branch: weekly false secure ≤1%; ever Ask-secure 3% / 6% / 13% (10%, 20%, lenient) | simulation | synthetic students | prediction | ✓ |
| w2-02-03 | `correct_share` 0.5: 83% no-skill ever secure; min features 3: 3.4–4.6% at 10% noise | simulation | synthetic students | prediction | ~ 4.6% in mcar, not "3–4%"; 8–10% at 20% noise |
| w2-02-04 | Verify scarce; gamer 49% vs partial 44% correct; 4-of-4 ticks blocks strong students | simulation | synthetic students | prediction | ~ rates under the proposal settings; "0.04" is a median of about 0.045 across configurations (max 0.40) |
| w2-02-05 | How AI works never secure; AUC 0.40 because of the decay clock; 14-day half-life helps | simulation + code | synthetic students | prediction | ~ 0.40 mnar, 0.44 mcar; 14 days gives 0.80–0.93 by cell |
| w2-02-06 | Half-life 2 → 30 days: strong Verify hold 0.49 → 0.74, partial 0.03 → 0.09 | simulation | synthetic students | prediction | ✓ (around the selected configuration, not the branch) |
| w2-02-07 | Ignored = missing vs 0 changes the metrics little | simulation | synthetic students | prediction | ✓ (14-day configuration) |
| w2-02-08 | Settable-now variant: no-skill ever ≤5% (mnar); 7% / 6% under lenient mcar | simulation | synthetic students | prediction | ✓ (Verify median days 11.7 → 15.8 in mcar) |
| w2-02-09 | The full proposal mainly helps How AI works; slower for improvers | simulation | synthetic students | prediction | ✓ |
| w2-02-10 | `learn_rate` .10 floor 0.12 → two correct = 0.79; .05 floor 0.06 → 0.62 | theory (calculation) | n/a | prediction | ✓ |
| w2-02-11 | NAEP: not reached = never presented; MC omit = 1/k credit | official document | US students | policy (method) | ✓ |
| w2-02-12 | PISA since 2015 doesn't score not-reached items as wrong; treatment choice matters | simulation + case study | PISA 2018, 15-year-olds | policy (method) | ~ omits-wrong only implied; means "can differ", about 5 points on average |
| w2-02-13 | Deterministic missing rules are problematic in low-stakes surveys | simulation + correlational | international students | policy (method) | ~ abstract only |
| w2-02-14 | Missingness related to ability, yet ignoring it was sufficient | correlational + simulation | German competence tests | policy (method) | ~ abstract only; "parameter estimation" generally |
| w2-02-15 | The effort-moderated IRT model beats 3PL on fit and validity | correlational + simulation | US university students | prediction | ~ abstract only |
| w2-02-30 | ChatGPT 2023: 55% / 18% references fabricated; 43% / 24% of real ones with errors | correlational (audit) | model outputs, no search | prediction | ✓ |
| w2-02-31 | GPT-4o 2025: 19.9% fabricated; 45.4% of real ones with errors | correlational | model outputs | prediction | ~ per-topic figures from the press release only |
| w2-02-32 | 8 free chatbots: 39.8% of references wrong or fabricated | correlational (audit) | model outputs | prediction | ~ abstract only |
| w2-02-33 | Generative search: 51.5% of sentences fully supported; 74.5% citation precision | correlational (audit) | 2023 search engines | prediction | ~ abstract only |
| w2-02-34 | GPT-4o with search: no invented URLs, about 30% of statements unsupported | correlational (audit) | medical questions | prediction | ✓ (no sources in over 20% of responses) |
| w2-02-35 | AI search tools misidentified the source over 60% of the time; ChatGPT hedged in 15 of 200 | practitioner (audit) | US news excerpts | prediction | ✓ |
| w2-02-36 | EBU/BBC: about a third of answers had serious sourcing problems | practitioner (expert review) | 18 countries incl. UK | prediction | ✓ |
| w2-02-37 | Under "are you sure?", models change answers 32–86% of the time | correlational (benchmark) | 2023 models | prediction | ✓ |
| w2-02-38 | SycEval: 43.52% of changes to correct, 14.66% to incorrect; citation rebuttals worst | correlational (benchmark) | 2024–25 models | prediction | ✓ |
| w2-02-39 | 2026 models abandon correct answers 17.5–97.3% of the time | correlational (benchmark) | 2026 models | prediction | ~ abstract only |
| w2-02-40 | Yielding depends mostly on the task; anchored facts conceded 1.3% | correlational (benchmark) | 2026 models | prediction | ~ abstract only; preprint |
| w2-02-41 | Self-correction without feedback doesn't help, and can hurt | correlational (benchmark) | GPT-3.5 | prediction | ✓ |
| w2-02-42 | Verbalised confidence is overconfident | correlational (benchmark) | 2023 models | prediction | ~ abstract only; which AUROC is black-box is inferred |
| w2-02-43 | Models falsely claim tool use (o3 5.0–12.8%) | practitioner (red team) | adversarial prompts | prediction | ✓ (narrow slice; the authors warn) |
| w2-02-44 | 25.4% of medical-journal quotations don't reflect the source | meta-analysis | published articles | prediction | ✓ |
| w2-02-45 | Fact-checkers separate fabricated, misattributed, false-context and outdated claims | practitioner | public misinformation | policy | ~ secondary copies only |
| w2-09-01 | NLT 2025: 70.6% of 16–18s have used generative AI; summarise 45.5% of monthly users | correlational (opt-in survey) | UK 16–18, about 4,900 | adoption | ~ 52.0% weekly is a share of users |
| w2-09-02 | 58.5% of 16–18s say they check; 10.0% "just copy" | correlational (self-report) | as above | engagement (self-report) | ✓ (base: those who had heard of generative AI) |
| w2-09-03 | FSM: equal use, more copying (30.0% vs 24.0%) | correlational | UK 13–18 | adoption / engagement | ✓ |
| w2-09-04 | Ofcom 2026: 25% of confident teens failed to spot an AI image | official document | UK 8–17 | prediction (confidence vs test) | ✓ |
| w2-09-10 | Revising with ChatGPT improved the essay but not knowledge gain | RCT (lab) | 117 university students | learning vs product | ~ abstract only; comparison groups were a human expert, writing analytics and no tool |

