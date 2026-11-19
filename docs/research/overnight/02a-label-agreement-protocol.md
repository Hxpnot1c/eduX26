# 02a · Label-agreement study: protocol, draft messages and key

Appendix to [02 · Defining and assessing AI literacy](02-ai-literacy-assessment.md). Wave 3 (overnight 18 Nov 2026). Copied from the scout note `work/w3/w3-02e.md` §1, §3 and Appendices A–C, with the blind verifier's corrections from `work/w3/verify-O.json` applied. 02 holds the summary, the recommendation (02 rec 8) and the findings table. This file is the ready-to-run kit.

> **Read this before using anything below.**
> - **The 40 messages (Appendix A) and the intended-label key (Appendix B) were drafted by a Claude model.** The chatbot under test is also Claude, so using them as they stand is circular. 02 rejects "generating agreement-study messages with the model under test".
> - **Before Wednesday, the team rewrites at least 20 of the 40 messages in its own words and a student voice.** If possible, one person also writes 5–10 extra items cold, without seeing the key. Freeze the rewritten set and the key in a git commit before anyone labels.
> - **The key is a coverage target, not gold and not a rater.** It shows which labels each message was meant to exercise, so prevalence is balanced. The reference standard is the adjudicated consensus of two blind humans.
> - **Figures inside the messages are illustrative, not checked facts.** Examples are "CPI 2.8% in February 2025" and "Bank Rate 4.75% in November 2024". No real student data is used.
> - **Not run yet.** Nothing here is a result. Every sample-size and simulation figure is our calculation (w3-02e-01, -02, -06).

**Wave 5 update (§4).** A dry run of the analysis script on a Claude proxy's labels against the key: a **pipeline test, not agreement evidence**. It found definitions to clarify before Wednesday and key errors to fix (§4.3), and a server bug that patch 0008 now guards. Use [`sims/agreement/analyse.py`](sims/agreement/README.md) for the real run; it replaces Appendix C's `agree.py`.

**Verifier corrections applied here (verify-O.json).**
- **AC1 example (w3-02e-04 ~).** At 87.5% prevalence (35 of 40 "yes" per rater) and 90% raw agreement, κ ≈ .54 and AC1 ≈ .87. The scout's κ .28 / AC1 .88 matches a marginal prevalence of 92.5%, not 87.5%.
- **Pass-rule simulation (w3-02e-06 ✓).** A rerun reproduced the **upper** ends of the ranges in §1.6 (independent errors). The **lower** ends depend on how strongly the bot's errors cluster within a message, which our model fixes by assumption. The rerun's clustered case (ICC .2) gave .39 / .72 / .94.
- **STARD 2015 (w3-02e-08 ~).** 30 items and the 85-member STARD Group are confirmed. It was developed in one web-based survey run in two rounds, and "a few" items were added, not "seven new items".
- **Krippendorff thresholds (w3-02e-05 ~).** The .800 / .667 bars come from Krippendorff (2004) through secondary sources. Hayes & Krippendorff (2007) don't state them. Check them before putting them on a slide.
- **Dropped:** the scout's preregistration claim citing a Data Colada post (w3-02e-14 ✗). The verifier found the post doesn't say what was claimed. Committing the protocol, messages, key and script to git before labelling stays as a light, time-stamped preregistration (our choice). It needs no outside citation.

**What the design does, in short** (details in §1.5 and §1.6):
- Headline statistics are pooled within each skill.
  - **Ask:** 4 features × 18 research messages = 72 decisions.
  - **Answer scoring:** 4 Verify ticks × 8 + 3 explain-back points × 8 = 56 decisions from 16 messages.
  - The CI is a cluster bootstrap over messages.
- Verify ticks (32 decisions, 8 messages) also get their own row, so "Verify labels agree" is never read off a pool that is mostly economics points.
- At κ = .7 the pooled CIs are about ±.16–.20 (our simulation, allowing for clustering). A single feature has n ≈ 18, about ±.33, so it is descriptive only.
- The pass rule is weak evidence. It passes a bot with true κ = .6 about 40–50% of the time and one with κ = .7 about 70–89% of the time (w3-02e-06 ✓, simulation; see the correction above). So report the human–human ceiling next to it.

---

## 1. Protocol (Wednesday afternoon, about 2 hours)

### 1.1 Question and design
**Question:** when a chatbot labels a student's message using eduX's real tool description, do its labels agree with careful humans using the same definitions, as well as the humans agree with each other?

**Design** (STARD-style framing, our adaptation):
- **Index test:** the chatbot's tool-call arguments.
- **Reference standard:** the consensus of two blind human labellers after adjudication.
- **Ceiling:** the agreement between the two humans before adjudication.
- **Test–retest:** the chatbot run twice on every item. In software A/B practice this plays the part of an A/A test, checking the measuring instrument before trusting a difference (analogy).

**Roles (4 people):**
- **A, author/runner:** edits the messages, holds the key, runs chatbot pass 1. Does not label.
- **B and C, labellers:** label blind, in separate rooms or sheets. They never see the key or the bot's output.
- **D, runner and adjudicator:** runs chatbot pass 2, then chairs the B/C adjudication and records the reasons.

### 1.2 What gets labelled (and what doesn't)

| Label | Applies to | Type | Source of definition |
|---|---|---|---|
| `request_type` | all 40 | nominal, 4 categories | 05e `ThisMessage.request_type` |
| `question_depth` | all 40 | ordinal, 3 levels | `ThisMessage.question_depth` |
| `engagement` | all 40 | ordinal, 3 levels | `ThisMessage.engagement` |
| `question_features` (concept, context, asks_sources, asks_reasoning) | R01–R18 | 4 binary decisions each | `ThisMessage.question_features` |
| `asks_recent` | R01–R18 | binary | `ThisMessage.asks_recent` (secondary) |
| Verify ticks a–d (`points_met` for `ail_verify`) | V01–V08 | 4 binary decisions each | `mark_points.csv` ail_verify_p1–p4 |
| `source_conflict` | V01–V08 | binary | `ThisMessage.source_conflict` (descriptive only; 2 positives) |
| explain-back points a–c (`points_met`) | E01–E08 | 3 binary decisions each | score_next given in the item's context |
| `misconception_ids` | E01–E08 | binary per candidate id (closed list) | `example-mini/misconceptions.csv` |
| `choice` | all 40 | nominal | descriptive only (1–2 positives) |

