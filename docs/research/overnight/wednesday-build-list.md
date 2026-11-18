# Wednesday build list (18 November)

**Five tested patches, check_mcp 74/74 after every one.** Wave 4 turned the build fixes into a patch series, `sims/fixes/combined/0001–0005`. Each patch applies on top of the one before it, on the 05e branch. A blind integration verifier (set Q) applied them in order, merged four conflicts by hand, and ran `check_mcp.py` after each step: 74/74 every time. The verifier also reran each fix's headline measurement on the stacked tree. Every number below is from that rerun (`work/w4/verify-Q.json`; the outputs are in `sims/fixes/combined/results/`). Where a scout's notes disagree with it, the verifier's rerun wins.

All results are **simulation: synthetic students or scripted turns, example pack, 05e branch.** None of them measures real students or claude.ai.

The words to record are in [pitch-script.md](pitch-script.md); the shot list and expo script are in [demo-plan.md](demo-plan.md).

## Summary
- **The series is 4–5 h of build work.** Apply it in this order: fast-forward 05e → 0001 core → 0002 focus → 0003 Verify scoring (+ migration 010) → 0004 MCQ (code + pack rows) → 0005 decay (optional). The verifier's hours: 0.5, 0.5, 1, 1.5, 1.
- **What it fixes on camera:**
  - Verify ends **developing (0.748)** in all six Plan A takes. On the bare branch it ended **new** in four of them, after the student had found the problem.
  - A testwise student who knows nothing now gets 0.28 of the MCQs right, against chance 0.31. Before, it was 0.96.
  - Research lines no longer pull PED or tax into focus: 3 of 43 lines do, down from 15 of 43.
  - The crash after long right-answer runs is gone (w4-fix-combined-1 ✓, w4-fix-verify-1 ✓, w4-fix-mcq-1 ✓, w4-fix-focus-1 ✓, w4-fix-core-1 ✓).
- **Every single skip was tested.** Leave out any one of 0001, 0003, 0004 or 0005 and the rest still applies, at 74/74. **Leaving out 0002 means using the variant of 0003**, so decide on 0002 before you apply 0003. Only single skips were tested, not pairs, and cuts after 11:30 come off the top of the stack (cut line).
- **The safest cut is 0005 (decay).** Plan A is identical with or without it. The cut you must not make is 0003: without it, Verify falls after the student catches the bad source, which is the opposite of the story.
- **Known residuals,** none of them on the Plan A script:
  - a student who keeps failing gets 7 reteaches in a row;
  - "what's due" works only with the exact wording;
  - the focus fix loses 2 of 21 genuine course questions;
  - the Verify fix works only if the chatbot sends `source_conflict`;
  - steps 4 and 5 change some on-screen wording and levels, so re-capture after them.
- **Unchanged:** the 16:30 freeze, the 18:00 gate and the cut line.

## Before you start (B1, 5 min)

The patches live on the research branch (`sims/fixes/` is untracked there). After the fast-forward, the 05e tree won't contain `docs/research/overnight/` unless you copy it in. Set one variable and use it throughout:

```bash
cd <repo root, on main after the fast-forward>          # "the 05e tree"
FIX=docs/research/overnight/sims/fixes                   # if the research folder is in this tree
# FIX=/home/vishnu/edux26-research/docs/research/overnight/sims/fixes   # otherwise, the absolute path
PY=/home/vishnu/edux26/.venv/bin/python
```

**Apply each patch with a dry run first** (from the 05e tree):
```bash
git apply --check docs/research/overnight/sims/fixes/combined/000N-*.diff && \
git apply docs/research/overnight/sims/fixes/combined/000N-*.diff
```
- If the research folder isn't in the tree, use `$FIX/combined/000N-*.diff`, the absolute path.
- `git am` and `patch -p1` also work; each gave a byte-identical tree.
- Commit after each step, so that a later cut can rebuild cleanly.

**The check after every step (about 1 min):**
```bash
bash $FIX/combined/harness/check.sh "$PWD" 8765 /tmp/claude-1000/check_N.txt
grep -c '^ok' /tmp/claude-1000/check_N.txt; tail -2 /tmp/claude-1000/check_N.txt
```
- **Expect:** `74`, then `all checks passed` and `exit 0`.
- The harness loads the example pack, runs `seed-demo --reset` and serves on localhost. It uses a fresh data folder under `/tmp/claude-1000/`, never `data/`.

