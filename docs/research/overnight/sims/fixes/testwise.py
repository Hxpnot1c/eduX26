"""A "testwise student" who knows no economics and no AI, and picks MCQ options by surface cues only.
Enumerates every multiple-choice question a code copy can build for the loaded pack (example-mini plus the
AI-literacy parts read in with it), by calling the copy's own plan functions, and reports the cue hit rates.

    EDUX_DATA_DIR=<fresh dir with the pack loaded> PYTHONPATH=<code copy> python testwise.py [--json out.json] [--list]

Question kinds enumerated (each distinct option set counts once):
  check        plan.check() on every point of every course part (prereq and review checks reuse these sets:
               prereq = point 1, review = points in rotation, same distractors)
  intuition    context_blocks.prequestion() for a new student focused on the part (needs >= mcq.min_distractors)
  how_ai_works plan.how_check() on the four ail_how_* parts
A step that is not an ask_mcq (the fixed copy's open-check fallback) counts as "no MCQ".

Cues (each also run alone):
  absolutes  drop options with absolute words (always, never, only, every, all, completely, ...), unless all have them
  punct      the option whose final punctuation differs from all the others (odd one out), if exactly one
  longest    the longest option (characters); shortest, the shortest (the old pack's keys were short fragments)
  hedge      the one option with a hedge word (can, may, usually, often, most, likely...), when the others have none
  similar    the option with most content-word overlap with the visible stem (the part's name; the intuition line
             for an intuition question); similar_desc uses name + description instead (an upper bound: the
             chatbot isn't shown the description with the question)
Length-rank cues (wave 6, w6-fix-length). Ties are exact: every ordering of tied options is averaged (n <= 4, so at
most 24), which matches gaming_sim's stable sort over shuffled letters:
  middle     drop the longest and the shortest option, guess among the rest (gaming_sim C2m)
  extremes   the anti-middle cue: guess between the longest and the shortest
  second_longest / second_shortest   the option one rank in from either end
  *_words    the same cues on word counts instead of characters
  *_jnd      a student who only sees a length difference above 10% (our choice): options within 10% of the
             longest count as "longest", within 10% of the shortest as "shortest"; middle = neither (guess all if empty)
Other cues:
  convergence  the option sharing the most content words with the other options (a classic test-wise strategy:
               distractors are often built as variations of the key)
  pair         the two options with the highest mutual word overlap (Jaccard >= 0.5, our choice), guess between them
               (mirror-image misconceptions: "the more inelastic, the more consumers bear" vs "... producers bear")
  odd_start    the one option whose first word differs when all the others share one
  pos_A / pos_last / pos_middle   always the first / last / a middle letter, averaged over 400 shuffles (student seeds)
  novel        sequence cue, reported separately: on point k >= 2 of a part, the option that was not in point k-1's
               check (the part's distractors repeat while the key changes). Not a length cue.
Item-writing checks (Haladyna, Downing & Rodriguez 2002 guidelines, from memory, not re-checked): key length rank,
max/min length ratio, key length / mean distractor length, options outside +-20% of the key, word-count spread.
Combined testwise: punct (if a unique odd one) -> absolutes -> hedge -> longest -> similar; ties split evenly (expected value).
When the server lets the chatbot write one extra option (extra_option), it is modelled as a full sentence with a
the server's distractors' most common ending, the median distractor length, no absolute words and no stem
overlap (our assumption; the fixed copy's text asks the chatbot for exactly this).
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import statistics
from dataclasses import dataclass

from edux import graph, learner, plan
from edux.context_blocks import Turn, prequestion

JND = 0.10   # our choice: a reader notices a length difference above 10%
from edux.settings import load_settings

ABSOLUTES = re.compile(r"\b(always|never|only|every|all|completely|altogether|entirely|must|none|nothing|"
                       r"everything|any|on purpose|whole|cannot|can't|single)\b", re.I)
HEDGES = re.compile(r"\b(can|could|may|might|usually|often|some|sometimes|most|tends?|probably|likely)\b", re.I)
STOP = set("a an the of to in on for and or is are be it its by with as at from that this than so if not no "
           "what why how when which do does did can will would has have had into up down more less".split())


def words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z%]+", t.lower()) if w not in STOP and len(w) > 2}


def end(t: str) -> str:
    t = t.strip()
    return t[-1] if t and not t[-1].isalnum() else "∅"


@dataclass
class Opt:
    text: str
    correct: bool
    synthetic: bool = False


def pick(opts: list[Opt], stem: str, cues: list[str], desc: str = "") -> float:
    """Expected score of a student who applies cues in order and guesses among what is left."""
    pool = list(opts)
    for cue in cues:
        if len(pool) == 1:
            break
        if cue == "absolutes":
            keep = [o for o in pool if not ABSOLUTES.search(o.text)]
            pool = keep or pool
        elif cue == "punct":
            ends = [end(o.text) for o in pool]
            odd = [o for o, e in zip(pool, ends) if ends.count(e) == 1]
            if len(odd) == 1 and len(pool) > 2:
                pool = odd
        elif cue == "hedge":   # the one option that hedges, when the others don't
            hedged = [o for o in pool if HEDGES.search(o.text)]
            if len(hedged) == 1 and len(pool) > 2:
                pool = hedged
        elif cue in ("longest", "shortest"):
            f = max if cue == "longest" else min
            m = f(len(o.text) for o in pool)
            pool = [o for o in pool if len(o.text) == m]
        elif cue in RANK_CUES:
            return rank_pick(pool, cue)
        elif cue == "convergence":
            score = {id(o): sum(len(words(o.text) & words(p.text)) for p in pool if p is not o) for o in pool}
            m = max(score.values())
            pool = [o for o in pool if score[id(o)] == m]
        elif cue == "pair":
            best, pair = 0.0, None
            for a, b in itertools.combinations(pool, 2):
                wa, wb = words(a.text), words(b.text)
                j = len(wa & wb) / max(1, len(wa | wb))
                if j > best:
                    best, pair = j, [a, b]
            if pair and best >= 0.5 and len(pool) > 2:
                pool = pair
        elif cue == "odd_start":
            firsts = [o.text.split()[0].lower() if o.text.split() else "" for o in pool]
            odd = [o for o, f in zip(pool, firsts) if firsts.count(f) == 1]
            if len(odd) == 1 and len(set(firsts)) == 2 and len(pool) > 2:
                pool = odd
        elif cue in ("similar", "similar_desc"):
            sw = words(stem if cue == "similar" else desc)
            score = {id(o): (len(words(o.text) & sw) / max(1, len(words(o.text)))) for o in pool}
            m = max(score.values())
            pool = [o for o in pool if score[id(o)] == m]
    return sum(o.correct for o in pool) / len(pool)


RANK_CUES = {f"{c}{u}" for c in ("middle", "extremes", "second_longest", "second_shortest")
             for u in ("", "_words", "_jnd")} | {"longest_words", "shortest_words", "longest_jnd", "shortest_jnd"}


def _len(o: Opt, unit: str) -> int:
    return len(o.text.split()) if unit == "_words" else len(o.text)


def rank_pick(pool: list[Opt], cue: str) -> float:
    """Expected score of a length-rank cue, averaged over every ordering of tied options (exact)."""
    unit = "_words" if cue.endswith("_words") else "_jnd" if cue.endswith("_jnd") else ""
    base = cue[: len(cue) - len(unit)] if unit else cue
    if unit == "_jnd":
        lens = [len(o.text) for o in pool]
        hi, lo = max(lens), min(lens)
        top = [o for o in pool if len(o.text) >= hi * (1 - JND)]
        bot = [o for o in pool if len(o.text) <= lo * (1 + JND)]
        chosen = {"longest": top, "shortest": bot,
                  "middle": [o for o in pool if o not in top and o not in bot] or pool,
                  "extremes": list({id(o): o for o in top + bot}.values())}.get(base, pool)
        return sum(o.correct for o in chosen) / len(chosen)
    total, n = 0.0, 0
    for order in itertools.permutations(pool):
        by = sorted(order, key=lambda o: _len(o, unit))   # stable: ties keep this ordering
        if base == "longest":
            chosen = [by[-1]]
        elif base == "shortest":
            chosen = [by[0]]
        elif base == "middle":
            chosen = by[1:-1] if len(by) > 2 else by
        elif base == "extremes":
            chosen = [by[0], by[-1]] if len(by) > 2 else by
        elif base == "second_longest":
            chosen = [by[-2]] if len(by) > 2 else by
        else:   # second_shortest
            chosen = [by[1]] if len(by) > 2 else by
        total += sum(o.correct for o in chosen) / len(chosen)
        n += 1
    return total / n


STRATS = {"absolutes": ["absolutes"], "punct": ["punct"], "hedge": ["hedge"], "longest": ["longest"],
          "shortest": ["shortest"], "similar": ["similar"], "similar_desc": ["similar_desc"],
          "testwise": ["punct", "absolutes", "hedge", "longest", "similar"],
          **{c: [c] for c in sorted(RANK_CUES)},
          "convergence": ["convergence"], "pair": ["pair"], "odd_start": ["odd_start"],
          "testwise_length": ["punct", "absolutes", "middle"]}
POSITION = ("pos_A", "pos_last", "pos_middle")
SHUFFLES = 400


def position_hits(q: dict) -> dict[str, float]:
    """Hit rates of letter-position strategies over SHUFFLES students, using the copy's own ask_mcq shuffle."""
    hits = {k: 0.0 for k in POSITION}
    for i in range(SHUFFLES):
        turn = Turn(student={"id": f"pos-{i}"}, parts=[q["part_id"]], message="", at="2026-11-19T10:00:00+00:00",
                    limits={}, resolution={})
        step = plan.ask_mcq(turn, q)
        letters = [letter for letter, o in step["mcq"]["options"].items()]
        key = next(letter for letter, o in step["mcq"]["options"].items() if o["id"] == "correct")
        hits["pos_A"] += key == letters[0]
        hits["pos_last"] += key == letters[-1]
        mid = letters[1:-1] if len(letters) > 2 else letters
        hits["pos_middle"] += (key in mid) / len(mid)
    return {k: v / SHUFFLES for k, v in hits.items()}


