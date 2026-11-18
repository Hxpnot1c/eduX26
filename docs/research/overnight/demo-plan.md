# Demo plan: video storyboard, live expo script, checklist

Waves 1–3. **Wave 3** replaces Plan A with an "as captured" shot list from a scripted rehearsal on the 05e branch (scout note `work/w3/w3-07.md`, blind verifier marks `work/w3/verify-P.json`; scripts and raw captures in [`sims/demo-05e/`](sims/demo-05e/), per-turn digest in [`sims/demo-05e/captures/DIGEST.md`](sims/demo-05e/captures/DIGEST.md)). It adds the pre-filming build fixes (§F), a section for when a judge types their own question (§B), and the wave-3 judge and student panel (`work/w3/panel-judges-student.md`) and the MCQ audit (`work/w3/w3-05.md`). Wave 2 brought the plan into line with [02](02-ai-literacy-assessment.md) (m2, per-part How AI works counts), [06](06-settings-simulation.md) (three bugs, the pitch chart) and [05](05-product-features.md) (teacher view, routes). Wave-1 sources: `work/w1/w1-07.md`, `work/w1/verify-C.json`, the wave-1 panels, and the captures in `sims/demo-captures/` (synthetic demo students, example pack, taken on an earlier build of `main`). Economics content issues are in [04](04-economics-education.md).

Deliverables: a 2–3 minute video (due Thursday 19 November, 23:59) and a live demo at the expo on 20 November, where judges visit teams. The official rules page publishes no rubric or weights, so the criterion tags below follow the judges panel's reading: **D** = defining AI literacy, **A** = assessing it, **L** = learning value, **F** = feasibility and who it helps.

Step 05e (Ask, Verify, How AI works) is **built on its branch (`build/05e-literacy-coaching`), not merged** to `main`.

> **Wave 6 update (read first; it overrides older numbers below).** The build is now the patch series in [wednesday-build-list.md](wednesday-build-list.md): 0001–0004, 0006–0008, 0011, 0009b, 0010b (if on time); 0005 optional. All results are simulation (synthetic students or scripted turns, example pack).
> - **Verify after 4c reads 0.740 with 0009b, not 0.748** (developing in all eight rehearsal takes; w6-planA ✓). Same word on screen. Never say a number on camera; if asked, "developing: one piece of evidence".
> - **With 0009b, a reported dead link or mismatch can't make Verify secure on its own** until the student has done one real check (w6-c2b-1 ✓). A second report in a retake stays developing.
> - **With 0010b, a course part can't go secure from MCQs picked straight after teaching** (w6-c1b-1 ✓). Such a part reads **developing; an explain-back makes it secure**. Shot 5 shows only first moves, so it is unaffected. No line in this plan says a part goes secure that way; keep it so.
> - **With 0011, the `ped_definition` check has new distractor wording** ("The slope of the demand curve is PED, so it is the same all along it"; "PED measures how far the price changes when the demand changes"). It appears in shot 5 (`demo-weak`), the `then_ped` take's prerequisite question and the expo script below. Re-capture shot 5 and reprint the line card after 0011. The literacy options in 4c are unchanged.
> - **Mock-ups:** use [`mockups/teacher-view.html`](mockups/teacher-view.html) and [`mockups/student-progress.html`](mockups/student-progress.html) for any teacher-view or design-progress picture ([mockups/README](mockups/README.md)). Keep the "Mock-up · illustrative data · not a live feature" tag in the crop, use the README's caption, and **say "this is the design" over anything not built**. Never use the student-progress mock-up in place of the live 4d shot.

## Summary

