# Step 05d: Point by point

**Branch:** `build/05d-point-by-point`
**Read first:** `docs/build/README.md`, `reference/tools-and-context.md` (choosing the plan), `reference/learner-model.md` (evidence), `reference/course-pack-format.md` (mark points), `reference/research.md`, `edux/plan.py`

## Why
Sources are in `reference/research.md`.
- **Learner-paced segments.** Meaningful, coherent segments that the learner moves through at their own pace improve retention and transfer, and reduce cognitive load (Rey et al., 2019).
- **A quick test after a segment** helps learning of the next one: the forward testing effect (Chan, Meissner & Davis, 2018).
- **But not too often.** Switching often between testing and studying can hurt new learning (Davis, Chan & Wilford, 2017). So the check comes after each meaningful point, not after every sentence.
- **Mastery learning** helps, especially weaker students, but strict gating can lower completion (Kulik, Kulik & Bangert-Drowns, 1990). So a student who already knows a point can skip to its check.

## What changes, in one line each
1. Mark points get an order within their part.
2. A new evidence type, `point_check`.
3. Teaching a part becomes a loop: one point per message, each followed by one quick check.
4. "I know this" skips straight to the point's check.
5. The loop ends with an explain-back of the whole part.

---

## A. Course pack
- `mark_points.csv` gets an `order` column: an integer within a part.
- **Validation:**
  - a warning when a part has more than `points.warn_max` or fewer than `points.warn_min` points;
  - an error on a duplicate `order` within a part.
- **Fallback:** a part with no mark points uses its notes' key points, in file order (ids `<note_id>:k<n>`, as now).
- Score points everywhere (`score_next`, letters from 05c) follow this order.

## B. The loop for one part
1. **Pre-question** for new parts, as now.
2. **`teach_point`** **(stop)**
   - **Content:** one point. `data`: `index`, `total`, `point`, `exemplar`, `check_hint`.
     - `check_hint` is how to check this kind of point, from `text/points/check_<part_type>.md` (e.g. a calculation asks for a number; a definition asks for it in their own words).
   - **Reply shape:**
     - a heading line, `Point {index} of {total}: {short title}`;
     - one or two sentences;
     - one worked line (LaTeX when it applies);
     - then **one quick check question on only this point**.
   - **Limits:** at most `points.max_words` words, no tangents, at most one example.
   - `support_given` on the exchange is the part's support level (`worked_example` or `hint`), so the immediate-recall rule applies to the check that follows.
   - `score_next` lists only this point (letter `a`), and `data.answer_type = point_check`.
3. **The student answers** (`answer.type = point_check`, `points_met` = the point, or empty). The score is 1 or 0. The next plan is:
   - **`feedback`:** one or two lines on why it's right or wrong;
   - then either:
     - right: the next `teach_point`;
     - wrong: `reteach_point` **(stop)**, a different way in (the anchor, a different example or the diagram), with the same check. At most `points.reteach_limit` times per point; after that, move on to the next point. The wrong evidence already schedules the part's review under the spacing rules, so nothing extra is recorded.
4. **"I know this"** (`this_message.choice = skip_point`, a new value) → `check_point` **(stop)**: the check question only, no teaching. `support_given` is `none`, so the answer is not discounted as immediate recall.
5. **"Just show me"** during the loop → `show` for the current point only: the worked line and the answer, with no check. The loop continues with the next point on the next turn.
6. **After the last point** → `explain_back` of the whole part **(stop)**. This joins the points together. It is scored on all of the part's points, as type `explain_back`.
7. **Well-known parts:** a part already at `levels.secure` skips the loop and goes straight to `explain_back`.

Fatigue and stuck rules still come first, as in 05b. Feedback plus the next point is the two-step plan; nothing is added after a stop step.

## C. Point progress
Progress is kept per part in `issued_plan.plan_json`, not in learner state:

```json
"points": {"ped_formula": {"index": 2, "reteaches": 0}, "ped_values": {"index": 1, "reteaches": 1}}
```

- A message that moves to a different part keeps the first part's progress. Coming back resumes at the point it stopped on.
- A finished part (explain-back asked) is removed from the map, so teaching it again starts from point 1.
- `evidence_log` stores no point id, so progress can't be rebuilt from events, and doesn't need to be: losing it only means starting a part from point 1 again.
- Rebuild is unaffected: it replays the evidence, and point progress is not part of state.

## D. Learner model
- New evidence type `point_check`, with its own slip and guess in `[bkt.evidence]`. Its guess is higher than `explain_back`'s, so it counts for less, because one point is a narrow check.
- The immediate-recall rule applies to it as to any chat evidence.

## Settings
```toml
[points]                   # point-by-point teaching (step 05d)
max_words = 80             # words per teach_point reply
reteach_limit = 1          # re-teaches of a missed point before moving on
warn_min = 2               # validation warning below this many points per part
warn_max = 4               # and above this many

[bkt.evidence]
point_check = { slip = 0.10, guess = 0.20 }
```

## Text
- `text/moves/teach_point.md` and `.cue.md`, `reteach_point.md` and `.cue.md`, `check_point.md` and `.cue.md`.
- `text/points/check_<part_type>.md`, one per part type.
- `text/server_instructions.md` gets a "one point per message, ending in one question" rule.
- `text/tools/tutor_turn.md` lists `skip_point` and `point_check`.

## Docs and scripts
- `reference/course-pack-format.md`: the `order` column and its validation.
- `reference/tools-and-context.md`: the loop, the new moves, `skip_point` and `point_check`.
- `reference/learner-model.md`: `point_check`.
- `reference/settings.md`: `[points]` and the new evidence type.
- `example-mini`: `order` on every mark point.
- `scripts/check_mcp.py`: a point-by-point run (below).

## Commits (one logical change each, no attribution)
1. `feat(ingest): order mark points within a part`
2. `feat(learner): add point check evidence`
3. `feat(context): teach one point at a time with a check after each`
4. `feat(context): let students skip to a point's check`
5. `feat(context): finish a part with an explain-back of all its points`
6. `docs(text): write point-by-point move texts`
7. `chore(scripts): add a point-by-point run to the MCP check`

## Done when (by hand, no tests yet)
- `scripts/check_mcp.py` runs `ped_formula` as demo-secure: pre-question → point 1 of N with a check → a correct answer → point 2 → a wrong answer → one re-teach → … → explain-back.
- Every `teach_point` step asks for at most 80 words and exactly one question.
- "I know this" goes straight to the check, with no teaching.
- `rebuild` gives identical state.
- **claude.ai check (Vishnu runs it):** each reply is short and ends in one question.
