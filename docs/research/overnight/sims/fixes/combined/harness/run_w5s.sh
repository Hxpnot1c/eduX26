#!/usr/bin/env bash
# Wave-5 integration check (verifier S). Rebuilds s5 (export + 0001..0005) and s6..s10 (+ the renumbered 0006..0010, one
# at a time), runs check_mcp on each (one at a time, on a quiet machine), the Plan A takes (plus final_research and
# clean_ticks_ad), the wave-5 probes, the labels probe, and the gaming sims (s8 vs s9 vs s10). Everything lives under
# /tmp/claude-1000/w5-verifyS/ (copies, data dirs, outputs); nothing is written to the repo.
#   run_w5s.sh [export]      (default /tmp/claude-1000/edux-05e-ff)
# This is transcribed from the commands verifier S ran, step by step; it has not been run end to end as one script.
set -euo pipefail
SRC="${1:-/tmp/claude-1000/edux-05e-ff}"
W=/tmp/claude-1000/w5-verifyS
HERE="$(cd "$(dirname "$0")" && pwd)"; C="$(dirname "$HERE")"; SIMS="$(cd "$C/../.." && pwd)"; F="$SIMS/fixes"; G="$SIMS/gaming"
PY=/home/vishnu/edux26/.venv/bin/python
mkdir -p "$W/out" "$W/data" "$W/h" "$W/cap"
SERIES=("$C"/000[1-5]-*.diff "$C"/0006-w5-*.diff "$C"/0007-w5-*.diff "$C"/0008-w5-*.diff "$C"/0009-w5-*.diff "$C"/0010-w5-*.diff)
# 1. build s5..s10 (s5 = first 5 patches, sN = first N patches)
for n in 5 6 7 8 9 10; do
  rm -rf "${W:?}/s$n"; cp -r "$SRC" "$W/s$n"
  for p in "${SERIES[@]:0:$n}"; do (cd "$W/s$n" && patch -p1 -s --no-backup-if-mismatch < "$p"); done
