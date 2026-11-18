# 04 · Economics education: gateway ideas, misconceptions and examiner themes

Wave 1. Sources: scout notes `work/w1/w1-04.md`, verifier marks `work/w1/verify-B.json`, the teacher panel `work/w1/panel-teacher.md`. We also checked the example pack (`coursepacks/example-mini/`) and the demo captures (`sims/demo-captures/`) ourselves. Builds on `docs/research/personalisation-findings.csv` (rows 3-10 and 5-05 already cover Eedi's outcome evidence) and does not repeat it.

Marks: ✓ confirmed by a blind verifier; ~ broadly supported, with the verifier's caveat given. No ✗ findings in this area.

## Summary

- **Opportunity cost is the best-evidenced gateway idea.** On one four-option item, only 21.6% of 199 economists and economics PhD students (about a third were students) chose the intended answer. Each wrong option drew 25–28% (w1-04-01 ✓). Students with a previous economics course did *worse* than those without: 7.4% against 17.2% (w1-04-02 ✓). Potter & Sanders (2012) dispute the item's key answer (not separately verified).
- **"Threshold concept" is a theory label, not a measured effect.** Davies & Mangan's table names four threshold concepts: opportunity cost, marginality, incentives and cumulative causation (w1-04-04 ~ secondary source; welfare and interacting markets appear elsewhere on the page, not in the table). The one quantitative test found opportunity-cost understanding barely moved over a semester, from 3.58 to 3.68 out of 5. The *level* of understanding correlated with the final grade (r = .45); the *change* did not (r = .01) (w1-04-03 ✓).
- **Misconceptions survive teaching.** In the US college norming data for the TUCE-4 test, "business demand limits productive capacity" fell only from 43% to 32% after a principles course. "Firms just pay the pollution tax" fell from 33% to 29% (w1-04-05 ✓). Belief in rent control fell after information but was not removed (w1-04-06 ~).
- **There is UK evidence for an inflation-rate vs price-level distractor.** In a YouGov survey for NIESR (August 2022), 36% of UK adults read "inflation fell from 10.1% to 6.1%" as prices falling (w1-04-07 ✓). These were adults, not students.
- **The 9EC0 examiner reports (2023–25) are public and a legitimate source of distractors.** The verifier confirmed they exist and corroborated the contestability-vs-competition theme. The other themes rest on the scout's own reading (w1-04-08 ✓, existence check only).
- **The example pack has a content error, and we agree with the teacher.** `externality_tax_eval_m1`'s correction implies that a correctly set tax removes the externality. It doesn't: it internalises it. Output falls to the social optimum, where some pollution and external cost remain (see below).
- **The example pack's MCQs give the answer away by form.** In the six distinct MCQs captured, the correct option never ends with a full stop and all 13 distractors do. The correct option is the shortest in 5 of 6. Correct options average 34 characters against 59 for distractors (our count, below).
- **Output:** 30 candidate misconception rows in our own words, as drafts with placeholder part ids, ready for the real pack once a teacher has reviewed them.

## Ranked recommendations

| Rank | Recommendation | Lands in | Effort | Before Thursday? | Rests on |
|---|---|---|---|---|---|
| 1 | **Fix the MCQ give-away in the pack.** Rewrite every `key_point` used as a correct option as a full sentence with a full stop, of similar length to its part's `wrong_idea` rows (within 0.7–1.3× the median distractor length; our choice). Do the parts on camera first: `ped_definition`, `ped_formula`, `ped_values`, `tax_incidence_split`. Also give `ped_formula`'s second point ("Keep the minus sign") its own sign-error misconception, so its check stops reusing distractors about the formula. Then re-capture and re-count. | pack (team edit), video | S | yes | our capture count; panel-teacher #2; w1-04-10 ✓ |
| 2 | **Correct `externality_tax_eval_m1`** with the wording below, and drop "always" from its `wrong_idea`. | pack (team edit) | S | yes | economics (below); panel-teacher #3 |
| 3 | **Load the 30 candidate rows as `status=draft`** into the real Edexcel pack's `misconceptions.csv`, with the source ids added to `sources.csv` (examiner reports as type `examiner_report`). Map each placeholder `node_id` to a real part id at load: misconceptions are served per part, so a row on a concept node never reaches an MCQ. Aim for 3 misconceptions per gateway part (`mcq.max_options = 4`). A teacher should sign the rows off before any student sees them (see Panel objections). | pack | S (load) / M (review) | load yes; review partly | w1-04-01 ✓, w1-04-05 ✓, w1-04-06 ~, w1-04-07 ✓, w1-04-08 ✓ |
| 4 | **Rule for writing rows: one wrong option = one misconception**, in the same form and length as a correct point, with no "always"/"never". A wrong option that two different misconceptions could produce can't tell them apart: rewrite or split it. Add the rule to `docs/build/reference/course-pack-format.md` (team edit). | course-pack-format doc | S | yes | w1-04-10 ✓; medical item-writing analogy (speculative) |
| 5 | **Mark gateway parts with what exists, not a new flag.** Add `prerequisite` edges from opportunity cost, marginal analysis and the multiplier (cumulative causation) to the parts that build on them, so `importance.w_dependents` ranks them higher. Set `difficulty = 0.7` (our choice) on those concepts for more checks and reviews. Externalities and welfare are not in Davies & Mangan's table, so give them the edges but not the "threshold" justification. | `edges.csv`, `nodes.csv` | S | yes | w1-04-04 ~; w1-04-03 ✓ |
| 6 | **Add `confusable` edges (`teach_use = contrast`)** for the twin concepts the examiner reports name: contestability↔competitiveness; price discrimination↔product differentiation; XED/YED/PED signs; PES↔PED determinants; economies of scale↔dynamic efficiency; current account↔budget deficit; absolute↔comparative advantage; HDI↔Gini; inflation rate↔price level; budget deficit↔national debt. Each needs a one-line note saying how the pair differs. | `edges.csv` | S | yes | w1-04-08 ✓ (existence only); w1-04-07 ✓; w1-04-11 ✓ |
| 7 | **Demo and pitch moment: our own UK opportunity-cost item.** Example: a free festival ticket against a paid gig you value at more than its price. One key and three distractors, one each for "free means costless", "the price paid" and "the gross value". Pitch line: "only about one in five economists and economics PhD students picked the intended answer, and economists still argue about the key" (see [pitch-notes](pitch-notes.md)). Never present the key as beyond dispute. | demo, pitch | S | yes | w1-04-01 ✓; Potter & Sanders 2012 |
| 8 | **Transfer reviews for gateway parts give an unfamiliar case without naming the concept**, so the student picks the frame. A one-line change to the `review_transfer` cue (team edit). | `text/` cue | S | yes | w1-04-04 ~ (assessment advice matches) |
| 9 | **Treat one misconception pick as weak evidence.** The design already activates a misconception on one pick and clears it on later correct evidence. Keep that, and never escalate from a single pick. Pitch: "we diagnose, then re-check". | pitch, design note | S | yes | w1-04-09 ✓ |
| 10 | **Run the opportunity-cost check even after "I know this"** (`skip_point`), at least as the first review, because prior exposure did not mean understanding. | settings / pack | S | yes | w1-04-02 ✓ |

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
- The `wrong_idea` also uses "always", the absolute word that gives a distractor away (rec 4).

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

Themes 1–3 become rows and `confusable` edges. Theme 4 fits the existing "answer the question set" cue. Themes 5–6 need level-marked answers (step 07, not built), which is the teacher's first objection.

## Later (not before Thursday; for the business plan and Q&A)

- **A content review queue with a measured error rate.** Time a teacher reviewing one part's rows, and count the errors found. This answers "who checks it?" with a number. Ties to step 10 (not built).
- **Graded distractors.** Shanahan et al. scored a "second-best" option as partial credit. A `partial` column could feed a score of 0.5 into knowledge tracing. M effort, code change.
- **Two-tier checks** for gateway parts (an answer, then a reason). Explain-back covers most of this already.
- **A pack validator warning** when a correct option's length falls outside 0.7–1.3× the median distractor length, or when it lacks a full stop and the distractors have one (our choice of thresholds).
- **Server-markable tasks beyond MCQ** (teacher #1): a numeric answer for calculation parts, and an "order the chain of reasoning" task. Whether these improve essay marks is an open question for wave 2.
- **TEL-4 high-school data** (US, closest age match). The PDF fonts blocked text extraction; worth a proper tool.

## Considered and rejected

- **Keying "a higher minimum wage reduces employment" as correct.** The empirical evidence is mixed. Row 20 tests the diagram error instead, framed as "in the competitive model".
- **Stantcheva's "prices rise faster than wages" finding.** It is a perception of one period's data, not a concept error.
- **Sapienza & Zingales expert–public gaps.** These are policy opinions, not concept errors.
- **A new `threshold` column in `nodes.csv`.** There is no measured evidence that flagging a threshold concept improves learning (w1-04-03 ✓). Edges and `difficulty` give the same scheduling effect with no code.
- **Copying TUCE or TEL item stems.** These are secure, copyrighted tests. We paraphrase three published items as misconceptions only.
- **Quoting examiner reports.** Summaries only.

## Panel objections this report answers or leaves open

| Objection (panel) | Status |
|---|---|
| "The correct option gives itself away" (teacher #2, student #3, judges #5) | **Answered for option form** (pasted explain-backs remain open): measured (6 of 6 sets give it away by the full stop) and root cause found (key_points vs wrong_idea). The fix is rec 1, a team edit to the pack. Still needs an owner and a re-capture. |
| "The check on 'Keep the minus sign' uses distractors about other points" (teacher #2) | **Answered** in rec 1: give each point its own misconception. |
| "I'd already red-pen one row" (teacher #3) | **Answered:** we agree, explain why, and give a corrected wording (rec 2). |
| "Who checks the content, and how often is it wrong?" (teacher #3) | **Partly.** Rec 3 keeps every new row a draft until a teacher signs it off. No review queue or measured error rate exists yet. |
| "It teaches recognition, not what the exam rewards" (teacher #1, student #5) | **Partly answered.** Rows target the board's own named errors, and transfer reviews don't name the concept (rec 8). Level-marked answers, chains of analysis and evaluation remain open (step 07). |
| "Distractors come from where?" (judges, teacher praise) | **Answered:** published research on economists and students, UK survey data and examiner reports (rec 3), with populations stated. |

## Findings

| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-04-01 | 21.6% of 199 economists and PhD students chose the intended opportunity-cost answer; wrong options drew 25.1/25.6/27.6% | correlational (survey) | US, ASSA 2005; about a third PhD students; not 16–18 | learning (concept test) | ✓ |
| w1-04-02 | Students with a prior economics course were correct less often (7.4% vs 17.2%, p = 0.008, n = 358) | correlational | US first-year undergraduates | learning | ✓ |
| w1-04-03 | Opportunity-cost score 3.58 → 3.68 of 5 over a semester; level correlates with final grade (r = .45), change does not (r = .01) | correlational | n = 431, first-years, Australia | learning | ✓ |
| w1-04-04 | Davies & Mangan's table: four threshold concepts (opportunity cost, marginality, incentives, cumulative causation); modelling concepts separate; assess with unfamiliar problems | theory (qualitative) | UK first-year undergraduates | learning (qualitative) | ~ secondary source; welfare and interacting markets not in the table |
| w1-04-05 | TUCE-4 distractors persist: 43→32%, 36→28%, 33→29%; mean correct about 31–33% → 43–47% | correlational (norming) | US college, n = 3,255 micro, 2,789 macro | learning | ✓ |
| w1-04-06 | 69% / 77% of first-years believed rent control helps; information reduced but did not remove the belief | RCT (lab) + quasi-experimental (field) | Spain, first-years; lab n = 172 | learning (belief change) | ~ authors' summary only; in the field, refutation beat the no-information control significantly; only in the lab was it not better than a plain text |
| w1-04-07 | 36% of UK adults read a fall in inflation as falling prices; 50% correct; 44% linked GDP to size of economy | correlational (survey) | UK adults, YouGov, Aug 2022 | learning (understanding) | ✓ |
| w1-04-08 | 9EC0 examiner reports 2023–25 exist and name recurring confusions, including contestability vs competition | official document | 9EC0 candidates, England | learning (exam performance) | ✓ existence check; other themes unchecked |
| w1-04-09 | Misconception choice rises then falls with ability; instruction can strengthen it first | correlational (IRT) | n = 1,250, US grades 8–12, astronomy | learning | ✓ |
| w1-04-10 | Eedi diagnostic questions: 4-option maths items with misconception distractors; 20M+ records | practitioner (dataset) | UK school maths (setting not checked) | prediction | ✓ |
| w1-04-11 | Stock-flow tasks: 77% vs 48% average; fewer than half showed the stock rising when inflow > outflow | correlational | graduate students, mostly MIT Sloan | learning | ✓ |
| w1-04-12 | "Good begets good" heuristic in lay macro judgements | correlational | lay adults (country not confirmed) | learning (causal judgement) | ~ abstract only; unemployment–inflation example from secondary summaries |
| (ours) | Example-pack MCQs: correct option has no full stop in 6/6 sets, is shortest in 5/6; mean 34 vs 59 characters | our measurement (captures) | synthetic demo students, example pack | n/a (assessment design) | not verified (our count; reproducible from `sims/demo-captures/`) |
