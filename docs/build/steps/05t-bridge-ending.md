# Step 05t: A bridge question towards the next topic

Branch `build/bridge-ending`, from `main` after step 05s.

## What
**When:** a reply has no question of its own, because a part has just finished or the reply only explains. Today `_second_step` adds an earned extend or the best due review. It now picks an ending.

**The ending, in a fixed order of tiers.** Within each tier, candidates are ordered by the value score (step 05i).
1. A due review on a part covered by any assessment within `priorities.horizon_days` (7).
2. **A bridge question** to the next topic.
3. Extend, if earned.
4. Any other due review.

**The bridge target:**
1. **First choice:** the class's next not-yet-covered section in spec order, from the coverage record (step 05q). It must be linked to the current part by a pack edge, and its prerequisites must be at least developing.
2. **Otherwise:** the not-yet-taught part with the strongest link (`link_weight`) to the current part whose prerequisites are at least developing.
3. **Otherwise:** no bridge.

"Not yet taught" means no evidence and no issued teaching step on the part.

**The question:**
- It uses the existing pre-question move (`ask_mcq`, purpose `intuition`) on the target part's **first key point**.
- It carries `data.link` (from-part, to-part, link text) and the short cue `ask_mcq_prequestion_bridge`. There's no new move section.
- **Its evidence** follows the pre-question rules. Being pre-teaching, it feeds the starting offset of its target's sector (step 05q).
  - That's the not-covered offset for a coverage-next target, and for any target the class hasn't covered.
  - A strongest-link target that was covered in class but never practised in Synapse feeds the covered offset instead.
- After the answer, as for any pre-question, the feedback comes first, then teaching on the target part starts.

**Reason line:** when the target comes from the coverage record, `data.reason` is "this links to what's next in class".

**CLI:** the student view shows the four tiers, each with its candidates and values, including the bridge candidate. The tiers not picked go to `considered` as now.

## Why, with sources
- **Prequestions help learn the specific information asked about,** g = 0.54, with no general benefit (St. Hilaire, Chan & Ahn, 2024). So the bridge asks about the next part's first key point, framed through the link, not a vague "any thoughts?".
- **Protect what's about to be tested, then build forward** (Cepeda et al., 2008, for the urgent review). The order itself is a judgement call.
- **Hand-set order, with the options not picked logged** (Doroudi, Aleven & Brunskill, 2019).

## Files
- `edux/plan.py`:
  - `_second_step` becomes `ending(turn, blocks, settings)`, built from the four tiers;
  - `bridge_target`;
  - the bridge question, built on `question(…, "intuition", …)`.
- `edux/learner.py`: `next_covered_section(class_id, at)` and `not_yet_taught(student_id, part_id)`.
- `edux/graph.py`: the strongest linked part, using pack edges only.
- `edux/cli.py`: the tiers in the student view.
- `text/moves/ask_mcq_prequestion_bridge.cue.md`.
- `scripts/check_mcp.py`: a `bridge` run.
- **Docs:** this file; `reference/tools-and-context.md` (`data.link`, the ending order); `reference/learner-model.md` (bridge evidence); `reference/research.md` rows if anything ends up different.

## Settings
None new: `priorities.horizon_days` sets tier 1.

## Commits
1. `feat(plan): pick the reply's ending from four tiers`
2. `feat(plan): add a bridge question towards the next topic`
3. `feat(plan): prefer the class's next section for the bridge`
4. `feat(cli): show the ending tiers and their candidates`
5. `chore(scripts): check the bridge ending in the MCP check`
6. `docs(reference): document the reply ending and the bridge question`

## Done when
- An urgent review beats the bridge.
- The bridge beats an earned extend.
- No link means no bridge.
- Coverage-next is preferred, with its reason line.
- The bridge answer on a not-covered target feeds the not-covered offset.
- The gate passes:
  - `check_mcp` passes;
  - no result is over 2,400 characters;
  - rebuild gives identical state;
  - the instructions word count is reported (cues don't count).

## Tests
In `scripts/check_mcp.py` (`bridge`), one check per item under Done when.
