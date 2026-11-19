# Synapse

Synapse is a learning service for school chatbots. It is an MCP server that:
- holds a course as a knowledge graph built from exam material (specification, past papers, mark schemes, notes)
- keeps a learner model for each student, built from what they do in their chatbot
- tells the chatbot how to teach that student on each turn, as a short ordered plan of one or two steps: what to check first, how much help to give, which misconception to correct, what is due for review

Students connect their own chatbot (claude.ai or ChatGPT) with a personal link. The chatbot calls one tool, `tutor_turn`, at the start of each reply. The server never calls an LLM itself. The chatbot labels the student's message and ticks the points their answer made. The server scores that with fixed rules from `settings.toml` and returns the plan for the reply.

Synapse is our entry to Cambridge EduX 2026 (Track 1, *Beneath the Surface: Defining and Assessing AI Literacy*). "eduX" is the competition's name, not the product's. The GitHub repository is `synapse-eduX26`.

The build plan and reference design are in [`docs/build`](docs/build/README.md).

**Names.** Everything a student, teacher or judge sees says Synapse. The internal identifiers keep their old spelling until after the competition, so existing set-ups keep working: the Python package `edux`, the `EDUX_*` environment variables and the `python -m edux.cli` command.

## Quick demo (about ten minutes)
You need Python 3.11+ and a tunnel tool (Cloudflare Tunnel or ngrok), because claude.ai and ChatGPT reach the server from the internet, not from your computer.

```bash
git clone git@github.com:Hxpnot1c/synapse-eduX26.git && cd synapse-eduX26
python3 -m venv .venv && .venv/bin/pip install -e .   # or: uv venv && uv pip install -e .
cp .env.example .env
scripts/demo.sh            # loads example-mini, creates three demo students, starts the server
```

