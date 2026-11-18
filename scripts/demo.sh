#!/usr/bin/env bash
# Synapse demo: load a course pack, (re)create the three demo students and start the MCP server.
#   scripts/demo.sh [pack folder]     default: coursepacks/example-mini
# Reads .env if there is one (EDUX_DATA_DIR, HOST, PORT, ALLOWED_HOSTS).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .env ]; then set -a; . ./.env; set +a; fi
PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python
PACK="${1:-coursepacks/example-mini}"

echo "== Synapse demo: loading $PACK"
"$PY" -m edux.cli load "$PACK"
echo
echo "== seeding demo students"
"$PY" -m edux.cli seed-demo --reset
echo
echo "Through a tunnel, use https://<tunnel-host>/mcp?key=<key> and add the tunnel host to ALLOWED_HOSTS."
echo
"$PY" -m edux.cli serve
