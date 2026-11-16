# Step 03: Graph lookups

**Branch:** `build/03-graph-lookups`
**Read first:** `../reference/database.md`, `../reference/course-pack-format.md` (edge types)

## Goal
Read-only functions in `edux/graph.py` that later steps use. All of them skip rows with status `rejected` and resolve old ids through `id_map`.

## Functions
- `get_node(id)`, `children(id)`, `ancestors(id)`.
- `parts_of(id)`: all parts under any node (recursive CTE).
- `concept_of(part_id)`.
- `prerequisites(id, depth=1)` and `dependents(id, depth=1)`. Concept edges apply to their parts.
- `analogous(id)`, `confusables(id)`, `causal_out(id)` and `causal_in(id)`. Each returns the edge note.
- `notes_for(part_ids, limit)`: ordered by source authority, then confidence.
- `misconceptions_for(part_ids)`.
- `questions_for(part_ids)`: with marks, paper and series.
- `search_notes(text, limit)`: FTS5, returning node ids with scores.
- `resolve(message, node_ids)`: turns given ids (parts or concepts) into parts. With no ids, uses `search_notes` and returns `candidates` when the top results are close.
- `weight(id)`: returns exam_weight, dependents and importance.
- `exam_papers_for(part_id)`.

## Commits
1. `feat(graph): add tree lookups`
2. `feat(graph): add typed edge lookups with concept inheritance`
3. `feat(graph): add notes, misconceptions and questions lookups`
4. `feat(graph): add note search and node resolution`

## Done when
In a Python shell against `example-mini`:
- each function returns what the pack says
- a concept's edges show up on its parts
- a renamed id resolves
