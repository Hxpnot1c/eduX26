# 0002. Research alignment register

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Vishnu (several items are product calls; see the "Owner" column)
- **Pull request:** this one

## Context

Before the Part 1 fixes and Part 2 pull requests A to F, the whole repository was read against the project's literature review (439 records, 14 to 17 November) and a further round of gap research (18 November). This register lists what the audit found, how serious it is, what the evidence says, and which pull request and record deals with it. It is a living document: each pull request updates the status of its own rows.

**Limits of the audit.**
- It was a reading of the code, settings, text and docs. Only the instruction word count was executed (897 of 900 words).
- The decisions file (`synapse-decisions-18nov.md`) and the `research/overnight` branch were not available to the audit. Rows may overlap Part 1 or Part 2 items and should be reconciled with them.
- Many sources were read at abstract or search-summary level only. The confidence column says so. Treat "abstract only" as "check before quoting".

## Decision

Adopt the register below as the work list for research alignment, in the priority order shown. P0 items contradict the research or risk a false claim. P1 items are well supported and should follow. P2 items are robustness and housekeeping. Held items stay held until Vishnu confirms.

## Research basis

The register cites sources in short form. Each implementing record gives the full citation and the limits.

### P0: contradicts the research, or risks a false claim

| ID | Finding | Code or doc | Research basis | Confidence | Owner | Status |
|---|---|---|---|---|---|---|
| C1 | An ordinary chat message raises `p_known` through the exchange nudge (depth 1.1, engagement 1.05), with no cap. About 14 to 20 labelled messages reach "secure" with no tested answer, and a student can steer the labels. | `edux/learner.py` `apply_exchange`; `settings.toml` `[nudges]` | Fluency is not mastery (Soderstrom & Bjork, 2015; Bastani et al., PNAS 2025: practice scores up 48%, unaided exam scores down 17%). Chatbot labels are unvalidated (LLM scoring of chat logs: best case accuracy 0.85 with no annotator agreement). | High for the principle; the cap value is a judgement call | Vishnu (changes levels) | Proposed: [0003](0003-cap-the-exchange-nudge.md), #46 |
| C2 | `points_met` is accepted as the chatbot sends it. A student can claim points, copy the chatbot's reply, or retry a multiple-choice check. | `edux/learner.py` `score_answer`; `edux/service.py` `tutor_turn` | LLM judges can be steered by injected text (Maloyan & Namiot, 2025: up to 73.8% attack success); models flatter users (Sharma et al., 2023); short-answer scoring agreement runs from near zero to about 0.7 weighted kappa. | Medium (abstracts and secondary reports) | Engineering | Planned |
| C3 | Ask and Verify are shown as levels; the Ask score rewards a phrasing pattern ("asks for sources"), which can invite fabricated citations and may penalise English-as-an-additional-language writers. | `ingest/ai_literacy/`, `text/literacy/`, `get_my_progress` | About four items per class give a standard error near 0.25; prompt length is unrelated to grade (r = .036); scoring should rest on structured judgements, not prose style. | Medium | Vishnu (changes wording and display) | Planned |
| C4 | "Fatigue" is inferred from falling performance, is sticky for the session, and a per-student `study_pattern` ("your answers drop after N minutes") is stored and shown. | `edux/learner.py` `_fatigued`; `service.py` study pattern | Response-time effort and effort-moderated scoring need no affect label (Wise & Kong, 2005; Wise & Kingsbury, 2016). Low-stakes rapid guessing starts late for reasons of motivation and working memory, not "fatigue" alone (Lindner et al., 2019; ages 10 to 11). EU AI Act Art. 5(1)(f) bans emotion inference from biometric data only (Commission Guidelines, 4 February 2025, paras 249 to 251). The project's own simulation flags about 77% of non-tired students by 60 minutes. | Medium. Legal reading needs counsel. | Vishnu | Decided 18 Nov, built in step 05s: [0013](0013-fatigue-as-pacing.md), #55 (curves deferred) |
| C5 | Personalisation is on by default, with values the project's own simulation calls "mostly noise" (k = 20, scale 2.0, bounds 0.5 to 1.5). | `settings.toml` `[personalisation]` | ICO Children's Code Standard 12: profiling off by default unless there is a compelling reason. Learning-rate estimates are unstable on short sequences (Lee et al., 2026). The repo's own recalibration is k = 400, scale 1.0, bounds 0.7 to 1.3. | Medium | Vishnu | Decided 18 Nov: offset off by default, starting points stay on. [0007](0007-personal-learning-rate-off-by-default.md), #50 |
| C6 | No retention limit, erasure or export. `demo.remove_students` leaves `call_log` rows. Student ids are slugs of real names. `STORE_PROMPTS` is dead. | `edux/cli.py`, `edux/demo.py`, migrations | UK GDPR Art. 5(1)(e) and Art. 17; ICO storage-limitation guidance; ICO "Edtech examined" (about 70% of audited providers had no clear retention period). | High for the requirement; retention periods are a judgement call | Vishnu | Decided 18 Nov: [0011](0011-data-handling.md), #54 |

### P1: well supported, build next

