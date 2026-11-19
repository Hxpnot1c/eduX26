#!/usr/bin/env bash
# run_w6.sh <tree> <label> <group>: runs gaming_w6.py (gaming_sim.py + C3t/C3x) on one tree, one process per strategy,
# same seeds as sims/gaming (rng seed "<strategy>-<k>"). group: course | literacy | all.
# N = 100 for the honest students (C0, L0, L0s), 30 for everything else; 40 messages, one session.
# Output: $OUT/<label>/<strategy>-<labeller>.json (OUT defaults to /tmp/claude-1000/w6-fix-counters/res)
set -u
CODE="$1"; LABEL="$2"; GROUP="$3"
PY=/home/vishnu/edux26/.venv/bin/python
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-/tmp/claude-1000/w6-fix-counters/res}/$LABEL"; DATA=/tmp/claude-1000/w6-fix-counters/data/$LABEL
mkdir -p "$OUT"
jobs=()
case "$GROUP" in
  course)   jobs=(C0:100:literal C1:30:literal C2m:30:literal C3:30:literal C3t:30:literal C3x:30:literal C3x:30:skeptical C4:30:literal C4:30:skeptical C5:30:literal);;
  literacy) jobs=(L0:100:literal L0s:100:literal L1:30:literal L1c:30:literal L1d:30:literal L1d:30:skeptical L2:30:literal L3:30:literal);;
  all)      jobs=(C0:100:literal C1:30:literal C2:30:literal C2m:30:literal C3:30:literal C3t:30:literal C3x:30:literal C3x:30:skeptical C4:30:literal C4:30:skeptical C5:30:literal
                  L0:100:literal L0s:100:literal L1:30:literal L1c:30:literal L1d:30:literal L1d:30:skeptical L2:30:literal L2:30:skeptical L3:30:literal L3:30:skeptical L4:30:literal L5:30:literal L6:30:literal);;
esac
pids=()
for j in "${jobs[@]}"; do
  IFS=: read -r s n lab <<<"$j"
  PYTHONPATH="$CODE" $PY "$HERE/gaming_w6.py" --code "$CODE" --data "$DATA/$s-$lab" --n "$n" --turns 40 --only "$s" \
    --labeller "$lab" --out "$OUT/$s-$lab.json" 2>/dev/null &
  pids+=($!)
  while [ "$(jobs -rp | wc -l)" -ge 8 ]; do wait -n; done
done
wait
echo "done $LABEL"
