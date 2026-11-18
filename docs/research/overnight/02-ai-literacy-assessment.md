# 02 · Defining and assessing AI literacy

Wave 1. Sources:
- **Scout notes.** `work/w1/w1-02a.md` (framework crosswalk; marks in `verify-D.json`) and `work/w1/w1-02b.md` (validity and reliability; marks in `verify-B.json`).
- **Panels.** The researcher panel (`panel-researcher.md`) and the student panel's points on literacy (`panel-student.md`).
- **Branch.** We read `build/05e-literacy-coaching` read-only in `/home/vishnu/edux26` to check the panel's claims about scoring.

Marks: ✓ confirmed, ~ broadly supported with a stated problem. Findings marked ✗ are left out.

**Coordinator's fact, which overrides the scout notes.** Step 05e is **built on its branch, 14 commits ahead of `main`, and not merged** (we checked with `git rev-list` and `merge-base`). Where scout notes say "designed, not built", read "built on the branch".

## Summary
- **What we measure is narrow, and we should say so.** Ask, Verify and How AI works cover parts of AILit Engage 2 and 3 and part of Create 3. No AILit competence is fully covered. Ethics, bias, privacy, authenticity and all of Shape AI are missing or out of scope (w1-02-01 ✓, w1-02-03 ✓, w1-02-04 ~).
- **We have three grades of evidence, and only one is scored by the server alone.**
  - (a) the letter in a how-AI-works MCQ, scored by the server;
  - (b) labels the chatbot gives the student's behaviour (question features, verify ticks), with no reliability data yet;
  - (c) what the student says they did ("I opened it").
- **The branch has five scoring problems that the researcher panel found.** We confirmed four in the code and one in part (see "Scoring problems in the 05e branch"):
  - Ask's threshold contradicts its coaching;
  - an ignored task scores 0;
  - Verify can be met by restating the reply;
  - two how-AI-works triggers don't fit their items;
  - the distractors give the answer away through absolute wording.
- **Reliability needs many moments.** One moment is worth about ρ₁ ≈ .17. Reliability .70 then needs about 12 moments per skill, and .80 needs about 20. With noise from the chatbot's labels, those become about 18 and 30 (w1-02-31 ✓).
- **The levels move too fast and stay fooled.** Simulation (synthetic students): two correct moments take a skill from new to secure. One unprompted "I checked" makes Verify secure (p = 0.82). With 15% of labels flipped, 11–16% of students without the skill end "secure" (w1-02-32 ✓).
- **A level falls in days because of the 2-day half-life.** A Verify level a week after one success shows about 0.22. That measures recency, not skill (w1-02-34 ✓). The branch has no separate half-life for literacy parts.
- **A credible validity target exists.** Published game-based stealth assessments reached r ≈ .36–.41 with external tests, after hours of play (w1-02-21 ✓, w1-02-22 ✓; convergent validity, not learning). Candidate external measures are GLAT for How AI works (w1-02-23 ✓) and a Civic Online Reasoning task for Verify (w1-02-27 ✓). Nothing validated measures Ask.
- **What to claim on Thursday.** Not "a validated test", but a validity argument. Scoring uses fixed rules; we report evidence counts; an agreement study against humans is planned (or done on Wednesday); a pilot of at least 62 students is designed.

## Ranked recommendations
Ranks 1–11 can be done before Thursday 23:59. "Branch" means `build/05e-literacy-coaching`, which the build team owns. This report edits no code or settings.

