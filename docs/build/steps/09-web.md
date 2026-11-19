# Step 09: the web pages (course map, student page, teacher page)

Decisions [0023](../../decisions/0023-web-pages-and-teacher-access.md) (access) and [0024](../../decisions/0024-visual-language-and-what-the-pages-will-not-show.md) (look, and what the pages will not show). Built as a stack of pull requests; this file is updated by each.

## Status
| # | Pull request | What | State |
|---|---|---|---|
| 1 | Foundations (`build/web-foundations`) | `edux/web` layer, routing next to `/mcp`, bearer-only sign-in, security headers, teacher keys and CLI, design tokens, fonts, level key, page shells | **built** |
| 2 | Course map (`build/web-course-map`) | `/api/map` and `/api/public/map`, the map, path and list views, detail panel, keyboard movement, public example map | **built** |
| 3 | Student page | `/me`: map, what next, reviews, coming up, AI-literacy practice, my record, chatbot set-up | planned |
| 4 | Teacher page (read-only) | `/teacher`: class map (≥5 per cell), coverage, misconceptions, assessments, help-seeking pattern | planned |
| 5 | Teacher actions | assessment and coverage forms, content review writing the teacher feedback CSV | planned |
| 6 | Polish | accessibility pass, print, responsive, demo script | planned |

## What pull request 1 added
- **`edux/web/app.py`:** `WebLayer` sends the pages, `/static` and `/api` to a small Starlette app and everything else (`/mcp`, the lifespan) to the existing MCP app behind `RequireKey`, unchanged. `/api/whoami` returns the role (and, for a teacher, their name and classes; nothing about a student). Security headers on every response; `no-store` on `/api`. A key in an `/api` URL is refused with a 400.
- **`edux/teachers.py`, migration 020, `teacher` CLI** (`add`, `assign`, `list`, `leave`, `delete`; `purge` includes teachers who left): hashed keys, class scoping.
- **`edux/web/static/`:** `css/tokens.css` (the palette and type scale, light and dark), `css/base.css`, `js/api.js` (fragment key to `sessionStorage`, bearer header), `js/shell.js` (the level key and the sign-in line), four page shells, six font files (Atkinson Hyperlegible Next, Newsreader; OFL licences alongside).
- **`scripts/check_contrast.py`:** WCAG contrast for every token pair in both schemes, and the level fills' luminance order.
- **`[web]` settings:** `public_example_map`.

## What pull request 2 added
- **`edux/web/views.py` `course_map`:** topics, concepts and parts as a flat list (each with its parent, a 0 to 1 importance for disc size, and counts of mark points and common wrong ideas, never their text) plus the four link types. AI-literacy parts and rejected or hidden rows are left out. No student data.
- **Routes:** `GET /api/public/map` (no key; only the synthetic `example-mini` pack, only if `web.public_example_map`) and `GET /api/map` (any student or teacher key; a student gets their own course, a teacher may name one with `?course=`).
- **`js/graph.js`:** three views of the same data. **Map**: topics hold concepts hold parts, a disc per part sized by importance; a concept with more than 12 parts collapses to one disc whose ring shows how its parts are spread. **Path**: the prerequisite chain left to right, linked parts only, the rest in a quiet row beneath. **List**: a table with the same information, the accessible alternative. Links stay hidden until a part is focused (hover, focus or select), then they are drawn rim to rim by line style: solid with a dot for prerequisite, dashed for analogous, dotted with ≠ for confusable, double for causal. A detail panel (beside the map on wide screens) names what a part needs first and what it is related to. Arrow keys move between parts, Enter selects, Escape clears. All text from the API is set with `textContent`; a test forbids `innerHTML` in any script.
- **Deep links:** `/map?view=path|list` and `/map?select=<id>`.
- **Tests:** `test_web_map.py` (view, routes, setting) and `test_web_browser.py` (a real Chromium against a live server: a disc per part, the three views, selection, sign-in; skipped when no browser is installed).

## Try it
```bash
python -m edux.cli load coursepacks/example-mini && python -m edux.cli seed-demo --reset
python -m edux.cli teacher add --name "Ms Demo"        # prints the key once
python -m edux.cli serve                               # then open http://127.0.0.1:8000/
# student: /me#key=<a demo student's key from demo-keys.json>    teacher: /teacher#key=<teacher key>
```

## Done when (pull request 1)
Pages and static files load with the headers; `/mcp` behaves as before; a student key signs in on `/me` and is refused on `/teacher`; a key in a URL is refused; no page refers to another origin or has inline code; the contrast check passes; `pytest`, `ruff`, `mypy`, `check_mcp.py` pass.

## Open
- `docs/build/reference/dpia-notes.md` is on the #56 branch, not in this stack: when #56 merges, add the `teacher` and `teacher_class` tables and a line saying what the pages display.
- Fonts: Atkinson Hyperlegible Next and Newsreader are a design call for Vishnu (0024).
