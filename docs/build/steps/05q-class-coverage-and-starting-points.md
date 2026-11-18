# Step 05q: Class coverage and starting points

Branch `build/class-coverage-and-starting-points`, from `main` after step 05p.

## What
1. **Classes.**
   - A `class` table: `id`, `name`, `course_pack`.
   - Students are linked by a nullable `student.class_id`. Each student row is already one student on one course, so one class per student row is enough. A student in two courses has two keys.
   - CLI: `class add --name … --pack …` and `class add-students --class … --students …`.
   - The demo seed puts the demo students in one class.
2. **Coverage record:** which parts of the spec a class has been taught, and when.
   - Table `class_coverage(class_id, node_id, taught_on, set_by)`. `set_by` is `cli`, `csv` or `mockup`. A coverage row on a node marks all its parts.
   - **Teacher input:**
     - CLI: `coverage set --class … --sections … --taught-on …`, where sections are node ids or spec codes;
     - CSV import: `coverage import --class … file.csv`, with columns `section,taught_on`;
     - `coverage export --class … --json`. The teacher mock-up's "where we are in the spec" tick-list reads this. The mock-up isn't in this repo, so the PR says where the JSON goes.
   - **Student fallback:** `update_my_profile(covered_in_class={topics, when?})`.
     - Topics are matched as for assessments (step 05i), and matched and unmatched topics are returned.
     - `when` defaults to today.
     - It applies to that student only and is stored in `student_coverage(student_id, node_id, taught_on, set_by)`.
   - **Coverage is profile, not events,** like assessments. A coverage row counts for an event only when `taught_on` is on or before the event's date, so a rebuild gives the same state.
3. **The starting point depends on coverage.** This applies only to parts with no evidence yet.
   - **Not covered:** `bkt.prior` with the difficulty shift, as now.
   - **Covered in class:** `coverage.prior_default` (0.50), with the difficulty shift.
   - **The class estimate** is only used when `coverage.class_estimate_enabled` is on (see "The class estimate and the privacy rules" below). It is off by default, and covered parts then use `coverage.prior_default`. When it's on, the default is replaced per class by an estimate from the class's own first answers on covered parts:
     - it's shrunk towards the default with k = `coverage.class_k` (25) first answers;
     - it's converted to a prior the same way as the personal adjustment (item 4), with the same smoothing;
     - it's never more than `coverage.class_max_down` (0.075) below `coverage.prior_default`. So by this route a covered topic never starts below 0.425, before the difficulty shift.
     - It's computed from the raw evidence of class members before the time asked, against the default covered prior. So there's no circularity, and a rebuild gives the same state.
   - **The forgetting clock starts at `taught_on`** for covered parts with no evidence. `p_now` decays from the covered prior since then.
     - `due_reviews` includes covered parts with no evidence, due at `taught_on` + the share gap, floored at `min_gap_days`, with reason `taught_in_class`.
     - So topics taught in class but never practised in Synapse get reviews.
     - If decay-to-prior (patch 0005) has landed, use its decay target.
