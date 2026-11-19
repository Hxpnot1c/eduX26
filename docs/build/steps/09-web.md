# Step 09: the web pages (course map, student page, teacher page)

Decisions [0023](../../decisions/0023-web-pages-and-teacher-access.md) (access) and [0024](../../decisions/0024-visual-language-and-what-the-pages-will-not-show.md) (look, and what the pages will not show). Built as a stack of pull requests; this file is updated by each.

## Status
| # | Pull request | What | State |
|---|---|---|---|
| 1 | Foundations (`build/web-foundations`) | `edux/web` layer, routing next to `/mcp`, bearer-only sign-in, security headers, teacher keys and CLI, design tokens, fonts, level key, page shells | **built** |
| 2 | Course map (`build/web-course-map`) | `/api/map` and `/api/public/map`, the map, path and list views, detail panel, keyboard movement, public example map | **built** |
| 3 | Student page (`build/web-student-page`) | `/me`: map coloured by level, what next, ready for a check, coming up, AI practice, my record, my chatbot | **built** |
| 4 | Teacher page, read-only (`build/web-teacher-page`) | `/teacher`: class map in bands (≥5 per cell), coverage, wrong ideas held by ≥5, assessments, help-seeking pattern, what the page does not show | **built** |
| 5 | Teacher actions (`build/web-teacher-actions`) | set or remove a test, mark sections as taught, audit trail | **built**; content review (approve, reject, edit rows) is **not built yet** and will be its own pull request |
| 6 | Polish (`build/web-polish`) | h1 and landmarks, 44 px tap targets, print, a 384-part scale test, accessibility checks in the tests, demo script | **built**; content review still to come |

## What pull request 1 added
- **`edux/web/app.py`:** `WebLayer` sends the pages, `/static` and `/api` to a small Starlette app and everything else (`/mcp`, the lifespan) to the existing MCP app behind `RequireKey`, unchanged. `/api/whoami` returns the role (and, for a teacher, their name and classes; nothing about a student). Security headers on every response; `no-store` on `/api`. A key in an `/api` URL is refused with a 400.
- **`edux/teachers.py`, migration 020, `teacher` CLI** (`add`, `assign`, `list`, `leave`, `delete`; `purge` includes teachers who left): hashed keys, class scoping.
- **`edux/web/static/`:** `css/tokens.css` (the palette and type scale, light and dark), `css/base.css`, `js/api.js` (fragment key to `sessionStorage`, bearer header), `js/shell.js` (the level key and the sign-in line), four page shells, six font files (Atkinson Hyperlegible Next, Newsreader; OFL licences alongside).
- **`scripts/check_contrast.py`:** WCAG contrast for every token pair in both schemes, and the level fills' luminance order.
- **`[web]` settings:** `public_example_map`. Later (decision 0026): `public_base_url`, `link_minutes`, `session_minutes` for map links from `get_my_progress`.

## What pull request 2 added
- **`edux/web/views.py` `course_map`:** topics, concepts and parts as a flat list (each with its parent, a 0 to 1 importance for disc size, and counts of mark points and common wrong ideas, never their text) plus the four link types. AI-literacy parts and rejected or hidden rows are left out. No student data.
- **Routes:** `GET /api/public/map` (no key; only the synthetic `example-mini` pack, only if `web.public_example_map`) and `GET /api/map` (any student or teacher key; a student gets their own course, a teacher may name one with `?course=`).
- **`js/graph.js`:** three views of the same data. **Map**: topics hold concepts hold parts, a disc per part sized by importance; a concept with more than 12 parts collapses to one disc whose ring shows how its parts are spread. **Path**: the prerequisite chain left to right, linked parts only, the rest in a quiet row beneath. **List**: a table with the same information, the accessible alternative. Links stay hidden until a part is focused (hover, focus or select), then they are drawn rim to rim by line style: solid with a dot for prerequisite, dashed for analogous, dotted with ≠ for confusable, double for causal. A detail panel (beside the map on wide screens) names what a part needs first and what it is related to. Arrow keys move between parts, Enter selects, Escape clears. All text from the API is set with `textContent`; a test forbids `innerHTML` in any script.
- **Deep links:** `/map?view=path|list` and `/map?select=<id>`.
- **Tests:** `test_web_map.py` (view, routes, setting) and `test_web_browser.py` (a real Chromium against a live server: a disc per part, the three views, selection, sign-in; skipped when no browser is installed).

