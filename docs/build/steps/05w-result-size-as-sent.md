# Step 05w: Count results as they are sent

Branch `build/fix-result-size`, from `main` once step 05v (#46) is merged.

## What
- Tool results are sent as compact JSON text and sized from that same text, so the number in `call_log.result_chars` is the number the chatbot receives.
- `service.fit_progress` keeps the levels-only `get_my_progress` within `results.max_chars` by dropping the lowest-ranked list items (`weak_links`, then `reviews_due`, then `levers`).
- `over_budget` covers `get_my_progress` as well as `tutor_turn`.
- `scripts/check_mcp.py` requires every `tutor_turn` result in the loop, and the levels-only `get_my_progress`, to be within the limit. It used to check the median.
- A failed `call_log` write is printed on stderr and never replaces the tool's result; stored error text is cut to 200 characters.

## Why
The MCP SDK pretty-prints results with `indent=2`, so the old count (`json.dumps`) understated what was sent by about a third: 2,355 counted and 3,571 sent for `demo-secure`'s progress. `get_my_progress` was never checked and could reach 2,425 characters. See [decision 0004](../../decisions/0004-count-results-as-sent.md).

## Files
- `edux/service.py`: `compact_json`, `result_size`, `fit_progress`, `over_budget`, `my_progress`.
- `edux/server.py`: `timed` returns a `CallToolResult` with the compact text; `ERROR_CHARS`; logging failure handled.
- `scripts/check_mcp.py`: sizes counted with `service.result_size`; every result within the limit.
- `tests/test_tool_results.py`.
- `docs/build/reference/database.md`, `tools-and-context.md`, `settings.md`.
- `docs/decisions/0004-count-results-as-sent.md`.

## Done when
- `pytest` passes.
- `scripts/check_mcp.py` passes with the new size checks and rebuild identical.
- Nothing is flagged `OVER BUDGET` on the demo path.
- No migration, and the instruction word count is unchanged.

## Notes
`get_my_progress` with `include_parts` is over the limit by design (about 3,100 characters for `demo-secure`). It is flagged, not trimmed. Whether to trim it is Vishnu's call.