| rank | recommendation | lands in | effort | before Thu? | rests on |
|---|---|---|---|---|---|
| 1 | **Definition and competency-model slide** (text below; [01](01-competition-fit.md) links here and does not repeat it). | pitch, video | S | yes | w1-02-01 ✓, w1-02-02 ✓, w1-02-07 ✓ |
| 2 | **Fix the Ask threshold.** The cheapest consistent fix is `literacy.ask_min_features = 3`, so a question is coached on Ask until it would also score as correct. The fuller fix (core + bonus) is at rank 13. Put it in `settings-proposal.toml`; the build team changes the branch's `settings.toml`. | settings (branch) | S | yes | branch code; researcher 1 |
| 3 | **Rewrite the how-AI-works distractors without absolute words.** Change "always", "only", "every single day", "on purpose", "every time" into hedged, plausible wrong ideas. Keep the lengths matched. The economics pack has a different give-away (form and length), fixed in [04](04-economics-education.md) rec 1. | course pack (`ingest/ai_literacy/misconceptions.csv`) | S | yes | branch data; researcher 3; student 3 |
| 4 | **Record an ignored task or check as missing, not 0.** Log it as an engagement event and leave BKT alone. Non-response is not low skill. | build (branch: `service._literacy_followup`, `_how_ai_works`) | S | yes, if the build team has time | branch code; researcher 1; student 3 |
| 5 | **Make Verify hard to pass by restating the reply.** Change the `verify_new` task to ask for something the reply doesn't contain (e.g. "what does the page give for the month before?"). Add a fifth tick: "decided to accept, revise or reject, and why". Require that tick for secure. Downweight tick 1 ("opened the source"), which can't be observed. | course pack, text (branch) | S | yes | w1-02-03 ✓; researcher 2 |
| 6 | **Damp unprompted reports.** Set `ail_unprompted` guess to 0.20 (our choice; then p after one report is 0.70, not 0.82), or require at least 3 ticks. Put it in `settings-proposal.toml`. | settings | S | yes (proposal) | w1-02-32 ✓; student 3 |
| 7 | **Key the fabrication check on web access.** Fire `ail_how_fabrication` only when `web_access` is false. That needs the label on conflict turns, because today it is stored on research turns only. Until then, drop distractor m2 ("searched… picked the wrong entry") for chats with search turned on. For the video, film with web search off, so correcting m2 is true (see the [demo plan](demo-plan.md)). | build (branch: `plan.HOW_TRIGGERS`, `learner` labels) | S–M | maybe | branch code; researcher 3 |
| 8 | **Inter-rater check of the chatbot's labels.** Hand-write 40 synthetic research questions (0–4 features) and 20 replies to Verify tasks (0–4 ticks). Two team members tick them blind against a one-page rubric. Get the chatbot's labels through the real MCP, and report Cohen's κ per feature with 95% CIs. κ ≥ .60 = usable for low-stakes formative use (our choice). Don't generate the messages with the model under test. | demo, pitch | M | yes (Wednesday, if time) | w1-02-28 ~, w1-02-29 ~ |
| 9 | **Validity-argument slide** (the table below), filled in with whatever #8 produces. Call the method "embedded assessment". The Ask and Verify tasks and the how-AI-works check are overt, so "stealth" overclaims; it fits at most the scoring of question features. | pitch | S | yes | w1-02-33 ~ |
| 10 | **Known-groups persona check.** Run a "novice" and a "practised" persona for 8 research turns each through the MCP on a fresh `EDUX_DATA_DIR`, and show their levels diverge. Say it tests the pipeline, not students. | demo | S | yes, once merged | scout note w1-02b |
| 11 | **Fix `docs/build/reference/research.md` row 29.** How AI works anchors to AILit Engage 2 (Knowledge 1.3 and 1.4), not Shape AI. The 05e Khanmigo line is fixed under [09](09-safety-ethics.md) rec 11. Team docs. | docs | S | yes | w1-02-04 ~ |
| 12 | **Show `n_moments` per skill and "provisional" below 8 moments** (our choice; about .58 reliability at ρ₁ = .15). The pitch line can be used now. | build (branch: progress), pitch | S | pitch yes; build maybe | w1-02-31 ✓ |
| 13 | **Ask scored as core + bonus.** Concept + context = the core, sources and reasoning = bonus, so "What was UK CPI in Feb 2025?" passes. | build | M | no | researcher 1 |
| 14 | **A `pushback_correct` label.** Don't fire the "agrees to please" check when the student rightly corrected the chatbot. | build, text | M | no | researcher 3 |
| 15 | **Two wrong picks before a misconception shows as "held"** on how-AI-works parts. One guess (p = .25) shouldn't label a student. | build | S–M | no | researcher 3 |
| 16 | **A separate half-life for literacy parts** (e.g. 14 days, our choice). | build, settings | M | no | w1-02-34 ✓ |

