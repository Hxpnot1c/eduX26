"""Read-only lookups over content.db: tree, typed edges, notes, questions and weights.

Every lookup skips rows with status 'rejected' (a rejected node also hides everything
under it) and resolves old ids through id_map. Edges on a concept apply to all of its
parts. Lookups return full lists with the numbers needed to rank them; choosing what
reaches the chatbot is left to the context blocks.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from edux import db
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


def prerequisites(node_id: str, depth: int = 1) -> list[dict]:
    """Prerequisites of a node up to depth hops."""
    raise NotImplementedError


def dependents(node_id: str, depth: int = 1) -> list[dict]:
    """Nodes that have this node as a prerequisite, up to depth hops."""
    raise NotImplementedError


def analogous(node_id: str) -> list[dict]:
    """Analogous nodes, with the edge note."""
    raise NotImplementedError


def confusables(node_id: str) -> list[dict]:
    """Confusable nodes, with the edge note."""
    raise NotImplementedError


def causal_out(node_id: str) -> list[dict]:
    """Nodes this node affects, with the edge note."""
    raise NotImplementedError


def causal_in(node_id: str) -> list[dict]:
    """Nodes that affect this node, with the edge note."""
    raise NotImplementedError


def notes_for(part_ids: list[str], limit: int) -> list[dict]:
    """Notes for the parts, ordered by source authority, then confidence."""
    raise NotImplementedError


def misconceptions_for(part_ids: list[str]) -> list[dict]:
    """Misconceptions attached to the parts."""
    raise NotImplementedError


def questions_for(part_ids: list[str]) -> list[dict]:
    """Past-paper questions testing the parts, with marks, paper and series."""
    raise NotImplementedError


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


def exam_papers_for(part_id: str) -> list[dict]:
    """Exam papers whose topics include the part."""
    raise NotImplementedError
