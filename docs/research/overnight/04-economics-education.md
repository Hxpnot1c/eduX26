# 04 · Economics education: mark structure, check types, misconceptions and examiner themes

Waves 1 and 2. Sources:
- **Wave 1:** scout notes `work/w1/w1-04.md`, verifier marks `work/w1/verify-B.json`, the teacher panel `work/w1/panel-teacher.md`. We also checked the example pack (`coursepacks/example-mini/`) and the demo captures (`sims/demo-captures/`) ourselves.
- **Wave 2:** scout notes `work/w2/w2-04.md`, verifier marks `work/w2/verify-G.json` (w2-04 rows), the panels `work/w2/panel-teacher-student.md` and `panel-judges-researcher.md`.

Builds on `docs/research/personalisation-findings.csv` (rows 3-10 and 5-05 already cover Eedi's outcome evidence) and `docs/build/reference/research.md` (Pan & Rickard, Agarwal, Barbieri et al., Zamary & Rawson), and doesn't repeat them. Learning-science moves that use this report's content (contrasting cases, self-marking, diagram practice) are in [03](03-learning-science.md).

Marks: ✓ confirmed by a blind verifier; ~ broadly supported, with the verifier's caveat given. No ✗ findings in this area. Exam-board documents are summarised as numbers and structure only. Nothing is quoted from them, and no question contexts are named.

## Summary

- **About two-thirds of 9EC0 marks are level-marked, and multiple choice is about 3.5%.** In the June 2025 mark schemes, Papers 1 and 2 each have 38 point-marked and 62 level-marked marks out of 100, and Paper 3 has 26 and 74. Weighted 35/35/30, that is 34.4% point-marked. Multiple choice is 10 of 300 raw marks (w2-04-02 ✓). eduX's only check today, a four-option MCQ, is the diagnostic way in, not the route to most marks.
- **Evaluation is about a quarter of the qualification, and some of it is point-marked.** Evaluation allocations add to 25, 25 and 30 marks, which agrees with the specification's AO4 band of 26–28% (w2-04-01 ✓, -02 ✓). Each 8-mark data-response part gives 2 marks each to knowledge, application, analysis and evaluation as points, not levels (w2-04-03 ✓). That is the cheapest real evaluation target.
- **We propose five server-scorable check types (C1–C5), with the panel's fixes.** None is built. `plan.ask_mcq` has no stem field, so even the MCQ-shaped ones (C1, C3, C4) need one. The panel fixes are:
  - every key must accept valid alternatives (such as monopsony);
  - C4 keys must accept that a point can either extend or weigh an argument;
  - a named teacher signs off every key;
  - C3 starts with a sketch on paper.
- **The evidence for chain tasks is cross-field and weak.** Faded ordering tasks transferred to code writing about as well as writing practice (w2-04-06 ~). Selection tasks overstate what students can produce (w2-04-14 ~). The nearest study, in a US business course, was small and non-randomised (w2-04-15 ~). No study shows any of these tasks raising economics essay marks.
- **Opportunity cost is the best-evidenced gateway idea, but "threshold concept" is a label, not a measured effect.** Only 21.6% of 199 economists and economics PhD students chose the intended answer to one item (w1-04-01 ✓). Students with a previous economics course did worse: 7.4% against 17.2% (w1-04-02 ✓). Understanding barely moved over a semester (3.58 to 3.68 of 5). Its level correlated with the final grade (r = .45), but its change did not (r = .01) (w1-04-03 ✓).
- **Misconceptions survive teaching, and we have sources for distractors.**
  - In US college TUCE-4 norming data, "business demand limits productive capacity" fell only from 43% to 32% (w1-04-05 ✓).
  - In a UK survey, 36% of adults read a falling inflation rate as falling prices (w1-04-07 ✓).
  - The 9EC0 examiner reports for 2023–25 are public and name the twin-concept confusions (w1-04-08 ✓, existence check).
- **The example pack has a content error and gives MCQ answers away by form.** `externality_tax_eval_m1`'s correction implies a well-set tax removes the externality; it internalises it. In all 6 MCQ option sets we captured, the correct option has no full stop and every distractor has one (our count).
- **Output:** 30 draft misconception rows in our own words, and worked C1–C5 examples, all awaiting a teacher's sign-off.

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on |
|---|---|---|---|---|---|
| 1 | **Fix the MCQ give-away in the pack.** Rewrite every `key_point` used as a correct option as a full sentence with a full stop, of similar length to its part's `wrong_idea` rows (within 0.7–1.3× the median distractor length; our choice). Do the parts on camera first: `ped_definition`, `ped_formula`, `ped_values`, `tax_incidence_split`. Give `ped_formula`'s second point ("Keep the minus sign") its own sign-error misconception, so its check stops reusing distractors about the formula. Then re-capture and re-count. | pack (team edit), video | S | yes | our capture count; w1 teacher #2; w1-04-10 ✓ |
| 2 | **Correct `externality_tax_eval_m1`** with the wording below, and drop "always" from its `wrong_idea`. | pack (team edit) | S | yes | economics (below); w1 teacher #3 |
| 3 | **Pitch and Q&A line from the tally:** "About two-thirds of 9EC0 marks are level-marked and multiple choice is about 3%. Our MCQs are the diagnostic way in; chain and evaluation checks are the path to the marks, and they're next." Say "about": Section A splits vary by year. The judges' panel called the counted split a strength. | pitch, Q&A | S | yes | w2-04-01 ✓, -02 ✓ |
| 4 | **Draft 2–3 C1 (missing link) and C3 (diagram shift) items as a labelled mock-up** for the video, on a less contested part such as `tax_incidence_split`. Apply the key rules below: name the model in the stem, use no distractor that another specification model makes right, and sketch first for C3. Label the items "draft, not yet signed off by a teacher". The stem field comes in step 07. | pack draft, video | S | yes (mock-up) | w2-04-06 ~, -13 ~; w2 teacher #2–3 |
| 5 | **Load the 30 candidate rows as `status=draft`** into the real Edexcel pack's `misconceptions.csv`, with source ids in `sources.csv` (examiner reports as type `examiner_report`). Map each placeholder `node_id` to a real part id at load: misconceptions are served per part, so a row on a concept node never reaches an MCQ. Aim for 3 misconceptions per gateway part (`mcq.max_options = 4`). A teacher signs the rows off before any student sees them. | pack | M (load S, review M) | load yes; review partly | w1-04-01 ✓, -05 ✓, -06 ~, -07 ✓, -08 ✓ |
| 6 | **Add `confusable` edges (`teach_use = contrast`)** for the twin concepts the examiner reports name: contestability↔competitiveness; price discrimination↔product differentiation; XED/YED/PED signs; PES↔PED determinants; economies of scale↔dynamic efficiency; current account↔budget deficit; absolute↔comparative advantage; HDI↔Gini; inflation rate↔price level; budget deficit↔national debt. Each needs a one-line note on how the pair differs. The example pack has only PED↔YED. These edges feed contrasting cases in reteach ([03](03-learning-science.md) rec 1). | `edges.csv` | S | yes | w1-04-08 ✓ (existence only); w1-04-07 ✓; w1-04-11 ✓ |
| 7 | **Add C1–C5 to `later.md` step 07** (team edit to `docs/build/`), with the tiers table, the key rules, teacher sign-off and the evidence-weight rule below. | `later.md` | S | yes (doc) | this report |
| 8 | **Rule for writing rows: one wrong option = one misconception**, in the same form and length as a correct point, with no "always" or "never". A wrong option that two different misconceptions could produce can't tell them apart, so rewrite or split it. Add it to `docs/build/reference/course-pack-format.md` (team edit). | course-pack-format doc | S | yes | w1-04-10 ✓; medical item-writing analogy (speculative) |
| 9 | **Mark gateway parts with what exists, not a new flag.** Add `prerequisite` edges from opportunity cost, marginal analysis and the multiplier (cumulative causation) to the parts that build on them, so `importance.w_dependents` ranks them higher. Set `difficulty = 0.7` (our choice) on those concepts. Externalities and welfare are not in Davies & Mangan's table, so give them the edges but not the "threshold" label. | `edges.csv`, `nodes.csv` | S | yes | w1-04-04 ~; w1-04-03 ✓ |
| 10 | **Demo and pitch moment: our own UK opportunity-cost item.** For example, a free festival ticket against a paid gig you value at more than its price. One key and three distractors, one each for "free means costless", "the price paid" and "the gross value". Pitch line: "only about one in five economists and economics PhD students picked the intended answer, and economists still argue about the key" (see [pitch-notes](pitch-notes.md)). Never present the key as beyond dispute. | demo, pitch | S | yes | w1-04-01 ✓; Potter & Sanders 2012 |
| 11 | **Transfer reviews for gateway parts give an unfamiliar case without naming the concept**, so the student picks the frame. A one-line change to the `review_transfer` cue (team edit). | `text/` cue | S | yes | w1-04-04 ~ |
| 12 | **Treat one misconception pick as weak evidence.** The design already activates a misconception on one pick and clears it on later correct evidence. Keep that, and never escalate from a single pick. Pitch: "we diagnose, then re-check". | pitch, design note | S | yes | w1-04-09 ✓ |
| 13 | **Run the opportunity-cost check even after "I know this"** (`skip_point`), at least as the first review, because prior exposure did not mean understanding. | settings / pack | S | yes | w1-04-02 ✓ |
| 14 | **Show the whole chain at once** in chain checks and chain reteaches. This is an exception to "one point per message", for chain tasks only. | `text/` cue, step 07 | S | partly | w2-04-13 ~, -12 ~ |
| 15 | **A key-review queue with a named teacher and a `contestable` flag.** Every C1–C5 key and every drafted row stays `draft` until a named teacher signs it off. A key the teacher marks `contestable` tells the student "examiners may credit other answers here", and a wrong answer on it never activates a misconception. Time each review and count disputed keys, so "who checks it?" gets a number. | step 07 / step 10, pack | M | no | w2 teacher #2, Q&A 2 |
| 16 | **Serve the 2 point-marked evaluation marks of 8-mark parts first**, through step 07's point-marked path (mark points for "one evaluative point with a reason"). | step 07, pack `mark_points.csv` | M | no | w2-04-03 ✓ |
| 17 | **Down-weight selection evidence.** A correct C1–C5 selection counts at half the weight of an explain-back point (our choice), and selection alone never marks a part "ready for levelled questions". | settings `[checks]`, learner | S | no | w2-04-14 ~ |
| 18 | **Ordering (C2) only after C1 works,** with cue words stripped and a validator warning. | step 07 | M | no | w2-04-04 ~ to -07 ~ |
| 19 | **Gate C5 by mastery** (≥ 0.7, our choice) and give novices completion tasks (C1). | step 07 | S | no | CSV 2-16 |
| 20 | **A plan-skeleton step before any levelled answer:** complete the chain (C1), pick the sentence that weighs it (C4), then write. Step 07 levels the result. This is also the end point for the "write my essay" draft moment the teacher panel raised: a plan, not prose. | step 07 | M | no | w2-04-08 ~ |
| 21 | **Pilot outcome: blind-levelled essays, not MCQ scores,** comparing chain checks with MCQ-only for one topic. | business plan / later | L | no | w2-04-15 ~ (the gap) |

## The 9EC0 mark split (numbers and structure only)

Method (scout, wave 2): read the specification for structure and assessment-objective weights. Then go through the June 2025 mark schemes for Papers 1–3 part by part. For each part, record whether marks are awarded per point or by level, and how the marks divide between knowledge, application and analysis (KAA) and evaluation. The verifier re-checked the 2025 tally (w2-04-02 ✓, -03 ✓). The scout also compared June 2023 Papers 1 and 3. The verifier did **not** check that comparison, so it is not evidence here.

**Structure** (w2-04-01 ✓). There are three papers, each 2 hours and 100 marks, weighted 35%, 35% and 30%.
- Papers 1 and 2 each have three sections: short questions (including multiple choice), one data-response question, and one extended answer chosen from two.
- Paper 3 has two data-response questions, each ending with a choice of extended answer.
- Assessment-objective bands are 22–24% each for AO1 and AO2, and 26–28% each for AO3 (analysis) and AO4 (evaluation).
- Source caveat: the copy read is Issue 2 (October 2016) on a school's website. Pearson's own link failed, and a later issue may exist.

**Marks by type, June 2025** (w2-04-02 ✓, -03 ✓; our tally):

| Paper (weight) | Point-marked | of which MCQ | Level-marked | Evaluation marks |
|---|---|---|---|---|
| 1 (35%) | 38 | 5 | 62 | 25 |
| 2 (35%) | 38 | 5 | 62 | 25 |
| 3 (30%) | 26 | 0 | 74 | 30 |
| **Weighted** | **34.4%** | **≈ 3.5% (10 of 300 raw marks)** | **≈ 66%** | **≈ 26.5%** |

How the marks are built, in our words:
- **Papers 1 and 2, short-question section (25 marks).** Five 5-mark questions. Each has one 1-mark multiple-choice item, and the rest are point-marked define, explain, calculate or diagram parts. The split inside this section varies by year, but the 25-mark total doesn't.
- **Papers 1 and 2, data response (50 marks).** A 5-mark and an 8-mark part are point-marked. The 8-mark part gives 2 points each to knowledge, application, analysis and evaluation. The 10-, 12- and 15-mark parts are levelled, each with a KAA share and an evaluation share (6+4, 8+4, 9+6). In 2025 Paper 1 has them in the order 12, 10, 15 and Paper 2 in the order 10, 12, 15.
- **Papers 1 and 2, extended answer (25 marks).** Levelled, 16 KAA and 9 evaluation.
- **Paper 3, each of two questions (50 marks).** Point-marked 5 and 8 (the 8 split as above), a levelled 12 (8 + 4) and a levelled 25 chosen from two (16 + 9).

**Cross-check:** evaluation marks total 2 + 4 + 4 + 6 + 9 = 25 on Papers 1 and 2, and (2 + 4 + 9) × 2 = 30 on Paper 3. Weighted, that is about 26.5%, inside the AO4 band.

**What it means for eduX.**
- MCQs target about 3.5% of the qualification directly, and point-marked short answers about another 30%. The levelled two-thirds needs step 07.
- The 8 point-marked evaluation marks per series (2 per 8-mark part; four such parts across the three papers) are evaluation practice that step 07's point-marked path can score before any levelling exists (rec 16).
- Confidence: high for structure, weights and the two-thirds share; medium for exact Section A splits, which vary by year.

## Five check types for the levelled marks (C1–C5)

"Rules-only" does not mean "selection-only". The chatbot ticks which of a fixed list of points a student's message contains, and the server scores the ticks. That gives three tiers:

| Tier | Example | Scoring reliability | Evidence of production |
|---|---|---|---|
| Server-keyed selection | MCQ, ordering, slot choice | exact | weak: selection overstates (w2-04-14 ~) |
| Chatbot-ticked short production | type the missing link; one-sentence "so what" | good if the accepted-points list is narrow | moderate |
| Levelled extended answer | 12- to 25-mark answers | needs a level per strand (step 07) | strong, but never a numeric mark |

### Key rules for every check (from the panel)

1. **A key must allow every valid alternative on the specification.** The teacher panel's example: a chain that runs a minimum wage through the competitive labour market marks wrong a strong student who argues monopsony, which is on the specification and is the best evaluation there. So:
   - the stem names the model ("in a competitive labour market");
   - a distractor must be wrong under **every** model on the specification, not only the one in the stem;
   - an answer that another model makes right ("it depends on whether the employer is a monopsonist") is never a distractor. It is accepted, or the item is rewritten;
   - parts where the models disagree (minimum wage, rent control) are flagged `contestable` and kept out of the demo.
2. **C4 keys accept that a point can serve either role.** The mark schemes credit the same point as KAA or as evaluation depending on how the candidate uses it. "Firms may replace workers with machines" can extend the chain or weigh it. A sentence that can play both roles is accepted for both, or not used.
3. **A named teacher signs off every key** before a student sees it. Keys stay `draft` until then (rec 15). The team are economics students, not teachers, so mock-ups are labelled "draft".
4. **Selection counts at half weight**, and never by itself marks a part ready for levelled questions (rec 17).

### C1 · Missing link (faded chain) — rank 1

- **Task:** the whole chain is shown at once (w2-04-13 ~), 4–5 links with one blank. The student picks the missing link from 4 options or types it.
- **Scoring:** the MCQ variant is server-keyed, with misconception links as distractors, through the existing `ask_mcq`. In the typed variant, the chatbot ticks against the accepted wording.
- **Targets:** KAA, because the top levels reward complete, connected reasoning.
- **Evidence:** faded ordering in code (w2-04-06 ~, analogy) plus inference transfer when items are shown together (w2-04-13 ~). Moderate to weak. Treating an economic chain as a procedure is our judgement, not a tested result.
- **Effort:** M. The MCQ needs a stem field (`ask_mcq` passes options only; for example a `chains.csv`), and the typed variant needs ticking against an accepted-wording list.
- **Design rule:** each adjacent pair is a direct cause and effect, and no two links are parallel effects of one cause.
- **Example** (ours; holds under every model on the specification, as rule 1 requires):
  - Chain: "A specific tax is put on each unit of a good → each firm's cost per unit rises → ____ → the price of the good rises → the quantity demanded falls."
  - Key: "the supply of the good shifts to the left (up by the tax)."
  - Distractors:
    - "the demand for the good shifts to the left" (a cost change read as a demand shift; row 7 and `tax_supply_shift_m1`);
    - "the supply of the good shifts to the right" (direction error; draft).
  - The scout's first draft used a minimum wage for care workers. We dropped it: under monopsony a minimum wage can lower the employer's marginal labour cost, so "supply shifts right" could be a valid answer and not a misconception.

### C2 · Order the chain (with one link that doesn't belong) — rank 3

- **Task:** order 4 shuffled links and leave out the one that doesn't belong.
- **Scoring:** the share of adjacent pairs in the right order, with 0 if the extra link is used (our choice). This needs a new answer type.
- **Evidence:** ordering gave equal learning in less time than writing code (w2-04-04 ~). Ordering scores correlated with code-writing scores (w2-04-05 ~). But the faded-Parsons authors report that plain ordering didn't transfer to writing (w2-04-06 ~; the verifier could not check that statement), and a review calls the evidence unreplicated (w2-04-07 ~). **A warm-up only, after C1.**
- **Give-away risk:** strip cue words ("therefore", "as a result") from link openings, or students solve by form. This is the same lesson as the full-stop give-away.

### C3 · Diagram shift, drawn first — rank 2

- **Task:** for a stated change, first "sketch it on paper". Then pick which curve moves (or none, with a line drawn instead), the direction, and what happens to price or wage and quantity. Four options are built from slot combinations, so it runs as an MCQ.
- **Why the sketch:** drawing helps only when followed by a step that joins the words to the picture (g = 0.35 with, −0.15 without; w2-03-03 ~ in [03](03-learning-science.md)). The slot answer is that step. The server never sees the sketch, so we don't claim to assess diagrams, and the slot answer counts as selection (half weight). Checking a photographed diagram is later and untested.
- **Targets:** diagram marks in short answers, and levelled parts that cap answers without a correct diagram. This matches examiner theme 1 below.
- **Evidence:** examiner-report themes (existence check only) and wave-1 rows. No direct learning trial: weak, but well aligned.
- **Example** (ours): "In a competitive labour market, a minimum wage is set above equilibrium."
  - Key: no curve shifts; a horizontal wage floor is drawn above equilibrium; the quantity of labour demanded falls and the quantity supplied rises.
  - Distractors: "labour demand shifts left; wage falls"; "labour supply shifts right; wage falls"; "a floor drawn at equilibrium; no change".
  - Flag `contestable`. A follow-up asks "what if the employer is a monopsonist?" and accepts that answer, rather than marking it wrong.

### C4 · The role of a sentence, relative to a stated argument — rank 4

- **Task:** the stem states the argument. The student picks which sentence **weighs** it (a condition, size, time period or counter-case). The simplest form is an MCQ: "Which sentence weighs this argument?"
- **Scoring:** server-keyed. Only sentences with a single role are used as distractors: off-question ones (a definition) and restatements. Any sentence that could extend *or* weigh is either accepted or left out (rule 2).
- **Targets:** evaluation. It teaches the criteria, which is the "product goals" mechanism in writing research (0.70; w2-04-08 ~).
- **Evidence:** writing meta-analysis plus case comparison (w2-04-10 ~). Moderate for the mechanism, weak for economics.
- **Example** (ours): stated argument "In a competitive labour market, a higher minimum wage reduces the quantity of labour firms demand."
  - Key: "The fall is small if demand for labour is wage-inelastic, as in care work where tasks are hard to automate."
  - Distractors: "A minimum wage is a legal floor employers must pay." (off-question); "So fewer workers are hired at the new wage." (restates).
  - Not used as a distractor: "Firms may replace some workers with machines." It extends the chain, and it can weigh the argument if used to judge size.
- **Not keyed:** "which point is strongest?". Examiners credit several valid judgements, so this needs teacher sign-off.

### C5 · Spot the unsupported judgement — rank 5, gated by mastery

- **Task:** read a 3-sentence conclusion and pick the sentence that asserts a judgement with no reason or condition, or repeats an earlier point.
- **Evidence:** erroneous examples help only learners with high prior knowledge (CSV 2-16). Examiner theme 6 (conclusions that repeat). Weak.
- **Gate:** only when the part's mastery is ≥ 0.7 (our choice).
- **Example** (ours):
  - (A) "Overall, the effect on employment is largest where demand for labour is elastic, as in hospitality."
  - (B) "Therefore the minimum wage is clearly a bad policy."
  - (C) "This depends on how far above the market wage it is set."
  - Key: B (no reason or condition, and normative).

### What the evidence does and doesn't show

- Writing research favours strategy instruction (0.82), summarising (0.82), product goals (0.70), sentence combining (0.50) and planning (0.32). Grammar teaching scored −0.32 (grades 4–12; w2-04-08 ~). Writing about content improves content learning, ES = 0.30 (w2-04-09 ~). Keep explain-back and add typed links, not grammar drills.
- High-level quizzing lifted both low- and high-level final-exam items in a biology course (w2-04-11 ~). Recall of premises practised one at a time didn't transfer to inference (w2-04-12 ~). Practised together, it did (w2-04-13 ~). **Definition MCQs alone shouldn't be expected to build analysis.**
- **No study shows these tasks raising economics essay marks.** The nearest is a non-randomised comparison in a US business course: structured writing helped multiple-choice results and only weakly helped essays (w2-04-15 ~). Hence rec 21.

## The content error: `externality_tax_eval_m1`

What the pack says (`coursepacks/example-mini/misconceptions.csv`, row `externality_tax_eval_m1`):
- `wrong_idea`: "A tax always removes the externality completely."
- `correction`: "It reduces output towards the optimum, but only fully if the tax equals the marginal external cost."

**We agree with the teacher that the correction is wrong.** In economics terms:
- A tax equal to the marginal external cost at the socially optimal output is a Pigouvian tax. It **internalises** the externality: the producer now faces the full social cost, so private and social cost coincide.
- Output falls from the market level to the social optimum, where marginal social benefit equals marginal social cost. That removes the **welfare loss** (the deadweight triangle), not the external cost.
- At the optimum, production still pollutes, and third parties still bear that external cost. The efficient amount of pollution is usually not zero. The tax raises revenue, but the people harmed are not compensated unless the government chooses to use it that way.
- So "only fully if the tax equals the MEC" tells a student that a well-set tax eliminates the externality. That is the very misconception the row is meant to correct, with a condition added.
- The pack contradicts itself. Its own note for this part (`externality_tax_eval_n1`) uses "internalises the externality" as the key wording.
- The `wrong_idea` also uses "always", the absolute word that gives a distractor away (rec 8).

**Suggested wording (ours, for teacher sign-off):**
- `wrong_idea`: "A tax on pollution stops the external cost altogether."
- `correction`: "Even a tax set at the marginal external cost leaves some pollution; it makes firms pay for it, so output falls to the social optimum and the welfare loss goes, not the external cost."

One error in nine parts is not an error rate. It does show that drafted rows need an economist's review before students see them (teacher Q&A question 2).

## The MCQ give-away, measured

Method: we walked every JSON file in `sims/demo-captures/`, collected every MCQ option set, and marked each option as a distractor if its text matches a `wrong_idea` in `example-mini/misconceptions.csv`, and as correct otherwise. The same set, shuffled for different students, counts once. Simulation context: synthetic demo students, example pack.

| measure | correct option | distractors |
|---|---|---|
| distinct option sets | 6 (in 17 different orderings across the captures) | |
| options counted | 6 | 13 |
| mean length (characters) | 34 | 59 |
| median length | 31 | 53 |
| ends with a full stop | 0 of 6 | 13 of 13 |
| shortest option in its set | 5 of 6 | |

- A student who picks "the option with no full stop" scores 6 out of 6. One who picks "the shortest option" scores 5 out of 6.
- The one exception is the intuition question on `ped_formula`. Its correct option is the key wording "% change in quantity demanded divided by % change in price" (58 characters). It is not the shortest, but it still has no full stop and doesn't read as a sentence.
- The ratio of correct length to median distractor length ranges from 0.36 ("Keep the minus sign") to 1.09. Three of the six sets fall below 0.7.
- **Root cause:** correct options come from `notes.csv` `key_points`. These are revision-card fragments: 22 of them, mean 22 characters, none with a full stop. Distractors come from `wrong_idea`: 13 rows, mean 53 characters, all full sentences with full stops. Commit f0a1c36 fixed *which* option is correct, not its form.
- **Second problem (the teacher's):** the check on "Keep the minus sign" reuses `ped_formula`'s three misconceptions, which are about the formula, not the sign. The check therefore tests "which line did I just read" while that line is still on screen.
- **Wave 3 found the opposite cue on parts with no points, and both are true.** When a part has no mark point, `plan._points` falls back to the node description, which becomes the longest option in 7 of 9 parts (w3-05-08 ~; [05](05-product-features.md)). Here the key came from a point and is a short fragment. The agreed fix covers both: never use the description as an option, keep the point as the key with matched length and punctuation, and skip the MCQ when a part has no points (05 rec 11; a wave-4 scout is testing it).
- **Not a problem on the 05e branch:** the how-AI-works check on invented links has matched options (61, 57, 56 and 56 characters, none with a full stop), after commit 7674bbd on `build/05e-literacy-coaching`. The fix used there can be copied to the economics pack.

## Candidate misconception rows

Core columns match `misconceptions.csv` (`id, node_id, wrong_idea, correction, source_ids`, with `status=draft`). All wording is ours. Themes are named in general terms only; nothing is quoted from exam-board documents.

**`node_id`s are placeholders** unless marked "(existing)", meaning they already exist in `coursepacks/example-mini/`. Map each to the real pack's part id at load. Rows 13–30 that rest on examiner reports have been checked only for the reports' existence, apart from contestability (row 13).

| # | id | node_id | wrong_idea | correction | source_ids | flag | evidence (population) |
|---|---|---|---|---|---|---|---|
| 1 | opportunity_cost_definition_m1 | opportunity_cost_definition | Something you get free of charge has no opportunity cost. | Using it still means giving up your next best alternative, so its opportunity cost is that alternative's net value. | ferraro_taylor_2005 | key disputed (potter_sanders_2012) | 25.1% chose "$0" (199 economists and PhD students, US) |
| 2 | opportunity_cost_definition_m2 | opportunity_cost_definition | The opportunity cost of a choice is the price of the alternative you gave up. | It is what the next best alternative was worth to you, minus what it would have cost; the price alone is not the cost. | ferraro_taylor_2005 | key disputed | 25.6% (as above) |
| 3 | opportunity_cost_definition_m3 | opportunity_cost_definition | The opportunity cost is the full value you would have got from the alternative. | Giving up the alternative also saves you its cost, so subtract that cost: only the net benefit is lost. | ferraro_taylor_2005 | key disputed | 27.6% (as above) |
| 4 | ppf_shape_m1 | ppf_shape | The PPF bows outwards because making more of one good means making less of the other. | That explains why it slopes down; it bows out because resources are not equally suited to every use, so each extra unit costs more. | shanahan_foster_meyer_2006 | | coded as the "second-best" option; no % (431 first-years, Australia) |
| 5 | price_simultaneous_shifts_m1 | price_simultaneous_shifts | If demand and supply both increase, the price must rise. | Quantity rises, but price depends on which shift is bigger; equal shifts leave it unchanged. | pang_marton_2005 | not verified; no % | teaching target in a variation-theory study |
| 6 | price_determination_mechanism_m1 | price_determination_mechanism | A good's price is high because it is useful or well made. | In a market, price is set by demand and supply together; usefulness matters only through demand. | davies_2013 | not verified; qualitative | first category of price conception in phenomenographic studies (Davies n = 10, UK undergraduates) |
| 7 | supply_shift_causes_m1 | supply_shift_causes | A rise in firms' costs of production reduces demand for the product. | Higher costs shift supply to the left; demand depends on buyers and does not shift. | tuce4_2007 | | 15% before, 10% after a course (US college, n = 3,255) |
| 8 | perfect_competition_long_run_m1 | perfect_competition_long_run | If costs rise for every firm in a competitive industry, their long-run economic profit falls. | In the long run, exit brings economic profit back to zero (normal profit); the lasting effect is lower supply and a higher price. | tuce4_2007 | | 36% before, 28% after (as above) |
| 9 | externality_tax_eval_m2 | externality_tax_eval (existing) | Firms would rather pay a pollution tax than cut production, so the tax changes nothing. | The tax makes polluting costlier, so firms cut pollution or output wherever that is cheaper than paying. | tuce4_2007 | | 33% before, 29% after (as above) |
| 10 | externality_tax_eval_m3 | externality_tax_eval (existing) | A tax on pollution shifts the demand curve, whereas a tax on the product shifts supply. | Both taxes are paid by producers, so both raise their costs; neither shifts demand. | tuce4_2007 | | 15% before, 11% after (as above) |
| 11 | lras_determinants_m1 | lras_determinants | An economy's productive capacity is limited by how much businesses want to buy. | Demand decides how much capacity is used; capacity itself depends on the quantity and quality of factors of production. | tuce4_2007 | table 43%, sample block 42% | 43% before, 32% after (US college, n = 2,789) |
| 12 | maximum_price_effects_m1 | maximum_price_effects | A maximum rent increases the number of homes available to rent. | In the supply and demand model, a ceiling below equilibrium lowers the quantity supplied, so there is a shortage, though tenants who find a home pay less. | brandts_etal_2022 | model prediction; policy-laden | 69% and 77% agreed at the start of term (first-years, Barcelona) |
| 13 | contestability_definition_m1 | contestability_definition | A market is contestable when many firms already compete in it. | Contestability is about the threat of entry (low barriers, low sunk costs), even if few firms are in the market now. | er_2024_p1; er_2025_p1 | | named in 2024 (citing 2022) and 2025 reports; no % (9EC0 candidates) |
| 14 | price_discrimination_definition_m1 | price_discrimination_definition | Price discrimination means charging different prices for different versions of a product. | It means charging different groups different prices for the same product, for reasons unrelated to cost. | er_2023_p1 | report theme not verified | no % |
| 15 | xed_values_m1 | xed_values | A negative cross elasticity of demand means the goods are substitutes. | Negative XED means complements; substitutes have positive XED. | er_2023_p1 | report theme not verified | no % |
| 16 | yed_values_m1 | yed_values | A necessity has a negative income elasticity of demand. | Necessities are normal goods with YED between 0 and 1; only inferior goods have negative YED. | er_2025_p1 | report theme not verified | no % |
| 17 | ped_values_m2 | ped_values (existing) | If PED changes from −0.3 to −0.6, demand has become price elastic. | Both values are below 1 ignoring the sign, so demand is still inelastic, just less so. | er_2024_p1 | report theme not verified | no % |
| 18 | pes_determinants_m1 | pes_determinants | Supply is price elastic when buyers have many substitutes. | Substitutes affect PED; PES depends on how easily firms can raise output (spare capacity, stocks, time, mobile factors). | er_2024_p1 | report theme not verified | no % |
| 19 | positive_externality_diagram_m1 | positive_externality_diagram | For a good with external benefits, the MSB curve lies below the MPB curve. | MSB equals MPB plus the external benefit, so MSB lies above MPB. | er_2025_p1 | report theme not verified | no % |
| 20 | minimum_wage_diagram_m1 | minimum_wage_diagram | A national minimum wage is drawn at the market-clearing wage. | To bind, it is set above equilibrium; in the competitive model this shows an excess supply of labour. | er_2025_p1 | model only; real effects debated | no % |
| 21 | economies_of_scale_definition_m1 | economies_of_scale_definition | Economies of scale shift the long-run average cost curve down over time. | Economies of scale are a move along LRAC as output grows; a downward shift over time is dynamic efficiency (for example, innovation). | er_2024_p1 | report theme not verified | no % |
| 22 | ad_as_diagram_axes_m1 | ad_as_diagram_axes | The vertical axis of an AD/AS diagram shows the price of a good. | It shows the average price level across the whole economy. | er_2025_p2 | report theme not verified | no % |
| 23 | inflation_rate_meaning_m1 | inflation_rate_meaning | When the inflation rate falls, prices are falling. | A lower positive inflation rate means prices still rise, just more slowly; prices fall only when inflation is negative (deflation). | escoe_2023 | | 36% read 10.1%→6.1% as prices falling (UK adults, Aug 2022) |
| 24 | percentage_points_m1 | percentage_points | A rate that rises from 2% to 3% has risen by 1%. | It has risen by 1 percentage point, which is a 50% increase in the rate. | er_2025_p2; er_2025_p3 | report theme not verified | no % |
| 25 | current_account_definition_m1 | current_account_definition | A current account deficit means the government spends more than it raises in taxes. | That is a budget deficit; a current account deficit means payments abroad for goods, services and income exceed receipts. | er_2024_p2 | report theme not verified | no % |
| 26 | comparative_advantage_definition_m1 | comparative_advantage_definition | A country gains from trade only in goods it produces more efficiently than other countries. | Gains come from comparative advantage: specialise where your opportunity cost is lower, even if you are less efficient at everything. | er_2024_p2 | report theme not verified | no % |
| 27 | multiplier_process_m1 | multiplier_process | The multiplier makes spending go round forever, so national income rises without limit. | Each round is smaller because of withdrawals (saving, tax, imports), so the total converges to a finite multiple of the injection. | davies_mangan_2007; er_2024_p2 | qualitative | UK undergraduates (handbook); 9EC0 candidates |
| 28 | phillips_curve_short_run_m1 | phillips_curve_short_run | Higher unemployment comes with higher inflation, because bad things in the economy go together. | In the short-run model, lower unemployment tends to go with higher inflation; both rising together (stagflation) usually needs a supply shock. | leiser_aroch_2009 | abstract only; example from secondary summaries | lay adults (country not confirmed) |
| 29 | deficit_debt_relationship_m1 | deficit_debt_relationship | When the budget deficit falls, the national debt falls. | Debt is a stock fed by the deficit (a flow); while there is any deficit, debt still rises, just more slowly. | sweeney_sterman_2000 | analogy (stock-flow) | fewer than half showed a stock rising while inflow > outflow (graduate students, mostly MIT Sloan) |
| 30 | development_indicators_m1 | development_indicators | A rising Gini coefficient is a sign of development, like a rising HDI. | A higher HDI is better, but a higher Gini means more inequality. | er_2025_p3 | report theme not verified | no % |

Rows left out because they duplicate existing ones: elasticity as slope (`ped_definition_m1`), percentage change from the new value (`ped_formula_m2`; add `er_2023_p1` to its sources) and indirect tax shifting demand (`tax_supply_shift_m1`).

Row 9 and the corrected `externality_tax_eval_m1` together give `externality_tax_eval` three misconceptions with row 10. Opportunity cost reaches three with rows 1–3. Every other proposed part has one row, so it still needs `extra_option` or more rows.

### Source ids

| source_id | type | citation |
|---|---|---|
| `ferraro_taylor_2005` | research | Ferraro, P.J. & Taylor, L.O. (2005). Do economists recognize an opportunity cost when they see one? A dismal performance from the dismal science. *Contributions to Economic Analysis & Policy* 4(1), Art. 7. https://ideas.repec.org/a/bpj/bejeap/vcontributions.4y2005i1n7.html |
| `potter_sanders_2012` | research | Potter, J. & Sanders, S. (2012). Do economists recognize an opportunity cost when they see one? A dismal performance or an arbitrary concept? *Southern Economic Journal* 79(2), 248–256. (Not separately verified.) |
| `shanahan_foster_meyer_2006` | research | Shanahan, M.P., Foster, G. & Meyer, J.H.F. (2006). Operationalising a threshold concept in economics. *International Review of Economics Education* 5(2), 29–57. https://www.economicsnetwork.ac.uk/iree/v5n2/shanahan.pdf |
| `davies_mangan_2007` | research | Davies, P. & Mangan, J. (2007). Threshold concepts and the integration of understanding in economics. *Studies in Higher Education* 32(6), 711–726. Paywalled; read via https://economicsnetwork.ac.uk/handbook/thresholdconcepts |
| `davies_2013` | research | Davies, P. (2013). Conference slides, Developments in Economics Education. https://economicsnetwork.ac.uk/dee2013/Peter%20Davies.pdf (not verified) |
| `pang_marton_2005` | research | Pang, M.F. & Marton, F. (2005). Learning theory as teaching resource. *Instructional Science* 33. https://pmc.ncbi.nlm.nih.gov/articles/PMC7089241/ (not verified) |
| `tuce4_2007` | research | Walstad, W.B., Watts, M. & Rebeck, K. (2007). *TUCE, 4th ed.: Examiner's Manual.* NCEE. https://www.econedlink.org/wp-content/uploads/2018/09/TUCE-4th.pdf |
| `brandts_etal_2022` | research | Brandts, J., Busom, I., Lopez-Mayan, C. & Panadés, J. (2022). Dispelling misconceptions about economics. *Journal of Economic Psychology* 88, 102461. Figures via https://focus.bse.eu/dispelling-misconceptions-rent-control/ |
| `escoe_2023` | research | Runge, J., da Silva Gomes, E. & Hughes, M. (2023). Falling inflation, tight labour market, and recessions. ESCoE blog. https://www.escoe.ac.uk/falling-inflation-tight-labour-market-and-recessions/ |
| `leiser_aroch_2009` | research | Leiser, D. & Aroch, R. (2009). Lay understanding of macroeconomic causation: the good-begets-good heuristic. *Applied Psychology* 58(3), 370–384 (abstract only). |
| `sweeney_sterman_2000` | research | Booth Sweeney, L. & Sterman, J.D. (2000). Bathtub dynamics. *System Dynamics Review* 16(4) (citation unverified). https://proceedings.systemdynamics.org/2000/PDFs/sweeney4.pdf |
| `er_2023_p1`…`er_2025_p3` | examiner_report | Pearson Edexcel, Examiners' Reports June 2023, 2024 and 2025, GCE Economics A 9EC0 Papers 01–03, on Pearson's qualifications site (e.g. https://qualifications.pearson.com/content/dam/pdf/A-Level/Economics/2015/Exam-materials/9ec0-01-pef-20250814.pdf). Summarised only, never quoted. |

## Examiner-report themes (9EC0, 2023–25), summarised

From the scout's reading. The verifier confirmed only that the reports exist and that the contestability theme appears (w1-04-08 ✓). Treat the rest as the scout's reading until a second person checks it.

1. **Diagrams:** curves swapped or misplaced (MSB/MPB, a minimum wage drawn at equilibrium, the subsidy area); static diagrams with no shift; diagrams drawn but never used; wrong axis labels.
2. **Twin-concept confusions:** the pairs listed in rec 6, plus labour shortage vs unemployment and positive vs normative.
3. **Quantitative slips:** the wrong base for a percentage change; percentage vs percentage points; sign errors; multiplier totals smaller than the injection; no working shown.
4. **Answering the question set:** cause and effect swapped; one factor when several were asked for; long answers to 2-mark questions.
5. **Application:** too theoretical, with no use of the extract or data; misread figures.
6. **Evaluation:** conclusions that repeat earlier points instead of judging scale, significance and context.

Themes 1–3 become rows, `confusable` edges and C3 diagram checks. Theme 4 fits the existing "answer the question set" cue. Themes 5–6 need level-marked answers (step 07, not built). Before levelling exists, C4 and C5 target theme 6, and the 2 point-marked evaluation marks on each 8-mark part are the first scorable evaluation practice (rec 16).

## Later (not before Thursday; for the business plan and Q&A)

- **The stem field and C1–C5 in step 07.** C1, C3 and C4 need a stem: a `chains.csv`, or a stem column on `questions.csv`. C2 needs an ordering answer type. The levelled path stays as `later.md` describes.
- **A measured review rate.** Time a teacher reviewing one part's rows and one C4 item, and count errors and disputed keys (w2 teacher questions 1 and 4). Ties to step 10 (not built).
- **How often would a monopsony or "depends on elasticity" answer conflict with a C1 or C4 key** across past 8- and 12-mark parts? Summaries only, no reproduced items.
- **Does completing chains raise levelled analysis marks in economics?** No study exists (w2-04-15 ~). Run the blind-levelled pilot (rec 21).
- **Photographed diagrams.** Can a chatbot's image input reliably label which curve moved and which way, for server scoring? Untested (student panel).
- **Graded distractors.** Shanahan et al. scored a "second-best" option as partial credit. A `partial` column could feed a score of 0.5 into knowledge tracing. M effort, code change.
- **Two-tier checks** for gateway parts (an answer, then a reason). Explain-back covers most of this already.
- **A pack validator warning** when a correct option's length falls outside 0.7–1.3× the median distractor length, or when it lacks a full stop and the distractors have one (our choice of thresholds). The same check applies to C2 cue words.
- **Tally the examiner reports** for which themes lose the most marks. Not done yet.
- **TEL-4 high-school data** (US, closest age match). The PDF fonts blocked text extraction; worth a proper tool.

## Considered and rejected

- **Keying "a higher minimum wage reduces employment" as correct.** The empirical evidence is mixed, and monopsony is on the specification. Row 20 and C3 test the diagram in a named model instead.
- **Distractors that are right under another specification model** (for example monopsony). They would mark the best students wrong (key rule 1).
- **Absolute "KAA or evaluation?" labels.** The mark schemes let the same point count as either, depending on use (key rule 2).
- **"Which evaluation point is strongest?" as an auto-keyed item.** Examiners credit several valid judgements. Only with teacher sign-off.
- **Keyword-matching essays on the server** (counting "however" or "depends on"). Easy to game, and it rewards surface form, like the full-stop give-away.
- **Sentence-combining as grammar drills.** Grammar instruction scored −0.32 (w2-04-08 ~). Keep combining tied to the economic link.
- **Treating ordering (C2) as evidence of essay skill.** Selection overstates knowledge (w2-04-14 ~), and transfer from plain ordering is doubtful (w2-04-06 ~).
- **A new `threshold` column in `nodes.csv`.** There is no measured evidence that flagging a threshold concept improves learning (w1-04-03 ✓). Edges and `difficulty` give the same scheduling effect with no code.
- **Stantcheva's "prices rise faster than wages" finding.** It is a perception of one period's data, not a concept error.
- **Sapienza & Zingales expert–public gaps.** These are policy opinions, not concept errors.
- **Copying TUCE or TEL item stems.** These are secure, copyrighted tests. We paraphrase three published items as misconceptions only.
- **Quoting examiner reports, mark schemes or past papers.** Numbers, structure and summaries only. All examples here are ours.
- **Citing Hinze, Wiley & Pellegrino (2013) on explanation tests.** It is relevant, but we couldn't read its abstract.

## Panel objections this report answers or leaves open

Status words: **answered** = built or answered by a document; **recommended** = fix recommended, not built; **partly**; **open**. Wave-1 rows are re-labelled with these words: no pack edit has been made yet.

| Objection (panel) | Status | Where |
|---|---|---|
| "You aim at 3% of my marks; the build hasn't moved" (w2 teacher #1; judges Q&A 4) | **Partly** | The counted split is in this report, with an honest pitch line (rec 3). C1–C5 are specified with key rules (rec 7). Nothing is built, and `ask_mcq` has no stem field. |
| "Show me a C1 item running" (w2 teacher Q&A 1) | **Open** | A labelled mock-up only (rec 4). The stem field comes in step 07. |
| "The worked examples would penalise my best students: monopsony, and C4 'extends' vs 'weighs'" (w2 teacher #2) | **Recommended** | Key rules 1–2: name the model; no distractor that another specification model makes right; `contestable` flag; a sentence that can play both roles is accepted for both or not used. The C1 example now uses a specific tax; C3 and C4 name a competitive labour market, and C3 accepts a monopsony follow-up. The rules are written, not applied to a real pack. |
| "Who signs off a keyed evaluation sentence?" (w2 teacher #2, Q&A 2) | **Recommended** | Key rule 3 and rec 15: a named teacher, a queue, a `contestable` flag. Not built. |
| "Selection still counts towards mastery; C3 never makes anyone draw" (w2 teacher #3) | **Recommended** | C3 starts with a paper sketch (as [03](03-learning-science.md) rec 3). Selection at half weight, never "ready" (rec 17, not before Thursday). |
| "The draft moment still writes the 25-marker" (w2 teacher #5) | **Partly** | Rec 20 makes the plan skeleton the end point. The draft moment itself belongs to the product and literacy reports. |
| "Which sentence weighs the argument" helps me (w2 student praise) | **Recommended** | C4, rank 4. |
| "Can I send a photo of my diagram?" (w2 student Q&A 2) | **Open** | Later: untested. |
| "The correct option gives itself away" (w1 teacher #2, student #3, judges #5) | **Recommended** | Measured (6 of 6 option sets) and root cause found. Rec 1 is a team edit to the pack, not yet made. Pasted explain-backs remain open. |
| "The check on 'Keep the minus sign' uses distractors about other points" (w1 teacher #2) | **Recommended** | Rec 1: give each point its own misconception. |
| "I'd already red-pen one row" (w1 teacher #3) | **Recommended** | We agree, explain why, and give corrected wording (rec 2). The pack isn't edited yet. |
| "Who checks the content, and how often is it wrong?" (w1 teacher #3) | **Partly** | New rows stay drafts until sign-off (rec 5), and rec 15 adds a timed review queue. No error rate exists yet. |
| "It teaches recognition, not what the exam rewards" (w1 teacher #1, student #5) | **Partly** | Rows target the board's named errors, transfer reviews don't name the concept (rec 11), and C1–C5 are the specified next step. Levelled answers are still step 07. |
| "Distractors come from where?" (w1 judges; teacher praise) | **Answered** | This document: published research, UK survey data and examiner reports, with populations stated (rec 5). |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-04-01 | 21.6% of 199 economists and PhD students chose the intended opportunity-cost answer; wrong options drew 25.1/25.6/27.6% | correlational (survey) | US, ASSA 2005; about a third PhD students; not 16–18 | learning (concept test) | ✓ |
| w1-04-02 | Students with a prior economics course were correct less often (7.4% vs 17.2%, p = 0.008, n = 358) | correlational | US first-year undergraduates | learning | ✓ |
| w1-04-03 | Opportunity-cost score 3.58 → 3.68 of 5 over a semester; level correlates with final grade (r = .45), change does not (r = .01) | correlational | n = 431, first-years, Australia | learning | ✓ |
| w1-04-04 | Davies & Mangan's table: four threshold concepts (opportunity cost, marginality, incentives, cumulative causation); modelling concepts separate; assess with unfamiliar problems | theory (qualitative) | UK first-year undergraduates | learning (qualitative) | ~ secondary source; welfare and interacting markets not in the table |
| w1-04-05 | TUCE-4 distractors persist: 43→32%, 36→28%, 33→29%; mean correct about 31–33% → 43–47% | correlational (norming) | US college, n = 3,255 micro, 2,789 macro | learning | ✓ |
| w1-04-06 | 69% / 77% of first-years believed rent control helps; information reduced but did not remove the belief | RCT (lab) + quasi-experimental (field) | Spain, first-years; lab n = 172 | learning (belief change) | ~ authors' summary only; in the field, refutation beat the no-information control; in the lab it was not better than a plain text |
| w1-04-07 | 36% of UK adults read a fall in inflation as falling prices; 50% correct; 44% linked GDP to size of economy | correlational (survey) | UK adults, YouGov, Aug 2022 | learning (understanding) | ✓ |
| w1-04-08 | 9EC0 examiner reports 2023–25 exist and name recurring confusions, including contestability vs competition | official document | 9EC0 candidates, England | learning (exam performance) | ✓ existence check; other themes unchecked |
| w1-04-09 | Misconception choice rises then falls with ability; instruction can strengthen it first | correlational (IRT) | n = 1,250, US grades 8–12, astronomy | learning | ✓ |
| w1-04-10 | Eedi diagnostic questions: 4-option maths items with misconception distractors; 20M+ records | practitioner (dataset) | UK school maths (setting not checked) | prediction | ✓ |
| w1-04-11 | Stock-flow tasks: 77% vs 48% average; fewer than half showed the stock rising when inflow > outflow | correlational | graduate students, mostly MIT Sloan | learning | ✓ |
| w1-04-12 | "Good begets good" heuristic in lay macro judgements | correlational | lay adults (country not confirmed) | learning (causal judgement) | ~ abstract only; unemployment–inflation example from secondary summaries |
| w2-04-01 | 9EC0: three 2-hour, 100-mark papers, 35/35/30; section structure as above; AO1/AO2 22–24% each, AO3/AO4 26–28% each | official document | 9EC0 candidates, England, 16–18 | policy (assessment design) | ✓ third-party copy of Issue 2 (2016); a later issue may exist |
| w2-04-02 | June 2025: Papers 1–2 each 38 point / 62 level, Paper 3 26 / 74; MCQ 5 + 5 + 0; weighted 34.4% point, ≈ 66% level, ≈ 3.5% MCQ; evaluation 25/25/30 | official document (our tally) | 9EC0 candidates | policy | ✓ 2025 tally; 2023 cross-check not verified |
| w2-04-03 | 8-mark data-response parts (one each on Papers 1–2, two on Paper 3) are point-marked 2+2+2+2 across knowledge, application, analysis, evaluation | official document | 9EC0 candidates | policy | ✓ 2025; 2023 not checked |
| w2-04-04 | Ordering (2D Parsons) problems took less time than fixing or writing code, with no difference in learning or 1-week retention | experimental comparison | introductory programming learners; not 16–18, not UK | learning; cost (time) | ~ abstract only |
| w2-04-05 | Parsons scores correlated notably with code-writing scores, weakly with tracing | correlational | university CS1 exam takers | prediction (assessment validity) | ~ abstract only |
| w2-04-06 | Faded Parsons beat code writing and tracing on patterns and improved writing about as much as writing practice; earlier plain Parsons did not transfer | RCT (small, within-subjects) | US university CS1 (237 consented) | learning | ~ abstract confirms the main result; the 50/43 analysed and the "plain Parsons didn't transfer" statement not checked |
| w2-04-07 | A review finds Parsons effectiveness uncertain for lack of replication | theory (narrative review) | introductory CS students | learning | ~ abstract only |
| w2-04-08 | Writing instruction, grades 4–12: strategy 0.82, summarising 0.82, peer help 0.75, product goals 0.70, sentence combining 0.50, prewriting 0.32, models 0.25, grammar −0.32 | meta-analysis (123 documents, 154 ES) | grades 4–12 | learning (writing quality) | ~ abstract only; "5 studies" for sentence combining and "mostly US" not verified |
| w2-04-09 | Writing about content improved content learning, ES = 0.30 (56 experiments), similar across subjects and school levels | meta-analysis | grades 1–12 | learning | ~ abstract only; CI 0.20–0.41 not verified |
| w2-04-10 | Case comparison d = .50 [.44, .56] across 57 experiments; larger with similarity search, principle after, immediate tests | meta-analysis | mixed ages, lab and classroom | learning | ~ abstract only; same paper as w2-03-01 in [03](03-learning-science.md) |
| w2-04-11 | A biology section quizzed all term at high level beat a low-level section on both low- and high-level final items | quasi-experimental (two intact sections) | US undergraduates | learning | ~ abstract only |
| w2-04-12 | Recall of premises practised one at a time improved premise recall but not deductive inference | RCT (lab, 4 experiments) | adult lab participants | learning | ~ abstract only |
| w2-04-13 | With related sentences shown together, retrieval practice aided inference 2 days later; one at a time it did not | RCT (lab, 3 experiments) | adult lab participants | learning | ~ abstract only |
| w2-04-14 | Fill-in-the-map scores sat near maximum; construct-a-map exposed incomplete knowledge | correlational (measurement) | US school science students | prediction (assessment validity) | ~ abstract only |
| w2-04-15 | Structured writing went with better lower-order (MCQ) results but only weakly better higher-order results | quasi-experimental (non-randomised, across semesters) | US undergraduates, about 210 in six sections | learning | ~ the course was "The International Context of Business" (ECO 305), not principles of economics |
| (ours) | Example-pack MCQs: correct option has no full stop in 6/6 sets, is shortest in 5/6; mean 34 vs 59 characters | our measurement (captures) | synthetic demo students, example pack | n/a (assessment design) | not verified (our count; reproducible from `sims/demo-captures/`) |
