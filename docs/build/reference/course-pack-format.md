# Course-pack format

A course pack is the contract between extraction (turning the specification, past papers, mark schemes, examiner reports and textbooks into structured data) and the system. It is a folder of UTF-8 CSV files in `coursepacks/<course_id>/`. All columns are defined once in `ingest/registry.py` (see `design-for-change.md`).

## General rules
- **IDs** are stable `snake_case` strings and are never renumbered: teacher feedback and learner events refer to them. A rename goes through `id_map.csv`.
- **Lists** inside a cell are separated by `;`, with `\;` for a literal semicolon.
- **Every content row** (nodes, edges, notes, misconceptions, mark points, questions, mark-scheme items) also has these columns, so teachers can edit it later:

| column | meaning |
|---|---|
| status | `draft` (default from extraction) / `approved` / `rejected` |
| flag | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | `extraction`, or a teacher's name |
| updated_at | ISO datetime |

- Rows with status `rejected` are loaded but never served. Flagged rows are served but listed in the load report.
- Unknown extra columns are kept in an `extra` JSON column.

## Files

### course.csv (one row)
| column | meaning |
|---|---|
| id | `aqa-econ-alevel` |
| name | `A-level Economics` |
| exam_board | `AQA` |
| spec_code | `7136` |
| spec_version | version or first-teaching year, used to reject past papers from an older specification |

### exam_papers.csv: the papers students will sit
| column | meaning |
|---|---|
| id | `paper1` |
| name | `Paper 1: Markets and market failure` |
| date | ISO date of the next sitting (students can override) |
| node_ids | topics this paper examines (their descendants are included) |

### sources.csv: every document the pack was built from
| column | meaning |
|---|---|
| id | e.g. `spec`, `ms_2024_p1`, `er_2024_p1`, `tb_main` |
| type | `specification` / `mark_scheme` / `examiner_report` / `question_paper` / `textbook` / `teacher` / `ours` |
| title | full title |
| edition | edition, version or exam series |
| reference | URL or catalogue reference |
| notes | licence, chapters used, etc. |

A source's **authority** comes from its type, ranked in `settings.toml` (mark scheme highest, `ours` lowest). When rows disagree, the higher authority wins, and notes are passed to the chatbot in authority order. Teacher edits override everything.

### nodes.csv: the knowledge tree
| column | meaning |
|---|---|
| id | e.g. `elasticities`, `ped`, `ped_formula` |
| parent_id | blank only for top-level topics |
| level | `topic` / `subtopic` / `concept` / `part` |
| name | e.g. `Price elasticity of demand: formula` |
| aliases | other names students use |
| spec_ref | specification section, e.g. `4.1.3.2` |
| part_type | parts only: `definition` / `calculation` / `diagram` / `mechanism` / `evaluation` / `application` |
| description | one or two sentences in our own words |
| source_ids | ids from sources.csv |
| extraction_confidence | 0–1 |

**Tree rules:**
- A part's parent is a concept.
- A concept's parent is a subtopic or topic.
- A subtopic's parent is a topic or subtopic.
- Only parts are tracked in the learner model. Concepts are tags that group parts and set focus.

### edges.csv: typed links between nodes
An edge on a concept applies to all its parts.

| column | meaning |
|---|---|
| from_id | node id |
| to_id | node id |
| type | `prerequisite` / `analogous` / `confusable` / `causal` |
| note | **required for analogous and causal:** what maps onto what, or how A affects B, in one line. The chatbot uses it to explain |
| confidence | 0–1 |
| source_ids | where the link is evidenced; may be blank for `ours` |

**Edge types:**
- **prerequisite:** you need A before you can understand B. Runs from A to B.
- **analogous:** A's structure maps onto B, so a student who understands A can be taught B through it. Two-way. Example: PED ↔ PES.
- **confusable:** students often mix them up. Two-way. Can coexist with analogous on the same pair.
- **causal:** in the economics, A affects B. Runs from A to B. Example: indirect tax → supply.

### notes.csv: what the chatbot answers from
Summaries and key wordings only, never long excerpts.

