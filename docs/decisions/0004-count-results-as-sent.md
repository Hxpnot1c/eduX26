# 0004. Count tool results as they are sent, and keep every default result inside the budget

- **Status:** Accepted
- **Date:** 2026-11-18
- **Pull request:** #47
- **Audit items:** C15, C16 in [0002](0002-research-alignment-register.md)

## Context

The handover's gate says no tool result may be over 2,400 characters. Three things were wrong.

1. **The count was not what is sent.** `service.result_size` counted `json.dumps(result)`. The MCP SDK sends the text part with `indent=2`. Measured through the MCP client on the seeded demo, the levels-only `get_my_progress` for `demo-secure` was 2,355 characters by the old count but **3,571 characters on the wire**. `tutor_turn` showed the same gap (736 counted, 1,012 sent).
2. **Only `tutor_turn` was checked.** `over_budget` ignored `get_my_progress`, which also has an unbounded part: after the check script's own activity, the levels-only result reached 2,425 characters, and nothing flagged it.
3. **The check used the median.** `scripts/check_mcp.py` asserted that the median `tutor_turn` result was within budget, which allows individual results over the limit.

Separately, the `finally` block in `timed()` called `service.log_call` without protection. If the `call_log` insert failed (a locked database, for example) the exception replaced the tool's result and the student's turn failed. Stored error text could also echo the student's input.

## Decision

- Send every tool result as **compact JSON text** (no spaces or newlines, non-ASCII characters unescaped) and count its size from that same text (`service.compact_json`, `service.result_size`). Counted equals sent.
- Add `service.fit_progress`: when the levels-only `get_my_progress` is over `results.max_chars`, drop the last, lowest-ranked item of `weak_links`, then `reviews_due`, then `levers`, until it fits. The tree, trends, AI-literacy block and study pattern are never cut. The every-part view (`include_parts`) is trimmed the same way, to its own larger limit.
- Extend `over_budget` to every tool.
- Give the every-part view (`get_my_progress` with `include_parts`) its own limit, `results.max_chars_full_progress = 4000`, so it is trimmed to that instead of being flagged. It is an engineering budget, not a research finding. The 2,400 gate covers every tool; this view is the only exception (Vishnu's decision, 18 November).
- Make `scripts/check_mcp.py` require that **every** `tutor_turn` result in the loop, and the levels-only `get_my_progress`, is within the limit, counted as sent.
- Wrap logging in `timed()` so a logging failure is printed on stderr and the result is still returned. Cut stored and printed error text to 200 characters.
- `results.max_chars` stays 2,400. It is an engineering budget (about 600 tokens), not a research finding.

## Research basis

None. This is an engineering correction, not a teaching claim. The 2,400-character limit is the project's own budget and is labelled as such in `settings.md`.

The only external fact is how the SDK serialises results: `pydantic_core.to_json(result, indent=2)` in `mcp` 1.30 (`mcp/server/fastmcp/utilities/func_metadata.py`, `_convert_to_content`), confirmed by measuring the wire text.

## Alternatives considered

- **Count the indented text instead.** Honest, but it makes the same limit about 35% tighter, so more reference blocks would be dropped from `tutor_turn` and the teaching content would change a day before the freeze. Sending compact text keeps the content and removes the whitespace the chatbot does not need.
- **Raise the single limit.** Rejected: the gate is the handover's number. Only the every-part view gets a second limit.
- **Flag the every-part view and leave it whole.** The first version of this pull request did that. Vishnu preferred a separate limit that is enforced.
- **Drop whole blocks from `get_my_progress`** (for example `trends`). Rejected: it changes what a student sees. Trailing list items are the lowest-ranked by construction.
- **Fix only the count and leave the check as a median.** Rejected: the gate says "no tool result is over".

## Consequences

- Chatbots receive compact JSON instead of indented JSON. The content is identical, and the model reads either. Characters sent fall by roughly a quarter to a third.
- A student with many reviews or weak links may see one or two fewer list items in `get_my_progress`, only when the result would otherwise be over budget.
- `get_my_progress` with `include_parts` is allowed up to 4,000 characters (about 3,200 for `demo-secure`) and is flagged `OVER BUDGET` only above that. The 4,000 is a judgement call, labelled as an engineering budget.
- No migration. Instruction word count unchanged (897 of 900).

## Verification

```
.venv/bin/python -m pytest -q
python scripts/check_mcp.py --url http://127.0.0.1:8765/mcp   # all checks passed
```

Measured on the seeded demo (every-part view 3,196 against its 4,000 limit): levels-only `get_my_progress` 2,355 characters sent (was 3,571); after the check run's own activity 2,149 (was 2,425 before trimming); largest `tutor_turn` in the loop 2,278; none flagged over budget. New tests cover the compact text, counted equals sent, a failing `log_call` not replacing the result, error cutting, and `fit_progress`.

## What would change our mind

If a chatbot client proves to need the indented form or `structuredContent`, send both and count the larger. The compact form still has to be confirmed in claude.ai once, before the freeze: run the demo with it and check the chatbot reads results normally. If the 2,400 budget turns out to hurt teaching (reference blocks dropped too often in real use), raise it from measured token counts, not by feel.