def item_checks(opts: list[Opt]) -> dict:
    """Item-writing checks on one option set (lengths after option_form)."""
    key = next(o for o in opts if o.correct)
    wrong = [o for o in opts if not o.correct and not o.synthetic]
    lens = [len(o.text) for o in opts if not o.synthetic]
    ranks = sorted(lens)
    lo_rank, hi_rank = ranks.index(len(key.text)), len(ranks) - 1 - ranks[::-1].index(len(key.text))
    wl = [len(o.text.split()) for o in opts if not o.synthetic]
    return {"key_len": len(key.text), "lens": lens,
            "key_rank": "tie" if lo_rank != hi_rank else ("shortest" if lo_rank == 0 else
                                                          "longest" if lo_rank == len(lens) - 1 else "middle"),
            "max_min_ratio": round(max(lens) / min(lens), 3),
            "key_vs_mean_wrong": round(len(key.text) / statistics.mean(len(o.text) for o in wrong), 3) if wrong else None,
            "outside_20pct_of_key": sum(abs(len(o.text) - len(key.text)) > 0.2 * len(key.text) for o in wrong),
            "word_spread": max(wl) - min(wl)}


def options_of(step: dict) -> list[Opt] | None:
    if step["move"] != "ask_mcq":
        return None
    q = step["question"]
    opts = [Opt(q["correct"], True)] + [Opt(w["text"], False) for w in q["wrong"]]
    if q["extra"]:   # the chatbot's option, in the form of the server's distractors (most common ending)
        med = int(statistics.median(len(w["text"]) for w in q["wrong"])) if q["wrong"] else 50
        ends = [end(w["text"]) for w in q["wrong"]] or ["."]
        tail = max(set(ends), key=ends.count)
        opts.append(Opt("x" * (med - (tail != "∅")) + (tail if tail != "∅" else ""), False, True))
    return opts