`scripts/demo.sh` prints a key and URL for each demo student: `demo-secure`, `demo-weak` and `demo-showme` (see [`docs/demo-script.md`](docs/demo-script.md) for what each one shows). Then:
1. Start a tunnel in a second terminal (see [Tunnel](#tunnel)) and add its host to `ALLOWED_HOSTS` in `.env`.
2. Restart `scripts/demo.sh`. It recreates the demo students' histories but keeps their keys, so connector URLs keep working.
3. Add the connector in claude.ai or ChatGPT with `https://<tunnel-host>/mcp?key=<key>` (see [Connect a chatbot](#connect-a-chatbot)).
4. Paste the set-up text from [`text/chatbot_setup.md`](text/chatbot_setup.md) into the chatbot's instructions.
5. Ask "how do I calculate PED?".

## Step by step

### Install
```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env
```
`.env` holds:
- `EDUX_DATA_DIR`: where `content.db` and `learner.db` live (default `./data`)
- `HOST`, `PORT`: where the server listens (default `127.0.0.1:8000`)
- `ALLOWED_HOSTS`: host names the server accepts, comma-separated

Students' messages are never stored. Student keys are stored only as hashes, and student ids are random (`s-1a2b3c4d`), never made from a name.

The commands below read the environment, so load `.env` first (`set -a; . ./.env; set +a`). `scripts/demo.sh` does this for you.

### Load a course pack
```bash
.venv/bin/python -m ingest.cli validate coursepacks/example-mini
.venv/bin/python -m edux.cli load coursepacks/example-mini
```
`example-mini` is a small invented Economics pack that is committed for testing and demos. Real packs live in `coursepacks/<id>/private/`, which git ignores. The real course is Pearson Edexcel A level Economics A (9EC0), with pack id `edexcel-econ-a` in `coursepacks/edexcel-econ-a/private/`. Its specification, papers, mark schemes and examiner reports are © Pearson Education Limited, so the pack holds our own summaries, short key wordings and references only, never full question or mark-scheme text. [`coursepacks/README.md`](coursepacks/README.md) describes the format. Loading rebuilds `content.db`; students' records in `learner.db` are kept.

### Add a student
```bash
.venv/bin/python -m edux.cli add-student --name "Sam" --course example-mini
```
This prints the student's id and key. Their connector URL is `https://<host>/mcp?key=<key>`. The key is the only thing that identifies them, so treat it like a password.

Other student commands:
- `state --student <id>`: their parts, levels and reviews due
- `sessions --student <id>`: their study sessions
- `set-profile --student <id> --profile minimal`: switch the context they get (`default` goes back; `minimal` gets notes only and no plan)
- `context --student <id> --message "..."`: print the context blocks for a message, numbers included (records nothing)
- `calls [--student <id>] [--last N]`: recent tool calls, server time per tool (median and 90th percentile), and the gap between a student's calls
- `seed-demo [--reset]`: create the three demo students

### Serve
```bash
.venv/bin/python -m edux.cli serve           # http://127.0.0.1:8000/mcp
```
Any request without a known key is refused with 401. Each tool call prints one line, e.g. `tutor_turn demo-weak 18ms 3.1k chars ok`; keys never appear in the console or the logs.

To check a running server without a chatbot (on `example-mini` with the demo students seeded, from the repo root with the same `EDUX_DATA_DIR`):
```bash
.venv/bin/python scripts/check_mcp.py --url http://127.0.0.1:8000/mcp
```
It runs a three-message conversation as `demo-secure` and checks each plan, the scores recorded, rebuild and timing. It reseeds the demo students before and after (keys stay the same).

### Tunnel
claude.ai and ChatGPT can't reach `localhost`, so give the server a public HTTPS address with either tool:

```bash
cloudflared tunnel --url http://localhost:8000   # prints https://<random>.trycloudflare.com
ngrok http 8000                                  # prints https://<random>.ngrok-free.app (needs a free account)
```

Add the tunnel's host name, without `https://`, to `ALLOWED_HOSTS` in `.env`, for example `ALLOWED_HOSTS=localhost,127.0.0.1,abc-def.trycloudflare.com`, then restart the server. A quick tunnel gets a new host name each time it starts.

### Connect a chatbot
The connector URL is `https://<tunnel-host>/mcp?key=<key>`, including `/mcp` and the key. Menu names change often; these are the routes at the time of writing.

**claude.ai**
1. Open Customize → Connectors (Settings → Connectors on older layouts) and choose **Add custom connector**.
2. Give it a name (e.g. Synapse) and paste the URL. Leave the OAuth fields under Advanced settings empty.
3. In a chat, turn the connector on from the tools menu.

The free plan allows one custom connector.

**ChatGPT (developer mode)**
1. Open Settings → Connectors (or Apps & Connectors) → Advanced settings and switch on **Developer mode**. This needs a paid plan.
2. Choose **Create**, give it a name and description, paste the URL, set authentication to **No authentication**, tick that you trust the provider and create it.
3. In a chat, turn the connector on for the conversation.

**Then**, paste the set-up text from [`text/chatbot_setup.md`](text/chatbot_setup.md) into the chatbot's custom instructions (or a project's instructions), so it calls `tutor_turn` at the start of every reply.

## Troubleshooting
- **421 "Invalid Host header" (or 403 "Invalid Origin header"):** the tunnel host isn't in `ALLOWED_HOSTS`. Add it without `https://` and restart the server.
- **401 "unknown or missing key":** the URL is missing `?key=`, or the student no longer exists (for example after deleting `learner.db`). Demo keys survive `seed-demo --reset`.
- **The chatbot doesn't see new tools or changed descriptions:** disconnect and reconnect the connector (or remove and re-add it) and start a new chat; tool lists are cached.
- **The connector worked yesterday but not today:** a quick tunnel's host changes on restart. Update `ALLOWED_HOSTS` and the connector URL.
- **Free plan:** claude.ai allows one custom connector on the free plan; remove another one first. ChatGPT developer mode needs a paid plan.
- **The chatbot answers without calling the tools:** check the set-up text is in its instructions and the connector is switched on in that chat.
- **Replies feel slow:** run `python -m edux.cli calls`. If `tutor_turn` takes a few milliseconds but the gap between calls is long, the time is the chatbot writing; a lower `answer_length` (or `[style] max_words`) shortens replies.

## Repository
- `edux/`: the server, learner model, graph lookups, context blocks and the per-turn plan
- `ingest/`: course pack validation and loading
- `coursepacks/`: course packs (`example-mini` committed; real ones in `private/`)
- `text/`: every piece of wording the chatbot sees
- `settings.toml`, `context.toml`: every teaching number, and which context each profile gets
- `scripts/`: the demo runner and the MCP client check
- `docs/`: the build plan, reference design and demo script

MIT licence.
