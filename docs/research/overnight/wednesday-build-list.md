# Wednesday build list (18 November)

> **Follow [RUNBOOK.md](RUNBOOK.md) on the day** (one page: exact commands, tested on a fresh clone). This file is the detailed reference: what each patch fixes, its residuals and the cut line. Where the two differ, the runbook's commands win.

**Eleven patches, check_mcp 74/74 after every one.** Wave 4 turned the build fixes into a patch series, `sims/fixes/combined/0001–0005`. Wave 5 added 0006–0008 (`-w5` files). Wave 6 replaced wave 5's two counters, 0009 and 0010, with fairer ones, **0009b and 0010b (✓ verified, verifier U)**, and added **0011 (MCQ option length rank; ✓ verified, verifier V, with an economics flag on two rows)**. Each patch applies on top of the one before it, on the 05e branch.
- **0001–0005:** a blind integration verifier (set Q) applied them in order, merged four conflicts by hand and ran `check_mcp.py` after each step: 74/74 every time (`work/w4/verify-Q.json`).
- **0006–0010:** a second blind verifier (set S) applied the renumbered files on 0001–0005: offsets only, no conflict, 74/74 after each (`work/w5/verify-S.json`, w5-fix-combined-2 ✓).
- **0009b and 0010b:** blind verifier U applied them on fresh 0001–0008 trees (no fuzz, offset or reject), ran check_mcp (74/74 after each), reran the gaming, probe and Plan A runs, and confirmed all 7 claims (w6-c2b-1 ✓ to w6-combined-3 ✓; `work/w6/verify-U.json`).
- **0011:** blind verifier V applied it on 0001–0008 (74/74) and reproduced the ingest warnings, testwise and gaming numbers (w6-len-1 to -4 ✓). It flagged two economics rows (w6-len-econ ~). The full stack 0008 + 0011 + 0009b + 0010b passing 74/74 is the scout's result (third run; the first two failed only the timing check under load), not the verifier's.
- **Test on a copy with an absolute `PYTHONPATH`, and print `edux.__file__` first.** A relative path silently imports the venv's unpatched 05e `edux` (w6-path-1 ~, w6-path-2 ~). Check from a neutral folder: `cd /tmp && PYTHONPATH=/abs/copy $PY -c 'import edux; print(edux.__file__)'`.
- Both verifiers reran each fix's headline measurement on the stacked tree. Every number below is from those reruns (outputs in `sims/fixes/combined/results/` and `results/w5-S/`). Where a scout's notes disagree with them, the verifier's rerun wins.

All results are **simulation: synthetic students or scripted turns, example pack, 05e branch.** None of them measures real students or claude.ai.

The words to record are in [pitch-script.md](pitch-script.md); the shot list and expo script are in [demo-plan.md](demo-plan.md).

## Summary
- **0001–0004 first (4 h), then 0006–0008, then 0011, 0009b and 0010b (all recommended, tested diffs, verified).** Order: fast-forward 05e → 0001 core → 0002 focus → 0003 Verify scoring (+ migration 010) → 0004 MCQ (code + pack rows) → 0006 stuck ladder and review requests → 0007 labelling text → 0008 Ask guard → **0011 MCQ length rank (step 5f)** → 0009b dead-link report cap → 0010b show-then-pick cap.
  - **0010b is dropped by default.** Start it only if 0009b has passed `check` by 15:00, which means the day is an hour ahead (see "The clock").
  - **0005 (decay) is optional, not a default.** There is no room for it before the 16:30 freeze if 0006–0011 go in. **0009 and 0010 are superseded**: don't apply them.
