# Build plan

This folder is the build plan for the learning service: an MCP server that a school's chatbot connects to. It holds the course as a knowledge graph built from real exam material, keeps a learner model for each student, and tells the chatbot how to teach that student each turn.

- `reference/`: what we're building. Read the relevant reference file before each step.
- `steps/`: the order to build it in, one branch and pull request per step.

## Steps

| Step | Branch | What it delivers |
|---|---|---|
| [01](steps/01-scaffold.md) | `build/01-scaffold` | Full folder and file layout, with stubs only. Merged before any real code |
| [02](steps/02-content-and-ingest.md) | `build/02-content-ingest` | Course-pack format, content database, validation, loading, teacher feedback overlay, exam weights |
| [03](steps/03-graph-lookups.md) | `build/03-graph-lookups` | Tree, edge and note lookups |
| [04](steps/04-learner-model.md) | `build/04-learner-model` | Learner database, event logs, state rebuilt from events, decay, nudges, scheduling, teaching policy |
| [04b](steps/04b-evidence-log.md) | `build/04b-evidence-log` | Evidence as an event: chat evidence with exchanges, immediate-recall discount, replay in rebuild |
| [04c](steps/04c-session-signals.md) | `build/04c-session-signals` | Sessions from events, surprise against the model's expectation, fatigue (softened evidence) and stuck parts |
| [05](steps/05-server-context.md) | `build/05-server-context` | MCP server over HTTP: learning context, exchange logging, progress, profile; context assembled from configurable blocks |
| [06](steps/06-demo.md) | `build/06-demo` | Demo seeding script, README, tunnel and connector set-up |
| [Later](steps/later.md) | | Checks (past-question, explain-back, link, find-the-error), automated tests, student and teacher pages, extras |

Checks and tests come after the base works end to end; the step files say where they will plug in.

## Working rules

**Branches and pull requests**
- One branch per step, created from the latest `main`. Never commit directly to `main`.
- Open a pull request when the step's "done when" list is met. Merge with **rebase and merge**, so `main` keeps a linear history of meaningful commits.
- Start the next step from the updated `main`.

**Commits**
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`, with a short imperative summary (≤ 72 characters).
- One logical change per commit. Each step file lists the commits it expects; small deviations are fine.
- No work-in-progress commits, no commented-out code, no generated databases, no secrets.
- Commit and pull-request messages describe the change only. They contain no tool or assistant attribution, co-author trailers, session links or "generated with" lines.

**Pull-request description**
```
## What
<one paragraph>

## How to check
<commands to run and what you should see>

## Notes
<decisions, follow-ups>
```

**Code**
- Python 3.11+, SQLite, MCP Python SDK `mcp>=1.30,<2`.
- Every teaching or scoring number lives in `settings.toml`. What the chatbot sees is configured in `context.toml` and the `text/` folder. Nothing else hard-codes them.
- If something in the plan conflicts with what you find (for example an SDK API has changed), stop and raise it in the pull request rather than guessing.