| column | meaning |
|---|---|
| id | e.g. `ped_formula_n1` |
| node_id | usually a part |
| summary | our own words, ≤ ~80 words |
| key_points | short points |
| key_wording | short phrases that earn marks, each < 15 words |
| source_id | |
| location | page, section or question reference |

### misconceptions.csv
| column | meaning |
|---|---|
| id | e.g. `ped_values_m1` |
| node_id | a part |
| wrong_idea | as a student might hold it |
| correction | one or two sentences |
| source_ids | examiner reports first where possible |

### mark_points.csv: our fallback points, for parts past papers don't test
| column | meaning |
|---|---|
| id | e.g. `ped_formula_p1` |
| node_id | a part |
| point | one sentence |
| exemplar | short model answer fragment |
| source_ids | **required**: the specification or textbook section the point is based on |

### past_papers.csv
| column | meaning |
|---|---|
| id | e.g. `2024_06_p1` |
| exam_paper_id | id in exam_papers.csv |
| series | `June 2024` |
| question_source_id | |
| mark_scheme_source_id | |
| examiner_report_source_id | may be blank |

### questions.csv
| column | meaning |
|---|---|
| id | e.g. `2024_06_p1_q03_2` |
| past_paper_id | |
| number | as printed, `03.2` |
| marks | integer |
| command_word | `Define` / `Calculate` / `Explain` / `Analyse` / `Evaluate` / ... |
| format | `mcq` / `short` / `data_response` / `essay` |
| assessment_objectives | e.g. `AO1;AO2` |
| node_ids | parts (preferred) or concepts it tests |
| summary | what it asks, in our own words |

### mark_scheme_items.csv
| column | meaning |
|---|---|
| id | e.g. `2024_06_p1_q03_2_i1` |
| question_id | |
| kind | `point` / `level` / `indicative` |
| marks | marks available, for `point` |
| level | level number, for `level` |
| text | our paraphrase plus any short key wording (< 15 words) |
| node_ids | parts this item relates to |

### id_map.csv (optional)
| column | meaning |
|---|---|
| old_id | an id that was renamed |
| new_id | what it became |

## Calculated on load (not in files)
Stored in the `node_weight` table:
- **exam_weight:** total marks of questions tagged to the node or its descendants. A question tagged to several nodes splits its marks equally. Normalised so the course sums to 1.
- **dependents:** the number of nodes reachable through `prerequisite` edges.
- **importance:** `w_exam × percentile(exam_weight) + w_dependents × percentile(dependents)`, with the weights in `settings.toml`.

## Validation
**Errors** block loading:
- unknown references or duplicate ids
- bad enum values
- tree-rule violations
- prerequisite cycles (print the cycle)
- analogous or causal edges without a note
- mark points without sources
- confidence values outside 0–1
- key wordings of 15 words or more
- note summaries over 120 words
- past papers from the wrong specification version

**Warnings** print:
- a part with no question, mark point or note
- a part with no misconception
- a concept with no parts
- a node with no edges
- `extraction_confidence` below 0.5
- mark-scheme marks that don't add up to the question's marks

## Teacher feedback (overlay)
`teacher_feedback/<course_id>.csv`, applied in `ts` order after every load, so it survives re-extraction.

| column | meaning |
|---|---|
| ts | ISO datetime |
| teacher | name |
| table | `nodes` / `edges` / `notes` / `misconceptions` / `mark_points` / `questions` / `mark_scheme_items` |
| target_id | id; for an edge, `from_id|to_id|type` |
| action | `approve` / `reject` / `edit` / `add` |
| field | for edit: column to change |
| value | for edit: new value; for add: `col=value;col=value` |
| note | free text |

**Actions:**
- `approve` sets status to approved.
- `reject` sets status to rejected.
- `edit` changes one field and sets `updated_by`.
- `add` inserts a row.

Each action is also recorded in the `teacher_feedback` table along with whether it applied. A missing target is reported, not fatal.

## Copyright
Specifications, past papers, mark schemes, examiner reports and textbooks belong to their publishers. Packs store our own summaries, short key wordings (< 15 words) and references, never full question or mark-scheme text. Real packs live in `coursepacks/<id>/private/`, which is git-ignored. Only `example-mini`, whose past-paper rows are invented and labelled `synthetic`, is committed.
