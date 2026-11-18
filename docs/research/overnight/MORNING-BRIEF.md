# Morning brief (after wave 6)

**Start here: [wednesday-build-list.md](wednesday-build-list.md) (11 patches, each checked by a blind verifier; check_mcp 74/74 after each)** and [pitch-script.md](pitch-script.md) (every word to record, Plan A and Plan B).

**Needs a human:**
- Paste the Challenge 1 brief into `challenge-brief.md`.
- Decide whether a matched Verify answer can get an empty plan under 0007.
- Confirm the `source_conflict` rule (a different figure counts).
- E reads 0004's pack rows and 0011's 22 rewordings, and rewords `tax_incidence_split_p2`/`_m2` (they ignore supply elasticity).

## Wednesday: five things
1. **09:00–13:00: fast-forward 05e, then 0001–0004.** Decide on 0002 before 0003. E holds edits to 0011's 22 rows until 0011 is in.
2. **13:30–15:30: 0006, 0007 + 0008, then 0011** (MCQ length rank: pack text and ingest warnings, 15 min, no code).
3. **15:30–16:00: 0009b** (dead-link report cap). **0010b only if 0009b passes by 15:00**; otherwise drop it. 0005 is optional and doesn't fit.
4. **Test copies with an absolute `PYTHONPATH`, and print `edux.__file__`.** A relative path silently runs unpatched code.
5. **16:30 freeze, 18:00 gate, film until 21:00.** Re-capture shot 5 after 0011. Over the mock-ups, say "this is the design".

## Three strongest pitch points
- **The market is known.** 21,005 9EC0 certificates in England in 2024–25, 51.5% of A level Economics (w4-08-08 ✓).
- **Checking is rewarded, not gamed.** Catching a bad source moves Verify to developing (0.740); "the link is broken" alone no longer reaches secure (simulation; w6-planA ✓, w6-c2b-1 ✓).
- **We show Microsoft's cost.** About 4p a call, £22.50 a student a year in our central case (w5-08u-01 ✓).

## Three biggest risks
- **Gaming.** The point-order cue remains, and pasted explain-backs reach secure if the chatbot ticks literally. Never say "gaming-proof".
- **Cost.** On Copilot, even a free eduX costs more than Sparx above 75 calls a year.
- **Labels.** Verify needs `source_conflict`. 0010b needs the chatbot not to tick pasted replies. Neither is tested on a real chatbot.

## What changed since wave 5
- **Counters verified.** 0009b and 0010b: all 7 claims ✓ (verifier U). Plan A Verify reads 0.740, not 0.748. Honest cost: 3.6 → 3.4 parts secure, but the first secure part takes 8.9 effort-minutes, not 2.4.
- **0011 is new.** The middle-length MCQ cue falls from 0.536 to 0.286 (chance 0.312); in play, 57% → 19% right (w6-len-3 ✓, w6-len-4 ✓, in-sample).
- **Path audit.** Stored wave-4 and wave-5 numbers reproduce with absolute paths (w6-path-3 ✓, -4 ✓).
- **New:** [mockups/](mockups/README.md) (teacher view, student progress; not built) and [roadmap.md](roadmap.md).
- **397 findings.** Wave 6 added 17 (14 ✓, 3 ~).