- **What it fixes on camera:**
  - Verify ends **developing** in all eight Plan A takes: 0.748 without 0009b, **0.740** with it (w6-planA ✓). On the bare branch it ended **new** in four of six takes, after the student had found the problem.
  - A testwise student who knows nothing gets 0.28 of the MCQs right on punctuation and longest-option cues, against chance 0.31. Before, it was 0.96. After 0004 a middle-length cue remained (0.536 on the 28 economics sets; 57% in play). **0011 cuts it to 0.286** (chance 0.312), and no length, position or first-word cue is above 0.375 (w6-len-3 ✓, in-sample). The sequence cue (the key is the one option not in the previous point's check) is not fixed.
  - Research lines no longer pull PED or tax into focus: 3 of 43 lines do, down from 15 of 43.
  - The crash after long right-answer runs is gone (w4-fix-combined-1 ✓, w4-fix-verify-1 ✓, w4-fix-mcq-1 ✓, w4-fix-focus-1 ✓, w4-fix-core-1 ✓).
  - If the chatbot labels the 4c answer `research`, Ask no longer drops to new in the progress shot (0008; w5-fix-guard-1 ✓).
- **What it fixes off camera:** a failing student no longer gets 23 bare reteaches in a row; the stop-or-switch offer comes at turn 8 (0006; w5-fix-stuck-1 ✓). With 0009b, "the link is broken" no longer makes Verify secure (100% → 0% of simulated gamers, shown developing). With 0010b, "just show me, then pick the match" no longer makes parts secure (9 → 0), at a small honest cost: 3.6 → 3.4 parts, but the first secure part takes 8.9 effort-minutes instead of 2.4 (w6-c1b-1 ✓, w6-c1b-2 ✓). With 0011, "drop the longest and shortest option" gets 19% right in play, not 57% (w6-len-4 ✓).
- **Every single skip of 0001–0010 was tested.** Leave out any one patch and the rest still applies, at 74/74. 0011 shares no file with 0009b or 0010b, so it can be left out alone. 0010b without 0009b needs `variants/0010b-alone-…` (74/74). **Leaving out 0002 means using the variant of 0003**, so decide on 0002 before you apply 0003. Only single skips were tested, not pairs. Cuts after the freeze come off the top of the stack (cut line).
- **Never cut 0003.** Without it, Verify falls after the student catches the bad source, which is the opposite of the story.
- **Team decisions (needs a human):** the empty plan after a matched Verify answer labelled `other` (step 5c); the `source_conflict` rule in 0007 (Option A); E's read of 0004's pack rows and 0011's 22 reworded rows, especially `tax_incidence_split_p2`/`_m2` (step 5f); 0005 or not.
- **Unchanged:** the 16:30 freeze, the 18:00 gate and the cut line. New patches come off the top first.

## Before you start (B1, 5 min)

The patches are committed (tracked) on branch `research/overnight`. [RUNBOOK.md](RUNBOOK.md) §0–1 gives the tested set-up: `ROOT`, `PY`, `SCRATCH`, `FIX` and `C` set once; `main` fast-forwarded to `build/05e-literacy-coaching` (`git merge --ff-only`, 14 commits); the fixes committed on a new branch `build/wednesday-fixes`, never on `main`; the patches copied outside the build tree with `git archive origin/research/overnight docs/research/overnight/sims | tar -x -C "$W/research"`; and a portable `check` function in place of `harness/check.sh` (which hard-codes one laptop's paths).

**Testing a patched copy: always use an absolute `PYTHONPATH`, and print `edux.__file__` before trusting a number** (`cd /tmp && PYTHONPATH=/abs/copy $PY -c 'import edux; print(edux.__file__)'`). A relative path silently runs the venv's unpatched 05e code (w6-path-1 ~).

**Apply each patch with a dry run first.** The runbook uses `git apply --check "$C/<file>" && git apply "$C/<file>"` for all ten patches (tested on a fresh clone, 18 Nov). The notes below are the earlier history:
```bash
git apply --check docs/research/overnight/sims/fixes/combined/000N-*.diff && \
git apply docs/research/overnight/sims/fixes/combined/000N-*.diff          # 0001–0005 only
```
- If the research folder isn't in the tree, use `$FIX/combined/000N-*.diff`, the absolute path.
- **From 0006 on, name each file in full.** `0006-*.diff` matches two files (`0006-stuck-…` and `0006-w5-stuck-…`), and the `000*.diff` glob picks up the old `0006b`/`0006c` files and misses 0010. Use only the `-w5` files for 0006–0008, then the `-w6` files `0011-…`, `0009b-…` and `0010b-…`. Never the superseded `0009-w5`/`0010-w5` files.
- **For 0006 onwards use `patch -p1`**, which verifier S and the wave-6 scout tested (it also tested `git am --keep-cr`; `git apply` was not tested on these files):
  ```bash
  P=$FIX/combined/0006-w5-stuck-ladder-and-review-requests.diff
  patch -p1 --dry-run < "$P" && patch -p1 < "$P"
  ```
- `patch -p1` works for 0001–0005 too, and so does `git am --keep-cr`. **Plain `git am` strips the CRs from 0004's two CSVs**, so the tree differs from the tested one.
- Commit after each step on `build/wednesday-fixes` (`fix: apply 000N …`), so that a later cut can rebuild cleanly. Don't push until the freeze passes.

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
- **Watch for OVER BUDGET.** On the full stack, the largest `check_mcp` result was **2,395 of 2,400 characters** (verifier W): 5 to spare. In the runbook's fresh-clone test it reached **2,399 after 0004**: 1 to spare (the count varies with the shuffled options). Watch the over-budget count in `check` and the server console in the dry run. Fallback if anything goes over: drop one reference block from that move's context, or trim the longest text in `text/`, then rerun `check`.

**Line numbers.** Every `file:line` in the reports is for `main`. After the fast-forward the lines shift, so find the code by function name.

`harness/run_all.sh` rebuilds and reruns everything, but it was transcribed from the verifier's commands and **has not been run end to end**. Use the per-step commands here.

## Owners (four roles)

| role | Wednesday |
|---|---|
| **B1 · Build lead** | The fast-forward and every patch: applies it, runs `check.sh`, commits. Owns the freeze. |
| **B2 · Second builder** | The step-specific test after each patch (below) and the Plan A rehearsal. Owns 0005 and the re-capture of the demo trees. |
| **E · Economist** | **Reviews 0004's drafted pack rows from 09:30** (`$FIX/mcq-pack-proposal/*.csv`) and the 22 rows 0011 rewords (0011 section of `$C/README.md`), in their 0011 wording. 13:30–14:00: **drafts** the `tax_incidence_split_p2`/`_m2` rewording in a note, never in the CSVs. B1 pastes it in after 0011 passes (about 15:30), commits, reloads and reruns `check`. Leave-behind and QR code Thursday 13:00–17:00. Checks the economics in the dry run. |
| **P · Pitch lead** | Pastes the Challenge 1 brief into `challenge-brief.md` at 09:00 (needs a human). Builds the deck 09:00–16:00. Line card, adult account, dry run and filming; video edit Thursday 09:00–17:00 with B2. |

## The series, step by step

Clock times assume a 09:00 start. The steps are serial: each patch needs the one before it.

| step | what | owner | hours | when |
|---|---|---|---|---|
| 0 | Fast-forward `main` to 05e | B1 | 0.5 | 09:00–09:30 |
| 1 | 0001 core | B1, B2 tests | 0.5 | 09:30–10:00 |
| 2 | 0002 focus (**default: apply**; B1 skips it only if `check` fails, then uses the 0003 variant; decided by 10:30) | B1, B2 tests | 0.5 | 10:00–10:30 |
| 3 | 0003 Verify scoring + migration 010 | B1, B2 tests | 1.0 | 10:30–11:30 |
| 4 | 0004 MCQ code + pack rows | B1 applies; E's review 09:30–11:30 | 1.5 | 11:30–13:00 |
| — | lunch. **P and E decide by 13:30: the `source_conflict` rule (default: Option A) and the empty plan after a matched check (default: accept it for now).** If they reject Option A, skip 0007 and use cut-line row 6 | P, E | | 13:00–13:30 |
| 5 | 0005 decay: **optional, not scheduled** (no room with 0006–0011; see the clock) | B2 | 1.0 (+0.5 re-capture) | — |
| 5b | 0006 stuck ladder + review requests (recommended) | B1, B2 tests | 1.0 here (+0.5 in the dry run) | 13:30–14:30 |
| 5c | 0007 labelling text + 0008 Ask guard (recommended) | B1, B2 tests | 0.75 | 14:30–15:15 |
| 5f | 0011 MCQ length rank (pack rows + ingest warnings; ✓ verified). E's 0.5 h read is in the morning review; E drafts p2/m2 13:30–14:00, B1 pastes it after 0011 | B1, B2 tests | 0.25 | 15:15–15:30 |
| 5d | 0009b dead-link report cap (✓ verified) | B1, B2 tests | 0.5 | 15:30–16:00 |
| 5e | 0010b show-then-pick cap (✓ verified; **dropped by default**: start only if 0009b has passed `check` by 15:00) | B1, B2 tests | 1.0 | **no slot**: 15:00–16:00 only if the day is 1 h ahead |
| — | Server, tunnel and claude.ai connector ([RUNBOOK](RUNBOOK.md) §4) | B2 | 0.5 | 15:30–16:15 (in parallel) |
| — | Deck | P | | 09:00–16:00 (in parallel) |
| 6 | Outside the series (optional, each with its own check) | B1 / E | ≤ 0.5 | only if ahead of time |
| 6b | Mock-ups: browser check, light and dark, 1280×720 | E | 0.5 | 14:00–14:30 (in parallel) |
| — | **Freeze and final checks** (check.sh, Plan A, seed-demo, re-capture, shot 5) | B1, B2 | 0.5 | 16:00–**16:30** |
| 7 | Dry run in claude.ai (now also: review wordings, stuck turns, a pasted explain-back); **18:00 gate** | all | 1.5 | 16:30–18:00 |
| 8 | Film Plan A or Plan B | all | 3.0 | 18:00–21:00 |
| 9 | Label-agreement study (optional), with the 02a key fixes | all | 2 × 4 people | after submission |
| — | Video edit (captions, highlight boxes, caption track) | P, B2 | | Thursday 09:00–17:00 |
| — | Leave-behind and QR code | E | | Thursday 13:00–17:00 |

**The clock.** Steps 0–4 end at 13:00. After lunch the patch window is 13:30–16:00 (2.5 h), because the freeze checks need 16:00–16:30. B1's time in that window: 0006 1.0 h + 0007/0008 0.75 h + 0011 0.25 h + 0009b 0.5 h = **2.5 h, which fills it**. 0010b's 1 h does not fit (without 0011 it was already 0.75 h over). So:
- **0010b is the one to drop.** Start it only if 0009b passes `check.sh` by **15:00** (the day an hour ahead). Otherwise leave it out and use its cut-line workaround. If the team wants 0010b's pitch line more than 0011, dropping 0011 saves only 15 minutes: not enough on its own.
- **0011 goes before 0009b**, because it is 15 minutes, touches no code and fixes a cue a judge can find at the expo. Applied right after 0008 is a tested position (scout: byte-identical trees in either order; verifier V: 74/74 on 0008 + 0011).
- **0005 gives way.** It changes nothing in Plan A; it fixes off-camera levels and the How AI works ranking. If the team wants 0005 instead (for a How AI works ranking claim), apply it at 13:30–14:30 and expect 0009b not to fit either.
- **E works in parallel:** the 22 rows of 0011 are read in the morning review, and the p2/m2 rewording is drafted 13:30–14:00 (not in the CSVs). B1 applies it after 0011.
- **The real-chatbot checks move into the dry run:** 0006's review wordings and stuck turns, and 0009b's pasted explain-back. The 02a re-keying moves to step 9.

**0006–0011 without 0005 is untested as a stack.** Every verifier tree (S, U, V) included 0005. The original 0006 was tested without 0005 (74/74, same probe numbers; w5-fix-residual), but verifier S built the `-w5` files on a tree with 0005. Dry-run each file with `patch -p1 --dry-run`. If any hunk is rejected, stop there and drop the rest. `check.sh` on that tree decides.

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
- **0009b adds a cap (step 5d).** A found problem still scores 1, but until the student has done one real check, reports can lift Verify only to developing. Every Plan A take reads **0.740** (developing; w6-planA ✓). The superseded 0009 would have turned 5 of 8 takes to new (w5-fix-counter-c2 ~; count corrected by verifier U).
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
  2. **Hold E's corrections to the 22 rows that 0011 rewords** (0011 section of `$C/README.md`) until 0011 is in (step 5f); B1 applies them. Read those rows in their 0011 wording. If you edit them earlier, 0011's hunks won't apply.
  3. E's other corrections go into the CSVs as a separate commit.
  4. Rerun `check.sh` and `testwise.py`.

  Any rewording means the rows are no longer the tested ones, so keep the form rules:
  - keys as plain claims, no closing full stop;
  - every option within ±20% of the key's length (our choice; 0011's ingest warning checks it);
  - no "always", "only" or "on purpose".

  **Don't add `ped_values_m2`.** It changes the demo target and breaks `check_mcp`, which hard-codes `ped_formula`; add it after filming. `ped_formula` still has no sign-error misconception: optional, step 6.
- **Apply:** `git apply docs/research/overnight/sims/fixes/combined/0004-mcq-give-away-key-is-a-mark-point-in-option-form-ope.diff`. The CSVs in `ingest/ai_literacy/` have CRLF line endings, so it prints "trailing whitespace" warnings. It still applies.
- **Test.** Run `check.sh` (74/74) and `python -m ingest.cli validate`. The only warning should be `ped_values` having 1 misconception. Then, on a fresh data folder with the pack loaded:
  ```bash
  EDUX_DATA_DIR=/tmp/claude-1000/tw-s4 PYTHONPATH=$PWD $PY $FIX/testwise.py --json /tmp/claude-1000/tw-s4.json
  ```
  Expect about 0.28 overall against chance about 0.31 (middle-length still 0.536 on economics until 0011). Then run the Plan A rehearsal.
- **On-screen change: re-capture.** The fabrication options change. The misconception shown in progress after an m2 pick becomes "Its links are tested before you see them, so the site is down for now". The 4c voiceover in the pitch script now names m1 (the rehearsal's pick), which is unchanged.
- **If skipped.** Hold on the first line of each reply and never close up on options. The old m2 is still in the set, so in 4c cut from the question straight to the reply after an m1 pick.

### Step 5 · `0005-decay-…diff`, not scheduled (B2, 1 h + 0.5 h re-capture)
**Wave 5–6: 0005 is optional, the trade-off for 0006–0011.** It doesn't fit before 16:30 with them (the clock). Apply it only if the team chooses it over 0010b and 0009b. The rest of this step is unchanged.

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

### Step 5b · `0006-w5-stuck-ladder-and-review-requests.diff` (B1 0.5 h; B2 tests 0.5 h; 0.5 h in the dry run)
- **On camera:** nothing changes. All eight Plan A takes have identical moves and levels (w5-fix-stuck-1 ✓).
- **At the expo, it fixes two things a judge can hit:**
  - **The stuck ladder.** After the one step back, each further miss climbs a rung: a worked example with its check, then an easier prerequisite check, then an offer to stop or switch, then worked examples round the part's points. For an always-failing student (30 turns), the longest bare-reteach run falls from 23 to **0**, the longest run with no MCQ from 24 to 1, and the stop-or-switch offer comes at **turn 8** (before: never). 29 of 30 plans have an MCQ (before: 6). A student who fails only open answers: 11/12 → 1/2. A strong student who misses only the harder extend questions gets no worked examples. Rung counts are our choice.
  - **Review requests.** A new optional label, `asks_for_reviews`, plus a few paraphrase patterns. With a perfect label, 28/28 review asks get a review and 0/18 ordinary messages are stolen. The patterns alone get 18/18 on the set they were written with, but only **2/10 on a holdout**. A careless always-true label steals 8/18. On the real MCP server, "hit me with a review question" gave a review with the label and a re-ask without it (w5-fix-reviews-1 ✓). How well Claude sets the label is untested.
- **Apply:** `patch -p1 < $FIX/combined/0006-w5-stuck-ladder-and-review-requests.diff` (dry run first). No migration. The server instructions stay at 889/900 words.
- **Test.** Run `check.sh` (74/74). Then the wave-5 probes **on a copy**, as for step 1 but with `sims/fixes/probes_w5.py`:
  ```bash
  cd /tmp/claude-1000/probe-s6     # a copy of the tree, with edux_sim.py and probes_w5.py copied in
  PYTHONPATH=$PWD $PY docs/research/overnight/sims/fixes/probes_w5.py /tmp/claude-1000/probes-data-s6
  ```
  Expect the numbers above, as in `results/w5-S/probes_w5_s6.txt`.
- **In the dry run (5 min):** type 10 review wordings and 3 wrong answers in a row in Claude. Check that `asks_for_reviews` is true on the review asks, and that the third miss brings a worked example.
- **If skipped:** Plan A is unchanged. Off camera, a judge who keeps answering wrong gets up to 23 bare reteaches, and "quiz me" paraphrases teach the old topic. Use the prompt button or the exact words "Quiz me on what's due", and don't let a judge keep answering wrong.

### Step 5c · `0007-w5-labels-text.diff` and `0008-w5-ask-guard.diff` (B1 0.5 h; B2 tests 0.25 h)
- **0007 is text only:** labelling rules in `text/tools/tutor_turn.md` (195 → 537 words with 0006; no cap) and 5 more words in the server instructions (894/900). In our words:
  - an answer is never `research`: a course answer or "ok, go on" is `concept`; an answer to a source-checking task or a how-AI-works question is `other`;
  - the `concept` question feature needs an economics term or an official statistic;
  - `source_conflict` is true when the source wouldn't open, or doesn't say what the chatbot said (a different figure, date or period, or the claim is missing). Rounding is not a conflict. **This is Option A, our choice and the default: P and E decide by 13:30; if they reject it, skip 0007 (cut-line row 6);**
  - `points_met`: tick only what the student fully produced; on a Verify answer, a for "wouldn't load" and d for a verdict.
- **0008 is 3 lines in `service.py`:** an answer sent with `request_type: research` and no question features is turned into `other` (AI-literacy part) or `concept` (course part) before anything is recorded.
- **On camera:** with 0008, if the chatbot labels the 4c answer `research`, Ask stays **developing (0.528)** in the progress shot. Without it, Ask drops to **new (0.256)**. Answers labelled research that wrote Ask 0.0: 3/3 → 0/3. An answer plus a real new question keeps its Ask credit (w5-fix-guard-1 ✓). 0007 alone changes nothing on the server: it acts on the chatbot (w5-fix-labels-1 ✓).
- **Apply:** `patch -p1 < $FIX/combined/0007-w5-labels-text.diff`, then `patch -p1 < $FIX/combined/0008-w5-ask-guard.diff` (dry run first each time).
- **Test.** Run `check.sh` after each (74/74). If the only failure is "MCQ options are shuffled differently for different students", rerun: it is a chance clash (verifier S, skip-0007 tree). Then `sims/fixes/labels_probe.py` on a copy: expect 0/3 answers writing Ask 0.0, as in `results/w5-S/labels_s8.txt`.
- **Team decision: the empty plan after a matched check.** Under 0007, a Verify answer where the source matched is labelled `other`, and `other` gets an **empty plan**: no feedback step on the check. Before, it got a stray course MCQ. The Verify evidence is still recorded. Plan A is unaffected, because every 4c turn sets `source_conflict`. Options: accept it for now (the chatbot replies in its own words), or add a feedback step later (code, after filming). **Default: accept it for now; P and E decide by 13:30.** Either way, don't film a matched check.
- **If skipped.** Skip 0008: if 4c is labelled `research`, Ask falls to new; retake. It is 3 lines, so keep it. Skip 0007: the server is unchanged, but the chatbot gets no rules for answers, `source_conflict` or ticks.

### Step 5f · `0011-w6-mcq-length-rank.diff` (B1 0.25 h; E 0.5 h read + p2/m2 rewording; ✓ verified; runs before 5d)
Added in wave 6 (`work/w6/w6-fix-length.md`; `sims/fixes/combined/README.md` "0011"). It is lettered 5f because it came last, but it is applied right after 0008.
- **What it fixes.** After 0004, the key is usually the middle-length option. "Drop the longest and shortest" scores 0.536 of the 28 economics option sets and "second-longest" 0.625, against chance 0.312. 0011 rewords 5 mark points and 17 misconceptions (meaning kept) so every misconception is within ±20% of each key on its part and the key's length rank is spread (shortest 8 / middle 10 / longest 10 of 28). Then middle scores 0.286, second-longest 0.321, and no cue is above 0.375 (w6-len-3 ✓; in-sample, about ±0.09 per strategy). In play, the middle-length gamer falls from 57% right and 4.4 false-secure parts to 19% and 0.2 (N = 30; w6-len-4 ✓).
- **It also adds two load warnings** in `ingest/validate.py` (thresholds our choice): a misconception more than 20% longer or shorter than a key on its part, and a pack whose key is the shortest, middle or longest option 15 points more often than an even spread. On the old pack they print 3 row warnings and "middle in 15 of 22"; on the new pack, none (w6-len-2 ✓). Keep them for the 9EC0 pack.
- **No code, text, settings or migration change.** It touches only the two example-mini CSVs and `validate.py`, and shares no file with 0009b or 0010b.
- **E reads the 22 changed rows** (before/after table in `work/w6/w6-fix-length.md`). Verifier V: 20 read correctly. Two need rewording (w6-len-econ ~):
  - `tax_incidence_split_p2` ("When demand is price elastic, producers bear more of the tax") and `_m2` ("If demand is price inelastic, producers bear most of the tax burden") ignore supply elasticity: incidence depends on PED relative to PES. m2 is now absolute rather than comparative, so it isn't strictly false when supply is even more inelastic. The two also read as mirror images, which is a pair cue.
  - Minor: `yed_definition_m1` ("its own price": whose?) and `pes_formula_m1` (carries a true clause about PED).
  - After any rewording, keep each row within ±20% of the keys on its part. Reload: the new warnings must stay silent. Rerun `testwise.py`: middle and second-longest should stay near 0.3.
- **Apply:** `patch -p1 < $FIX/combined/0011-w6-mcq-length-rank.diff` (dry run first), then reload the pack and `seed-demo --reset`.
- **Test.** Run `check.sh` (74/74). The load prints only the old `ped_values` warning. Then `testwise.py` on a fresh data folder, with the absolute-path check above. Expect economics middle 0.286 and second-longest 0.321 (`results/w6-length/testwise_s11.json`).
- **On camera:** Plan A's literacy shots are unchanged (the AI-literacy rows are untouched). **The `ped_definition` check changes wording:** its distractors now read "The slope of the demand curve is PED, so it is the same all along it" and "PED measures how far the price changes when the demand changes". That check appears in the `then_ped` take's prerequisite question, in shot 5 (`demo-weak`) and in the expo script. Re-capture shot 5 after 0011, and update the expo line card.
- **Residual: the sequence cue.** A part's misconceptions are the distractors for every one of its points, so on a point-2 or point-3 check the key is the only option not in the previous check (100% on 11 sets, before and after). Fixing it needs point-specific misconceptions (later, L). Say "options are written to the same length, and the right one isn't the odd one out", never "the MCQs can't be gamed".
- **If skipped:** nothing changes on camera. At the expo, a judge who drops the longest and shortest option gets about 57% right. Make no claim that the options resist cue-guessing.

### Step 5d · `0009b-w6-dead-link-report-cap.diff` (B1 0.5 h; ✓ verified)
**Wave 6 replaced 0009 with 0009b.** Blind verifier U confirmed every number below on fresh trees (`work/w6/verify-U.json`; w6-c2b-1 ✓, w6-c2b-2 ✓, w6-planA ✓, w6-combined-3 ✓). Use 0009 or 0009b, never both.
- **What it changes.** A dead-link report (any Verify answer sent with `source_conflict`) still scores Verify 1. But until the student has done one real check of their own (a correct Verify answer that wasn't a report), reports can lift Verify only to developing, not secure. It also appends one sentence to the `points_met` bullet in `text/tools/tutor_turn.md` (+34 words): never tick a point for words that only repeat the chatbot's reply, a point it just showed, or its citation.
- **Off camera (simulation: synthetic students):** "the link is broken" gamers reach Verify secure in **0%** of runs (was 100%), shown developing. Copying the publisher and date from the citation: 0% under a literal labeller too. Honest partial-skill students: 62% Verify secure against 64% without it (N = 300, SE about 3 points; within noise).
- **On camera:** **all eight Plan A takes stay Verify developing (0.740)**, including the dead-page and a,d-ticked lines. Ask (0.528) and the plan moves are identical. No re-shoot. The on-screen level is the same word as before (0.748 without it).
- **Apply:** `patch -p1 < $FIX/combined/0009b-w6-dead-link-report-cap.diff` (dry run first; it applies on 0008, and on 0008 + 0011).
- **Test.** Run `check.sh` (74/74, no expectation changed; `results/w6/check_t9b.txt`). Then the Plan A rehearsal: expect Verify developing in every take.
- **In the dry run (5 min):** paste one explain-back that only repeats the chatbot's reply. The chatbot should not tick it. Untested in a real chatbot.
- **Residual.** A student who has done one real check can then report dead links freely (L1c: Verify secure 100%; the rule allows it). A genuine mismatch report is capped too until one real check.
- **If skipped:** Plan A keeps 0.748. "The link is broken", twice, makes Verify secure for 100% of simulated gamers in under a minute: the most visible exploit at an AI-literacy stand ([06](06-settings-simulation.md)). Don't invite the dead-link line at the expo.
- **Superseded: `0009-w5-broken-link-counter.diff`.** It gave a bare or a,d-ticked report no evidence, which clashed with 0007's own ticking rule and turned 5 of 8 Plan A takes to Verify new (w5-fix-counter-c2 ~; verifier U's recount). Don't apply it.

### Step 5e · `0010b-w6-show-then-pick-cap.diff` (B1 1 h; ✓ verified; only if on time)
**Wave 6 replaced 0010 with 0010b.** Verifier U confirmed the numbers below (w6-c1b-1 ✓, w6-c1b-2 ✓, w6-c1b-3 ✓). Use 0010 or 0010b, never both. 0010b applies on 0009b; without 0009b use `variants/0010b-alone-w6-show-then-pick-cap.diff` and add 0009b's tutor_turn.md sentence by hand.
- **What it changes.** An answer the student **picks** within 30 min of a worked example or hint (an MCQ check, a review, a prequestion) can't make a part secure. An answer the student **writes** (explain-back, extend, past question) still can. A prerequisite boost never makes a part secure on its own. In `plan.py`, a miss on an open answer is cleared only by a complete open answer.
- **Off camera:** "just show me" + match: 9 → **0** parts secure; "teach me" + match: 9 → 0; middle-length guessing 4.4 → 0; always "A" 0.8 → 0. Honest students: **3.4 parts secure in a session against 3.6** (0010 gave 1.4), 2.5 at +7 days (unchanged). The cost: the first secure part comes after 8.9 effort-minutes instead of 2.4. A student who fails only open answers gets the stop-or-switch offer at turn 19 (0010: never).
- **It relies on the 0009b text line.** A gamer who pastes the shown point back as an explain-back reaches 9/9 parts under a literal labeller, 0/9 under a skeptical one. Don't take 0010b without that sentence.
- **On camera:** Plan A is unchanged, and `seed-demo` progress is identical. Shot 5 shows only first moves, so it is unaffected. A part picked right straight after teaching now reads **developing**; an explain-back (or a later check) makes it secure. Say that, never "one right answer and it's secure".
- **Apply:** `patch -p1 < $FIX/combined/0010b-w6-show-then-pick-cap.diff` (dry run first). Test: `check.sh` (74/74), then the wave-5 probes as in step 5b (always-failing student unchanged; review asks 18/18).
- **Go/no-go at 15:00 (dropped by default).** Start it only if 0009b has passed `check` by 15:00, which means the day is an hour ahead; it must pass by 16:00, because the freeze checks need 16:00–16:30. Otherwise keep 0009b and 0011 and drop 0010b. Then make no "picking straight after being shown never makes a part secure" claim, and don't demo "just show me" followed by a progress shot.
- **Superseded: `0010-w5-show-then-answer-counter.diff`.** It cut honest students' secure parts 3.6 → 1.4, removed the stop-or-switch offer for students who fail only explain-backs, and still leaked 4.0 parts to "teach me + match" (w5-fix-counter-c1 ~). Don't apply it.

### Step 6 · Outside the series: optional, not tested with it (only if on time; each needs its own `check.sh`)
None of these is in 0001–0011. Apply them only after the last patch you keep. Each needs its own 74/74 and a Plan A rerun before 16:00; otherwise drop it and use the workaround. With 0006–0011 in, expect no time for them.

| item | owner | time | if not done |
|---|---|---|---|
| **Literacy settings:** `literacy.ask_min_features = 3`, `ail_question` guess .30, `ail_unprompted` guess .20 ([02](02-ai-literacy-assessment.md) rec 2; w2-02-08 ✓, simulated on pre-wave-4 code) | B1 | 15 min + check | **Drop the slide-6 add-on.** 4b keeps 3 or more features anyway |
| A sign-error misconception for `ped_formula` ("keep the minus sign") | E | 30 min + validate | Nothing on camera |
| Per-part How AI works counts ("checked n, right m") in `get_my_progress` | — | not built | In 4d, highlight only the "still held" line, never a How AI works level |
| `fix4b` "not yet shown" flag | — | not in the series | No "not yet shown" line |
| Record a skip when a new task replaces an unanswered Verify task (`service._literacy_followup`; [06](06-settings-simulation.md)) | — | 1 line, untested | No claim that progress or the teacher view shows skipped tasks |

### Step 6b · Mock-ups: browser check before capture (E, 0.5 h, 14:00–14:30 in parallel)
- **What:** [`mockups/teacher-view.html`](mockups/teacher-view.html) and [`mockups/student-progress.html`](mockups/student-progress.html), static pictures of a design for the deck and video, with invented numbers ([mockups/README](mockups/README.md)).
- **Check, before anyone captures them.** Nobody has rendered them yet (no headless browser overnight).
  - Open each at **1280×720**, in **light and dark** (switch the OS setting).
  - Nothing is cut off at 720 px. The second MCQ on the teacher view is collapsed so that it fits.
  - The "Mock-up · illustrative data · not a live feature" tag sits inside every crop. Keep it in every shot.
  - Text is readable in both themes.
- **Designed, not built: the voiceover says "this is the design" over these.**
  - The whole teacher view (05 rec 23 builds it later).
  - On the student page: the "not yet shown" label (`fix4b`), How AI works "checked n, right m", and the "what your teacher sees" line.
  - **The skip count** ("Skipped: 2 tasks") rests on 0003, which is tested but not merged. The live counter misses most ignored tasks: about 2% were counted in simulation (w5-06g-07 ~). Crop that line, or say "this is the design".
- **Captions and lines:** as in the mock-ups README. Never say "How AI works level"; say "per-part results".

### Freeze and final checks (B1, until 16:30)
1. Run `check.sh` on the frozen tree: 74/74.
2. Run the Plan A rehearsal: no OVER BUDGET.
3. Run `seed-demo --reset`.
4. Re-capture the progress views if step 4, 5 or 5e is in, and shot 5 if 5f (0011) is in (the `ped_definition` options change wording). With 0009b in, the 4d Verify level is 0.740 (still developing).
5. **Check shot 5.** The verifier's rerun covered only the literacy episode, but 0004 changes how checks are built and 0005 moves `demo-secure`'s levels. On the frozen build, send "How do I calculate price elasticity of demand?" as `demo-secure` and as `demo-weak`. Confirm the first moves:
   - `demo-secure`: an intuition question;
   - `demo-weak`: a check on the definition, then last time's mistake corrected.

   If they differ, P edits the shot-5 words before filming. With 0010b in, no part in shot 5 goes secure; if any course progress view is shown, a part picked right straight after teaching reads developing.

**Nothing merges after 16:30.**

### Step 7 · Dry run in claude.ai, adult account, web search off (16:30–18:00)
- **Who:** P drives, B1 watches labels and the console, E checks the economics, B2 stands by.
- **How:**
  - Type the line card verbatim.
  - Expand every tool call and check the labels: 4a and 4b `research`; 4b with 3 or more features; 4c `source_conflict: true` and `request_type: other`. **With 0003, `source_conflict` decides whether Verify rises.**
  - **With 0009b:** paste one explain-back that only repeats the chatbot's reply; it should not be ticked.
  - **With 0006 (5 min):** 10 review wordings; is `asks_for_reviews` true on the asks and false on the rest? Three wrong answers in a row: does a worked example follow?
  - **With 0007:** does the chatbot label the 4c answer `other` and an explain-back `concept`?
  - Any miss: reset, new chat, try again (any number of resets before the gate).
- **The 18:00 gate.** Plan A needs all three:
  - the patched 05e build;
  - `check_mcp` passing with no OVER BUDGET;
  - one take, after any number of resets, that runs 4a–4d with the right labels and no mid-episode retake.

  Otherwise, film Plan B ([pitch-script.md](pitch-script.md) §1b). The gate doesn't wait for fixes.

### Step 8 · Film (18:00–21:00)
- **Who:** P and E drive, B1 watches the console, B2 records the fallback clips.
- **What:**
  - Plan A (§1) or Plan B (§1b) from [pitch-script.md](pitch-script.md).
  - Reset and open a new chat before every take.
  - Then record the two offline fallback clips.

### Step 9 · Label-agreement study (optional)
- **What:** rewrite at least 20 of the 40 draft messages in a student voice. Then two blind raters, two bot runs, and κ pooled per skill ([02a](02a-label-agreement-protocol.md)).
- **First, fix the key and the rater sheet (20 min; [02a](02a-label-agreement-protocol.md) §4):**
  - **Label clarifications:** raters read the same rules the chatbot gets in 0007 (request_type on answers, the `concept` feature, `source_conflict` Option A, `points_met` and the Verify ticks), plus the engagement wording in 02a.
  - **V01–V08 `request_type`:** re-key from `research` to `other`. `research` on an answer scores Ask 0/4, and `concept` pulls the course focus.
  - **V01 and V08 `source_conflict`:** re-key to true under Option A (a different figure counts). Decide V04.
  - **V08 rater rule:** the protocol tells raters "says they opened it" for tick a, but the chatbot never sees that rule. Give raters 0007's `points_met` wording instead, word for word.
- **Then analyse with `sims/agreement/analyse.py`** (stdlib; it replaces Appendix C's `agree.py`): `python3 docs/research/overnight/sims/agreement/analyse.py decisions.csv > results.md`, once after the B/C labels and again after adjudication. Its only numbers so far come from a dry run of a Claude proxy against a Claude-written key: a pipeline test, not agreement evidence (w5-02s-01 ~).
- **If dropped:** slide 6 says "we're checking those labels against two humans", with no number. If it is dropped rather than moved, say "next, we check those labels".

## CUT LINE: if behind at the 16:30 freeze (18:00 gate)

**Never cut:** step 0, **0001** (it carries the clamp; only whole patches were tested, so don't split it), the dry run and filming. Anything not merged and passing by **16:30** is dropped, and its workaround switches on. The **18:00 gate** then picks Plan A or Plan B.

**Cuts come off the top of the stack. The new patches go first.** The series is serial, so 0001–0003 are in by 11:30.
- **0002 can be dropped only before 10:30.** Then apply the 0003 variant instead of 0003.
- **After that, drop from the top:** 0010b, 0009b, 0011, 0008, 0007, 0006, then 0005 (if in), then the step-6 extras, then 0004. 0011 shares no file with 0009b or 0010b: a tree without it is byte-identical to applying the rest in order, but run `check.sh` on that tree anyway.
- **To remove a patch from the middle** (0003, say), rebuild from the 05e commit, applying the series without it. Then run `check.sh` on that exact tree. Don't revert it in place: that is untested, and 0005's `check_mcp` hunk sits on 0003's rewritten docstring.
- Only single skips were tested (each 74/74). If two patches are out, `check.sh` on that tree decides.

Drop in this order, first to go at the top:

| drop order | item | on-camera workaround |
|---|---|---|
| 1 | Step 9, the label study | Move it to Wednesday night or Thursday. Slide 6: "we're checking those labels", with no number |
| 2 | Step 6 extras | Drop the slide-6 add-on. In 4d, highlight only "still held" |
| 3 | 0010b show-then-pick cap | Plan A is unchanged. No "picking straight after being shown never makes a part secure" claim; don't demo "just show me" then a progress shot |
| 4 | 0009b dead-link report cap | Plan A is back to 0.748. Don't invite the dead-link line at the expo; no "a reported dead link alone can't reach secure" claim |
| 4b | 0011 MCQ length rank | Nothing on camera; the shot-5 options keep their 0004 wording. No "options are the same length" claim. At the expo, don't invite a judge to guess options |
| 5 | 0008 Ask guard | Check `request_type: other` on 4c in every take; retake if it says `research` |
| 6 | 0007 labelling text | Same label check. Matched Verify answers get a stray course MCQ again: don't film one |
| 7 | 0006 stuck ladder + reviews | Plan A is unchanged. At the expo, don't let a judge keep answering wrong; use the "Quiz me on what's due" button |
| 8 | 0005 decay (if applied) | Plan A is unchanged. No How AI works ranking claim; don't linger on `state` |
| 9 | 0004 MCQ | Hold on each reply's first line, with no option close-ups. In 4c, cut past the options to the reply after an m1 pick |
| 10 | 0003 Verify (rebuild without it; not recommended) | Send 4c as the Verify answer with points a, c, d. After a dead-page take, never show Verify. Finish the episode before any PED question |
| — | 0002 focus: only by the 10:30 decision, with the 0003 variant | Film from the line card. At the expo, use §B's honest script |

## Known residuals (flag them; don't demo them)
- **Without 0006: seven reteaches in a row.** After the single step back, a student who keeps failing `ped_formula` gets 7 reteach-only plans with no question (w4-fix-core-2 ✓ note). With 0006 there are no bare-reteach runs (w5-fix-stuck-1 ✓).
- **"What's due" paraphrases.** Without 0006, only the exact wording works (w4-fix-core-3 ~). With 0006, it depends on the chatbot setting `asks_for_reviews`; the patterns alone catch 2/10 new wordings (w5-fix-reviews-1 ✓). Use the prompt button at the expo.
- **The focus fix loses 2 of 21 genuine course questions** (16/21 → 14/21), and every research question that names a course part (2/5 → 0/5) (w4-fix-focus-1 ✓).
- **The Verify fix depends on the chatbot flagging `source_conflict`.** Without the label, Verify stays new and the task is re-asked (w4-fix-verify-1 ✓ note).
- **Cheap tricks still pay off camera.** Without 0011, a middle-length option cue gets 57–58% of MCQs right against 31% chance ([06](06-settings-simulation.md)); with it, 19% (w6-len-4 ✓). With 0011, the sequence cue remains: a student who remembers the last check's options finds the key on point-2 and point-3 checks. Even with 0009b and 0010b, guessers still gain "developing", a student who has done one real check can then report dead links freely, and pasting the shown point back as an explain-back reaches secure if the chatbot ticks literally. Never say "gaming-proof".
- **The skip counter misses most ignored tasks** (about 2% counted; w5-06g-07 ~). No claim that progress shows skipped tasks.
- **A matched Verify answer gets an empty plan** under 0007 (team decision, step 5c).
- **Steps 4, 5, 5e and 5f change on-screen wording and levels.** Re-capture after them: the m2 text, the `demo-secure` and `demo-showme` levels, any course part shown going secure from MCQs straight after teaching (5e), and the `ped_definition` options in shot 5 and the expo script (5f). Verify reads 0.740 with 0009b: the same word, developing.
- **0004's and 0011's pack rows are draft wording** until E has read them. `tax_incidence_split_p2`/`_m2` need rewording (w6-len-econ ~).
- **Test copies need an absolute `PYTHONPATH`.** Nine wrapper scripts silently fall back to the unpatched venv code if given a relative path (w6-path-2 ~). The stored wave-4 and wave-5 numbers reproduce with absolute paths (w6-path-3 ✓, w6-path-4 ✓).

## Note for the build docs (research does not edit these)
The patches change behaviour that `docs/build/` still describes the old way. B1 or the doc owner should update, after filming if necessary:
- **`docs/build/reference/learner-model.md`** (around lines 134 and 136): an ignored literacy task or check is "counted as a skip, no evidence", not "recorded as 0". Add the found-a-problem rule: a reported dead or mismatched source scores Verify 1. If 0005 is in, add decay towards the starting estimate, with Ask and Verify towards 0. If 0004 is in, add mark-point-only keys and open checks.
- **The 05e step doc** (`docs/build/steps/05e-literacy-coaching.md`, the "Bad links" section around lines 102–103 and 201): the same Verify and skip rules, and migration 010.
- **Wave 5–6:** if 0009b is in, add "reports can't lift Verify past developing until one real check". If 0006 is in, describe the stuck ladder and the `asks_for_reviews` label. If 0010b is in, add "a pick straight after a show or hint can't make a part secure; a written answer can". If 0011 is in, note the two ingest warnings (option length band and key-rank spread) in the course-pack docs. Later, mirror 0007's labelling rules in the `Field(description=…)` strings in `edux/server.py`, so raters and the chatbot read one text (w5-fix-labels rec 4).
- **Bump `protocol` to `v0.3` in `settings.toml`.** The meaning of a Verify score changed, and none of the patches bumps it.

## Findings (home report for the wave-4 to wave-6 fix findings; the w6-path-* audit rows live in [06](06-settings-simulation.md))

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
| w5-fix-stuck-1 | Stuck ladder (0006): always-failing student's longest bare-reteach run 23 → 0, no-MCQ run 24 → 1, stop-or-switch offer never → turn 8, MCQ plans 6/30 → 29/30 | simulation | scripted turns, example pack, 05e | system behaviour | ✓ (with 0010, no stop offer for an open-only failer in 40 turns) |
| w5-fix-reviews-1 | Review requests (0006): asks answered with a review 1/18 → 18/18, 0/12 stolen; holdout patterns only 2/10; perfect label 28/28; always-true label steals 8/18 | simulation | scripted messages, example pack | system behaviour | ✓ (18/18 in-sample; real chatbot labels untested) |
| w5-fix-labels-1 | Labelling text (0007) applies, 74/74, Plan A unchanged; text alone leaves research-labelled answers writing Ask 0.0 (3/3) | simulation | scripted turns | system behaviour | ✓ |
| w5-fix-guard-1 | Ask guard (0008): research-labelled answers writing Ask 0.0 3/3 → 0/3; final_research Ask new 0.256 → developing 0.528 | simulation | scripted turns | prediction (validity) | ✓ |
| w5-fix-counter-c2 | Broken-link counter (0009, superseded by 0009b): "link is broken" gamers Verify secure 100% → 0% (N = 30); honest 65% → 59% (N = 100); Plan A final 0.636 | simulation | synthetic students | prediction (validity) | ~ final_ticks_ad, clean, plan_now, then_ped and a dead link ticked a, d also fall to new (0.300) |
| w5-fix-counter-c1 | Show-then-answer counter (0010, superseded by 0010b): show-me gamers 9 → 0 parts secure; honest 3.6 → 1.4 parts secure in a session, first secure 2.4 → 12.0 min | simulation | synthetic students | prediction (validity) | ~ with 0006, an open-only failer gets no stop offer in 40 turns |
| w5-fix-combined-2 | 0006–0010 apply on 0001–0005 with offsets only; identical tree via patch -p1 and git am --keep-cr; 74/74 after each step and on each single skip | simulation | 05e export | system reliability | ✓ (plain git am strips 0004's CRs) |
| w6-c2b-1 | Dead-link report cap (0009b): "link is broken" gamers' Verify secure 100% → 0%, held at developing 0.740; copied-details gamers 100% → 0% under both labellers | simulation | synthetic students, N = 30–100 | prediction (validity) | ✓ (L1c, one real check then reports, still 100% by design) |
| w6-c2b-2 | 0009b honest cost: partial-skill students Verify secure 64% → 62% (N = 300, SE about 3 pts); strong 100% | simulation | synthetic students | prediction (validity) | ✓ |
| w6-c1b-1 | Show-then-pick cap (0010b): C3 9 → 0, C3t 9 → 0, C2m 4.4 → 0, C1 0.8 → 0 parts secure | simulation | synthetic students, N = 30 | prediction (validity) | ✓ (pasted explain-back C3x 9.0 under a literal labeller) |
| w6-c1b-2 | 0010b honest cost: 3.6 → 3.4 parts secure in session, 2.5 at +7 d; first secure 2.4 → 8.9 effort-min | simulation | synthetic students, N = 100 | prediction (validity) | ✓ |
| w6-c1b-3 | 0010b restores the stop/switch offer for an open-only failer (turn 19; 0010 never); other probes unchanged | simulation | scripted turns | system behaviour | ✓ |
| w6-planA | All 8 Plan A takes end Verify developing 0.740 with 0009b (0.748 on 0008); Ask 0.528, moves identical | simulation | scripted Plan A turns | prediction (displayed level) | ✓ |
| w6-combined-3 | 0009b and 0010b apply cleanly on 0001–0008; 74/74 after each; seed-demo progress identical | simulation | 05e export | system reliability | ✓ |
| w6-len-1 | 0011 (5 mark points, 17 misconceptions, 2 ingest warnings) applies on 0001–0008; 74/74 | simulation | 05e export | system reliability | ✓ |
| w6-len-2 | 0011's ingest check: old pack 3 row warnings + "middle in 15 of 22"; new pack none | simulation | example pack | system behaviour | ✓ |
| w6-len-3 | Testwise, 28 economics sets: middle 0.536 → 0.286, second-longest 0.625 → 0.321, max cue 0.375 (chance 0.312); sequence cue 1.0 unchanged | simulation | cue-only student, example pack | prediction (validity) | ✓ (in-sample) |
| w6-len-4 | Gaming, N = 30: C2m right 0.569 → 0.191, secure 4.37 → 0.17; C2l2 0.649 → 0.194; random control 0.31 → 0.33 | simulation | synthetic students | prediction (validity) | ✓ (middle length now mildly anti-informative) |
| w6-len-econ | 20 of 22 reworded rows sound; tax_incidence_split_p2/_m2 ignore supply elasticity and mirror each other | practitioner | example pack | content accuracy | ~ flag only, not fixed |