| ID | Finding | Research basis | Confidence | Owner | Status |
|---|---|---|---|---|---|
| C7 | No confidence or calibration capture, and no commit-before-reveal on checks. | Calibration as the signature metric (Fernandes et al., 2025); cognitive forcing reduces over-reliance (Buçinca et al., 2021). No validated reliance instrument exists. | Medium | Vishnu | Planned |
| C8 | Aided and unaided evidence are not separated. `homework` is accepted but changes nothing. | Bastani et al. (2025); OECD Digital Education Outlook 2026. | Medium | Vishnu | Planned |
| C9 | No seeded-error or clean-control items, so error detection and appropriate reliance are unmeasured. | Seeded-error item rules: one human-injected atomic error, 30 to 50% clean controls, rotated forms. | Medium | Vishnu | **Held** (Part 3 literacy expansion) |
| C10 | The student key travels in the URL query string, is stored in plain text, and never expires or rotates. | RFC 9110 §17.9; RFC 9700 §4.3.2; MCP authorization spec (2025-06-18): access tokens must not be in the query string; UK GDPR Art. 32. | High for the rule | Vishnu | Documentation and hashing proposed; OAuth **held** (Part 3 key security) |
| C11 | Students are not told what is recorded or how to delete it. | ICO Children's Code Standard 11 (transparency). | Medium | Vishnu | Planned |
| C12 | `try_first` and `hint` choices are accepted but do nothing. The first "just show me" gives the answer at once. | Attempt-first and hint ladders (Bastani et al., 2025; DfE generative AI product safety standards: no full answers by default). | Medium | Vishnu | **Held** (Part 3 better reteach) |
| C13 | Feedback has no feed-forward line. "Mark the figures that need checking" is a blanket flag. | Hattie & Timperley (2007); blanket hedging cut correct reliance as well (94.8% to 83.1%). | Medium | Engineering | Planned |
| C14 | `review_when_below` is 0.50 against evidence favouring 0.70 to 0.80. Decay numbers are uncited. | Cepeda et al. (2008); Carpenter, Pan & Butler (2022): feedback on retrieval and 1 to 7 day gaps in classrooms. | Medium | Engineering | Planned |

### P2: robustness and housekeeping

| ID | Finding | Status |
|---|---|---|
| C15 | The `finally` block in `timed()` can replace a tool result if the `call_log` insert fails. Stored error text can echo input. | Proposed: [0004](0004-count-results-as-sent.md), #47 |
| C16 | The result budget did not count what is sent: the SDK pretty-prints (3,571 characters on the wire against 2,355 counted for `get_my_progress`), `get_my_progress` was not checked, and the gate used a median. | Proposed: [0004](0004-count-results-as-sent.md), #47 |
| C17 | Only three words of instruction headroom (897 of 900). Tool descriptions (895 words) are outside the cap. | Planned (before Part 2 A) |
| C18 | Unbounded input sizes; no rate limit; migrations not run under a lock. | Planned |
| C19 | No unit tests. `scripts/check_mcp.py` is the only check and needs a running server. | Planned (this series) |
| C20 | Documentation drift: `dpia-notes.md` is referenced but missing; `settings.md` lists removed keys and has no "from research" or "judgement call" labels; step 05e disagrees with the code on ignored literacy tasks. | Planned |
| C21 | No accessibility, plain-language mode or English-as-an-additional-language audit. | Later |
| C22 | No safeguarding pathway for distress or disclosure. | Required before any pupil pilot; not needed for filming |

### Corrections to the research itself

Made in the research pack (outside this repository) on 18 November.

| ID | Correction |
|---|---|
| R1 | EU AI Act Art. 5(1)(f): the ban covers emotion inference from **biometric data** only. Text or timing inference is out of scope, fatigue is a "physical state" (in safety examples), keystroke dynamics are biometric, and the exception is narrow. Counsel should confirm for response-latency data and territorial scope. |
| R2 | Koedinger et al. (PNAS 2023): the starting-point result is robust and replicated (Simpson et al., 2024); the uniform-learning-rate result is sensitive to how many practice opportunities are included (Lee et al., 2026). Say "on long practice sequences" and do not claim learning rate is uniform. |
| R3 | BKT parameters are mostly judgement calls. Only guess + slip < 1 and caps below 0.5 are evidence-based (van de Sande, 2013). |
| R4 | Citations the repo relies on were missing from the index. Many are now in `research.md`. |
| R5 | Every numeric setting needs a "from research" or "judgement call" label. |

## Alternatives considered

- **Fix everything in one pull request.** Rejected: the house rule is one logical change per pull request, and several rows are product calls.
- **Treat the audit as advice only.** Rejected: unlabelled numbers and unvalidated chatbot labels directly affect the claims the pitch makes.

## Consequences

The work list is explicit and ordered. Rows that change what students or teachers see wait for Vishnu. Held items stay held.

## Verification

Each row moves to a record with a pull request number and the verification commands for that change. The register is complete when no P0 row is "Planned".

## What would change our mind

A pilot with real students showing the exchange nudge, the performance-based fatigue rule or personal learning rates improve prediction on held-out data would justify reinstating them with fitted values.

## Open gaps in the evidence

- No A-level or UK secondary evidence for bridging, knowledge tracing or spacing of free-response mark points.
- No study of a student's own chatbot labelling that student's work.
- No published guidance on audit sampling rates for chatbot labels (our own arithmetic: about 385 labels per stratum for ±5 percentage points, about 96 for ±10).
- UK rostering, NCSC guidance on URL secrets, the full DfE product safety standards text, and ChatGPT connector authentication were not verified.
- Legal questions marked for counsel: AI Act scope for an England-only product, controller and processor roles if we tune on usage data, and whether response latency counts as biometric.
