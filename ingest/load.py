"""Load a course pack into content.db.

Recreates the database from content_schema.sql, inserts rows (unknown columns into
extra), fills question_node, id_map, note_fts and node_fts, computes node weights, applies the
teacher feedback overlay and prints a load report.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from edux import db
from edux.settings import Settings, load_settings
from ingest import registry
from ingest.registry import FileSpec, split_list
from ingest.validate import Issue, Table, read_pack, validate_tables, value_error

ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_DIR = ROOT / "teacher_feedback"


@dataclass
class LoadReport:
    """Counts per table, warnings, flagged rows, low-confidence rows and feedback not applied."""

    pack_path: str = ""
    db_path: str = ""
    course_id: str = ""
    errors: list[Issue] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)
    low_confidence: list[str] = field(default_factory=list)
    feedback_not_applied: list[str] = field(default_factory=list)
    suggested_links: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_pack(
    pack_dir: Path, db_path: Path | None = None, feedback_dir: Path | None = None, settings: Settings | None = None
) -> LoadReport:
    """Validate and load a pack into a fresh content.db; return the report."""
    db_path = db_path or db.content_db_path()
    settings = settings or load_settings()
    report = LoadReport(pack_path=str(pack_dir), db_path=str(db_path))
    if not pack_dir.is_dir():
        report.errors.append(Issue(str(pack_dir), None, "course pack folder not found"))
        return report
    tables = read_pack(pack_dir)
    result = validate_tables(tables)
    report.errors = result.errors
    report.warnings = [str(w) for w in result.warnings]
    if result.errors:
        return report

    report.course_id = tables["course.csv"].rows[0]["id"]
    conn = create_database(db_path)
    try:
        insert_rows(conn, tables, report.course_id)
        feedback_csv = (feedback_dir or FEEDBACK_DIR) / f"{report.course_id}.csv"
        report.feedback_not_applied = apply_feedback(conn, feedback_csv, report.course_id)
        fill_question_node(conn)
        build_note_index(conn)
        build_node_index(conn)
        compute_weights(conn, settings)
        report.suggested_links = compute_link_weights(conn, settings)
        report.counts = count_rows(conn)
        report.flagged, report.low_confidence = flagged_rows(conn)
        write_load_info(conn, report)
        conn.commit()
    finally:
        conn.close()
    return report


def create_database(db_path: Path) -> sqlite3.Connection:
    """Delete and recreate content.db from content_schema.sql."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        Path(f"{db_path}{suffix}").unlink(missing_ok=True)
    conn = db.connect_content(db_path)
    conn.executescript(db.CONTENT_SCHEMA.read_text(encoding="utf-8"))
    return conn


def _convert(value: str, column: registry.Column) -> object:
    if value == "":
        value = column.default if column.default is not None else ""
        if value == "":
            return None if column.default is None else ""
    if column.type == "int":
        return int(value)
    if column.type == "real":
        return float(value)
    return value


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def insert_file(conn: sqlite3.Connection, spec: FileSpec, rows: list[dict[str, str]], header: list[str], course_id: str) -> int:
    """Insert one file's rows; columns not in the registry go to extra as JSON. Returns the row count."""
    db_columns = _table_columns(conn, spec.table)
    known = [c for c in spec.columns if c.name in db_columns]
    unknown = [h for h in header if h and spec.column(h) is None]
    names = [c.name for c in known]
    if spec.course_scoped and "course_id" in db_columns:
        names.append("course_id")
    if "extra" in db_columns:
        names.append("extra")
    sql = f"INSERT INTO {spec.table} ({', '.join(f'"{n}"' for n in names)}) VALUES ({', '.join('?' * len(names))})"
    for row in rows:
        values = [_convert(row.get(c.name, ""), c) for c in known]
        if spec.course_scoped and "course_id" in db_columns:
            values.append(course_id)
        if "extra" in db_columns:
            extra = {h: row[h] for h in unknown if row.get(h)}
            values.append(json.dumps(extra, ensure_ascii=False) if extra else None)
        conn.execute(sql, values)
    return len(rows)


def insert_rows(conn: sqlite3.Connection, tables: dict[str, Table], course_id: str) -> dict[str, int]:
    """Insert every file's rows, including id_map; return counts per table."""
    return {t.spec.table: insert_file(conn, t.spec, t.rows, t.header, course_id) for t in tables.values() if t.present}