## What pull request 3 added
- **`GET /api/me`** (a student key; a teacher key gets 403, a key in the URL 400): `views.student_page` returns the student's own record only: a per-part overlay (level, a short note on the evidence it rests on, how faded to draw it), what to practise next, reviews with a plain reason each, tests coming up with the suggested plan, AI-literacy practice, a record summary, and the chatbot set-up text. **No probability, score, rank, streak, percentile or comparison appears** (a test walks the JSON for those keys). `service.progress_parts` is the chatbot's progress data before its size limit; `get_my_progress` is that, trimmed, so the chatbot's result is unchanged.
- **Levels follow decision 0015:** a part with no answers is "taught in class, not yet checked" if the class covered it, else "no answers yet", never developing or secure. A part answered recently is drawn at full strength and fades to half by 60 days (judgement calls: `FADE_FULL_DAYS` 7, `FADE_FLOOR_DAYS` 60), so forgetting shows without a number.
- **`/me`:** the map from PR 2 with the overlay, then hairline lists: *What next* (the existing levers), *Ready for a check* (each review with its reason in plain words, no "overdue"), *Coming up* (tests, and the plan from `plan_study`), *AI practice* (practice feedback with the number of checks and days behind each level), *How sure you were* (only once there are enough rated answers), *My record* (counts, what is kept and how to have it deleted, and a copy button to ask the chatbot to re-check a part), *My chatbot* (the paste-in text, read from `text/chatbot_setup.md` so the two cannot differ).
- Found by looking at the real page: literal `**` in the "what is kept" lines, and an empty section shown because `.row { display: grid }` beat the `hidden` attribute. Both fixed, with tests.

