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
Combined testwise: punct (if a unique odd one) -> absolutes -> hedge -> longest -> similar; ties split evenly (expected value).
When the server lets the chatbot write one extra option (extra_option), it is modelled as a full sentence with a
the server's distractors' most common ending, the median distractor length, no absolute words and no stem
overlap (our assumption; the fixed copy's text asks the chatbot for exactly this).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from dataclasses import dataclass

from edux import graph, learner, plan
from edux.context_blocks import Turn, prequestion
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
        elif cue in ("similar", "similar_desc"):
            sw = words(stem if cue == "similar" else desc)
            score = {id(o): (len(words(o.text) & sw) / max(1, len(words(o.text)))) for o in pool}
            m = max(score.values())
            pool = [o for o in pool if score[id(o)] == m]
    return sum(o.correct for o in pool) / len(pool)


STRATS = {"absolutes": ["absolutes"], "punct": ["punct"], "hedge": ["hedge"], "longest": ["longest"],
          "shortest": ["shortest"], "similar": ["similar"], "similar_desc": ["similar_desc"],
          "testwise": ["punct", "absolutes", "hedge", "longest", "similar"]}


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

    def add(kind, part, step, stem):
        opts = options_of(step) if step else None
        key = (part, kind, tuple(sorted(o.text for o in opts)) if opts else None)
        if key in seen:
            return
        seen.add(key)
        out.append({"kind": kind, "part": part, "stem": stem, "desc": f"{node['name']}. {node['description']}",
                    "mcq": opts is not None,
                    "options": [{"text": o.text, "correct": o.correct, "synthetic": o.synthetic} for o in opts or []],
                    "step_move": step["move"] if step else "none"})

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
            add("check", part, plan.check(turn, part, i, settings), stem)
        pq = prequestion(turn, settings)
        if pq and pq.get("correct"):
            step = plan.ask_mcq(turn, plan.question(part, "intuition", pq["correct"], settings), pq.get("source") or {})
            add("intuition", part, step, node.get("intuition") or stem)
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
    groups = {"economics": [q for q in qs if q["kind"] != "how_ai_works"],
              "how_ai_works": [q for q in qs if q["kind"] == "how_ai_works"]}
    groups["all"] = qs
    summary = {}
    for g, items in groups.items():
        m = [q for q in items if q["mcq"]]
        row = {"questions": len(items), "mcqs": len(m), "open_fallback": len(items) - len(m)}
        if m:
            row["chance"] = round(statistics.mean(q["chance"] for q in m), 3)
            row.update({s: round(statistics.mean(q["hits"][s] for q in m), 3) for s in STRATS})
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
    print(json.dumps(summary, indent=1))
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"summary": summary, "questions": qs}, f, indent=1)


if __name__ == "__main__":
    main()
