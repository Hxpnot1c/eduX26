"""Label-agreement analysis for the eduX Wednesday study (02a protocol). Stdlib only.

Extends agree.py from 02a Appendix C. Implements the analysis plan in 02a §1.4, §1.6 and §1.8.

Modes
  python analyse.py decisions.csv                 analyse a real results file (Wednesday)
  python analyse.py --dryrun [--write-csv F]      build proxy-vs-key decisions from the w5-02r JSON
                                                  and 02a Appendix B, then analyse them
  python analyse.py --synth F                     write a synthetic five-rater file (B, C, consensus,
                                                  bot1, bot2) made by flipping the key, for testing

decisions.csv columns: msg_id,label,unit,rater,value  (02a §1.8)
  label  ask_feature | answer_point | misconception | request_type | depth | engagement |
         asks_recent | source_conflict | choice
  unit   the decision inside a message (asks_sources, a, ped_formula_m2 ...), '-' for one-per-message
  rater  B, C, consensus, bot1, bot2 (or key, proxy for the dry run)
  value  0/1 (yes/no/true/false accepted) for binary labels, a category otherwise
Optional extra columns are ignored.

Scope (02a §1.2): ask_feature, asks_recent on R*; answer_point on V* (ticks a-d) and E* (points a-c);
source_conflict on V*; misconception on E* (one decision per candidate id listed in the item's
context); request_type, depth, engagement, choice on all 40. Rows outside the scope are dropped and
counted. Practice items (P*) are always dropped.
"""
import argparse, csv, json, math, os, random, re, sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OVERNIGHT = os.path.normpath(os.path.join(HERE, "..", ".."))
PROTOCOL = os.path.join(OVERNIGHT, "02a-label-agreement-protocol.md")
PROXY = os.path.join(OVERNIGHT, "work", "w5", "w5-02r-labels.md")

ORD = {"depth": ["surface", "mechanism", "transfer"],
       "engagement": ["passive", "active", "constructive"],
       "ask_score": ["0", "1", "2", "3", "4"],
       "verify_ticks": ["0", "1", "2", "3", "4"]}
BINARY = {"ask_feature", "answer_point", "misconception", "asks_recent", "source_conflict"}
NOMINAL = {"request_type", "choice"}
RARE = {"asks_recent", "source_conflict", "choice", "misconception"}
SCOPE = {"ask_feature": "R", "asks_recent": "R", "source_conflict": "V", "misconception": "E",
         "answer_point": "VE", "request_type": "RVEO", "depth": "RVEO", "engagement": "RVEO",
         "choice": "RVEO"}
FEATURES = ["concept", "context", "asks_sources", "asks_reasoning"]
CATS = {"request_type": ["concept", "research", "homework", "other"],
        "choice": ["try_first", "hint", "just_show_me", "skip_point", "none"],
        "depth": ORD["depth"], "engagement": ORD["engagement"]}
EXPECTED = {"ask_feature": 72, "answer_point": 56, "misconception": 12, "request_type": 40, "depth": 40,
            "engagement": 40, "asks_recent": 18, "source_conflict": 8, "choice": 40}
MISSING = {"", "na", "n/a", "-", "none_given", "missing"}
REPS = 2000