**Test copies (B2).** The rehearsal, Verify-scenario and probe scripts refuse to run against anything except a copy under a fixed `/tmp/claude-1000/` path. So B2 tests on a copy and never adds files to the build tree:
```bash
cp -r "$PWD" /tmp/claude-1000/w3-07/sN          # for run_episode.py
cp -r "$PWD" /tmp/claude-1000/w4-fix-verify/sN  # for verify_run_episode.py (step 3)
```

**The Plan A rehearsal (about 3 min, B2):**
```bash
cd $FIX/../demo-05e
$PY run_episode.py --code /tmp/claude-1000/w3-07/sN --label sN --out /tmp/claude-1000/w3-07/cap \
    --scenario final final_ticks_ad clean plan_now then_ped recommended
```
- **Check the console for OVER BUDGET.** The verifier's Plan A digest reports no errors, but it does not record the reply budget. The largest result had only about 80 characters to spare before wave 4 (w3-07-c2 ~). 0003 adds a `skipped` field to progress and 0004 changes option texts, so **the budget has not been checked on the patched stack.**

**Line numbers.** Every `file:line` in the reports is for `main`. After the fast-forward the lines shift, so find the code by function name.

`harness/run_all.sh` rebuilds and reruns everything, but it was transcribed from the verifier's commands and **has not been run end to end**. Use the per-step commands here.

## Owners (four roles)

| role | Wednesday |
|---|---|
| **B1 · Build lead** | The fast-forward and every patch: applies it, runs `check.sh`, commits. Owns the freeze. |
| **B2 · Second builder** | The step-specific test after each patch (below) and the Plan A rehearsal. Owns 0005 and the re-capture of the demo trees. |
| **E · Economist** | **Reviews 0004's drafted pack rows from 09:30**: 20 mark points, 10 misconceptions, the four How AI works sets. Checks the economics in the dry run. |
| **P · Pitch lead** | Pastes the Challenge 1 brief into `challenge-brief.md` (needs a human). Line card, adult account, deck, dry run and filming. |

## The series, step by step

Clock times assume a 09:00 start. The steps are serial: each patch needs the one before it.

| step | what | owner | hours | when |
|---|---|---|---|---|
| 0 | Fast-forward `main` to 05e | B1 | 0.5 | 09:00–09:30 |
| 1 | 0001 core | B1, B2 tests | 0.5 | 09:30–10:00 |
| 2 | 0002 focus (**decide before 0003**) | B1, B2 tests | 0.5 | 10:00–10:30 |
| 3 | 0003 Verify scoring + migration 010 | B1, B2 tests | 1.0 | 10:30–11:30 |
| 4 | 0004 MCQ code + pack rows | B1 applies; E's review 09:30–11:30 | 1.5 | 11:30–13:00 |
| — | lunch | | | 13:00–13:30 |
| 5 | 0005 decay (**optional**; merged by 15:00 or dropped) | B2 | 1.0 (+0.5 re-capture) | 13:30–15:00 |
| 6 | Outside the series (optional, each with its own check) | B1 / E | ≤ 1 | 15:00–15:45 |
| — | **Freeze and final checks** | B1 | — | until **16:30** |
| 7 | Dry run in claude.ai; **18:00 gate** | all | 1.5 | 16:30–18:00 |
| 8 | Film Plan A or Plan B | all | 3.0 | 18:00–21:00 |
| 9 | Label-agreement study (optional) | all | 2 × 4 people | 21:00–23:00 or Thursday |

### Step 0 · Fast-forward `main` to `build/05e-literacy-coaching` (B1, 0.5 h)
- **On camera, this gives you** the whole AI-literacy episode: the Ask and Verify tasks, the How AI works question and the record. Without it, Plan A doesn't exist.
- **How:** the branch already contains `main` and is 14 commits ahead with no conflicts (coordinator; w3-07-c6 ✓).
- **Test:** `check.sh`, expect 74/74. The verifier's base run was 74/74.
- **If skipped:** never skipped. If it fails, film Plan B ([pitch-script.md](pitch-script.md) §1b).

