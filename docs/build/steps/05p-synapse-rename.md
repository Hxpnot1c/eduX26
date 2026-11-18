# Step 05p: The product is called Synapse

Branch `build/synapse-rename`, from `main` after the fix steps 05k–05o.

## What
eduX is the competition's name, not the product's. Everything a user, a teacher or a judge sees says **Synapse**.

**Rename now (user-facing):**
- the MCP server's display name (`FastMCP(name=…)` in `edux/server.py`);
- the server instructions (`text/server_instructions.md`) and any other `text/` file that names the product;
- the README title and prose;
- the docs prose. The first mention in a file reads "Synapse (repo eduX26)", and later ones "Synapse";
- the demo script (`scripts/demo.sh`) and its printed lines;
- CLI help text (`edux/cli.py`: the parser description and help strings);
- step docs from now on. Step docs written before this one aren't rewritten, except where they're edited anyway.

**Leave for now (internal):**
- the `edux/` package and its imports;
- `EDUX_*` environment variables;
- the repo name;
- the `docs/research/` files, which record what was reviewed at the time.

## Why
The competition is eduX; the product needs its own name. Renaming internal identifiers mid-competition would touch every file and break existing set-ups (connector URLs, env vars), for no gain to users.

## Files
- `edux/server.py`, `edux/cli.py`.
- `text/server_instructions.md`, and any `text/` file that names the product.
- `README.md`, `scripts/demo.sh`.
- `docs/build/README.md`, `docs/build/reference/*.md` (prose only), `docs/build/steps/06-demo.md`.
- `docs/build/steps/later.md`: the internal-rename line is already listed by the docs PR.
- `scripts/check_mcp.py`: the server's reported name is "Synapse".

## Settings
None.

## Commits
1. `feat(server): name the MCP server Synapse`
2. `docs(text): call the product Synapse in the server instructions`
3. `chore(cli): call the product Synapse in help text and the demo script`
4. `docs: call the product Synapse in the README and build docs`

## Done when
- A connected chatbot shows "Synapse". `grep -ri edux` finds only package names, imports, env vars, the repo name, `docs/research/` and older step docs.
- The instructions word count is unchanged or lower (the names are the same length), and is reported.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state.

## Tests
`scripts/check_mcp.py`: the server name. Everything else is a text change.
