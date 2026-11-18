# Demo plan: video storyboard, live expo script, checklist

Waves 1 and 2. Wave 2 added no demo scout note; this edit brings the plan into line with [02](02-ai-literacy-assessment.md) (the m2 option, per-part How AI works counts), [06](06-settings-simulation.md) (three bugs, the pitch chart) and [05](05-product-features.md) (teacher view, routes). Wave-1 sources: scout notes `work/w1/w1-07.md`, verifier marks `work/w1/verify-C.json`, panels `work/w1/panel-judges.md`, `panel-student.md` and `panel-teacher.md`, the captures in `sims/demo-captures/` (synthetic demo students, example pack), and the 05e branch (`build/05e-literacy-coaching`: its literacy pack files and its `scripts/check_mcp.py`). Economics content issues are in [`04-economics-education.md`](04-economics-education.md).

Deliverables: a 2–3 minute video (due Thursday 19 November, 23:59) and a live demo at the expo on 20 November, where judges visit teams. The official rules page publishes no rubric or weights, so the criterion tags below follow the judges panel's reading: **D** = defining AI literacy, **A** = assessing it, **L** = learning value, **F** = feasibility and who it helps.

## Summary

- **Fix three bugs before filming (wave 2, [06](06-settings-simulation.md)).** (1) `p_known` reaches exactly 1.0 and the next exchange crashes `tutor_turn` with a divide-by-zero (w1-06-01 ✓). A take or a judge's run that answers one part right many times can hit it. (2) Once a part is flagged stuck, every later plan in the session is the same prerequisite check (w1-06-02 ~). Shot 5 and the expo PED run both go through `demo-weak`'s prerequisite path, where this loop shows. (3) "Quiz me on what's due" teaches the old focus instead of the due reviews (w1-06-03 ✓). All three are S fixes (rec 11).
- **m2 is out (wave 2).** Shots 4c–4d no longer teach "searched a database and picked the wrong entry" (m2). With search on it is often true (w2-02-33 ~, w2-02-34 ✓). Film with web search off. The point taught is that a cited source may not exist, or may not say what was claimed. m2 is never taught and never seeded (rec 12; [02](02-ai-literacy-assessment.md) recs 3, 7).
- **How AI works shows as per-part counts, not a level (wave 2).** The rolled-up level ranks no-skill students above strong ones in simulation (w2-02-05 ~). Shot 4d and the expo show "checked n, right m" per part and the wrong ideas still held (rec 13; [02](02-ai-literacy-assessment.md) rec 6).
- **Lead with AI literacy, not elasticity.** The judges panel's single biggest fix is to rebuild the video around one AI-literacy episode of about 60–75 s. It should open on the definition and rubric and end on the student's literacy record. PED moves to a 20-second supporting shot and to the expo (panel-judges).
- **Step 05e is built on its branch, not merged.** The branch has the parts the episode needs: Ask and Verify tasks after a research question, a four-option how-AI-works check when a student reports a bad source (its options need [02](02-ai-literacy-assessment.md) rec 3's rewrite, which removes m2), and an AI-literacy section in `get_my_progress`. So the storyboard has **Plan A** (05e merged and passing a claude.ai dry run by the gate) and **Plan B** (not).
- **Plan A shots are expected output, not captured output.** They come from the branch's code and its check script, which passes those steps against the server. Nobody has yet run the episode end to end in claude.ai. Do that first on Wednesday.
- **"Same question, different students" shows two plans, not three.** In the captures, `demo-secure` and `demo-showme` get the same first move (an intuition MCQ). Only `demo-weak` differs (a prerequisite check, plus a correction of its old mistake). The video says "two students". The third student's difference appears only in its progress history.
- **The product runs and is fast** (our capture run; not verifier-checked; "no model calls" lowers our cost, not the school's, which pays its host per turn: [business plan](business-plan.md)): 51 of 51 MCP checks passed on the current build (without 05e), the median `tutor_turn` server time was 14 ms, and the captured runs made zero network calls.
- **The economics MCQs give the answer away by form.** In all 6 distinct option sets captured, the correct option lacks a full stop and every distractor has one; it is the shortest option in 5 of 6. Fix the pack wording before any close-up ([04](04-economics-education.md) rec 1). The 05e how-AI-works options are matched in length and none has a full stop, but the distractors still use absolute words ("always", "on purpose") while the correct option hedges. Fix that before a close-up too ([02](02-ai-literacy-assessment.md) rec 3).
- **Age:** claude.ai consumer plans are 18+ (w1-05-02 ✓). Film every chatbot shot on an adult team member's account, with a caption, and never show or imply a 16- or 17-year-old using consumer claude.ai.
- **Expo:** one live student, two people (one talks, one drives), a reset and a new chat between judges, and a four-rung fallback ladder decided in under 30 s (w1-07-07 ✓, w1-07-08 ~).

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on |
|---|---|---|---|---|---|
| 1 | **Gate at 18:00 Wednesday (our choice): Plan A or Plan B.** Plan A needs all three: 05e merged to `main` (or, if not merged, the branch build itself, provided the expo runs that same build); the branch's `check_mcp.py` passing; and one end-to-end dry run of the literacy episode in claude.ai on the adult account without a retake. Merge status alone is not the test. | team decision | S | yes | panel-judges Q3; branch check script |
| 2 | **Fix the MCQ option form in the pack before recording.** Full-sentence correct options with full stops, matched in length to their distractors, at least on `ped_definition`, `ped_formula`, `ped_values`, `tax_incidence_split`. Re-capture to confirm. | pack (team edit) | S | yes | 04 rec 1; panel-teacher #2; panel-student #3; panel-judges #5 |
| 3 | **Film on an adult team member's account and caption every chatbot shot**: "Filmed on an adult team member's account. Students under 18 would use a school-managed chatbot." Demo students are synthetic, and the video says so. | video, expo | S | yes | w1-05-02 ✓; panel-judges #4 |
| 4 | **Shoot the storyboard below (Plan A or B), with the literacy episode at 60–75 s.** Keywords on screen, narration as the main channel, no music under speech, and a separate full-caption track. | video | M | yes | panel-judges; w1-07-01 ✓, -02 ~, -04 ~, -05 ~ |
| 5 | **Reset ritual for every take and every judge:** `python -m edux.cli seed-demo --reset`, then a **new chat**. On 05e, the fabrication check comes at most once per part per session, so a second take in the same session won't show it. | checklist | S | yes | scout note w1-07; branch check script |
| 6 | **Rewrite the `ped_definition → ped_formula` intuition note as an everyday hook.** Today it reads as a prerequisite reminder, and on camera the intuition question looks like a formula quiz. | pack `edges.csv` (team edit) | S | yes | captures; scout note w1-07 |
| 7 | **Record two offline fallback clips** (about 60 s each): the PED run and the literacy episode (Plan A) or the progress shot (Plan B). Keep them on the laptop desktop and on a phone. | expo fallback L2 | S | yes | w1-07-07 ✓ |
| 8 | **Rewrite `docs/demo-script.md`** to match steps 05d/05e and the live script below. It still describes `prequestion`, `check_prereq` and `feedback`/`teach`. | team doc | S | yes | scout note w1-07 |
| 9 | **Rehearse the expo script five times against the clock, including two forced failures** (tunnel off; chatbot skips the tool). | team | S | yes | w1-07-08 ~ |
| 10 | **End the literacy episode on How AI works, not on Verify "secure".** Verify rests on the student's own report; How AI works is scored by the server from a letter. | video, expo | S | yes | panel-judges #3; w1-02-32 ✓ ([02](02-ai-literacy-assessment.md)) |
| 11 | **Fix the three simulation bugs before the gate** (wave 2). Clamp `p_known` to [0.001, 0.999] (bug 1, the crash); one prerequisite check per stuck part per session, then reteach or switch (bug 2, the loop); let "Quiz me on what's due" reach the reviews (bug 3). Add a test for each. Until bug 3 is fixed, make no spacing or "reviews due" claim on camera. | build | S each | yes | w1-06-01 ✓, w1-06-02 ~, w1-06-03 ✓; [06](06-settings-simulation.md) recs 1–3 |
| 12 | **Rewrite shots 4c–4d without m2** (wave 2). Web search off and captioned. The student reports a source that doesn't say what was claimed, and picks a wrong option from [02](02-ai-literacy-assessment.md)'s rewritten set. The feedback teaches that a cited source may not exist, or may not say what was claimed. Don't seed m2 as "held". Needs [02](02-ai-literacy-assessment.md) rec 3 done first. | video, expo, seed | S | yes | w2-02-33 ~, w2-02-34 ✓; coordinator decision |
| 13 | **Show How AI works as per-part counts** ("checked n, right m", plus wrong ideas still held) in 4d and at the expo, not as a level. Freeze-frame whatever the build shows; if it still shows a level, don't highlight that number. | video, expo, build | S | yes | w2-02-05 ~; [02](02-ai-literacy-assessment.md) rec 6 |
| 14 | **One pitch chart from the simulation** ("eduX tested its own alarms", spec in §E). Deck, and the expo printout; not the video. | pitch, expo L3 | S | yes | w1-06-04 ✓, w1-06-05 ✓; [06](06-settings-simulation.md) rec 8 |

Ranks 11–14 were added in wave 2 and keep the wave-1 numbers stable. Rec 11 belongs with rec 1: it is part of the gate. Mock-ups in the video (teacher view, C1/C3 items) are capped at about 15 s in total and labelled "mock-up".

## A. Video storyboard (2:30)

Design rules:
- **Segment.** Each segment gets one keyword in the top-left corner (Rey et al. 2019, w1-07-04 ~).
- **Signal.** One highlight box at a time, on the line that changed (w1-07-02 ~, -03 ~).
- **Keep it coherent.** No stock footage, no music bed and no team backstory (w1-07-05 ~).
- **Pre-train.** Show the diagram before the demo (w1-07-01 ✓).
- **Keep it short.** 2:30 leaves a margin under the 3:00 limit; shorter videos hold more viewing in MOOC data (an engagement result, not a learning or judging one; w1-07-06 ✓).

These are learning effects measured mostly on university students. Applying them to persuading judges is our analogy.

Narration: about 290 words at roughly 2.2 words per second (our choice). On every chatbot frame, burn in a small caption: "Adult team account · synthetic demo student".

### Plan A: 05e merged (or the same branch build at the expo) and passing the gate

**Shots 4a–4d are expected from the branch's code and its check script. They have not been captured in claude.ai.** Re-time them after the Wednesday dry run.

| Time | Segment (on-screen keyword) | Screen | Voiceover | Tag |
|---|---|---|---|---|
| 0:00–0:10 | **1. What is** | claude.ai, adult account. A student asks about UK inflation and gets a confident answer with a source link. Freeze. | "Sixth-formers already ask chatbots for facts and sources. Whether they can tell when it's wrong stays invisible." | D |
| 0:10–0:26 | **2. AI literacy, defined** | A rubric card: three rows (Ask, Verify, How AI works), each with an observable behaviour per level. **Ask:** names the idea, the setting, asks for sources and for reasoning. **Verify:** names the source, its publisher and date, says what it says, and whether it matched. **How AI works:** picks the right reason a cited source may not exist or may not say what was claimed, why a chatbot sounds sure, misses recent events, or changes its answer when pushed. Footer: "Assessed from what students do while studying, not a quiz." | "We define AI literacy as three things students do: ask a precise question, verify a claim against a source, and understand why chatbots fail. Each has levels we can see in normal study." | D |
| 0:26–0:36 | **3. How it works** | Diagram: student → school chatbot → `tutor_turn` → eduX → plan → reply. "No AI model" on the eduX box. | "eduX plugs into the school's chatbot. It calls us every message; we return a teaching plan from fixed rules. We never call an AI model." | F |
| 0:36–0:52 | **4a. Ask** | `demo-weak` types a vague research question ("what's happening with inflation?"). The reply answers with sources, then models a sharper version and sets one task: rewrite it with a time period. Highlight the task line. | "A vague question. eduX scores what the question contains, and the chatbot asks for a sharper version." (Add the feature count on screen only if the dry run shows it.) | A |
| 0:52–1:06 | **4b. Verify** | The student rewrites: UK CPI, 2025, with sources and reasons. The reply answers with sources, then a Verify task: open the ONS link and say what month the figure is for. | "The sharper question counts as evidence. Now a verify task: open the source and check one figure." | A |
| 1:06–1:32 | **4c. How AI works** | Caption "web search off". The student types "That ONS page doesn't give that figure." The reply says that's what checking is for and corrects the claim. Then a four-option question on why the source was wrong, using [02](02-ai-literacy-assessment.md)'s rewritten set (rec 3; never m2). The student picks the wrong idea that a reference with a named publisher and date is probably real (final wording from the rewritten csv). The next reply names that idea and corrects it: a cited source may not exist, or may not say what was claimed, so check it. Highlight box on the four options (matched in length and form once [02](02-ai-literacy-assessment.md) rec 3 is done). | "The source doesn't say what the chatbot claimed. That is the moment to learn why. One question, four options, each wrong option a real misconception. This student trusted a source because it looked official. Now they know a cited source may not exist, or may not say what was claimed." | A, D |
| 1:32–1:48 | **4d. The record** | `get_my_progress`, AI-literacy section: Ask and Verify levels with their evidence counts; How AI works as per-part counts ("checked n, right m"), plus the wrong idea still held. Cut to the terminal row for `ail_how_fabrication`. Highlight the How AI works counts, not Verify. | "Every moment is evidence. The server scores the letter itself, not the chatbot's opinion, and the student sees which wrong ideas about AI they still hold." | A |
| 1:48–2:08 | **5. Same question, two students** | Split screen, both typing "How do I calculate price elasticity of demand?". Left, `demo-secure`: an intuition question. Right, `demo-weak`: a quick check on *PED: definition*, then a reply that also corrects last time's mistake (dividing price by quantity). Caption "two synthetic demo students". Hold on the first line of each reply, not the options (until rec 2 is done). | "The same engine teaches the course. Same question, two students. One gets an intuition question. The other gets a check on the idea it builds on, and last time's mistake corrected." | L |
| 2:08–2:20 | **6. Feasible** | Silent terminal montage, under 3 s per shot: the console line `tutor_turn … 13ms … ok`; `pyproject.toml` showing `mcp` and `uvicorn`; `check_mcp.py` ending `all checks passed`; the connector URL with the key blurred. "Sample course pack" on screen. | "It runs on a laptop. A turn takes milliseconds, because the school's chatbot does the writing. All our automated checks pass." | F |
| 2:20–2:30 | **7. What could be** | Back to the opening chat, now with the how-AI-works question in place. End card: eduX, one line, team names. | "Same chatbot. Now every slip becomes a lesson in how AI works, and a record of it. That's eduX." | D, A |

The literacy episode (4a–4d) runs 0:36–1:48, which is 72 s.

**Running the unmerged branch.** If 05e passes the dry run but isn't merged, filming from the branch is acceptable only if the expo runs that same build. Caption nothing as "live in the product" that isn't in the build the judges will see.

**Plan A filming risks, each with a response:**
- **Web search off, and m2 never appears.** Turn web search off for the whole episode and caption 4c "web search off". The option set must be [02](02-ai-literacy-assessment.md)'s rewritten one: m2 ("searched a database and picked the wrong entry") is often true with search on, so it is never a wrong option, never taught and never seeded (w2-02-33 ~, w2-02-34 ✓; [02](02-ai-literacy-assessment.md) recs 3, 7). The correct point is true either way.
- **No bad source on cue.** The chatbot may give a link that works and matches, or none. The student's "doesn't give that figure" line is therefore scripted.
  - If the take has a genuinely broken or mismatched link, use it.
  - Otherwise, caption 4c "Scripted demo: the student reports a mismatched source".
  - Never claim on camera that the chatbot invented the link unless it did.
- **The chatbot may not set `source_conflict`.** The console shows whether it did. Retake. If it fails three times, use Plan B's segment 4.
- **Untested sequence.** The check script tests a bad link after a cutoff check, not while a Verify task is waiting. The dry run must confirm that 4b → 4c works in that order. If not, cut 4b and go straight from 4a to 4c.
- **One fabrication check per part per session.** Reset and open a new chat before every retake (rec 5).
- **The progress wording in 4d is not yet seen in claude.ai.** Freeze-frame whatever it really says. Don't caption numbers it doesn't show.

### Plan B: 05e not merged, or failing the gate

Same segments 1–3 and 6–7. In segment 2, the footer changes to "Ask · Verify · How AI works: built on a branch, being merged". The episode uses what `main` produces today (captured) and is labelled honestly. It is weaker on criterion 1, and the team should know that.

| Time | Segment | Screen | Voiceover | Tag |
|---|---|---|---|---|
| 0:36–1:00 | **4a. Letting it think for you** | `demo-showme` asks "How am I doing?". Highlight three lines from the `get_my_progress` reply (captured): asking to be shown answers **up** (0% → 75%); deep questions **down** (100% → 25%); "your answers tend to drop after about 35 minutes". Caption: "Synthetic demo student, scripted history". | "AI literacy shows in behaviour. This student now asks to be shown the answer three times out of four, and their questions have got shallower. eduX tells them, in plain words." | A |
| 1:00–1:20 | **4b. Shown, then checked** | The same student types "just show me". The reply shows the point with one worked line, then ends with a check (captured, `extras.json`). Cut to `reviews_due` from the progress capture, captioned "from earlier sessions": the parts they were shown before (reason `just_show_me`). | "When they ask to be shown, eduX shows, then checks. And it brings back what they were shown before." | A, L |
| 1:20–1:40 | **4c. How AI works (designed)** | A card with the four options of the fabrication check **after** [02](02-ai-literacy-assessment.md) rec 3's rewrite (the branch pack still contains m2; don't show it), plus the branch's check-script line passing ("a bad link gets source_conflict first, then a 4-option check on fabrication"). Caption: "Built on a branch, not yet in the live build". | "Next: when a source turns out wrong, one question on why a cited source may not exist or may not say what was claimed. Each wrong option is a real misconception. It's built and tested on our branch, and being merged." | A, D |

The literacy episode runs 0:36–1:40, which is 64 s. Segment 5 then runs 1:40–2:08 and may add the `state` row moving for `demo-secure` (*PED: formula* new 0.30 → developing 0.56 after one right check; captured).

Never mock the 05e moment with hand-written chat or JSON. Judges ask questions at the expo (see Considered and rejected).

### What the captures support for "same question, different students"

| Student | First move on "How do I calculate PED?" (captured) | Difference shown elsewhere |
|---|---|---|
| `demo-secure` | intuition MCQ on *PED: formula* | the `state` table moves after a wrong then a right letter |
| `demo-showme` | the **same** intuition MCQ, with the same note | `get_my_progress` trends: just-show-me up, depth down, 35-minute pattern |
| `demo-weak` | prerequisite MCQ on *PED: definition* | the next reply also corrects its held misconception `ped_formula_m1` |

Narrate "two students, two plans". Mention a third only as a history, not as a third plan.

## B. Live expo script (4 minutes)

**Setup.** One laptop. One person talks, the other drives (w1-07-07 ✓).
- **Window 1:** claude.ai on the adult team member's paid account (the free plan allows one custom connector; w1-05-01 ✓). Web search off. The eduX connector is on for `demo-weak`, the set-up text is in the project instructions, and a new chat is open. A sticky note on the bezel reads "adult team account · synthetic student".
- **Window 2:** a terminal with three panes: the server console; `python -m edux.cli state --student demo-weak`; and the `demo-captures/` JSON for the other two students.
- **On the table:** a printed one-pager with the definition and rubric card, the two-student split screen and the `demo-showme` progress lines (fallback L3).

| Time | Say / type | Expected (source) | If it fails |
|---|---|---|---|
| 0:00–0:20 | Say: "eduX is the teaching brain behind a school's chatbot. Our server never calls an AI model. It assesses AI literacy from what students do while they study." Point at the rubric card. "Ask, Verify, How AI works." | n/a | n/a |
| 0:20–1:30 | **Plan A:** type a vague research question; then the sharpened version; then "That ONS page doesn't give that figure." Answer the four-option question with the wrong letter (the "looks official, so probably real" option from the rewritten set; never m2). Web search off. | An Ask task, then a Verify task, then a correction and the fabrication check, then the misconception named and the point that a cited source may not exist or may not say what was claimed (branch code; dry-run on Wednesday) | **No literacy move:** check the console for `source_conflict`; retype once. Then go to L2 (the recorded episode). |
| | **Plan B:** show `demo-showme`'s progress (captured JSON or the printout) and the designed fabrication options card, labelled "on our branch". | captures | n/a |
| 1:30–2:00 | Type **"How do I calculate price elasticity of demand?"** | Console prints `tutor_turn demo-weak … ok`. A quick check on *PED: definition* with lettered options (captured). | **Tool not called:** open the tools menu, check eduX is on, open a new chat and retype. After 30 s, go to **L1**. **The chatbot answers without the plan:** type "Call tutor_turn first, then follow its plan." |
| 2:00–2:30 | Type the **wrong letter**: the option "PED measures how much the price changes when demand changes". | Feedback names that misconception and also corrects "divide the change in price by the change in quantity" (held from two days ago). Then point 1 of 2 with one worked line, then a check (captured). | **Reply skips the misconception:** show the plan JSON in the terminal and say "the plan told it to; chatbots don't always comply, which is why the server scores letters itself". |
| 2:30–3:00 | Type the **right letter**, then re-run `state`. | *PED: formula* rises 0.14 → about 0.40, and the old misconception clears (captured). | **Slow (> 20 s):** "the server answered in milliseconds; the wait is the chatbot writing." After 45 s, go to **L2**. |
| 3:00–3:30 | Show the printed split screen: "Same question: this student knows the groundwork, so they get an intuition question instead." | captures | n/a |
| 3:30–4:00 | Feasibility and who it's for. Point at the console times and the passing checks. "This is an adult team account. For students under 18, the route is a school-managed chatbot; Microsoft Copilot Studio is the best documented one, and we haven't tested it yet." Invite the judge to type a question. | Any course question gives a plan | **Off-course question:** the plan is empty or a brief answer. Say so honestly: "it only plans for the course it knows". |

**Order matters (Plan A).** A Verify task left waiting may take the question slot after two course replies (`literacy.max_waits = 2` on the branch). Either finish the literacy episode with the four-option answer, as scripted, or run PED first. Confirm which order works on Wednesday.

**The PED run uses the prerequisite path.** `demo-weak` gets a prerequisite check first, which is where bug 2's step-back loop shows ([06](06-settings-simulation.md)). Until rec 11 is built, don't let a judge keep answering prerequisite checks in the same session: reset and open a new chat.

**Fallback ladder.** Decide in under 30 s, and never debug in front of a judge:
- **L0:** live in claude.ai through the tunnel.
- **L1:** local only. `scripts/check_mcp.py` scrolls past (about 25 s), plus `python -m edux.cli context --student demo-weak --message "How do I calculate PED?"` to show the plan. No network needed (Graham, w1-07-07 ✓).
- **L2:** the offline recordings (PED, and the literacy episode or the progress shot).
- **L3:** the printed one-pager.

**Known failure modes:**
- **Crash after many right answers (bug 1).** `tutor_turn` raises `ZeroDivisionError` once a part's `p_known` hits 1.0. If the console shows it, go to L2 and reseed between judges. Rec 11 removes it.
- **Tunnel restarted.** A quick tunnel gets a new host on every restart, so `ALLOWED_HOSTS`, the connector URL and the server all need changing (about 2 minutes). Go to L1 and fix it between judges. Start one tunnel at T-60 and never restart it. Keep a phone hotspot as backup.
- **Message caps.** The plan's message caps were not checked (read-only rule). Use a paid account, and keep L2 ready.
- **ChatGPT.** Don't demo it live. Every eduX tool counts as a write action there and asks for confirmation each turn (w1-05-05 ✓).

## C. Pre-demo checklist (read-and-do)

One person reads each item aloud; the driver does it and answers "checked". Each list has at most five items (our choice, after aviation and surgical checklists; w1-07-09 ~, w1-07-10 ~; this is an analogy, not evidence about demos).

**Wednesday 18:00: the gate**
1. 05e merged, or the exact expo build fixed, with the three 06 bug fixes in (rec 11). Its `check_mcp.py` and the three new tests pass. Save the output.
2. The literacy episode has run once end to end in claude.ai on the adult account. Plan A or B decided and written on the sticky note.
3. Pack wording fixed (rec 2) and the literacy options rewritten without m2 (rec 12), loaded, `ingest.cli validate` clean, options re-captured and balanced.
4. Intuition note rewritten (rec 6).
5. Paid adult account ready, with the connector added, web search off, and the set-up text in the project instructions.

**T-24 h (Wednesday evening)**
1. Video exported, with burned-in age captions and a separate caption track.
2. L2 recordings saved in two places.
3. L3 one-pager printed.
4. Keys reseeded after recording if any were visible.
5. Five timed rehearsals done, two with forced failures.

**T-60 min (at the venue)**
1. Mains power. Notifications off. Browser zoom 125%. Large terminal font.
2. Venue wifi tested; hotspot on standby.
3. `scripts/demo.sh` running. Tunnel started once; `ALLOWED_HOSTS` and the connector URL updated; server restarted.
4. One full dry run of §B, then `seed-demo --reset` and a new chat.
5. No keys on any screen.

**Before each judge (30 s)**
1. `python -m edux.cli seed-demo --reset` prints "keys kept".
2. New chat open, connector on.
3. Terminal `state` pane cleared.
4. Talker and driver agree on Plan A or B.

**If anything fails:** say "here's the recorded run", move down the ladder, and fix it after the judge leaves.

## D. Bugs and confusing outputs found while capturing

These are for the build team. None is fixed. Unless marked, they were seen on `main` with the example pack.

**Found by simulation in wave 2 ([06](06-settings-simulation.md)); fix before filming (rec 11):**
- **S1. Divide-by-zero crash.** `p_known` reaches exactly 1.0 (no upper clamp, `edux/learner.py:634-637`); the next exchange divides by zero (`edux/learner.py:457`). A probe hit it after 44 correct checks on one part (w1-06-01 ✓).
- **S2. Step-back loop.** Once a part is flagged stuck, the flag never clears in that session, and 12 of 14 consecutive plans were the same prerequisite check (`edux/plan.py:332-337`; w1-06-02 ~).
- **S3. "Quiz me on what's due" misses the reviews.** A message with no parts inherits the last focus, so the `reviews_only` branch is never reached (`edux/service.py:246-247`; w1-06-03 ✓). This is likely the cause of item 8 below.

**Found while capturing in wave 1:**

1. **MCQ give-away.** The correct option lacks a full stop in 6 of 6 option sets and is the shortest in 5 of 6. Measurement and root cause: [04](04-economics-education.md), "The MCQ give-away, measured".
2. **The check on "Keep the minus sign" reuses distractors about the formula.** So it tests which line was just shown, while that line is still on screen (panel-teacher #2).
3. **Review MCQs have two options plus `extra_option`** (`tax_incidence_split`, `ped_values`), so the chatbot writes the third option. The `tax_incidence_split` distractor also uses "always" ("Producers always pay the whole tax…"), which gives it away.
4. **After a wrong prerequisite letter, `demo-weak` goes straight on to teaching the target.** *PED: definition* stays "new" (0.12 → 0.17). Step 05d doesn't say whether a missed prerequisite should be re-taught. Answer if asked: "we correct it in one line; the prerequisite is scheduled for review".
5. **One right check clears a misconception about a different point.** `ped_formula_m1` (divide price by quantity) went inactive after a right letter on "percentage change from the original". This may be the intended rule, but it looks odd on screen.
6. **The intuition note is a prerequisite reminder,** not an everyday hook (rec 6).
7. **`demo-secure` and `demo-showme` get identical first turns.** Step 06's done-when expects `demo-secure` to show the anchor (`pes_formula`) and reviews due; neither appears.
8. **"Quiz me on what's due" varies.** `demo-secure` gets a *tax incidence* review and `demo-showme` a *PED values* review. `demo-weak` gets an empty plan, so the chatbot improvises. With a check pending, the same message gets a brief answer and a re-ask instead of reviews.
9. **Decay looks harsh on screen.** `tax_incidence_split` shows p_now 0.00 ("new") against p_known 0.77 after 60 days. Viewers will read that as "knows nothing".
10. **The review date and the half-life look inconsistent.** After two checks, `ped_formula` has a 2.0-day half-life but a review due in 38 days. This may be exam-anchored spacing working as designed. Don't show that column until the learner-model owner confirms it.
11. **`conflict_flagged` on `main` gives no literacy move;** the flag is only stored. On the 05e branch it triggers a how-AI-works check on confidence. You can't make the chatbot correct itself on cue, though, so don't plan a shot on it.
12. **A content error in the pack:** the correction for `externality_tax_eval_m1` (04). It is not on camera, but a teacher judge may open the pack.
13. **`docs/demo-script.md` is out of date** (rec 8).

## E. Pitch chart from the simulation (rec 14)

From [06](06-settings-simulation.md), "Recommended chart for the pitch". Title: **"eduX tested its own alarms."** Two small grouped bar charts side by side, both far scenario (study 150–90 days before the exam, then stop), current settings against evidence-based settings:

| Panel | Current | Evidence-based settings | Paired difference |
|---|---|---|---|
| "Secure" but not known on exam day | 76% | 55% | −21 pts (95% CI ±6) |
| Parts truly secure at the end (of 9) | 3.9 | 4.7 | +0.8 (95% CI ±0.3) |

- **Always show both panels.** A model that never says "secure" would score 0% on the first panel; the second stops that misleading (w1-06-04 ✓, w1-06-05 ✓).
- Caption on the slide: "Simulation: synthetic students on our 9-part example pack. Not a learning result."
- Say "evidence-based settings", not "tuned" (a different package in 06). Build the chart fresh; don't reuse `sims/results/false_secure.svg`.
- Put it in the deck and on the expo printout (L3). Keep it out of the 2:30 video, which is about AI literacy.

## Later (not before Thursday; for the business plan and Q&A)

- **A teacher view mock-up, labelled as a mock-up.** Misconceptions to reteach and the weakest parts, no chats, groups of at least 6; class AI literacy only in bands and only if the school opts in; never per-student levels or scores (coordinator decision; spec in [05](05-product-features.md) rec 4). It belongs in the deck; [05](05-product-features.md) also allows about 8 s in the video, inside the 15-s cap on mock-ups (see the note under the ranked table).
- **An answer-first mode for students in a rush,** with the check offered after and skippable (panel-student #1).
- **A validity plan for literacy scores:** agreement with a teacher's ratings on synthetic messages, and slower knowledge-tracing settings for literacy parts (panel-judges #3).
- **School routes:** test Copilot Studio; set `readOnlyHint` on `get_my_progress` so ChatGPT stops asking for confirmation on that tool ([05](05-product-features.md) rec 10).
- **A literacy moment inside homework,** not only on research questions (panel-student #2).

## Considered and rejected

- **Leading the video with PED.** The judges panel scores problem fit at 2 when the video shows elasticity rather than AI literacy.
- **Narrating "three students, three plans".** The captures show two plans.
- **Faking the 05e moment** with hand-written chat or JSON. It is a credibility risk at an expo where judges ask questions.
- **Showing a 16- or 17-year-old on consumer claude.ai,** or captioning a demo student as under 18 on it. The terms are 18+ (w1-05-02 ✓).
- **Building the literacy shot on self-correction** (`conflict_flagged`). It can't be triggered on cue.
- **Ending on "Verify: secure".** That invites the objection that one self-report makes Verify secure.
- **Three students live in three chats.** One connector on the free plan, a key per student, and triple the failure points.
- **Demoing ChatGPT live.** Unrehearsed, and it asks for confirmation on every turn.
- **A music bed, stock footage or a full on-screen transcript** (w1-07-01 ✓: redundancy has the weakest median effect, 0.10).
- **A 3:00 video.** 2:30 leaves a margin.

## Panel objections this report answers or leaves open

| Objection | Status |
|---|---|
| "A revision tutor, not an AI-literacy entry" (judges #1) | **Recommended** (Plan A: definition first, a 72-s literacy episode, PED cut to 20 s; not filmed yet). **Only partly by Plan B.** |
| "Your demo corrects a true belief" (m2; judges w2 #1) | **Recommended:** shots 4c–4d rewritten (rec 12), search off; needs [02](02-ai-literacy-assessment.md) rec 3 in the pack before filming. |
| "Where is your definition?" (judges #2) | **Partly here:** segment 2's rubric card. The full definition and crosswalk are on the deck ([02](02-ai-literacy-assessment.md) rec 1). |
| "Why believe a 'secure' Verify?" (judges #3) | **Avoided on screen, not answered:** we end on How AI works. Validity work is Later. |
| "Your students can't legally use the chatbot you filmed" (judges #4, student Q4, teacher #5) | **Recommended for the video and expo:** adult-account captions and a truthful route statement, written but not yet filmed. The route (Copilot Studio) is untested ([05](05-product-features.md)). |
| "Your assessment gives the answer away" (judges #5, student #3, teacher #2) | **Measured, with a fix named** (rec 2). It needs an owner on Wednesday. The literacy options are matched in length but still need [02](02-ai-literacy-assessment.md) rec 3. |
| "Same question, three plans" | **Corrected:** two plans, plus one history. |
| "I ask a question and get a quiz" (student #1) | **Partly.** Plan B's "shown, then checked" shot shows the current behaviour. The compromise (guided example, skippable check) is in [05](05-product-features.md) and [09](09-safety-ethics.md) rec 14. |
| "It feels like being watched" (student #4) | **Partly.** If a caption is used, take it from [05](05-product-features.md) rec 6: teachers see class patterns from groups of 6 or more, never chats, levels or AI-literacy scores. Not built in `text/` yet. |
| "No teacher view" (teacher #4, judges Q3) | **Partly:** a labelled mock-up in the deck ([05](05-product-features.md) rec 4). |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-07-01 | Mayer's median effects: coherence 0.86, signalling 0.70, segmenting 0.67, pre-training 0.78, modality 1.00, redundancy 0.10 | theory (author's summary) | lab experiments; population not stated in the chapter | learning | ✓ |
| w1-07-02 | Signalling meta-analysis: d = 0.38, 44 effects, 29 studies, 2,726 participants | meta-analysis | mixed ages | learning | ~ abstract level only |
| w1-07-03 | Signalling meta-analysis: retention g = 0.53, transfer g = 0.33 (103 studies, ~12,200 participants) | meta-analysis | about 14% secondary pupils | learning | ~ secondary source; CIs not checked |
| w1-07-04 | Segmenting meta-analysis: small-to-medium gains in retention and transfer (56 investigations) | meta-analysis | mostly university | learning | ~ abstract via secondary snippets; load and time claims secondary only |
| w1-07-05 | Seductive details hinder learning (g = −0.33; worse when pace is not learner-controlled) | meta-analysis | mixed | learning | ~ secondary only |
| w1-07-06 | Shorter MOOC videos are much more engaging (6.9M sessions) | correlational | adult MOOC learners | engagement (not learning) | ✓ |
| w1-07-07 | Graham: say what it is in the first sentence, get to the demo fast, one talks and one drives, run the server locally | practitioner | startup founders | none (opinion) | ✓ |
| w1-07-08 | YC: one point per slide, about seven words, one best presenter, rehearse | practitioner | YC founders | none (opinion) | ~ the guide says demos seldom work in modern Demo Day talks, not that they "often fail under time pressure" |
| w1-07-09 | Surgical checklist: deaths 1.5% → 0.8%, complications 11.0% → 7.0% | quasi-experimental | surgical patients 16+, 8 hospitals | safety (not learning) | ~ abstract only |
| w1-07-10 | NASA flight-deck checklist report ends with design guidelines | official document | airline crews | policy | ~ abstract only |
| w1-07-11 | A hackathon guide: video should be only a demo, at most 2 minutes; a live demo is the best proof | practitioner | one US hackathon (not EduX) | none (rules) | ✓ |
| w1-07-12 | Duarte: pitches alternate between "what is" and "what could be" | practitioner (secondary) | business presentations | none | ~ the cited source doesn't mention ending on the reward; that is in the book itself, not read |
| (captures) | 51/51 MCP checks pass on the current build (without 05e); median `tutor_turn` 14 ms; zero network calls in captured runs | our run (synthetic demo students, example pack) | n/a | cost / feasibility | not verified; reproducible via `sims/capture_demo.py` |
| (branch) | 05e fabrication-check options are matched in length (61, 57, 56, 56 characters, no full stops); absolute wording remains, and the set still includes m2 ([02](02-ai-literacy-assessment.md) rec 3 rewrites it) | our measurement of `ingest/ai_literacy/` on `build/05e-literacy-coaching` | n/a | n/a | not verified |

The economics MCQ give-away count (correct option lacks a full stop in 6/6 sets) has its home in [04](04-economics-education.md).
