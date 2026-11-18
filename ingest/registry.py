"""Every course-pack file and column, defined once.

Validation, loading, the empty CSV templates and coursepacks/README.md are generated
from these definitions. Adding a column is one line here.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

TYPES = ("text", "int", "real", "date", "list")

STATUSES = ("draft", "approved", "rejected")
LEVELS = ("topic", "subtopic", "concept", "part")
PART_TYPES = ("definition", "calculation", "diagram", "mechanism", "evaluation", "application")
EDGE_TYPES = ("prerequisite", "analogous", "confusable", "causal")
TEACH_USES = ("intuition", "contrast", "none")
SOURCE_TYPES = ("specification", "mark_scheme", "examiner_report", "question_paper", "textbook", "teacher", "ours")
QUESTION_FORMATS = ("mcq", "short", "data_response", "essay")
MARK_SCHEME_KINDS = ("point", "level", "indicative")
FEEDBACK_TABLES = ("nodes", "edges", "notes", "misconceptions", "mark_points", "questions", "mark_scheme_items")
FEEDBACK_ACTIONS = ("approve", "reject", "edit", "add")

# Teacher-feedback edit field on edges that sets the link weight rather than an edge column.
EDGE_WEIGHT_FIELD = "weight"

# The AI-literacy mini pack (step 05e): committed, and read in with every pack. Its nodes sit under this topic.
AI_LITERACY_DIR = Path(__file__).resolve().parent / "ai_literacy"
AI_LITERACY_TOPIC = "ai_literacy"


@dataclass(frozen=True)
class Column:
    """One CSV column: type, required flag, allowed values, default and meaning."""

    name: str
    type: str = "text"
    required: bool = False
    enum: tuple[str, ...] = ()
    default: str | None = None
    doc: str = ""
    bounds: tuple[float, float] | None = None


@dataclass(frozen=True)
class FileSpec:
    """One course-pack CSV file and the content.db table it loads into."""

    name: str
    table: str
    columns: tuple[Column, ...]
    key: tuple[str, ...] = ("id",)
    content_row: bool = False
    required_file: bool = False
    course_scoped: bool = False
    doc: str = ""

    @property
    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    def column(self, name: str) -> Column | None:
        return next((c for c in self.columns if c.name == name), None)


def C(name: str, type: str = "text", required: bool = False, enum: tuple[str, ...] = (), default: str | None = None,
      doc: str = "", bounds: tuple[float, float] | None = None) -> Column:
    return Column(name, type, required, enum, default, doc, bounds)


CONTENT_COLUMNS = (
    C("status", enum=STATUSES, default="draft", doc="draft / approved / rejected"),
    C("flag", default="", doc="blank, or a short reason extraction thinks the row may be wrong"),
    C("updated_by", default="extraction", doc="`extraction`, or a teacher's name"),
    C("updated_at", doc="ISO datetime"),
)


def _content(*columns: Column) -> tuple[Column, ...]:
    return columns + CONTENT_COLUMNS


_FILES = (
    FileSpec("course.csv", "course", (
        C("id", required=True, doc="course id, e.g. `edexcel-econ-a`"),
        C("name", required=True, doc="e.g. `A level Economics A`"),
        C("exam_board", doc="e.g. `Pearson Edexcel`"),
        C("spec_code", doc="e.g. `9EC0`"),
        C("spec_version", doc="version or first-teaching year; past papers from an earlier year are rejected"),
    ), required_file=True, doc="One row."),
    FileSpec("exam_papers.csv", "exam_paper", (
        C("id", required=True, doc="e.g. `paper1`"),
        C("name", doc="e.g. `Paper 1: Markets and business behaviour`"),
        C("date", "date", doc="ISO date of the next sitting"),
        C("node_ids", "list", doc="topics this paper examines (descendants included)"),
    ), course_scoped=True, doc="The papers students will sit."),
    FileSpec("sources.csv", "source", (
        C("id", required=True, doc="e.g. `spec`, `ms_2024_p1`, `tb_main`"),
        C("type", required=True, enum=SOURCE_TYPES, doc="source type; sets its authority in settings.toml"),
        C("title", doc="full title"),
        C("edition", doc="edition, version or exam series"),
        C("reference", doc="URL or catalogue reference"),
        C("notes", doc="licence, chapters used, etc."),
    ), required_file=True, course_scoped=True, doc="Every document the pack was built from."),
    FileSpec("nodes.csv", "node", _content(
        C("id", required=True, doc="e.g. `ped_formula`"),
        C("parent_id", doc="blank only for top-level topics"),
        C("level", required=True, enum=LEVELS, doc="topic / subtopic / concept / part"),
        C("name", required=True, doc="e.g. `Price elasticity of demand: formula`"),
        C("aliases", "list", default="", doc="other names students use"),
        C("spec_ref", default="", doc="specification section, e.g. `4.1.3.2`"),
        C("part_type", enum=PART_TYPES, doc="parts only"),
        C("description", required=True, doc="one or two sentences in our own words"),
        C("source_ids", "list", default="", doc="ids from sources.csv"),
        C("extraction_confidence", "real", default="1.0", doc="0–1", bounds=(0, 1)),
        C("difficulty", "real", doc="optional, 0 (easy) to 1 (hard); blank inherits from the nearest ancestor, else average", bounds=(0, 1)),
        C("intuition", default="", doc="parts only: one line in everyday language that leads into the idea; the source of the intuition question when no known part links in"),
        C("diagram", enum=("true", "false"), default="false", doc="parts only, optional: `true` when the content is a diagram (supply and demand shifts, a tax wedge, externalities, AD/AS), so teaching includes a labelled diagram or asks for a sketch. Set by the content, never by the student"),
    ), content_row=True, required_file=True, course_scoped=True, doc="The knowledge tree."),
    FileSpec("edges.csv", "edge", _content(
        C("from_id", required=True, doc="node id"),
        C("to_id", required=True, doc="node id"),
        C("type", required=True, enum=EDGE_TYPES, doc="prerequisite / analogous / confusable / causal"),
        C("note", default="", doc="what the link means, e.g. what maps onto what, or how A affects B; required when `teach_use` is `intuition`, a warning if missing elsewhere"),
        C("confidence", "real", default="0.8", doc="0–1", bounds=(0, 1)),
        C("source_ids", "list", default="", doc="where the link is evidenced"),
        C("teach_use", enum=TEACH_USES, default="none",
          doc="`intuition` (the `from` part can lead into the `to` part), `contrast` (use it to show the difference) or `none`"),
    ), key=("from_id", "to_id", "type"), content_row=True, required_file=True,
        doc="Typed links between nodes. An edge on a concept applies to all its parts."),
    FileSpec("notes.csv", "note", _content(
        C("id", required=True, doc="e.g. `ped_formula_n1`"),
        C("node_id", required=True, doc="usually a part"),
        C("summary", required=True, doc="our own words, ≤ ~80 words (error over 120)"),
        C("key_points", "list", default="", doc="short points"),
        C("key_wording", "list", default="", doc="short phrases that earn marks, each < 15 words"),
        C("source_id", doc="id from sources.csv"),
        C("location", doc="page, section or question reference"),
    ), content_row=True, required_file=True, doc="What the chatbot answers from."),
    FileSpec("misconceptions.csv", "misconception", _content(
        C("id", required=True, doc="e.g. `ped_values_m1`"),
        C("node_id", required=True, doc="a part"),
        C("wrong_idea", required=True, doc="as a student might hold it"),
        C("correction", required=True, doc="one or two sentences"),
        C("source_ids", "list", default="", doc="examiner reports first where possible"),
    ), content_row=True),
    FileSpec("mark_points.csv", "mark_point", _content(
        C("id", required=True, doc="e.g. `ped_formula_p1`"),
        C("node_id", required=True, doc="a part"),
        C("point", required=True, doc="one sentence"),
        C("exemplar", default="", doc="short model answer fragment"),
        C("source_ids", "list", required=True, doc="the specification or textbook section the point is based on"),
        C("order", "int", doc="position within the part (1, 2, ...); points are taught and scored in this order"),
    ), content_row=True, doc="Our fallback points, for parts past papers don't test."),
    FileSpec("past_papers.csv", "past_paper", (
        C("id", required=True, doc="e.g. `2024_06_p1`"),
        C("exam_paper_id", required=True, doc="id in exam_papers.csv"),
        C("series", doc="e.g. `June 2024`"),
        C("question_source_id", doc="id in sources.csv"),
        C("mark_scheme_source_id", doc="id in sources.csv"),
        C("examiner_report_source_id", doc="id in sources.csv; may be blank"),
    ), course_scoped=True),
    FileSpec("questions.csv", "question", _content(
        C("id", required=True, doc="e.g. `2024_06_p1_q03_2`"),
        C("past_paper_id", required=True, doc="id in past_papers.csv"),
        C("number", doc="as printed, `03.2`"),
        C("marks", "int", required=True, doc="integer"),
        C("command_word", doc="`Define` / `Calculate` / `Explain` / `Analyse` / `Evaluate` / ..."),
        C("format", enum=QUESTION_FORMATS, doc="mcq / short / data_response / essay"),
        C("assessment_objectives", "list", doc="e.g. `AO1;AO2`"),
        C("node_ids", "list", required=True, doc="parts (preferred) or concepts it tests"),
        C("summary", doc="what it asks, in our own words"),
    ), content_row=True),
    FileSpec("mark_scheme_items.csv", "mark_scheme_item", _content(
        C("id", required=True, doc="e.g. `2024_06_p1_q03_2_i1`"),
        C("question_id", required=True, doc="id in questions.csv"),
        C("kind", enum=MARK_SCHEME_KINDS, doc="point / level / indicative"),
        C("marks", "int", doc="marks available, for `point`"),
        C("level", "int", doc="level number, for `level`"),
        C("text", required=True, doc="our paraphrase plus any short key wording (< 15 words)"),
        C("node_ids", "list", default="", doc="parts this item relates to"),
    ), content_row=True),
    FileSpec("trusted_sources.csv", "trusted_source", _content(
        C("id", required=True, doc="e.g. `ons_inflation`, so teacher feedback can target the row"),
        C("node_id", required=True, doc="a topic or concept the source is good for (its descendants included)"),
        C("name", required=True, doc="e.g. `ONS`"),
        C("url", required=True, doc="the landing page for this kind of data (http or https)"),
        C("what_for", required=True, doc="one line, e.g. `UK inflation and price indices`"),
    ), content_row=True, doc="Optional. Sources research answers point to first, per topic (step 05e)."),
    FileSpec("id_map.csv", "id_map", (
        C("old_id", required=True, doc="an id that was renamed"),
        C("new_id", required=True, doc="what it became"),
    ), key=("old_id",), doc="Optional. Renamed ids."),
)

FILES: dict[str, FileSpec] = {f.name: f for f in _FILES}

FEEDBACK = FileSpec("teacher_feedback/<course_id>.csv", "teacher_feedback", (
    C("ts", required=True, doc="ISO datetime"),
    C("teacher", required=True, doc="name"),
    C("table", required=True, enum=FEEDBACK_TABLES, doc="the pack file the target is in, without `.csv`"),
    C("target_id", required=True, doc="id; for an edge, `from_id|to_id|type`"),
    C("action", required=True, enum=FEEDBACK_ACTIONS, doc="approve / reject / edit / add"),
    C("field", doc="for edit: column to change; on edges, `weight` sets the link weight (0–1)"),
    C("value", doc="for edit: new value; for add: `col=value;col=value`"),
    C("note", doc="free text"),
), key=(), doc="Teacher feedback overlay, applied in `ts` order after every load.")

FEEDBACK_TABLE_FILES: dict[str, str] = {t: f"{t}.csv" for t in FEEDBACK_TABLES}


def get(file_name: str) -> FileSpec:
    """The spec for a course-pack file, e.g. "nodes.csv"."""
    return FILES[file_name]


def split_list(cell: str | None) -> list[str]:
    """Split a ;-separated cell, honouring \\; as a literal semicolon; blanks are dropped."""
    if not cell:
        return []
    items, current, i = [], [], 0
    while i < len(cell):
        ch = cell[i]
        if ch == "\\" and i + 1 < len(cell) and cell[i + 1] == ";":
            current.append(";")
            i += 2
            continue
        if ch == ";":
            items.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    items.append("".join(current))
    return [item.strip() for item in items if item.strip()]


def write_templates(out_dir: Path) -> list[Path]:
    """Write a header-only CSV for every file; return the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for spec in FILES.values():
        path = out_dir / spec.name
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerow(spec.column_names)
        written.append(path)
    return written


