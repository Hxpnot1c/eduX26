# Step 09: the web pages (course map, student page, teacher page)

Decisions [0023](../../decisions/0023-web-pages-and-teacher-access.md) (access) and [0024](../../decisions/0024-visual-language-and-what-the-pages-will-not-show.md) (look, and what the pages will not show). Built as a stack of pull requests; this file is updated by each.

## Status
| # | Pull request | What | State |
|---|---|---|---|
| 1 | Foundations (`build/web-foundations`) | `edux/web` layer, routing next to `/mcp`, bearer-only sign-in, security headers, teacher keys and CLI, design tokens, fonts, level key, page shells | **built** |
| 2 | Course map | `/api/map`, the map and path views, text alternative, public example map | planned |
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
