# demo-05e: Plan A rehearsal against the 05e branch (wave 3, w3-07)

This folder rehearses the Plan A AI-literacy episode (demo-plan.md, shots 4a–4d) end to end against the code of
`build/05e-literacy-coaching`, with no chatbot. The script plays the chatbot's side: it sends the labels a chatbot
with web search off would send, through the branch's own MCP server on 127.0.0.1, with the MCP Python client.
The notes and the "as captured" shot list are in `../../work/w3/w3-07.md`.

**These are not claude.ai captures.** They show what the server tells the chatbot to do and what it records. What
Claude actually writes, and which labels it really sends, still needs the Wednesday dry run.

## Copies (never the repo or the export)
`make_copies.sh` rebuilds all three. The read-only export `/tmp/claude-1000/edux-05e` was copied to three folders under `/tmp/claude-1000/w3-07/`:

| label | what | settings |
|---|---|---|
| `branch` | the export as it is | branch `settings.toml` |
| `w2` | the export + the wave-2 settings (02 rec 2) | `literacy.ask_min_features = 3`, `ail_question` guess 0.30, `ail_unprompted` guess 0.20 |
| `rewrite` | `w2` + a **placeholder** rewrite of the fabrication option set in `ingest/ai_literacy/` (no m2; written for this test after 02's content table; **not proposed wording**) | as `w2` |

Each scenario gets a fresh `EDUX_DATA_DIR` under `/tmp/claude-1000/w3-07/data/`. It runs `edux.cli load coursepacks/example-mini`
(the branch reads `ingest/ai_literacy/` in with every pack), then `seed-demo --reset`, then `edux.cli serve`. The student is `demo-weak`.

## Files
- `scenarios.py`: the turns (message, labels, answer) for each scenario. `pick` names the option id; the driver reads its letter from the stored letter map, as the driver on camera would read it off the screen.
- `run_episode.py`: the driver. For each turn it records:
  - the arguments sent and the full result;
  - what the chatbot is told (cue plus data, per step);
  - the server console line (ms, chars, OVER BUDGET) and the wall time;
  - the AI-literacy p_now and levels, before and after;
  - the evidence written, held misconceptions, and the pending literacy task or how-AI-works check.
- `probe_resolve.py`: which words in a line pull a course part into focus (example-mini). Output: `captures/probe_resolve.txt`.
- `digest.py`: writes `captures/DIGEST.md`. It lists every turn of every scenario per copy, a branch-vs-w2 diff of what a viewer could see, and timing and size totals.
- `run_check_mcp.sh`: runs a copy's own `scripts/check_mcp.py` against its own server. Output: `captures/check_mcp_{branch,w2}.txt`.
- `captures/<label>__<scenario>.json`: the raw captures.

## Re-run
```bash
cd docs/research/overnight/sims/demo-05e
./make_copies.sh
PY=/home/vishnu/edux26/.venv/bin/python
for L in branch w2 rewrite; do $PY run_episode.py --code /tmp/claude-1000/w3-07/$L --label $L --out captures; done
$PY digest.py
```
A full run of every scenario on one copy takes about 3 minutes, mostly the 1.1 s gap between turns (events are stamped to the second).

## Scenarios
| scenario | what it tests |
|---|---|
| `as_written` | demo-plan wave-1 lines and the check script's labels on the dead-link turn (`research`, `[context]`) |
| `plan_now` | demo-plan's current (wave-2) lines: 4c "That ONS page doesn't give that figure.", pick m1 |
| `clean`, `clean_m1`, `clean_right_pick`, `clean_candidates` | focus-safe wording, with the dead-page turn labelled `other` |
| `final`, `final_ticks_ad` | the shot list proposed in w3-07.md, with the 4c Verify answer ticked a,c,d or only a,d |
| `recommended`, `recommended_right`, `recommended_no_verify_answer` | an earlier version of it (4c "That page doesn't say that.") |
| `t1_concept`, `t1p_concept` | 4a labelled `concept` instead of `research` |
| `recent_t1`, `recent_t2` | the chatbot labels 4a or 4b `asks_recent` (search off) |
| `one_feature_rewrite`, `three_feature_rewrite` | 4b with 2 or 3 question features |
| `conflict_*`, `no_source_conflict_label`, `clean_conflict_research` | other ways the chatbot might label the 4c turn |
| `petrol`, `search_on`, `skip_4b`, `after_m2_ok`, `retake_same_session`, `then_ped`, `as_written_then_ped` | other topics, search on, cutting a shot, ignoring the re-ask, retakes, expo order |

Not tested: m3 (its "on purpose" wording is an absolute give-away cue).
