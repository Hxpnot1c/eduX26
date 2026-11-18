#!/usr/bin/env bash
# Rebuild the four w4-fix-mcq copies from the read-only 05e export: before, after (code), rows (code + pack rows),
# rows3 (rows + 3 options). Never touches the export or the repo.   mcq_make_copies.sh [export] [dest]
set -euo pipefail
SRC="${1:-/tmp/claude-1000/edux-05e-ff}"; DST="${2:-/tmp/claude-1000/w4-fix-mcq-rebuild}"
HERE="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$DST"; mkdir -p "$DST"; cd "$DST"
cp -r "$SRC" before; cp -r "$SRC" after
(cd after && patch -p1 -s < "$HERE/mcq-giveaway-code.diff")
cp -r after rows; (cd rows && patch -p1 -s < "$HERE/mcq-giveaway-pack.diff")
cp -r rows rows3; (cd rows3 && patch -p0 -s settings.toml < "$HERE/mcq-3-options-settings.diff")
echo "copies in $DST: before after rows rows3"
