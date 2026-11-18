#!/usr/bin/env bash
# check.sh <code> <port> <out>: the copy's own scripts/check_mcp.py against its own localhost server, fresh data dir
set -u
CODE="$1"; PORT="$2"; OUT="$3"
PY=/home/vishnu/edux26/.venv/bin/python
DATA=/tmp/claude-1000/w5-06g/data/check-$PORT
rm -rf "$DATA"; mkdir -p "$DATA"
cd "$CODE"
export EDUX_DATA_DIR="$DATA" PYTHONPATH="$CODE" PYTHONDONTWRITEBYTECODE=1
$PY -m edux.cli load coursepacks/example-mini >"$DATA/load.txt" 2>&1
$PY -m edux.cli seed-demo --reset >/dev/null
$PY -m edux.cli serve --host 127.0.0.1 --port "$PORT" >"$DATA/server.log" 2>&1 &
SRV=$!
for i in $(seq 50); do curl -s -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep 0.2; done
$PY scripts/check_mcp.py --url "http://127.0.0.1:$PORT/mcp" >"$OUT" 2>&1
echo "exit $?" >>"$OUT"
kill $SRV
