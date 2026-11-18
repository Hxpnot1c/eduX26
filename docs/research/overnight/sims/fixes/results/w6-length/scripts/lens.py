import csv, sys
d = sys.argv[1] + "/coursepacks/example-mini/"
f = lambda t: t.strip().rstrip(".;!").rstrip()
mps = list(csv.DictReader(open(d + "mark_points.csv")))
mis = list(csv.DictReader(open(d + "misconceptions.csv")))
parts = []
for r in mps:
    if r["node_id"] not in parts: parts.append(r["node_id"])
for p in parts:
    ws = [f(m["wrong_idea"]) for m in mis if m["node_id"] == p]
    print(f"== {p}  distractors: " + "  ".join(f"{len(w)}c/{len(w.split())}w '{w.split()[0]}'" for w in ws))
    for r in sorted([r for r in mps if r["node_id"] == p], key=lambda r: r["order"]):
        k = f(r["point"]); L = sorted([len(k)] + [len(w) for w in ws]); W = sorted([len(k.split())] + [len(w.split()) for w in ws])
        rc = [i for i, x in enumerate(L) if x == len(k)]; rw = [i for i, x in enumerate(W) if x == len(k.split())]
        print(f"   key o{r['order']} {len(k)}c rank{rc}/{len(L)}  {len(k.split())}w rank{rw}  '{k.split()[0]}'  {k}")
