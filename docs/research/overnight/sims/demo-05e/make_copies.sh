#!/usr/bin/env bash
# Rebuild the three code copies used by run_episode.py from the read-only 05e export (never edits the export or repo).
#   make_copies.sh [export dir]   default /tmp/claude-1000/edux-05e
set -euo pipefail
SRC="${1:-/tmp/claude-1000/edux-05e}"
DST=/tmp/claude-1000/w3-07
mkdir -p "$DST"; cd "$DST"
rm -rf branch w2 rewrite
cp -r "$SRC" branch
cp -r "$SRC" w2
python3 - w2/settings.toml <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
for old, new in [("ask_min_features = 2 ", "ask_min_features = 3 "),
                 ("ail_question = { slip = 0.15, guess = 0.20 }", "ail_question = { slip = 0.15, guess = 0.30 }"),
                 ("ail_unprompted = { slip = 0.05, guess = 0.10 }", "ail_unprompted = { slip = 0.05, guess = 0.20 }")]:
    assert old in s, old
    s = s.replace(old, new)
open(p, "w").write(s)
PY
cp -r w2 rewrite
python3 - rewrite/ingest/ai_literacy <<'PY'
# PLACEHOLDER wording for a test only (w3-07): the fabrication set without m2, after 02's content table. Not a proposal.
import csv, sys, os
d = sys.argv[1]
def edit(name, key, change):
    rows = list(csv.DictReader(open(os.path.join(d, name)))); fields = rows[0].keys()
    for r in rows:
        if r["id"] in change: change[r["id"]](r)
    w = csv.DictWriter(open(os.path.join(d, name), "w", newline=""), fieldnames=fields); w.writeheader(); w.writerows(rows)
edit("mark_points.csv", "id", {"ail_how_fabrication_p1": lambda r: r.update(point="A cited source might not exist, or might not say what was claimed")})
new = {"ail_how_fabrication_m1": ("A reference naming a publisher and a date is probably a real one", "A real-looking reference can still be made up or misquoted: open it and check."),
       "ail_how_fabrication_m2": ("It probably copied a page that was later deleted from the internet", "More likely it wrote text that looked like a source; either way, check it."),
       "ail_how_fabrication_m3": ("If a link opens, the page probably backs up what the chatbot said", "A page can open and still not say what was claimed: read what it says.")}
edit("misconceptions.csv", "id", {k: (lambda v: lambda r: r.update(wrong_idea=v[0], correction=v[1]))(v) for k, v in new.items()})
PY
echo "copies ready in $DST: branch w2 rewrite"