### Step 1 · `0001-core-fixes-…diff` (B1 0.5 h; B2 tests)
- **What it fixes.** Three bugs that could show at the expo or off script:
  - **The crash.** `p_known` is clamped to [0.001, 0.999]. On the bare branch it hit exactly 1.0 at answer 44 of 200, and the next exchange raised `ZeroDivisionError`; so did a row already saved at 1.0. Now it peaks at 0.999 and both run (w4-fix-core-1 ✓). For seeded `demo-showme`, 39 more right answers on `ped_definition` would have crashed it: a long expo day could get there.
  - **The step-back loop.** A student wrong on every `ped_formula` check got the same prerequisite check in 12 of 14 plans. Now it is 1 of 14 (w4-fix-core-2 ✓).
  - **"Quiz me on what's due."** It taught the old focus. Now it gives the due review (`ask_mcq pes_definition`). This works **only for the exact prompt wording**, in any case or punctuation (w4-fix-core-3 ~).
- **Apply:** `git apply docs/research/overnight/sims/fixes/combined/0001-core-fixes-clamp-p_known-one-step-back-per-stuck-par.diff`
- **Test.** Run `check.sh` (expect 74/74). Then B2 runs the probes **on a copy**: the probe uses the tree it sits in, so copy the tree to `/tmp/claude-1000/probe-s1`, and copy `sims/edux_sim.py` and `sims/fixes/probes_w4.py` into the copy's `docs/research/overnight/sims/{,fixes/}`. Never into the build tree.
  ```bash
  cd /tmp/claude-1000/probe-s1
  PYTHONPATH=$PWD $PY docs/research/overnight/sims/fixes/probes_w4.py /tmp/claude-1000/probes-data-s1
  ```
  Expect, as in `results/probes_s1.txt`:
  - `max p_known 0.999 … exchange ok; legacy row at 1.0: exchange ok`;
  - both "Quiz me on what's due" lines → `ask_mcq pes_definition review`;
  - `1 of 14 plans were a step-back prerequisite check`.
- **If skipped (never cut; it carries the clamp):** the verifier tested the series without 0001 (74/74), and Plan A is unaffected. But off camera the crash, the loop and quiz-me on the old focus all come back. If it somehow isn't in:
  - reset between judges;
  - don't let a judge keep answering prerequisite checks;
  - make no "reviews due" claim.

### Step 2 · `0002-focus-…diff` (B1 0.5 h; B2 tests)
- **What it fixes.** A research or other message never sets or changes the course focus (the "side turn").
  - Off script, lines like "what was inflation like?" pulled PED or tax into focus, and the next reply taught a course part nobody asked about.
  - End-to-end false focus falls from **15/43 to 3/43** on the focus test set, and from 9/18 to 3/18 on the holdout (w4-fix-focus-1 ✓).
  - Plan A is identical, because the line card already uses focus-safe wording.
  - What it doesn't apply: the resolver name-gate and the sources fallback (two other draft diffs).
- **Apply:** `git apply docs/research/overnight/sims/fixes/combined/0002-focus-a-research-or-other-message-never-sets-or-chan.diff`
- **Test.** Run `check.sh` (74/74). Then, on a fresh data folder with the pack loaded:
  ```bash
  EDUX_DATA_DIR=/tmp/claude-1000/focus-s2 PYTHONPATH=$PWD $PY $FIX/focus_measure.py --label s2
  ```
  Expect `saved false focus 3/43` and `genuine saved right focus 14/21`. Add `--holdout` and expect 3/18.
- **Cost.** It loses 2 of 21 genuine course questions: right focus falls from 16/21 to 14/21.
  - Research questions that do name a course part go from 2/5 to 0/5, because a research turn never moves the focus, even when it is right.
  - The 3 false-focus lines left are homework (2) and a name-word trap (1).
- **If skipped:** you must use **`variants/0003-alt-verify-scoring-without-0002.diff` in place of 0003**, because 0003 doesn't apply without 0002. The verifier tested this at 74/74.
  - **Decide before 10:30, when 0003 goes in.** Dropping 0002 after 0003 is in means reverting both.
  - On camera, film strictly from the line card. Never type "give", "link", "ONS", "first", "cost", "different" or "shows".
  - At the expo, use demo-plan §B's honest script. This is the one break with no clean live workaround.
  - The verifier did not rerun the as-written take without 0002.