**Dropped, with reasons:**
- `conflict_flagged` and `pushback_changed` describe the chatbot's own reply, not the student's message, so a human can't label them from the message.
- `web_access` is a capability of the chat, not a property of the message.
- Verify tick a ("opens the source") can't be observed. It is defined here as **"the student says they opened it"** ([02](02-ai-literacy-assessment.md) notes this threat).

**Rater instructions = the real tool text, verbatim.** Give B and C a two-page codebook made of:
- the `Field(description=…)` strings for `ThisMessage` and `Answer` from the **05e branch** `edux/server.py` (main lacks `question_features`);
- `text/tools/tutor_turn.md`;
- rules 3–4 of `text/server_instructions.md`.

Add nothing else. If humans need more explanation than the chatbot gets, that is a finding about the tool text.

### 1.3 How the chatbot labels (use the real tool description)
- **Option 1 (preferred if anyone has API access): a 40-line harness.**
  - Export the 05e branch tool list from the MCP server (`tools/list`) and pass it as the tool definitions.
  - Use `text/server_instructions.md` as the system text.
  - Force the `tutor_turn` tool and record its `input` JSON.
  - For V and E items, insert one prior assistant turn (the question in the item's context) and a prior tool result containing that item's `score_next`, so the bot has what it would have live.
  - **Use real prior tool results as templates.** Wednesday morning, call the 05e `tutor_turn` locally with a fresh temp `EDUX_DATA_DIR` until it returns (i) a Verify task plan and (ii) an explain-back plan. Save both JSON results, then edit only the claim/question text and the score_next points per item.
  - The bot must send `answer.part_id` and `answer.type`: `ail_verify` with type `ail_task` for V items, and the item's part (e.g. `ped_definition`) with type `explain_back` for E items. It can only know these from that prior result, which is why the templates matter.
  - Record the model id.
- **Option 2: claude.ai with the eduX connector on a throwaway student key, against a fresh `EDUX_DATA_DIR`.**
  - Start a **new chat per message**. Read the `tutor_turn` arguments from the tool-call panel, or from the call log in the temp data dir.
  - For V and E items, paste the context line first, as the "previous turn". This is less faithful than option 1, so say so in the results.
  - **Record the first `tutor_turn` call's arguments only.** With no outstanding question, the server can return `{"ok": false}`. The server instructions then tell the bot to fix the field and call again, which changes its labels. The E-item points (a–c) are also not in `example-mini/mark_points.csv`, so the server will reject them. Count each rejection in the flow table, and score the first call.
- **Timing rule.** Time the three practice items first. If one item takes the runner more than about 1.5 minutes, cut pass 2 to a random 12 items and report test–retest on that subset only.
- Either way:
  - run every item **twice** (A does pass 1, D does pass 2, in parallel);
  - record `client`;
  - count every item where the bot didn't call the tool or returned an invalid label. Report those (STARD "flow"); never silently drop them.

### 1.4 Statistic per label type

| Label type | Primary statistic | Also report | Why |
|---|---|---|---|
| Binary, pooled within a skill (Ask features; Verify ticks + explain-back points) | Cohen's κ, chatbot vs consensus; 95% CI by **cluster bootstrap over messages** (2,000 resamples) | raw % agreement; Gwet's AC1; sensitivity and specificity vs consensus; κ for B vs C (ceiling) and bot1 vs bot2 (retest) | Decisions within a message are correlated, so the bootstrap resamples whole messages. AC1 guards against the prevalence paradox: at 87.5% prevalence and 90% raw agreement, κ ≈ .54 while AC1 ≈ .87 (w3-02e-04 ~, our corrected example). |
| Three raters together (B, C, bot) | Fleiss' κ or Krippendorff's α (nominal) | — | One number for "do all three agree" |
| Ordinal (question_depth, engagement) | quadratic-weighted κ, or Krippendorff's α (ordinal) | confusion matrix | Off by one level is less bad than off by two |
| Nominal, more than 2 categories (request_type) | Cohen's κ | confusion matrix | — |
| Rare binary (source_conflict, choice, asks_recent) | raw counts and % agreement only | AC1 | κ is unstable with 1–3 positives in 40 |
| What the server computes | Ask score (features ÷ 4) per message: weighted κ on the 0–4 count, and agreement on "≥ `ask_min_features`"; Verify tick count per answer | — | This is the decision that actually drives the learner model |

### 1.5 Sample size: the maths
Large-sample standard error of κ for two raters on a binary label (Cohen's 1960 approximation; Fleiss, Cohen & Everitt 1969 later gave the exact large-sample variance, which is a little different):

  SE(κ) ≈ √[ p_o (1 − p_o) / ( n (1 − p_e)² ) ]

Here p_e = π² + (1 − π)² for prevalence π (equal marginals), and p_o = κ(1 − p_e) + p_e. Solving for the n that gives half-width w:

  n = 1.96² · p_o (1 − p_o) / ( (1 − p_e)² · w² )

**95% half-width (±) by n (our calculation):**

| prevalence π | κ | n = 20 | 40 | 60 | 80 | 100 | 200 |
|---|---|---|---|---|---|---|---|
| 0.5 | .6 | .35 | .25 | .20 | .18 | .16 | .11 |
| 0.5 | .7 | .31 | .22 | .18 | .16 | .14 | .10 |
| 0.5 | .8 | .26 | .19 | .15 | .13 | .12 | .08 |
| 0.3 | .7 | .35 | .25 | .20 | .17 | .16 | .11 |
| 0.15 | .7 | .46 | .32 | .26 | .23 | .20 | .14 |

**n needed for a given half-width (κ = .7):** ±.25 needs 32 (π .5) or 39 (π .3); ±.20 needs 49 or 60; ±.15 needs 88 or 107; ±.10 needs 196 or 240.

**Testing against "only fair" agreement** (Donner & Eliasziw goodness-of-fit formula, equal marginals; we reconstructed it ourselves from its description and did not check it against Sim & Wright's printed table, which is paywalled):

  n = (z₁₋α/₂ + z₁₋β)² / Σᵢ [ (Pᵢ(κ₁) − Pᵢ(κ₀))² / Pᵢ(κ₀) ]

The cells are P₁ = π² + π(1−π)κ, P₂ = 2π(1−π)(1−κ), P₃ = (1−π)² + π(1−π)κ.

| κ₀ (null) | κ₁ (true) | π = .5 | π = .3 | π = .15 |
|---|---|---|---|---|
| .4 | .8 | 42 | 48 | 74 |
| .4 | .7 | 74 | 85 | 131 |
| .5 | .8 | 66 | 77 | 122 |
| .6 | .8 | 126 | 149 | 239 |
| .6 | .9 | 56 | 66 | 107 |

(Power .80, two-sided α .05. One-sided needs about 20% fewer: 33 for .4 vs .8.) A Monte Carlo check (4,000 replicates, χ² goodness-of-fit test with π estimated) gives power .88 at n = 41 for .4 vs .8, and .92 at n = 90 for .4 vs .7. So the formula is about right, if a little conservative.

**What that means for our 40 messages (our design):**

| Skill / label | Decisions | Messages | Expected ±95% at κ = .7 | Use |
|---|---|---|---|---|
| Ask: 4 question features, pooled | 72 | 18 | ±.16 independent; about ±.18 with clustered bot errors (cluster-bootstrap simulation, our calculation) | **headline** |
| Answer scoring: Verify ticks + explain-back points, pooled | 56 | 16 | about ±.18 independent; about ±.20 clustered (same simulation) | **headline** |
| Verify ticks alone | 32 | 8 | about ±.25–.30 | own row, descriptive |
| question_depth, engagement, request_type | 40 | 40 | about ±.22 | secondary |
| a single feature (e.g. asks_sources) | 18 | 18 | about ±.33 | descriptive only |
| misconception ids (closed list) | 12 | 8 | too few | descriptive only |

To reach ±.15 per skill, the study would need about 25 research messages and about 25 answer messages, with 2 hours of labelling each. That is a pilot-term job, not a Wednesday job.

### 1.6 Pass/fail thresholds (our choice, with reasons)
For each headline skill (Ask; answer scoring):
1. **Ceiling check first.** If B vs C κ < .60, the label **definition** fails. Rewrite the tool text and don't report the bot's κ as a bot result.
2. **Pass:** bot vs consensus κ ≥ .60 **and** its 95% cluster-bootstrap lower bound ≥ .40, **and** the mean of bot–B and bot–C κ is no more than .10 below B–C κ. Compare like with like here: the consensus is built from B and C, so bot–consensus is biased upwards against B–C. Use bot–consensus for κ, sensitivity and specificity, and bot–B/bot–C for the ceiling test.
3. **Strong:** κ ≥ .80. Krippendorff's customary bar for α (≥ .800) is the same order of strictness; .667 is his floor for tentative conclusions (secondary source).
4. **Fail:** anything else. We say so on Thursday and fix the description.
5. **Specificity guard (eduX-specific):** report bot specificity vs consensus. Over-ticking inflates Ask and Verify levels (false secure), so bot specificity below .80 is flagged even if κ passes.

**Why .60 / .40.** .60 is where the Landis & Koch (1977) bands move from "moderate" to "substantial". They called their bands arbitrary, so this is a convention, not evidence. The lower bound of .40 rules out "fair or worse" agreement.

**What the rule does** (simulation, our calculation; prevalence .5; cluster-bootstrap lower bound; 600 replicates per cell; the range runs from independent errors to errors that cluster within messages):

| Design | true κ .6 | .7 | .8 | mean full CI width at κ .7 |
|---|---|---|---|---|
| Ask, 72 decisions / 18 messages | passes 38–50% | 80–89% | 98–99% | .31–.36 |
| Answers, 56 decisions / 16 messages | 37–47% | 71–81% | 93–98% | .35–.40 |
| (for reference) 40 independent items, Wald bound | 40% | 74% | 95% | .44 |

So a pass is weak evidence of κ ≥ .6, and a fail doesn't separate .6 from .7.

**Verifier note (w3-02e-06 ✓).** An independent rerun (2,000 replicates, 1,000 cluster-bootstrap resamples) reproduced the upper end of each Ask range with independent errors: .47–.48, .86–.88 and .99. With within-message error correlation (rater vs gold, ICC .2) it gave .39, .72 and .94. So the lower ends depend on the clustering model we assumed. For 40 independent items it gave .40–.44, .71–.75 and .94–.96, depending on the model.

### 1.7 Running order (Wednesday, 2 hours)

| Time | Who | What |
|---|---|---|
| before 14:00 | A | Rewrite at least 20 of the 40 messages in a student voice. Write 5–10 extra cold items if possible. Fill the key. **Commit the messages, the key (as a separate file B/C won't open) and this protocol.** The commit hash is the preregistration. |
| 14:00–14:10 | all | B and C read the codebook (tool text only). Calibrate on the 3 practice items (Appendix A, P1–P3), not part of the 40. Discuss the practice items only. A and D run the bot on P1–P3 and time it (timing rule, §1.3). |
| 14:10–14:55 | B, C | Label all 40 independently, about 1 min per item, in the results sheet (one row per decision, §1.8). |
| 14:10–14:55 | A, D | Chatbot pass 1 (A) and pass 2 (D), fresh chat or harness call per item. Record the raw JSON. |
| 14:55–15:10 | A | Paste everything into `decisions.csv`. Run `agree.py` (Appendix C) for B–C. |
| 15:10–15:35 | B, C, D | Adjudicate **only** the B–C disagreements, without seeing the bot's labels. D records the reason for each (e.g. "tick c vs d unclear"). This produces `consensus`. |
| 15:35–15:45 | A | Rerun `agree.py`: bot vs consensus, bot1 vs bot2. Build the 2×2 tables. |
| 15:45–16:00 | all | Fill the results template. Pick the Thursday claim (§3) that matches. List the definition fixes. |

### 1.8 Results template

**Data layout (`decisions.csv`):** `msg_id,label,unit,rater,value`. For example:
- `R07,ask_feature,context,B,1`
- `V02,answer_point,d,bot1,0`
- `E03,misconception,ped_formula_m2,consensus,1`
- `R01,depth,-,C,mechanism`

**Table 1. Flow (STARD-style).** Items planned 40 | items labelled by B / C | bot calls returning valid labels, pass 1 / pass 2 | items excluded (with reason).

**Table 2. Headline agreement.**

| Skill | Decisions (messages) | Prevalence (consensus) | B–C κ [95% CI] | bot–consensus κ [95% CI] | bot % agree | bot AC1 | bot sensitivity | bot specificity | bot1–bot2 κ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Ask features (pooled) | 72 (18) | | | | | | | | | |
| Answer scoring (pooled) | 56 (16) | | | | | | | | | |
| of which Verify ticks (descriptive) | 32 (8) | | | | | | | | | — |

Also add a column for the mean of bot–B and bot–C κ (the ceiling test, §1.6).

**Table 3. Secondary labels.**

| Label | n | B–C (wκ or κ) | bot–consensus | bot1–bot2 | Notes |
|---|---|---|---|---|---|
| question_depth | 40 | | | | |
| engagement | 40 | | | | |
| request_type | 40 | | | | |

**Table 4. Descriptive.** Per feature (concept, context, asks_sources, asks_reasoning), per Verify tick (a–d), per explain-back point, misconceptions, source_conflict, asks_recent, choice: counts of agree/disagree for bot vs consensus.

**Table 5. Server-level outcome.** Ask score (0–4) per message: weighted κ, bot vs consensus; % of messages where bot and consensus fall on the same side of `ask_min_features`. Verify tick count per answer: same.

**Table 6. Adjudication log.** Item, label, B, C, consensus, reason. This list is the to-do list for the tool description.

**Table 7. Where the key disagreed with the consensus.** These are messages that didn't say what we meant them to say. Fix the message, not the score.

## 3. What can honestly be claimed on Thursday

**Always include:** n per skill, κ with its 95% CI, the human–human κ, and the four limits: **synthetic messages, written by the team (drafted with AI help), one chatbot, not a validation.**

- **If both skills pass (pre-written):** "On 40 synthetic A-level Economics messages, Claude's labels agreed with two blind human labellers about as well as the humans agreed with each other. Question features: κ = __ (95% CI __–__; 72 decisions). Answer marking: κ = __ (__–__; 56 decisions). Humans with each other: κ = __ / __. This is a first check of one chatbot, not a validation. The pilot repeats it on real messages."
- **If one fails:** "Labels for research questions agreed well (κ = __, CI __–__). Labels for checking claims didn't (κ = __). The humans split on the same ticks, so we are rewriting that definition, and we'll recheck."
- **If the humans disagree (ceiling fails):** "Our own team disagreed on __ (κ = __), so the definition is the problem, not the chatbot. That's exactly what this check is for."
- **Never say:**
  - "validated";
  - "the chatbot labels accurately" without the n and the CI;
  - any per-feature κ as a headline (n ≈ 18, about ±.33);
  - anything about real students;
  - anything about ChatGPT or Copilot if only Claude was run;
  - "κ = .8 proves reliable assessment" (agreement on labels is one link in the scoring inference, not reliability of the literacy level, which still needs about 12 moments per skill; [02](02-ai-literacy-assessment.md)).
- **Video/pitch shape:** one bar pair per skill (B–C vs bot–consensus, with CI whiskers), captioned "40 synthetic messages · 2 human labellers · Claude · 18 Nov 2026".

## 4. Wave 5: dry run, definitions to clarify, key fixes, and how to run `analyse.py`

Sources: `work/w5/w5-02r-labels.md` (proxy labels), `work/w5/w5-02s.md` (dry run and audit), `work/w5/w5-fix-labels.md` (patch 0007), and verifier S (`work/w5/verify-S.json`).

> **Not agreement evidence.** The key was drafted by a Claude model, the proxy labeller is a Claude model, and a Claude model classified the disagreements. Two Claude models agreeing says nothing about humans or about the chatbot's labels in use. Shared blind spots are invisible: "no disagreement" on a label does not mean its definition is clear. Never quote these numbers as a result, a κ for the bot, or a pass.

### 4.1 What the dry run showed (a pipeline test)
- **The script runs end to end** on data in the real format (w5-02s-01 ~). It handled consensus filled from B where B = C, blank bot cells counted as missing (not 0), a bot that calls an R item `concept` (its features scored 0, as the server records), a typo (stops with the line and value), and every verdict branch except "pass". Quadratic-weighted κ matches scikit-learn; Krippendorff's α reproduces textbook values. AC1 is not checked against an outside implementation, and Fleiss' κ is not implemented.
- **Dry-run numbers, for the pipeline only:** pooled Ask features 72 decisions, answer scoring 56. Do not report them.
- **33 disagreements between proxy and key: 29 genuinely ambiguous definitions, 2 proxy errors, 2 key errors** (w5-02s-03 ~; classified by a Claude model). None was a plain misreading of a message: nearly all trace to definitions.
- **Biggest single cause: `request_type` on answers.** All eight V items disagreed (key `research`, proxy `concept`), and the tool text gave no rule. On the server it is not cosmetic: a Verify answer labelled `research` records **Ask 0/4** and routes the turn to the research plan (w5-02s-02 ✓; confirmed in code and in probes). Patch 0007 now tells the chatbot the rule, and patch 0008 guards the server ([build list](wednesday-build-list.md) step 5c).
- **Engagement was the proxy's blind spot.** It produced 9 disagreements, 7 of them on labels the proxy marked "sure". Unsure flags are useful triage, not complete: 11 of 33 disagreements came on "sure" labels.

### 4.2 Definitions to clarify (now mostly in patch 0007)
Raters and the chatbot must read the same text (§1.2: "add nothing else"). Patch 0007 appends these rules to `text/tools/tutor_turn.md`; give raters the same wording.

| # | label | rule (our wording) | in 0007? |
|---|---|---|---|
| 1 | `request_type` on answers | An answer is never `research`. A course answer or "ok, go on" is `concept`. An answer to a source-checking task or how-AI-works question is `other`, and so is off-course chat | yes |
| 2 | `request_type`: concept vs research | research needs facts or figures about a particular place and time, or asks for sources. A how-or-why question about a course idea is concept, even if it names a real country or currency | yes |
| 3 | `source_conflict` | True when the source wouldn't open, or doesn't say what the chatbot said: the claim is missing, or the figure, date or period differs. Rounding is not a conflict. **Option A, our choice; the team confirms** | yes |
| 4 | `points_met` and Verify ticks | Tick a point only if the message contains all of it, in any words. Verify: a for "opened it" or "wouldn't load"; d for a verdict. With 0009b, also: never tick what only repeats the chatbot's reply, a point it just showed, or its citation | yes (0009b adds the last sentence) |
| 5 | `question_features: concept` | Needs an economics term or an official statistic. The price of an everyday thing (petrol, rents, food banks) doesn't count on its own | yes |
| 6 | `engagement` | passive: no question and no answer. active: asks, or answers by recalling or restating. constructive: adds a step of their own (a reason, an inference, a comparison with a conclusion, an application). Being wrong doesn't change the level | yes |
| 7 | `question_depth` on non-questions | Defined only for questions, yet required on every message. Text option: surface for a non-question, unless it explains a cause or applies the idea. Better (code, later): make it optional for answers | no |
| 8 | `choice` / `homework` | Set `just_show_me` also when the student asks to be given the answer; `homework` when they ask for work they will hand in | no |
| 9 | `asks_reasoning`, `context`, `asks_recent` | No disagreements, but both labellers were Claude. Watch these in the B–C adjudication | no |

### 4.3 Key errors to fix (before anyone labels)
Don't edit Appendix B in place unless you then rerun `analyse.py --dryrun`: the script parses Appendix B and its `KEY_NOTE_FLAGS` map. Apply these to the frozen key in the study commit.

| item(s) | label | now | change to | why |
|---|---|---|---|---|
| V01–V08 | `request_type` | research | **other** | `research` scores Ask 0/4; `concept` pulls the course focus (verifier S); 0007 says `other` |
| V01, V08 | `source_conflict` | 0 | **1** | Under Option A a different figure is a conflict (2.8% vs 3.0%; 2.2% vs 2.0%) |
| V04 | `source_conflict` | — | decide | "highest since the late 1940s" vs "since WW2" |
| V08 | tick a (rater rule) | raters told "says they opened it" | **give raters 0007's `points_met` wording, word for word** | The chatbot never saw the "says they opened it" rule, so bot and humans had different instructions |
| O04, O06 | engagement | active | active (keep); the proxy's "passive" was its error | asking for something isn't "just reading" |
| E01 | engagement | constructive | active | pure recall (rule 6) |
| V items with "so…" (V01, V02, V04, V07, V08) | engagement | active | constructive | an inference is their own step (rule 6). E04 stays constructive: a wrong reason is still a reason |
| R03, R05, R10, R12, R16 | `concept` feature | as keyed | check against rule 5 | "petrol prices", "rents", "food banks" alone don't count |
| R09 | `request_type` | research | concept, or rewrite it to ask for data with a place and time | it is course theory as written |
| O04 | `choice` | none | `just_show_me` (our suggestion) | "just write my 25 marker" is a show-me request |
| E08 | point c | 1 | decide: does c need both halves? | the student gave only the inferior-good half |

Also decide before labelling: if a bot calls an R item `concept`, its four features score **0** (what the server records). The script does this and says how many it scored.

### 4.4 How to run `analyse.py` on Wednesday
Full instructions: [`sims/agreement/README.md`](sims/agreement/README.md). Stdlib Python, about 1 s.
1. Collect `decisions.csv`: one row per decision, `msg_id,label,unit,rater,value`. Raters `B`, `C`, `consensus`, `bot1`, `bot2`. **Leave blanks for missing values, never 0.** Enter consensus rows only for adjudicated B–C disagreements; the script fills consensus = B elsewhere.
2. After the B and C labels, and again after adjudication:
   ```bash
   python3 docs/research/overnight/sims/agreement/analyse.py decisions.csv > results.md
   ```
   Options: `--pairs B-C,bot1-consensus`, `--ask-min 2,3`, `--reps 2000`.
3. Read the flow table first (a **!** marks a count below the expected n), then the verdict, then Table 5 (the server-level Ask score and Verify tick count).
4. If the messages are rewritten, update Appendix A/B and `KEY_NOTE_FLAGS` before any `--dryrun`. The real run needs only `decisions.csv`.
5. Report with the §3 templates. The script prints a warning if the only raters are `key` and `proxy`.

### 4.5 Findings (home report for the wave-5 label findings)

| id | claim | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w5-02s-01 | The agreement script runs end to end on real-format data (missing values, consensus fill, features-0 rule, verdict branches) | simulation (pipeline test) | Claude proxy vs Claude-written key; 40 synthetic messages | system reliability | ~ not re-run by a verifier; Claude vs Claude, not agreement evidence |
| w5-02s-02 | Labelling a Verify answer `research` makes the server record Ask 0/4 and route to the research plan | code reading + probe | 05e branch | prediction (validity) | ✓ confirmed in code and by verifier S |
| w5-02s-03 | Of 33 proxy–key disagreements, 29 were ambiguous definitions, 2 proxy errors, 2 key errors | simulation (audit) | as w5-02s-01 | prediction (label clarity) | ~ classified by a Claude model; not verified |

## Appendix A. The 40 draft messages (CSV-ready; show to raters)

**Read first.**
- Written for this study (illustrative numbers, not checked facts; no real student data).
- **Drafted by a Claude model.** Rewrite at least 20 in a student voice before Wednesday, and add cold items if possible.
- The context column is what the student was answering. For V and E items, show it to all raters and to the bot (as the previous turn). E items: the part is the misconception ids' prefix (e.g. `ped_definition`) and the answer type is `explain_back`.
- Verify score_next for every V item:
  - a) Opens the source the claim came from (rate as: says they opened it).
  - b) Names who published the source and when.
  - c) Compares the claim with what the source says.
  - d) Says whether the claim matched the source.

