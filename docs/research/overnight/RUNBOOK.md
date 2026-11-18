# Wednesday runbook (one page)

Follow this top to bottom. Details, residuals and cut-line workarounds are in [wednesday-build-list.md](wednesday-build-list.md); the words to record are in [pitch-script.md](pitch-script.md). Owners: **B1** build lead, **B2** second builder, **E** economist, **P** pitch lead.

## 0. Prerequisites and variables (B1, 09:00)
Python 3.11+, git, curl, `cloudflared` (or ngrok) for the tunnel. From the root of a clone of `git@github.com:Hxpnot1c/eduX26.git`:

```bash
python3 -m venv .venv && .venv/bin/pip install -e .     # once per laptop
ROOT=$PWD                     # the repo root
PY=$ROOT/.venv/bin/python     # use $PY everywhere, never bare python
SCRATCH=/tmp/claude-1000      # the research scripts refuse any other folder (a safety guard in them)
W=$SCRATCH/wed
FIX=$W/research/docs/research/overnight/sims/fixes
C=$FIX/combined
```

## 1. Fast-forward and branch (B1, 09:00–09:30)
Never commit to `main` directly (docs/build/README.md). `main` fast-forwards to the 05e branch; the fixes go on a new branch.
```bash
git fetch origin
git switch main && git merge --ff-only origin/build/05e-literacy-coaching   # 14 commits, no merge commit
git switch -c build/wednesday-fixes
$PY -m pip install -q -e .
rm -rf "$W" && mkdir -p "$W/research"
git archive origin/research/overnight docs/research/overnight/sims | tar -x -C "$W/research"
ls "$C"/*.diff | wc -l       # expect 16 (includes superseded files; use only the ten below)
```
`git archive` copies the patches (tracked on `research/overnight`) **outside** the build tree, so nothing from the research branch gets committed. Don't use `git checkout origin/research/overnight -- …`: it stages those files.

**The check after every patch (about 1 min).** Paste this function once:
```bash
check() {  # check <name>
  local D=$W/check-$1; rm -rf "$D"; mkdir -p "$D"
  ( cd "$ROOT" && export EDUX_DATA_DIR="$D"
    "$PY" -m edux.cli load coursepacks/example-mini >"$D/load.txt" 2>&1
    "$PY" -m edux.cli seed-demo --reset >/dev/null
    "$PY" -m edux.cli serve --host 127.0.0.1 --port 8765 >"$D/server.log" 2>&1 & S=$!
    for i in $(seq 50); do curl -s -o /dev/null http://127.0.0.1:8765/ && break; sleep 0.2; done
    "$PY" scripts/check_mcp.py --url http://127.0.0.1:8765/mcp >"$D/check.txt" 2>&1; echo "exit $?" >>"$D/check.txt"
    kill $S )
  echo "ok lines: $(grep -c '^ok' "$D/check.txt")"; grep -o 'largest [0-9]*, [0-9]* over budget' "$D/check.txt"; tail -2 "$D/check.txt"
}
check base     # expect: ok lines: 74 / largest ~2298, 0 over budget / all checks passed / exit 0
```
It uses a fresh data folder under `$W`, never `data/`. If the only failure is the timing check or "MCQ options are shuffled differently", rerun once (chance or load).

