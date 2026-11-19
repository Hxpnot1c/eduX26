# Wave-4 combined patch series (05e branch)

> **Always use an absolute `PYTHONPATH` when you test a patched copy, and print `edux.__file__` first.** The venv's editable `edux` is the unpatched 05e code (`/home/vishnu/edux26/edux`). A relative path (e.g. `PYTHONPATH=s8` after `cd s8`), or a wrapper given a relative copy path (`cd "$CODE"; PYTHONPATH="$CODE"`: `mcq_run_tw.sh`, `harness/check.sh` and seven others), silently imports that unpatched code. With `python -m` or `-c`, the current directory also comes before `PYTHONPATH`. Check from a neutral directory: `cd /tmp && PYTHONPATH=/abs/path/to/copy $PY -c 'import edux; print(edux.__file__)'`. Verifier V reran the stored wave-4 testwise and wave-5 gaming results with absolute paths: they reproduce (w6-path-1 ~ to w6-path-5 ✓; `work/w6/verify-V.json`).

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

## 0006: stuck ladder and review requests (wave 5, w5-fix-residual)

`0006-stuck-ladder-and-review-requests.diff` fixes the first two caveats above. It touches `edux/plan.py`, `edux/service.py`, `edux/server.py`,
`text/tools/tutor_turn.md`, and adds two cue files, `text/moves/show_stuck.cue.md` and `text/moves/offer_stop_stuck.cue.md`. It needs no migration, and
settings and the server instructions are unchanged (still 889/900 words; cue variants don't count).

**Applies:**
- **With w5-fix-labels' 0006b and 0006c:** they apply on top of 0006, and that tree (s6bc) also passes 74/74 with the same probe numbers. Server instructions go to 894 words because of 0006b.
- **On top of 0005:** cleanly with `patch -p1` and `git apply --check`, and the tree is byte-identical to the tested copy. It also applies
**without 0005** (export + 0001–0004 + 0006): clean, check_mcp 74/74, and the same probe numbers. It does not apply
without 0001: the service.py hunks sit on fix3's `_asks_for_reviews`.

**1. Stuck ladder (plan.py).** Before: after the one step back, a student who keeps failing an explain-back got
feedback + reteach with no question, without end (`choose()`'s `if retry:` branch). The MCQ path was already capped
by `reteach_limit`. Now consecutive misses on the focus part are counted in `progress["_misses"]`, which is reset by a right
check or a complete explanation, a new session or another part. Once the step back has been done this session, each further miss
climbs one rung (a missed harder `extend` question neither counts nor resets):
1. a worked example (`show`, cue `show_stuck`) and its check MCQ;
2. an easier prerequisite check (`ask_mcq` prereq, stuck; preferring a prerequisite not checked this session);
3. an offer to stop or switch (`offer_stop`, cue `offer_stop_stuck`, `quick_parts` = developing parts other than this one);
4. beyond that, worked examples moving round the part's points, each with a check.

A rung that can't be built falls through to the next: no prerequisite with mark points, or stopping already offered this session.
Before any step back, a second miss in a row on an open answer gets the worked example instead of a second bare reteach. A right
check straight after a worked example doesn't reset the count. All numbers are our choice (`LADDER`, `OPEN_RETEACHES_IN_A_ROW`).

**2. Review requests (service.py, server.py).** Before: only the exact `review_due` prompt wording was detected
(substring match, fix3). Now three signals count:
- that wording;
- a new optional label, `this_message.asks_for_reviews`, with one sentence added to `text/tools/tutor_turn.md`;
- a few paraphrase patterns (`_REVIEW_ASKS`).

Same-topic and revision-advice wordings are excluded (`_NOT_REVIEW_ASKS`: "quiz me on this", "how should I revise").
A request is honoured only when:
- the message names no course node by name, alias or description (`graph.search_nodes`, not the notes, whose everyday words matched by chance: "Can we go through my reviews please" resolved to tax_incidence_split);
- it isn't a research question;
- a review with MCQ points is due.

With nothing due, the message stays on the last focus instead of returning an empty plan. A detected request also skips the `request_type = "other"` early-out and drops a pending question (same session).

| measure (scripts: `sims/fixes/probes_w5.py`; outputs `results/w5/`) | s5 = 0001–0005 | s6 = + 0006 |
|---|---|---|
| check_mcp | 74/74 | 74/74 (no expectation changed) |
| | | One harness run while other servers were running failed the "server time under 100 ms" check on **both** s5 and s6 (median about 150 ms). On a quiet rerun, both medians were 27 ms, so this is load, not 0006. |
| wave-4 probe 3 (the residual as reported): reteach-only plans after the step back | 7 (turns 8–14) | **0** |
| always-failing student, 30 turns: longest run of plans with no MCQ | 24 | **1** |
| … longest run of bare reteaches | 23 | **0** |
| … first stop-or-switch offer | never | **turn 8** |
| … plans with an MCQ | 6/30 | 29/30 |
| fails open answers only, 20 turns: longest bare-reteach run / no-MCQ run | 11 / 12 | **1 / 2** |
| recovers after the step back: ladder fires on correct answers | – | no (1 worked example, on the one miss) |
| strong student who misses only the harder (extend) questions: worked examples | 0 | 0 (extend never counts as a miss) |
| 30-message set (18 review asks / 12 not), due, request_type concept: asks answered with a review / ordinary messages stolen | 1/18 / 0/12 | **18/18 / 0/12** |
| same, request_type other | 0/18 (empty plan) / 0/12 | **18/18 / 0/12** |
| same, 2 min after a pending check | 0/18 (re-ask) / 0/12 | **18/18 / 0/12** |
| same, nothing due: stays on the topic (not an empty plan) | 29/30 | **30/30** |
| 16-message holdout written after the patterns were frozen, patterns only | 0/10 / 0/6 | **2/10** / 0/6 |
| all 46 messages with a perfect `asks_for_reviews` label | 1/28 / 0/18 | **28/28 / 0/18** |
| label end to end through the real MCP server (`sims/fixes/label_smoke_w5.py`, demo-showme after a YED turn, "hit me with a review question", which the patterns miss) | – | label true → `ask_mcq` review; label false → re-ask of the pending YED question |
| all 46 with a careless label (always true) | 1/28 / 0/18 | 28/28 / **8/18 stolen** |
| Plan A (6 takes) | – | identical to s5 |
| wave-4 probes (`probes_w4.py`) | – | 1, 4 and 5 unchanged; probe 2: "Can you test me on my reviews?" now gives a review; probe 3 now shows the ladder (turn 3 step back, 5 worked example, 6 easier prerequisite, 8 stop-or-switch). Its "4 of 8 step-back" count counts every `:stuck` step |

**Read the paraphrase numbers with care.** I wrote the 30-message set and the patterns together, so 18/18 is
in-sample. On the holdout the patterns alone get 2/10. The label is the real fix and the patterns are a fallback. The
label numbers measure the plumbing only. How well Claude or ChatGPT actually sets the label is untested: try it on Wednesday with the real chatbot (5 min).

**Time (student team):** about 2–2.5 h in total.
- Apply and read the diff: 0.5 h.
- Rerun check_mcp, the probes and Plan A with `harness/run_w5.sh`: 0.5 h.
- Try 10 review wordings and 3 stuck turns in the real chatbot: 0.5–1 h.
- Re-shoot nothing: Plan A is unchanged.

**If short of time:**
- Keep the plan.py part (stuck ladder).
- In service.py, the label is the part that matters; the patterns can be cut.
- Cut it all and the cost is only off camera: a failing student loops on reteaches, and "quiz me" paraphrases teach the old topic.

## 0006b / 0006c: labelling rules (wave 5, w5-fix-labels)

The notes are in `work/w5/w5-fix-labels.md`. The probe is `sims/fixes/labels_probe.py`, and the outputs are in `results/w5-labels/`.

**The problem.** A student answers a Verify task, or any question, and the chatbot labels it `request_type: research`.
- `service.py:383–385` then records Ask evidence from the empty `question_features`: `ail_question` scores **0/4 = 0.0**.
- `service.py:416–418` routes the turn to `plan.research`, which gives `answer_with_sources` and a new Ask task.
- The turn is also logged as research for the progress question-feature shares (`service.py:559`).
- In the Plan A "final" take, labelling the 4c line `research` drops Ask from **developing to new** in the progress shot.

A new finding: labelling that answer **`concept`** pulls the course focus. Even a plain "the ONS page says 9.1%…" answer set the focus to
`tax_incidence_split` and produced a course MCQ. So answers to source-checking and how-AI-works tasks should be **`other`**, as the Plan A
labels already are. Course answers and "ok, go on" stay `concept`.

**0006b (text only):** `text/tools/tutor_turn.md` and `text/server_instructions.md`.
- It adds 5 "Labelling rules" bullets in our own words: request_type for answers and acknowledgements, and concept vs research for theory about a real event; the `concept` question feature; source_conflict; engagement; points_met, including partial points and Verify ticks a and d.
- **source_conflict: our choice.** A different figure, date or period counts, and so does a missing claim. Rounding the same figure doesn't. This is w5-02s Option A, and the team should confirm it.
- Instructions: rule 3 now ends "by the rules in tutor_turn", and rule 4 says "fully produced".

**0006c (optional, `edux/service.py`, 3 lines):** an answer object sent with `request_type: research` and no `question_features` is turned into `other` (on an AI-literacy part) or `concept` (on a course part). This happens before anything is recorded or routed. A real new question sent with an answer keeps research, and its Ask evidence still counts. A research label with **no** answer object is fixed by the text only.

| measure | s5 = 0001–0005 | + 0006b | + 0006b + 0006c | + 0006 + 0006b + 0006c |
|---|---|---|---|---|
| check_mcp (load avg < 4) | 74/74 | 74/74 | 74/74 (0006c alone on s5: 74/74 too) | 74/74 |
| server instructions (cap 900) | 889 | 894 | 894 | 894 |
| move sections changed (sentence cap 2, cue cap 15) | – | none | none | none |
| `tools/tutor_turn.md` words (no cap) | 195 | 522 | 522 | 537 (0006 adds a sentence) |
| probe: answers labelled research that write Ask 0.0 (3 cases with an answer object) | 3/3 | 3/3 (the text acts on the bot, not the server) | **0/3** | – |
| probe: answer + new question with 4 features keeps Ask 1.0 | yes | yes | yes | – |
| Plan A final_research (4c labelled research): Ask at turn 5 | **new** | new | **developing** (= final) | – |
| Plan A takes final, final_concept, clean, plan_now, recommended, final_ticks_ad, then_ped | – | – | levels identical to s5 | – |

Under load (load average about 16, other agents running), the timing check failed: median 127–158 ms against a 100 ms limit. Everything passed on a quiet rerun, s5 included.

**Conflicts with 0006.** Both patches touch `text/tools/tutor_turn.md` and 0006c touches `edux/service.py`, but the hunks don't overlap:
- 0006 edits line 3 of tutor_turn.md, and 0006b appends after line 7;
- in service.py, 0006 has one hunk above the 0006c guard and two below it, and none of them overlap.

`patch -p1` in either order (0006 → b → c, or b → c → 0006) gives byte-identical trees, with offsets only and no fuzz.
They don't clash in meaning either:
- 0006's review detection needs `not answer`;
- its probe sends "OK, let's keep going." as concept, which 0006b also says;
- 0006 adds no words to the instructions.

**Behaviour change to know about.** A *matched* Verify answer (no source_conflict) now gets `other` and so an **empty plan**: no feedback
step on the check. Before, it defaulted to concept and got a stray course MCQ. The Verify evidence is still recorded. Plan A is unchanged
because every 4c turn there sets source_conflict.

**Applying.** 0006b and 0006c carry `git format-patch` headers. `git apply --check` and `git am` on a scratch repo of s5 both succeeded,
and the result is identical to the tested tree. 0006 has no mail header, so `git am 000*.diff` stops at 0006: use `git apply` or `patch -p1`
for that file. 0006c is optional, but the `000*` glob picks it up.

**Time:** about 1 h. Agree the source_conflict rule (15 min), apply both and rerun check_mcp (10 min), check in the real chatbot that the
4c line and an explain-back get `other` and `concept` (10 min), and re-key the 02a items (20 min). **If short:** keep 0006c and the
request_type bullet.

## Wave 5: renumbered series 0006–0010 (blind integration check, verifier S)

I worked from the diffs, scripts and READMEs in `combined/` and `sims/gaming/` only. Fresh copies are under
`/tmp/claude-1000/w5-verifyS/`: s5 = export + 0001–0005, and each later sN adds one patch. Outputs are in
`results/w5-S/` and the claim marks are in `work/w5/verify-S.json`. `harness/run_w5s.sh` is transcribed from the commands
I ran, step by step. It has not been run end to end as one script.

### Apply order
The original `0006`, `0006b` and `0006c` files are kept for reference. **Don't use the `000*.diff` glob any more.** It
picks up both 0006 files and the b/c files, and it misses 0010. Name the files explicitly:

| # | file | was | touches |
|---|---|---|---|
| 1–5 | `0001-…` to `0005-…` (as above) | – | – |
| 6 | `0006-w5-stuck-ladder-and-review-requests.diff` | `0006-stuck-ladder-and-review-requests.diff` | plan.py, service.py, server.py, tools/tutor_turn.md, 2 new cue files |
| 7 | `0007-w5-labels-text.diff` | `0006b-labels-text.diff` | text/tools/tutor_turn.md, text/server_instructions.md |
| 8 | `0008-w5-ask-guard.diff` | `0006c-ask-guard.diff` | service.py (3 lines) |
| 9 | `0009-w5-broken-link-counter.diff` | `sims/gaming/counters/c2.diff` | learner.py `found_problem`, service.py |
| 10 | `0010-w5-show-then-answer-counter.diff` | `sims/gaming/counters/c1.diff` | learner.py `_apply_evidence` cap |

```bash
cd <repo on the 05e branch>
C=docs/research/overnight/sims/fixes/combined
for p in $C/000[1-5]-*.diff $C/00{06,07,08,09,10}-w5-*.diff; do patch -p1 < "$p"; done
# or: git am --keep-cr $C/000[1-5]-*.diff $C/00{06,07,08,09,10}-w5-*.diff
```
I regenerated each new file as `diff -ruN a b` between consecutive tested trees and gave it a mail header. The
originals applied in order with offsets only: 0006c at +41 lines, c2's service.py hunks at +53 and c1 at +9. There was
no fuzz, no reject and **no conflict to resolve by hand**. The new files apply at offset 0.

How I checked the series:
- `patch -p1` of 0001–0010 onto a fresh export gives a tree byte-identical to s10.
- `git am --keep-cr` gives the same tree. Plain `git am` strips the CRs from 0004's two CSVs.

On meaning, I read the interactions:
- 0008 rewrites `request_type` before 0009's `_found_problem` runs.
- 0009 adds `reported=` so that a bare report still closes the verify task.
- 0010 caps `immediate` evidence, and 0006's ladder check after a worked example is `immediate`.

### Results per step
- check_mcp: one tree at a time on a quiet machine (load average under 1), on the copy's own localhost server.
- Plan A: `run_episode.py` with 8 takes, the usual 6 plus 2 I added. **final_research** is final with the 4c answer labelled `research`. **clean_ticks_ad** is the dead-page line sent as the verify answer with a,d ticked, which is what 0007's rule asks for.

| step | check_mcp | Plan A, Verify level at 4d (p) | measured |
|---|---|---|---|
| s5 (0001–0005) | 74/74 (timing median 26 ms) | developing (0.748) in all 8; final_research Ask **new** (0.256) | always-failing student: longest bare-reteach run 23, no-MCQ run 24, no stop offer in 30 turns; review asks 1/18 (concept), 0/18 (other or pending) |
| +0006 stuck/reviews | 74/74 | identical to s5 (moves and levels) | bare-reteach run **0**, no-MCQ run **1**, stop/switch offer at **turn 8**, 29/30 plans with an MCQ; open-only failer 11/12 → **1/2**; strong student who misses only extend questions: no ladder (0 worked examples). Reviews: patterns 18/18 asks, 0/12 stolen (in-sample); holdout **2/10**; perfect label **28/28**, 0/18 stolen; careless always-true label 28/28 but **8/18 stolen**. Real MCP server, "hit me with a review question": label true → review MCQ, label false → re-ask (on s10). Server instructions unchanged. |
| +0007 labels text | 74/74 | identical to s6 | text only, so the server can't act on it: answers labelled research still write Ask 0.0 (3/3) |
| +0008 ask guard | 74/74 | final_research Ask new → **developing (0.528)**, its plan now has no research steps; the other 7 identical | answers labelled research that write Ask 0.0: 3/3 → **0/3**; answer + real new question keeps Ask 1.0; research label with **no** answer object still writes Ask 0.0 (text-only territory) |
| +0009 broken-link counter (c2) | 74/74 | final, final_research and recommended (a,c,d): **developing (0.636)**. **final_ticks_ad, clean, plan_now, then_ped, clean_ticks_ad: new (0.300)** (3 developing / 5 new; corrected in wave 6 by verifier U, which reran all 8 takes) | gaming, N=30: L1 ("link is broken") Verify secure 100% → **0%**; L1d (copies publisher and date) 100% → 100% (literal labeller), 0% (skeptical). Honest L0 Verify secure, N=100 on the same seeds: 65% → **59%**; L0s 100% → 100%. Course strategies unchanged |
| +0010 show-then-answer counter (c1) | 74/74 | identical to s9 (all 8) | gaming, N=30: C3 (show me + match) 9 → **0** parts secure; C2m 4.4 → 2.2; C1 false-secure 57% → 17%; C5 2.0 → 0.6. **Honest C0 (N=100): 3.6 → 1.4 parts secure in session, first secure 2.4 → 12.0 min, at +7 days 2.5 → 0.9.** The stuck ladder still holds (same probe numbers), except the student who fails only open answers: **no stop/switch offer in 40 turns** (was turn 15; `results/w5-S/probes_w5long_s{8,10}.txt`), because a later right check resets the miss count; worked examples and MCQs continue, with no bare-reteach runs |

**The Plan A "final" take still ends Verify developing after the whole series, but only at 0.636 and only because the
chatbot ticks c as well as a,d.**
- If it ticks only a,d (final_ticks_ad), or the student says only that the page is dead or wrong (clean, plan_now, then_ped), Verify ends **new** under 0009.
- plan_now is `demo-plan.md`'s current 4c line, so it needs the final wording.
- 0007's own `points_met` rule tells the chatbot to tick a for "wouldn't load" and d for a verdict. So a chatbot that follows it on a dead link sends exactly a,d, which 0009 treats as no evidence (clean_ticks_ad: new).
- 0007's rule and 0009 pull against each other on dead links. Either accept that a dead link alone earns nothing, or shoot only the "the page says 9.1%, not 11.1%" line. Check in the real chatbot that it ticks c on that line.

The 100 ms timing check passed on every tree (medians 26–27 ms) and on every skip tree, so there was no rerun.

### Hours (student team)
- 0006: about 2–2.5 h.
- 0007 + 0008: about 1 h.
- 0009: 0.5 h to apply, plus 0.5 h to re-check the demo lines (re-shoot any take whose 4c line doesn't state what the page shows).
- 0010: 0.5 h to apply and rerun, plus 0.5 h to re-check any secure progress shot.
- Total for 0006–0010: **about 5 h** on top of the 4–5 h for 0001–0005. Each check_mcp run takes about 1 min and each Plan A pass about 3–4 min.

### What can be skipped, and what that means
Each of 0006–0010 left out on its own: the rest of the series still applies (offsets only) and check_mcp passes 74/74
(`results/w5-S/check_skip*.txt`). One exception: the first run without 0007 failed one check, "MCQ options are shuffled
differently for different students" (1 order for 3 students). That check draws one shuffle per student at the current time,
so it is a chance clash. 0007 is text only and doesn't touch the shuffle. Three reruns all passed 74/74 (`check_skip0007_rerun*.txt`).
- **Skip 0010 (c1).** Plan A is unchanged. Off camera, "just show me" and then picking the matching option reaches secure on every part in about 7 minutes (C3: 9/9 parts). Keeping it costs honest students: secure comes much later (C0 secure parts 3.6 → 1.4 in a session). In the demo, a part only reaches secure after a review or a later session. It also stops the stop/switch offer reaching students who fail only explain-backs. Keep it only if the pitch claims "cheap tricks don't reach secure". Otherwise this is the first cut.
- **Skip 0009 (c2).** Plan A keeps 0.748 in every take. Off camera, "the link is broken" makes Verify secure for 100% of the simulated gamers in under a minute (L1). If you keep it, use the final 4c wording and confirm the chatbot ticks c. The honest cost is small (L0 65% → 59%), but a student who genuinely finds a dead link and only says so gets nothing. The
  skeptical-labeller results (L1d, L2 and L3 at 0%) depend on a text sentence that is **in neither 0007 nor 0009**: tick a
  verify point only for what the student found on the source itself, never for what repeats your reply or its citation.
  Without it, L1d (copies the publisher and date from the citation) still reaches Verify secure in 100% of runs on s10.
  Append that sentence to 0007's `points_met` bullet if you keep 0009.
- **Skip 0008.** If the chatbot labels the 4c answer `research`, Ask drops to **new** in the progress shot. Cheap (3 lines): keep it.
- **Skip 0007.** The server is unchanged. The chatbot gets no rules for labelling answers, source_conflict or ticks.
- **Skip 0006.** Plan A is unchanged. Off camera, a failing student gets up to 23 bare reteaches in a row, and "quiz me" paraphrases go to the old focus.

## Wave 6: fairer counters 0009b and 0010b (w6-fix-counters)

**Verified (wave 6, verifier U, `work/w6/verify-U.json`): all 7 claims ✓** (gaming, honest cost, stop/switch offer, Plan A 0.740 in 8/8 takes, clean apply and 74/74). These are alternatives to 0009 and 0010. **Use 0009 or 0009b, never both. The same goes for 0010 and 0010b.** Notes are in `work/w6/w6-fix-counters.md`, results in `results/w6/`, and the scripts in `sims/fixes/w6/`.

| # | file | applies on | touches |
|---|---|---|---|
| 9b | `0009b-w6-dead-link-report-cap.diff` | 0008 | learner.py (`apply_evidence_event`, `_apply_evidence` gains `cap=`, 2 helpers), tools/tutor_turn.md (+34 words) |
| 10b | `0010b-w6-show-then-pick-cap.diff` | 0009b (it reuses 0009b's `cap=`) | learner.py (immediate cap, prerequisite boost), plan.py `_misses` |
| – | `variants/0010b-alone-w6-show-then-pick-cap.diff` | 0008 (series without 0009b) | as 10b plus the `cap=` plumbing; add 0009b's tutor_turn.md sentence by hand |

```bash
C=docs/research/overnight/sims/fixes/combined
for p in $C/000[1-5]-*.diff $C/00{06,07,08}-w5-*.diff $C/0009b-w6-*.diff $C/0010b-w6-*.diff; do patch -p1 < "$p"; done
```
Applying the patches with `patch -p1` to a fresh export gives `edux/` and `text/` byte-identical to the trees I tested. A dry run of 0010b straight on 0008 fails one hunk; use the `variants/` file for that case.

### What changes
- **0009b (dead-link report).** A Verify answer sent with `source_conflict` still scores 1, so an honest a,d tick or a bare report still counts. Until the student has one successful check of their own on Verify (a correct Verify answer that wasn't a report), reports can't lift Verify past `levels.secure - 0.01`, so they cap it at developing. Once the student has done a real check, reports count in full. Text: never tick a point for words that only repeat the chatbot's reply, a point it just showed, or its citation.
- **0010b (show then pick).** Immediate evidence (within 30 min of a worked example or hint) that the student *picks* (an MCQ check, a review or a prequestion) can't make a part secure. An answer the student *writes* (explain_back, extend, past_question) still can.
  - A prerequisite boost from a dependent part is indirect evidence, so it never makes a prerequisite secure on its own. This is the leak that let "teach me + pick the matching option" reach secure under 0010.
  - plan.py: a miss on an open answer is cleared only by a complete open answer. This restores the stop/switch offer that 0010 lost.

### Results
Same harness, seeds and N as `sims/gaming`, plus three adaptive gamers in `sims/fixes/w6/gaming_w6.py`:
- C3t: "teach me" + pick the matching option.
- C3x: "just show me" + match + paste the shown point back.
- L1c: one real check, then "the link is broken".

N = 100 for C0, L0 and L0s, 30 for the rest, plus L0 at N = 300. Base = 0001–0008.

| | base (0008) | 0009 / 0010 | **0009b / 0010b** |
|---|---|---|---|
| Plan A, 8 takes: Verify at 4d | developing 0.748 in all 8 | 0.636 in 3 takes, **new (0.300) in 5** (verifier U) | **developing 0.740 in all 8**; Ask 0.528 and plan moves identical |
| L1 "link is broken": Verify secure | 100% | 0% (shown new) | **0%** (developing, 0.740) |
| L1d with copied details, literal labeller | 100% | 100% | **0%** (developing) |
| L1c one real check, then reports | 100% | 0% | 100% (the rule allows it: one real check + one report) |
| L0 honest partial: Verify secure, N=300 (SE about 3 pts) | 64% | 60% | **62%** |
| L0s honest strong | 100% | 100% | 100% |
| C0 honest: parts secure in session / +7 d / effort-min to first secure | 3.6 / 2.5 / 2.4 | 1.4 / 0.9 / 12.0 | **3.4 / 2.5 / 8.9** |
| C3 show + match | 9 | 0 | **0** |
| C3t teach + match | 9 | 4.0 | **0** |
| C2m middle-length guess | 4.4 | 2.2 | **0** |
| C1 always "A" | 0.8 | 0.2 | **0** |
| C3x show + paste explain-back: literal / skeptical labeller | 9 / 9 | 4 / 2 | **9 / 0** (needs the 0009b text line to be followed) |
| C4 copy explain-back: literal / skeptical labeller | 3.8 / 1.3 | 1.3 / 0.3 | 3.8 / 0.0 |
| open-only failer: stop/switch offer (40 turns) | turn 15 | never | **turn 19** |

The other probes are unchanged from 0008:
- always-failing student: stop/switch offer at turn 8, 29/30 plans with an MCQ, no bare-reteach runs;
- review asks: 18/18, with 0/12 ordinary messages stolen.

`seed-demo` progress for every seeded student is identical to 0008. check_mcp passes **74/74** on 0009b, on 0009b+0010b and on 0010b alone (timing median 25–27 ms, no rerun).

### Hours and what to cut
- 0009b: 0.5 h. No demo re-shoot: every Plan A take still shows developing.
- 0010b: 1 h, including a rerun of check_mcp and the probes. Re-check any course progress shot that relies on a part going secure from MCQs straight after teaching. Such a part now needs an explain-back.
- If short of time, keep 0009b (cheap, and it fixes the demo conflict) and drop 0010b.
- Don't take 0010b without the "never tick what only repeats your reply" sentence. Without it, C3x still reaches 9/9 under a literal labeller.

## 0011: MCQ options of even length rank (wave 6, w6-fix-length)

**Verified (wave 6, verifier V, `work/w6/verify-V.json`): apply + 74/74, ingest warnings, testwise and gaming numbers ✓; economics ~ (see below).** `0011-w6-mcq-length-rank.diff` applies on 0008. Notes and the full before/after row list for the economist are in
`work/w6/w6-fix-length.md`; outputs in `../results/w6-length/`.

**The problem.** After 0004, the key in an example-mini MCQ is usually the middle-length option. A student who
drops the longest and shortest options gets 0.536 of the 28 economics option sets right, and second-longest gets
0.625, against chance 0.312 (`testwise.py`). In play (gaming_sim C2m) that is 57% right and 4.4 false-secure parts.
Only 5 sets had an option outside ±20% of the key, so the cue was **rank**, not spread.

**The change.** It touches the pack and the ingest checks only: no edux/, text/, settings or migration change.
- `coursepacks/example-mini/mark_points.csv`: 5 rows reworded (meaning kept).
- `coursepacks/example-mini/misconceptions.csv`: 17 `wrong_idea` texts reworded (same wrong idea; the corrections are untouched).
- Every misconception is now within ±20% of each key on its part. Each part's keys sit at different ranks around its fixed misconceptions, and first words are varied.
- `ingest/validate.py` `check_option_lengths()` adds two load **warnings** (thresholds are our choice): a misconception more than 20%
  longer or shorter than a mark point of its part, and a pack where the key is the shortest, middle or longest option 15 points more often
  than an even spread. On the old pack: 3 rows, plus "middle in 15 of 22 (about 9 if even)". On the new pack: none.

| measure | s8 = 0001–0008 | + 0011 |
|---|---|---|
| testwise, economics (28 sets, chance 0.312): middle / second-longest / second-shortest | 0.536 / 0.625 / 0.446 | **0.286 / 0.321 / 0.250** |
| … odd first word / testwise_length (punct → absolutes → middle) | 0.414 / 0.446 | 0.235 / 0.339 |
| … highest of every length, position and item-writing cue | 0.625 | **0.375** (target ≤ 0.412) |
| … key rank shortest / middle / longest / tie | 3 / 13 / 3 / 9 | 8 / 10 / 10 / 0 |
| … sequence cue (the option not in the previous point's check, 11 sets) | 1.0 | **1.0, not fixed** |
| gaming C2m (drop longest and shortest), N=30: right / secure parts | 0.57 / 4.4 | **0.19 / 0.2** |
| gaming C2l2 (second-longest, new), N=30 | 0.65 / 5.2 | 0.19 / 0.2 |
| gaming C2x (longest or shortest, new), N=30 | 0.19 / 0.6 | 0.33 / 1.8 |
| gaming C2r (random option, same flow: the control), N=30 | 0.31 / 1.1 | 0.33 / 1.5 (C2x is within noise of this) |
| honest C0, N=100 | 0.75 / 3.6 | 0.75 / 3.6 |
| check_mcp | 74/74 | **74/74** |
| Plan A (6 repo takes) | – | identical moves, evidence and levels |

**Conflicts.** None. 0011 shares no file with 0009, 0010, 0009b or 0010b:
- applied before or after 0009+0010, or before or after 0009b+0010b, `patch -p1` gives byte-identical trees with no offsets;
- check_mcp gives 74/74 on 0001–0008 + 0011 + 0009 + 0010 on the second run (the first, at load average 5, failed only the timing check: 135 ms);
- on 0001–0008 + 0011 + 0009b + 0010b it gave 74/74 on the third run. The first two failed only the 100 ms timing check (128–140 ms) at load average 7–8. That tree without 0011 ran at 96 ms in the same minute.

`git am --keep-cr` works as for 0001–0008.

**On camera.** Only then_ped's turn-5 prerequisite MCQ (ped_definition) shows changed distractor wording. The AI-literacy rows that Plan A uses are untouched.

**Read with care.**
- The after-numbers are in-sample: the texts were tuned while watching these 28 sets, with a standard error of about ±0.09 per strategy.
- The ingest warning is the part that generalises to the 9EC0 pack.
- Two rows need an economist's eye: `tax_incidence_split_p2` and `_m2`. Verifier V (~): both ignore supply elasticity (incidence depends on PED relative to PES), m2 is now absolute ("most of the tax") rather than comparative, and the two read as near mirror images, which is a pair cue. Minor: `yed_definition_m1` ("its own price" has an unclear referent) and `pes_formula_m1` (carries a true clause about PED). Reword, then rerun `testwise.py`.
- The full stack 0001–0008 + 0011 + 0009b + 0010b passing 74/74 is the scout's result; verifier V checked 0001–0008 + 0011 only.
- The sequence cue needs point-specific misconceptions (later, L). Don't claim the MCQs can't be gamed.

**Time:** about 1 h: apply and reload (10 min), economist reads the 22 rows (30 min), rerun check_mcp and testwise (10 min).
**If short:** keep the `validate.py` part and the pack rows the economist approves. Each row stands alone, but rank balance
needs most of them, so rerun `testwise.py` after a partial take.