# ---------------------------------------------------------------- statistics
def kappa(a, b, order=None, weights=None):
    """Cohen's kappa; weighted if `weights` (index by position in `order`)."""
    cats = order or sorted(set(a) | set(b), key=str)
    n, k = len(a), len(cats)
    ix = {c: i for i, c in enumerate(cats)}
    w = weights or [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    po = sum(w[ix[x]][ix[y]] for x, y in zip(a, b)) / n
    pa = [sum(x == c for x in a) / n for c in cats]
    pb = [sum(y == c for y in b) / n for c in cats]
    pe = sum(w[i][j] * pa[i] * pb[j] for i in range(k) for j in range(k))
    return (po - pe) / (1 - pe) if pe < 1 - 1e-12 else float("nan")


def quad_weights(order):
    k = len(order)
    return [[1 - ((i - j) / (k - 1)) ** 2 for j in range(k)] for i in range(k)]


def ac1(a, b, cats=None):
    """Gwet's AC1 (nominal). `cats` = the label's full category set (q)."""
    cats = cats or sorted(set(a) | set(b), key=str)
    n, q = len(a), len(cats)
    po = sum(x == y for x, y in zip(a, b)) / n
    if q < 2:
        return float("nan")
    pi = [(sum(x == c for x in a) + sum(y == c for y in b)) / (2 * n) for c in cats]
    pe = sum(p * (1 - p) for p in pi) / (q - 1)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def stat(rows, r1, r2, label):
    a = [r[r1] for r in rows]; b = [r[r2] for r in rows]
    if label in ORD:
        return kappa(a, b, ORD[label], quad_weights(ORD[label]))
    return kappa(a, b)


def cluster_boot(rows, r1, r2, label, reps=None, seed=1):
    """Percentile CI from resampling whole messages. Returns (lo, hi, n_nan_dropped)."""
    reps = reps or REPS
    by_msg = defaultdict(list)
    for r in rows:
        by_msg[r["msg"]].append(r)
    msgs = list(by_msg); rng = random.Random(seed); vals = []; dropped = 0
    for _ in range(reps):
        sample = [r for m in (rng.choice(msgs) for _ in msgs) for r in by_msg[m]]
        v = stat(sample, r1, r2, label)
        if v == v:
            vals.append(v)
        else:
            dropped += 1
    if len(vals) < 50:
        return float("nan"), float("nan"), dropped
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1], dropped


def kripp_alpha(units, metric="nominal", order=None):
    """Krippendorff's alpha. units: list of lists of values (missing values left out)."""
    pairs = Counter()
    for vals in units:
        m = len(vals)
        if m < 2:
            continue
        for i in range(m):
            for j in range(m):
                if i != j:
                    pairs[(vals[i], vals[j])] += 1 / (m - 1)
    if not pairs:
        return float("nan")
    cats = order or sorted({c for p in pairs for c in p}, key=str)
    nc = {c: sum(v for (x, _), v in pairs.items() if x == c) for c in cats}
    n = sum(nc.values())

    def delta(c, k):
        if c == k:
            return 0.0
        if metric == "nominal":
            return 1.0
        i, j = sorted((cats.index(c), cats.index(k)))
        s = sum(nc[cats[g]] for g in range(i, j + 1)) - (nc[c] + nc[k]) / 2
        return s * s
    do = sum(v * delta(c, k) for (c, k), v in pairs.items())
    de = sum(nc[c] * nc[k] * delta(c, k) for c in cats for k in cats) / (n - 1)
    return 1 - do / de if de > 0 else float("nan")


