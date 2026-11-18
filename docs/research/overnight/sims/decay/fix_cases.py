"""w3-06: the first-principles students of cases.py under each fix (population.install). Writes results/fix_cases.md."""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import edux_sim as S  # noqa: E402
import population as POP  # noqa: E402
from cases import T0, iso  # noqa: E402

CASES = {"U": [], "W": [(0, False)], "C": [(0, True)], "WC": [(0, False), (0.01, True)],
         "CCC": [(0, True), (2, True), (6, True)], "CW": [(0, True), (3, False)]}
DAYS = [0, 3, 7, 14, 30, 60]


def main(out=HERE / "results" / "fix_cases.md"):
    S.setup_data_dir("/tmp/claude-1000/w3-06/fixcases")
    S.use_settings("current")
    from edux import learner as L
    P = "ped_values"
    lines = ["# First-principles students under each fix (part `ped_values`, prior 0.30)", "",
             "p_now by days since each student's last evidence; level in brackets (n new, d developing, s secure).", ""]
    lines.append("| variant | student | " + " | ".join(f"d{d}" for d in DAYS) + " |")
    lines.append("|---|---|" + "---|" * len(DAYS))
    for v in POP.VARIANTS:
        POP.install(v)
        for name, evs in CASES.items():
            sid = f"{v}-{name}"
            L.add_student(sid, "example-mini", student_id=sid)
            for d, ok in evs:
                L.record_evidence(sid, P, "mcq_check", 1.0 if ok else 0.0, ts=iso(T0 + timedelta(days=d)),
                                  origin="check", apply="now")
            last = max([d for d, _ in evs], default=0)
            vals = [L.part_p(sid, P, iso(T0 + timedelta(days=last + d, seconds=60))) for d in DAYS]
            lines.append(f"| {v} | {name} | " + " | ".join(f"{p:.3f} ({L.level(p)[0]})" for p in vals) + " |")
    POP.install("current")
    Path(out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
