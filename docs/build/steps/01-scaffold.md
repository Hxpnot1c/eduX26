# Step 01: Scaffold

**Branch:** `build/01-scaffold`
**Read first:** `../reference/design-for-change.md`

## Goal
Create the full folder and file layout with stubs, so every later step only fills files in. No real logic. Merge this before writing any code.

## Layout

```
.
├── README.md                     # short: what this is, link to docs/build
├── LICENSE                       # MIT unless the team decides otherwise
├── .gitignore                    # Python, *.db, .env, coursepacks/*/private/
├── .env.example                  # EDUX_DATA_DIR, STORE_PROMPTS=0, HOST, PORT, ALLOWED_HOSTS
├── pyproject.toml                # package edux + ingest; deps: mcp[cli]>=1.30,<2, uvicorn; python >=3.11
├── settings.toml                 # full contents from reference/settings.md
├── context.toml                  # full contents from reference/settings.md
├── text/
│   ├── server_instructions.md    # placeholder heading
│   ├── teaching_note.md
│   ├── chatbot_setup.md
│   ├── support/{worked_example,hint,explain_back}.md
│   └── tools/{get_learning_context,log_exchange,get_my_progress,update_my_profile}.md
├── edux/
│   ├── __init__.py
│   ├── settings.py               # load settings.toml + context.toml, settings_hash
│   ├── db.py                     # connections, WAL, ATTACH, migrations runner
│   ├── content_schema.sql
│   ├── graph.py                  # tree, edges, notes, weights lookups
│   ├── learner.py                # events, rebuild_state, scoring rules
│   ├── context_blocks.py         # one function per block + registry
│   ├── service.py                # what each tool does
│   ├── server.py                 # MCP adapters, auth by key
│   └── cli.py                    # load, rebuild, add-student, seed-demo
├── ingest/
│   ├── __init__.py
│   ├── registry.py               # column definitions
│   ├── validate.py
│   ├── load.py                   # CSV → content.db, weights, feedback overlay, report
│   └── cli.py                    # validate, load, templates
├── migrations/
│   └── 001_init.sql              # learner.db schema from reference/database.md
├── coursepacks/
│   └── example-mini/             # header-only CSVs for now
├── teacher_feedback/
│   └── .gitkeep
├── scripts/
│   └── .gitkeep
└── docs/
    └── build/                    # this plan
```

Python stubs contain the module docstring, imports and function signatures with docstrings, with bodies `raise NotImplementedError`. Signatures follow the reference files.

## Commits
1. `chore: add project metadata, licence and gitignore`
2. `docs: add build plan`
3. `chore: add settings, context config and text placeholders`
4. `chore: scaffold edux and ingest packages with stubs`
5. `chore: add schema files and learner migration`
6. `chore: add example course pack headers`

## Done when
- `pip install -e .` works.
- `python -c "import edux, ingest"` works.
- `settings.toml` and `context.toml` parse.
- No database files or secrets are committed.
