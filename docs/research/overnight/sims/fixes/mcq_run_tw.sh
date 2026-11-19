#!/usr/bin/env bash
# run_tw.sh <code copy> <label> [--list]
set -eu
CODE="$1"; LABEL="$2"; shift 2
PY=/home/vishnu/edux26/.venv/bin/python
DATA=/tmp/claude-1000/w4-fix-mcq/data/tw-$LABEL
rm -rf "$DATA"; mkdir -p "$DATA"
cd "$CODE"
export EDUX_DATA_DIR="$DATA" PYTHONPATH="$CODE" PYTHONDONTWRITEBYTECODE=1
$PY -m edux.cli load coursepacks/example-mini > "$DATA/load.txt" 2>&1
$PY /home/vishnu/edux26-research/docs/research/overnight/sims/fixes/testwise.py --json /home/vishnu/edux26-research/docs/research/overnight/sims/fixes/testwise_$LABEL.json "$@"
