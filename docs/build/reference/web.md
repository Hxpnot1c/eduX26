# The web layer

Pages and a small JSON API, served by the same process as the MCP endpoint. See decisions 0023, 0024 and 0026 and step [09](../steps/09-web.md).

## Routes
| Path | Who | What |
|---|---|---|
| `/mcp` | a student key in `?key=` (as before) | the MCP endpoint; unchanged |
| `/`, `/map`, `/me`, `/teacher` | anyone | static pages with no data; they fetch data from `/api` |
| `/static/*` | anyone | CSS, JavaScript, fonts, and the logo and icons in `static/brand/` |
| `/favicon.ico` | anyone | the same file as `/static/brand/favicon.ico` |
| `/api/public/map` | anyone | the structure of the synthetic example pack (`views.EXAMPLE_COURSE_ID`), only if `web.public_example_map`; 404 for any other pack |
| `/api/map` | a student or teacher key (bearer) | the course structure: `{course, nodes, edges}`; a student gets their own course, a teacher may add `?course=` |
| `/api/me` | a student key (bearer); a teacher key gets 403 | the student's own page: `overlay`, `network` (the concept network, decision 0029: `course`, `nodes` {id, short, name, band, concept, level, note, test, q, d, imp}, `edges` {a, b, t, n}, `bands`; levels only), `next`, `reviews`, `coming_up`, `ai_literacy`, `calibration`, `record`, `parts`, `setup` |
| `/api/teacher/class/<id>` | a teacher key for a class assigned to them (else 404; a student key gets 403) | class level only: `class`, `min_cell`, `coverage`, `assessments`, `seeded`, `enough`, `overlay` (a band per part, or withheld), `wrong_ideas` (held by at least the minimum), `help_seeking` (or null) |
| `POST /api/teacher/class/<id>/assessments`, `…/assessments/remove`, `…/coverage` | a teacher key for that class | set or remove a test, mark sections as taught; JSON body (16 KB at most); 400 with a plain reason if refused; reply is the refreshed class view |
| `POST /api/link` | anyone with a map link token, as JSON `{"token"}` | swaps a link from `get_my_progress`, once, for `{"session", "expires_in"}` (seconds); 401 if the token is unknown, used or expired |
| `/api/whoami` | a student or teacher key, as `Authorization: Bearer` | `{"role": "student"}`, or for a teacher `{"role": "teacher", "name", "classes": [{id, name}]}` |

An `/api` request with `?key=` is refused with 400. A teacher key never opens `/mcp`; a student key never opens the teacher API. A session token from a map link opens what a student key opens on `/api` (all read-only) and never `/mcp` or the teacher API.

## Headers (every response from this layer)
`Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive `Permissions-Policy`; `Cache-Control: no-store` on `/api`.

## Sign-in
Open `/me#key=<key>` or `/teacher#key=<key>`. The fragment is never sent to a server. `js/api.js` moves the key into `sessionStorage`, removes the fragment from the address bar and sends `Authorization: Bearer` on every call. "Forget this device" clears it.

## Map links from the chatbot (decision 0026)
With `web.public_base_url` set (or `EDUX_PUBLIC_BASE_URL`, which overrides it when not empty; neither set means no links), `get_my_progress` returns `map_url` = `{base}/me#link=<token>` and `map_url_expires_minutes`. The token is 32 random bytes; the `web_link` table (migration 022) stores only its SHA-256, the student id and an expiry of `web.link_minutes` (15). Every call issues a new one; expired rows are deleted when the next is issued, and `delete_student` removes a student's rows.

`js/api.js` removes `#link=` from the address bar before anything else, then POSTs the token to `/api/link`. The swap marks it used in the same statement that checks it, so it works once, and returns a session token (also stored as a hash only) valid for `web.session_minutes` (120). The page keeps the session in `sessionStorage` and sends it as its bearer, like a key; closing the tab or "Forget this device" ends it sooner. If the swap is refused (the link was used, perhaps by a chat app's preview, or has expired), the sign-in line says: "This link has already been used or has expired. Ask Synapse for your progress again to get a new one." The student's key never appears in a tool result or the chat.

## Teachers
`python -m edux.cli teacher add --name "…"` prints the key once; `teacher assign --teacher t-… --class c-…` lets them see a class; `teacher list | leave | delete --yes`. Keys are stored as SHA-256 only; `purge` deletes teachers who left after `retention.after_leaving_days`.

## Brand
`edux/web/static/brand/` holds the Synapse logo (`synapse-logo.png`, transparent), square icons (`synapse-icon-{16,32,180,192,512}.png`), `favicon.ico` and `site.webmanifest`. Every page links the favicon, the 16 and 32 px icons, the 180 px apple-touch-icon and the manifest (192 and 512 px), and shows the logo 30 px tall at the top left of the header, linking to `/`, with `alt="Synapse"`. The PNGs were recompressed losslessly (same pixels); keep the folder under 200 KB. With a public base URL set, the MCP server's `serverInfo` lists the 192 and 512 px icons at `{base}/static/brand/…`; with none, it sends no icons.

## Design tokens
`edux/web/static/css/tokens.css`. `python scripts/check_contrast.py` checks every pair against WCAG 2.2 and the level fills' luminance order. Fonts are self-hosted OFL subsets in `static/fonts/` with their licences.

## The map data (`/api/map`, `/api/public/map`)
`nodes`: `{id, parent, level (topic|concept|part), name, spec_ref}` and for parts also `part_type`, `description`, `importance` (0 to 1, for disc size), `mark_points` and `misconceptions` (counts only). `edges`: `{from, to, type (prerequisite|analogous|confusable|causal), note, weight}`. Structure only: no student data, and no mark point or misconception text.

## The class view's privacy rules (`views.class_summary`)
Minimum cell `coverage.class_min_students` (5). A class under the minimum: coverage and assessments only. A part: withheld if fewer than the minimum students have answered; otherwise a band (`few`, `mixed`, `most` by the share at developing or secure, edges at one third and two thirds), never a count at each level. Wrong ideas: only those held now by at least the minimum. Help-seeking: only if at least the minimum students wrote in each window. No student identifier, name or key; no confidence, fatigue, learning-speed or rapid-guess data.

## Changes a teacher makes, and the audit trail
`edux/web/actions.py` holds the three operations. Every change writes one `teacher_action` row (migration 021): time, teacher id, class, what, detail. A deleted teacher's id becomes "former teacher". `teachers.recent_actions(class_id)` feeds the "Recent changes" list.
