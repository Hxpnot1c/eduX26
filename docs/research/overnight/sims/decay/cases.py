"""w3-06 first-principles cases: the decay-clock asymmetry on economics parts, through the real learner code.

Each case is one synthetic student on the example-mini pack in a throwaway EDUX_DATA_DIR under
/tmp/claude-1000/w3-06/cases. Evidence goes in with learner.record_evidence(apply="now"), exchanges with
record_exchange(apply="now"); p_now is read with learner.part_p at day offsets. Nothing in the repo is edited.
Writes results/cases.md.
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edux_sim as S  # noqa: E402

T0 = datetime(2027, 1, 11, 17, 0, tzinfo=timezone.utc)   # 148 days before the pack's exam (2027-06-08)


def iso(t):
    return t.isoformat(timespec="seconds")


def main(out=HERE / "results" / "cases.md"):
    S.setup_data_dir("/tmp/claude-1000/w3-06/cases")
    S.use_settings("current")
    from edux import learner
    L = learner
    lines = ["# w3-06 first-principles cases (real code, settings.toml as is)", ""]

    def student(name):
        return L.add_student(name, "example-mini", student_id=name)["id"] if L.get_student(name) is None else name

    def ev(sid, part, ok, t, typ="mcq_check"):
        L.record_evidence(sid, part, typ, 1.0 if ok else 0.0, ts=iso(t), origin="check", apply="now")

    P = "ped_values"   # default difficulty, no teacher value: prior .30, half-life 2
    pr, hl = L.initial_state(P)
    lines.append(f"Part `{P}`: prior {pr:.3f}, starting half-life {hl:.2f} days.")
    lines.append("")
    # Case set 1: one part, four students
    cases = {
        "U untouched": [],
        "W one wrong check": [(0, False)],
        "WW two wrong checks": [(0, False), (0.01, False)],
        "C one right check": [(0, True)],
        "WC wrong then right (same day)": [(0, False), (0.01, True)],
        "CCC right on days 0, 2, 6": [(0, True), (2, True), (6, True)],
    }
    traj = {}
    days = [0, 1, 2, 3, 4, 5, 7, 10, 14, 21, 30, 60]
    for name, evs in cases.items():
        sid = student("c-" + name.split()[0])
        for d, ok in evs:
            ev(sid, P, ok, T0 + timedelta(days=d))
        last = max([d for d, _ in evs], default=0)
        traj[name] = [L.part_p(sid, P, iso(T0 + timedelta(days=last + d, seconds=60))) for d in days]
        row = L._conn().execute("SELECT * FROM part_state WHERE student_id=? AND part_id=?", (sid, P)).fetchone()
        traj[name].append(dict(row) if row else None)
    lines.append("## p_now on one part, by days since each student's last evidence")
    lines.append("")
    lines.append("| student | " + " | ".join(f"d{d}" for d in days) + " | half-life | clock |")
    lines.append("|---|" + "---|" * (len(days) + 2))
    for name, vals in traj.items():
        st = vals[-1]
        lines.append(f"| {name} | " + " | ".join(f"{v:.3f}" for v in vals[:-1]) +
                     f" | {st['half_life_days'] if st else hl:.1f} | {'set' if st and st['clock_start'] else 'none'} |")
    lines.append("")
    # crossing days, analytic: p_c * 0.5**(t/h) = target -> t = h * log2(p_c/target)
    st = traj["C one right check"][-1]
    pc, h = st["p_known"], st["half_life_days"]
    pw = traj["W one wrong check"][0]
    pww = traj["WW two wrong checks"][0]
    lev = L._settings().levels
    lines.append("## Crossing times for student C (one right check), t = h·log2(p_known / target)")
    lines.append("")
    for label, target in [("below `new` (0.40): level drops to new", lev.new),
                          ("below untouched U (prior)", pr),
                          ("below W (one wrong, never right)", pw),
                          ("below WW (two wrong, never right)", pww)]:
        lines.append(f"- {label}: {h * math.log2(pc / target):.1f} days")
    st3 = traj["CCC right on days 0, 2, 6"][-1]
    lines.append(f"- student CCC (half-life {st3['half_life_days']:.0f} d, p_known {st3['p_known']:.3f}) falls below U after "
                 f"{st3['half_life_days'] * math.log2(st3['p_known'] / pr):.1f} days and below W after "
                 f"{st3['half_life_days'] * math.log2(st3['p_known'] / pw):.1f} days from the last right answer")
    lines.append("")
    # Spacing: the review gap after the right answer vs the crossing time, by days to exam
    lines.append("## Review gap after a right answer vs crossing time (scheduling shares from settings.toml)")
    lines.append("")
    lines.append("| days to exam | review gap (days) | C's p_now when the review falls due | below U? | below W? |")
    lines.append("|---|---|---|---|---|")
    sc = L._settings().scheduling
    for dte in [150, 90, 61, 45, 30, 14, 10, 5]:
        share = sc.share_far if dte > 60 else sc.share_mid if dte >= 14 else sc.share_near
        gap = max(sc.min_gap_days, share * dte)
        p_due = pc * 0.5 ** (gap / h)
        lines.append(f"| {dte} | {gap:.1f} | {p_due:.3f} | {'yes' if p_due < pr else 'no'} | {'yes' if p_due < pw else 'no'} |")
    lines.append("")

    # Case 2: propagation onto a never-right prerequisite
    lines.append("## Propagation onto a prerequisite never answered right (prereq_boost, no clock)")
    lines.append("")
    sid = student("c-prop")
    pre, dep = "ped_formula", "ped_values"   # edge ped_formula -> ped_values (prerequisite)
    rows = []
    for k in range(6):
        t = T0 + timedelta(days=2 * k)
        ev(sid, dep, True, t)
        stp = L._conn().execute("SELECT * FROM part_state WHERE student_id=? AND part_id=?", (sid, pre)).fetchone()
        rows.append((k + 1, L.part_p(sid, dep, iso(t)), L.part_p(sid, pre, iso(t)), stp["clock_start"]))
    for k, pd, pp, clk in rows:
        lines.append(f"- after right answer {k} on `{dep}` (day {2*(k-1)}): `{dep}` {pd:.3f}, `{pre}` {pp:.3f} "
                     f"({L.level(pp)}), `{pre}` clock {'set' if clk else 'none'}")
    for d in (30, 90):
        lines.append(f"- day {10 + d}: `{dep}` {L.part_p(sid, dep, iso(T0 + timedelta(days=10 + d))):.3f}, "
                     f"`{pre}` {L.part_p(sid, pre, iso(T0 + timedelta(days=10 + d))):.3f} (never answered, never decays)")
    lines.append("")

    # Case 3: exchange nudges with no check (transfer x constructive = odds x1.155 per exchange)
    lines.append("## Exchange nudges with no check (transfer + constructive labels)")
    lines.append("")
    sid = student("c-nudge")
    P3 = "pes_definition"
    for k in range(1, 16):
        L.record_exchange(sid, [P3], "transfer", "constructive", ts=iso(T0 + timedelta(minutes=2 * k)), apply="now")
        if k in (3, 4, 8, 10, 14, 15):
            p = L.part_p(sid, P3, iso(T0 + timedelta(minutes=2 * k)))
            lines.append(f"- after {k} exchanges: {p:.3f} ({L.level(p)})")
    p90 = L.part_p(sid, P3, iso(T0 + timedelta(days=90)))
    q = L._conn().execute("SELECT reason, due FROM review_queue WHERE student_id=? AND part_id=?", (sid, P3)).fetchone()
    lines.append(f"- 90 days later: {p90:.3f} ({L.level(p90)}); review queued: {dict(q) if q else None}")
    lines.append("")

    # Case 4: untouched priors by difficulty vs the candidate band
    lines.append("## Untouched priors vs propagation.queue_band (learner.candidates; not called by live code)")
    lines.append("")
    lo, hi = L._settings().propagation.queue_band
    for part in L.all_parts():
        p0, h0 = L.initial_state(part)
        lines.append(f"- `{part}`: difficulty {L.difficulty(part):.2f}, prior {p0:.3f}, half-life {h0:.2f}"
                     f"{'  <- below band floor %.2f: never a candidate while untouched' % lo if p0 < lo else ''}")
    lines.append("")
    Path(out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