4. **A personal starting adjustment, split by sector.** Each student has two separate log-odds offsets, **covered** and **not covered**. Success in one never spills into the other.
   - **Evidence used:** only answers on a part from before any teaching of that part:
     - a pre-question;
     - an "I know this" check;
     - an explain-back before any teach step on it.

     "Teaching" means an earlier issued `teach_point`, `show`, `reteach` or worked example on that part, or an exchange with support `worked_example` or `hint` on it. Each answer's sector is its part's coverage at that time.
   - **The estimate** is n/(n + k) × (logit(smoothed score) − logit(smoothed expected)). Both are smoothed before the logit, so an all-right or all-wrong start can't give an infinite offset:
     - smoothed score = (sum of scores + 0.5) / (n + 1);
     - smoothed expected = (sum of expected success under the part's starting point + 0.5) / (n + 1).
   - It is built from evidence in earlier sessions, like the learning-rate offset, so it is stable within a session and cacheable (step 05r).
   - **Shrinkage:** k = `starting.k` (25) first answers. **Bounds:** ±`starting.bound_logits` (1.5).
   - **Applies to:** parts in that sector with no evidence yet.
   - **Excluded:** `ail_*` parts get neither offset and no coverage.
   - Pre-question answers feed it even when their knowledge weight is 0. Their score still says what the student knew.
5. **Prerequisites feed forward.** A part with no evidence shifts its starting point by:
   `propagation.forward_weight × mean over its direct prerequisites of (logit p_now(prereq) − logit starting point of that prereq)`
   - It uses course-pack prerequisite edges only, one hop, and is not recursive.
   - It stops mattering once the part has its own evidence.
   - The existing upward propagation (`prereq_boost`) is unchanged.
6. **Richer open answers count for more.** The explain-back guess falls with the number of mark points required:
   - 0.20 for 1–2 points;
   - 0.15 for 3;
   - 0.10 for 4 or more.

   The number comes from the step asked: 1 for a narrowed explain-back (`point_id`), otherwise the part's point count. No migration is needed.

**The starting point, in order:**
1. `logit(base prior)`, where the base prior is the not-covered prior, or the covered prior or class estimate;
2. plus the sector's personal offset;
3. plus the feed-forward shift;
4. then back to a probability, clamped to [0.01, 0.99].

The difficulty shift on the half-life is unchanged.

**Immediacy is unchanged.** An answer straight after teaching still gets immediate-evidence handling. Performance straight after instruction overstates retention (Soderstrom & Bjork, 2015).

## Why, with sources
- **Starting points depend on whether the class has covered the topic:** achievement gaps come mainly from differences in learning opportunities (Koedinger et al., 2023).
- **Personalise the starting point:**
  - Pardos & Heffernan (2010): individualising the prior improved prediction, even when set from first responses.
  - Simpson, Norberg & Fancsali (2024): starting-knowledge SD is 0.57–0.90 logits, which implies k ≈ 18–44 in our simulation; 25 is the middle.
  - Yudelson, Koedinger & Gordon (2013) is the counterpoint, and is recorded.
- **Split by sector:** success on taught topics says little about topics not yet taught (Koedinger et al., 2023).
- **Only pre-teaching answers:** answers straight after teaching show the student followed it (Soderstrom & Bjork, 2015).
- **Feed-forward:** modelling skill links beats plain BKT (Käser et al., 2014, 2017). They give no weight, so 0.5 is a judgement call.
- **The forgetting clock from `taught_on`:** the decay model plus Cepeda et al. (2008).
- Full rows are in `reference/research.md`, under "Learner model and settings" and "Personalisation".

## The class estimate and the privacy rules
`docs/research/personalisation.md` §5 and §7 treat a class-level starting estimate as **cross-student profiling**. So, as §7 requires:
- **It is off by default.** `coverage.class_estimate_enabled = false`. It is turned on only by the school's written instruction, recorded as this setting.
- **One school's data only.** It reads only members of the student's own class.
- **At least 5 students.** There's no class estimate from fewer than `coverage.class_min_students` students with first answers on covered parts.
- **It's listed in the DPIA notes,** `docs/build/reference/dpia-notes.md`, which this step creates.
- **Students are told.** While it's on, a one-line notice (`text/notices/class_estimate.md`) tells students that their class's results shape their starting point:
  - in `get_my_progress`;
  - on the first `tutor_turn` of a session, once.
- **The downward cap is 0.075** (`coverage.class_max_down`), so by this route a covered topic never starts below 0.425.
- **It stays off in the demo seed.** Covered topics use `coverage.prior_default`.

With it off, the coverage record still works fully: covered parts start at the default and their clock starts at `taught_on`.

## Files
- **Migrations:** the next free number when you start (014 at time of writing, if no earlier step has taken one):
  - `class`;
  - `student.class_id`;
  - `class_coverage`;
  - `student_coverage`.
- `edux/learner.py`:
  - `initial_state` becomes `starting_point(student_id, part_id, at)`, built in the order above;
  - `covered(student_id, node_id, at)`, `class_estimate`, `starting_offsets` and `forward_shift`;
  - the clock start for covered parts in `_load_state` and `part_p`;
  - covered parts in `due_reviews`;
  - the guess by number of points in `slip_guess`.
- `edux/service.py`, `edux/server.py`: `update_my_profile(covered_in_class=…)`.
- `edux/cli.py`: the `class` and `coverage` commands; `state` shows each part's sector and both offsets.
- `edux/demo.py`:
  - the demo class has covered the first few Theme 1 sections of the example pack (3.1.1 PED, 3.1.2 PES), taught 3–4 weeks back;
  - demo-weak's covered topics have faded since then.
- `text/tools/update_my_profile.md`: `covered_in_class`.
- `text/notices/class_estimate.md`: the student notice, shown only while the class estimate is on.
- `docs/build/reference/dpia-notes.md` (new): lists the class estimate (cross-student, school-instructed, off by default).
- `scripts/check_mcp.py`: a `coverage` run.
- **Docs:**
  - this file;
  - `reference/database.md` (the new tables);
  - `reference/learner-model.md` (the starting point, sectors, feed-forward, the clock);
  - `reference/settings.md` (labels);
  - `reference/tools-and-context.md` (`covered_in_class`);
  - `reference/research.md`: the "Starting points depend on whether the class has covered the topic" caveat now says the class estimate is off by default, school-instructed and capped at 0.075. Other rows change too if anything ends up different.

## Settings
```toml
[coverage]
prior_default = 0.50             # judgement call, starting value
class_k = 25                     # from research: Simpson et al. (2024) spread plus our simulation
class_estimate_enabled = false   # off by default: on only with the school's written instruction (personalisation.md §7)
class_min_students = 5           # from personalisation.md §5/§7: minimum cell size
class_max_down = 0.075           # from personalisation.md §7: the class estimate never goes more than this below prior_default

[starting]
k = 25                           # from research: Simpson et al. (2024) intercept SD 0.57–0.90 logits → k ≈ 18–44 in our simulation
bound_logits = 1.5               # from research: about ±2 SD of that spread

[propagation]
forward_weight = 0.5             # judgement call; Käser et al. (2014, 2017) model the links but give no weight

[bkt.explain_back_guess]         # judgement call: a complete multi-point answer is far harder to produce by luck
up_to_2 = 0.20
three = 0.15
four_plus = 0.10
```
The startup identifiability check covers the new guesses.

## Commits
1. `feat(learner): add classes and link students to them` (migration)
2. `feat(cli): create classes and add students`
3. `feat(learner): record class and student coverage` (migration)
4. `feat(cli): set, import and export class coverage`
5. `feat(server): let a student say what was covered in class`
6. `feat(learner): start covered parts from the covered prior and the taught date`
7. `feat(learner): estimate the covered prior from the class's first answers`
8. `feat(learner): split the personal starting adjustment by coverage`
9. `feat(learner): feed prerequisites forward into new parts' starting points`
10. `feat(learner): lower the explain-back guess as mark points rise`
11. `feat(demo): put the demo students in a class with covered sections`
12. `chore(scripts): check coverage and starting points in the MCP check`
13. `docs(reference): document classes, coverage and starting points`

## Done when
- A covered part with no evidence starts at the covered prior and decays from `taught_on`. It's due for review without ever being practised.
- Covered success raises covered starting points and leaves not-covered ones unchanged.
- Pre-teaching evidence moves the offset; post-teaching evidence doesn't.
- Feed-forward moves a new part, and stops once the part has evidence.
- The explain-back guess is 0.20 / 0.15 / 0.10 by number of points.
- An all-right and an all-wrong start give finite offsets within ±1.5 logits.
- With the class estimate off, covered parts start at `coverage.prior_default`. With it on, it needs 5 students, never goes below 0.425 before the difficulty shift, and the notice appears.
- `ail_*` starting points are unchanged.
- Every demo student's levels per part are re-captured and listed in the PR.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported. The tool description doesn't count towards it.

## Tests
In `scripts/check_mcp.py` (`coverage`):
- covered versus not-covered starting points;
- the clock starts at `taught_on`;
- covered success raises covered starting points and leaves not-covered ones unchanged;
- pre-teaching evidence feeds the offset, post-teaching doesn't;
- feed-forward moves a new part and stops once it has evidence;
- the explain-back guess by number of points;
- an all-right and an all-wrong start (finite, bounded offsets);
- the class estimate: off by default; with it on, fewer than 5 students gives no estimate, the 0.075 cap holds, and the notice appears;
- `ail_*` untouched;
- rebuild identical.
