# 0026. Map links from the chatbot: single-use tokens, never the key

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu
- **Pull request:** (to add)
- **Research:** none; a security and convenience change. The numbers are judgement calls.

## Context

A student who asks the chatbot about their progress should be able to open their map and progress page. The page signs in from `/me#key=<key>` (decision 0023), but a tool result goes into the chat, and the chatbot provider stores chats. Putting the student's key in a result would leave a long-lived secret that opens their record in someone else's storage.

## Decision

1. **A setting, off unless set.** `web.public_base_url` (default `""`), overridden by `EDUX_PUBLIC_BASE_URL` when that is set and not empty (the repo's `EDUX_*` pattern). Without it, `get_my_progress` returns no link and issues no token.
2. **A single-use link token, not the key.** Each `get_my_progress` call makes 32 random bytes (`secrets.token_urlsafe(32)`) and returns `map_url` = `{base}/me#link=<token>` with `map_url_expires_minutes`. `web_link` (migration 022) stores only the SHA-256 (the scheme used for student and teacher keys), the student id and an expiry of `web.link_minutes` (15). The link is added before `fit_progress`, so it counts towards the 2,400-character limit as sent. If the result is still over (the tree and AI literacy are never cut), the link is left out. There's a new link on every call (no new tool parameter).
3. **Swapped once for a short, read-only session.** The page removes `#link=` from the address bar at once and POSTs the token to `/api/link`. One `UPDATE … WHERE used_at IS NULL AND expires_at > now` both checks it and marks it used, so a second swap fails. The reply is a session token (stored as a hash, `web.session_minutes` = 120) that the page keeps in `sessionStorage` and sends as its bearer. A session counts as its student on `/api`, which is read-only for students. It never opens `/mcp` (that takes the key) or the teacher API.
4. **Link previews.** A chat app that builds a preview by running the page's JavaScript could use the token up before the student clicks. Most preview fetchers never see it: the fragment isn't sent to the server, and they don't run scripts. When it does happen, the page doesn't show an error or a blank page. It says: "This link has already been used or has expired. Ask Synapse for your progress again to get a new one." (tested in a real browser).
5. **What the chatbot is told.** Server instructions rule 12: "Share map_url only if asked about progress or the map." The tool description adds that it works once and soon expires, that a new call gives a new one, not to repeat it unprompted, and that it is not the student's key. The instructions stay within 900 words (899). Room was made by cutting words without changing meaning, as in 0019.

## Consequences

- The student's key never appears in a tool result or the chat. A link that leaks from the chat log is useless after one use or 15 minutes, and a session after 2 hours or when the tab closes.
- `web_link` has a `student_id` column, so `delete_student` and `export_student` cover it. Expired rows are deleted when the next link is issued.
- A link opened in a second browser after the first has used it gets the message, not the page. The student asks again.
- The demo deployment needs `EDUX_PUBLIC_BASE_URL` set to the public address of the pages (the tunnel's https URL).
