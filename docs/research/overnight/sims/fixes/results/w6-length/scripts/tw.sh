#!/usr/bin/env bash
# tw.sh <code copy> <label> [--list]: load example-mini into a fresh data dir, run testwise.py
set -eu
CODE="$(cd "$1" && pwd)"; LABEL="$2"; shift 2
PY=/home/vishnu/edux26/.venv/bin/python
W=/tmp/claude-1000/w6-fix-length
DATA=$W/data/tw-$LABEL
rm -rf "$DATA"; mkdir -p "$DATA"
cd "$CODE"
export EDUX_DATA_DIR="$DATA" PYTHONPATH="$CODE" PYTHONDONTWRITEBYTECODE=1
$PY -m edux.cli load coursepacks/example-mini > "$DATA/load.txt" 2>&1
$PY /home/vishnu/edux26-research/docs/research/overnight/sims/fixes/testwise.py --json $W/tw_$LABEL.json "$@"
