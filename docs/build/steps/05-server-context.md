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
- `text/tools/log_exchange.md` must say: send `evidence` only when the student actually produced an answer or explanation in this turn, scored 0–1 against the notes and mark points from `get_learning_context`. Never send it for the chatbot's own explanation.
- `python -m edux.cli serve`.

## Choosing what goes into each block
Graph lookups (step 03) return full lists with the numbers needed to rank them. Each block chooses what reaches the chatbot **for this turn**, not by a fixed top N. Most blocks combine three ingredients:
1. **Content weights:** node importance, link weight (`edge_weight`), source authority, marks.
2. **The student's state:** `p_now`, active misconceptions, recent activity (step 04).
3. **Relevance to the message:** `graph.relevance` / `graph.node_relevance`.

| block | what decides what's shown |
|---|---|
| focus | how well each part matches the message (`graph.resolve`). Ties go to parts the student touched recently, then importance |
| support | the student's `p_now` on the focus part. Nothing to rank |
| weak_prerequisites | how weak the student is on it × link weight × importance |
| anchor | the student is secure on the analogous part × link weight |
| confusables | past mix-ups by this student, or the message mentions the other part × link weight |
| causal (new) | the message asks about effects or causes and mentions the other end × link weight. Uses `graph.causal_out` / `causal_in` |
| active_misconceptions | ones the student holds first, then relevance to the message, then how recently seen |
| notes | relevance to the message first, then source authority (a calculation question gets the formula note) |
| exam_relevance | marks at stake, closeness of the exam, and command word matching the request ("calculate", "explain") |
| reviews_due | due-ness × importance, boosted when the due part is linked to the current focus |
| teaching_note | built from the other blocks. Nothing to rank |

- Every coefficient in these scores goes in `settings.toml`, under a section per block if they differ. The limits stay in `context.toml`.
- Add `causal` to `BLOCKS`, to the `full` profile in `context.toml`, and to the block table in `reference/tools-and-context.md`.
- The cross-student misconception signal (`learner.misconception_link_signal`) is added to link weight when it is read, with share `link_weight.w_misconception`. It's 0 until there is enough evidence across students.

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
