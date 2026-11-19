"""Simulate review_when_below at different values (audit item C14, Vishnu's decision of 18 November).

    python scripts/simulate_review_threshold.py [--students 60] [--thresholds 0.5 0.75] [--days 90]

SYNTHETIC STUDENTS on the example pack. They test how the scheduling rules behave when the assumptions below hold;
they are not evidence about real students and never a learning gain.

What it does: each synthetic student studies every part of the example pack in the first weeks (an explain-back after
teaching), then comes to a session every other day with some probability and does up to three of the reviews the real
code says are due (learner.due_reviews). Their true memory is hidden: one trace per part, recall = exp(-days since the
last retrieval / S); S starts at 4 days; a right review multiplies it by 2 (if at least half a day after the last
retrieval), a wrong one by 0.5 (never below 1 day). The real learner model (BKT with forgetting, the review queue, the
share gap and review_when_below) sees only the answers. Each answer is right with probability recall x (1 - slip) + (1 -
recall) x guess, drawn from a uniform that depends only on (seed, part, day), so every variant meets the same dice.
On exam day the model's belief is compared with the hidden truth.

Metrics per variant (mean over students): reviews done a week; mean true recall on exam day (retention); parts the model
calls secure whose true recall is below 0.5 (false secure); parts it calls secure whose true recall is at least 0.75
(truly secure); and how many of the studied parts were due but never reached by the three-a-session cap.
Only review_when_below changes between variants; everything else in settings.toml is as it is.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import math
import os
import random
import statistics
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SLIP, GUESS, S0, MIN_S = 0.10, 0.25, 4.0, 1.0       # the truth model: our choices, not findings
SESSION_EVERY, ATTEND, PER_SESSION = 2, 0.8, 3       # a session every 2 days, attended 80% of the time, 3 reviews a time


def uniform(seed: int, part: str, day: int) -> float:
    digest = hashlib.sha256(f"{seed}:{part}:{day}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def simulate(threshold: float, seeds: list[int], days: int, folder: Path) -> list[dict]:
    os.environ["EDUX_DATA_DIR"] = str(folder)
    from edux import db, graph, learner
    from ingest import load

    pack = Path(__file__).resolve().parent.parent / "coursepacks" / "example-mini"
    report = load.load_pack(pack, db_path=db.content_db_path())
    learner.use_database(db.learner_db_path(), db.content_db_path())
    settings = learner._settings()
    changed = dataclasses.replace(settings, scheduling=dataclasses.replace(settings.scheduling, review_when_below=threshold))
    learner._settings = lambda: changed
    parts = [p for p in learner.all_parts() if not graph.is_literacy(p)]
    start = datetime.now(timezone.utc).replace(microsecond=0, second=0, minute=0, hour=9) - timedelta(days=days + 5)
    exam = start + timedelta(days=days)
    rows = []
    for seed in seeds:
        sid = learner.add_student(f"S{seed}", report.course_id)["id"]
        with learner._conn() as conn:
            conn.execute("UPDATE student_profile SET exam_date_override = ? WHERE student_id = ?", (exam.date().isoformat(), sid))
        rng = random.Random(seed)
        strength, last = {}, {}                     # hidden truth per part
        reviews = missed = 0

        def stamp(day: float) -> str:
            return (start + timedelta(days=day)).isoformat(timespec="seconds")

        for i, part in enumerate(parts):            # taught and checked in the first weeks
            day = 1 + 3 * i
            ok = rng.random() < 0.7
            strength[part], last[part] = (S0 if ok else MIN_S), float(day)
            learner.record_evidence(sid, part, "explain_back", float(ok), ts=stamp(day), apply="now")
        for day in range(1 + 3 * len(parts), days):
            if (day % SESSION_EVERY) or rng.random() > ATTEND:
                continue
            at = stamp(day + 0.1)
            due = learner.due_reviews(sid, 99, at)
            missed += max(0, len(due) - PER_SESSION)
            for r in due[:PER_SESSION]:
                part = r["part_id"]
                recall = math.exp(-(day - last[part]) / strength[part]) if part in strength else 0.0
                p_right = recall * (1 - SLIP) + (1 - recall) * GUESS
                right = uniform(seed, part, day) < p_right
                if day - last[part] >= 0.5:
                    strength[part] = max(MIN_S, strength[part] * (2.0 if right else 0.5))
                last[part] = float(day)
                learner.record_evidence(sid, part, "review", float(right), ts=stamp(day + 0.1), apply="now", n_options=4)
                reviews += 1
        exam_at = exam.isoformat(timespec="seconds")
        truth = {p: math.exp(-(days - last[p]) / strength[p]) for p in parts}
        belief = {p: learner.part_p(sid, p, exam_at) for p in parts}
        secure = [p for p in parts if learner.level(belief[p]) == "secure"]
        rows.append({"reviews_per_week": reviews / (days / 7), "retention": statistics.mean(truth.values()),
                     "false_secure": sum(truth[p] < 0.5 for p in secure), "truly_secure": sum(truth[p] >= 0.75 for p in secure),
                     "secure": len(secure), "capped": missed})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--students", type=int, default=60)
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.5, 0.75])
    parser.add_argument("--days", type=int, default=90)
    args = parser.parse_args()
    seeds = list(range(1, args.students + 1))
    print(f"SYNTHETIC students, {args.students} per variant, {args.days} days, example-mini pack (9 parts). Not learning gains.")
    print(f"{'review_when_below':>18} {'reviews/week':>13} {'true retention':>15} {'false secure':>13} {'truly secure':>13} {'reviews capped':>15}")
    for threshold in args.thresholds:
        with tempfile.TemporaryDirectory() as folder:
            import subprocess

            out = subprocess.run([sys.executable, __file__, "--worker", str(threshold), str(args.students), str(args.days), folder],
                                 capture_output=True, text=True, check=True).stdout.strip()
            print(out)


def worker(threshold: float, students: int, days: int, folder: str) -> None:
    rows = simulate(threshold, list(range(1, students + 1)), days, Path(folder))
    mean = lambda k: statistics.mean(r[k] for r in rows)       # noqa: E731
    sd = lambda k: statistics.stdev(r[k] for r in rows) / math.sqrt(len(rows))       # noqa: E731
    print(f"{threshold:>18.2f} {mean('reviews_per_week'):>7.2f}±{sd('reviews_per_week'):<4.2f} {mean('retention'):>9.3f}±{sd('retention'):<5.3f} "
          f"{mean('false_secure'):>7.2f}±{sd('false_secure'):<4.2f} {mean('truly_secure'):>7.2f}±{sd('truly_secure'):<4.2f} "
          f"{mean('capped'):>9.1f}±{sd('capped'):<4.1f}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()