- **Plan A is now an "as captured" shot list: simulated on the 05e branch; confirm in the Wednesday claude.ai dry run.** A script played the chatbot's side against the branch's own server. Every plan arrived on cue (Ask task, Verify task, `source_conflict` plus a 4-option how-AI-works check, the misconception named, the AI-literacy record), but only when the chatbot sends the right labels (w3-07-c1 ✓). Which labels Claude really sends is the open question for Wednesday.
- **The worst break: ordinary words pull economics into the literacy episode.** On the example pack, "give", "link", "ONS", "first", "cost", "different" and "shows" each match a course part. "Please give me sources" made the sources OBR and IFS (tax) for an inflation question, and the reply to the how-AI-works answer added a PED prerequisite quiz (w3-07-c3 ✓). The video uses a line card of probed, clean lines. The expo can't, because judges type their own words (panel-judges w3 #2): this is MUST fix 1 (§F).
- **Verify scoring punishes the behaviour it assesses.** If the chatbot ticks only "opened" and "said whether it matched" for a dead page, Verify falls 0.30 → 0.14. Moving on while a Verify task waits records a 0 (same fall). A mismatch answer that states what the page says raises it to 0.748, just under "secure" (w3-07-c5 ✓; the 2-of-4 depends on which ticks the chatbot sends). These are MUST fixes 2–3. Until they land, 4c uses the mismatch line, sent as the Verify answer, and no Verify record is shown after a dead-page take.
- **Seven MUST build fixes before filming, in priority order** (§F): the focus fix; reported mismatch or dead page counts as Verify met; moving on scores nothing; m2 out of the option sets; no node description as an MCQ option; the three crash and loop bugs; per-part How AI works counts. Each has an on-camera workaround if it misses the gate. The gate doesn't require all seven.
- **The economics MCQs give the answer away, and worse than wave 1 measured.** On the current build, the correct option is the node description (a topic label) in 7 of 9 parts, because `edux/plan.py:376` falls back to it when a part has no mark point. The correct option is the longest in 7 of 9 parts (w3-05-08 ~, verifier: 7, not 6). Wave 1's "shortest, no full stop" is also true, for a different option source: where a part has points, the key is a short fragment with no full stop ([04](04-economics-education.md)); where it has none, the description fallback makes it the longest (w3-05).
- **Feasible, with one tight margin.** The branch's check script passes 74/74 on both settings copies (w3-07-c6 ✓). Median server time was 7–10 ms on our laptop runs (machine-dependent). The largest `tutor_turn` result is 2,318 of 2,400 characters by the server's own count, about 80 characters spare (w3-07-c2 ~). Pack and code fixes that lengthen text can push it over, so re-run the rehearsal after every fix.
- **Lead with AI literacy; two students, not three.** The 72-s literacy episode leads; PED is a 20-s supporting shot. In "same question, different students", two of the three demo students get the same first move. If any shot or slide uses Ofcom's "1 in 4", caption it "AI-made images": it was an image test, not checking a chatbot's claim (w2-09-04 ✓; panel-judges w3 #3).
- **Age and expo.** claude.ai consumer plans are 18+ (w1-05-02 ✓): film on an adult team member's account, captioned. At the expo: one live student, one talker and one driver, a reset and new chat between judges, an honest script for judges' own questions (§B), and a four-rung fallback ladder (w1-07-07 ✓, w1-07-08 ~).

## Ranked recommendations

Ranks 1–14 keep their wave-1 and wave-2 numbers. Ranks 15–21 are new in wave 3.

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on |
|---|---|---|---|---|---|
| 1 | **Gate at 18:00 Wednesday (our choice): Plan A or Plan B.** Plan A needs all three: the 05e build fixed (merged to `main`, or the branch build itself, provided the expo runs that same build); its `check_mcp.py` passing with no OVER BUDGET line in a rehearsal re-run (rec 20); and one end-to-end dry run of the literacy episode in claude.ai on the adult account, with the labels checked (rec 16), without a retake. The MUST fixes (§F) are not part of the test; any that missed it switch on their workaround. | team decision | S | yes | panel-judges Q3; w3-07-c1 ✓, -c6 ✓ |
| 2 | **Fix the MCQ correct option before recording** (wave 3). Never use a node description as an option. Keep the mark point as the key (commit `f0a1c36` on `main` chose the point over the exemplar on purpose), matched to its distractors in length and punctuation. Skip the MCQ when a part has no points, and add mark points for the demo parts (`ped_definition`, `ped_formula`, `ped_values`, `tax_incidence_split`). A wave-4 scout is testing this (in progress). This is MUST fix 5. | build, pack | S | yes | w3-05-08 ~; panel-judges w3 #5; panel-student w3 #4 |
| 3 | **Film on an adult team member's account and caption every chatbot shot**: "Filmed on an adult team member's account. Students under 18 would use a school-managed chatbot." Demo students are synthetic, and the video says so. | video, expo | S | yes | w1-05-02 ✓; panel-judges #4 |
| 4 | **Shoot the storyboard below (Plan A or B), with the literacy episode at 60–75 s.** Keywords on screen, narration as the main channel, no music under speech, and a separate full-caption track. | video | M | yes | panel-judges; w1-07-01 ✓, -02 ~, -04 ~, -05 ~ |
| 5 | **Reset ritual for every take and every judge:** `python -m edux.cli seed-demo --reset`, then a **new chat**. A second take in the same session gets `source_conflict` but no fabrication check, and option letters reshuffle every take. | checklist | S | yes | w3-07-09 (simulation, not verified) |
| 6 | **Rewrite the `ped_definition → ped_formula` intuition note as an everyday hook.** Today it reads as a prerequisite reminder, and the intuition question looks like a formula quiz. | pack `edges.csv` | S | yes | captures; scout note w1-07 |
| 7 | **Record two offline fallback clips** (about 60 s each): the PED run and the literacy episode (Plan A) or the progress shot (Plan B). Keep them on the laptop desktop and on a phone. | expo fallback L2 | S | yes | w1-07-07 ✓ |
| 8 | **Rewrite `docs/demo-script.md`** to match steps 05d/05e and the live script below. | team doc | S | yes | scout note w1-07 |
| 9 | **Rehearse the expo script five times against the clock,** including two forced failures (tunnel off; chatbot skips the tool) and one run where a team member plays a judge typing their own words (§B). | team | S | yes | w1-07-08 ~; panel-judges w3 #2 |
| 10 | **End the literacy episode on How AI works, not on Verify "secure".** Verify rests on the student's own report and the chatbot's ticks; How AI works is scored by the server from a letter. | video, expo | S | yes | panel-judges #3; w1-02-32 ✓ |
| 11 | **Fix the three simulation bugs** (crash, step-back loop, "quiz me on what's due"). Now MUST fix 6 (§F). Until bug 3 is fixed, make no spacing or "reviews due" claim on camera. | build | S each | yes | w1-06-01 ✓, w1-06-02 ~, w1-06-03 ✓; [06](06-settings-simulation.md) recs 1–3 |
| 12 | **Shots 4c–4d without m2.** Web search off and captioned. Remove m2 from the option set ([02](02-ai-literacy-assessment.md) rec 3; MUST fix 4). Never teach or seed m2. | video, expo, pack | S | yes | w2-02-33 ~, w2-02-34 ✓; w3-07-c7 ✓ |
| 13 | **Show How AI works as per-part counts** ("checked n, right m", plus wrong ideas still held), not a level. MUST fix 7. Until built, highlight only the "held" line in 4d. | video, expo, build | S | yes | w2-02-05 ~; w3-07-c7 ✓; [02](02-ai-literacy-assessment.md) rec 6 |
| 14 | **One pitch chart from the simulation** ("eduX tested its own alarms", §E). Deck and expo printout; not the video. | pitch, expo L3 | S | yes | w1-06-04 ✓, w1-06-05 ✓; [06](06-settings-simulation.md) rec 8 |
| 15 | **Film the "as captured" Plan A with a printed line card.** Type the lines verbatim. Never type "give", "link", "ONS", "first", "cost", "different" or "shows" in a literacy line. Re-run `probe_resolve.py` on whichever pack is loaded on the day; the 9EC0 pack will match different words. | video, expo | S | yes | w3-07-c3 ✓ |
| 16 | **Label checkpoint in the dry run and every take.** Expand the tool call: 4a and 4b `request_type: research` and `asks_recent: false`; 4b at least 3 features; 4c `source_conflict: true` and `request_type: other`, ideally with the Verify answer. Any miss: reset, new chat, retake. | dry run, video | S | yes | w3-07-c1 ✓, -c4 ✓ |
| 17 | **Match the 4c line to the option set.** Rewritten set (m2 gone): the mismatch line, stating what the page says. Branch set unchanged: the dead-page line, pick m1, and don't show Verify in 4d unless MUST fix 2 is built. | video, pack | S | yes | w3-07-c5 ✓, -c7 ✓ |
| 18 | **Build the MUST fixes in §F in order,** with a test each. The SHOULD list follows only when the MUSTs are in. | build | S–M | as many as possible | §F |
| 19 | **4d: type "How am I doing at asking and checking AI answers?"** `get_my_progress` lists the economics tree first, all "new", and the chatbot may lead with it. Highlight the held line, not a level. | video | S | yes | w3-07-c7 ✓ |
| 20 | **Re-run the rehearsal after every pack or code fix** (`sims/demo-05e/run_episode.py`) and check the server console for OVER BUDGET. Full-sentence MCQ keys, rewritten literacy options and per-part counts all add characters to an 80-character margin. | build, gate | S | yes | w3-07-c2 ~ |
| 21 | **Script the honest answers for judges' own questions** (§B) and rehearse them. Say what today's build does, not what we wish it did. | expo | S | yes | panel-judges w3 #1–#2; panel-student w3 #1–#2 |

Mock-ups in the video (teacher view, C1/C3 items) are capped at about 15 s in total and labelled "mock-up". Wave 6: the teacher view is [`mockups/teacher-view.html`](mockups/teacher-view.html), captured at 1280×720 after E's light/dark check, captioned "Mock-up · illustrative class data", with the voiceover "This is the design: teachers see what to reteach, never who said what." The default video uses none.

## F. Pre-filming build fixes, in priority order

**MUST** = without it, a camera or a judge sees a wrong or embarrassing result. Ordered by how likely and how visible that is. Each has a workaround if it misses the 18:00 gate; the gate doesn't depend on them.

| # | MUST fix | What shows on camera without it | Where | Workaround if not built | Rests on |
|---|---|---|---|---|---|
| M1 | **Literacy turns never set or keep a course focus.** A research or `source_conflict` turn doesn't resolve course parts, and an answered how-AI-works check doesn't hand over to teaching when the turn had no course message. | A judge's "give me sources on the cost of living" sets the focus to *Evaluating taxes on negative externalities*. Sources come from the wrong topic, and the reply after the how-AI-works answer adds an economics quiz. | `service.tutor_turn`, `plan.choose` (w3-07 rec 4) | Video: the line card (rec 15). Expo: §B's honest script. This is the one break that can't be scripted around live. | w3-07-c3 ✓; panel-judges w3 #2; panel-student w3 #1 |
| M2 | **A reported mismatch or dead page counts as Verify met.** Score `ail_task` as met when `source_conflict` comes with it, or make "opened + said it didn't match" a full answer. | Catching an invented link lowers Verify 0.30 → 0.14. A judge asks "a student reports a dead link: Verify?" | `learner` scoring, Verify mark points (w3-07 rec 5) | Use the mismatch line, stating what the page says, sent as the Verify answer. After a dead-page take, never show the Verify record. | w3-07-c5 ✓; panel-judges w3 #1; panel-student w3 #2 |
| M3 | **Moving on scores nothing, not 0.** An ignored Verify task or check writes a `literacy_ignored` event, not `ail_task 0`. | After the how-AI-works answer the Verify task is re-asked; "ok" or a PED question then scores it 0 (Verify 0.30 → 0.14). | `service._literacy_followup`, `_how_ai_works` ([02](02-ai-literacy-assessment.md) rec 4) | Send 4c as the Verify answer so nothing waits. Otherwise cut on the feedback line, or answer the re-ask with the clean line in the shot list. At the expo, finish the episode before the PED question. | w3-07-c5 ✓; w2-02-07 ✓ |
| M4 | **m2 out of every option set.** Rewrite the fabrication options ([02](02-ai-literacy-assessment.md) rec 3) and the fabrication part's intuition line. | m2 is in all 26 captured fabrication option sets, at a different letter each take. With search on it is often true. | pack `ingest/ai_literacy/` | Branch set: pick m1 with the dead-page line. Hold the shot on the reply's first line, not the options. | w3-07-c7 ✓; w2-02-33 ~, -34 ✓ |
| M5 | **No node description as an MCQ option.** Keep the mark point as the key, never the exemplar (commit `f0a1c36` on `main` chose the point on purpose), matched to its distractors in length and punctuation. Skip the MCQ for parts with no mark point, and add mark points for the demo parts. A wave-4 scout is testing this (in progress). | The right answer in the PED shot and every judge's course question is a topic label such as "Calculating PED from percentage changes in quantity demanded and price.", and it is the longest option. | `edux/plan.py:376` (`_points` fallback), `check`/`review`/`prereq`; pack `mark_points.csv` ([05](05-product-features.md) rec 11) | Hold on the first line of each reply, never the options. No close-ups of options. | w3-05-08 ~; panel-judges w3 #5 |
| M6 | **The three crash and loop bugs.** Clamp `p_known` to [0.001, 0.999]; one prerequisite check per stuck part per session; "quiz me on what's due" reaches the reviews. | A crash (`ZeroDivisionError`) after many right answers; the same prerequisite check over and over on `demo-weak`; "what's due" teaching the old focus. | `edux/learner.py:634-637`, `:457`; `edux/plan.py:332-337`; `edux/service.py:246-247` ([06](06-settings-simulation.md) recs 1–3) | Reset between judges; don't let a judge keep answering prerequisite checks; no spacing claim. | w1-06-01 ✓, -02 ~, -03 ✓ |
| M7 | **How AI works as per-part counts** ("checked 1, right 0; still held: …"). | "How AI works: new" straight after the lesson in 4d. | `get_my_progress` ([02](02-ai-literacy-assessment.md) rec 6) | Highlight only the "held" line. If a judge asks: "one answer is thin evidence; here's the count", and show the `state` pane. | w3-07-c7 ✓; w2-02-05 ~; panel-judges w3 #4 |

**SHOULD** (better on camera or more honest, but nothing breaks without it):
1. **Don't score Ask on a `source_conflict` turn.** If the chatbot labels the dead-link turn `research`, Ask falls from 0.53 (developing) to 0.26 (new) before the record shot (w3-07-05, simulation, not verified). Workaround: the label checkpoint (rec 16).
2. **Wave-2 settings** ([02](02-ai-literacy-assessment.md) rec 2). On camera the only change is that a 2-feature 4b gets a second Ask task, so 4b must have at least 3 features. The check script still passes 74/74 (w3-07-c6 ✓).
3. **Fix the Ask task's promise.** "Rewrite your question adding <feature>, then I'll answer the sharper version" contradicts the full answer just given. Change it to "Rewrite it adding <feature>; the answer will be sharper." (`text/literacy/ask_new.md`; w3-07 rec 9.)
4. **Rewrite the fabrication intuition line** ("a citation is just more likely-looking words"). It goes out with every how-AI-works feedback and jars after a mismatch story (w3-07 rec 10).
5. **A recent-question label shouldn't block the fabrication check.** If the chatbot labels 4a or 4b `asks_recent` with search off, the cutoff check replaces the Ask or Verify task, and the fabrication check never fires at 4c (w3-07-c4 ✓).
6. **Candidates without a question.** "…and why did it change?" returns two topics as `candidates` without an `ask_which` step. Claude may ask "which topic did you mean?" (w3-07, open).
7. **The decay fix** ([06](06-settings-simulation.md) recs 9–10): right-once economics parts read below never-right after about a week. Not on camera in 2:30, but a judge who opens `state` may see it (panel-judges w3 #4).
8. **Three-option MCQs** with the guess raised to about 0.33 to match ([w3-05](work/w3/w3-05.md) rec 4). Settings only; both change together.

## A. Video storyboard (2:30)

Design rules:
- **Segment.** Each segment gets one keyword in the top-left corner (Rey et al. 2019, w1-07-04 ~).
- **Signal.** One highlight box at a time, on the line that changed (w1-07-02 ~, -03 ~).
- **Keep it coherent.** No stock footage, no music bed and no team backstory (w1-07-05 ~).
- **Pre-train.** Show the diagram before the demo (w1-07-01 ✓).
- **Keep it short.** 2:30 leaves a margin under the 3:00 limit; shorter videos hold more viewing in MOOC data (an engagement result, not a learning or judging one; w1-07-06 ✓).

These are learning effects measured mostly on university students. Applying them to persuading judges is our analogy.

Narration: about 290 words at roughly 2.2 words per second (our choice). On every chatbot frame, burn in a small caption: "Adult team account · synthetic demo student".

### Plan A "as captured": 05e build passing the gate

> **Simulated on the 05e branch; confirm in the Wednesday claude.ai dry run.** A script drove the branch's own server on 127.0.0.1, playing the chatbot's side with the labels below (simulation: synthetic demo student `demo-weak`, example pack). It shows what the server tells the chatbot and what it records. What Claude writes, and which labels it really sends, is not yet known. Scripts, captures and scenario names: [`sims/demo-05e/`](sims/demo-05e/).

**Storyboard.**

| Time | Segment (on-screen keyword) | Screen | Voiceover | Tag |
|---|---|---|---|---|
| 0:00–0:10 | **1. What is** | claude.ai, adult account. A student asks about UK inflation and gets a confident answer with a source link. Freeze. | "Sixth-formers already ask chatbots for facts and sources. Whether they can tell when it's wrong stays invisible." | D |
| 0:10–0:26 | **2. AI literacy, defined** | A rubric card: three rows (Ask, Verify, How AI works), each with an observable behaviour per level. **Ask:** names the idea, the setting, asks for sources and for reasoning. **Verify:** names the source, its publisher and date, says what it says, and whether it matched. **How AI works:** picks the right reason a cited source may not exist or may not say what was claimed, why a chatbot sounds sure, misses recent events, or changes its answer when pushed. Footer: "Assessed from what students do while studying, not a quiz." | "We define AI literacy as three things students do: ask a precise question, verify a claim against a source, and understand why chatbots fail. Each has levels we can see in normal study." | D |
| 0:26–0:36 | **3. How it works** | Diagram: student → school chatbot → `tutor_turn` → eduX → plan → reply. "No AI model" on the eduX box. | "eduX plugs into the school's chatbot. It calls us every message; we return a teaching plan from fixed rules. We never call an AI model." | F |
| 0:36–0:52 | **4a. Ask** | `demo-weak` types line 4a (shot list). The reply answers with sources, then asks for a sharper question with a time period. Highlight the task line. | "A vague question. eduX scores what the question contains, and the chatbot asks for a sharper version." | A |
| 0:52–1:06 | **4b. Verify** | The student types line 4b. The reply answers with sources, then a Verify task: open the ONS link and say what month the figure is for. | "The sharper question counts as evidence. Now a verify task: open the source and check one figure." | A |
| 1:06–1:32 | **4c. How AI works** | Caption "web search off", plus "Scripted demo: the student reports a mismatched source" (mismatch line) or "Scripted demo: the student reports a dead link" (dead-page line), unless that really happened. The student types line 4c. The reply says that's what checking is for, then shows four options on why the source was wrong. The student picks the wrong option in line 4c′. The next reply names that idea and corrects it. Highlight box on the correction, not the options (until M4 and M5 are in). | Mismatch version: "The page doesn't say what the chatbot claimed. That is the moment to learn why. This student trusted the reference because it looked official. Now they know a cited source may not exist, or may not say what was claimed." Dead-page version: "…This student thought the page had been deleted. But a cited link may never have existed: chatbots write likely-looking text." | A, D |
| 1:32–1:48 | **4d. The record** | The student types line 4d. The AI-literacy section of `get_my_progress`: Ask, Verify and How AI works, with the wrong idea still held. Cut to the terminal `state` row for `ail_how_fabrication`. Highlight the held line (per-part counts if M7 is built). | "Every moment is evidence. The server scores the letter itself, not the chatbot's opinion, and the student sees which wrong ideas about AI they still hold." | A |
| 1:48–2:08 | **5. Same question, two students** | Split screen, both typing "How do I calculate price elasticity of demand?". Left, `demo-secure`: an intuition question. Right, `demo-weak`: a quick check on *PED: definition*, then a reply that also corrects last time's mistake. Caption "two synthetic demo students". Hold on the first line of each reply, not the options (until M5). Re-capture on the expo build: the wave-1 captures came from an earlier build. | "The same engine teaches the course. Same question, two students. One gets an intuition question. The other gets a check on the idea it builds on, and last time's mistake corrected." | L |
| 2:08–2:20 | **6. Feasible** | Silent terminal montage, under 3 s per shot: a console line `tutor_turn … ms … ok`; `pyproject.toml` showing `mcp` and `uvicorn`; `check_mcp.py` ending `all checks passed`; the connector URL with the key blurred. "Sample course pack" on screen. | "It runs on a laptop. A turn takes milliseconds, because the school's chatbot does the writing. All our automated checks pass." | F |
| 2:20–2:30 | **7. What could be** | Back to the opening chat, now with the how-AI-works question in place. End card: eduX, one line, team names. | "Same chatbot. Now every slip becomes a lesson in how AI works, and a record of it. That's eduX." | D, A |

The literacy episode (4a–4d) runs 0:36–1:48, which is 72 s. If segment 1 or the deck's slide 1 uses Ofcom's "1 in 4", say "spot AI-made images", never "check facts" (w2-09-04 ✓).

**Shot list: what to type, what to check, what to expect.** "Plan" is what the server returned in our run (scenario `final`, copies `branch` and `rewrite`). Labels are what the chatbot must send; check them in the expanded tool call (rec 16).

**Every take first:** `seed-demo --reset` prints "keys kept"; new chat; connector on for `demo-weak`; web search off; the line card on the desk.

| Shot | Driver types (verbatim) | Labels the chatbot must send | Plan returned (simulated) | State change (branch / wave-2 settings) | If it goes wrong |
|---|---|---|---|---|---|
| **4a** | `what was inflation like?` | `request_type: research`; features `[concept]`; `web_access: false`; `asks_recent: false` | `answer_with_sources` (no trusted sources) → `literacy_task` Ask. The chatbot answers in full, marks figures to check, says it can't search, then the task "Rewrite your question adding a time period…". | Ask 0.30 → 0.18 / 0.19 (new); Ask task waiting | **Labelled `concept`:** empty plan, no Ask task. Reset, retake, or type `what was inflation like in the past?` (probed clean). **Labelled `asks_recent`:** a cutoff check replaces the Ask task. Answer it correctly, then reset and retake. Never type "happening", "now" or "latest" (w3-07-c4 ✓). |
| **4b** | `What was UK CPI inflation in 2022, and why did it change? Sources please.` | `research`; features `[concept, context, asks_sources, asks_reasoning]` (at least 3); `asks_recent: false` | `answer_with_sources` (trusted: ONS inflation, ONS spending, OBR) → `literacy_task` Verify: "Open the ONS link: what month is that figure for?" | Ask → 0.53 / 0.45 (developing); Verify task waiting | **Only 2 features:** under wave-2 settings, a second Ask task instead of Verify (w3-07-c6 ✓). **Labelled recent:** the Verify task is replaced and 4c later fails (w3-07-c4 ✓). **"Which topic did you mean?"** ("why did it change" returns two topic candidates): reset and use `What was UK CPI inflation in 2022, and why? Sources please.` (clean, but then the pack gives no ONS link). |
| **4c** (rewritten options) | `I opened it and the page says <X>, not <Y>.` X = the figure on the page, Y = the figure the chatbot gave. Captured as "…says 9.1%, not 11.1%." | `source_conflict: true`; `request_type: other`; ideally `answer: {part_id: ail_verify, type: ail_task, points_met: [a, c, d]}` | `source_conflict` → `ask_mcq` How AI works, 4 options (letters shuffle every take) | Verify answered with a, c, d → 0.748 (developing, 0.002 below secure). **With 0003 + 0009b: 0.740** (developing) whatever is ticked (w6-planA ✓). Check waiting. | **No `source_conflict`:** only a re-ask of the Verify task; reset and retake. **Labelled `research`:** Ask falls to new (w3-07-05, not verified); retake. **The real page matches:** keep the caption "Scripted demo"; never say the chatbot invented it. |
| **4c** (branch options, M4 not in) | `I clicked it and the page doesn't exist.` | as above, with `points_met: [a, d]` | as above | Verify → 0.14 (unless M2 is built). Check waiting. | Same as above. Then don't show Verify in 4d. |
| **4c′** | The letter beside the chosen wrong option, read off the screen. Rewritten set: the "a reference naming a publisher and a date is probably real" option (final wording from the rewritten csv). Branch set: "It copied a page that was later deleted from the internet". **Never m2; not m3** ("on purpose" gives itself away). | `request_type: other`; `answer: {part_id: ail_how_fabrication, type: mcq, choice: <letter>}` | `feedback` (correct false): the correct option, the intuition line, then the misconception named and corrected. If 4c wasn't sent as the Verify answer, a `reask` of the Verify task follows. | Fabrication 0.33 → 0.15; How AI works rollup 0.33 → 0.29 (still "new"); the wrong idea held | **The re-ask** ("Open the link: what month…?") jars after the student said the page was wrong. Cut on the feedback line, or answer it with `I opened it and the page says 9.1%, not 11.1%. It's from the Office for National Statistics, March 2023.` (probed clean in this edit; w3-07's suggested "…it's the ONS…" line pulls in *Indirect tax: splitting the burden*). Never answer "ok" (scores 0 until M3). |
| **4d** | `How am I doing at asking and checking AI answers?` | none (the chatbot calls `get_my_progress`) | AI literacy: Ask developing; Verify developing (mismatch answered) or new; How AI works new, with the wrong idea held; then the economics tree, all "new" | none | **Leads with economics:** freeze-frame the literacy lines, or cut to the `state` pane. **"How AI works: new":** highlight only the held line (M7). **Verify "developing":** say "one piece of evidence", not "can verify". |

Alternative ending (simulated, `recommended_right`): the right letter gives feedback only, and How AI works reaches "developing" with nothing held. Cleaner, but it shows no misconception, so the storyboard keeps the wrong pick.

**Fallbacks across the episode:**
- **The chatbot keeps failing the labels:** cut 4b (4a → 4c → 4c′ → 4d still runs; the re-ask is then the Ask task, which jars less; scenario `skip_4b`). After three failed takes, use Plan B.
- **Retakes:** reset and new chat every time. A second take in the same session gets no fabrication check (w3-07-09, not verified).
- **Line wording:** every literacy line on the card was probed against the branch resolver on the example pack. If the 9EC0 pack is loaded, re-probe (`sims/demo-05e/probe_resolve.py`).
- **Captions:** caption nothing as "live in the product" that isn't in the build the judges will see. If filming from the unmerged branch, the expo runs that same build.

### Plan B: 05e not merged, or failing the gate

Same segments 1–3 and 6–7. In segment 2, the footer changes to "Ask · Verify · How AI works: built on a branch, being merged". The episode uses what `main` produces today (captured) and is labelled honestly. It is weaker on criterion 1, and the team should know that.

| Time | Segment | Screen | Voiceover | Tag |
|---|---|---|---|---|
| 0:36–1:00 | **4a. Letting it think for you** | `demo-showme` asks "How am I doing?". Highlight three lines from the `get_my_progress` reply (captured): asking to be shown answers **up** (0% → 75%); deep questions **down** (100% → 25%); "your answers tend to drop after about 35 minutes". Caption: "Synthetic demo student, scripted history". | "AI literacy shows in behaviour. This student now asks to be shown the answer three times out of four, and their questions have got shallower. eduX tells them, in plain words." | A |
| 1:00–1:20 | **4b. Shown, then checked** | The same student types "just show me". The reply shows the point with one worked line, then ends with a check (captured). Cut to `reviews_due` from the progress capture, captioned "from earlier sessions". | "When they ask to be shown, eduX shows, then checks. And it brings back what they were shown before." | A, L |
| 1:20–1:40 | **4c. How AI works (designed)** | A card with the four options of the fabrication check **after** [02](02-ai-literacy-assessment.md) rec 3's rewrite (the branch pack still contains m2; don't show it), plus the branch's check-script line passing. Caption: "Built on a branch, not yet in the live build". | "Next: when a source turns out wrong, one question on why a cited source may not exist or may not say what was claimed. Each wrong option is a real misconception. It's built and tested on our branch, and being merged." | A, D |

The literacy episode runs 0:36–1:40, which is 64 s. Segment 5 then runs 1:40–2:08. Never mock the 05e moment with hand-written chat or JSON.

### What the captures support for "same question, different students"

Wave-1 captures, earlier build of `main`; re-capture on the expo build.

| Student | First move on "How do I calculate PED?" (captured) | Difference shown elsewhere |
|---|---|---|
| `demo-secure` | intuition MCQ on *PED: formula* | the `state` table moves after a wrong then a right letter |
| `demo-showme` | the **same** intuition MCQ, with the same note | `get_my_progress` trends: just-show-me up, depth down, 35-minute pattern |
| `demo-weak` | prerequisite MCQ on *PED: definition* | the next reply also corrects its held misconception `ped_formula_m1` |

Narrate "two students, two plans". Mention a third only as a history.

## B. Live expo script (4 minutes)

**Setup.** One laptop. One person talks, the other drives (w1-07-07 ✓).
- **Window 1:** claude.ai on the adult team member's paid account (the free plan allows one custom connector; w1-05-01 ✓). Web search off. The eduX connector is on for `demo-weak`, the set-up text is in the project instructions, and a new chat is open. A sticky note on the bezel reads "adult team account · synthetic student".
- **Window 2:** a terminal with three panes: the server console; `python -m edux.cli state --student demo-weak`; and the `demo-captures/` JSON for the other two students.
- **On the table:** the line card; a printed one-pager with the definition and rubric card, the two-student split screen and the `demo-showme` progress lines (fallback L3); and a crib card listing which MUST fixes (§F) are not built, with the honest line for each.

| Time | Say / type | Expected (source) | If it fails |
|---|---|---|---|
| 0:00–0:20 | Say: "eduX is the teaching brain behind a school's chatbot. Our server never calls an AI model. It assesses AI literacy from what students do while they study." Point at the rubric card. "Ask, Verify, How AI works." | n/a | n/a |
| 0:20–1:30 | **Plan A:** lines 4a, 4b, 4c, 4c′ from the card (§A shot list). Web search off. | An Ask task, a Verify task, the fabrication check, then the misconception named (simulated on the branch; dry-run on Wednesday) | **No literacy move:** check the console for `source_conflict`; retype once. Then go to L2. |
| | **Plan B:** show `demo-showme`'s progress (captured JSON or the printout) and the designed fabrication options card, labelled "on our branch". | captures | n/a |
| 1:30–2:00 | Type **"How do I calculate price elasticity of demand?"** | Console prints `tutor_turn demo-weak … ok`. A quick check on *PED: definition* with lettered options. | **Tool not called:** open the tools menu, check eduX is on, open a new chat and retype. After 30 s, go to **L1**. **The chatbot answers without the plan:** type "Call tutor_turn first, then follow its plan." |
| 2:00–2:30 | Type the **wrong letter**: the option "PED measures how much the price changes when demand changes" (**with 0011:** "PED measures how far the price changes when the demand changes"). | Feedback names that misconception and also corrects the held "divide the change in price by the change in quantity" (**with 0011:** "…by the change in quantity demanded to get PED"). Then a teaching point and a check (wave-1 capture). | **Reply skips the misconception:** show the plan JSON and say "the plan told it to; chatbots don't always comply, which is why the server scores letters itself". |
| 2:30–3:00 | Type the **right letter**, then re-run `state`. | *PED: formula* rises (0.14 → about 0.40 in the wave-1 capture; re-capture). With 0010b, a pick straight after teaching never makes a part secure: say "developing; an explain-back makes it secure". | **Slow (> 20 s):** "the server answered in milliseconds; the wait is the chatbot writing." After 45 s, go to **L2**. |
| 3:00–3:30 | Show the printed split screen: "Same question: this student knows the groundwork, so they get an intuition question instead." | captures | n/a |
| 3:30–4:00 | Feasibility and who it's for. "This is an adult team account. For students under 18, the route is a school-managed chatbot; Microsoft Copilot Studio is the best documented one, and we haven't tested it yet." **Invite the judge to type their own question** (next section). | see below | see below |

**Order (Plan A).** If 4c went in as the Verify answer, nothing is waiting and the PED question can follow. If a Verify task is still waiting when the PED question comes, it scores 0 and the PED turn opens with a prerequisite check (scenario `then_ped`; w3-07-c5 ✓). With 0003 an ignored task is a skip, not 0; with 0011 that prerequisite question's two distractors read as in the wave-6 box above. Answer the re-ask first, or run PED before the literacy episode.

**The PED run uses the prerequisite path.** That is where the step-back loop shows (M6). Until it is fixed, don't let a judge keep answering prerequisite checks in the same session.

### When a judge types their own question

Judges will type their own words (panel-judges w3 #2). The line card protects the video, not this. Say before they type: "This is live and unscripted. The console shows the plan our server sent, so you can see what it asked the chatbot to do." Then let the driver read the plan out.

**What will happen on today's branch build** (example pack; our probe of the branch resolver, w3-07-c3 ✓ plus this edit's probe; re-probe if the 9EC0 pack is loaded):

| A judge types… | What eduX does today | Honest line (until the fix is built) |
|---|---|---|
| A research question with everyday words: "give me sources on the cost of living", "can you find me sources on the cost of living crisis?" | "cost" sets the focus to *Evaluating taxes on negative externalities*. The answer comes with that topic's sources, and the Ask task still appears. The focus sticks, so the reply to a later how-AI-works answer can add an economics quiz. | "Our word-matcher read 'cost' as the economics topic. That's a known bug: research turns shouldn't touch the course focus. The fix is [built / not built yet]." (M1) |
| A follow-up in their own words: "the figure on the page is not the one you gave", "the page has another number" | "gave" pulls in *Indirect tax: splitting the burden*; "another number" pulls in the whole Elasticities topic. | Same as above. |
| A recent question: "what's the latest on interest rates?" (search off) | Likely labelled recent, so a how-AI-works check on why chatbots miss recent events. A good literacy moment: let it run. | "With search off, it doesn't know recent figures, so eduX asks why." |
| "That link is dead" / "that page doesn't exist" | A how-AI-works check on fabrication, once per part per session. If the chatbot sends it as the Verify answer with two ticks, **Verify goes down** (0.30 → 0.14). | "Today, reporting a dead link lowers Verify. That's wrong: catching it is the skill we want. The fix is to count it as a check, and it's [built / recommended, not built]." Never say "it counts as checking" unless M2 is built. (M2) |
| "ok", or a new question while a task waits | The waiting task scores 0. | "Moving on shouldn't count against you; today it does. The fix records it as skipped." (M3) |
| A course question ("what's PED?") | A plan: a check or teaching point. Without M5, the correct option is the topic label and the longest. | If they spot it: "Yes, the right option is the topic description. We're replacing it with plain-claim answers from the mark scheme." |
| Anything off-course | An empty plan or a brief answer. | "It only plans for the course it knows." |
| "How AI works says new after the lesson?" | One wrong answer leaves the level at "new". | "One answer is thin evidence. Here's the count" (point at the `state` pane). (M7) |

**Rules for the talker:**
- Read the plan from the console, then say what it did. Don't predict what the chatbot will write.
- Never quietly retype a judge's question in safer words. If you rephrase it, say why ("the word 'cost' trips our matcher; watch what happens without it").
- Name each bug with its fix and its status (built, recommended, open). Don't claim a fix that isn't in the build on the laptop.
- If the chatbot skips the tool or labels oddly, say so: "the chatbot decided that; the server only sees the labels it sends."
- After the judge leaves: `seed-demo --reset` and a new chat. Their turns are now in `demo-weak`'s record.

**Fallback ladder.** Decide in under 30 s, and never debug in front of a judge:
- **L0:** live in claude.ai through the tunnel.
- **L1:** local only. `scripts/check_mcp.py` scrolls past (about 25 s), plus `python -m edux.cli context --student demo-weak --message "How do I calculate PED?"` to show the plan. No network needed (Graham, w1-07-07 ✓).
- **L2:** the offline recordings (PED, and the literacy episode or the progress shot).
- **L3:** the printed one-pager.

**Known failure modes:**
- **Crash after many right answers (M6).** `tutor_turn` raises `ZeroDivisionError` once a part's `p_known` hits 1.0. If the console shows it, go to L2 and reseed between judges.
- **Tunnel restarted.** A quick tunnel gets a new host on every restart, so `ALLOWED_HOSTS`, the connector URL and the server all need changing (about 2 minutes). Go to L1 and fix it between judges. Start one tunnel at T-60 and never restart it. Keep a phone hotspot as backup. The tunnel adds latency we didn't measure (w3-07-c2 ~ covers localhost only).
- **Result too long.** The largest result has about 80 characters to spare (w3-07-c2 ~). If the console prints OVER BUDGET, the result is cut; go to L2.
- **Message caps.** Not checked. Use a paid account and keep L2 ready.
- **ChatGPT.** Don't demo it live. Every eduX tool counts as a write action there and asks for confirmation each turn (w1-05-05 ✓).

## C. Pre-demo checklist (read-and-do)

One person reads each item aloud; the driver does it and answers "checked". Each list has at most five items (our choice, after aviation and surgical checklists; w1-07-09 ~, w1-07-10 ~; an analogy, not evidence about demos).

**Wednesday 18:00: the gate**
1. The expo build is fixed (05e merged, or the exact branch build). The MUST fixes that landed are listed on the crib card; the rest have their workaround switched on. `check_mcp.py` and the new tests pass. Save the output.
2. `sims/demo-05e/run_episode.py` re-run on that build with the loaded pack: no OVER BUDGET line; `probe_resolve.py` clean for every line on the card. Card printed.
3. The literacy episode has run once end to end in claude.ai on the adult account, with the labels checked on every turn (rec 16). Plan A or B decided and written on the sticky note.
4. Pack: m2 out of the fabrication options (M4), mark points for the demo parts, keys matched in length and punctuation (M5), intuition note rewritten (rec 6); `ingest.cli validate` clean.
5. Paid adult account ready, with the connector added, web search off, and the set-up text in the project instructions.

**T-24 h (Wednesday evening)**
1. Video exported, with burned-in age captions, "Scripted demo" on 4c if the page matched, "AI-made images" on any Ofcom number, and a separate caption track.
2. L2 recordings saved in two places.
3. L3 one-pager, line card and crib card printed.
4. Keys reseeded after recording if any were visible.
5. Five timed rehearsals done: two with forced failures, one with a team member typing their own questions as a judge.

**T-60 min (at the venue)**
1. Mains power. Notifications off. Browser zoom 125%. Large terminal font.
2. Venue wifi tested; hotspot on standby.
3. `scripts/demo.sh` running. Tunnel started once; `ALLOWED_HOSTS` and the connector URL updated; server restarted.
4. One full dry run of §B, then `seed-demo --reset` and a new chat.
5. No keys on any screen.

**Before each judge (30 s)**
1. `python -m edux.cli seed-demo --reset` prints "keys kept".
2. New chat open, connector on, web search off.
3. Terminal `state` pane cleared; console visible.
4. Talker and driver agree on Plan A or B; line card and crib card on the table.

**If anything fails:** say "here's the recorded run", move down the ladder, and fix it after the judge leaves.

## D. Bugs and confusing outputs found while capturing

For the build team. None is fixed. The MUST and SHOULD lists in §F take their order from here.

**Found by the wave-3 rehearsal on the 05e branch** (simulation; [`sims/demo-05e/`](sims/demo-05e/)):
- **R1. Common words set the course focus** (M1). Full-text OR match: "give" → *Indirect tax: shifting supply*; "link" → *PED: interpreting values*; "ONS" → *Indirect tax: splitting the burden*; "first" → *PED: formula*; "cost" → *Evaluating taxes on negative externalities*; "different" → *PED: definition*; "shows" → *Indirect tax: shifting supply* (w3-07-c3 ✓). This edit's probe adds "gave" → *splitting the burden* and "another number" → all six elasticity parts. Once set, the focus sticks for later turns.
- **R2. Verify scoring.** A dead page with two ticks: 0.30 → 0.14. Moving on: `ail_task` 0, same fall. A mismatch with three ticks: 0.748, 0.002 below secure, whether three or four points are ticked (w3-07-c5 ✓). A second good answer in a retake without a reset would show "secure". Wave 6: with 0009b, a second *report* stays developing (0.740) until the student has done one real check (w6-c2b-1 ✓); reset anyway.
- **R3. The Verify task is re-asked after the how-AI-works check,** contradicting the student, unless 4c was sent as the Verify answer (w3-07-c5 ✓).
- **R4. Labels decide the shot.** 4a labelled `concept`: empty plan. 4a or 4b labelled `asks_recent` with search off: the cutoff check replaces the task, and in `recent_t2` the fabrication check never fires (w3-07-c4 ✓). The dead-link turn labelled `research`: Ask 0.53 → 0.26 (w3-07-05, not verified).
- **R5. m2 is in all 26 fabrication option sets; How AI works shows "new" after the lesson,** and there are no per-part counts (w3-07-c7 ✓). The branch's m1 correction ("The link never existed") contradicts a mismatch story.
- **R6. Option letters reshuffle every take** (the shuffle seed includes the turn's timestamp), and a retake in the same session loses the check (w3-07-09, not verified).
- **R7. The Ask task promises "then I'll answer the sharper version"** after a full answer.
- **R8. Size margin:** 2,318 of 2,400 characters by the server's count (w3-07-c2 ~).

**Found in the MCQ audit (wave 3):**
- **Q1. The correct option is the node description in 7 of 9 parts** (`edux/plan.py:376`, `_points` falls back to it when a part has no mark point; the pack has mark points for 2 parts). It is the longest option in 7 of 9 (w3-05-08 ~). On the current build the option comes from mark points (or that fallback), not note key points. The wave-1 captures showed short key points without full stops, so they appear to come from an earlier code path; we could not pin which commit changed it ([04](04-economics-education.md) rec 1 rewrites key points the current build no longer uses as options).

**Found by simulation in wave 2 ([06](06-settings-simulation.md)), M6:**
- **S1. Divide-by-zero crash.** `p_known` reaches exactly 1.0 (no upper clamp, `edux/learner.py:634-637`); the next exchange divides by zero (`edux/learner.py:457`; w1-06-01 ✓).
- **S2. Step-back loop.** Once a part is flagged stuck, 12 of 14 consecutive plans were the same prerequisite check (`edux/plan.py:332-337`; w1-06-02 ~).
- **S3. "Quiz me on what's due" misses the reviews** (`edux/service.py:246-247`; w1-06-03 ✓).

**Found while capturing in wave 1** (earlier build of `main`):
1. **The check on "Keep the minus sign" reuses distractors about the formula,** so it tests which line was just shown (panel-teacher #2).
2. **Review MCQs had two options plus `extra_option`,** so the chatbot writes the third. The `tax_incidence_split` distractor uses "always".
3. **After a wrong prerequisite letter, `demo-weak` goes straight on to teaching the target.** Answer if asked: "we correct it in one line; the prerequisite is scheduled for review".
4. **One right check clears a misconception about a different point** (`ped_formula_m1`). It may be intended, but it looks odd on screen.
5. **The intuition note is a prerequisite reminder,** not an everyday hook (rec 6).
6. **`demo-secure` and `demo-showme` get identical first turns.**
7. **Decay looks harsh on screen:** `tax_incidence_split` shows p_now 0.00 against p_known 0.77 after 60 days ([06](06-settings-simulation.md) recs 9–10).
8. **The review date and the half-life look inconsistent.** Don't show that column until the learner-model owner confirms it.
9. **`conflict_flagged` can't be triggered on cue,** so no shot rests on it.
10. **A content error in the pack:** the correction for `externality_tax_eval_m1` ([04](04-economics-education.md)).
11. **`docs/demo-script.md` is out of date** (rec 8).

## E. Pitch chart from the simulation (rec 14)

From [06](06-settings-simulation.md), "Recommended chart for the pitch". Title: **"eduX tested its own alarms."** Two small grouped bar charts side by side, both far scenario (study 150–90 days before the exam, then stop), current settings against evidence-based settings:

| Panel | Current | Evidence-based settings | Paired difference |
|---|---|---|---|
| "Secure" but not known on exam day | 76% | 55% | −21 pts (95% CI ±6) |
| Parts truly secure at the end (of 9) | 3.9 | 4.7 | +0.8 (95% CI ±0.3) |

- **Always show both panels.** A model that never says "secure" would score 0% on the first panel; the second stops that misleading (w1-06-04 ✓, w1-06-05 ✓).
- Caption: "Simulation: synthetic students on our 9-part example pack. Not a learning result."
- Say "evidence-based settings", not "tuned". Build the chart fresh; don't reuse `sims/results/false_secure.svg`.
- Deck and expo printout (L3) only; not the 2:30 video.

## Later (not before Thursday; for the business plan and Q&A)

- **A teacher view mock-up, labelled as a mock-up** (coordinator decision; spec in [05](05-product-features.md)). Deck, and at most about 8 s of the video inside the 15-s mock-up cap. **Drawn in wave 6:** [`mockups/teacher-view.html`](mockups/teacher-view.html) (not built; "this is the design").
- **An answer-first mode for students in a rush,** with the check offered after and skippable (panel-student #1).
- **A validity plan for literacy scores:** the label-agreement study ([02a](02a-label-agreement-protocol.md)) and slower settings for literacy parts ([02](02-ai-literacy-assessment.md) rec 21).
- **How often real student research questions contain the resolver's trigger words** (panel-student w3 Q1). The focus fix (M1) makes this moot for literacy turns, but course questions still resolve by the same match.
- **School routes:** test Copilot Studio; set `readOnlyHint` on `get_my_progress` ([05](05-product-features.md)). "Copilot Studio, untested" isn't yet a named route (panel-student w3 Q5).
- **A literacy moment inside homework,** not only on research questions (panel-student #2).

## Considered and rejected

- **Leading the video with PED.** The judges panel scores problem fit at 2 when the video shows elasticity rather than AI literacy.
- **The wave-1 and wave-2 Plan A lines** ("what's happening with inflation?", "Please give me sources", "That ONS page doesn't give that figure."). "happening" invites a recent-question label; "give" and "ONS" pull in tax parts (w3-07-c3 ✓, -c4 ✓).
- **The check script's petrol lines.** "cost" resolves to an externality part, and the petrol 4b brings PED teaching into 4c′ (w3-07).
- **Seeding literacy history for `demo-weak`** so 4d shows more. It would be scripted history in the shot called "the record".
- **Quietly rewording a judge's question into safe words.** Judges would rightly read it as hiding a bug.
- **Narrating "three students, three plans".** The captures show two plans.
- **Faking the 05e moment** with hand-written chat or JSON.
- **Showing a 16- or 17-year-old on consumer claude.ai** (w1-05-02 ✓).
- **Building the literacy shot on self-correction** (`conflict_flagged`). It can't be triggered on cue.
- **Ending on "Verify: secure".** It invites the objection that one self-report makes Verify secure.
- **Three students live in three chats.** Triple the failure points.
- **Demoing ChatGPT live.** It asks for confirmation on every turn.
- **A music bed, stock footage or a full on-screen transcript** (w1-07-01 ✓). **A 3:00 video.**

## Panel objections this report answers or leaves open

| Objection | Status |
|---|---|
| "Catching a fake link lowers Verify; moving on scores 0" (judges w3 #1, student w3 #2) | **Recommended** (M2, M3), not built. Partly worked around on camera (mismatch line sent as the Verify answer). At the expo, the honest line says so. |
| "The demo only works with banned words; we'll type our own" (judges w3 #2, student w3 #1) | **Partly:** the line card covers the video; §B scripts the honest answer. The fix (M1) is recommended, not built. |
| "Slide-1 evidence doesn't match the claim" (judges w3 #3) | **Partly:** caption "AI-made images" wherever the Ofcom number appears. The brief is still unpasted. |
| "The record misreads: 'new' after the lesson" (judges w3 #4, student w3 #5) | **Recommended** (M7; [06](06-settings-simulation.md) recs 9–10), not built. On camera: highlight the held line. |
| "Economics checks still give the answer away" (judges w3 #5, student w3 #4) | **Recommended** (M5; [05](05-product-features.md) rec 11), not built; a wave-4 scout is testing it. On camera: no close-ups of options. |
| "Prototype: 3 on video, 2 live at the expo" (judges w3 re-score) | **Partly:** the as-captured shot list and §B. Moves to 4 only with M1–M2 built. |
| "A revision tutor, not an AI-literacy entry" (judges #1) | **Recommended:** Plan A leads with the definition and a 72-s literacy episode; not filmed yet. Only partly by Plan B. |
| "Your demo corrects a true belief" (m2; judges w2 #1) | **Recommended** (rec 12, M4), not built in the pack. Workaround: pick m1 with the dead-page line. |
| "Where is your definition?" (judges #2) | **Partly here:** segment 2's rubric card; the full definition is in [02](02-ai-literacy-assessment.md) rec 1. |
| "Why believe a 'secure' Verify?" (judges #3) | **Avoided on screen, not answered:** we end on How AI works. |
| "Your students can't legally use the chatbot you filmed" (judges #4, student Q4, teacher #5) | **Recommended:** adult-account captions and a truthful route statement. The route is untested. |
| "Same question, three plans" | **Answered:** two plans, plus one history. |
| "I ask a question and get a quiz" (student #1) | **Partly:** Plan B's "shown, then checked" shot; the compromise is in [05](05-product-features.md). M1 also stops research questions turning into economics quizzes. |
| "It feels like being watched" (student #4) | **Partly:** caption from [05](05-product-features.md); not built in `text/`. |
| "No teacher view" (teacher #4, judges Q3) | **Partly:** a labelled mock-up in the deck. |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w3-07-c1 | On the 05e branch, the scripted episode returns an Ask task, a Verify task, `source_conflict` plus a 4-option fabrication check, the misconception named, and an AI-literacy section in progress | simulation | synthetic demo student, example pack | n/a (product behaviour) | ✓ holds only if the chatbot sends these labels |
| w3-07-c2 | Never over budget in the rehearsal; largest result 2,318 of 2,400 characters by the server's count; median server time 7–10 ms | simulation | laptop, localhost | cost (latency) | ~ scout's 2,192 was the driver's count; margin ~80 chars; timing machine-dependent |
| w3-07-c3 | "give", "link", "ONS", "first", "cost", "different", "shows" resolve to course parts; the wave-1 lines turn the reply after the check into a PED prerequisite MCQ | simulation | example pack | n/a | ✓ |
| w3-07-c4 | 4a labelled `concept` gives an empty plan; `asks_recent` replaces the Ask (or Verify) task, and the fabrication check can then never fire | simulation | synthetic | n/a | ✓ |
| w3-07-c5 | Moving on scores `ail_task` 0 (Verify 0.30 → 0.14); dead page ticked a, d scores 0.5 (→ 0.14); a mismatch ticked a, c, d gives 0.748 (developing) | simulation | synthetic | prediction | ✓ the 2-of-4 follows from the ticks chosen, not the server |
| w3-07-c6 | Wave-2 settings: a 2-feature 4b gets a second Ask task; branch check script passes 74/74 on both copies | simulation | synthetic | prediction | ✓ |
| w3-07-c7 | How AI works shows "new" after a wrong pick; m2 is in all 26 fabrication option sets | simulation | synthetic | prediction | ✓ |
| w3-07-05 | The dead-link turn labelled `research` pulls Ask 0.53 → 0.26 before the record shot | simulation | synthetic | prediction | not verified |
| w3-07-09 | A same-session retake loses the fabrication check; letters reshuffle every take | simulation | synthetic | n/a | not verified |
| (probe, this edit) | On the branch resolver and example pack: "cost of living" → externality tax; "the one you gave" → tax incidence; "another number" → all elasticity parts; the 4d line and "…says 9.1%, not 11.1%. It's from the Office for National Statistics, March 2023." match nothing | our run | example pack | n/a | not verified; reproducible with `probe_resolve.py` |
| w3-05-08 | The correct MCQ option is the node description in 7 of 9 parts (`plan.py:376` fallback), and the longest option in 7 of 9 | our audit | example pack | n/a | ~ verifier: 7 of 9 longest, not 6 |
| w2-09-04 | 52% of UK teens confident at identifying AI-made content; 25% of those failed Ofcom's image test | survey with a performance task | UK 13–17 | AI literacy (image test, not fact-checking) | ✓ |
| w1-07-01 | Mayer's median effects: coherence 0.86, signalling 0.70, segmenting 0.67, pre-training 0.78, modality 1.00, redundancy 0.10 | theory (author's summary) | lab experiments | learning | ✓ |
| w1-07-02 | Signalling meta-analysis: d = 0.38, 44 effects, 29 studies, 2,726 participants | meta-analysis | mixed ages | learning | ~ abstract level only |
| w1-07-03 | Signalling meta-analysis: retention g = 0.53, transfer g = 0.33 | meta-analysis | about 14% secondary pupils | learning | ~ secondary source; CIs not checked |
| w1-07-04 | Segmenting meta-analysis: small-to-medium gains in retention and transfer | meta-analysis | mostly university | learning | ~ abstract via secondary snippets |
| w1-07-05 | Seductive details hinder learning (g = −0.33) | meta-analysis | mixed | learning | ~ secondary only |
| w1-07-06 | Shorter MOOC videos are much more engaging (6.9M sessions) | correlational | adult MOOC learners | engagement (not learning) | ✓ |
| w1-07-07 | Graham: say what it is first, demo fast, one talks and one drives, run the server locally | practitioner | startup founders | none (opinion) | ✓ |
| w1-07-08 | YC: one point per slide, one best presenter, rehearse | practitioner | YC founders | none (opinion) | ~ the guide says demos seldom work in modern Demo Day talks |
| w1-07-09 | Surgical checklist: deaths 1.5% → 0.8%, complications 11.0% → 7.0% | quasi-experimental | surgical patients 16+ | safety (not learning) | ~ abstract only |
| w1-07-10 | NASA flight-deck checklist report ends with design guidelines | official document | airline crews | policy | ~ abstract only |
| w1-07-11 | A hackathon guide: video only a demo, at most 2 minutes; live demo is the best proof | practitioner | one US hackathon | none (rules) | ✓ |
| w1-07-12 | Duarte: pitches alternate between "what is" and "what could be" | practitioner (secondary) | business presentations | none | ~ ending on the reward is in the book, not read |
| (captures) | 51/51 MCP checks on the wave-1 build of `main` (without 05e); median `tutor_turn` 14 ms; zero network calls | our run | n/a | cost / feasibility | not verified; `sims/capture_demo.py` |
