# Step 06: Demo

**Branch:** `build/06-demo`

## Goal
Anyone on the team can run the demo from the README in under ten minutes, from claude.ai and ChatGPT, against the real course pack.

## Work
- `python -m edux.cli seed-demo`: creates three demo students with different histories, built by replaying scripted events rather than writing state directly.
  - One mostly secure, with reviews due.
  - One with weak prerequisites and an active misconception.
  - One who uses "just show me" often.
- Root `README.md`:
  - what it is
  - install
  - load a pack
  - add a student
  - serve
  - tunnel (Cloudflare Tunnel or ngrok)
  - add the connector in claude.ai and in ChatGPT developer mode, with the URL format `https://<tunnel-host>/mcp?key=<key>`
  - paste the chatbot set-up text
  - troubleshooting: allowed hosts, connector refresh, free-plan connector limit
- `scripts/demo.sh`: load the pack, seed, serve.
- A short `docs/demo-script.md` for the video: which student and which questions show each feature.

## Commits
1. `feat(cli): seed demo students from scripted events`
2. `chore(scripts): add demo runner`
3. `docs: write README with set-up and connector instructions`
4. `docs: add demo script`

## Done when
- A fresh clone, following the README, gets a working connector in claude.ai.
- The three demo students get visibly different context for the same question.