## Framework crosswalk (compact)
Status: **main** = built on `main`; **branch** = built on the 05e branch, not merged; **—** = not built. Evidence grades (a), (b) and (c) are defined in the Summary.

**OECD–EC AILit Framework (final, 2026): 4 domains, 19 competences** (w1-02-01 ✓)

| AILit competence (abridged) | eduX | coverage | status | grade |
|---|---|---|---|---|
| Engage 1: AI's role and influence | How AI works: agreement | partly | branch | a |
| Engage 2: describe how AI does tasks, correcting misconceptions | How AI works (4 parts) | Basic rung only (recognition) | branch | a |
| Engage 3: accept, revise or reject outputs | Verify | to Intermediate; Advanced needs the justification tick (rec 5) | branch | b, c |
| Engage 4–7: recommenders, energy, bias, ethics | — | missing or out of scope | — | — |
| Create 1: build on own ideas | `constructive` label, try-first | proxy | main | b |
| Create 3: direct generative AI | Ask | partly | branch | b |
| Create 2, 4: prototyping; authenticity and IP | — | out of scope; coach only (JCQ) | — | — |
| Manage 1: decide whether to use AI for the task | "just show me" share (trend) | proxy | main | b |
| Manage 2: choose an approach by how systems work | How AI works: cutoff | partly | branch | a |
| Manage 4: monitor AI use | progress trends | proxy | main | b |
| Manage 3; Shape 1–4 | — | missing or out of scope | — | — |

**Count.**
- Fully covered: 0.
- Partly: 8. Five rest on the branch (Engage 1, 2, 3; Create 3; Manage 2) and three on `main`, as proxies (Create 1; Manage 1, 4).
- Missing or out of scope: 11.

A scout note's count ("only 3 rest on anything built") predates the coordinator's check and is out of date.

**Other frameworks, briefly:**
- **UNESCO students' framework (2024): 12 competencies.** The ethics aspect is missing (w1-02-06 ✓). It also has a privacy competency ("Safe and responsible use"); we coach on privacy and never score it, because scoring would mean logging disclosures.
- **Long & Magerko (2020).** Their three-part definition maps evaluate → Verify, communicate → Ask, use as a tool → the "just show me" trend (w1-02-07 ✓).
- **Ng et al. (2021).** Partial on 3 of 4 aspects; ethics is missing (w1-02-08 ~, abstract only).
- **Digital Promise (2024).** Its "Evaluate" means weighing AI's costs and benefits to society, not fact-checking. Don't map Verify to it (w1-02-09 ✓).
- **AI4K12.** We touch Learning and Natural Interaction only (w1-02-10 ✓).
- **England.** The Curriculum and Assessment Review says to understand how AI works and to use it without becoming dependent on it, and places AI in Computing (w1-02-11 ✓). eduX complements that inside a subject. The DfE product safety standards (13 headed sections) ask for no final answers by default and for tracking offloading (w1-02-12 ✓).
- **JCQ / Ofqual.** They cover acknowledging AI use in coursework; 9EC0 is exam-only, so coach only (w1-02-13 ✓).
- **EU AI Act Art. 4.** It concerns the staff of providers and deployers, not pupils. Business plan only (w1-02-14 ~, secondary source for the 2026 amendment).