## 2. The patches, in this order
**Apply command, the same for every patch:** `git apply --check "$C/<file>" && git apply "$C/<file>"`. We use `git apply` because it worked for all ten on a fresh clone, works the same on Linux and macOS (BSD `patch` has no `--no-backup-if-mismatch`), leaves no `.orig` file, and `--check` changes nothing if it fails. If `--check` fails, stop: drop that patch and everything after it ([cut line](wednesday-build-list.md#cut-line-if-behind-at-the-1630-freeze-1800-gate)).
**After each:** `check <n>`, then `git add -A && git commit -m "fix: apply <n> <short name>"`. Don't push until the 16:30 freeze passes.

| # | file (in `$C/`) | owner · slot | expected after `check` |
|---|---|---|---|
| 0001 | `0001-core-fixes-clamp-p_known-one-step-back-per-stuck-par.diff` | B1 · 09:30–10:00 | 74 ok, all checks passed |
| 0002 | `0002-focus-a-research-or-other-message-never-sets-or-chan.diff` | B1 · 10:00–10:30. **Default: apply.** Skip only if `check` fails; then use `variants/0003-alt-…` for 0003. Decided by 10:30 | 74 ok |
| 0003 | `0003-verify-scoring-a-found-dead-or-mismatched-source-sco.diff` (adds `migrations/010_literacy_skip.sql`) | B1 · 10:30–11:30 | 74 ok |
| 0004 | `0004-mcq-give-away-key-is-a-mark-point-in-option-form-ope.diff` | B1 · 11:30–13:00; E reads rows 09:30–11:30 | "trailing whitespace" warnings (CRLF CSVs: fine); 74 ok; also `$PY -m ingest.cli validate coursepacks/example-mini` |
| 0006 | `0006-w5-stuck-ladder-and-review-requests.diff` | B1 · 13:30–14:30 | 74 ok |
| 0007 | `0007-w5-labels-text.diff` | B1 · 14:30–14:50 | 74 ok |
| 0008 | `0008-w5-ask-guard.diff` | B1 · 14:50–15:15 | 74 ok |
| 0011 | `0011-w6-mcq-length-rank.diff` | B1 · 15:15–15:30; then B1 pastes E's p2/m2 rewording (separate commit, rerun `check`) | 74 ok; load prints no length warnings |
| 0009b | `0009b-w6-dead-link-report-cap.diff` | B1 · 15:30–16:00 | 74 ok |
| 0010b | `0010b-w6-show-then-pick-cap.diff` | B1 · **only if 0009b has passed `check` by 15:00** (the day an hour ahead); otherwise drop it | 74 ok |
| 0005 | `0005-decay-towards-the-starting-estimate-Ask-and-Verify-t.diff` | optional, not scheduled; if used, apply right after 0004 (tested) | 74 ok |

Never apply `0006-stuck…`, `0006b`, `0006c`, `0009-w5` or `0010-w5`: superseded.

**Optional deeper tests (B2, Linux/WSL only; untested here on macOS, where `/tmp` resolves to `/private/tmp` and the scripts' guard refuses it):** testwise after 0004 and 0011:
```bash
D=$W/tw; rm -rf "$D"; mkdir -p "$D"; EDUX_DATA_DIR=$D $PY -m edux.cli load coursepacks/example-mini >/dev/null
EDUX_DATA_DIR=$D PYTHONPATH=$ROOT $PY $FIX/testwise.py --json $W/tw.json   # expect about 0.28 overall; after 0011 economics middle about 0.29
```
Probes and the Plan A rehearsal: see the build list (they need copies under `$SCRATCH/w3-07/`).

**E (09:30 on):** read `$FIX/mcq-pack-proposal/*.csv` (0004 rows) and the 0011 section of `$C/README.md` (the 22 rows 0011 rewords). 13:30–14:00 write the `tax_incidence_split_p2`/`_m2` rewording in a note; **never edit the CSVs**. B1 applies it after 0011. Keep every option within ±20% of the key's length.

## 3. Freeze (B1, B2, 16:00–16:30)
`check final` → 74 ok, 0 over budget. **The largest result is at the limit: 2,395 of 2,400 characters in the verifier's run, and 2,399 after 0004 in our clone test (2,382 on the final stack).** If `check` shows over budget: trim one reference block, rerun. Then re-capture shot 5 (`ped_definition` options change with 0011). Push: `git push -u origin build/wednesday-fixes`, open a PR. Nothing merges after 16:30.

## 4. Server, tunnel, connector (B2, 15:30–16:15, in parallel with B1)
From the 05e README (the local part tested; tunnel and connector **untested here**):
```bash
cp .env.example .env
scripts/demo.sh                                  # loads example-mini, seeds demo students, prints keys, serves :8000
cloudflared tunnel --url http://localhost:8000   # second terminal; prints https://<host>.trycloudflare.com
```
Add `<host>` (no `https://`) to `ALLOWED_HOSTS` in `.env`, restart `scripts/demo.sh` (keys stay). In claude.ai (adult account, web search off): Customize → Connectors → Add custom connector, URL `https://<host>/mcp?key=<demo-weak key>`. Paste `text/chatbot_setup.md` into the instructions. 421 = host not in `ALLOWED_HOSTS`; 401 = key missing.

## 5. Dry run and gate (all, 16:30–18:00)
P drives the line card (pitch-script §1), B1 expands every tool call: 4a/4b `research`, 4c `source_conflict: true`, `request_type: other`. Watch the server console for over-budget results. Any miss: reset, new chat, try again. **18:00 gate:** Plan A if one take, after any number of resets, runs 4a–4d with the right labels and no mid-episode retake, and `check final` passed. Otherwise Plan B (pitch-script §1b).

## 6. After the gate
| what | who | when |
|---|---|---|
| Film Plan A or B (reset + new chat every take), then the two fallback clips | P, E drive; B1 console; B2 fallbacks | Wed 18:00–21:00 |
| Deck (4 minutes; pitch-script §2) | P | Wed 09:00–16:00, final pass Thu |
| Video edit: captions, highlight boxes, caption track | P, B2 | Thu 09:00–17:00 |
| Leave-behind and QR code | E | Thu 13:00–17:00 |
| Submit video + deck | P | Thu, before 23:59 |
| Label-agreement study | all | after submission |

## What was tested (18 Nov, fresh clone, Linux, Python 3.14)
On a fresh clone of a local copy of the GitHub branches: the venv install, §1 (fast-forward: 14 commits; branch; `git archive`: 16 diffs), `check base` (74/74), and **all ten patches, 0001 to 0010b in the order above, applied with `git apply`, then `check` and a commit after each: 74/74 every time, 0 over budget, 10 commits on `build/wednesday-fixes`, clean tree after.** Largest result: 2,298 base; 2,313 / 2,313 / 2,335 / **2,399** / 2,399 / 2,399 / 2,399 after 0001–0008; 2,382 after 0011, 0009b and 0010b. 0004 prints CRLF "trailing whitespace" warnings and still applies. Untested: 0005 in this clone, the testwise command, `scripts/demo.sh`, the tunnel and the claude.ai connector, and anything on macOS.