### Step 3 · `0003-verify-scoring-…diff`, with migration 010 (B1 1 h; B2 tests)
- **What it fixes: the story of the literacy episode.**
  - A reported dead page or mismatch now scores Verify 1, so Verify reaches **developing (0.748)**. On the bare branch it fell to **new (0.143)**: catching the bad source lowered the score.
  - An ignored Verify task, or an ignored How AI works check, is now a **skip**. It records no evidence and shows `skipped: 1` in progress. Before, it was scored 0 (w4-fix-verify-1 ✓).
  - In Plan A, Verify ends developing in all six takes. Before, it was new in clean, plan_now, final_ticks_ad and then_ped. The re-ask at turn 4 disappears.
- **Apply.** `git apply docs/research/overnight/sims/fixes/combined/0003-verify-scoring-a-found-dead-or-mismatched-source-sco.diff`
  - If 0002 was skipped, apply `$FIX/combined/variants/0003-alt-verify-scoring-without-0002.diff` instead.
  - **Migration 010** (`literacy_skip`, a new append-only table) is in the patch. It runs by itself when the database opens (`db.run_migrations`), so there is no manual SQL. It is additive.
  - Run `python -m edux.cli seed-demo --reset` afterwards so retakes start clean.
- **Test.** Run `check.sh` (74/74). Three expectations changed inside it, because an ignored task or check is now a skip rather than 0. The count stays 74.
  - Then, on the copy under `/tmp/claude-1000/w4-fix-verify/s3`, run:
    ```bash
    cd $FIX
    $PY verify_run_episode.py --code /tmp/claude-1000/w4-fix-verify/s3 --label s3 \
        --out /tmp/claude-1000/w4-fix-verify/vcap --scenario dead_ad_then_ok verify_ignored final_ticks_ad
    ```
  - Expect Verify `0.748 developing` for the dead-page and mismatch runs, and `0.300`, no evidence, `skipped 1` for `verify_ignored`.
  - Then run the Plan A rehearsal: Verify should read developing in all six takes, and there should be no OVER BUDGET.
- **Residual: it depends on the label.** If the chatbot leaves out `source_conflict`, nothing changes: Verify stays new and the task is re-asked. So check that label in every dry-run tool call.
- **By design,** every found problem scores 1, whatever is ticked. A matched check (no conflict) is now graded: a, c, d gives 0.636, and a, b, c, d gives 0.748.
- **If skipped (not recommended).** In the main take, Verify ends new after the student found the problem. The old workarounds come back:
  - send 4c as the Verify answer with points a, c and d;
  - after a dead-page take, never show Verify in 4d;
  - at the expo, finish the episode before any PED question.

### Step 4 · `0004-mcq-give-away-…diff`, code and pack rows (B1 1.5 h; E reviews the rows)
- **What it fixes.** The right MCQ option could be spotted from its punctuation or length.
  - A testwise student who knows nothing scored **0.96** (chance 0.31). Now it is **0.28** (chance 0.305): economics 0.29 against 0.31, How AI works 0.25 against 0.25 (w4-fix-mcq-1 ✓).
  - Keys now come only from a part's mark points, shown without a closing full stop. A part with no mark points gets an open check (show, then explain back), and ingest warns about it.
  - Economics MCQs go from 21 to 28.
  - The patch also replaces m2 in the fabrication set, the option the coordinator ruled must not be taught. It corrects `externality_tax_eval_m1` too: a tax at the right level removes the welfare loss, not all pollution.
- **Both halves are needed.** The code alone still scores 0.83. On the old pack it turns 7 of 9 parts into open checks, and `check_mcp` stops at check 1.
- **E's review (09:30–11:30, before B1 applies).** Read the drafted rows in `$FIX/mcq-pack-proposal/`: the 20 economics mark points, 10 misconceptions and the four How AI works sets. They are the scout's wording, marked `draft`. Order of work:
  1. B1 applies 0004 as tested.
  2. E's corrections go into the CSVs as a separate commit.
  3. Rerun `check.sh` and `testwise.py`.

  Any rewording means the rows are no longer the tested ones, so keep the form rules:
  - keys as plain claims, no closing full stop;
  - lengths within 0.7–1.3× the distractors' median (our choice);
  - no "always", "only" or "on purpose".

  **Don't add `ped_values_m2`.** It changes the demo target and breaks `check_mcp`, which hard-codes `ped_formula`; add it after filming. `ped_formula` still has no sign-error misconception: optional, step 6.
