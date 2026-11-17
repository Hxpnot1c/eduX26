# Course packs

Generated from `ingest/registry.py` by `python -m ingest.cli readme`. Do not edit by hand.

A course pack is a folder of UTF-8 CSV files in `coursepacks/<course_id>/`. See `docs/build/reference/course-pack-format.md` for the rules. `python -m ingest.cli templates <dir>` writes empty templates.

- Lists inside a cell are separated by `;`, with `\;` for a literal semicolon.
- Unknown extra columns are kept in the row's `extra` JSON column.
- Real packs live in `coursepacks/<id>/private/`, which is git-ignored (the Pearson Edexcel A level Economics A (9EC0) pack: `coursepacks/edexcel-econ-a/private/`).

## Files

### course.csv

One row.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | course id, e.g. `edexcel-econ-a` |
| name | text | yes |  |  | e.g. `A level Economics A` |
| exam_board | text |  |  |  | e.g. `Pearson Edexcel` |
| spec_code | text |  |  |  | e.g. `9EC0` |
| spec_version | text |  |  |  | version or first-teaching year; past papers from an earlier year are rejected |

### exam_papers.csv

The papers students will sit.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `paper1` |
| name | text |  |  |  | e.g. `Paper 1: Markets and business behaviour` |
| date | date |  |  |  | ISO date of the next sitting |
| node_ids | list |  |  |  | topics this paper examines (descendants included) |

### sources.csv

Every document the pack was built from.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `spec`, `ms_2024_p1`, `tb_main` |
| type | text | yes | `specification` / `mark_scheme` / `examiner_report` / `question_paper` / `textbook` / `teacher` / `ours` |  | source type; sets its authority in settings.toml |
| title | text |  |  |  | full title |
| edition | text |  |  |  | edition, version or exam series |
| reference | text |  |  |  | URL or catalogue reference |
| notes | text |  |  |  | licence, chapters used, etc. |

### nodes.csv

The knowledge tree.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `ped_formula` |
| parent_id | text |  |  |  | blank only for top-level topics |
| level | text | yes | `topic` / `subtopic` / `concept` / `part` |  | topic / subtopic / concept / part |
| name | text | yes |  |  | e.g. `Price elasticity of demand: formula` |
| aliases | list |  |  |  | other names students use |
| spec_ref | text |  |  |  | specification section, e.g. `4.1.3.2` |
| part_type | text |  | `definition` / `calculation` / `diagram` / `mechanism` / `evaluation` / `application` |  | parts only |
| description | text | yes |  |  | one or two sentences in our own words |
| source_ids | list |  |  |  | ids from sources.csv |
| extraction_confidence | real |  |  | `1.0` | 0–1 |
| difficulty | real |  |  |  | optional, 0 (easy) to 1 (hard); blank inherits from the nearest ancestor, else average |
| intuition | text |  |  |  | parts only: one line in everyday language that leads into the idea; the source of the intuition question when no known part links in |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### edges.csv

Typed links between nodes. An edge on a concept applies to all its parts.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| from_id | text | yes |  |  | node id |
| to_id | text | yes |  |  | node id |
| type | text | yes | `prerequisite` / `analogous` / `confusable` / `causal` |  | prerequisite / analogous / confusable / causal |
| note | text |  |  |  | what the link means, e.g. what maps onto what, or how A affects B; required when `teach_use` is `intuition`, a warning if missing elsewhere |
| confidence | real |  |  | `0.8` | 0–1 |
| source_ids | list |  |  |  | where the link is evidenced |
| teach_use | text |  | `intuition` / `contrast` / `none` | `none` | `intuition` (the `from` part can lead into the `to` part), `contrast` (use it to show the difference) or `none` |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### notes.csv

What the chatbot answers from.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `ped_formula_n1` |
| node_id | text | yes |  |  | usually a part |
| summary | text | yes |  |  | our own words, ≤ ~80 words (error over 120) |
| key_points | list |  |  |  | short points |
| key_wording | list |  |  |  | short phrases that earn marks, each < 15 words |
| source_id | text |  |  |  | id from sources.csv |
| location | text |  |  |  | page, section or question reference |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### misconceptions.csv

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `ped_values_m1` |
| node_id | text | yes |  |  | a part |
| wrong_idea | text | yes |  |  | as a student might hold it |
| correction | text | yes |  |  | one or two sentences |
| source_ids | list |  |  |  | examiner reports first where possible |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### mark_points.csv

