# Wednesday build list (18 November)

One list, in dependency order, with hours and owners. It merges the build fixes from [demo-plan](demo-plan.md) §F (MUST and SHOULD), [06](06-settings-simulation.md), [02](02-ai-literacy-assessment.md), [05](05-product-features.md) and [09](09-safety-ethics.md). The words to record are in [pitch-script.md](pitch-script.md).

**Wave 4 is writing tested diffs for items 2–7** (`sims/fixes/`, specs in `work/w4/`). The first drafts there, two alternative focus diffs for item 3, are not reviewed yet. This file will be updated with the tested diffs, their before/after numbers and revised hours. Until then the hours below are the reports' estimates.

**Line numbers.** Every `file:line` quoted in the reports is for `main`. After item 1 the code is the 05e branch and the lines shift, so find the code by the function names given here.

## Owners (four roles, working in parallel)

| role | what they own on Wednesday |
|---|---|
| **B1 · Build lead** | Item 1, then the learner and planner fixes (2, 5 code, 6). Merges every fix and runs the checks after it. |
| **B2 · Second builder** | The literacy service fixes (3, 4) and the decay fix (7). |
| **E · Economist** | Course-pack and literacy-option text (5 text, 8). Checks the economics in the dry run. |
| **P · Pitch lead** | Pastes the Challenge 1 brief into `challenge-brief.md` (needs a human). Writes the line card, sets up the adult account, builds the deck, drives the dry run and the filming. |

**After every merged fix (B1, about 15 min each, already counted in the hours):** run `scripts/check_mcp.py` (must stay 74/74). Then re-run the rehearsal (`sims/demo-05e/run_episode.py`) and check the console for OVER BUDGET. The largest result has only about 80 characters to spare (w3-07-c2 ~).

## The list