def fill_question_node(conn: sqlite3.Connection) -> None:
    """One row per (question, node) from questions' node_ids, for joins."""
    conn.execute("DELETE FROM question_node")
    for qid, node_ids in conn.execute("SELECT id, node_ids FROM question").fetchall():
        conn.executemany("INSERT OR IGNORE INTO question_node VALUES (?, ?)", [(qid, n) for n in split_list(node_ids)])


def build_note_index(conn: sqlite3.Connection) -> None:
    """Fill note_fts from summary, key points and key wording."""
    conn.execute("DELETE FROM note_fts")
    for nid, summary, points, wording in conn.execute("SELECT id, summary, key_points, key_wording FROM note").fetchall():
        body = "\n".join([summary or "", *split_list(points), *split_list(wording)])
        conn.execute("INSERT INTO note_fts (id, body) VALUES (?, ?)", (nid, body))


class FeedbackError(Exception):
    """A feedback row that cannot be applied; the message is recorded."""


def _feedback_target(spec: FileSpec, target_id: str) -> dict[str, str]:
    parts = target_id.split("|")
    if len(parts) != len(spec.key) or not all(parts):
        raise FeedbackError(f"target_id must be {'|'.join(spec.key)}")
    return dict(zip(spec.key, parts))


def _where(target: dict[str, str]) -> tuple[str, list[str]]:
    return " AND ".join(f"{k} = ?" for k in target), list(target.values())


def _apply_feedback_row(conn: sqlite3.Connection, fb: dict[str, str], course_id: str) -> str:
    """Apply one feedback row; return a message, or raise FeedbackError."""
    for col in registry.FEEDBACK.columns:
        problem = value_error(col, fb.get(col.name, ""))
        if problem:
            raise FeedbackError(problem)
    spec = registry.FILES[registry.FEEDBACK_TABLE_FILES[fb["table"]]]
    target = _feedback_target(spec, fb["target_id"])
    where, args = _where(target)
    stamp = {"updated_by": fb["teacher"], "updated_at": fb["ts"]}
    action = fb["action"]

    if action in ("approve", "reject"):
        status = "approved" if action == "approve" else "rejected"
        cur = conn.execute(f"UPDATE {spec.table} SET status = ?, updated_by = ?, updated_at = ? WHERE {where}",
                           [status, stamp["updated_by"], stamp["updated_at"], *args])
        if not cur.rowcount:
            raise FeedbackError("target not found")
        return f"status set to {status}"

    if action == "edit":
        field_name, value = fb.get("field", ""), fb.get("value", "")
        if spec.table == "edge" and field_name == registry.EDGE_WEIGHT_FIELD:
            try:
                weight = float(value)
            except ValueError:
                raise FeedbackError(f"weight must be a number, got {value!r}") from None
            if not 0 <= weight <= 1:
                raise FeedbackError(f"weight must be between 0 and 1, got {weight}")
            if not conn.execute(f"SELECT 1 FROM edge WHERE {where}", args).fetchone():
                raise FeedbackError("target not found")
            conn.execute(
                """INSERT INTO edge_weight (from_id, to_id, type, teacher_weight) VALUES (?, ?, ?, ?)
                   ON CONFLICT (from_id, to_id, type) DO UPDATE SET teacher_weight = excluded.teacher_weight""",
                [*args, weight],
            )
            return f"link weight set to {weight}"
        column = spec.column(field_name)
        if column is None or field_name in spec.key or field_name in stamp:
            raise FeedbackError(f"cannot edit field {field_name!r}")
        problem = value_error(column, value)
        if problem:
            raise FeedbackError(problem)
        cur = conn.execute(f'UPDATE {spec.table} SET "{field_name}" = ?, updated_by = ?, updated_at = ? WHERE {where}',
                           [_convert(value, column), stamp["updated_by"], stamp["updated_at"], *args])
        if not cur.rowcount:
            raise FeedbackError("target not found")
        return f"{field_name} edited"

    # add
    row = dict(target)
    for pair in split_list(fb.get("value", "")):
        name, sep, value = pair.partition("=")
        if not sep or spec.column(name.strip()) is None:
            raise FeedbackError(f"bad add value {pair!r}: expected col=value with a known column")
        row[name.strip()] = value.strip()
    row.setdefault("status", "approved")
    row.update(stamp)
    for col in spec.columns:
        problem = value_error(col, row.get(col.name, ""))
        if problem:
            raise FeedbackError(problem)
    if conn.execute(f"SELECT 1 FROM {spec.table} WHERE {where}", args).fetchone():
        raise FeedbackError("a row with this id already exists")
    insert_file(conn, spec, [row], list(row), course_id)
    return "row added"


