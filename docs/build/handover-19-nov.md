# Handover: the overnight build, 19 November 2026

Written for Vishnu and whoever picks this up next. It says what is built, in what order to merge it, what needs a human decision, and what to check before filming. Everything is on pull requests; **nothing has been merged**. The latest version of this note is on the tip of the stack (see the bottom).

## 1. What is built (all on open pull requests)
| PR | Branch | What |
|---|---|---|
| #48 | `build/synapse-rename` | Project is Synapse (eduX26 is the competition); repo renamed `synapse-eduX26` |
| #49 to #53 | `build/fix-*` | Part 1 fixes: exchange-nudge ceiling 0.35 (strict), results counted as sent (compact JSON), personal learning rate off by default, priorities, reply style, engagement rules |
| #54 | `build/data-handling` | Student key hashed, opaque ids, `delete-student`, `export-student`, `leave-student`, `purge`, retention settings (decision 0011) |
| #55 | `build/fatigue-time-on-task` | Fatigue as pacing from elapsed time and rapid guesses; no mood inference (0013) |
| #57 | `build/formative-literacy-wording` | Ask/Verify shown as practice feedback with the evidence behind them (0014) |
| #58 | `build/class-coverage-and-starting-points` | Classes, "taught in class", starting points, display rule (0015) |
| #59 | `build/learner-cache` | Per-session offset cache; 600-answer rebuild 32.9 s to 1.9 s (0016) |
| #60 | `build/bridge-ending` | Ending tiers and the bridge question (0017) |
| #61 | `build/class-assessments` | Class tests, reminders, `plan_my_study` (0018) |
| #62 | `build/calibration` | "How sure are you?" and a calibration line, never feeding the estimate (0019) |
| #63 | `build/review-threshold-simulation` | Simulation: keep `review_when_below` at 0.50 (0020) |
| #64 | `build/find-the-error` | Find-the-error practice, **built and off by default** (0021) |
| #65 | `build/demo-path-and-labels` | Demo script update, `EDUX_CONFIDENCE`, settings labelling rule |
| #66 | `build/limits-and-notice` | Input length limits; pupil-facing data notice |
| #67 | `docs/aided-unaided-scoping` | Aided/unaided evidence scoping (0022, **held**); Plan A re-run |
| #68 | `docs/dfe-safety-mapping` | Mapping to the DfE product safety standards; signposting line |
| #69 | `build/soak-test` | Seeded random soak test |
| #70 | `build/find-error-check-sentence` | Server checks the named sentence in find-the-error |
| #71 | `build/ci-and-coverage` | CI (ruff, mypy, pytest, coverage 94%), a soak test, a days-left fix |
| #72 to #77 | `build/web-*` | The web pages (see 1b) |
| #56 | `docs/dpia-and-scoping` | DPIA notes (updated for the newer tables), find-the-error scoping (0012). A sibling off #54, not in the chain |
| #20 | `research/overnight` | Untouched |

**Merge order** (each a fast-forward of `main` once the one before is in): #48, #49, #50, #51, #52, #53, #54, then #55, #57, #58, #59, #60, #61, #62, #63, #64, #65, #66, #67, #68, #69, #70, #71, then #72, #73, #74, #75, #76, #77. Merge #56 after #54 (it only adds docs). Decision records 0021 and 0012 link to each other, so merge #56 before or with #64 to avoid a dead link.

## 1b. The web pages (added later on 19 November; PRs #72 to #77, stacked after #71)
A course map (`/map`), a student page (`/me`) and a teacher page (`/teacher`), with teacher keys, bearer-only sign-in and a strict content security policy. See [step 09](steps/09-web.md) and decisions 0023 and 0024. **Content review (approve/reject/edit pack rows) is not built.** Product calls for Vishnu: whether teachers see the help-seeking pattern at all, the class band wording, fonts, and the public example map on the live URL. Not tested with real students, teachers, screen readers or a phone.

## 2. Checked on the tip of the stack (19 November)
- `pytest`: 215 passed.
- `scripts/check_mcp.py`: all checks passed, **with find-the-error off and on**; largest `tutor_turn` result 2,327 to 2,395 of 2,400 characters; rebuild identical for every demo student.
- Server instructions: **898 of 900 words**.
- Soak test: seeds 1 to 9 at 500 random turns each, clean.
- Plan A (the AI-literacy episode, overnight `run_episode.py`, six scenarios): Verify ends at **0.740, developing** (the same as overnight), Ask at 0.528; none over budget. The margin below secure is 0.01.

## 3. Decisions for Vishnu (product calls)
1. **Find-the-error (0021): switch on or not.** It is off. Evidence for it is thin (0012). Turn on with `EDUX_FIND_ERROR=1`. A teacher should check the generated items first.
2. **Keep `review_when_below` at 0.50 (0020)?** The simulation found no case for 0.75 (retention 0.182 against 0.202; fewer truly secure parts, 0.45 against 0.73). Judgement call either way.
3. **Aided and unaided evidence (0022).** Recommended: a part cannot show as secure without one unaided correct answer some hours after teaching. It changes what the demo shows, so held.
4. **Hint ladder (C12).** The DfE standard 10 says full solutions only after a genuine attempt; the first "just show me" breaks that. Raised in priority; still held.
5. **Confidence question on the filmed demo?** It adds one exchange to checks and reviews. `EDUX_CONFIDENCE=0` removes it.
6. **Safeguarding (C22)** is required before any pupil pilot: the school's chatbot must do distress detection and DSL alerts; Synapse keeps no message text and must say so (see `dfe-safety-mapping.md`).

## 4. Before filming
- Reseed shortly before recording (`seed-demo --reset` keeps the keys). Re-run Plan A if anything in `settings.toml` changes.
- Dry run in claude.ai: results are now compact JSON; confirm the chatbot reads them normally. **Not done.**
- Film with web search off (Plan A). Do not add a Verify task: Verify is 0.01 below secure.
- Captions: simulations are synthetic; teacher view is a mock-up; never "gaming-proof".
- `docs/demo-script.md` starts with what changed on the demo path.

## 5. Open items (not built)
- Held (Part 3): OAuth / key rotation, better reteach (C12), server-side check of `points_met` (C2), aided/unaided (C8).
- Rate limiting and a migration lock (C18). English as an additional language and plain-language audit (C21). Safeguarding pathway (C22). Teacher sign-off of the pupil notice and of find-the-error items.
- A teacher-facing offloading rate (DfE standard 4): the data exists, the view does not.
- Known limit: two turns inside one second can replay in a different order after a rebuild (08-tests).
- `settings.md` removed-key drift was not fully re-audited.

## 6. Where things are
Decision records `docs/decisions/` (index in its README; the living register is 0002). Step docs `docs/build/steps/05k` to `05za`. Reference docs `docs/build/reference/`. Research pack (outside git): `/home/ajk/Projects/eduX26/research/`.