def _file_section(spec: FileSpec) -> list[str]:
    lines = [f"### {spec.name}", ""]
    if spec.doc:
        lines += [spec.doc, ""]
    lines += ["| column | type | required | allowed values | default | meaning |", "|---|---|---|---|---|---|"]
    for c in spec.columns:
        enum = " / ".join(f"`{v}`" for v in c.enum)
        default = "" if c.default in (None, "") else f"`{c.default}`"
        lines.append(f"| {c.name} | {c.type} | {'yes' if c.required else ''} | {enum} | {default} | {c.doc} |")
    return lines + [""]


def render_readme() -> str:
    """Markdown description of every file and column, for coursepacks/README.md."""
    lines = [
        "# Course packs",
        "",
        "Generated from `ingest/registry.py` by `python -m ingest.cli readme`. Do not edit by hand.",
        "",
        "A course pack is a folder of UTF-8 CSV files in `coursepacks/<course_id>/`. "
        "See `docs/build/reference/course-pack-format.md` for the rules. "
        "`python -m ingest.cli templates <dir>` writes empty templates.",
        "",
        "- Lists inside a cell are separated by `;`, with `\\;` for a literal semicolon.",
        "- Unknown extra columns are kept in the row's `extra` JSON column.",
        "- Real packs live in `coursepacks/<id>/private/`, which is git-ignored "
        "(the Pearson Edexcel A level Economics A (9EC0) pack: `coursepacks/edexcel-econ-a/private/`).",
        "",
        "## Files",
        "",
    ]
    for spec in FILES.values():
        lines += _file_section(spec)
    lines += ["## Teacher feedback", ""] + _file_section(FEEDBACK)
    return "\n".join(lines).rstrip() + "\n"