## Definition and competency model (ours, for the slide)
> **AI literacy, for a 16–18-year-old studying with a chatbot (our definition):** knowing when and how far to trust it, shown in what they do while they work. That means asking questions it can answer and that can be checked; checking the claims that matter against a source they can name, then deciding to accept, revise or reject them; and recognising, when it fails, why it failed: invented sources, confidence that isn't evidence, a training cut-off, giving way to pushback.

Anchors: AILit's distinction between literacy and tool use (w1-02-02 ✓); Engage 2–3 and Manage 1 (w1-02-03 ✓, w1-02-05 ✓); the CAR's "without becoming dependent" (w1-02-11 ✓); Long & Magerko's definition (w1-02-07 ✓).

| skill (as shown in progress) | what we observe in chat | grade | levels (new → developing → secure) | what we cannot observe |
|---|---|---|---|---|
| **Ask** | Names the idea; gives place and period; asks for sources; asks for reasoning; rewrites after coaching | b | vague → one feature missing → precise and checkable | Whether a better question came from understanding or from copying the feedback |
| **Verify** | Names source, publisher and date; states what the source says; says whether it matched; *accept / revise / reject and why (proposed)*; checks unprompted | b, c | doesn't check → checks when asked → checks unprompted and justifies the decision | Whether they opened the link; checking done outside the chat |
| **How AI works** | Picks the right explanation in a 4-option check at the moment of a failure | a | — (per-part level) | Explaining it in their own words (AILit Intermediate); transfer to other tools |
| *Just-show-me trend* (shown to the student, **not scored**) | Share of "just show me" choices over 14 days | b | — | Whether a choice reflects judgement or tiredness |
| *Responsible use* (**coached, not scored**) | One line on what not to paste and on acknowledging AI use | none | — | everything |

The model is narrow on purpose. It assesses the critical use of chatbot output for study, which is close to information literacy (researcher objection 5). Two honesty lines for the pitch:
- "Only the how-AI-works letters are scored by our server alone."
- "AILit levels aren't tied to age, so we don't claim 16–18-year-olds should be Advanced" (w1-02-01 ✓).

**Not adopted: "Decide" as a fourth scored skill (a scout proposal).** We keep the trend unscored, for three reasons:
- the student panel reads it as surveillance (student objection 4);
- a "hint" choice isn't proof of judgement (w1-02-05 ✓, risk);
- the progress output on video shows `ask`, `verify` and `how_ai_works`, so the slide should use the same names.

## Validity argument (Kane-style, one slide)
Structure from Kane (2013) and the AERA/APA/NCME Standards' five sources of evidence (w1-02-33 ~, abstracts and secondary only).

| claim (inference) | evidence we have | threats we know of | evidence we'd gather |
|---|---|---|---|
| **Scoring:** a tick or letter means the student did it | Fixed server rules; the how-AI-works letter is scored by the server; an evidence-centred design document | Chatbot labels unchecked; Verify ticks 2–4 can be met by restating the reply; "opened" can't be seen; distractor cues; ignored = 0 | κ per feature, chatbot vs two humans, on 40 + 20 synthetic messages (rec 8); a per-chatbot audit of self-labels (`source_conflict`, `pushback_changed`, `web_access`) on about 20 scripted transcripts |
| **Generalisation:** enough moments for a stable level | Spearman–Brown: about 12 moments for .70 (w1-02-31 ✓) | Two moments reach secure; one self-report reaches 0.82 (w1-02-32 ✓); each how-AI-works part is checked at most once a session; Ask and Verify only on research turns | Show `n_moments` and "provisional" (rec 12); split-half reliability of Ask in the pilot |
| **Extrapolation:** the level reflects AI literacy beyond eduX | Content overlap: How AI works and GLAT's hallucination and cutoff items (w1-02-23 ✓); lateral reading can be taught (Wineburg et al. 2022, in `research.md`) | Construct narrow (close to information literacy); Ask rewards a prompt ritual | Convergent r with GLAT or AILIT-S and one COR task (N ≥ 62; target r ≈ .3–.4); discriminant check against economics levels; think-aloud with 5 students |
| **Use:** coaching on the level helps and doesn't harm | Formative only, no grade; answers on research questions never withheld | A level that decays in days reads as "lost the skill" (w1-02-34 ✓); the label "held" after one wrong pick; scores may vary with the chatbot | Pre/post AILIT-S in a pilot; fairness check by group and by chatbot; log which chatbot labelled each exchange |

