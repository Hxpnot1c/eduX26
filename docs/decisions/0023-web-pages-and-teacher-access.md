# 0023. Web pages, bearer-only sign-in and teacher keys

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (teacher access and what teachers may see are product calls)
- **Pull request:** #72 (foundations); the map, student page and teacher page follow in later pull requests
- **Audit item:** C10 (keys in URLs) in [0002](0002-research-alignment-register.md); DfE standard 4 in [dfe-safety-mapping](../build/reference/dfe-safety-mapping.md)

## Context
Synapse has no web interface: a student reads their record only through a chatbot, and a teacher only through the CLI. `later.md` reserved a student page and a teacher view. Three things had to be settled before building them: how a browser signs in without putting a key in a URL (register C10), who a teacher is (only student keys existed), and what the pages may show.

## Decision
- **Pages beside `/mcp`, served by the same process.** `/mcp` is untouched and still behind the student key. The pages and `/static` carry no data and are public. All data is under `/api`.
- **Bearer-only sign-in.** The key arrives in the URL **fragment** (`/me#key=…`), which a browser never sends to a server. The page moves it into `sessionStorage` (gone when the tab closes), removes it from the address bar, and sends it as `Authorization: Bearer`. An `/api` request with `?key=` is refused with a 400 even if the key is right. "Forget this device" clears it.
- **Teacher keys.** A `teacher` table (migration 020) and `teacher_class` table, keys stored only as SHA-256 like students'. CLI: `teacher add | assign | list | leave | delete`; `purge` removes teachers who left. A teacher key opens the teacher API only and never `/mcp`; a student key never opens the teacher API. A teacher sees only classes assigned to them.
- **No other origin, ever.** Strict content security policy (`default-src 'none'`, scripts, styles, fonts and connections only from `'self'`), `Referrer-Policy: no-referrer`, `no-store` on the API. Fonts are self-hosted (OFL). A test fails if any page refers to another origin or has inline script or style.
- **Public example map is a setting** (`web.public_example_map`, a judgement call, on) for the synthetic example pack only.

## Research basis
- RFC 9110 §17.9, RFC 9700 §4.3.2 and the MCP authorization specification (2025-06-18): tokens must not travel in a URL query string (the reason for the fragment). A fragment is not an access-control mechanism, only a way to keep the key out of server logs, referrers and request URLs; browser history and screenshots can still hold it.
- ICO Children's Code (standard 11, transparency) and the DfE product safety standards (privacy, standard 6): no third-party requests from pages used by children; a font or script CDN would send each pupil's address to a third party.
- `personalisation.md` §5 and Kaliisa et al. (2023, 38 studies): what the dashboards may show, and that no claim of improved outcomes is made. See 0024.

## Alternatives considered
- **Key in the query string** (`/me?key=`, as `later.md` first sketched): simplest, but it lands in tunnel and server logs, history and referrers. Rejected for the reason in C10.
- **A cookie set by a sign-in page:** needs a sign-in form and CSRF protection; no better against a shared computer. Held with OAuth.
- **A shared school passphrase for teachers:** no per-teacher scoping or audit trail.
- **A build step (React, Svelte):** adds Node, a build and a bundle for three small pages. Rejected for plain HTML, CSS and JavaScript.

## Consequences
- The MCP endpoint, tools and server instructions are unchanged (898 of 900 words; no result over 2,400 characters).
- A key in a fragment can still be left in browser history or a screenshot on a shared computer. Mitigations: session-only storage, the fragment removed at once, "forget this device". OAuth remains the held proper fix (C10).
- Teachers are new personal data (a name and a hash). DPIA notes updated; a teacher who left is purged after the same retention as a student.
- **Open:** what each page may show (0024); teacher write actions (a later pull request).

## Verification
`tests/test_web_foundations.py` (24 tests): routing next to `/mcp`, headers, bearer-only sign-in, a URL key refused, a teacher key refused on `/mcp`, whoami returns nothing about a student, scoping, hashing, leave and purge, the CLI, and static checks (no other origin, no inline code, assets exist, licences travel with fonts, contrast). `check_mcp.py` unchanged and passing; pages checked in a real browser at three widths in light and dark.

## What would change our mind
A pilot school that needs single sign-on (move to OAuth sooner), or evidence that fragments are being leaked in practice (move to short-lived tokens exchanged at sign-in).
