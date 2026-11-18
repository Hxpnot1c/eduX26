# Morning brief (after wave 5)

**Start here: [wednesday-build-list.md](wednesday-build-list.md) (10 patches, check_mcp 74/74 after each; 0009b and 0010b verification pending)** and [pitch-script.md](pitch-script.md) (every word to record, Plan A and Plan B).

**Needs a human:**
- Paste the Challenge 1 brief into `challenge-brief.md`.
- Decide whether a matched Verify answer can get an empty plan under 0007.
- Confirm the `source_conflict` rule (a different figure counts).
- E reads 0004's pack rows.

## Wednesday
1. **09:00–13:00: fast-forward 05e, then 0001–0004.** Decide on 0002 before 0003.
2. **13:30–15:15: 0006 (stuck ladder, review requests), 0007 + 0008 (labelling text, Ask guard).**
3. **15:15–16:30: 0009b and 0010b**, the wave-6 counters that replace 0009 and 0010 (recommended, verification pending). Dead-link gamers and "show me, then pick" gamers stop reaching secure. Honest students barely lose. Plan A stays Verify developing: no re-shoot. Drop 0010b first if late. 0005 gives way.
4. **E checks the mock-ups at 1280×720, light and dark.** Say "this is the design" over anything not built.
5. **16:30 freeze, 18:00 gate, film until 21:00.**

## Three strongest pitch points
- **The market is known.** 21,005 9EC0 certificates in England in 2024–25, 51.5% of A level Economics (w4-08-08 ✓).
- **Checking is rewarded.** Catching a bad source moves Verify from new to developing (simulation; w4-fix-verify-1 ✓).
- **We show Microsoft's cost.** It is about 4p a call, £22.50 a student a year in our central case (w5-08u-01 ✓). [roadmap.md](roadmap.md) has the after-competition slide.

## Three biggest risks
- **Gaming.** Cheap tricks still out-earn honest work in simulation, and the MCQs have a 58% middle-length cue. Never say "gaming-proof".
- **Cost.** On Copilot, even a free eduX costs more than Sparx above 75 calls a year. Microsoft takes 4.5× our revenue.
- **Labels.** Verify needs `source_conflict`. 0010b relies on the chatbot not ticking pasted replies (untested). Label agreement is not yet shown.

## What changed since wave 4
- **More patches.** 0006–0010 were stacked by a blind verifier: offsets only, 74/74 after each (w5-fix-combined-2 ✓). 0009b/0010b now replace 0009/0010.
- **Gaming red team** ([06](06-settings-simulation.md)). "The link is broken" made Verify secure for 100% of simulated gamers. Wave 6's 0009b: 0%.
- **Label dry run** ([02a](02a-label-agreement-protocol.md)). A Claude proxy against a Claude-written key: a pipeline test, not agreement. It found the request_type bug that 0008 guards.
- **Unit economics** ([business plan](business-plan.md)). The class cap is about £65 a month in term, not £45. 05e calls `tutor_turn` on research replies too.
- **New:** [roadmap.md](roadmap.md) (12 months, four gates) and [mockups/](mockups/README.md).
- **380 findings.** Wave 5 added 23 (10 ✓, 13 ~).
