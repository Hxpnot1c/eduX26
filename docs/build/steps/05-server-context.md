# Step 05: Server and context

**Branch:** `build/05-server-context`
**Read first:** `../reference/tools-and-context.md`, `../reference/settings.md` (context.toml, text/)

## Goal
The MCP server over Streamable HTTP at `/mcp`, with student keys, the four base tools, the two prompts and configurable context blocks.

## Work
- `edux/context_blocks.py`:
  - one function per block, each taking `(student, parts, settings)` and returning a dict or `None`
  - a `BLOCKS` registry
  - `assemble(profile, ...)`, which follows `context.toml` and applies the limits
- `edux/service.py`: `learning_context`, `log_exchange`, `my_progress` and `update_profile`. These hold the logic; the server only adapts arguments.
- `edux/server.py`:
  - FastMCP with instructions from `text/server_instructions.md` and tool descriptions from `text/tools/`.
  - Read `key` from the request query string; map it to a student; reject unknown keys.
  - `Literal` types for labels.
  - Transport security with `ALLOWED_HOSTS` from the environment, so a tunnel host works.
- Prompts: `review_due` and `check_me`.
- Fill in the `text/` files with real wording, including `chatbot_setup.md` (the paste-in instructions for students).
- `python -m edux.cli serve`.

## Commits
1. `feat(context): add context blocks and profile assembly`
2. `feat(service): add learning context, exchange logging, progress and profile`
3. `feat(server): serve tools over streamable HTTP with student keys`
4. `feat(server): add review and check prompts`
5. `docs(text): write server instructions, tool descriptions and support text`

## Done when
- MCP Inspector, connected to `http://localhost:<port>/mcp?key=<key>`, lists the tools.
- `get_learning_context` returns the blocks for an `example-mini` part.
- `log_exchange` returns at once, and `state` shows the update.
- A wrong key is refused.
- Switching the student's profile to `minimal` changes the output.