def enumerate_mcqs(settings) -> list[dict]:
    out, seen = [], set()
    student = {"id": "testwise-probe"}
    at = "2026-11-19T10:00:00+00:00"

    def add(kind, part, step, stem, index=1):
        opts = options_of(step) if step else None
        key = (part, kind, tuple(sorted(o.text for o in opts)) if opts else None)
        if key in seen:
            return
        seen.add(key)
        out.append({"kind": kind, "part": part, "stem": stem, "desc": f"{node['name']}. {node['description']}",
                    "mcq": opts is not None,
                    "options": [{"text": o.text, "correct": o.correct, "synthetic": o.synthetic} for o in opts or []],
                    "step_move": step["move"] if step else "none", "point_index": index,
                    "_q": step.get("question") if opts else None})

    ail = [n["id"] for n in graph._conn().execute("SELECT id FROM node WHERE id LIKE 'ail_how_%' AND level = 'part'")]
    for part in learner.all_parts() + [p for p in ail if p not in learner.all_parts()]:
        node = graph.get_node(part)
        turn = Turn(student=student, parts=[part], message="", at=at, limits={}, resolution={})
        stem = node["name"]   # visible stem: the part's name (the description is an upper bound, similar_desc)
        if part.startswith("ail_how_"):
            add("how_ai_works", part, plan.how_check(turn, part, settings), stem)
            continue
        if part.startswith("ail_"):
            continue
        if hasattr(plan, "mcq_points") and not plan.mcq_points(part):   # fixed copy: open checks only
            add("check", part, plan.open_check(turn, part)[-1], stem)
            continue
        for i in range(1, len(plan._points(part)) + 1):
            add("check", part, plan.check(turn, part, i, settings), stem, i)
        pq = prequestion(turn, settings)
        if pq and pq.get("correct"):
            step = plan.ask_mcq(turn, plan.question(part, "intuition", pq["correct"], settings), pq.get("source") or {})
            add("intuition", part, step, node.get("intuition") or stem)
    return out