S = under 2 h, M = half a day (the reports' scale). Clock times assume a 09:00 start.

| # | item | owner | hours | when | rests on | if not in by the freeze |
|---|---|---|---|---|---|---|
| 1 | **Fast-forward `main` to `build/05e-literacy-coaching`.** The branch already contains `main` and is 14 commits ahead with no conflicts, so this takes minutes. Run `check_mcp.py` (74/74) on the result. | B1 | 0.5 | 09:00–09:30 | coordinator; w3-07-c6 ✓ | Never dropped. If it fails, film Plan B ([demo-plan](demo-plan.md) §A). |
| 2 | **Crash and loop bugs, divide-by-zero first.**<br>(a) Clamp `p_known` to [0.001, 0.999] after the update in `_apply_evidence` and again in `apply_exchange`, with a test: 50 right checks on one part, then one more exchange, and no exception. **30 min, first.**<br>(b) Step back once per stuck part per session (`plan.choose`, stuck branch, and `stuck_parts`).<br>(c) "Quiz me on what's due" reaches the reviews: don't inherit `last["focus"]` on a review cue or a new session (`service.tutor_turn`). | B1 | 2.0 | 09:30–11:30 | [06](06-settings-simulation.md) recs 1–3; w1-06-01 ✓, -02 ~, -03 ✓; demo-plan M6 | (a) never dropped. (b)–(c): reset between judges, don't let a judge keep answering prerequisite checks, and make no spacing or "reviews due" claim. |
| 3 | **Literacy turns never set or keep a course focus.** A research or `source_conflict` turn doesn't resolve course parts. An answered how-AI-works check doesn't hand over to teaching when the turn had no course message (`service.tutor_turn`, `plan.choose`). | B2 | 2.0 | 09:30–11:30 | demo-plan M1; w3-07-c3 ✓ | Video: the printed line card (never type "give", "link", "ONS", "first", "cost", "different" or "shows"). Expo: §B's honest script. This is the one break that can't be scripted round live. |
| 4 | **Reporting a mismatch or a dead page counts as checking; an ignored or moved-on task is missing.**<br>• Score `ail_task` as met when `source_conflict` comes with it, or make "opened + said it didn't match" a full answer.<br>• In `service._literacy_followup` and `_how_ai_works`, write a `literacy_ignored` event, not `ail_task 0` or `ail_how 0`. Show "tasks done: n of m". | B2 | 1.5 | 11:30–13:00 | demo-plan M2–M3; [02](02-ai-literacy-assessment.md) recs 4–5; w3-07-c5 ✓, w2-02-11 ✓ | Use the mismatch line, sent as the Verify answer with points a, c and d. After a dead-page take, never show Verify in 4d. At the expo, finish the episode before any PED question. |
| 5 | **MCQ options: description fallback, m2 and absolute words.**<br>• **Code (B1, 1 h):** never use the node description as an option (`plan._points` fallback). Skip the MCQ and use explain-back when a part has no points. Add an ingest warning. Keep the mark point as the key, not the exemplar: commit `f0a1c36` chose the point on purpose. A wave-4 scout is testing this fix.<br>• **Literacy options (E):** remove m2 from every fabrication option set (`ingest/ai_literacy/`). Rewrite them to pass the cue check: no "always", "only" or "on purpose", lengths matched within a few characters, **no full stops** (the 05e set's form).<br>• **Economics keys (E):** add mark points for the demo parts (`ped_definition`, `ped_formula`, `ped_values`, `tax_incidence_split`). Write each key as a **full sentence with a full stop**, like its `wrong_idea` distractors, within 0.7–1.3× their median length (our choice). No absolute words in distractors either. E's two text tasks take 2 h together. | B1 + E | 3.0 (1 + 2) | B1 11:30–12:30; E 09:30–11:30 | demo-plan M4–M5; [02](02-ai-literacy-assessment.md) rec 3; [05](05-product-features.md) rec 11; [04](04-economics-education.md) rec 1; w3-05-08 ~, w3-07-c7 ✓ | Hold on the first line of each reply and never close up on options. Use the dead-page 4c version: pick m1 and cut past the options. |
| 6 | **Literacy settings, and How AI works as per-part counts.**<br>• Settings (15 min): `literacy.ask_min_features = 3`, `ail_question` guess .30, `ail_unprompted` guess .20.<br>• Counts: `get_my_progress` shows "checked n, right m; still held: …", not a level. | B1 | 1.5 | 13:00–14:30 | [02](02-ai-literacy-assessment.md) recs 2 and 6; w2-02-08 ✓, w2-02-05 ~; demo-plan M7 | Settings: drop the slide-6 add-on in the pitch script, and keep 4b at 3 or more features anyway. Counts: highlight only the "still held" line in 4d. If asked: "one answer is thin evidence; here's the count", and show the `state` pane. |
| 7 | **Decay fix (b), then (c) if time.**<br>(b) In `part_p`: cap a never-right part at its prior and show "not yet shown". Keep `level()` returning "new". About 1 h.<br>(c) Decay towards the prior: give `p_now` a floor argument, with a test and `rebuild_all()` after deploying. About 2–3 h, **optional**. **Merge by 15:30 or leave it until after filming:** it changes stored state, so it needs a rehearsal and `check_mcp` pass before the freeze. It isn't on camera. | B2 | 1.0 (+1.5–2.5) | (b) 13:00–14:00; (c) 14:00–15:30, hard stop | [06](06-settings-simulation.md) recs 9–10; w3-06-01 ✓, -05 ✓, -08 ✓, -09 ~ | No ranking claim and no "not yet shown" line ([06](06-settings-simulation.md) rec 11). Don't linger on the `state` pane. |
| 8 | **Content fixes.** Correct `externality_tax_eval_m1`: a tax internalises the externality and removes the welfare loss, not the external cost (wording in [04](04-economics-education.md)), and drop "always" from its `wrong_idea`. Give `ped_formula`'s "keep the minus sign" its own sign-error misconception. Check the demo parts' points from item 5. Run `ingest.cli validate` clean. | E | 1.0 | 11:30–12:30 | [04](04-economics-education.md) recs 1–2 | Keep the externalities part off camera. If a judge reaches it, say the correction is being fixed. |
| — | **Code freeze and final checks** (`check_mcp` 74/74, rehearsal, no OVER BUDGET), then `seed-demo --reset`. | B1 | 2.0 | 14:30–16:30 (B1 merges and checks; nothing merges after 16:30) | demo-plan recs 18, 20 | — |
| 9 | **Dry run in claude.ai, adult account, web search off.** Type the line card verbatim. Expand every tool call and check the labels (4a/4b `research`, 4b 3 or more features, 4c `source_conflict: true`). Any miss: reset, new chat, retake. **18:00 gate:** Plan A needs the fixed 05e build, `check_mcp` passing with no OVER BUDGET, and one end-to-end episode with the right labels and no retake. Otherwise film Plan B. | P drives; B1 watches labels and console; E checks economics; B2 on fixes | 1.5 | 16:30–18:00 | demo-plan recs 1, 16; w3-07-c1 ✓, -c4 ✓ | Never dropped. |
| 10 | **Film** Plan A or Plan B from [pitch-script.md](pitch-script.md) §1. Reset and new chat before every take. Then record the two offline fallback clips. | P + E (driver); B1 console; B2 fallback clips | 3.0 | 18:00–21:00 | demo-plan recs 3–5, 7 | Never dropped. Edit on Thursday. |
| 11 | **Label-agreement study** (optional). Rewrite at least 20 of the 40 draft messages in a student voice and commit them, then two blind raters, two bot runs and κ pooled per skill ([02a](02a-label-agreement-protocol.md)). | all four (P and E rewrite the messages) | 2.0 × 4 people (+1 to rewrite) | Wednesday 21:00–23:00 or Thursday morning | [02](02-ai-literacy-assessment.md) rec 8; w3-02e-01 ✓, -06 ✓ | Slide 6 keeps "we're checking those labels against two humans", with no number. If the study is dropped rather than moved, say "next, we check those labels". |

**Hours by owner before the dry run:**
- B1: 7 h (items 1, 2, 5 code, 6 and the freeze), with lunch 12:30–13:00.
- B2: 4.5 h, or 6 h with 7(c).
- E: 3 h. E then helps P with the line card and the item 11 messages.
- P: the deck, the brief, the line card and the account. The critical path is B1's, ending at 16:30.

## CUT LINE: if behind at the 16:30 freeze (18:00 gate)

**Never cut:** 1, 2(a), 9 and 10. Anything not merged and passing by the **16:30 freeze** is dropped and its workaround switches on; the dry run tests the frozen build. The **18:00 gate** then decides Plan A or Plan B. It does not wait for fixes. Drop in this order (first to go at the top):

| drop order | item | on-camera workaround |
|---|---|---|
| 1 | 11 Agreement study | Move it to Wednesday night or Thursday. Slide 6 says "we're checking those labels" with no number, or "next, we check" if it's dropped. |
| 2 | 7(c) Decay towards the prior | (b) alone covers what a judge can see. No ranking claim. |
| 3 | 7(b) Not-yet-shown cap | No "not yet shown" line. Don't open `state` for long; no slide ranks students. |
| 4 | 6 Per-part counts | In 4d, highlight only the "still held" line, never "How AI works: new". |
| 5 | 6 Settings | Drop the slide-6 add-on ("5% or fewer…"). 4b keeps 3 or more features. |
| 6 | 2(b)–(c) Loop and "what's due" | Reset between judges, and don't let a judge keep answering prerequisite checks. No spacing claim. |
| 7 | 4 Verify credit and missing tasks | Use the mismatch line as the Verify answer (points a, c, d). After a dead-page take, never show Verify. Finish the episode before any PED question. |
| 8 | 5 MCQ fixes | Use the dead-page 4c and pick m1. Hold on each reply's first line; no option close-ups. |
| 9 | 8 Content | Keep the externalities part off camera. |
| 10 | 3 Focus fix | Film from the line card. At the expo, use §B's honest script; this is the one item with no clean live workaround, which is why it is built first. |

**Thursday (not on this list):** edit the video, build the deck from [pitch-script.md](pitch-script.md) §2, print the leave-behind (§3), and rehearse the expo script five times. Submission closes at 23:59.
