"""Simulated class: synthetic students through Synapse's real learner model, level shares by week.

    python scripts/simulate_class_levels.py [out.json] [--students 25] [--days 56]

SYNTHETIC students on the example-mini pack. They show how the rules behave; they are not evidence about real
students and never a learning gain.

A. One student, one part, 30 days: pre-question wrong, taught and explained back, checked, forgets, reviews.
   p_now is sampled between events (each event is recorded before the samples that follow it).
B. A class for 8 weeks: a new part taught every 5 days; sessions every other day (attended 80%); in a session a
   student explains back and checks the newest part, then does up to 3 reviews the real code says are due. Hidden
   memory (our choice, as in scripts/simulate_review_threshold.py): recall = exp(-days / S), S starts at
   4 x exp(0.3 x ability) days if the first answer is right (1 day if not), doubles after a right review and halves
   after a wrong one (never below 1 day); right with probability recall x 0.9 + (1 - recall) x 0.25.
   Weekly snapshot over the (student, taught part) pairs: the share at each level by the number (new / developing /
   secure), the share at each level shown to students (new / needs review / taught in class / developing / secure),
   reviews done per student that week, and the reviews due but not done at the snapshot per student (the backlog).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["EDUX_DATA_DIR"] = tempfile.mkdtemp(prefix="synsim-")

from edux import db, graph, learner  # noqa: E402
from ingest import load  # noqa: E402

report = load.load_pack(ROOT / "coursepacks" / "example-mini", db_path=db.content_db_path())
learner.use_database(db.learner_db_path(), db.content_db_path())
PARTS = [p for p in learner.all_parts() if not graph.is_literacy(p)]
START = datetime.now(timezone.utc).replace(microsecond=0, second=0, minute=0, hour=9) - timedelta(days=80)
SHOWN = ("new", "needs_review", "taught_in_class", "developing", "secure")


def stamp(day: float) -> str:
    return (START + timedelta(days=day)).isoformat(timespec="seconds")


def uniform(*key) -> float:
    return int.from_bytes(hashlib.sha256(":".join(map(str, key)).encode()).digest()[:8], "big") / 2**64


# --- A: one student, one part ----------------------------------------------------------------------------------
def run_a() -> dict:
    part = "ped_values" if "ped_values" in PARTS else PARTS[0]
    sid = learner.add_student("A", report.course_id)["id"]
    m = 1 / 1440  # a minute, in days
    events = [  # day, evidence type, score, label
        (0.0, "prequestion", 0.0, "Pre-question: wrong"),
        (10 * m, "explain_back", 1.0, "Taught, then explains it back"),
        (14 * m, "mcq_check", 1.0, "Check: right"),
        (2.0, "review", 1.0, "Review: right"),
        (9.0, "review", 0.0, "Review: wrong (forgot)"),
        (9.0 + 10 * m, "explain_back", 1.0, "Re-explains it"),
        (16.0, "review", 1.0, "Review: right"),
        (28.0, "review", 1.0, "Review before the mock: right"),
    ]
    samples = [{"day": -1.0, "p": round(learner.part_p(sid, part, stamp(-1.0)), 4)}]
    marks = []
    for i, (day, kind, score, label) in enumerate(events):
        learner.record_evidence(
            sid, part, kind, score, ts=stamp(day), apply="now", n_options=4 if kind in ("mcq_check", "review") else None
        )
        p = learner.part_p(sid, part, stamp(day))
        marks.append({"day": round(day, 4), "p": round(p, 4), "label": label, "right": score > 0})
        end = events[i + 1][0] if i + 1 < len(events) else 30.0
        t = day + 0.25
        while t < end:
            samples.append({"day": round(t, 4), "p": round(learner.part_p(sid, part, stamp(t)), 4)})
            t += 0.25
    samples.append({"day": 30.0, "p": round(learner.part_p(sid, part, stamp(30.0)), 4)})
    return {"part": part, "part_name": graph.require_node(part)["name"], "samples": samples, "events": marks}


# --- B: a class --------------------------------------------------------------------------------------------------
def run_b(n_students: int = 25, days: int = 56, teach_every: int = 5, mock_day: int | None = None, tag: str = "B") -> dict:
    taught_on = {p: 1 + i * teach_every for i, p in enumerate(PARTS)}
    students = []
    class_id = learner.add_class(f"class-{tag}", report.course_id)
    for k in range(n_students):
        rng = random.Random(1000 + k)
        sid = learner.add_student(f"{tag}{k}", report.course_id)["id"]
        students.append({"id": sid, "ability": rng.gauss(0, 1), "S": {}, "last": {}, "done": set()})
    learner.add_students_to_class(class_id, [s["id"] for s in students])
    if mock_day is not None:
        learner.add_class_assessment(class_id, "Half-term mock", "mock", (START + timedelta(days=mock_day)).date().isoformat(), PARTS)
    weeks, reviews_this_week = [], 0
    for day in range(1, days + 1):
        for k, s in enumerate(students):
            if day % 2 or uniform("attend", k, day) > 0.8:
                continue
            new = [p for p in PARTS if taught_on[p] <= day and p not in s["done"]]
            for p in new[:2]:  # up to two taught parts not yet studied, oldest first (catching up after an absence)
                ok = uniform("first", k, p) < 1 / (1 + math.exp(-(s["ability"] + 0.8)))
                learner.record_evidence(s["id"], p, "explain_back", float(ok), ts=stamp(day + 0.40), apply="now")
                chk = uniform("check", k, p) < (0.85 if ok else 0.35)
                learner.record_evidence(s["id"], p, "mcq_check", float(chk), ts=stamp(day + 0.41), apply="now", n_options=4)
                s["S"][p] = 4 * math.exp(0.3 * s["ability"]) if ok else 1.0
                s["last"][p] = day + 0.41
                s["done"].add(p)
            at = stamp(day + 0.45)
            for r in learner.due_reviews(s["id"], 3, at):
                p = r["part_id"]
                if p not in s["S"]:
                    continue
                recall = math.exp(-(day + 0.45 - s["last"][p]) / s["S"][p])
                right = uniform("rev", k, p, day) < recall * 0.9 + (1 - recall) * 0.25
                if day + 0.45 - s["last"][p] >= 0.5:
                    s["S"][p] = max(1.0, s["S"][p] * (2.0 if right else 0.5))
                s["last"][p] = day + 0.45
                learner.record_evidence(s["id"], p, "review", float(right), ts=at, apply="now", n_options=4)
                reviews_this_week += 1
        if day % 7 == 0:
            at = stamp(day + 0.99)
            by_number = {"new": 0, "developing": 0, "secure": 0}
            shown = dict.fromkeys(SHOWN, 0)
            for s in students:
                for p in PARTS:
                    if taught_on[p] <= day:
                        by_number[learner.level(learner.part_p(s["id"], p, at))] += 1
                        shown[learner.shown_level(s["id"], p, at)] += 1
            total = sum(by_number.values())
            backlog = sum(len([r for r in learner.due_reviews(s["id"], 1000, at) if r["part_id"] in s["S"]]) for s in students)
            weeks.append(
                {
                    "week": day // 7,
                    "taught_parts": sum(t <= day for t in taught_on.values()),
                    "pairs": total,
                    "by_number": {k: round(v / total, 4) for k, v in by_number.items()},
                    "shown": {k: round(v / total, 4) for k, v in shown.items()},
                    "reviews_per_student": round(reviews_this_week / n_students, 2),
                    "backlog_per_student": round(backlog / n_students, 2),
                }
            )
            reviews_this_week = 0
            print("week", day // 7, weeks[-1], file=sys.stderr)
    return {"students": n_students, "days": days, "teach_every": teach_every, "mock_day": mock_day, "parts": len(PARTS), "weeks": weeks}


def table(name: str, run: dict) -> str:
    head = f"{'week':>4} {'new':>6} {'dev':>6} {'sec':>6} | {'new':>6} {'review':>6} {'taught':>6} {'dev':>6} {'sec':>6} | {'rev/st':>6} {'backlog':>7}"
    lines = [f"{name} (SYNTHETIC students; by the number | as shown | reviews a week and due-not-done per student)", head]
    for w in run["weeks"]:
        n, s = w["by_number"], w["shown"]
        lines.append(
            f"{w['week']:>4} {n['new']:>6.2f} {n['developing']:>6.2f} {n['secure']:>6.2f} | {s['new']:>6.2f} {s['needs_review']:>6.2f} "
            f"{s['taught_in_class']:>6.2f} {s['developing']:>6.2f} {s['secure']:>6.2f} | {w['reviews_per_student']:>6.2f} "
            f"{w['backlog_per_student']:>7.2f}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", help="write the full results here as JSON")
    ap.add_argument("--students", type=int, default=25)
    ap.add_argument("--days", type=int, default=56)
    a = ap.parse_args()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out = {
        "commit": commit,
        "A": run_a(),
        "B_final_only": run_b(a.students, a.days, tag="F"),
        "B_mock": run_b(a.students, a.days, mock_day=a.days, tag="M"),
    }
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))
    print("SYNTHETIC students: how the rules behave, not evidence about real students. Not learning gains.")
    print(table("B, final exam only", out["B_final_only"]))
    print(table("B, with a mock on the last day", out["B_mock"]))
