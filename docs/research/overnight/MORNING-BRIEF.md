# Morning brief (after wave 1)

**Needs a human:** paste the Challenge 1 brief from the EduX site into the repo (it renders only in a browser). Save it as `challenge-brief.md` here.

## Wednesday: five things, ranked
1. **Merge 05e and pass the 18:00 gate.** Merge `build/05e-literacy-coaching` into `main`. Run `scripts/check_mcp.py`, then one claude.ai dry run of the literacy episode with web search off. Effort M. Owner: build lead. ([demo-plan](demo-plan.md) rec 1)
2. **Fix the give-away MCQs before filming.** Economics pack: correct options as full sentences, matched in length. Drop absolute words from `ingest/ai_literacy/misconceptions.csv`. Correct `externality_tax_eval_m1`. Effort S. Owner: an economist on the team. ([04](04-economics-education.md) recs 1–2; [02](02-ai-literacy-assessment.md) rec 3)
3. **Small branch fixes before filming.** Set `literacy.ask_min_features = 3` and the `ail_unprompted` guess to 0.20. Record an ignored task as missing, not 0. Delete line 3 of `text/style.md`. Add `readOnlyHint` to `get_my_progress`. Effort S each. Owner: build team. ([02](02-ai-literacy-assessment.md) recs 2, 4, 6; [09](09-safety-ethics.md) rec 1; [05](05-product-features.md) rec 4)
4. **Film Plan A.** A 72-second literacy episode that ends on How AI works, not Verify. Adult-account caption; elasticity gets 20 s. Effort M. Owners: one talker, one driver. ([demo-plan](demo-plan.md))
5. **Build the deck.** Slides: definition, rubric, validity argument, works-with line, mock teacher view. No Khanmigo line, no Gemini claim. Effort S–M. Owner: pitch lead. ([pitch-notes](pitch-notes.md))

## Three strongest new pitch points
- **A recognised anchor.** The final OECD–EC AILit Framework (2026) says AI literacy is not tool use. We score behaviour, not use (w1-02-01 ✓, w1-02-02 ✓).
- **Observing beats asking.** Self-rated AI literacy correlated only r = .21 with a knowledge test (w1-02-25 ✓). A performance test predicted AI-assisted work; self-report did not (w1-02-23 ✓).
- **Distractors from evidence.** 36% of UK adults read falling inflation as falling prices (w1-04-07 ✓). On one opportunity-cost item, about one economist in five chose the intended answer, though the key is disputed (w1-04-01 ✓).

## Three weaknesses judges will spot
- **The video shows a revision tutor.** 05e is unmerged and the current script has no literacy moment. The red team scored problem fit 2 out of 5 ([01](01-competition-fit.md)).
- **Literacy levels inflate easily.** One "I checked" gives Verify 0.82. With 15% label noise, 11–16% of students without the skill end "secure" (w1-02-32 ✓; simulation, synthetic students). Correct MCQ options stand out by form ([04](04-economics-education.md)).
- **No tested under-18 route.** claude.ai is 18+ (w1-05-02 ✓). Gemini school accounts can't add MCP (w1-05-09 ✓). Copilot Studio is untested. Keys are stored in plaintext ([09](09-safety-ethics.md)).

## What changed
First wave: 97 findings: 67 ✓, 30 ~ and 0 ✗. Each claim was checked by one of four blind verifiers. Six red-team personas raised 30 objections ([judge-panel](judge-panel.md)). The simulation report (06) is in progress.
