"""w6-fix-counters: build the counter variants as edited copies of a base tree (export + 0001-0008).

    python make_variants.py <base tree> <out dir> [variant ...]
Each variant is <out>/<name>, a copy of the base with edux/learner.py edited by string replacement (asserts that every
anchor is found exactly once). Variants (see work/w6/w6-fix-counters.md):
  d1   a dead/mismatched-source report (an ail_verify answer on an exchange labelled source_conflict) can't lift Verify
       past levels.secure - 0.01 (developing); found_problem unchanged (scores 1)
  d2   d1 + only the first report in a session counts (later ones are logged, weight 0)
  d3   as d1, but the cap is lifted once the student has one successful check of their own on Verify (a correct
       Verify answer on an exchange not labelled source_conflict): a report counts towards secure only alongside a
       real check
  d4   d3 + only the first report in a session counts
  c1   0010 as shipped: any immediate evidence capped below secure
  c1m  only recognition evidence (MCQ checks etc.) is capped when immediate; open answers the student produces
       (explain_back, extend, past_question, link) can still make a part secure
  c1r  immediate evidence capped below secure until the part has one correct non-immediate answer
  c1j  immediate evidence capped only when the window contains a "just show me" on the part
  c1js immediate evidence after a "just show me" uses guess 0.60 (no cap)
  p    (add-on) a prerequisite boost from capped evidence is capped the same way (otherwise a capped gain on a
       part still lifts its prerequisites past secure: the leak that lets C3t reach secure under c1)
  P    (add-on) a prerequisite boost never lifts a part past levels.secure - 0.01 (indirect evidence alone never
       makes a part secure)
Combinations: join with '+', e.g. d2+c1m+p.
"""
import shutil
import sys
from pathlib import Path

CAP_PARAM = [
    ("""def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, evidence_type: str, correct: bool, ts: str,
                    weight: float = 1.0, slip_add: float = 0.0) -> None:""",
     """def _apply_evidence(conn: sqlite3.Connection, student_id: str, part_id: str, evidence_type: str, correct: bool, ts: str,
                    weight: float = 1.0, slip_add: float = 0.0, cap: float | None = None,
                    guess_override: float | None = None) -> None:"""),
    ("""    slip, guess = s.bkt.evidence[evidence_type].slip, s.bkt.evidence[evidence_type].guess
""",
     """    slip, guess = s.bkt.evidence[evidence_type].slip, s.bkt.evidence[evidence_type].guess
    if guess_override is not None:
        guess = guess_override
"""),
    ("""    p = before + weight * (p - before)

    factor""",
     """    p = before + weight * (p - before)
    if cap is not None and p > cap:
        p = max(before, cap)

    factor"""),
    ("""        _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts, weight=weight, slip_add=slip_add)""",
     """        _apply_evidence(conn, student_id, part_id, evidence_type, correct, ts, weight=weight, slip_add=slip_add,
                        cap=min(caps) if caps else None, guess_override=guess_override)"""),
    ("""    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)
    surprise""",
     """    caps, guess_override = [], None
    #@@IMMEDIATE@@
    #@@REPORT@@
    p_before = _p_at(_load_state(conn, student_id, part_id, ts), ts)
    surprise"""),
]

REPORT = {
    "d3": """if part_id == AIL_VERIFY and _reported(conn, event) and not _checked_before(conn, event):
        caps.append(s.levels.secure - 0.01)""",
    "d4": """if part_id == AIL_VERIFY and _reported(conn, event):
        if not _checked_before(conn, event):
            caps.append(s.levels.secure - 0.01)
        if _reported_before(conn, event, session_start(conn, student_id, ts)):
            weight = 0.0""",
    "d1": """if part_id == AIL_VERIFY and _reported(conn, event):
        caps.append(s.levels.secure - 0.01)""",
    "d2": """if part_id == AIL_VERIFY and _reported(conn, event):
        caps.append(s.levels.secure - 0.01)
        if _reported_before(conn, event, session_start(conn, student_id, ts)):
            weight = 0.0""",
}
HELPERS = '''

def _reported(conn: sqlite3.Connection, event: dict) -> bool:
    """The evidence came with an exchange labelled source_conflict (a dead or mismatched source reported)."""
    if not event.get("exchange_id"):
        return False
    row = conn.execute("SELECT source_conflict FROM exchange_log WHERE id = ?", (event["exchange_id"],)).fetchone()
    return bool(row and row["source_conflict"])


def _reported_before(conn: sqlite3.Connection, event: dict, since: str) -> bool:
    """An earlier report already gave Verify evidence this session."""
    return conn.execute(
        """SELECT 1 FROM evidence_log e JOIN exchange_log x ON x.id = e.exchange_id WHERE e.student_id = ?
           AND e.part_id = ? AND x.source_conflict = 1 AND e.ts >= ? AND e.id < ? LIMIT 1""",
        (event["student_id"], AIL_VERIFY, since, event["id"])).fetchone() is not None


def _checked_before(conn: sqlite3.Connection, event: dict) -> bool:
    """The student has done one successful check of their own on Verify before this (a correct Verify answer whose
    exchange was not a dead or mismatched source report)."""
    return conn.execute(
        """SELECT 1 FROM evidence_log e LEFT JOIN exchange_log x ON x.id = e.exchange_id WHERE e.student_id = ?
           AND e.part_id = ? AND e.id < ? AND e.score >= ? AND COALESCE(x.source_conflict, 0) = 0 LIMIT 1""",
        (event["student_id"], AIL_VERIFY, event["id"], _settings().bkt.correct_share)).fetchone() is not None


def _recently_shown(conn: sqlite3.Connection, student_id: str, part_id: str, ts: str) -> bool:
    """A "just show me" on the part within evidence.immediate_window_minutes before ts."""
    since = _event_ts(parse_ts(ts) - timedelta(minutes=_settings().evidence.immediate_window_minutes))
    rows = conn.execute("""SELECT node_ids FROM exchange_log WHERE student_id = ? AND ts >= ? AND ts <= ?
                           AND choice_taken = 'just_show_me'""", (student_id, since, ts))
    return any(part_id in _tagged_parts(split(r["node_ids"])) for r in rows)


def _had_spaced_success(conn: sqlite3.Connection, student_id: str, part_id: str, before_id: int) -> bool:
    """A correct answer on the part that was not immediate (outside the immediate-recall window)."""
    return conn.execute(
        """SELECT 1 FROM evidence_derived d JOIN evidence_log l ON l.id = d.evidence_id WHERE l.student_id = ?
           AND l.part_id = ? AND l.id < ? AND l.score >= ? AND d.immediate = 0 AND d.weight > 0 LIMIT 1""",
        (student_id, part_id, before_id, _settings().bkt.correct_share)).fetchone() is not None
'''

