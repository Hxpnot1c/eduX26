"""Read-only lookups over content.db: tree, typed edges, notes, questions and weights.

Every lookup skips rows with status 'rejected' (a rejected node also hides everything
under it) and resolves old ids through id_map. Edges on a concept apply to all of its
parts. Lookups return full lists with the numbers needed to rank them; choosing what
reaches the chatbot is left to the context blocks.
"""

from __future__ import annotations

import functools
import sqlite3
import threading
from pathlib import Path

from edux import db
from edux.settings import Settings, load_settings
from ingest.registry import split_list

# Nodes that are not rejected and have no rejected ancestor.
VISIBLE = """WITH RECURSIVE visible(id) AS (
    SELECT id FROM node WHERE coalesce(parent_id, '') = '' AND status != 'rejected'
    UNION SELECT n.id FROM node n JOIN visible v ON n.parent_id = v.id WHERE n.status != 'rejected')"""

_local = threading.local()
_db_path: Path | None = None


def use_database(path: Path | None) -> None:
    """Point lookups at a specific content.db (None: the default in EDUX_DATA_DIR)."""
    global _db_path
    _db_path = path
    _local.__dict__.clear()


def _conn() -> sqlite3.Connection:
    """This thread's connection to content.db, opened on first use."""
    path = _db_path or db.content_db_path()
    if getattr(_local, "path", None) != path:
        _local.conn = db.connect_content(path)
        _local.path = path
    return _local.conn


@functools.cache
def _settings() -> Settings:
    return load_settings()


def _node_dict(row: sqlite3.Row) -> dict:
    node = dict(row)
    node["aliases"] = split_list(node.get("aliases"))
    node["source_ids"] = split_list(node.get("source_ids"))
    return node


def canonical(node_id: str) -> str:
    """The current id for a possibly renamed id, following id_map (a -> b -> c)."""
    seen = {node_id}
    while True:
        row = _conn().execute("SELECT new_id FROM id_map WHERE old_id = ?", (node_id,)).fetchone()
        if row is None or row[0] in seen:
            return node_id
        node_id = row[0]
        seen.add(node_id)


def _visible_ids() -> set[str]:
    return {r[0] for r in _conn().execute(f"{VISIBLE} SELECT id FROM visible")}


def get_node(node_id: str) -> dict | None:
    """One node by id, or None if it doesn't exist or is hidden."""
    row = _conn().execute(f"{VISIBLE} SELECT n.* FROM node n JOIN visible v ON v.id = n.id WHERE n.id = ?",
                          (canonical(node_id),)).fetchone()
    return _node_dict(row) if row else None


def children(node_id: str) -> list[dict]:
    """Direct children of a node, in pack order."""
    rows = _conn().execute(f"{VISIBLE} SELECT n.* FROM node n JOIN visible v ON v.id = n.id "
                           "WHERE n.parent_id = ? ORDER BY n.rowid", (canonical(node_id),))
    return [_node_dict(r) for r in rows]


def ancestors(node_id: str) -> list[dict]:
    """Parent chain from the node's parent up to its topic."""
    node = get_node(node_id)
    chain: list[dict] = []
    while node and node.get("parent_id"):
        node = get_node(node["parent_id"])
        if node is None or any(a["id"] == node["id"] for a in chain):
            break
        chain.append(node)
    return chain


def parts_of(node_id: str) -> list[str]:
    """All parts under any node (recursive); a part returns itself."""
    node_id = canonical(node_id)
    rows = _conn().execute(f"""{VISIBLE}, sub(id) AS (
            SELECT id FROM visible WHERE id = ?
            UNION SELECT n.id FROM node n JOIN sub s ON n.parent_id = s.id JOIN visible v ON v.id = n.id)
        SELECT n.id FROM node n JOIN sub s ON s.id = n.id WHERE n.level = 'part' ORDER BY n.rowid""", (node_id,))
    return [r[0] for r in rows]


def concept_of(part_id: str) -> str | None:
    """The concept a part belongs to."""
    node = get_node(part_id)
    if not node or node["level"] != "part":
        return None
    parent = get_node(node["parent_id"]) if node.get("parent_id") else None
    return parent["id"] if parent and parent["level"] == "concept" else None


