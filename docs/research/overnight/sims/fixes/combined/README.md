# Wave-4 combined patch series (05e branch)

This is the blind integration check by w4 verifier Q. Five patches turn the 05e export
(`/tmp/claude-1000/edux-05e-ff`, the tree that `main` fast-forwards to) into the fully fixed tree. Each patch applies
on top of the one before it. I built them only from the scouts' diffs, scripts and READMEs in `sims/fixes/`.
Claim verdicts are in `work/w4/verify-Q.json`.

## Apply order

| # | file | source diff(s) | touches |
|---|---|---|---|
| 1 | `0001-core-fixes-…diff` | `fix1-clamp`, `fix2-stuck-once`, `fix3-quiz-me` | learner.py, plan.py, service.py |
| 2 | `0002-focus-…diff` | `focus-side-turn` (Fix 1 only; not the name-gate or the sources fallback) | service.py |
| 3 | `0003-verify-scoring-…diff` | `verify-scoring` (incl. `migrations/010_literacy_skip.sql`) | demo.py, learner.py, service.py, check_mcp.py, settings.toml, text/tools/get_my_progress.md |
| 4 | `0004-mcq-give-away-…diff` | `mcq-giveaway-code` + `mcq-giveaway-pack` (not the 3-options settings) | context_blocks.py, plan.py, service.py, ingest/validate.py, text/moves/ask_mcq.md, both packs' mark_points/misconceptions CSVs |
| 5 | `0005-decay-…diff` (optional) | `fix4-decay-bc` (floor = prior; Ask/Verify floor 0; never-right part capped at prior; not `fix4b`) | learner.py, check_mcp.py |

`variants/0003-alt-verify-scoring-without-0002.diff` replaces 0003 if you skip step 2.

```bash
cd <repo on the 05e branch>
git am /path/to/combined/000*.diff          # or: for p in combined/000*.diff; do git apply "$p"; done   or   patch -p1 < each
```
The CSVs in `ingest/ai_literacy/` have CRLF line endings, so 0004 prints "trailing whitespace" warnings. It still
applies. Applying with `git apply` and with `patch -p1` each gave a tree byte-identical to the integration copy.

## Conflicts resolved by hand
1. **service.py, quiz-me vs side turn (0001/0002).** fix3 rewrote the `if not resolution[...] and last["focus"]` line
   that focus-side-turn uses as context. The hunk applied with fuzz 2. I checked that `side_turn` sits before
   `resolution = graph.resolve(...)` and that the quiz-me guard is kept.
2. **service.py ~346–358, side turn vs verify (0002/0003).** The verify hunk failed. I placed
   `if this_message.get("source_conflict") and not lost: evidence = _found_problem(last, evidence, at)` straight
   after the `node_ids` block and before the `side_turn` line. It doesn't read `side_turn`, and `side_turn` doesn't
   read `evidence`.
3. **plan.py stuck block, stuck-once vs mcq (0001/0004).** I kept fix2's once-per-session guard
   (`_stuck_handled[focus] != session_id`). Inside it is mcq's fallback:
   `stepped = prereq_check(...) if back else None`, and if `stepped` is None the whole part is retaught.
4. **check_mcp.py `waiting_task`, verify vs decay (0003/0005).** The decay seed line
   (`record_evidence(student, "ped_definition", "mcq_check", 1.0)`) applied with fuzz 1 below verify's rewritten
   docstring. I checked it.

## Test commands
Everything ran on copies under `/tmp/claude-1000/w4-verifyQ/` (s0 = export, sN = export + 0001..000N), with fresh
`EDUX_DATA_DIR`s and localhost servers only. `harness/run_all.sh` rebuilds and reruns all of it. It is transcribed
from the commands I actually ran but has **not been run end to end**.
```bash
harness/check.sh <copy> <port> <out>                    # the copy's own scripts/check_mcp.py, load + seed-demo + serve
# probes: copy sims/edux_sim.py and sims/fixes/probes_w4.py into <copy>/docs/research/overnight/sims/{,fixes/}
PYTHONPATH=<copy> $PY <copy>/docs/research/overnight/sims/fixes/probes_w4.py <data dir>
# Plan A: sims/demo-05e/run_episode.py with its /tmp path changed to w4-verifyQ
$PY run_episode.py --code <copy> --label sN --out cap --scenario final final_ticks_ad clean plan_now then_ped recommended
$PY harness/digest_q.py cap s0 s2 s3 s4 s5
# headline numbers
EDUX_DATA_DIR=<fresh> PYTHONPATH=<copy> $PY ../focus_measure.py --label L [--holdout]
EDUX_DATA_DIR=<fresh, pack loaded> PYTHONPATH=<copy> $PY ../testwise.py --json out.json
PYTHONPATH=<copy>:sims/literacy $PY ../lit_real.py <copy> <data dir> 60 out.json
$PY verify_run_episode.py --code <copy> --label L --out vcap --scenario dead_ad_then_ok verify_ignored matched_acd ...
```

