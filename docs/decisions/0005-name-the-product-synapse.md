# 0005. Name the product Synapse; eduX is the competition

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Vishnu (what students, teachers and judges see)
- **Pull request:** #48
- **Step:** [05p](../build/steps/05p-synapse-rename.md)

## Context

The project was called eduX26 in the README, the server name, the chatbot-facing text, the AI-literacy pack and the docs. eduX26 is the name of the competition we entered (Cambridge EduX 2026, Track 1). The product is called Synapse. A student's chatbot, a teacher or a judge should see the product name, not the competition's. The GitHub repository was renamed to `synapse-eduX26` on 18 November, so the old clone URL in the README was wrong.

## Decision

- **User-facing names say Synapse:** the MCP server's reported name, the server instructions, the chatbot set-up text, CLI help, the demo script, the README and the docs, including the research notes in `docs/research/` and the author and title columns of the AI-literacy and example packs.
- **The README says what eduX is** (the competition) and gives the repository name `synapse-eduX26` and the new clone command. The git `origin` remote is updated.
- **Internal identifiers keep their old spelling until after the competition:** the `edux` Python package and imports, `EDUX_*` environment variables, the `python -m edux.cli` command, and the `edux_ai_literacy` source id. Renaming them would touch every file and break existing set-ups (connector URLs, environment files) the day before filming, for no gain to users. They stay on the list in `later.md` for one commit after the competition.
- `scripts/check_mcp.py` checks that the server reports the name "Synapse".

## Research basis

None. This is a naming decision, not a teaching claim. No numbers change.

## Alternatives considered

- **Rename the internal package and environment variables now.** The request was to update "all references". Rejected for now because it breaks working set-ups before the freeze; it is one mechanical commit afterwards. This is the part Vishnu should confirm.
- **Leave the research notes under `docs/research/` unchanged,** as step 05p first said, because they record what was reviewed. Changed after the request: they refer to the product, not to a source, and a reader should not meet two names.
- **Rename the competition references too.** Rejected: eduX26 / EduX 2026 is the competition's real name.

## Consequences

- A connected chatbot shows "Synapse". The instruction word count is unchanged (897 of 900), because "eduX" and "Synapse" are each one word.
- A grep for `eduX` finds only step 05p (which describes the decision) and the README's explanation of the competition name.
- The research folder (outside this repository) still uses "eduX 2026" for the competition, which is correct.
- Existing connector URLs keep working, because the path and keys are unchanged.

## Verification

```
.venv/bin/python -m pytest -q
python scripts/check_mcp.py --url http://127.0.0.1:8771/mcp   # all checks passed, including the server name
grep -rn "eduX" . --include=*.md --include=*.py --include=*.toml --include=*.csv --include=*.sh   # only 05p and the README competition line
```

## What would change our mind

If another team or a judge confuses the repository and the product, rename the internal identifiers earlier.