def novel_hits(qs: list[dict]) -> dict[int, list[float]]:
    """The sequence cue: a part's point k check after its point k-1 check. The student picks among the options that
    were not in the previous set (guess among all if none is new). Keyed by id() of the point-k question."""
    out: dict[int, list[float]] = {}
    checks = {}
    for q in qs:
        if q["kind"] == "check" and q["mcq"]:
            checks.setdefault(q["part"], {})[q["point_index"]] = q
    for part, by in checks.items():
        for k in sorted(by):
            if k - 1 in by:
                before = {o["text"] for o in by[k - 1]["options"]}
                new = [o for o in by[k]["options"] if o["text"] not in before] or by[k]["options"]
                out.setdefault(id(by[k]), []).append(sum(o["correct"] for o in new) / len(new))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    settings = load_settings()
    qs = enumerate_mcqs(settings)
    for q in qs:
        if q["mcq"]:
            opts = [Opt(o["text"], o["correct"], o["synthetic"]) for o in q["options"]]
            q["chance"] = 1 / len(opts)
            q["hits"] = {s: pick(opts, q["stem"], c, q["desc"]) for s, c in STRATS.items()}
            q["hits"].update(position_hits(q.pop("_q")))
            q["items"] = item_checks(opts)
        else:
            q.pop("_q", None)
    novel = novel_hits(qs)
    groups = {"economics": [q for q in qs if q["kind"] != "how_ai_works"],
              "how_ai_works": [q for q in qs if q["kind"] == "how_ai_works"]}
    groups["all"] = qs
    summary = {}
    for g, items in groups.items():
        m = [q for q in items if q["mcq"]]
        row = {"questions": len(items), "mcqs": len(m), "open_fallback": len(items) - len(m)}
        if m:
            row["chance"] = round(statistics.mean(q["chance"] for q in m), 3)
            row.update({s: round(statistics.mean(q["hits"][s] for q in m), 3) for s in list(STRATS) + list(POSITION)})
            p1 = [q for q in m if q.get("point_index", 1) == 1]   # point-1 checks and intuition questions
            row["point1_sets"] = len(p1)
            row["point1_middle"] = round(statistics.mean(q["hits"]["middle"] for q in p1), 3)
            row["point1_longest"] = round(statistics.mean(q["hits"]["longest"] for q in p1), 3)
            row["point1_shortest"] = round(statistics.mean(q["hits"]["shortest"] for q in p1), 3)
            row["point1_chance"] = round(statistics.mean(q["chance"] for q in p1), 3)
            row["key_rank_counts"] = {r: sum(q["items"]["key_rank"] == r for q in m)
                                      for r in ("shortest", "middle", "longest", "tie")}
            row["max_min_ratio_mean"] = round(statistics.mean(q["items"]["max_min_ratio"] for q in m), 3)
            row["max_min_ratio_max"] = max(q["items"]["max_min_ratio"] for q in m)
            row["sets_with_option_outside_20pct_of_key"] = sum(q["items"]["outside_20pct_of_key"] > 0 for q in m)
            nv = [h for q in items for h in novel.get(id(q), [])]
            row["novel_sets"] = len(nv)
            if nv:
                row["novel"] = round(statistics.mean(nv), 3)
            row["correct_no_full_stop_rate"] = round(statistics.mean(
                end([o for o in q["options"] if o["correct"]][0]["text"]) != "." for q in m), 3)
            row["correct_longest_rate"] = round(statistics.mean(
                q["hits"]["longest"] == 1.0 for q in m), 3)
            row["sets_with_absolute_distractor"] = sum(
                any(ABSOLUTES.search(o["text"]) for o in q["options"] if not o["correct"]) for q in m)
            row["sets_with_absolute_correct"] = sum(
                any(ABSOLUTES.search(o["text"]) for o in q["options"] if o["correct"]) for q in m)
        summary[g] = row
    if args.list:
        for q in qs:
            print(f"\n[{q['kind']}] {q['part']}  stem: {q['stem'][:70]}")
            if not q["mcq"]:
                print(f"   no MCQ -> {q['step_move']}")
                continue
            for o in q["options"]:
                print(f"   {'*' if o['correct'] else ' '} ({len(o['text']):3d}) {'[chatbot writes]' if o['synthetic'] else o['text']}")
            print("   hits: " + ", ".join(f"{s}={v:.2f}" for s, v in q["hits"].items()) + f"  chance={q['chance']:.2f}")
            print(f"   items: {q['items']}")
    print(json.dumps(summary, indent=1))
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"summary": summary, "questions": qs}, f, indent=1)


if __name__ == "__main__":
    main()