## Results per step (outputs in `results/`)

| step | check_mcp | probes | Plan A (6 takes) | headline |
|---|---|---|---|---|
| base | 74/74 | ZeroDivisionError; quiz-me teaches old focus; 12/14 step-back plans; talk-only part 0.763 secure | Verify ends **new** in clean, plan_now, final_ticks_ad, then_ped; turn 4 re-asks the task | — |
| 1 core | 74/74 | no error (max 0.999); quiz-me → review; 1/14 step-back | (not run; no literacy change) | — |
| 2 focus | 74/74 | unchanged | identical to base | false focus 15/43 → **3/43** (holdout 9/18 → 3/18); genuine right focus 16/21 → 14/21 |
| 3 verify | 74/74 (3 expectations changed: an ignored task or check is a skip, not 0) | unchanged | Verify ends **developing (0.748)** in all 6; turn-4 re-ask gone; then_ped no longer writes Verify 0 | dead page 0.143 → 0.748; ignored: no evidence, `skipped: 1` |
| 4 mcq | 74/74 | unchanged | same flow; m2 misconception text changes | testwise 0.96 → **0.28** (chance 0.31) |
| 5 decay | 74/74 (one setup line added in waiting_task) | talk-only 0.763 secure → **0.300 new**; untouched prerequisite 0.44 → 0.30 and now gets a prereq check | identical to step 4 | How-AI-works AUC none-vs-strong 0.44/0.40 → 0.77/0.90 (branch), 0.51/0.31 → **0.85/0.88** (branch_missing); N=60, about ±0.05 |

Caveats found during verification:
- After the single step back, a student who keeps failing gets 7 reteach-only plans in a row (probe turns 8–14).
- Quiz-me works only for the exact prompt wording.
- If the chatbot leaves out `source_conflict`, Verify is unchanged.
- The pack wording in 0004 is the scout's proposal and needs an economist's read.

## Time estimate (student team)
About **4–5 h in total**: 0001 0.5 h; 0002 0.5 h; 0003 1 h (migration, reseed); 0004 1.5 h (mostly reading the
pack rows); 0005 1 h (recheck the seeded demo trees). Each check_mcp run takes about 1 min and each Plan A pass
about 3 min.

## What can be skipped, and what that means on camera
Every skip below was tested: the remaining series applies and check_mcp passes 74/74.
- **Skip 0005 (decay), the safest cut.** Plan A is unchanged. Off camera, a part the student only talked about
  can still show secure, and the How-AI-works AUC stays around chance (0.3–0.5), so don't put a "we can rank AI
  literacy" claim for How-AI-works on a slide. If you **keep** 0005, re-shoot or re-check any progress shot of
  demo-secure or demo-showme. ped_values, pes and indirect_taxes change level on demo-secure; pes and
  pes_definition change on demo-showme.
- **Skip 0004 (mcq).** On camera, the right MCQ option can be spotted from punctuation or length: 0.96 testwise
  hit rate. A judge reading the options may notice. Plan A is unchanged apart from the old fabrication option
  texts.
- **Skip 0002 (focus).** Use `variants/0003-alt-…diff` instead of 0003. Plan A is unchanged with the
  focus-safe wording. Off script, research or chat lines can pull PED or tax into focus (15/43 on the focus test set), and the
  next reply teaches a course part nobody asked about. I did not rerun the as_written take.
- **Skip 0003 (verify).** In the main take, Verify ends **new** after the student found the dead or mismatched
  page, which is the opposite of the story. Not recommended.
- **Skip 0001 (core).** Plan A is unaffected. Off camera: a crash after long right-answer runs, the step-back loop,
  and quiz-me going to the old focus. Cheap enough to keep.
