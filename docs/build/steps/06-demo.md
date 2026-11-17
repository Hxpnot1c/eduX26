# Step 06: Demo

**Branch:** `build/06-demo`

## Goal
Anyone on the team can run the demo from the README in under ten minutes, from claude.ai and ChatGPT, against the loaded course pack (example-mini until the real pack exists).

## Work
- `python -m edux.cli seed-demo`: creates three demo students with different histories, built by replaying scripted events rather than writing state directly.
  - One mostly secure, with reviews due.
  - One with weak prerequisites and an active misconception.
  - One who uses "just show me" often.
  - Parts are chosen by role from the loaded pack, not fixed ids (see below), so the same command works on any pack.
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

## Demo students
`seed-demo [--course] [--reset] [--parts role=id,...]` creates `demo-secure`, `demo-weak` and `demo-showme`. Every event goes through `record_exchange` / `record_evidence` with timestamps counted back from now. Each student's `exam_date_override` is about 150 days ahead, so spacing and review modes work whatever dates the pack has. `--reset` removes the three students and their events first, and recreates them with the same keys so connector URLs keep working.

### Picking parts by role
Picks are deterministic: ties go to importance, then pack order.

| role | rule |
|---|---|
| `target` | a part with a prerequisite part and at least `prequestion.min_distractors` misconceptions (`mcq.min_distractors` from step 05d), most important first |
| `prereq` | the target's prerequisite part with the highest link weight |
| `misconception` | the target's misconception from an examiner report, otherwise its first |
| `anchor` | a part analogous to the target: highest link weight, then the same part type |
| `confusable` | a part confusable with the target, highest link weight |
| `review_parts` | the 3 most important parts that aren't the target, a part depending on it, the prereq or the anchor |
| `showme_parts` | the 2 most important parts that aren't the target |

**Fallbacks**, each with a printed warning naming the feature that won't show:
- No part has enough misconceptions: the target needs only one (no pre-question).
- No part has a prerequisite: the target is the most important part, and `demo-weak` skips the weak prerequisite.
- No analogous or confusable part: that role is skipped.
- Too few parts for a role: use what there is. Seeding fails only if the pack has no parts.

`--parts target=ped_values,prereq=ped_formula` overrides single roles. Ids are checked and resolve through `id_map`. The chosen roles are printed.

### The three students
The target has no events for `demo-secure` or `demo-showme`, and neither do the parts that depend on it (their evidence would pass a prerequisite boost to the target). Events are recorded in time order, so `rebuild` gives the same state. The same question about the target shows:
- **demo-secure:** pre-question, anchor and reviews due. Most parts are secure, including the prerequisite and anchor; one review part is weak (`recall`), the others developing (`transfer`).
- **demo-weak:** weak prerequisite, the misconception to correct and worked-example support. No pre-question, because the target has evidence.
- **demo-showme:** its offloading history ("just show me" reviews, a rising just-show-me trend), and a pre-question only if there's no "just show me" in the current session. Three past sessions (9, 6 and 3 days ago, about 50 minutes each) start well and then drop on previously correct parts from about minute 35, so `get_my_progress` shows the study pattern. They're past sessions, so there's no fatigue block now.

`docs/demo-script.md` uses Edexcel 9EC0-style questions written by us and refers to real papers only by reference: no exam-board text in the script, README or video.

## Commits
1. `docs: pick demo parts by role from the loaded pack`
2. `feat(cli): seed demo students from scripted events`
3. `chore(scripts): add demo runner`
4. `docs: write README with set-up and connector instructions`
5. `docs: add demo script`

## Done when
- A fresh clone, following the README, gets a working connector in claude.ai.
- The three demo students get visibly different context for the same question about the target, as listed above.
