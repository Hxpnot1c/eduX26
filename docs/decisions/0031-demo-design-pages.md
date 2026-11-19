# 0031. Serve the two design pages as they are, in demo mode only

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu
- **Pull request:** see the branch `build/demo-design-pages`

## Decision

With demo mode on (`EDUX_DEMO_TEACHER=1`, or `web.demo_teacher`, decision 0030):
- `/teacher` returns `static/demo/synapse-teacher-demo.html`;
- `/me/demo` returns `static/demo/synapse-student-demo.html`.

Both are Vishnu's self-contained design pages: inline CSS, JS and sample data, and the logo as a `data:` image.

- **Byte for byte.** There is no templating and nothing is injected. `.gitattributes` keeps git from converting their line endings, and a test compares the SHA-256 of the response with the file's.
- **No sign-in.** They hold sample data only.
- **Their own policy, for these two routes only.** `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`. Every other route keeps the site's policy, which lets nothing leave the origin (0024).
- **The map link.** `/me` keeps the `#link=` swap as it is. In demo mode `/api/link` adds `"demo": true` to a successful swap, and the page then goes on to `/me/demo`. A failed swap still shows "already used or expired".
- **Not static files.** The files are never served under `/static/demo/` (404), so they can't be reached outside demo mode.
- **Demo mode off.** `/teacher` and `/me` are exactly as before, and `/me/demo` is 404.

## Consequences

- **Sample data, not the record.** In demo mode the teacher and student pages show the design's sample data, not the learner model. The real teacher view (0030) and the student page (0029) are hidden behind these pages until demo mode is off.
- **Two exceptions to 0024.** These two routes run inline code and load Google Fonts. That is acceptable only because they hold no student data and run only in demo mode.

## Verification

`tests/test_web_demo_pages.py`: byte-for-byte bodies and the policy in demo mode; every other route's policy unchanged; with demo mode off, `/teacher` and `/me` unchanged and `/me/demo` 404; never served as static files; the link swap's demo flag; the redirect only after a successful swap.