def _own_ids(node_id: str) -> list[str]:
    """The node plus, for a part, its concept: the ids whose edges apply to it."""
    concept = concept_of(node_id)
    return [node_id] + ([concept] if concept else [])


def _edges(node_id: str, edge_type: str, direction: str) -> list[dict]:
    """Non-rejected edges of one type touching the node (or its concept), with both ends visible.

    direction is "out" (node is from_id), "in" (node is to_id) or "both". Each result has
    other (the node at the far end), via (the concept it was inherited from, or None),
    note, confidence and weight.
    """
    node_id = canonical(node_id)
    if get_node(node_id) is None:
        return []
    own = _own_ids(node_id)
    visible = _visible_ids()
    rows = _conn().execute(
        f"""SELECT e.from_id, e.to_id, e.type, e.note, e.confidence, w.weight
            FROM edge e LEFT JOIN edge_weight w ON w.from_id = e.from_id AND w.to_id = e.to_id AND w.type = e.type
            WHERE e.type = ? AND e.status != 'rejected'
            AND (e.from_id IN ({','.join('?' * len(own))}) OR e.to_id IN ({','.join('?' * len(own))}))
            ORDER BY e.rowid""",
        [edge_type, *own, *own],
    ).fetchall()
    results, seen = [], set()
    for r in rows:
        if r["from_id"] not in visible or r["to_id"] not in visible:
            continue
        for end, other, wanted in ((r["from_id"], r["to_id"], "out"), (r["to_id"], r["from_id"], "in")):
            if end in own and direction in (wanted, "both") and other not in own and (other, r["type"]) not in seen:
                seen.add((other, r["type"]))
                results.append({
                    "other": other,
                    "other_name": get_node(other)["name"],
                    "type": r["type"],
                    "direction": wanted,
                    "via": None if end == node_id else end,
                    "note": r["note"] or "",
                    "confidence": r["confidence"],
                    "weight": r["weight"],
                })
    return results


def _walk(node_id: str, direction: str, depth: int) -> list[dict]:
    found: dict[str, dict] = {}
    frontier = [canonical(node_id)]
    for hop in range(1, depth + 1):
        next_frontier = []
        for current in frontier:
            for edge in _edges(current, "prerequisite", direction):
                if edge["other"] not in found and edge["other"] != canonical(node_id):
                    found[edge["other"]] = {**edge, "depth": hop, "from_node": current}
                    next_frontier.append(edge["other"])
        frontier = next_frontier
    return list(found.values())


def prerequisites(node_id: str, depth: int = 1) -> list[dict]:
    """What must be learnt before this node, up to depth hops, each with its depth."""
    return _walk(node_id, "in", depth)


def dependents(node_id: str, depth: int = 1) -> list[dict]:
    """What builds on this node, up to depth hops, each with its depth."""
    return _walk(node_id, "out", depth)


def analogous(node_id: str) -> list[dict]:
    """Analogous nodes (either direction), with the edge note and weight."""
    return _edges(node_id, "analogous", "both")


def confusables(node_id: str) -> list[dict]:
    """Confusable nodes (either direction), with the edge note and weight."""
    return _edges(node_id, "confusable", "both")


def causal_out(node_id: str) -> list[dict]:
    """Nodes this node affects, with the edge note and weight."""
    return _edges(node_id, "causal", "out")


def causal_in(node_id: str) -> list[dict]:
    """Nodes that affect this node, with the edge note and weight."""
    return _edges(node_id, "causal", "in")


def _expand_parts(node_ids: list[str]) -> list[str]:
    """Canonical, visible parts for a list of part or concept ids, in order, without repeats."""
    parts: list[str] = []
    for node_id in node_ids:
        for part in parts_of(node_id):
            if part not in parts:
                parts.append(part)
    return parts


def _placeholders(values: list) -> str:
    return ",".join("?" * len(values))