```csv
msg_id,block,context,message
P1,practice,,"why did house prices in the UK fall in 2023? where are you getting that from"
P2,practice,"Chatbot asked: In your own words, what is a subsidy? score_next: a) a payment from government to producers b) lowers their costs so supply shifts right c) price falls by less than the subsidy. Misconceptions: none listed","its money from the government to firms so they can produce more and it gets cheaper"
P3,practice,"Chatbot claimed UK GDP grew 0.1% in a quarter and asked the student to check it (Verify task)","I looked it up and it's right"
R01,research,,"what happened to uk inflation between 2021 and 2023 and why did energy prices push it up so much? can you link the ONS data"
R02,research,,"how much is the minimum wage"
R03,research,,"whats the number for that thing on the news about prices going up"
R04,research,,"what happened in Britain in September 2022"
R05,research,,"find me a reliable source on whats happening with food banks"
R06,research,,"why do things cost so much more now than when i was little"
R07,research,,"what was the UK unemployment rate in 2019"
R08,research,,"where can i find official figures on the current account deficit"
R09,research,,"why did the depreciation of the pound make imports dearer? i think its because you need more pounds to buy the same dollars, is that right"
R10,research,,"can you link me something reliable on what happened to petrol prices in the UK in 2022"
R11,research,,"why did prices in Argentina go so crazy in 2023"
R12,research,,"explain why rents are so high and give me sources"
R13,research,,"what was the Bank of England base rate at the end of 2023? please cite the BoE page"
R14,research,,"how did the energy price cap in 2022 affect UK inflation and why"
R15,research,,"explain how a sugar tax changes what consumers buy, and is there actual evidence it works? link the studies"
R16,research,,"why did prices in the US rise so fast in 2021-22, and where is your data from"
R17,research,,"In the UK in 2024, why did real wages start rising again? I'd like the ONS series you're using so I can check it."
R18,research,,"whats the latest CPI figure for the UK this month, whats driving it, and link the ONS release"
V01,verify,"Chatbot claimed UK CPI inflation was 3.0% in February 2025 (ONS) and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","opened the ONS link, its the ONS CPI bulletin from 19 March 2025. it says 2.8% for February not 3.0%, so you were wrong"
V02,verify,"Chatbot claimed Bank Rate was cut to 4.75% in November 2024 and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","Opened the BoE page, Bank of England, 7 November 2024. It says Bank Rate went to 4.75%; you said 4.75%."
V03,verify,"Chatbot claimed UK youth unemployment rose in 2024 and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","yeah I clicked it and it matches"
V04,verify,"Chatbot claimed the UK tax burden is the highest since the Second World War and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","its from the IFS, a 2023 report. they say the highest since the late 1940s and you said since WW2"
V05,verify,"Chatbot claimed UK unemployment was 4.4% and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","you said unemployment was 4.4% so thats the answer"
V06,verify,"Chatbot claimed real wages grew 2% in 2024 (ONS link given) and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","the link you gave just goes to a page not found"
V07,verify,"Chatbot claimed UK youth unemployment was 15% in 2024 (ONS) and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","opened it, its an ONS article from June 2024 but it doesnt say anything about youth unemployment being 15%, its about the overall rate. so I cant confirm it"
V08,verify,"Chatbot claimed UK GDP growth was 2.0% in a year and asked the student to check it. score_next: a) Opens the source the claim came from b) Names who published the source and when c) Compares the claim with what the source says d) Says whether the claim matched the source. Part ail_verify, answer type ail_task","the page says 2.2% not 2.0% so it was a bit off"
E01,explain,"Chatbot asked: In your own words, what does PED measure? score_next: a) how much quantity demanded responds b) to a change in the good's own price c) in percentage (proportional) terms. Misconceptions: ped_definition_m1 = PED is the slope of the demand curve; ped_definition_m2 = PED measures how price changes when demand changes","its how much quantity demanded changes when the price changes, in percentage terms"
E02,explain,"Chatbot asked: In your own words, what does PED measure? score_next: a) how much quantity demanded responds b) to a change in the good's own price c) in percentage (proportional) terms. Misconceptions: ped_definition_m1 = PED is the slope of the demand curve; ped_definition_m2 = PED measures how price changes when demand changes","it's basically how steep the demand curve is"
E03,explain,"Chatbot asked: How do you calculate PED? score_next: a) % change in quantity demanded on top b) divided by % change in price c) percentage changes worked out from the original values. Misconceptions: ped_formula_m1 = divide change in price by change in quantity; ped_formula_m2 = work out the percentage changes from the new values; ped_formula_m3 = no percentages, just the changes","% change in Qd divided by % change in price, and you use the new price to work out the percentage"
E04,explain,"Chatbot asked: What does it mean if a good's PED is -0.4? score_next: a) demand is price inelastic b) because the value ignoring the sign is less than 1 c) quantity changes proportionally less than price. Misconceptions: ped_values_m1 = an elastic good has a PED below 1","it's elastic because it's below 1"
E05,explain,"Chatbot asked: Who pays an indirect tax? score_next: a) it is split between consumers and producers b) the split depends on PED and PES c) the more inelastic side bears more. Misconceptions: tax_incidence_split_m1 = producers pay all of it because they hand it to the government","consumers pay some through higher prices and firms pay the rest, depends on elasticity"
E06,explain,"Chatbot asked: What happens on the diagram when a specific tax is added? score_next: a) supply shifts left/up b) the vertical shift equals the tax per unit c) price rises and quantity falls. Misconceptions: tax_supply_shift_m1 = an indirect tax shifts the demand curve","demand shifts left because people buy less when its taxed, so price goes up and quantity goes down"
E07,explain,"Chatbot asked: Evaluate using a tax to deal with pollution. score_next: a) it cuts output towards the socially optimal level b) the external cost is hard to value in money c) it only fully corrects if the tax equals the marginal external cost. Misconceptions: externality_tax_eval_m1 = a tax always removes the externality completely","it moves output closer to the socially optimal level but the government cant really measure the cost of pollution in £ so it might set it wrong"
E08,explain,"Chatbot asked: What is income elasticity of demand? score_next: a) responsiveness of demand to a change in income b) other things, including the good's price, held constant c) positive for normal goods, negative for inferior goods. Misconceptions: yed_definition_m1 = YED uses the change in price","how demand responds when price changes, and if its negative its an inferior good"
O01,other,,"whats a merit good"
O02,other,,"why doesnt a subsidy lower the price by the full amount of the subsidy?"
O03,other,,"so if a sugar tax works because demand is a bit elastic, wouldnt a cigarette tax barely cut smoking since smokers are addicted?"
O04,other,,"can you just write my 25 marker on whether the minimum wage should go up, its due tomorrow"
O05,other,,"ok that makes sense"
O06,other,,"I already know PED, can we skip to the next bit"
```

