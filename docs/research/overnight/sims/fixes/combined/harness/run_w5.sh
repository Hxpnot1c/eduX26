#!/usr/bin/env bash
# Rebuild s5 (export + 0001..0005), s6 (s5 + 0006), s4+6 (export + 0001..0004 + 0006) and s6bc (s6 + 0006b + 0006c); run check_mcp, the wave-4
# and wave-5 probes on each, and the Plan A episode on s5/s6. Data dirs and copies under /tmp/claude-1000/w5-fixres/.
#   run_w5.sh [export]      (default /tmp/claude-1000/edux-05e-ff)
set -euo pipefail
SRC="${1:-/tmp/claude-1000/edux-05e-ff}"
W=/tmp/claude-1000/w5-fixres
HERE="$(cd "$(dirname "$0")" && pwd)"; C="$(dirname "$HERE")"; SIMS="$(cd "$C/../.." && pwd)"; F="$SIMS/fixes"
PY=/home/vishnu/edux26/.venv/bin/python
mkdir -p "$W/out" "$W/data" "$W/h" "$W/cap"
build() {   # build <name> <patch>...
  rm -rf "${W:?}/$1"; cp -r "$SRC" "$W/$1"; local n="$1"; shift
  for p in "$@"; do (cd "$W/$n" && patch -p1 -s --no-backup-if-mismatch < "$p"); done
}
build s5 "$C"/000[1-5]*.diff
build s6 "$C"/000[1-5]*.diff "$C"/0006-stuck-ladder-and-review-requests.diff
build s4+6 "$C"/000[1-4]*.diff "$C"/0006-stuck-ladder-and-review-requests.diff
build s6bc "$C"/000[1-5]*.diff "$C"/0006-stuck-ladder-and-review-requests.diff "$C"/0006b-*.diff "$C"/0006c-*.diff   # with w5-fix-labels' patches
sed 's#/tmp/claude-1000/w4-verifyQ/#/tmp/claude-1000/w5-fixres/#' "$HERE/check.sh" > "$W/check.sh"; chmod +x "$W/check.sh"
port=8851
for n in s5 s6 s4+6 s6bc; do
  "$W/check.sh" "$W/$n" $port "$W/out/check_$n.txt"; port=$((port + 1)); tail -1 "$W/out/check_$n.txt"
  mkdir -p "$W/$n/docs/research/overnight/sims/fixes"
  cp "$SIMS/edux_sim.py" "$W/$n/docs/research/overnight/sims/"; cp "$F/probes_w4.py" "$F/probes_w5.py" "$W/$n/docs/research/overnight/sims/fixes/"
  (cd "$W/$n" && PYTHONPATH="$W/$n" $PY docs/research/overnight/sims/fixes/probes_w4.py "$W/data/probes-$n" > "$W/out/probes_$n.txt")
  (cd "$W/$n" && PYTHONPATH="$W/$n" $PY docs/research/overnight/sims/fixes/probes_w5.py "$W/data/p5-$n" --json "$W/out/probes_w5_$n.json" > "$W/out/probes_w5_$n.txt")
  grep '^A\|^B' "$W/out/probes_w5_$n.txt"
done
cp "$SIMS/demo-05e/run_episode.py" "$SIMS/demo-05e/scenarios.py" "$W/h/"
sed -i 's#/tmp/claude-1000/w3-07/#/tmp/claude-1000/w5-fixres/#g' "$W/h/run_episode.py"
for n in 5 6; do (cd "$W/h" && $PY run_episode.py --code "$W/s$n" --label "s$n" --out "$W/cap" --port $((8860 + n)) \
  --scenario final final_ticks_ad clean plan_now then_ped recommended > "$W/out/episode_s$n.log"); done
$PY "$HERE/digest_q.py" "$W/cap" s5 s6 > "$W/out/planA_digest.txt"
echo "outputs in $W/out"