OPEN = '("explain_back", "extend", "past_question", "link")'
IMMEDIATE = {
    "c1": """if evidence_type == "immediate":
        caps.append(s.levels.secure - 0.01)""",
    "c1m": f"""if evidence_type == "immediate" and event["evidence_type"] not in {OPEN}:
        caps.append(s.levels.secure - 0.01)""",
    "c1r": """if evidence_type == "immediate" and not _had_spaced_success(conn, student_id, part_id, event["id"]):
        caps.append(s.levels.secure - 0.01)""",
    "c1j": """if evidence_type == "immediate" and _recently_shown(conn, student_id, part_id, ts):
        caps.append(s.levels.secure - 0.01)""",
    "c1js": """if evidence_type == "immediate" and _recently_shown(conn, student_id, part_id, ts):
        guess_override = 0.60""",
}


def edit(src: str, old: str, new: str) -> str:
    assert src.count(old) == 1, (src.count(old), old[:80])
    return src.replace(old, new)


def build(base: Path, out: Path, name: str) -> None:
    parts = name.split("+")
    dst = out / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns("__pycache__"))
    f = dst / "edux" / "learner.py"
    src = f.read_text()
    for old, new in CAP_PARAM:
        src = edit(src, old, new)
    imm = [p for p in parts if p in IMMEDIATE]
    rep = [p for p in parts if p in REPORT]
    prop = [p for p in parts if p in ("p", "P")]
    assert len(imm) + len(rep) + len(prop) == len(parts), parts
    old = """                other["p_known"] = min(0.99, _p_at(other, ts) + s.propagation.prereq_boost * gain)"""
    if prop == ["p"]:
        src = edit(src, old, """                was = _p_at(other, ts)
                other["p_known"] = min(0.99, was + s.propagation.prereq_boost * gain)
                if cap is not None:   # capped evidence can't make a prerequisite secure either
                    other["p_known"] = min(other["p_known"], max(was, cap))""")
    elif prop == ["P"]:
        src = edit(src, old, """                was = _p_at(other, ts)
                other["p_known"] = min(0.99, was + s.propagation.prereq_boost * gain)
                # indirect evidence alone never makes a part secure
                other["p_known"] = min(other["p_known"], max(was, s.levels.secure - 0.01))""")
    src = edit(src, "#@@IMMEDIATE@@", IMMEDIATE[imm[0]] if imm else "")
    src = edit(src, "#@@REPORT@@", REPORT[rep[0]] if rep else "")
    src = edit(src, "\n\ndef apply_evidence_event(", HELPERS + "\n\ndef apply_evidence_event(")
    f.write_text(src)
    if "c1r" in parts:   # c1r needs to know which past evidence was immediate: an evidence_derived column
        mig = dst / "migrations"
        last = sorted(mig.glob("*.sql"))[-1].name
        n = int(last.split("_")[0]) + 1
        (mig / f"{n:03d}_evidence_immediate.sql").write_text(
            "ALTER TABLE evidence_derived ADD COLUMN immediate INTEGER NOT NULL DEFAULT 0;\n")
        src = f.read_text()
        src = edit(src, """        \"\"\"INSERT OR REPLACE INTO evidence_derived (evidence_id, student_id, session_id, p_before, surprise, weight, fatigued)
           VALUES (?, ?, ?, ?, ?, ?, ?)\"\"\",
        (event["id"], student_id, session_id, p_before, surprise, weight, int(fatigued)))""",
                   """        \"\"\"INSERT OR REPLACE INTO evidence_derived (evidence_id, student_id, session_id, p_before, surprise, weight, fatigued,
             immediate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)\"\"\",
        (event["id"], student_id, session_id, p_before, surprise, weight, int(fatigued), int(evidence_type == "immediate")))""")
        f.write_text(src)
    print("built", dst)


if __name__ == "__main__":
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    for name in sys.argv[3:]:
        build(base, out, name)