- **Apply:** `git apply docs/research/overnight/sims/fixes/combined/0004-mcq-give-away-key-is-a-mark-point-in-option-form-ope.diff`. The CSVs in `ingest/ai_literacy/` have CRLF line endings, so it prints "trailing whitespace" warnings. It still applies.
- **Test.** Run `check.sh` (74/74) and `python -m ingest.cli validate`. The only warning should be `ped_values` having 1 misconception. Then, on a fresh data folder with the pack loaded:
  ```bash
  EDUX_DATA_DIR=/tmp/claude-1000/tw-s4 PYTHONPATH=$PWD $PY $FIX/testwise.py --json /tmp/claude-1000/tw-s4.json
  ```
  Expect about 0.28 overall against chance about 0.31. Then run the Plan A rehearsal.
- **On-screen change: re-capture.** The fabrication options change. The misconception shown in progress after an m2 pick becomes "Its links are tested before you see them, so the site is down for now". The 4c voiceover in the pitch script now names m1 (the rehearsal's pick), which is unchanged.
- **If skipped.** Hold on the first line of each reply and never close up on options. The old m2 is still in the set, so in 4c cut from the question straight to the reply after an m1 pick.

### Step 5 · `0005-decay-…diff`, optional (B2, 1 h + 0.5 h re-capture; merged by 15:00 or dropped)
- **What it fixes.** Nothing in Plan A, which is identical. It fixes what a judge could find in the `state` pane or on a ranking slide:
  - **A part the student only talked about** (14 exchanges, no check) read **0.763, secure**. Now it reads **0.300, new**.
  - **A never-answered prerequisite** read 0.440. Now it reads 0.300, and it gets a prerequisite check.
  - **How AI works ranking** (none vs strong, week 8, N = 60 a group, about ±0.05) rises from 0.51/0.31 to **0.85/0.88**. Ask stays at 1.00 and Verify at 0.94–1.00 (w4-fix-core-4 ✓; simulation: synthetic students).
  - Parts decay towards their starting estimate; Ask and Verify decay towards 0. The "not yet shown" display flag (`fix4b`) is **not** included.
- **Apply.** `git apply docs/research/overnight/sims/fixes/combined/0005-decay-towards-the-starting-estimate-Ask-and-Verify-t.diff`
  - Then run `python -m edux.cli rebuild`, then `seed-demo --reset`.
  - The patch adds one setup line to check_mcp's `waiting_task`.
- **Test.** Run `check.sh` (74/74), then the probes again. Expect `talk_only … 0.300 (new)` and `never-answered ped_formula reads 0.300`, as in `results/probes_s5.txt`.
- **On-screen change: re-capture.**
  - `demo-secure`: `ped_values` becomes new (was developing), `pes` secure (was developing), `indirect_taxes` developing (was new).
  - `demo-showme`: `pes` becomes developing and `pes_definition` secure (both were new).
  - Plan B's "about 35 minutes" line becomes 31. Plan B never speaks it.
  - Re-shoot or re-check any progress shot of these two students.
- **If skipped (the safest cut).** Plan A is unchanged. Off camera, a talk-only part can still show secure, and How AI works ranking stays near chance (0.3–0.5). So put no "we can rank AI literacy" claim for How AI works on any slide, and don't linger on `state`.

### Step 6 · Outside the series: optional, not tested with it (≤ 1 h; each needs its own `check.sh`)
None of these is in 0001–0005. Apply them only after 0005 (or after 0004 if 0005 is cut). Each needs its own 74/74 and a Plan A rerun before 15:45; otherwise drop it and use the workaround.

| item | owner | time | if not done |
|---|---|---|---|
| **Literacy settings:** `literacy.ask_min_features = 3`, `ail_question` guess .30, `ail_unprompted` guess .20 ([02](02-ai-literacy-assessment.md) rec 2; w2-02-08 ✓, simulated on pre-wave-4 code) | B1 | 15 min + check | **Drop the slide-6 add-on.** 4b keeps 3 or more features anyway |
| A sign-error misconception for `ped_formula` ("keep the minus sign") | E | 30 min + validate | Nothing on camera |
| Per-part How AI works counts ("checked n, right m") in `get_my_progress` | — | not built | In 4d, highlight only the "still held" line, never a How AI works level |
| `fix4b` "not yet shown" flag | — | not in the series | No "not yet shown" line |

### Freeze and final checks (B1, until 16:30)
1. Run `check.sh` on the frozen tree: 74/74.
2. Run the Plan A rehearsal: no OVER BUDGET.
3. Run `seed-demo --reset`.
4. Re-capture the progress views if step 4 or 5 is in.
5. **Check shot 5.** The verifier's rerun covered only the literacy episode, but 0004 changes how checks are built and 0005 moves `demo-secure`'s levels. On the frozen build, send "How do I calculate price elasticity of demand?" as `demo-secure` and as `demo-weak`. Confirm the first moves:
   - `demo-secure`: an intuition question;
   - `demo-weak`: a check on the definition, then last time's mistake corrected.

   If they differ, P edits the shot-5 words before filming.

**Nothing merges after 16:30.**

### Step 7 · Dry run in claude.ai, adult account, web search off (16:30–18:00)
- **Who:** P drives, B1 watches labels and the console, E checks the economics, B2 stands by.
- **How:**
  - Type the line card verbatim.
  - Expand every tool call and check the labels: 4a and 4b `research`; 4b with 3 or more features; 4c `source_conflict: true`. **With 0003, the last one decides whether Verify rises.**
  - Any miss: reset, new chat, retake.
- **The 18:00 gate.** Plan A needs all three:
  - the patched 05e build;
  - `check_mcp` passing with no OVER BUDGET;
  - one end-to-end episode with the right labels and no retake.

  Otherwise, film Plan B ([pitch-script.md](pitch-script.md) §1b). The gate doesn't wait for fixes.

### Step 8 · Film (18:00–21:00)
- **Who:** P and E drive, B1 watches the console, B2 records the fallback clips.
- **What:**
  - Plan A (§1) or Plan B (§1b) from [pitch-script.md](pitch-script.md).
  - Reset and open a new chat before every take.
  - Then record the two offline fallback clips.

### Step 9 · Label-agreement study (optional)
- **What:** rewrite at least 20 of the 40 draft messages in a student voice. Then two blind raters, two bot runs, and κ pooled per skill ([02a](02a-label-agreement-protocol.md)).
- **If dropped:** slide 6 says "we're checking those labels against two humans", with no number. If it is dropped rather than moved, say "next, we check those labels".

## CUT LINE: if behind at the 16:30 freeze (18:00 gate)

**Never cut:** step 0, **0001** (it carries the clamp; only whole patches were tested, so don't split it), the dry run and filming. Anything not merged and passing by **16:30** is dropped, and its workaround switches on. The **18:00 gate** then picks Plan A or Plan B.

**Cuts come off the top of the stack.** The series is serial, so 0001–0003 are in by 11:30.
- **0002 can be dropped only before 10:30.** Then apply the 0003 variant instead of 0003.
- **After that, drop from the top:** 0005, then the step-6 extras, then 0004.
- **To remove a patch from the middle** (0003, say), rebuild from the 05e commit, applying the series without it. Then run `check.sh` on that exact tree. Don't revert it in place: that is untested, and 0005's `check_mcp` hunk sits on 0003's rewritten docstring.
- Only single skips were tested (each 74/74). If two patches are out, `check.sh` on that tree decides.

Drop in this order, first to go at the top:

| drop order | item | on-camera workaround |
|---|---|---|
| 1 | Step 9, the label study | Move it to Wednesday night or Thursday. Slide 6: "we're checking those labels", with no number |
| 2 | Step 6 extras | Drop the slide-6 add-on. In 4d, highlight only "still held" |
| 3 | 0005 decay | Plan A is unchanged. No How AI works ranking claim; don't linger on `state` |
| 4 | 0004 MCQ | Hold on each reply's first line, with no option close-ups. In 4c, cut past the options to the reply after an m1 pick |
| 5 | 0003 Verify (rebuild without it; not recommended) | Send 4c as the Verify answer with points a, c, d. After a dead-page take, never show Verify. Finish the episode before any PED question |
| — | 0002 focus: only by the 10:30 decision, with the 0003 variant | Film from the line card. At the expo, use §B's honest script |

## Known residuals (flag them; don't demo them)
- **Seven reteaches in a row.** After the single step back, a student who keeps failing `ped_formula` gets 7 reteach-only plans with no question (probe turns 8–14). It is milder than the old loop, but real. At the expo, don't let a judge keep answering wrong (w4-fix-core-2 ✓ note).
- **"What's due" needs the exact wording.** Use the prompt button, or type "Quiz me on what's due". "Can you test me on my reviews?" still teaches the old focus (w4-fix-core-3 ~).
- **The focus fix loses 2 of 21 genuine course questions** (16/21 → 14/21), and every research question that names a course part (2/5 → 0/5) (w4-fix-focus-1 ✓).
- **The Verify fix depends on the chatbot flagging `source_conflict`.** Without the label, Verify stays new and the task is re-asked (w4-fix-verify-1 ✓ note).
- **Steps 4 and 5 change on-screen wording and levels.** Re-capture after them: the m2 text, and the `demo-secure` and `demo-showme` levels listed above.
- **0004's pack rows are draft wording** until E has read them.

## Note for the build docs (research does not edit these)
The patches change behaviour that `docs/build/` still describes the old way. B1 or the doc owner should update, after filming if necessary:
- **`docs/build/reference/learner-model.md`** (around lines 134 and 136): an ignored literacy task or check is "counted as a skip, no evidence", not "recorded as 0". Add the found-a-problem rule: a reported dead or mismatched source scores Verify 1. If 0005 is in, add decay towards the starting estimate, with Ask and Verify towards 0. If 0004 is in, add mark-point-only keys and open checks.
- **The 05e step doc** (`docs/build/steps/05e-literacy-coaching.md`, the "Bad links" section around lines 102–103 and 201): the same Verify and skip rules, and migration 010.
- **Bump `protocol` to `v0.3` in `settings.toml`.** The meaning of a Verify score changed, and none of the patches bumps it.

## Findings (home report for the wave-4 fix findings)

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w4-fix-core-1 | Clamp: the run that hit 1.0 at answer 44 and crashed now peaks at 0.999; a legacy 1.0 row also runs; s1–s5 | simulation | scripted turns, example pack, 05e | system reliability | ✓ |
| w4-fix-core-2 | One step back per stuck part per session: 12/14 → 1/14 step-back plans | simulation | as above | system behaviour | ✓ (then 7 reteach-only plans in a row) |
| w4-fix-core-3 | "Quiz me on what's due" now reaches the due review | simulation | as above | system behaviour | ~ exact prompt wording only; a paraphrase still teaches the old focus |
| w4-fix-core-4 | Decay (b)+(c): talk-only 0.763 secure → 0.300 new; How AI works AUC 0.51/0.31 → 0.85/0.88 | simulation | synthetic students, N = 60 a group | prediction | ✓ (about ±0.05) |
| w4-fix-focus-1 | Side turn: false focus 15/43 → 3/43 (holdout 9/18 → 3/18); genuine 16/21 → 14/21 | simulation | scripted lines, example pack | system behaviour | ✓ |
| w4-fix-verify-1 | Found problem scores 1: Verify 0.143 new → 0.748 developing; ignored task is a skip | simulation | scripted episodes, demo-weak | prediction (validity) | ✓ (needs `source_conflict`) |
| w4-fix-mcq-1 | Testwise hit rate 0.96 → 0.28 (chance 0.31); economics MCQs 21 → 28 | simulation | scripted testwise student | prediction (validity) | ✓ (pack rows are draft) |
| w4-fix-combined-1 | The five patches stack; check_mcp 74/74 after each; six Plan A takes run after steps 2–5 | simulation | 05e export | system reliability | ✓ (`run_all.sh` not run end to end) |