## Appendix B. Intended-label key (DO NOT SHOW TO RATERS; a coverage target, not gold)

**Abbreviations:**
- Features: C = concept, X = context, S = asks_sources, R = asks_reasoning.
- Verify ticks: a–d as above.
- `*` = deliberately borderline (expect disagreement; useful for finding definition problems).

**Design check (prevalence, by construction):**
- Each Ask feature: 10/18. Total 40/72 = 56%. Feature counts per message: 0:1, 1:4, 2:6, 3:4, 4:3.
- Verify ticks: a 5/8, b 4/8, c 5/8, d 4/8. Total 18/32 = 56%.
- Explain-back points: 11/24 = 46%.
- Misconception decisions: 5/12.
- source_conflict: 2/40.
- question_depth: surface 24, mechanism 15, transfer 1. Transfer is rare, so treat ordinal κ for depth as secondary, and consider rewriting 2–3 items as transfer questions.

```csv
msg_id,request_type,question_depth,engagement,choice,features,asks_recent,source_conflict,points_met,misconception_ids,notes
R01,research,mechanism,active,none,C;X;S;R,no,no,,,
R02,research,surface,active,none,C,yes*,no,,,"current value = recent?"
R03,research,surface,active,none,,yes,no,,,"*concept not named (prices going up)"
R04,research,surface,active,none,X,no,no,,,
R05,research,surface,active,none,S,yes,no,,,
R06,research,mechanism,active,none,R,yes,no,,,
R07,research,surface,active,none,C;X,no,no,,,
R08,research,surface,active,none,C;S,no,no,,,
R09,research,mechanism,constructive,none,C;R,no,no,,,"student offers own reasoning"
R10,research,surface,active,none,X;S,no,no,,,"*petrol prices = concept?"
R11,research,mechanism,active,none,X;R,no,no,,,
R12,research,mechanism,active,none,S;R,yes,no,,,
R13,research,surface,active,none,C;X;S,no,no,,,
R14,research,mechanism,active,none,C;X;R,no,no,,,
R15,research,mechanism,active,none,C;S;R,no,no,,,
R16,research,mechanism,active,none,X;S;R,no,no,,,"*prices rising = inflation named?"
R17,research,mechanism,active,none,C;X;S;R,no,no,,,
R18,research,mechanism,active,none,C;X;S;R,yes,no,,,
V01,research*,surface,active,none,,,no,a;b;c;d,,
V02,research*,surface,active,none,,,no,a;b;c,,"*c vs d: no explicit verdict"
V03,research*,surface,active,none,,,no,a;d,,
V04,research*,surface,active,none,,,no,b;c,,"*a not stated"
V05,research*,surface,passive,none,,,no,,,"restating trap: 0 ticks"
V06,research*,surface,active,none,,,yes,a,,"*tried to open = a?"
V07,research*,surface,active,none,,,yes,a;b;c;d,,
V08,research*,surface,active,none,,,no,c;d,,
E01,concept,surface,constructive,none,,,no,a;b;c,,
E02,concept,surface,active*,none,,,no,,ped_definition_m1,
E03,concept,mechanism,constructive,none,,,no,a;b,ped_formula_m2,
E04,concept,surface,constructive,none,,,no,,ped_values_m1,
E05,concept,mechanism,constructive,none,,,no,a;b,,
E06,concept,mechanism,constructive,none,,,no,c,tax_supply_shift_m1,"*c stated but reasoning wrong"
E07,concept,mechanism,constructive,none,,,no,a;b,,"*c implied by 'might set it wrong'?"
E08,concept,surface,constructive,none,,,no,c,yed_definition_m1,
O01,concept,surface,active,none,,,no,,,
O02,concept,mechanism,active,none,,,no,,,
O03,concept,transfer,constructive,none,,,no,,,
O04,homework,surface,active,none*,,,no,,,"*just_show_me?"
O05,other,surface,passive,none,,,no,,,
O06,concept,surface,active,skip_point,,,no,,,
```

