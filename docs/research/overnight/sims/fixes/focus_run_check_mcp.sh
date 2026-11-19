#!/usr/bin/env bash
# Run a code copy's own scripts/check_mcp.py against its own server on a fresh data dir (localhost only).
#   run_check_mcp.sh <code copy> <port> <out-file> <data dir under /tmp/claude-1000/>
set -u
CODE="$1"; PORT="$2"; OUT="$3"; DATA="$4"
PY=/home/vishnu/edux26/.venv/bin/python
case "$DATA" in /tmp/claude-1000/*) ;; *) echo "data dir must be under /tmp/claude-1000"; exit 2;; esac
rm -rf "$DATA"; mkdir -p "$DATA"
cd "$CODE"
export EDUX_DATA_DIR="$DATA" PYTHONPATH="$CODE" PYTHONDONTWRITEBYTECODE=1
$PY -m edux.cli load coursepacks/example-mini >/dev/null
$PY -m edux.cli seed-demo --reset >/dev/null
$PY -m edux.cli serve --host 127.0.0.1 --port "$PORT" >"$DATA/server.log" 2>&1 &
SRV=$!
for i in $(seq 50); do curl -s -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep 0.2; done
$PY scripts/check_mcp.py --url "http://127.0.0.1:$PORT/mcp" >"$OUT" 2>&1
echo "exit $?" >>"$OUT"
kill $SRV