Slide wording (our draft): *"We don't claim a validated test. We claim a validity argument: fixed scoring rules, labels checked against humans (κ = __), levels shown with evidence counts, and a pilot designed to correlate with an external AI-literacy test."*

## Reliability maths in brief
All of this is first-principles calculation (w1-02-31 ✓, recomputed by the verifier).
- **One moment.** Back-solving from GLAT (α .80, 20 items) and the Newton's Playground test (α .72, 12 items) gives ρ₁ = α / (k − (k−1)α) ≈ .17. This holds only *if* a moment is as good as a carefully built MCQ item.
- **Moments needed** (Spearman–Brown, k = ρ*(1−ρ₁) / (ρ₁(1−ρ*))):

  | ρ₁ | for .60 | for .70 | for .80 |
  |---|---|---|---|
  | .17 | 8 | 12 | 20 |
  | .12 (with label noise) | 11 | 18 | 30 |
- **Label noise.** ρ₁ × r_rater ≈ .17 × .70 ≈ .12. Treating κ as a reliability coefficient is an approximation (our choice).
- **Attenuation.** r_obs = r_true × √(rel_ours × rel_test). With .6, .6 and .7, r_obs ≈ .39, which is why r ≈ .4 counts as a good result.
- **Pilot size.** Fisher z at power .8 and α .05: r = .35 needs N ≈ 62; r = .40 needs N ≈ 47.
- **Agreement-study precision.** With κ = .7 and 40 items per feature, the 95% CI is about ±.22. Report per-feature CIs.
- **BKT simulation** (simulation: synthetic students; no course pack; branch settings, which we confirmed match; best case, because the data follow the model's own assumptions) (w1-02-32 ✓):
  - two correct moments go from 0.30 to secure;
  - one `ail_unprompted` gives 0.82;
  - with 15% flipped labels after 12 moments: corr(p, truth) .86 for `ail_task`, and 11–16% false "secure".
- **What this means in time.** A student asking 2–3 research questions a week needs over a month to get a reliable Ask level. Meanwhile the 2-day half-life drags levels down between moments (w1-02-34 ✓).

## Scoring problems in the 05e branch
The researcher panel's five problems. We checked each with `git -C /home/vishnu/edux26 show origin/build/05e-literacy-coaching:<path>`.

| # | problem (panel) | what the branch shows | verdict |
|---|---|---|---|
| 1 | **Ask 2/4 = 0.5 is below `correct_share` 0.67, yet `ask_min_features = 2` treats it as good enough.** | `learner.question_evidence` scores features / 4. `apply_evidence_event` sets correct when score ≥ `bkt.correct_share` (0.67). `plan.literacy_task` moves to Verify when there are 2 or more features. So a 2-feature question counts as *wrong* for Ask, yet the student is coached on Verify. In effect, Ask is correct only at 3 or more features. The precise "UK CPI in Feb 2025?" (concept + context) fails. | **Confirmed** |
| 2 | **An ignored task is recorded as 0** (`ail_task` slip .10), heavier than a vague question. | `service._literacy_followup` records `ail_task` 0.0 after `max_followups` (1) re-asks within a session. `_how_ai_works` does the same for an unanswered check (`ail_how` 0.0). Settings: `ail_task` slip .10, guess .15 vs `ail_question` .15 / .20, so a 0 moves p further. Nuance: a session gap or fatigue drops the task **unscored**. | **Confirmed**, with that nuance; it also applies to how-AI-works checks |
| 3 | **Verify measures restating:** "opened" can't be seen; ticks 2–4 can be met by repeating what the chatbot said; the source is one the chatbot proposed. | Mark points p1–p4 are as stated, and p1 ("opens the source") can't be observed. The `verify_new` task asks for the month of a figure, which a sourced reply may already give. But `answer_with_sources` tells the chatbot to prefer the pack's **trusted sources**, so the source is teacher-curated, not the chatbot's own choice. It is still checking the cited source, not reading other sources. | **Partly confirmed.** Restating is possible; the "chatbot-proposed source" part is only partly true |
| 4 | **How-AI-works triggers don't fit their items.** | `plan.HOW_TRIGGERS`: fabrication fires on `source_conflict` alone, with no `web_access` condition, while cutoff does check it. `source_conflict` includes a link that "didn't say what was claimed". With search on, that is often misattribution, so distractor m2 ("searched a source database and picked the wrong entry") may be the true account. `web_access` is stored only on research turns. Agreement fires on `pushback_changed`, which has no condition on whether the student was right, so "check against the notes" is the wrong lesson when the student corrected a real error. One wrong pick marks a misconception active (`_activate_misconceptions`), and progress lists it as "held". | **Confirmed** |
| 5 | **Giveaway wording.** | In `ingest/ai_literacy/misconceptions.csv`, the distractors carry absolute cues: "every time", "every single day", "always", "only… when", "on purpose". The correct points hedge ("can make up", "doesn't show", "can shift"). Lengths look matched (commit 7674bbd shortened the fabrication point to match), and none of the literacy options has a full stop. So the full-stop and length cue is in the **economics** pack ([04](04-economics-education.md)), not the literacy pack. | **Confirmed** for absolute versus hedged wording; the length cue doesn't apply to literacy items |

**Also confirmed on the branch:**
- The 05e step doc still carries the withdrawn Khanmigo line (line 7; fix in [09](09-safety-ethics.md) rec 11).
- Progress shows a level per skill, with no `n_moments`.
- `[literacy]` has no separate half-life.
- Each how-AI-works part gets at most one check per session.

**One correction to both panels.** Ask and Verify evidence comes only from research turns. But three of the four how-AI-works triggers (fabrication, agreement, confidence) fire on any turn type; only cutoff needs a research question. So How AI works is not limited to research turns (researcher 5, student 2).

## Later (not before Thursday; for the business plan and Q&A)
- **Convergent-validity pilot, preregistered.** At least 62 consenting students, with school consent and a DPIA. Measures: How AI works vs GLAT or AILIT-S; Verify vs one COR task scored by two humans; Ask vs a human-rated question-writing task. Expect r ≈ .3–.4 (w1-02-21 ✓, w1-02-22 ✓, w1-02-23 ✓, w1-02-24 ~, w1-02-27 ✓).
- **Per-chatbot audit of self-labels, and logging which chatbot labelled each exchange.** This covers measurement invariance and fairness (w1-02-30 ~).
- **Think-aloud with 5 students** (response-process evidence).
- **Explain-back after a how-AI-works check** (to reach AILit Engage 2 Intermediate), and an `ail_how_bias` part once a trigger label exists.
- **Literacy moments inside homework turns** (student 2), e.g. "which line of that answer would you check against your notes?". This is not designed yet.
- **IRT calibration of the how-AI-works items.** It needs hundreds of responses per item.

## Considered and rejected
- **Self-report scales (MAILS, SNAIL, AILQ) as the convergent check.** MAILS correlates only r = .21 with a knowledge test (w1-02-25 ✓). A self-report vs performance meta-analysis found r = .055, CI −.047 to .156 (w1-02-15 ✓; preprint, three correlations, one research programme).
- **Claiming reliability from BKT posteriors.** Our slip and guess are not fitted, so the posterior isn't evidence.
- **Generating the agreement-study messages with the model being tested.** That is circular.
- **Using real students before Thursday.** There is no consent route and no DPIA.
- **Putting GLAT items in the product.** It would contaminate the convergent check.
- **Scoring ethics or privacy.** Rules can't grade open ethical reasoning, and scoring privacy would mean logging minors' disclosures.
- **Mapping 16–18-year-olds to AILit "Advanced", or Verify to Digital Promise's "Evaluate".** Neither is supported (w1-02-01 ✓, w1-02-09 ✓).
- **"Decide" as a scored skill.** See the competency model above.

## Panel objections this report answers or leaves open
| objection | status |
|---|---|
| Researcher 1: scoring contradicts coaching; ignored = 0 | **Partly.** Recs 2 and 4 (S) fix the contradiction and ignored = 0; precise two-feature questions still fail until rec 13, after Thursday. None is made yet. |
| Researcher 2: Verify measures restating | **Partly.** Recs 5 and 3 change the task and add a justification tick. Tick 1 stays unobservable; say so. |
| Researcher 3: items don't fit their triggers; cues; "held" after one click | **Partly.** Recs 3 and 7 can land before Thursday; recs 14 and 15 come later. |
| Researcher 4: the assessed system writes its own evidence | **Partly.** The agreement study (rec 8) covers labels of student messages only. The self-label audit is later. |
| Researcher 5: the claim outruns the construct | **Answered** in wording: a narrow, named construct; "embedded"; evidence counts (recs 1, 9, 12). |
| Student 2: "I'd never see the literacy part" | **Partly.** How-AI-works checks fire on any turn type. Ask and Verify are research-only. Homework moments come later. |
| Student 3: MCQs easy to game; "I checked" makes Verify secure; ignored = 0 | **Answered** by recs 3, 6 and 4, if the build team takes them. |
| Student 4: feels like being watched | **Partly.** The trend is not scored and is shown to the student only. Who sees what must be on the slide. |
| Judges 3: "Why believe a 'secure' Verify?" | **Partly.** There is a validity slide and maths. The BKT settings are unchanged until recs 6 and 16. |

## Findings
| id | claim (short) | strength | population | outcome | mark |
|---|---|---|---|---|---|
| w1-02-01 | AILit final (2026): 4 domains, 19 competences, feeds PISA 2029 MAIL; levels not tied to age | official document | primary and secondary, international | policy | ✓ |
| w1-02-02 | AILit: AI literacy differs from tool use | official document | as above | policy | ✓ |
| w1-02-03 | Engage 3 progression: why and how to verify → verify against trusted sources → justify accept / revise / reject | official document | as above | policy | ✓ |
| w1-02-04 | Engage 2 asks learners to describe how AI works; Knowledge 1.3 and 3.2 | official document | as above | policy | ~ the framework links Engage 2 to Knowledge 1.3 and 1.4; 3.2 goes with Engage 3–4 |
| w1-02-05 | Manage 1: decide whether to use AI; Manage 4: monitor use | official document | as above | policy | ✓ |
| w1-02-06 | UNESCO 2024: 12 competencies, 4 aspects, 3 levels; privacy under "Safe and responsible use" | official document | school students, international | policy | ✓ |
| w1-02-07 | Long & Magerko: evaluate / communicate / use; 17 competencies, 5 themes, 15 design considerations | theory | general learners | policy | ✓ |
| w1-02-08 | Ng et al. 2021: 30 articles; four aspects | theory | mixed | policy | ~ abstract only |
| w1-02-09 | Digital Promise "Evaluate" = societal costs and benefits, not fact-checking | practitioner | PK–12, US | policy | ✓ |
| w1-02-10 | AI4K12 Five Big Ideas | practitioner | K–12, US | policy | ✓ |
| w1-02-11 | CAR (Nov 2025): understand AI, use it without dependence; place it in Computing | official document | England | policy | ✓ |
| w1-02-12 | DfE GenAI product safety standards: no final answers by default; track offloading; function-based language; no unjustified confidence | official document | England | policy | ✓ (13 headed sections, not "13 standards") |
| w1-02-13 | JCQ: unacknowledged AI use is malpractice; Ofqual KS4/KS5 lesson plan (9 Mar 2026) | official document | England KS4/KS5 | policy | ✓ |
| w1-02-14 | EU AI Act Art. 4 duty on providers and deployers; softened by the 2026 Omnibus | official document | EU | policy | ~ secondary sources only for the amendment |
| w1-02-15 | Self-report vs performance: r = .055 [−.047, .156], N = 2,765 | meta-analysis (exploratory preprint) | workplace adults | prediction | ✓ |
| w1-02-20 | Newton's Playground: gold trophies r = .22–.40 with a physics pretest | correlational | 167 US grade 8–9 | prediction | ✓ |
| w1-02-21 | Use Your Brainz stealth assessment: r = .40 (Raven's), .41 (MicroDYN) | correlational | 55 US 7th graders (47 analysed) | prediction | ✓ |
| w1-02-22 | Physics Playground: stealth estimate r = .36 / .40 with pre / post tests | correlational | US school students, n = 263 | prediction | ✓ |
| w1-02-23 | GLAT: 20 items, α = .80; predicts AI-assisted task performance (β = .22) where self-report does not | correlational | HE students (Prolific) | prediction | ✓ |
| w1-02-24 | AILIT-S: 10 items, under 5 min, 1,465 university students DE/UK/US | correlational | university students | prediction | ~ abstract only; r = .91 from a secondary blog |
| w1-02-25 | MAILS self-report r = .21 with a knowledge test | correlational | 120 German adults | prediction | ✓ |
| w1-02-26 | AILQ (32 items, 363 HK secondary); Chiu et al. 25 MCQs, 2,390 grade 7–9 | correlational | Hong Kong secondary | prediction | ~ abstracts only; HK location for Chiu inferred |
| w1-02-27 | COR national portrait: 3,446 US high-school students; under 2% Mastery; 52% fooled by the video | correlational (descriptive) | US high school | learning (performance level) | ✓ (four of six tasks under 2% Mastery, not one) |
| w1-02-28 | GPT-4 few-shot marking of K–12 short answers κ = .70 vs human .75 | correlational | ages 5–16 | prediction | ~ abstract only; zero-shot .68 not confirmed |
| w1-02-29 | LLM agreement varies by task: GPT-4 QWK .30 / .43 / .87 | correlational | mixed | prediction | ~ Chamieh confirmed; the Jiang & Bosch .677 and "rubric in prompt" not verified |
| w1-02-30 | Autoscoring meta-analysis: decoder LLMs agree less, wording-sensitive, bias | meta-analysis (preprint) | mostly K–12 written work | prediction | ~ 890 = configurations × 10 items; −0.37 on the Fisher-z scale (frequentist −0.14, n.s.); bias from one illustrative output |
| w1-02-31 | ρ₁ ≈ .17; about 12 moments for .70 and 20 for .80; 18 and 30 at ρ₁ .12 | theory (calculation) | n/a | prediction | ✓ |
| w1-02-32 | BKT sim: 2 correct → secure; one unprompted → 0.82; 11–16% false secure with 15% flips | simulation (synthetic students) | 20,000 per cell | prediction | ✓ |
| w1-02-33 | Kane's argument-based validation; the Standards' five sources | theory | n/a | policy (method) | ~ abstracts and secondary only |
| w1-02-34 | Literacy parts use the 2-day base half-life: about 0.22 a week after one success | theory (design review) | n/a | prediction | ✓ |

Also cited here; each sits in its home report's table: w1-09-08 ~ ([09](09-safety-ethics.md)).
