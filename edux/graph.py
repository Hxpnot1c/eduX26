"""Read-only lookups over content.db: tree, typed edges, notes, questions and weights.

Every lookup skips rows with status 'rejected' and resolves old ids through id_map.
Edges on a concept apply to all of its parts.
"""

from __future__ import annotations


def get_node(node_id: str) -> dict | None:
    """One node by id."""
    raise NotImplementedError


def children(node_id: str) -> list[dict]:
    """Direct children of a node."""
    raise NotImplementedError


def ancestors(node_id: str) -> list[dict]:
    """Parent chain from the node up to its topic."""
    raise NotImplementedError


def parts_of(node_id: str) -> list[str]:
    """All parts under any node (recursive); a part returns itself."""
    raise NotImplementedError


def concept_of(part_id: str) -> str | None:
    """The concept a part belongs to."""
    raise NotImplementedError


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
    """exam_weight, dependents and importance for a node."""
    raise NotImplementedError


def exam_papers_for(part_id: str) -> list[dict]:
    """Exam papers whose topics include the part."""
    raise NotImplementedError
