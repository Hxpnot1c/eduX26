"""Validate a course pack against the registry and the format rules.

All errors and warnings are collected rather than stopping at the first.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from edux.settings import load_settings
from ingest import registry
from ingest.registry import FileSpec, split_list

MAX_KEY_WORDING_WORDS = 15  # a key wording must be shorter than this
MAX_SUMMARY_WORDS = 120
LOW_CONFIDENCE = 0.5
URL = re.compile(r"https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(:\d+)?(/\S*)?")


@dataclass
class Issue:
    """One error or warning, with where it was found."""

    file: str
    row: int | None
    message: str

    def __str__(self) -> str:
        where = self.file if self.row is None else f"{self.file}:{self.row}"
        return f"{where}: {self.message}"


@dataclass
class ValidationResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class Table:
    """One pack file as read: its header and rows (raw strings, with the CSV line number under "_line")."""

    spec: FileSpec
    present: bool
    header: list[str] = field(default_factory=list)
    rows: list[dict[str, str]] = field(default_factory=list)


def _read_dir(pack_dir: Path) -> dict[str, Table]:
    tables = {}
    for spec in registry.FILES.values():
        path = pack_dir / spec.name
        if not path.exists():
            tables[spec.name] = Table(spec, present=False)
            continue
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header = [h.strip() for h in reader.fieldnames or []]
            rows = []
            for line, raw in enumerate(reader, start=2):
                row = {(k or "").strip(): (v or "").strip() if isinstance(v, str) else "" for k, v in raw.items()}
                row["_line"] = str(line)
                rows.append(row)
        tables[spec.name] = Table(spec, True, header, rows)
    return tables


def read_pack(pack_dir: Path, ai_literacy: bool = True) -> dict[str, Table]:
    """Read every registry file in the pack; a missing file gives an empty table. The AI-literacy mini pack
    (ingest/ai_literacy/) is read in with every pack: its rows are added to the pack's own (their line
    numbers are the mini pack's, so an issue on one names a line there)."""
    tables = _read_dir(pack_dir)
    if not ai_literacy or pack_dir.resolve() == registry.AI_LITERACY_DIR:
        return tables
    for name, extra in _read_dir(registry.AI_LITERACY_DIR).items():
        if not extra.present:
            continue
        table = tables[name]
        header = table.header + [h for h in extra.header if h not in table.header]
        tables[name] = Table(table.spec, True, header, table.rows + extra.rows)
    return tables


def row_key(spec: FileSpec, row: dict[str, str]) -> str:
    """The row's id, or from_id|to_id|type for an edge."""
    return "|".join(row.get(k, "") for k in spec.key)


def value_error(col: registry.Column, value: str) -> str | None:
    """Why a cell value is invalid for its column (required, type, enum), or None if it is fine."""
    if not value or (col.type == "list" and not split_list(value)):
        return f"{col.name} is required" if col.required else None
    parsers = {"int": (int, "an integer"), "real": (float, "a number"), "date": (date.fromisoformat, "an ISO date")}
    if col.type in parsers:
        parse, what = parsers[col.type]
        try:
            parsed = parse(value)
        except ValueError:
            return f"{col.name} must be {what}, got {value!r}"
        if col.bounds and not col.bounds[0] <= parsed <= col.bounds[1]:
            return f"{col.name} must be between {col.bounds[0]} and {col.bounds[1]}, got {parsed}"
    if col.enum and value not in col.enum:
        return f"{col.name} {value!r} is not one of {', '.join(col.enum)}"
    return None


def _words(text: str) -> int:
    return len(text.split())