## What pull request 4 added
- **`GET /api/teacher/class/<id>`** (a teacher key; a student key gets 403; a class that is not theirs gets the same 404 as one that does not exist; a URL key 400): `views.class_summary`.
- **Privacy rules kept in one place (decision 0024):** a class under 5 students shows only coverage and assessments, and no student data. A part where fewer than 5 students have answered is **withheld**. A part is shown as a **band** (few at developing yet / about half / most at developing or secure) and never as a count at each level, so a small group cannot be found by subtraction; the bands borrow the three level colours so colour keeps one meaning. A cell resting on fewer than 8 students is drawn lighter and called thin (judgement call `THIN`; the band edges at one third and two thirds are also judgement calls). Wrong ideas are listed only when 5 or more students hold one now. The help-seeking pattern (share of messages asking to be shown the answer, recent against before) is shown only when 5 or more students wrote in each window, with a line saying a rise can mean a hard topic. No student id, name, key, confidence, calibration, fatigue or learning-speed figure appears; a test walks the JSON for them.
- **`/teacher`:** a class picker (only the teacher's own classes), the class map with the shared graph code, coverage ("where we are in the spec" and what is not yet covered), common wrong ideas with the right idea, coming up, asking to be shown, and a plain "what this page does not show" list that also says dashboards have not been shown to improve results.
- **Synthetic class for demos:** `seed-demo --pupils 8` adds "Synthetic pupil N" to the demo class from a seeded generator (the same count always gives the same class); the page says "Seeded data". `seed-demo --reset` removes them.
- Teacher write actions (assessment and coverage forms, content review) are the next pull request.

## What pull request 5 added
- **Three POST routes** under `/api/teacher/class/<id>/`: `assessments` (set a test or assignment), `assessments/remove`, `coverage` (mark sections as taught). Each needs a teacher key for that class (a student key gets 403, another teacher's class and an unknown class both get 404, a URL key 400); the body is JSON, at most 16 KB. They reuse the command line's operations and the student form's validation (`service._check_assessment`, `graph.match_sections`), so the same bad input is refused with the same plain reason, and a refusal changes nothing. The reply is the refreshed class view.
- **Audit trail:** migration 021 `teacher_action` (time, teacher id, class, what, detail). "Recent changes" on the page shows the latest six, with the teacher's name. If a teacher is deleted their rows keep their place but the id becomes "former teacher", so the trail outlives the person without keeping who they were.
- **Forms** with real labels and fieldsets, concept checkboxes taken from the course map, a polite status line, and a Remove button on each test. Marking a section as taught sets `class_coverage.set_by = 'web'` and, as with the command line, students are then shown it as "taught in class, not yet checked" (a test checks this end to end).
- No cookies are used, so there is no ambient credential for a cross-site request to borrow: the bearer header must be sent by the page itself.

## Not built: content review
Listing draft and flagged pack rows and letting a teacher approve, reject or edit them (writing the teacher feedback CSV that `ingest.load.apply_feedback` reads) is a separate pull request. It writes to the content database that live chats read, so it needs its own care: apply only the new row (re-applying the whole CSV would repeat log lines), authorise per course, and show what each change will do before it is made.

## What pull request 6 added
- **Accessibility basics, now tested:** one `h1` per page (visually hidden, so the design is unchanged), headings that do not skip a level, landmarks, a skip link that goes somewhere, a label for every form control, text on every button, no positive `tabindex`, tap targets of at least 44 px, reduced motion, and a print stylesheet that hides forms and controls. `tests/test_web_accessibility.py` keeps these from regressing.
- **Scale, measured:** `tests/test_web_scale.py` generates a 384-part course (8 topics of 5 concepts, the middle concept of each topic holding 20 parts), loads it through the real ingest, serves it and times the real page in Chromium. Every large concept collapses to one disc whose ring shows the spread, 224 discs are drawn, the accessible list has a row per part, and **drawing took 9 ms** (headless desktop Chromium; not a phone). `course_map` builds in well under 3 s.
- Demo script section for the pages; a favicon placeholder so browsers do not request one.

## Not checked (be honest about these)
- **A person using a screen reader or only the keyboard.** The markup checks and the roving keyboard focus are tested, but focus order and what a screen reader says were not tried with real assistive technology.
- **A real phone.** Layout was reviewed at 390 px in a desktop browser.
- **Colour-blindness by a person.** The palette keeps its order in greyscale (checked by `check_contrast.py`) and every level also has a ring and fill state, but it was not tried with colour-blind users.
- **Real students and teachers.** Nothing here has been used by either; the wording, the bands and what is left out are all untested with them.
- **A real course pack.** Only the 9-part example and a generated 384-part pack have been drawn.

## Try it
```bash
python -m edux.cli load coursepacks/example-mini && python -m edux.cli seed-demo --reset --pupils 8
python -m edux.cli teacher add --name "Ms Demo"        # prints the key once
python -m edux.cli teacher assign --teacher <t-id> --class demo-class
python -m edux.cli serve                               # then open http://127.0.0.1:8000/
# student: /me#key=<a demo student's key from demo-keys.json>    teacher: /teacher#key=<teacher key>
```

## Done when (pull request 1)
Pages and static files load with the headers; `/mcp` behaves as before; a student key signs in on `/me` and is refused on `/teacher`; a key in a URL is refused; no page refers to another origin or has inline code; the contrast check passes; `pytest`, `ruff`, `mypy`, `check_mcp.py` pass.

## Open
- `docs/build/reference/dpia-notes.md` is on the #56 branch, not in this stack: when #56 merges, add the `teacher` and `teacher_class` tables and a line saying what the pages display.
- Fonts: Atkinson Hyperlegible Next and Newsreader are a design call for Vishnu (0024).
