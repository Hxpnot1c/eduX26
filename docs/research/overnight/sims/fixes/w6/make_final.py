"""w6-fix-counters: build the clean 0009b / 0010b trees (the code that goes in the diffs).

    python make_final.py <base tree: export + 0001-0008> <out dir>
Writes <out>/t9b (base + 0009b) and <out>/t10b (t9b + 0010b), and <out>/t10only (base + 0010b alone, to check it
applies and runs without 0009b). Edits are exact string replacements (each anchor must occur once).
"""
import shutil
import sys
from pathlib import Path

CAP_SIG = [
    ("""def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, evidence_type: str, correct: bool, ts: str,
                    weight: float = 1.0, slip_add: float = 0.0) -> None:
    \"\"\"The BKT update on one part; weight (0–1) scales how far p_known moves towards the BKT result.
    slip_add raises slip (capped at session.slip_cap) while the session is fatigued.\"\"\"""",
     """def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, evidence_type: str, correct: bool, ts: str,
                    weight: float = 1.0, slip_add: float = 0.0, cap: float | None = None) -> None:
    \"\"\"The BKT update on one part; weight (0–1) scales how far p_known moves towards the BKT result.
    slip_add raises slip (capped at session.slip_cap) while the session is fatigued. cap: p_known rises no higher
    than this (or than where it was).\"\"\""""),
    ("""    p = before + weight * (p - before)

    factor""",
     """    p = before + weight * (p - before)
    if cap is not None and p > cap:
        p = max(before, cap)

    factor"""),
    ("""        _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts, weight=weight, slip_add=slip_add)""",
     """        _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts, weight=weight, slip_add=slip_add, cap=cap)"""),
    ("""            evidence_type = "immediate"
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)""",
     """            evidence_type = "immediate"
    cap = None
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)"""),
]

P9 = [
    ("""def found_problem(kind: str = "ail_task", points_met: list[str] | None = None) -> dict:
    \"\"\"Verify evidence for a reported dead or mismatched source (step 05e): finding the problem is a successful
    check, so it scores 1 whatever was ticked (a dead page has no publisher, date or figure to tick).\"\"\"""",
     """def found_problem(kind: str = "ail_task", points_met: list[str] | None = None) -> dict:
    \"\"\"Verify evidence for a reported dead or mismatched source (step 05e): finding the problem is a successful
    check, so it scores 1 whatever was ticked (a dead page has no publisher, date or figure to tick). A report
    can't be told apart from a made-up one, so apply_evidence_event limits it: until the student has done one
    successful check of their own on Verify, reports reach developing at most.\"\"\""""),
    ("""    cap = None
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)""",
     """    cap = None
    if part_id == AIL_VERIFY and _reported(conn, event):
        # a reported dead or mismatched source counts as a check (a dead page has nothing else to tick), but it
        # can't be told apart from a made-up one: until the student has done one successful check of their own on
        # Verify, reports can't make Verify secure
        if not _checked_before(conn, event):
            cap = s.levels.secure - 0.01
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)"""),
    ("""\n\ndef apply_evidence_event(event: dict) -> None:""",
     '''

def _reported(conn: sqlite3.Connection, event: dict) -> bool:
    """The evidence came with an exchange labelled source_conflict (a dead or mismatched source reported)."""
    row = conn.execute("SELECT source_conflict FROM exchange_log WHERE id = ?", (event.get("exchange_id"),)).fetchone()
    return bool(row and row["source_conflict"])


def _checked_before(conn: sqlite3.Connection, event: dict) -> bool:
    """The student has done one successful check of their own on Verify: a correct Verify answer that was not a
    report."""
    return conn.execute(
        """SELECT 1 FROM evidence_log e LEFT JOIN exchange_log x ON x.id = e.exchange_id WHERE e.student_id = ?
           AND e.part_id = ? AND e.id < ? AND e.score >= ? AND COALESCE(x.source_conflict, 0) = 0 LIMIT 1""",
        (event["student_id"], AIL_VERIFY, event["id"], _settings().bkt.correct_share)).fetchone() is not None


def apply_evidence_event(event: dict) -> None:'''),
]

P10 = [
    ("""LITERACY_ANSWERS = ("ail_task", "ail_unprompted")""",
     """OPEN_ANSWERS = ("explain_back", "extend", "past_question", "link")   # answers the student writes, not picks
LITERACY_ANSWERS = ("ail_task", "ail_unprompted")"""),
    ("""    cap = None
""",
     """    cap = None
    if evidence_type == "immediate" and event["evidence_type"] not in OPEN_ANSWERS:
        # a pick straight after being shown or hinted (the option repeats the point just shown) can't make a part
        # secure; an answer they write themselves (explain-back, extend) still can
        cap = s.levels.secure - 0.01
"""),
    ("""                other["p_known"] = min(0.99, _p_at(other, ts) + s.propagation.prereq_boost * gain)""",
     """                was = _p_at(other, ts)
                # a boost from a dependent part is indirect evidence: it never makes a prerequisite secure on its own
                other["p_known"] = min(0.99, was + s.propagation.prereq_boost * gain, max(was, s.levels.secure - 0.01))"""),
]


TEXT9 = [
    ("""giving both figures without a verdict is c, not d.""",
     """giving both figures without a verdict is c, not d. Never tick a point for words that only repeat your own reply, a point you just showed or your citation: on a source check that is not looking, in an explain-back it is copying."""),
]


PLAN10 = [
    ("""check straight after a worked example doesn't reset the count (they had just been shown it).""",
     """check straight after a worked example doesn't reset the count (they had just been shown it), and a miss on an
# open answer is cleared only by a complete open answer (right checks in between don't show they can explain it)."""),
    ("""    missed = retry is not None if open_answer else not evidence["correct"]
    just_shown = any(s.get("key") == "show_stuck" for s in last_plan)
    state["n"] = state["n"] + 1 if missed else (state["n"] if just_shown and not open_answer else 0)""",
     """    missed = retry is not None if open_answer else not evidence["correct"]
    just_shown = any(s.get("key") == "show_stuck" for s in last_plan)
    keep = not open_answer and (just_shown or state.get("open"))
    state["n"] = state["n"] + 1 if missed else (state["n"] if keep else 0)
    if open_answer:
        state["open"] = missed"""),
]


def apply(tree: Path, edits, path: str = "edux/learner.py") -> None:
    f = tree / path
    src = f.read_text()
    for old, new in edits:
        assert src.count(old) == 1, (src.count(old), old[:100])
        src = src.replace(old, new)
    f.write_text(src)


def fresh(base: Path, dst: Path) -> Path:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns("__pycache__"))
    return dst


if __name__ == "__main__":
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    t9 = fresh(base, out / "t9b"); apply(t9, CAP_SIG + P9); apply(t9, TEXT9, "text/tools/tutor_turn.md")
    t10 = fresh(t9, out / "t10b"); apply(t10, P10); apply(t10, PLAN10, "edux/plan.py")
    t10o = fresh(base, out / "t10only"); apply(t10o, CAP_SIG + P10); apply(t10o, PLAN10, "edux/plan.py")
    print("built", t9, t10, t10o)
