# Morning brief (after wave 4)

**Start here: [wednesday-build-list.md](wednesday-build-list.md) — 5 tested patches, check_mcp 74/74**, and [pitch-script.md](pitch-script.md): every word to record, Plan A and Plan B.

**Needs a human:** paste the Challenge 1 brief into `challenge-brief.md`.

## Wednesday: five things
1. **09:00: fast-forward `main` to 05e, then 0001 (core) and 0002 (focus).** B1, 1.5 h. Decide on 0002 before 0003; skipping it means the 0003 variant.
2. **0003: Verify scoring, with migration 010.** 1 h. A reported dead or mismatched page counts as checking. An ignored task is a skip, not a 0.
3. **0004: MCQ code and pack rows.** 1.5 h. Economist reads the drafted rows from 09:30.
4. **0005: decay, optional.** B2. Merged by 15:00 or dropped. If it goes in, re-capture the demo students.
5. **16:30 freeze.** Dry run, search off; check `source_conflict` on 4c. **18:00 gate.** Film until 21:00.

## Three strongest pitch points
- **The market is known.** About 21,000 9EC0 certificates in England in 2024–25: 51.5% of A level Economics, up 42% in four years (w4-08-08 ✓). That is slide 8.
- **Checking is rewarded.** After 0003, catching a bad source moves Verify from new to developing. Q&A only: simulation (w4-fix-verify-1 ✓).
- **The checks can't be gamed by form.** A testwise student who knows nothing scores 0.28 against chance 0.31, down from 0.96. Q&A only, simulation (w4-fix-mcq-1 ✓).

## Three biggest risks
- **The Verify fix needs the chatbot's `source_conflict` label.** Without it, Verify stays new.
- **Steps 4 and 5 change on-screen wording and levels.** Re-capture after them; watch for OVER BUDGET (unchecked on the patched stack).
- **Microsoft's opt-in admin switch** locks students to Study and Learn. Any school that turns it on is closed to eduX (MC1548047, read on a mirror; w4-08-01 ~).

Minor: seven reteaches in a row for a failing student; "what's due" needs exact wording; focus fix loses 2/21 genuine questions.

## What changed since wave 3
- **A tested patch series.** It stacks on 05e with 74/74 after each step, and every single skip was tested (w4-fix-combined-1 ✓). Re-measured in simulation: no crash; step-back 12/14 → 1/14; false focus 15/43 → 3/43; Verify developing in all six Plan A takes; testwise 0.96 → 0.28; How AI works AUC 0.85/0.88 with decay.
- **Pitch red-team edits:** five drifting numbers fixed; "Each moment adds evidence"; "names a wrong idea"; slide 5's logic; slide 8 Edexcel only; a Plan B voiceover.
- **Edexcel's share comes from Ofqual's tables.** The revenue ceiling is about £239k a year at £5 (our estimate; w4-08-10 ✓).
- **Microsoft's switch** is a channel condition in the business plan and 05.
- **357 findings.** Wave 4 added 19 (16 ✓, 3 ~).