Our fallback points, for parts past papers don't test.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `ped_formula_p1` |
| node_id | text | yes |  |  | a part |
| point | text | yes |  |  | one sentence |
| exemplar | text |  |  |  | short model answer fragment |
| source_ids | list | yes |  |  | the specification or textbook section the point is based on |
| order | int |  |  |  | position within the part (1, 2, ...); points are taught and scored in this order |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### past_papers.csv

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `2024_06_p1` |
| exam_paper_id | text | yes |  |  | id in exam_papers.csv |
| series | text |  |  |  | e.g. `June 2024` |
| question_source_id | text |  |  |  | id in sources.csv |
| mark_scheme_source_id | text |  |  |  | id in sources.csv |
| examiner_report_source_id | text |  |  |  | id in sources.csv; may be blank |

### questions.csv

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `2024_06_p1_q03_2` |
| past_paper_id | text | yes |  |  | id in past_papers.csv |
| number | text |  |  |  | as printed, `03.2` |
| marks | int | yes |  |  | integer |
| command_word | text |  |  |  | `Define` / `Calculate` / `Explain` / `Analyse` / `Evaluate` / ... |
| format | text |  | `mcq` / `short` / `data_response` / `essay` |  | mcq / short / data_response / essay |
| assessment_objectives | list |  |  |  | e.g. `AO1;AO2` |
| node_ids | list | yes |  |  | parts (preferred) or concepts it tests |
| summary | text |  |  |  | what it asks, in our own words |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### mark_scheme_items.csv

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `2024_06_p1_q03_2_i1` |
| question_id | text | yes |  |  | id in questions.csv |
| kind | text |  | `point` / `level` / `indicative` |  | point / level / indicative |
| marks | int |  |  |  | marks available, for `point` |
| level | int |  |  |  | level number, for `level` |
| text | text | yes |  |  | our paraphrase plus any short key wording (< 15 words) |
| node_ids | list |  |  |  | parts this item relates to |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### trusted_sources.csv

Optional. Sources research answers point to first, per topic (step 05e).

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| id | text | yes |  |  | e.g. `ons_inflation`, so teacher feedback can target the row |
| node_id | text | yes |  |  | a topic or concept the source is good for (its descendants included) |
| name | text | yes |  |  | e.g. `ONS` |
| url | text | yes |  |  | the landing page for this kind of data (http or https) |
| what_for | text | yes |  |  | one line, e.g. `UK inflation and price indices` |
| status | text |  | `draft` / `approved` / `rejected` | `draft` | draft / approved / rejected |
| flag | text |  |  |  | blank, or a short reason extraction thinks the row may be wrong |
| updated_by | text |  |  | `extraction` | `extraction`, or a teacher's name |
| updated_at | text |  |  |  | ISO datetime |

### id_map.csv

Optional. Renamed ids.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| old_id | text | yes |  |  | an id that was renamed |
| new_id | text | yes |  |  | what it became |

## Teacher feedback

### teacher_feedback/<course_id>.csv

Teacher feedback overlay, applied in `ts` order after every load.

| column | type | required | allowed values | default | meaning |
|---|---|---|---|---|---|
| ts | text | yes |  |  | ISO datetime |
| teacher | text | yes |  |  | name |
| table | text | yes | `nodes` / `edges` / `notes` / `misconceptions` / `mark_points` / `questions` / `mark_scheme_items` |  | the pack file the target is in, without `.csv` |
| target_id | text | yes |  |  | id; for an edge, `from_id|to_id|type` |
| action | text | yes | `approve` / `reject` / `edit` / `add` |  | approve / reject / edit / add |
| field | text |  |  |  | for edit: column to change; on edges, `weight` sets the link weight (0–1) |
| value | text |  |  |  | for edit: new value; for add: `col=value;col=value` |
| note | text |  |  |  | free text |