def fisher_greater(a, b, c, d):
    """One-sided Fisher exact p for a 2x2 [[a,b],[c,d]]: P(X >= a)."""
    r1, c1, n = a + b, a + c, a + b + c + d
    def h(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    return sum(h(x) for x in range(a, min(r1, c1) + 1))


def f2(x):
    return "n/a" if x != x else f"{x:.2f}"


# ---------------------------------------------------------------- loading
def norm_value(label, v):
    """Normalised value, or None for a missing cell (blank / NA): missing is never read as 0."""
    lv = v.strip().lower().rstrip("*")
    if lv in MISSING and not (label == "choice" and lv == "-"):
        return None
    if label in BINARY:
        if lv in ("1", "yes", "true", "y"):
            return "1"
        if lv in ("0", "no", "false", "n"):
            return "0"
        raise ValueError(f"bad binary value {v!r} for {label}")
    if label in CATS and lv not in CATS[label]:
        raise ValueError(f"bad value {v!r} for {label}; allowed: {', '.join(CATS[label])}")
    return lv


def load(path, fill=True):
    """Read decisions.csv. Returns (table, dropped, notes). Blank/NA values are counted as missing, not 0.
    fill=True applies the two Wednesday rules (printed in the report):
      1. consensus = B where B == C and no consensus row was entered (only B-C disagreements are adjudicated);
      2. a bot rater that labelled an R item as non-research sent no features: its missing ask_feature and
         asks_recent rows for that item are scored 0 (what the server records)."""
    table = defaultdict(dict); dropped = Counter(); missing = Counter(); notes = []
    with open(path, newline="") as fh:
        for i, r in enumerate(csv.DictReader(fh), 2):
            lab, msg, rater = r["label"].strip(), r["msg_id"].strip(), r["rater"].strip()
            if msg[:1] not in SCOPE.get(lab, ""):
                dropped[(lab, msg[:1])] += 1
                continue
            try:
                v = norm_value(lab, r["value"])
            except ValueError as e:
                sys.exit(f"{path} line {i}: msg {msg}, label {lab}, rater {rater}: {e}")
            if v is None:
                missing[(lab, rater)] += 1
                continue
            table[(lab, msg, r["unit"].strip())][rater] = v
    if missing:
        notes.append("Missing values (blank/NA, left out, NOT scored 0): "
                     + ", ".join(f"{l}/{r}: {n}" for (l, r), n in sorted(missing.items())))
    if fill:
        n = 0
        for v in table.values():
            if "B" in v and "C" in v and v["B"] == v["C"] and "consensus" not in v:
                v["consensus"] = v["B"]; n += 1
        if n:
            notes.append(f"Filled consensus = B on {n} decisions where B == C and no consensus row existed.")
        raters = {rt for v in table.values() for rt in v}
        units = defaultdict(set)
        for (lab, msg, unit) in table:
            if lab in ("ask_feature", "asks_recent"):
                units[lab].add(unit)
        units["ask_feature"] |= set(FEATURES); units["asks_recent"] = {"-"}
        filled = Counter()
        for (lab, msg, unit), v in list(table.items()):
            if lab != "request_type":
                continue
            for rt, val in v.items():
                if rt.startswith("bot") and msg.startswith("R") and val != "research":
                    for flab in ("ask_feature", "asks_recent"):
                        for u in units[flab]:
                            cell = table[(flab, msg, u)]
                            if rt not in cell:
                                cell[rt] = "0"; filled[rt] += 1
        if filled:
            notes.append("Bot said non-research on an R item; its missing feature/asks_recent rows were scored 0: "
                         + ", ".join(f"{r}: {n}" for r, n in sorted(filled.items())))
    return table, dropped, notes


def flow(table):
    """Decisions per label and rater vs the protocol's expected n (STARD-style flow)."""
    raters = sorted({rt for v in table.values() for rt in v})
    print("## Flow: decisions per label and rater (expected n from 02a)\n")
    print("| Label | expected | " + " | ".join(raters) + " |")
    print("|---|---|" + "---|" * len(raters))
    for lab, exp in EXPECTED.items():
        cnt = Counter(rt for k, v in table.items() if k[0] == lab for rt in v)
        cells = [f"{cnt[r]}" + ("" if cnt[r] == exp else " **!**") for r in raters]
        print(f"| {lab} | {exp} | " + " | ".join(cells) + " |")
    print("\n**!** = not the expected count: find out why before reading the agreement tables.\n")


def derived(table, raters):
    """Server-level outcomes (02a Table 5): Ask score 0-4 per R message, Verify tick count per V answer."""
    out = defaultdict(dict)
    for lab, src, pref, nunits in (("ask_score", "ask_feature", "R", 4), ("verify_ticks", "answer_point", "V", 4)):
        per = defaultdict(lambda: defaultdict(list))
        for (l, m, u), v in table.items():
            if l == src and m.startswith(pref):
                for rt, val in v.items():
                    per[m][rt].append(val)
        for m, d in per.items():
            for rt, vals in d.items():
                if len(vals) == nunits:
                    out[(lab, m, "-")][rt] = str(sum(int(x) for x in vals))
    return out


# ---------------------------------------------------------------- reporting
def rows_for(table, lab, r1, r2, msg_prefix=None, unit=None):
    return [{"msg": k[1], "unit": k[2], r1: v[r1], r2: v[r2]} for k, v in sorted(table.items())
            if k[0] == lab and r1 in v and r2 in v
            and (msg_prefix is None or k[1][:1] in msg_prefix) and (unit is None or k[2] == unit)]


def binary_row(rows, r1, r2, lab, boot=True):
    n = len(rows); msgs = len({r["msg"] for r in rows})
    a = [r[r1] for r in rows]; b = [r[r2] for r in rows]
    pct = sum(x == y for x, y in zip(a, b)) / n
    k = kappa(a, b)
    lo, hi, nan = cluster_boot(rows, r1, r2, lab) if boot else (float("nan"),) * 2 + (0,)
    tp = sum(x == "1" and y == "1" for x, y in zip(a, b)); fn = sum(x == "0" and y == "1" for x, y in zip(a, b))
    tn = sum(x == "0" and y == "0" for x, y in zip(a, b)); fp = sum(x == "1" and y == "0" for x, y in zip(a, b))
    sens = tp / (tp + fn) if tp + fn else float("nan"); spec = tn / (tn + fp) if tn + fp else float("nan")
    prev = (tp + fn) / n
    return dict(n=n, msgs=msgs, prev=prev, pct=pct, k=k, lo=lo, hi=hi, nan=nan, ac1=ac1(a, b, ["0", "1"]),
                sens=sens, spec=spec, tp=tp, fp=fp, fn=fn, tn=tn)


def confusion(rows, r1, r2, cats):
    print(f"\nConfusion ({r1} rows x {r2} columns):\n")
    print("| " + r1 + " \\ " + r2 + " | " + " | ".join(cats) + " |")
    print("|---" * (len(cats) + 1) + "|")
    for c in cats:
        print(f"| {c} | " + " | ".join(str(sum(r[r1] == c and r[r2] == k for r in rows)) for k in cats) + " |")


def report(table, pairs, ask_mins=(2, 3), quiet_units=False):
    raters = {rt for v in table.values() for rt in v}
    pairs = [p for p in pairs if p[0] in raters and p[1] in raters]
    if not pairs:
        sys.exit(f"no rater pairs available; raters in file: {sorted(raters)}")
    if raters <= {"key", "proxy"}:
        print("> **WARNING: raters are `key` and `proxy`. Both were produced by a Claude model. This is a pipeline\n"
              "> dry run and a rubric-ambiguity audit, NOT agreement evidence. Do not quote these numbers as results.**\n")
    print(f"Raters found: {', '.join(sorted(raters))}. Pairs: {', '.join(a + '-' + b for a, b in pairs)}. "
          f"Cluster bootstrap: {REPS} resamples over messages, seed 1. Sensitivity/specificity: first rater = test, "
          f"second = reference.\n")

    # Table 2: headline pooled binary
    print("## Headline binary decisions (pooled within skill)\n")
    print("| Skill | Pair | Decisions (msgs) | Prev. (ref) | % agree | kappa [95% CI] | NaN resamples | AC1 | Sens | Spec | TP/FP/FN/TN |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    groups = [("Ask features (pooled)", "ask_feature", None), ("Answer scoring (pooled)", "answer_point", None),
              ("of which Verify ticks", "answer_point", "V"), ("of which explain-back points", "answer_point", "E")]
    results = {}
    for name, lab, pref in groups:
        for r1, r2 in pairs:
            rows = rows_for(table, lab, r1, r2, pref)
            if len(rows) < 5:
                continue
            s = binary_row(rows, r1, r2, lab); results[(name, r1, r2)] = s
            print(f"| {name} | {r1}-{r2} | {s['n']} ({s['msgs']}) | {s['prev']:.2f} | {s['pct']:.2f} | "
                  f"{f2(s['k'])} [{f2(s['lo'])}, {f2(s['hi'])}] | {s['nan']} | {f2(s['ac1'])} | {f2(s['sens'])} | "
                  f"{f2(s['spec'])} | {s['tp']}/{s['fp']}/{s['fn']}/{s['tn']} |")

    # Verdict (02a §1.6) only when the human data exist
    if {"B", "C", "consensus", "bot1"} <= raters:
        print("\n## Verdict (02a §1.6)\n")
        for name in ("Ask features (pooled)", "Answer scoring (pooled)"):
            bc = results.get((name, "B", "C")); bot = results.get((name, "bot1", "consensus"))
            bb = results.get((name, "bot1", "B")); bcc = results.get((name, "bot1", "C"))
            if not (bc and bot and bb and bcc):
                continue
            mean_bot = (bb["k"] + bcc["k"]) / 2
            if bc["k"] < 0.60:
                v = f"CEILING FAILS (B-C kappa {f2(bc['k'])} < .60): the definition fails; do not report bot kappa as a bot result"
            elif bot["k"] >= 0.60 and bot["lo"] >= 0.40 and mean_bot >= bc["k"] - 0.10:
                v = "STRONG" if bot["k"] >= 0.80 else "PASS"
            else:
                v = "FAIL"
            guard = " ; SPECIFICITY FLAG (bot spec < .80)" if bot["spec"] < 0.80 else ""
            print(f"- {name}: {v}{guard}. bot-consensus kappa {f2(bot['k'])} (lower {f2(bot['lo'])}); "
                  f"mean(bot-B, bot-C) {f2(mean_bot)} vs B-C {f2(bc['k'])}.")

    # Per-unit descriptive
    if not quiet_units:
        print("\n## Per feature / tick / point (descriptive only; n is tiny)\n")
        print("| Label | Unit | Msgs | Pair | Agree | Disagree | % agree | kappa | AC1 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for lab, pref, units in (("ask_feature", "R", FEATURES), ("answer_point", "V", list("abcd")),
                                 ("answer_point", "E", list("abc"))):
            for u in units:
                for r1, r2 in pairs:
                    rows = rows_for(table, lab, r1, r2, pref, u)
                    if not rows:
                        continue
                    s = binary_row(rows, r1, r2, lab, boot=False)
                    print(f"| {lab} | {pref}:{u} | {s['n']} | {r1}-{r2} | {s['tp'] + s['tn']} | {s['fp'] + s['fn']} | "
                          f"{s['pct']:.2f} | {f2(s['k'])} | {f2(s['ac1'])} |")

    # Table 3: secondary nominal/ordinal
    print("\n## Secondary labels (nominal and ordinal)\n")
    print("| Label | Pair | n (msgs) | % agree | kappa (unweighted) | weighted kappa (quadratic) [95% CI] | AC1 |")
    print("|---|---|---|---|---|---|---|")
    for lab in ("request_type", "depth", "engagement"):
        for r1, r2 in pairs:
            rows = rows_for(table, lab, r1, r2)
            if len(rows) < 5:
                continue
            a = [r[r1] for r in rows]; b = [r[r2] for r in rows]
            pct = sum(x == y for x, y in zip(a, b)) / len(rows)
            lo, hi, nan = cluster_boot(rows, r1, r2, lab)
            uw = kappa(a, b)
            wk = f"{f2(stat(rows, r1, r2, lab))} [{f2(lo)}, {f2(hi)}]" if lab in ORD else "-"
            ci = "" if lab in ORD else f" [{f2(lo)}, {f2(hi)}]"
            cats = CATS[lab]
            print(f"| {lab} | {r1}-{r2} | {len(rows)} | {pct:.2f} | {f2(uw)}{ci} | {wk} | {f2(ac1(a, b, cats))} |")
    for lab in ("request_type", "depth", "engagement"):
        r1, r2 = pairs[0] if ("bot1", "consensus") not in pairs else ("bot1", "consensus")
        rows = rows_for(table, lab, r1, r2)
        if rows:
            print(f"\n**{lab}**", end="")
            cats = ORD.get(lab) or sorted({r[r1] for r in rows} | {r[r2] for r in rows})
            confusion(rows, r1, r2, cats)

    # Multi-rater alpha
    multi = [r for r in ("B", "C", "bot1") if r in raters]
    if len(multi) < 2:
        multi = sorted(raters)[:2]
    print(f"\n## Krippendorff's alpha across raters {', '.join(multi)}\n")
    print("| Label | Metric | Units | alpha |")
    print("|---|---|---|---|")
    for lab in ("ask_feature", "answer_point", "request_type", "depth", "engagement"):
        units = [[v[r] for r in multi if r in v] for k, v in table.items() if k[0] == lab]
        metric = "ordinal" if lab in ORD else "nominal"
        print(f"| {lab} | {metric} | {len(units)} | {f2(kripp_alpha(units, metric, ORD.get(lab)))} |")

    # Table 4 rare labels
    print("\n## Rare labels (counts and % agreement; kappa unstable)\n")
    print("| Label | Pair | n | ref positives | test positives | agree | disagree | % agree | AC1 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for lab in ("asks_recent", "source_conflict", "misconception", "choice"):
        for r1, r2 in pairs:
            rows = rows_for(table, lab, r1, r2)
            if not rows:
                continue
            a = [r[r1] for r in rows]; b = [r[r2] for r in rows]
            if lab == "choice":
                pos_t = sum(x != "none" for x in a); pos_r = sum(y != "none" for y in b)
                cats = CATS["choice"]
            else:
                pos_t = a.count("1"); pos_r = b.count("1"); cats = ["0", "1"]
            agree = sum(x == y for x, y in zip(a, b))
            print(f"| {lab} | {r1}-{r2} | {len(rows)} | {pos_r} | {pos_t} | {agree} | {len(rows) - agree} | "
                  f"{agree / len(rows):.2f} | {f2(ac1(a, b, cats))} |")

    # Table 5 server-level
    der = derived(table, raters)
    print("\n## Server-level outcome (02a Table 5)\n")
    print("| Outcome | Pair | Msgs | exact % | weighted kappa (quadratic) [95% CI] | same side of threshold |")
    print("|---|---|---|---|---|---|")
    for lab in ("ask_score", "verify_ticks"):
        for r1, r2 in pairs:
            rows = rows_for(der, lab, r1, r2)
            if len(rows) < 5:
                continue
            exact = sum(r[r1] == r[r2] for r in rows) / len(rows)
            lo, hi, _ = cluster_boot(rows, r1, r2, lab)
            if lab == "ask_score":
                side = "; ".join(f">= {t}: {sum((int(r[r1]) >= t) == (int(r[r2]) >= t) for r in rows)}/{len(rows)}" for t in ask_mins)
            else:
                side = "-"
            print(f"| {lab} | {r1}-{r2} | {len(rows)} | {exact:.2f} | {f2(stat(rows, r1, r2, lab))} [{f2(lo)}, {f2(hi)}] | {side} |")
    return results


def disagreements(table, r1, r2):
    out = []
    for (lab, msg, unit), v in sorted(table.items()):
        if r1 in v and r2 in v and v[r1] != v[r2]:
            out.append((lab, msg, unit, v[r1], v[r2]))
    return out


# ---------------------------------------------------------------- dry run builder
def md_block(text, after, lang):
    i = text.index(after)
    m = re.search(r"```" + lang + r"\n(.*?)\n```", text[i:], re.S)
    return m.group(1)


# Key notes ('*' in the notes column) that point at a specific decision, hand-mapped from Appendix B.
KEY_NOTE_FLAGS = {("R03", "ask_feature", "concept"), ("R10", "ask_feature", "concept"),
                  ("R16", "ask_feature", "concept"), ("V02", "answer_point", "c"), ("V02", "answer_point", "d"),
                  ("V04", "answer_point", "a"), ("V06", "answer_point", "a"), ("E06", "answer_point", "c"),
                  ("E07", "answer_point", "c")}
FEAT = {"C": "concept", "X": "context", "S": "asks_sources", "R": "asks_reasoning"}
PROXY_FIELD = {"ask_feature": "question_features", "asks_recent": "asks_recent", "source_conflict": "source_conflict",
               "request_type": "request_type", "depth": "question_depth", "engagement": "engagement",
               "choice": "choice", "answer_point": "points_met", "misconception": "misconception_ids"}


def build_dryrun(protocol=PROTOCOL, proxy=PROXY):
    """Returns (rows, meta). rows: dicts msg_id,label,unit,rater,value. meta[(label,msg,unit)]: flags."""
    ptxt = open(protocol).read()
    msgs = list(csv.DictReader(md_block(ptxt, "## Appendix A", "csv").splitlines()))
    key = {r["msg_id"]: r for r in csv.DictReader(md_block(ptxt, "## Appendix B", "csv").splitlines())}
    prox = {it["msg_id"]: it for it in json.loads(md_block(open(proxy).read(), "## Labels (JSON)", "json"))["items"]}
    rows, meta = [], {}

    def add(lab, msg, unit, kval, pval, kstar, pfield, pobj):
        star = kstar or (msg, lab, unit) in KEY_NOTE_FLAGS
        meta[(lab, msg, unit)] = {"key_borderline": star, "proxy_unsure": pobj[pfield]["conf"] == "unsure",
                                  "proxy_why": pobj[pfield].get("ambiguous_words", []),
                                  "proxy_note": prox[msg].get("note") or (prox[msg].get("answer") or {}).get("points_note"),
                                  "key_note": key[msg]["notes"]}
        rows.append(dict(msg_id=msg, label=lab, unit=unit, rater="key", value=kval))
        rows.append(dict(msg_id=msg, label=lab, unit=unit, rater="proxy", value=pval))

    for m in msgs:
        mid = m["msg_id"]
        if mid.startswith("P"):
            continue
        k, p = key[mid], prox[mid]
        tm = p["this_message"]
        for lab, col in (("request_type", "request_type"), ("depth", "question_depth"),
                         ("engagement", "engagement"), ("choice", "choice")):
            add(lab, mid, "-", k[col].rstrip("*"), str(tm[PROXY_FIELD[lab]]["value"]), k[col].endswith("*"),
                PROXY_FIELD[lab], tm)
        if mid.startswith("R"):
            kf = {FEAT[x] for x in k["features"].split(";") if x}
            pf = set(tm["question_features"]["value"])
            for f in FEATURES:
                add("ask_feature", mid, f, str(int(f in kf)), str(int(f in pf)), False, "question_features", tm)
            add("asks_recent", mid, "-", norm_value("asks_recent", k["asks_recent"]),
                str(int(bool(tm["asks_recent"]["value"]))), k["asks_recent"].endswith("*"), "asks_recent", tm)
        if mid.startswith("V"):
            add("source_conflict", mid, "-", norm_value("source_conflict", k["source_conflict"]),
                str(int(bool(tm["source_conflict"]["value"]))), False, "source_conflict", tm)
        if mid[0] in "VE":
            ans = p["answer"]
            kp = set(filter(None, k["points_met"].split(";"))); pp = set(ans["points_met"]["value"])
            for u in ("abcd" if mid[0] == "V" else "abc"):
                add("answer_point", mid, u, str(int(u in kp)), str(int(u in pp)), False, "points_met", ans)
        if mid.startswith("E"):
            ans = p["answer"]
            cands = re.findall(r"(\w+_m\d+)\s*=", m["context"])
            km = set(filter(None, k["misconception_ids"].split(";"))); pm = set(ans["misconception_ids"]["value"])
            for c in cands:
                add("misconception", mid, c, str(int(c in km)), str(int(c in pm)), False, "misconception_ids", ans)
            extra = (km | pm) - set(cands)
            if extra:
                print(f"note: {mid} labels outside the candidate list: {sorted(extra)}", file=sys.stderr)
    return rows, meta


def flag_analysis(table, meta, flag):
    """Disagreement rate by flag, at decision level and item-field level."""
    dec = Counter(); fld = defaultdict(lambda: [False, False])
    for key, v in table.items():
        if key not in meta:
            continue
        f = meta[key][flag]; dis = v["key"] != v["proxy"]
        dec[(f, dis)] += 1
        fk = (key[0], key[1]); fld[fk][0] |= f; fld[fk][1] |= dis
    fc = Counter((f, d) for f, d in fld.values())
    print(f"\n### Disagreement by `{flag}`\n")
    print("| Level | flagged: disagree / total | not flagged: disagree / total | one-sided Fisher p (flagged disagree more) |")
    print("|---|---|---|---|")
    for name, c in (("decision", dec), ("item-field", fc)):
        a, b = c[(True, True)], c[(True, False)]; cc, d = c[(False, True)], c[(False, False)]
        rate = lambda x, y: f"{x}/{x + y} ({x / (x + y):.0%})" if x + y else "0/0"
        print(f"| {name} | {rate(a, b)} | {rate(cc, d)} | {fisher_greater(a, b, cc, d):.3f} |")


def run_dryrun(write_csv=None):
    rows, meta = build_dryrun()
    path = write_csv or "/tmp/claude-1000/w5-02s/dryrun_decisions.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["msg_id", "label", "unit", "rater", "value"]); w.writeheader(); w.writerows(rows)
    print(f"# Dry run: proxy (w5-02r) vs key (02a Appendix B)\n\nDecisions written to `{path}`.\n")
    table, dropped, notes = load(path, fill=False)
    flow(table)
    report(table, [("proxy", "key")])
    print("\n## Unsure / borderline flags vs disagreement\n")
    print("The proxy's `conf` is per field, so one `question_features` unsure flag covers 4 decisions. "
          "Item-field level counts each (label, message) once.")
    flag_analysis(table, meta, "proxy_unsure")
    flag_analysis(table, meta, "key_borderline")
    print("\n## Every disagreement (proxy vs key)\n")
    print("| # | Label | Msg | Unit | Key | Proxy | Key `*` | Proxy unsure | Proxy note |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, (lab, msg, unit, pv, kv) in enumerate(disagreements(table, "proxy", "key"), 1):
        m = meta[(lab, msg, unit)]
        note = (m["proxy_note"] or "").replace("|", "/")
        print(f"| {i} | {lab} | {msg} | {unit} | {kv} | {pv} | {'yes' if m['key_borderline'] else ''} | "
              f"{'yes' if m['proxy_unsure'] else ''} | {note} |")


# ---------------------------------------------------------------- synthetic five-rater test file
def synth(path, seed=7):
    rows, _ = build_dryrun()
    rng = random.Random(seed)
    cats = defaultdict(set)
    for r in rows:
        cats[r["label"]].add(r["value"])
    out = []
    for r in rows:
        if r["rater"] != "key":
            continue
        base = r["value"]
        def flip(p):
            if rng.random() >= p:
                return base
            others = sorted(cats[r["label"]] - {base})
            return rng.choice(others) if others else base
        cons = flip(0.03)  # consensus = key with a few changes
        for rater, p in (("B", 0.10), ("C", 0.10), ("bot1", 0.15), ("bot2", 0.15)):
            if rng.random() < p:
                v = rng.choice(sorted(cats[r["label"]] - {cons}) or [cons])
            else:
                v = cons
            out.append({**r, "rater": rater, "value": v})
        out.append({**r, "rater": "consensus", "value": cons})
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["msg_id", "label", "unit", "rater", "value"]); w.writeheader(); w.writerows(out)
    print(f"wrote {len(out)} synthetic rows to {path} (raters B, C, consensus, bot1, bot2; NOT data)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--dryrun", action="store_true")
    ap.add_argument("--write-csv")
    ap.add_argument("--synth")
    ap.add_argument("--pairs", default="B-C,bot1-consensus,bot1-B,bot1-C,bot1-bot2",
                    help="comma list of test-reference pairs (default: the protocol's)")
    ap.add_argument("--ask-min", default="2,3", help="ask_min_features thresholds for Table 5")
    ap.add_argument("--reps", type=int, default=REPS)
    a = ap.parse_args()
    globals()["REPS"] = a.reps
    if a.synth:
        return synth(a.synth)
    if a.dryrun:
        return run_dryrun(a.write_csv)
    if not a.csv:
        ap.error("give decisions.csv, --dryrun or --synth")
    table, dropped, notes = load(a.csv)
    if dropped:
        print(f"Dropped rows outside the protocol scope: {dict(dropped)}\n")
    for n in notes:
        print(f"- {n}")
    print()
    flow(table)
    pairs = [tuple(p.split("-", 1)) for p in a.pairs.split(",")]
    report(table, pairs, tuple(int(x) for x in a.ask_min.split(",")))
    for r1, r2 in pairs[:2]:
        d = disagreements(table, r1, r2)
        if d:
            print(f"\n## Disagreements {r1} vs {r2} ({len(d)})\n")
            for lab, msg, unit, x, y in d:
                print(f"- {msg} {lab} {unit}: {r1}={x}, {r2}={y}")


if __name__ == "__main__":
    main()
