#!/usr/bin/env bash
# Rebuild the wave-4 combined copies s0..s5 from the read-only 05e export and run every check on each step.
# Never touches the repo, /home/vishnu/edux26 or the export. All data dirs are under /tmp/claude-1000/w4-verifyQ/.
#   run_all.sh [export]      (default /tmp/claude-1000/edux-05e-ff)
set -euo pipefail
SRC="${1:-/tmp/claude-1000/edux-05e-ff}"
W=/tmp/claude-1000/w4-verifyQ
HERE="$(cd "$(dirname "$0")" && pwd)"; C="$(dirname "$HERE")"; SIMS="$(cd "$C/../.." && pwd)"; F="$SIMS/fixes"
PY=/home/vishnu/edux26/.venv/bin/python
mkdir -p "$W/h" "$W/out" "$W/cap" "$W/vcap"

# copies: s0 = export, sN = export + patches 0001..000N
for n in 0 1 2 3 4 5; do
  rm -rf "${W:?}/s$n"; cp -r "$SRC" "$W/s$n"
  for p in $(ls "$C"/000*.diff | head -n "$n"); do (cd "$W/s$n" && patch -p1 -s --no-backup-if-mismatch < "$p"); done
done

# demo-05e and verify drivers, pointed at this folder (their own data paths are hard-coded)
cp "$SIMS/demo-05e/run_episode.py" "$SIMS/demo-05e/scenarios.py" "$F/verify_run_episode.py" "$F/verify_scenarios.py" "$W/h/"
sed -i 's#/tmp/claude-1000/w3-07/#/tmp/claude-1000/w4-verifyQ/#g' "$W/h/run_episode.py"
sed -i 's#/tmp/claude-1000/w4-fix-verify/#/tmp/claude-1000/w4-verifyQ/#g; s#data/{label}#vdata/{label}#' "$W/h/verify_run_episode.py"

PLAN_A="final final_ticks_ad clean plan_now then_ped recommended"
VERIFY="dead_ad_then_ok dead_noanswer_then_ok final final_ticks_ad final_ticks_abcd verify_ignored unprompted_dead_task_open unprompted_dead_no_task clean"
for n in 0 1 2 3 4 5; do
  "$HERE/check.sh" "$W/s$n" $((8810 + n)) "$W/out/check_s$n.txt"; tail -1 "$W/out/check_s$n.txt"
  # probes (wave-1 bugs + talk-only + propagation): probes_w4.py must sit inside the copy (edux_sim.ROOT = copy)
  mkdir -p "$W/s$n/docs/research/overnight/sims/fixes"
  cp "$SIMS/edux_sim.py" "$W/s$n/docs/research/overnight/sims/"; cp "$F/probes_w4.py" "$W/s$n/docs/research/overnight/sims/fixes/"
  (cd "$W/s$n" && PYTHONPATH="$W/s$n" $PY docs/research/overnight/sims/fixes/probes_w4.py "$W/data/probes-s$n" > "$W/out/probes_s$n.txt")
  rm -rf "${W:?}/s$n/docs/research/overnight"
  [ "$n" -ge 2 ] && (cd "$W/h" && $PY run_episode.py --code "$W/s$n" --label "s$n" --out "$W/cap" --port $((8820 + n)) --scenario $PLAN_A)
done
(cd "$W/h" && for n in 0 3 5; do $PY verify_run_episode.py --code "$W/s$n" --label "s$n" --out "$W/vcap" --port $((8830 + n)) --scenario $VERIFY; done)
$PY "$HERE/digest_q.py" "$W/cap" s0 s2 s3 s4 s5 > "$W/out/planA_digest.txt"
$PY "$HERE/digest_q.py" "$W/vcap" s0 s3 s5 > "$W/out/verify_scenarios_digest.txt"

# headline numbers
for n in 0 2 5; do for h in "" "--holdout"; do t="s$n${h:+-holdout}"; rm -rf "${W:?}/data/focus-$t"; mkdir -p "$W/data/focus-$t"
  (cd "$W/out" && EDUX_DATA_DIR="$W/data/focus-$t" PYTHONPATH="$W/s$n" $PY "$F/focus_measure.py" --label "$t" $h > "$W/out/focus_$t.txt"); done; done
for n in 0 4 5; do D="$W/data/tw-s$n"; rm -rf "${D:?}"; mkdir -p "$D"
  (cd "$W/s$n" && EDUX_DATA_DIR="$D" PYTHONPATH="$W/s$n" $PY -m edux.cli load coursepacks/example-mini >/dev/null 2>&1 \
     && EDUX_DATA_DIR="$D" PYTHONPATH="$W/s$n" $PY "$F/testwise.py" --json "$W/out/testwise_s$n.json" > /dev/null); done
for n in 0 5; do (cd "$W/out" && PYTHONPATH="$W/s$n:$SIMS/literacy" $PY "$F/lit_real.py" "$W/s$n" "$W/data/lit-s$n" 60 "$W/out/lit-s$n.json" > "$W/out/lit-s$n.log"); done
for n in 4 5; do D="$W/data/state-s$n"; rm -rf "${D:?}"; mkdir -p "$D"
  (cd "$W/s$n" && export EDUX_DATA_DIR="$D" PYTHONPATH="$W/s$n"; $PY -m edux.cli load coursepacks/example-mini >/dev/null 2>&1; \
   $PY -m edux.cli seed-demo --reset >/dev/null; $PY "$HERE/demo_state.py" > "$W/out/demo_state_s$n.txt"); done
echo "outputs in $W/out"