def apply_feedback(conn: sqlite3.Connection, feedback_csv: Path, course_id: str = "") -> list[str]:
    """Apply teacher feedback in ts order and record each action; return messages for those not applied."""
    if not feedback_csv.exists():
        return []
    with feedback_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
    not_applied = []
    for line, fb in sorted(enumerate(rows, start=2), key=lambda lr: lr[1].get("ts", "")):
        try:
            message, applied = _apply_feedback_row(conn, fb, course_id), 1
        except FeedbackError as e:
            message, applied = str(e), 0
            not_applied.append(f"{feedback_csv.name}:{line}: {fb.get('action', '')} {fb.get('table', '')} "
                               f"{fb.get('target_id', '')!r}: {message}")
        conn.execute(
            """INSERT INTO teacher_feedback (ts, teacher, tbl, target_id, action, field, value, note, applied, message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [fb.get(k, "") for k in ("ts", "teacher", "table", "target_id", "action", "field", "value", "note")] + [applied, message],
        )
    return not_applied


class Tree:
    """The non-rejected node tree, with parts under each node."""

    def __init__(self, conn: sqlite3.Connection):
        rows = conn.execute("SELECT id, parent_id, level FROM node WHERE status != 'rejected'").fetchall()
        self.level = {r["id"]: r["level"] for r in rows}
        self.parent = {r["id"]: r["parent_id"] for r in rows if r["parent_id"] in self.level}
        self.children: dict[str, list[str]] = defaultdict(list)
        for child, parent in self.parent.items():
            self.children[parent].append(child)
        self._parts: dict[str, list[str]] = {}

    def __contains__(self, node_id: str) -> bool:
        return node_id in self.level

    def parts_under(self, node_id: str) -> list[str]:
        """Parts in a node's subtree; a part gives itself."""
        if node_id not in self._parts:
            if self.level.get(node_id) == "part":
                self._parts[node_id] = [node_id]
            else:
                self._parts[node_id] = [p for c in self.children.get(node_id, []) for p in self.parts_under(c)]
        return self._parts[node_id]

    def targets(self, node_id: str) -> list[str]:
        """Where something tagged to a node lands: its parts, or the node itself if it has none."""
        return self.parts_under(node_id) or [node_id]

    def ancestors_and_self(self, node_id: str) -> list[str]:
        chain = [node_id]
        while chain[-1] in self.parent and self.parent[chain[-1]] not in chain:
            chain.append(self.parent[chain[-1]])
        return chain


def percentile_ranks(values: dict[str, float]) -> dict[str, float]:
    """Percentile rank (0–1) of each value among the others; ties share the mid rank, a lone value gets 0.5."""
    n = len(values)
    if n < 2:
        return {k: 0.5 for k in values}
    ordered = sorted(values.values())
    ranks = {}
    for key, v in values.items():
        less = sum(1 for x in ordered if x < v)
        equal = sum(1 for x in ordered if x == v)
        ranks[key] = (less + (equal - 1) / 2) / (n - 1)
    return ranks


def question_marks_by_part(conn: sqlite3.Connection, tree: Tree) -> dict[str, float]:
    """Marks of non-rejected questions split equally across their tagged nodes, then across each node's parts."""
    marks: dict[str, float] = defaultdict(float)
    for marks_total, node_ids in conn.execute("SELECT marks, node_ids FROM question WHERE status != 'rejected'"):
        tags = [n for n in split_list(node_ids) if n in tree]
        for tag in tags:
            targets = tree.targets(tag)
            for target in targets:
                marks[target] += marks_total / len(tags) / len(targets)
    return marks


def prerequisite_reach(conn: sqlite3.Connection, tree: Tree) -> dict[str, set[str]]:
    """For each part, the parts reachable from it through prerequisite edges (concept edges apply to their parts)."""
    graph: dict[str, set[str]] = defaultdict(set)
    rows = conn.execute("SELECT from_id, to_id FROM edge WHERE type = 'prerequisite' AND status != 'rejected'")
    for from_id, to_id in rows:
        if from_id in tree and to_id in tree:
            for a in tree.targets(from_id):
                graph[a].update(tree.targets(to_id))
    reach: dict[str, set[str]] = {}
    for start in graph:
        seen, stack = set(), [start]
        while stack:
            for nxt in graph.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        reach[start] = seen
    return reach


def compute_weights(conn: sqlite3.Connection, settings: Settings) -> None:
    """Fill node_weight with exam_weight, dependents and importance.

    exam_weight: share of all question marks tagged to the node or its descendants (the course sums to 1).
    dependents: parts reachable from the node's parts through prerequisite edges.
    importance: w_exam x percentile(exam_weight) + w_dependents x percentile(dependents), ranked within each level.
    """
    tree = Tree(conn)
    part_marks = question_marks_by_part(conn, tree)
    total = sum(part_marks.values())
    raw: dict[str, float] = defaultdict(float)
    for target, m in part_marks.items():
        for node_id in tree.ancestors_and_self(target):
            raw[node_id] += m
    reach = prerequisite_reach(conn, tree)

    exam_weight, dependents = {}, {}
    for node_id in tree.level:
        exam_weight[node_id] = raw[node_id] / total if total else 0.0
        own = set(tree.targets(node_id))
        reached = set().union(*(reach.get(p, set()) for p in own))
        dependents[node_id] = len(reached - own)

    importance = {}
    for level in set(tree.level.values()):
        ids = [i for i, lv in tree.level.items() if lv == level]
        pe = percentile_ranks({i: exam_weight[i] for i in ids})
        pd = percentile_ranks({i: float(dependents[i]) for i in ids})
        for i in ids:
            importance[i] = settings.importance.w_exam * pe[i] + settings.importance.w_dependents * pd[i]

    conn.execute("DELETE FROM node_weight")
    conn.executemany("INSERT INTO node_weight VALUES (?, ?, ?, ?)",
                     [(i, exam_weight[i], dependents[i], importance[i]) for i in tree.level])


def question_tags(conn: sqlite3.Connection, tree: Tree) -> dict[str, tuple[int, set[str]]]:
    """For each non-rejected question: its marks and the parts it touches, from its own tags and its mark-scheme items'."""
    tags: dict[str, tuple[int, set[str]]] = {}
    for qid, marks, node_ids in conn.execute("SELECT id, marks, node_ids FROM question WHERE status != 'rejected'"):
        tags[qid] = (marks, {p for n in split_list(node_ids) if n in tree for p in tree.targets(n)})
    for qid, node_ids in conn.execute("SELECT question_id, node_ids FROM mark_scheme_item WHERE status != 'rejected'"):
        if qid in tags:
            tags[qid][1].update(p for n in split_list(node_ids) if n in tree for p in tree.targets(n))
    return tags


def material_sections(conn: sqlite3.Connection, tree: Tree, source_types: list[str]) -> list[set[str]]:
    """Parts covered by each section (source + location) of the teaching materials."""
    sections: dict[tuple[str, str], set[str]] = defaultdict(set)
    rows = conn.execute(
        f"""SELECT n.source_id, n.location, n.node_id FROM note n JOIN source s ON s.id = n.source_id
            WHERE n.status != 'rejected' AND coalesce(n.location, '') != ''
            AND s.type IN ({', '.join('?' * len(source_types))})""",
        source_types,
    )
    for source_id, location, node_id in rows:
        if node_id in tree:
            sections[(source_id, location)].update(tree.targets(node_id))
    return list(sections.values())


def compute_link_weights(conn: sqlite3.Connection, settings: Settings) -> list[str]:
    """Fill edge_weight from exam and teaching-material co-occurrence; return suggested links.

    computed = base + (1 - base) x (w_exam x exam_marks / max + w_material x material_count / max).
    weight = teacher_weight when a teacher set one, else computed.
    """
    lw = settings.link_weight
    tree = Tree(conn)
    questions = question_tags(conn, tree)
    sections = material_sections(conn, tree, lw.material_source_types)

    stats = []
    for from_id, to_id, etype in conn.execute("SELECT from_id, to_id, type FROM edge").fetchall():
        a, b = set(tree.targets(from_id)), set(tree.targets(to_id))
        linked = [m for m, parts in questions.values() if parts & a and parts & b]
        material = sum(1 for parts in sections if parts & a and parts & b)
        stats.append((from_id, to_id, etype, len(linked), float(sum(linked)), material))

    max_marks = max((s[4] for s in stats), default=0) or 1
    max_material = max((s[5] for s in stats), default=0) or 1
    rows = []
    for from_id, to_id, etype, n_questions, marks, material in stats:
        evidence = lw.w_exam * marks / max_marks + lw.w_material * material / max_material
        rows.append((from_id, to_id, etype, n_questions, marks, material, lw.base + (1 - lw.base) * evidence))
    conn.executemany(
        """INSERT INTO edge_weight (from_id, to_id, type, exam_questions, exam_marks, material_count, computed, weight)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?7)
           ON CONFLICT (from_id, to_id, type) DO UPDATE SET exam_questions = excluded.exam_questions,
             exam_marks = excluded.exam_marks, material_count = excluded.material_count, computed = excluded.computed,
             weight = coalesce(edge_weight.teacher_weight, excluded.computed)""",
        rows,
    )
    return suggest_links(conn, tree, questions, lw.suggest_min_questions)


def suggest_links(conn: sqlite3.Connection, tree: Tree, questions: dict[str, tuple[int, set[str]]], min_questions: int) -> list[str]:
    """Pairs of parts in different concepts that enough questions test together but no edge connects."""
    together: dict[tuple[str, str], int] = defaultdict(int)
    for _, parts in questions.values():
        for p in parts:
            for q in parts:
                if p < q and tree.parent.get(p) != tree.parent.get(q):
                    together[(p, q)] += 1
    linked = set()
    for from_id, to_id in conn.execute("SELECT from_id, to_id FROM edge WHERE status != 'rejected'"):
        if from_id in tree and to_id in tree:
            for p in tree.targets(from_id):
                for q in tree.targets(to_id):
                    linked.update({(p, q), (q, p)})
    return [f"{p} <-> {q}: tested together in {n} questions"
            for (p, q), n in sorted(together.items(), key=lambda kv: -kv[1]) if n >= min_questions and (p, q) not in linked]


def build_node_index(conn: sqlite3.Connection) -> None:
    """Fill node_fts from each node's name, aliases and description, so students' own words find nodes."""
    conn.execute("DELETE FROM node_fts")
    for nid, name, aliases, description in conn.execute("SELECT id, name, aliases, description FROM node").fetchall():
        conn.execute("INSERT INTO node_fts (id, name, aliases, description) VALUES (?, ?, ?, ?)",
                     (nid, name, " ".join(split_list(aliases)), description))


def count_rows(conn: sqlite3.Connection) -> dict[str, int]:
    """Row counts for every table loaded from the pack plus derived tables."""
    tables = [s.table for s in registry.FILES.values()] + ["question_node", "node_weight", "edge_weight", "teacher_feedback"]
    return {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in tables}


def flagged_rows(conn: sqlite3.Connection) -> tuple[list[str], list[str]]:
    """Served rows that extraction flagged, and nodes with extraction_confidence below 0.5."""
    flagged = []
    for spec in registry.FILES.values():
        if not spec.content_row:
            continue
        key = " || '|' || ".join(spec.key)
        rows = conn.execute(f"SELECT {key}, flag FROM {spec.table} WHERE flag != '' AND status != 'rejected'")
        flagged += [f"{spec.name} {k}: {flag}" for k, flag in rows]
    low = [f"nodes.csv {i}: {c}" for i, c in conn.execute(
        "SELECT id, extraction_confidence FROM node WHERE extraction_confidence < 0.5 AND status != 'rejected'")]
    return flagged, low


def write_load_info(conn: sqlite3.Connection, report: LoadReport) -> None:
    """Record when and what was loaded."""
    summary = json.dumps({
        "counts": report.counts,
        "warnings": len(report.warnings),
        "flagged": len(report.flagged),
        "low_confidence": len(report.low_confidence),
        "feedback_not_applied": len(report.feedback_not_applied),
        "suggested_links": len(report.suggested_links),
    })
    conn.execute("DELETE FROM load_info")
    conn.execute("INSERT INTO load_info VALUES (?, ?, ?, ?)",
                 (datetime.now(timezone.utc).isoformat(timespec="seconds"), report.course_id, report.pack_path, summary))


def _section(title: str, lines: list[str]) -> None:
    print(f"\n{title} ({len(lines)})")
    for line in lines:
        print(f"  {line}")


def print_report(report: LoadReport) -> None:
    """Print the load report."""
    if report.errors:
        for issue in report.errors:
            print(f"ERROR   {issue}")
        print(f"\nNot loaded: {len(report.errors)} error(s). content.db was not changed.")
        return
    print(f"Loaded {report.course_id} from {report.pack_path}")
    print(f"into {report.db_path}")
    print("\nRows")
    for table, n in report.counts.items():
        print(f"  {table:18} {n}")
    _section("Warnings", report.warnings)
    _section("Flagged rows", report.flagged)
    _section("Extraction confidence below 0.5", report.low_confidence)
    _section("Teacher feedback not applied", report.feedback_not_applied)
    _section("Suggested links", report.suggested_links)
