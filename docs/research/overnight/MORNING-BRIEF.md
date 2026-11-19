# Morning brief (after wave 7)

**Start here: [RUNBOOK.md](RUNBOOK.md) first** (one page, commands tested on a fresh clone), **then [pitch-script.md](pitch-script.md)** (every word to record, Plan A and Plan B). [wednesday-build-list.md](wednesday-build-list.md) is the detailed reference.

**Needs a human:**
- Paste the Challenge 1 brief into `challenge-brief.md`.
- By 13:30, P and E: the empty plan after a matched Verify answer (default: accept it for now) and the `source_conflict` rule (default: Option A, a different figure counts).
- E reads 0004's pack rows and 0011's 22 rewordings, and drafts (B1 applies after 0011) a rewording of `tax_incidence_split_p2`/`_m2` (they ignore supply elasticity).

## Wednesday: five things
1. **09:00–13:00: fast-forward 05e, then 0001–0004.** Decide on 0002 before 0003. E holds edits to 0011's 22 rows until 0011 is in.
2. **13:30–15:30: 0006, 0007 + 0008, then 0011** (MCQ length rank: pack text and ingest warnings, 15 min, no code).
3. **15:30–16:00: 0009b** (dead-link report cap). **0010b is dropped by default**: start it only if 0009b has passed `check` by 15:00. 0005 is optional and doesn't fit.
4. **Budget: the largest result is 2,395 of 2,400 characters.** Watch over budget in `check` and the dry run; fallback: drop one reference block or trim text.
5. **16:30 freeze, 18:00 gate, film until 21:00.** Re-capture shot 5 after 0011. Over the mock-ups, say "this is the design".

## Three strongest pitch points
- **The market is known.** 21,005 9EC0 certificates in England in 2024–25, 51.5% of A level Economics (w4-08-08 ✓).
- **Checking is rewarded, and the cheap tricks we found are capped.** Catching a bad source moves Verify to developing (0.740); "the link is broken" alone no longer reaches secure (simulation; w6-c2b-1 ✓).
- **One AI-literacy moment, scored by our server alone.** The chatbot labels; fixed rules score. (Microsoft's cost, about 4p a call, is for Q&A only, not the pitch; w5-08u-01 ✓.)

## Three biggest risks
- **Gaming.** The point-order cue remains, and pasted explain-backs reach secure if the chatbot ticks literally. Never say "gaming-proof".
- **Cost (Q&A).** On Copilot, even a free eduX costs more than Sparx above 75 calls a year.
- **Labels.** Verify needs `source_conflict`. 0010b needs the chatbot not to tick pasted replies. Neither is tested on a real chatbot.

## What changed since wave 5
- **Wave 7:** [RUNBOOK.md](RUNBOOK.md); the full stack re-verified (74/74; verifier W).
- **Counters verified.** 0009b and 0010b: all 7 claims ✓ (verifier U). Plan A Verify reads 0.740, not 0.748. Honest cost: 3.6 → 3.4 parts secure, but the first secure part takes 8.9 effort-minutes, not 2.4.
- **0011:** middle-length MCQ cue 0.536 → 0.286 (chance 0.312; w6-len-3 ✓, in-sample).
- **397 findings.** Wave 6 added 17 (14 ✓, 3 ~).