def notes_for(part_ids: list[str], limit: int | None = None) -> list[dict]:
    """Notes on the parts and on their concepts, ordered by source authority, then approved, then unflagged.

    Each note has its source title and type, authority and via (the concept it came from, or None).
    limit, when given, caps the notes per part.
    """
    authority = _settings().authority
    results, seen = [], set()
    for part in _expand_parts(part_ids):
        own = _own_ids(part)
        rows = _conn().execute(
            f"""SELECT n.*, s.title AS source_title, s.type AS source_type FROM note n
                LEFT JOIN source s ON s.id = n.source_id
                WHERE n.node_id IN ({_placeholders(own)}) AND n.status != 'rejected'""",
            own,
        ).fetchall()
        notes = []
        for r in rows:
            note = dict(r)
            note["key_points"] = split_list(note["key_points"])
            note["key_wording"] = split_list(note["key_wording"])
            note["authority"] = authority.get(note["source_type"] or "", 0)
            note["part_id"] = part
            note["via"] = None if note["node_id"] == part else note["node_id"]
            notes.append(note)
        notes.sort(key=lambda n: (-n["authority"], n["status"] != "approved", bool(n["flag"]), n["via"] is not None))
        for note in notes[:limit] if limit is not None else notes:
            if note["id"] not in seen:
                seen.add(note["id"])
                results.append(note)
    return results


def misconceptions_for(part_ids: list[str]) -> list[dict]:
    """Misconceptions attached to the parts (concept ids expand to their parts)."""
    parts = _expand_parts(part_ids)
    if not parts:
        return []
    rows = _conn().execute(
        f"""SELECT * FROM misconception WHERE node_id IN ({_placeholders(parts)}) AND status != 'rejected'
            ORDER BY rowid""",
        parts,
    )
    return [{**dict(r), "source_ids": split_list(r["source_ids"])} for r in rows]


def questions_for(part_ids: list[str]) -> list[dict]:
    """Past-paper questions testing the parts, with marks, paper and series.

    A question tagged to a concept or topic counts for the parts under it; via names that tag.
    parts lists which of the requested parts each question tests.
    """
    found: dict[str, dict] = {}
    for part in _expand_parts(part_ids):
        lineage = [part] + [a["id"] for a in ancestors(part)]
        rows = _conn().execute(
            f"""SELECT q.*, qn.node_id AS tag, pp.series, pp.exam_paper_id AS paper_id, ep.name AS paper_name
                FROM question_node qn JOIN question q ON q.id = qn.question_id
                LEFT JOIN past_paper pp ON pp.id = q.past_paper_id
                LEFT JOIN exam_paper ep ON ep.id = pp.exam_paper_id
                WHERE qn.node_id IN ({_placeholders(lineage)}) AND q.status != 'rejected'
                ORDER BY q.rowid""",
            lineage,
        ).fetchall()
        for r in rows:
            question = found.get(r["id"])
            if question is None:
                question = {k: r[k] for k in r.keys() if k != "tag"}
                question["node_ids"] = split_list(r["node_ids"])
                question["assessment_objectives"] = split_list(r["assessment_objectives"])
                question["parts"] = []
                question["via"] = None if r["tag"] == part else r["tag"]
                found[r["id"]] = question
            if part not in question["parts"]:
                question["parts"].append(part)
    return list(found.values())


def exam_papers_for(part_id: str) -> list[dict]:
    """Exam papers whose topics include the part (directly or through an ancestor)."""
    part_id = canonical(part_id)
    lineage = {part_id} | {a["id"] for a in ancestors(part_id)}
    papers = []
    for r in _conn().execute("SELECT id, name, date, node_ids FROM exam_paper ORDER BY date, rowid"):
        hits = [n for n in split_list(r["node_ids"]) if canonical(n) in lineage]
        if hits:
            papers.append({"id": r["id"], "name": r["name"], "date": r["date"], "via": hits[0]})
    return papers


def search_notes(text: str, limit: int) -> list[tuple[str, float]]:
    """Full-text search over notes; returns (node_id, score) pairs."""
    raise NotImplementedError


def resolve(message: str, node_ids: list[str] | None) -> dict:
    """Turn given ids (parts or concepts) into parts; with none, search notes and return candidates when unclear."""
    raise NotImplementedError


def weight(node_id: str) -> dict:
    """exam_weight, dependents and importance for a node (zeros if it has none)."""
    row = _conn().execute("SELECT exam_weight, dependents, importance FROM node_weight WHERE node_id = ?",
                          (canonical(node_id),)).fetchone()
    return dict(row) if row else {"exam_weight": 0.0, "dependents": 0, "importance": 0.0}

