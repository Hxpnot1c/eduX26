# DfE generative AI product safety standards: how Synapse maps to them

**Source:** Department for Education, *Generative AI: product safety standards*, GOV.UK, **updated 19 January 2026** (read in full on 19 November 2026; the page lists 13 standards, each labelled learner-facing or learner and teacher-facing). Quotations below are from that page.

**Read this first.** Synapse is a connector that a school's chosen chatbot calls. It is not the chat product the pupil types into. So the standards that are about what the pupil sees and says (filtering, distress detection, safeguarding alerts) belong mainly to the chatbot company and the school's choice of it. Synapse **deliberately holds no message text** (decision 0011), which is also why it cannot do prompt logging or text-based distress detection. We should say that plainly, not claim compliance, and tell a school which standards it must check with its chatbot supplier.

| # | Standard (scope) | What it expects | Synapse today | Gap or action | Owner |
|---|---|---|---|---|---|
| 1 | Stated purpose | State the purpose; do not "exaggerate the impact or capabilities" | Formative practice feedback, not a grade (0014); simulations captioned as synthetic | Keep the pitch to this; no "gaming-proof" | Vishnu |
| 3 | Filtering (learner-facing) | Prevent harmful content, throughout a conversation | None: Synapse sends teaching instructions, not free content | Belongs to the chatbot; the school must check it | School |
| 4 | Monitoring and reporting (learner-facing) | Log prompts and responses; alert the DSL to harmful content and to disclosures; report the rate of cognitive offloading to teachers | Does **not** log messages (minimisation). Records "just show me" and passive trends per student; teacher view is a mock-up | **Tension to disclose:** the school gets prompt logging only from the chatbot. Offloading report: the data exists (`trends.just_show_me`), the teacher view does not | Vishnu, school |
| 5 | Security | Resist jailbreaking; permission levels | Key in URL query string (C10: hashing built, OAuth held); no admin roles | Held (Part 3). Say so | Vishnu |
| 6 | Privacy | No commercial use of personal data without a lawful basis | No ads, no training; retention and erasure built (0011); no message text | DPIA notes updated; DPO review open | Vishnu, DPO |
| 7 | Intellectual property | Do not store learners' work | Free-text answers are not stored; only scores and ids | None | |
| 8 | Design and testing | Transparency and children's safety; test new versions | 211 tests, an MCP check, notice in `chatbot_setup.md` (C11) | No child-user testing yet | School pilot |
| 9 | Governance | Risk assessment; complaints route | `dpia-notes.md` is a draft; no complaints route | Needs the school's named contact | Vishnu, school |
| 10 | **Cognitive development** (learner-facing) | No "final answers, full solutions, or complete worked examples by default"; "prompt learners for input before providing answers"; "only show a full solution after a genuine learner attempt"; friction to switch to direct help; track offloading | Strong match: a pre-question first, then teach; `just_show_me` is recorded and not rewarded; a worked example first asks a quick question after 2 shows (`show.max_per_part_session`). **Gap:** the first "just show me" shows the answer at once, which is not "after a genuine attempt" | This is the hint ladder in C12 (held). The DfE text is a new reason to prioritise it | Vishnu |
| 11 | Emotional and social development | No anthropomorphism; remind users AI cannot replace human relationships; **hard** time limits that cannot be bypassed | No mood inference; break suggestions are **soft** (0013) | Hard limits are a school or device policy; we do not enforce them. Say so. The "I" statements rule is the chatbot's | School |
| 12 | Mental health (learner-facing) | Detect signs of distress, tiered response, flag the DSL, always point to human help | **Nothing.** Synapse cannot see text. A fatigue or rapid-guess signal is not distress and must never be presented as one | **Required before any pupil pilot (C22):** the school confirms its chatbot does this; Synapse adds a one-line "if you're struggling, talk to someone" in the setup text and a documented rule that timing signals never reach a teacher as welfare flags | Vishnu, school |
| 13 | **Manipulation** | No flattery, false confidence, inappropriate reward promises, or design "to prolong use" | Strong match: no streaks or points, reminders opt-in and without guilt, calibration shown as a gap not a score, practice labelled as not a grade, a stop offered when finished | Keep checking new wording against this list | |

## What this changes
- **C12 (hint ladder) moves up** in priority. The first-show-at-once behaviour is the clearest divergence from the DfE text. Still held for Vishnu.
- **C22 stays required before a pilot**, with the split above (chatbot company: detection and DSL alerts; Synapse: no welfare inference, signposting line, honest disclosure).
- **Disclosure to put in the pitch and white paper:** "Synapse does not replace the chatbot's filtering, logging or safeguarding monitoring. It deliberately keeps no message text."
- A teacher-facing **offloading rate** is within reach (the `just_show_me` trend exists), and is one of the few things the standards ask teachers to be given.

## Limits
The standards apply to products, and whether a connector is "a product" under them is a question for the school's DPO. The wording above is the DfE's, not legal advice. Vendor blogs describing these standards were not relied on.
