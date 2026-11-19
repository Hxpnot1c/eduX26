# The web layer

Pages and a small JSON API, served by the same process as the MCP endpoint. See decisions 0023 and 0024 and step [09](../steps/09-web.md).

## Routes
| Path | Who | What |
|---|---|---|
| `/mcp` | a student key in `?key=` (as before) | the MCP endpoint; unchanged |
| `/`, `/map`, `/me`, `/teacher` | anyone | static pages with no data; they fetch data from `/api` |
| `/static/*` | anyone | CSS, JavaScript, fonts |
| `/api/whoami` | a student or teacher key, as `Authorization: Bearer` | `{"role": "student"}`, or for a teacher `{"role": "teacher", "name", "classes": [{id, name}]}` |

An `/api` request with `?key=` is refused with 400. A teacher key never opens `/mcp`; a student key never opens the teacher API. Later pull requests add `/api/map`, `/api/public/map`, `/api/me/*` and `/api/teacher/*`.

## Headers (every response from this layer)
`Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive `Permissions-Policy`; `Cache-Control: no-store` on `/api`.

## Sign-in
Open `/me#key=<key>` or `/teacher#key=<key>`. The fragment is never sent to a server. `js/api.js` moves the key into `sessionStorage`, removes the fragment from the address bar and sends `Authorization: Bearer` on every call. "Forget this device" clears it.

## Teachers
`python -m edux.cli teacher add --name "…"` prints the key once; `teacher assign --teacher t-… --class c-…` lets them see a class; `teacher list | leave | delete --yes`. Keys are stored as SHA-256 only; `purge` deletes teachers who left after `retention.after_leaving_days`.

## Design tokens
`edux/web/static/css/tokens.css`. `python scripts/check_contrast.py` checks every pair against WCAG 2.2 and the level fills' luminance order. Fonts are self-hosted OFL subsets in `static/fonts/` with their licences.
