#!/usr/bin/env bash
# run_variant.sh <code copy> <label> [n] [turns] [extra args]: every strategy in its own process (literal labeller),
# plus the skeptical labeller for the restating strategies. Results: results/<label>/<strategy>-<labeller>.json
set -u
CODE="$1"; LABEL="$2"; N="${3:-30}"; TURNS="${4:-40}"; shift 4 || shift $#
PY=/home/vishnu/edux26/.venv/bin/python
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA=/tmp/claude-1000/w5-06g/data/$LABEL
OUT="$HERE/results/$LABEL"; mkdir -p "$OUT"
pids=()
for s in ${ONLY:-C0 C1 C2 C2m C3 C4 C5 L0 L0s L1 L1d L2 L3 L4 L5 L6}; do
  PYTHONPATH="$CODE" $PY "$HERE/gaming_sim.py" --code "$CODE" --data "$DATA/$s" --n "$N" --turns "$TURNS" --only "$s" --out "$OUT/$s-literal.json" "$@" &
  pids+=($!)
done
for s in ${ONLY_SK:-C4 L1d L2 L3}; do
  PYTHONPATH="$CODE" $PY "$HERE/gaming_sim.py" --code "$CODE" --data "$DATA/$s-sk" --n "$N" --turns "$TURNS" --only "$s" --labeller skeptical --out "$OUT/$s-skeptical.json" "$@" &
  pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait $p || fail=1; done
echo "done $LABEL fail=$fail"