done
# 2. check_mcp, one tree at a time (the 100 ms timing check fails under load; rerun once if only that fails)
sed 's#/tmp/claude-1000/w5-06g/#/tmp/claude-1000/w5-verifyS/#' "$G/check.sh" > "$W/h/check.sh"; chmod +x "$W/h/check.sh"
port=8931; for n in 5 6 7 8 9 10; do "$W/h/check.sh" "$W/s$n" $port "$W/out/check_s$n.txt"; port=$((port + 1)); tail -2 "$W/out/check_s$n.txt"; done
# 3. Plan A takes, with two extra scenarios (4c labelled research; dead link ticked a,d as 0007 says)
cp "$SIMS/demo-05e/run_episode.py" "$SIMS/demo-05e/scenarios.py" "$W/h/"
sed -i 's#/tmp/claude-1000/w3-07/#/tmp/claude-1000/w5-verifyS/#g' "$W/h/run_episode.py"
cat >> "$W/h/scenarios.py" <<'EOF'
SCENARIOS.update({
    "final_research": {"about": "final, but the chatbot labels the 4c verify answer request_type research",
                       "turns": [T1P, T2R, {**T3S, "labels": {**T3S["labels"], "request_type": "research"},
                                            "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "c", "d"]}},
                                 T4_M1, PROGRESS]},
    "clean_ticks_ad": {"about": "clean (dead page), sent as the verify answer with a,d ticked (0007's rule)",
                       "turns": [T1, T2C, {**T3C, "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "d"]}},
                                 T4_M2, PROGRESS]},
})
EOF
for n in 5 6 7 8 9 10; do (cd "$W/h" && $PY run_episode.py --code "$W/s$n" --label "s$n" --out "$W/cap" --port $((8960 + n)) \
  --scenario final final_ticks_ad clean plan_now then_ped recommended final_research clean_ticks_ad > "$W/out/episode_s$n.log"); done
$PY "$HERE/digest_q.py" "$W/cap" s5 s6 s7 s8 s9 s10 > "$W/out/planA_digest.txt"
# 4. wave-5 probes (stuck ladder, review requests) and the labels probe
for n in 5 6 8 10; do
  mkdir -p "$W/s$n/docs/research/overnight/sims/fixes"
  cp "$SIMS/edux_sim.py" "$W/s$n/docs/research/overnight/sims/"; cp "$F/probes_w5.py" "$W/s$n/docs/research/overnight/sims/fixes/"
  (cd "$W/s$n" && PYTHONPATH="$W/s$n" $PY docs/research/overnight/sims/fixes/probes_w5.py "$W/data/p5-s$n" --json "$W/out/probes_w5_s$n.json" > "$W/out/probes_w5_s$n.txt")
done
# 40-turn open-answer-only failer (stuck ladder x 0010): same probe with that run lengthened, stopping before part B
for n in 8 10; do
  f="$W/s$n/docs/research/overnight/sims/fixes/probes_w5_long.py"
  sed -e 's/"misses_open_only": stuck_run("a3", 20,/"misses_open_only": stuck_run("a3", 40,/' \
      -e 's/^    for condition, override in/    print("STOP"); return\n    for condition, override in/' \
      "$W/s$n/docs/research/overnight/sims/fixes/probes_w5.py" > "$f"
  (cd "$W/s$n" && PYTHONPATH="$W/s$n" $PY "$f" "$W/data/p5long-s$n" > "$W/out/probes_w5long_s$n.txt")
done
sed 's#/tmp/claude-1000/w5-fix-labels/data/probe#/tmp/claude-1000/w5-verifyS/data/labels-probe#' "$F/labels_probe.py" > "$W/h/labels_probe.py"
for n in 7 8 10; do (cd "$W/h" && PYTHONPATH="$W/s$n" $PY labels_probe.py "$W/s$n" --json "$W/out/labels_s$n.json" > "$W/out/labels_s$n.txt"); done
# 5. gaming sims (CPU heavy: run last). Results under $W/gres/<label>/
cp "$G/gaming_sim.py" "$G/summarise.py" "$W/h/"
sed -e 's#/tmp/claude-1000/w5-06g/#/tmp/claude-1000/w5-verifyS/#' -e 's#OUT="$HERE/results/$LABEL"#OUT="/tmp/claude-1000/w5-verifyS/gres/$LABEL"#' \
  "$G/run_variant.sh" > "$W/h/run_variant.sh"; chmod +x "$W/h/run_variant.sh"
for n in 8 9 10; do "$W/h/run_variant.sh" "$W/s$n" "s$n" 30 40; done
for n in 8 9 10; do ONLY="C0 L0" ONLY_SK="L1d" "$W/h/run_variant.sh" "$W/s$n" "s${n}_n100" 100 40; done
for d in "$W"/gres/*; do $PY "$W/h/summarise.py" "$d" > "$d/summary.md"; done
# 6. skip trees: s5 + the renumbered series minus one patch each, then check_mcp (rerun once on a chance shuffle clash)
port=8941; for skip in 0006 0007 0008 0009 0010; do
  d="$W/skip/no$skip"; rm -rf "${d:?}"; cp -r "$W/s5" "$d"
  for p in "$C"/00{06,07,08,09,10}-w5-*.diff; do case "$p" in *"/$skip-"*) continue;; esac; (cd "$d" && patch -p1 -s --no-backup-if-mismatch < "$p"); done
  "$W/h/check.sh" "$d" $port "$W/out/check_skip$skip.txt"; port=$((port + 1)); tail -2 "$W/out/check_skip$skip.txt"
done
# 7. asks_for_reviews through the real MCP server (s10, demo-showme)
D="$W/data/smoke"; rm -rf "${D:?}"; mkdir -p "$D"
( cd "$W/s10" && export EDUX_DATA_DIR="$D" PYTHONPATH="$W/s10"; $PY -m edux.cli load coursepacks/example-mini >/dev/null
  $PY -m edux.cli seed-demo --reset >/dev/null; $PY -m edux.cli serve --host 127.0.0.1 --port 8990 >"$D/server.log" 2>&1 & S=$!
  for i in $(seq 50); do curl -s -o /dev/null http://127.0.0.1:8990/ && break; sleep 0.2; done
  $PY "$F/label_smoke_w5.py" "$W/s10" http://127.0.0.1:8990/mcp; kill $S )
echo "outputs in $W/out and $W/gres"