`research*` on the V items marks a known gap in the tool text: it doesn't say what `request_type` an answer to a Verify task should be. Expect disagreement, and treat it as a definition fix rather than a bot error.

## Appendix C. Scripts (our code; stdlib Python)

> **Superseded by [`sims/agreement/analyse.py`](sims/agreement/README.md)** (wave 5), which adds the missing-value, consensus-fill and features-0 rules, value checks, the flow table, sensitivity and specificity, the verdict and Table 5. Kept for reference.

**`agree.py`** (full source; tested on fake data, for example ask_feature bot1–consensus: 72 decisions / 18 messages, κ .72 [.58, .86]). Copy it into a file and run `python agree.py decisions.csv`. For each label and rater pair it prints n decisions, n messages, % agreement, κ (quadratic-weighted for `depth` and `engagement`), a 95% CI by cluster bootstrap over messages (2,000 resamples) and AC1. Sensitivity and specificity: count by hand from the bot1-vs-consensus rows (four cells).

```python
"""Label-agreement stats for the eduX Wednesday study. Stdlib only.
Input: decisions.csv with columns msg_id,label,unit,rater,value
  label: e.g. ask_feature, answer_point, misconception, request_type, depth, engagement
  unit:  the decision within a message (e.g. 'asks_sources', 'p2'); use '-' for one-per-message labels
  rater: B, C, consensus, bot1, bot2      value: 0/1, or a category
Usage: python agree.py decisions.csv
"""
import csv, random, sys
from collections import defaultdict

ORD = {"depth": ["surface", "mechanism", "transfer"], "engagement": ["passive", "active", "constructive"]}

def kappa(a, b, weights=None):
    cats = sorted(set(a) | set(b), key=str); n = len(a); k = len(cats); ix = {c: i for i, c in enumerate(cats)}
    w = weights or [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    po = sum(w[ix[x]][ix[y]] for x, y in zip(a, b)) / n
    pa = [sum(x == c for x in a) / n for c in cats]; pb = [sum(y == c for y in b) / n for c in cats]
    pe = sum(w[i][j] * pa[i] * pb[j] for i in range(k) for j in range(k))
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")

def quad_weights(order):
    k = len(order); return [[1 - ((i - j) / (k - 1)) ** 2 for j in range(k)] for i in range(k)]

def ac1(a, b):
    cats = sorted(set(a) | set(b), key=str); n = len(a); q = len(cats)
    po = sum(x == y for x, y in zip(a, b)) / n
    pi = [(sum(x == c for x in a) + sum(y == c for y in b)) / (2 * n) for c in cats]
    pe = sum(p * (1 - p) for p in pi) / (q - 1) if q > 1 else 1.0
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")

def stat(rows, r1, r2, label):
    if label in ORD:  # ordinal: quadratic-weighted kappa on ranks
        order = ORD[label]; a = [order.index(r[r1]) for r in rows]; b = [order.index(r[r2]) for r in rows]
        return kappa(a, b, quad_weights(order))
    a = [r[r1] for r in rows]; b = [r[r2] for r in rows]
    return kappa(a, b)

def cluster_boot(rows, r1, r2, label, reps=2000, seed=1):
    by_msg = defaultdict(list)
    for r in rows: by_msg[r["msg"]].append(r)
    msgs = list(by_msg); rng = random.Random(seed); vals = []
    for _ in range(reps):
        sample = [r for m in (rng.choice(msgs) for _ in msgs) for r in by_msg[m]]
        v = stat(sample, r1, r2, label)
        if v == v: vals.append(v)
    vals.sort(); return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]

def main(path):
    table = defaultdict(dict)
    for r in csv.DictReader(open(path, newline="")):
        table[(r["label"], r["msg_id"], r["unit"])][r["rater"]] = r["value"].strip()
    labels = sorted({k[0] for k in table})
    pairs = [("B", "C"), ("bot1", "consensus"), ("bot1", "B"), ("bot1", "C"), ("bot1", "bot2")]
    print("label,pair,n_decisions,n_messages,pct_agree,kappa,ci_low,ci_high,ac1")
    for lab in labels:
        for r1, r2 in pairs:
            rows = [{"msg": k[1], r1: v[r1], r2: v[r2]} for k, v in table.items() if k[0] == lab and r1 in v and r2 in v]
            if len(rows) < 5: continue
            pct = sum(r[r1] == r[r2] for r in rows) / len(rows)
            k = stat(rows, r1, r2, lab); lo, hi = cluster_boot(rows, r1, r2, lab)
            a1 = ac1([r[r1] for r in rows], [r[r2] for r in rows]) if lab not in ORD else float("nan")
            print(f"{lab},{r1}-{r2},{len(rows)},{len({r['msg'] for r in rows})},{pct:.2f},{k:.2f},{lo:.2f},{hi:.2f},{a1:.2f}")

if __name__ == "__main__":
    main(sys.argv[1])
```