class _Checker:
    def __init__(self, tables: dict[str, Table]):
        self.t = tables
        self.result = ValidationResult()

    def error(self, file: str, row: dict | None, message: str) -> None:
        self.result.errors.append(Issue(file, int(row["_line"]) if row else None, message))

    def warn(self, file: str, row: dict | None, message: str) -> None:
        self.result.warnings.append(Issue(file, int(row["_line"]) if row else None, message))

    def rows(self, name: str) -> list[dict[str, str]]:
        return self.t[name].rows

    def ids(self, name: str) -> set[str]:
        return {r["id"] for r in self.rows(name) if r.get("id")}

    # --- per file -------------------------------------------------------

    def check_files(self) -> None:
        for name, table in self.t.items():
            spec = table.spec
            if not table.present:
                if spec.required_file:
                    self.error(name, None, "required file is missing")
                continue
            missing = [c.name for c in spec.columns if c.required and c.name not in table.header]
            if missing:
                self.error(name, None, f"missing required column(s): {', '.join(missing)}")
            seen: dict[str, int] = {}
            for row in table.rows:
                self.check_row(spec, row)
                key = row_key(spec, row)
                if key.strip("|"):
                    if key in seen:
                        self.error(name, row, f"duplicate id {key!r} (first on line {seen[key]})")
                    else:
                        seen[key] = int(row["_line"])

    def check_row(self, spec: FileSpec, row: dict[str, str]) -> None:
        for col in spec.columns:
            problem = value_error(col, row.get(col.name, ""))
            if problem:
                self.error(spec.name, row, problem)

    # --- references -----------------------------------------------------

    def check_refs(self) -> None:
        nodes, sources = self.ids("nodes.csv"), self.ids("sources.csv")
        exam_papers, past_papers = self.ids("exam_papers.csv"), self.ids("past_papers.csv")
        questions = self.ids("questions.csv")

        def ref(file: str, row: dict, column: str, known: set[str], what: str, is_list: bool = False) -> None:
            values = split_list(row.get(column, "")) if is_list else [row.get(column, "")]
            for v in values:
                if v and v not in known:
                    self.error(file, row, f"{column}: unknown {what} {v!r}")

        for r in self.rows("exam_papers.csv"):
            ref("exam_papers.csv", r, "node_ids", nodes, "node", True)
        for r in self.rows("nodes.csv"):
            ref("nodes.csv", r, "parent_id", nodes, "node")
            ref("nodes.csv", r, "source_ids", sources, "source", True)
        for r in self.rows("edges.csv"):
            ref("edges.csv", r, "from_id", nodes, "node")
            ref("edges.csv", r, "to_id", nodes, "node")
            ref("edges.csv", r, "source_ids", sources, "source", True)
        for r in self.rows("notes.csv"):
            ref("notes.csv", r, "node_id", nodes, "node")
            ref("notes.csv", r, "source_id", sources, "source")
        for name in ("misconceptions.csv", "mark_points.csv"):
            for r in self.rows(name):
                ref(name, r, "node_id", nodes, "node")
                ref(name, r, "source_ids", sources, "source", True)
        for r in self.rows("past_papers.csv"):
            ref("past_papers.csv", r, "exam_paper_id", exam_papers, "exam paper")
            for col in ("question_source_id", "mark_scheme_source_id", "examiner_report_source_id"):
                ref("past_papers.csv", r, col, sources, "source")
        for r in self.rows("questions.csv"):
            ref("questions.csv", r, "past_paper_id", past_papers, "past paper")
            ref("questions.csv", r, "node_ids", nodes, "node", True)
        for r in self.rows("mark_scheme_items.csv"):
            ref("mark_scheme_items.csv", r, "question_id", questions, "question")
            ref("mark_scheme_items.csv", r, "node_ids", nodes, "node", True)
        for r in self.rows("trusted_sources.csv"):
            ref("trusted_sources.csv", r, "node_id", nodes, "node")
            if r.get("url") and not URL.fullmatch(r["url"]):
                self.error("trusted_sources.csv", r, f"url {r['url']!r} is not an http or https address")
        all_ids = set().union(*(self.ids(n) for n in registry.FILES if n not in ("id_map.csv", "course.csv")))
        for r in self.rows("id_map.csv"):
            if r.get("old_id") in all_ids:
                self.error("id_map.csv", r, f"old_id {r['old_id']!r} is still in use")
            if r.get("new_id") and r["new_id"] not in all_ids:
                self.error("id_map.csv", r, f"new_id: unknown id {r['new_id']!r}")

    # --- content rules --------------------------------------------------

    def check_course(self) -> None:
        rows = self.rows("course.csv")
        if self.t["course.csv"].present and len(rows) != 1:
            self.error("course.csv", None, f"must have exactly one row, found {len(rows)}")
        spec_version = rows[0].get("spec_version", "") if rows else ""
        if not re.fullmatch(r"\d{4}", spec_version):
            return
        first_year = int(spec_version)
        for r in self.rows("past_papers.csv"):
            years = re.findall(r"\b(\d{4})\b", r.get("series", ""))
            if years and int(years[0]) < first_year:
                self.error("past_papers.csv", r, f"series {r['series']!r} predates specification version {spec_version}")

    def check_tree(self) -> None:
        by_id = {r["id"]: r for r in self.rows("nodes.csv") if r.get("id")}
        allowed_parents = {"part": {"concept"}, "concept": {"subtopic", "topic"}, "subtopic": {"topic", "subtopic"}}
        for r in self.rows("nodes.csv"):
            level, parent_id = r.get("level", ""), r.get("parent_id", "")
            if level == "topic":
                if parent_id:
                    self.error("nodes.csv", r, "a topic must not have a parent")
            elif level in allowed_parents:
                parent = by_id.get(parent_id)
                if not parent_id:
                    self.error("nodes.csv", r, f"a {level} must have a parent")
                elif parent and parent.get("level") not in allowed_parents[level]:
                    self.error("nodes.csv", r, f"a {level}'s parent must be a {' or '.join(sorted(allowed_parents[level]))}, "
                               f"but {parent_id!r} is a {parent.get('level')}")
            if level == "part" and not r.get("part_type"):
                self.error("nodes.csv", r, "part_type is required for parts")
            if level != "part" and r.get("part_type"):
                self.error("nodes.csv", r, "part_type is for parts only")
        # parent cycles would loop forever later; catch them here
        for start in by_id:
            seen, current = set(), start
            while current in by_id and current not in seen:
                seen.add(current)
                current = by_id[current].get("parent_id", "")
            if current == start:
                self.error("nodes.csv", by_id[start], f"parent chain loops back to {start!r}")
        parts = {i for i, r in by_id.items() if r.get("level") == "part"}
        for name in ("misconceptions.csv", "mark_points.csv"):
            for r in self.rows(name):
                if r.get("node_id") in by_id and r["node_id"] not in parts:
                    self.error(name, r, f"node_id {r['node_id']!r} must be a part")

    def check_edges(self) -> None:
        graph: dict[str, list[str]] = defaultdict(list)
        for r in self.rows("edges.csv"):
            etype = r.get("type", "")
            if r.get("from_id") and r.get("from_id") == r.get("to_id"):
                self.error("edges.csv", r, "an edge cannot link a node to itself")
            if not r.get("note"):   # the intuition question is built from the note, so it can't be missing there
                if r.get("teach_use") == "intuition":
                    self.error("edges.csv", r, "an edge with teach_use = intuition needs a note")
                else:
                    self.warn("edges.csv", r, f"{'an' if etype[:1] in 'aeiou' else 'a'} {etype or 'untyped'} edge has no note")
            if etype == "prerequisite" and r.get("status") != "rejected":
                graph[r.get("from_id", "")].append(r.get("to_id", ""))
        for cycle in _find_cycles(graph):
            self.error("edges.csv", None, "prerequisite cycle: " + " -> ".join(cycle))

    def check_order(self) -> None:
        """A mark point's order must be unique within its part."""
        seen: dict[tuple[str, str], int] = {}
        for r in self.rows("mark_points.csv"):
            order = r.get("order", "")
            if not order:
                continue
            key = (r.get("node_id", ""), order)
            if key in seen:
                self.error("mark_points.csv", r, f"order {order} is already used on {key[0]!r} (line {seen[key]})")
            else:
                seen[key] = int(r["_line"])

    def check_values(self) -> None:
        for r in self.rows("nodes.csv"):
            try:
                value = float(r.get("extraction_confidence") or "nan")
            except ValueError:
                continue
            if 0 <= value < LOW_CONFIDENCE:
                self.warn("nodes.csv", r, f"extraction_confidence {value} is below {LOW_CONFIDENCE}")
        for r in self.rows("notes.csv"):
            n = _words(r.get("summary", ""))
            if n > MAX_SUMMARY_WORDS:
                self.error("notes.csv", r, f"summary has {n} words (max {MAX_SUMMARY_WORDS})")
            for wording in split_list(r.get("key_wording", "")):
                if _words(wording) >= MAX_KEY_WORDING_WORDS:
                    self.error("notes.csv", r, f"key wording has {_words(wording)} words (must be under {MAX_KEY_WORDING_WORDS}): {wording[:40]!r}...")

    # --- warnings -------------------------------------------------------

    def check_coverage(self) -> None:
        by_id = {r["id"]: r for r in self.rows("nodes.csv") if r.get("id")}

        def lineage(node_id: str) -> list[str]:
            chain, seen = [], set()
            while node_id in by_id and node_id not in seen:
                seen.add(node_id)
                chain.append(node_id)
                node_id = by_id[node_id].get("parent_id", "")
            return chain

        tested: set[str] = set()
        for r in self.rows("questions.csv"):
            tested.update(split_list(r.get("node_ids", "")))
        for r in self.rows("mark_scheme_items.csv"):
            tested.update(split_list(r.get("node_ids", "")))
        covered = tested | {r.get("node_id") for r in self.rows("mark_points.csv")} | {r.get("node_id") for r in self.rows("notes.csv")}
        settings = load_settings()
        misconception_count: dict[str, int] = defaultdict(int)
        for r in self.rows("misconceptions.csv"):
            if r.get("status") != "rejected":
                misconception_count[r.get("node_id", "")] += 1
        points: dict[str, int] = defaultdict(int)
        for r in self.rows("mark_points.csv"):
            if r.get("status") != "rejected":
                points[r.get("node_id", "")] += 1
        for r in self.rows("notes.csv"):   # a part with no mark points is taught from its notes' key points
            if r.get("status") != "rejected":
                points["notes:" + r.get("node_id", "")] += len(split_list(r.get("key_points", "")))
        with_edges: set[str] = set()
        for r in self.rows("edges.csv"):
            with_edges.update((r.get("from_id"), r.get("to_id")))
        children: dict[str, list[str]] = defaultdict(list)
        for i, r in by_id.items():
            children[r.get("parent_id", "")].append(i)

        for i, r in by_id.items():
            if registry.AI_LITERACY_TOPIC in lineage(i):   # the mini pack is ours: no exam coverage or edges
                continue
            level = r.get("level")
            if level == "part":
                if not points[i]:
                    self.warn("nodes.csv", r, f"part {i!r} has no mark points: its checks are open (explain-back), "
                              "not multiple choice")
                if not covered.intersection(lineage(i)):
                    self.warn("nodes.csv", r, f"part {i!r} has no question, mark point or note")
                if misconception_count[i] < settings.mcq.min_distractors:
                    self.warn("nodes.csv", r, f"part {i!r} has {misconception_count[i]} misconception(s), "
                              f"fewer than mcq.min_distractors ({settings.mcq.min_distractors})")
                n = points[i] or points["notes:" + i]
                if n and not settings.points.warn_min <= n <= settings.points.warn_max:
                    self.warn("nodes.csv", r, f"part {i!r} has {n} point(s), outside points.warn_min to "
                              f"points.warn_max ({settings.points.warn_min}–{settings.points.warn_max})")
                if not r.get("intuition"):
                    self.warn("nodes.csv", r, f"part {i!r} has no intuition line")
                if not with_edges.intersection(lineage(i)[:2]):
                    self.warn("nodes.csv", r, f"part {i!r} has no edges (on itself or its concept)")
            elif level == "concept":
                kids = children.get(i, [])
                if not any(by_id[k].get("level") == "part" for k in kids):
                    self.warn("nodes.csv", r, f"concept {i!r} has no parts")
                elif i not in with_edges and not with_edges.intersection(kids):
                    self.warn("nodes.csv", r, f"concept {i!r} has no edges (on itself or its parts)")

        items_by_question: dict[str, list[dict]] = defaultdict(list)
        for r in self.rows("mark_scheme_items.csv"):
            items_by_question[r.get("question_id", "")].append(r)
        for q in self.rows("questions.csv"):
            items = [i for i in items_by_question.get(q.get("id", ""), []) if i.get("kind") == "point"]
            if not items:
                continue
            try:
                total, expected = sum(int(i.get("marks") or 0) for i in items), int(q.get("marks") or 0)
            except ValueError:
                continue
            if total != expected:
                self.warn("questions.csv", q, f"mark-scheme points add up to {total}, question is worth {expected}")


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Each distinct cycle in a directed graph, as a path that starts and ends on the same node."""
    white, grey, black = 0, 1, 2
    colour: dict[str, int] = defaultdict(int)
    stack: list[str] = []
    cycles, seen = [], set()

    def visit(node: str) -> None:
        colour[node] = grey
        stack.append(node)
        for nxt in graph.get(node, []):
            if colour[nxt] == grey:
                cycle = stack[stack.index(nxt):] + [nxt]
                key = frozenset(cycle)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cycle)
            elif colour[nxt] == white:
                visit(nxt)
        stack.pop()
        colour[node] = black

    for node in sorted(graph):
        if colour[node] == white:
            visit(node)
    return cycles


def validate_tables(tables: dict[str, Table]) -> ValidationResult:
    """Run every check on a pack that has already been read."""
    checker = _Checker(tables)
    checker.check_files()
    checker.check_refs()
    checker.check_course()
    checker.check_tree()
    checker.check_edges()
    checker.check_order()
    checker.check_values()
    checker.check_coverage()
    return checker.result


def validate_pack(pack_dir: Path) -> ValidationResult:
    """Run every check in the course-pack format reference."""
    if not pack_dir.is_dir():
        return ValidationResult(errors=[Issue(str(pack_dir), None, "course pack folder not found")])
    return validate_tables(read_pack(pack_dir))


def print_result(result: ValidationResult) -> None:
    """Print errors, then warnings, then a one-line summary."""
    for issue in result.errors:
        print(f"ERROR   {issue}")
    for issue in result.warnings:
        print(f"warning {issue}")
    print(f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)")
