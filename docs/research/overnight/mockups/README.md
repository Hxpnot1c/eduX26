# Mock-ups for the deck and video

Two static HTML pages. They are **pictures of a design, not product code**. Every number on them is invented. Each page has a "Mock-up · illustrative data · not a live feature" tag at the top left, inside any 1280×720 crop. Keep the tag in every shot.

Open the file in a browser at 1280×720 and screen-capture it. The pages use no scripts, fonts or links from outside, and the system font stack. Light and dark follow the OS setting (`prefers-color-scheme`). Text contrast is at least 5.8:1 in both themes (WCAG AA).

## teacher-view.html: one-screen class view

**Follows:** [05 Product features](../05-product-features.md), "Teacher view" (spec and mock; rec 4), and the coordinator decision on per-student data in `work/WRITER.md` (wave 2).

**Shows (class of 18, invented):**
1. **Two misconception flags.** Each meets the alarm rule (our choice): at least 6 students and at least 40% of those offered the option, first attempt, 14-day window, recomputed weekly. One flag has its starter MCQ open; the other's is collapsed so the page fits 720 px. The wrong options are written as misconceptions and kept to similar length and punctuation (the patch 0004 lesson). Below the flags: "Nothing flagged does not mean no problems". Misconceptions below the rule are not listed at all.
2. **Five weakest parts**, as share words (some / about half / most) and count bands (6–9, 10–14, 15+). One row is suppressed: "too few students (5 or fewer)".
3. **Class AI literacy, shown as school opt-in: on.** Ask and Verify appear as bands only. How AI works has no level: one per-part row, and the rest suppressed.
4. **Per-student completion, shown as school opt-in: off.** It has no counts and no names.
5. **Footer** listing what is never shown.

No names, no chats, no per-student levels. It never says "anonymous", "all clear" or "all". Part names are short labels in our own words, matching the Edexcel 9EC0 content areas. There is no exam-board text.

**Status: not built** (05 rec 23, teacher view as code, comes later). The flag rule and the bands are specified but not implemented.

**Caption on screen:** "Mock-up · illustrative class data". **Voice-over (05 rec 4):** "Teachers see what to reteach, never who said what."

**Don't say** that it catches every problem. In a small set it catches misconceptions held by about half the class, not by a third (05, small-class table).

## student-progress.html: what `get_my_progress` shows a student after the fixes

**Follows:**
- [06](../06-settings-simulation.md) rec 10 ("not yet shown");
- [02](../02-ai-literacy-assessment.md) rec 6 and [demo plan](../demo-plan.md) rec 13 / M7 (How AI works as per-part counts plus the wrong ideas still held, no level);
- 05 rec 6 ("what your teacher sees" line, word for word);
- patch 0003 (skip count: a skipped task is missing, not wrong).

**Shows:** part levels (secure / developing / new / not yet shown), three reviews due, one next step, Ask and Verify as levels, How AI works as "checked n, right m" per part with one wrong idea still held, "Skipped: 2 tasks. Skipping never lowers a level", and the exam countdown in weeks. Plain words. No timers, streaks, time on task or fatigue lines.

**What each element rests on:**

| Element | Status |
|---|---|
| Part levels secure / developing / new, reviews due | on `main` |
| Ask and Verify levels; wrong ideas still held | 05e branch (built, not merged) |
| Skip count ("skipping never lowers a level") | patch 0003 in the combined series (tested, not merged) |
| "Not yet shown" label | `fix4b`, **not in the patch series**: recommended, not built |
| How AI works "checked n, right m" | **recommended, not built** (wednesday-build-list) |
| "What your teacher sees" line | **recommended, not built** (05 rec 6, a `text/` edit) |
| Exam countdown in weeks | the exam date already exists (course pack or `exam_date_override`); showing it as weeks is our proposal |
| Next step, in plain words | the chatbot's job, per `text/tools/get_my_progress.md` |

The real tool returns JSON that the chatbot puts into words. This page shows how those words could look.

**Caption on screen:** "Mock-up · illustrative data · what a student could see once the fixes land".

**Rules for using it (from pitch-notes):**
- Don't say "a part only counts as known once you've got it right" as a fact until 06 rec 10 (`fix4b`) is built. Until then, voice-over: "This is the design: nothing counts as known until it's been answered right."
- Never say "How AI works level". Say "per-part results".
- The wrong idea shown is about confidence, not "it searched a database and picked the wrong entry" (WRITER wave-2 rule: with web search on, that is often true).
