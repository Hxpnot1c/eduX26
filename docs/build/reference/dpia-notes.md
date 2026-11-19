# DPIA notes (draft for DPO review)

**Status: draft, written by the build team. Not legal advice and not a completed DPIA.** Items marked **[COUNSEL]** need a solicitor or the school's data protection officer. This page is what a school's DPIA can start from: what Synapse stores, why, what is core and what is optional, the defaults, how long it is kept and how it is deleted. Dated 19 November 2026; it describes `main` after step 05x.

## Roles
- The school is the likely controller and Synapse a processor acting on its written instructions. If Synapse tunes its settings on live pupil data, or pools data across schools, it becomes a controller (ICO ed-tech guidance). Neither is done, and the settings say not to. **[COUNSEL]**
- The student's own chatbot (claude.ai or ChatGPT) is a separate service the student uses under their own account. The Synapse server never calls an LLM. The chatbot sends Synapse labels and the student's answers; Synapse sends the chatbot a plan, levels and course reference. The chatbot vendor's terms, age limits and data flows are outside Synapse. **[COUNSEL]**

## What is stored, and why
| Data | Where | Why | Core? |
|---|---|---|---|
| Random student id, key hash, optional display name, course, context profile, created and left dates | `student` | Identify the student's link; delete on leaving | Core |
| Each exchange: time, client name, parts discussed, depth and engagement labels, the choice made ("just show me", quiz...), misconception ids, request type, research-question features, flags | `exchange_log` | The learner model and the in-session rules | Core |
| Each answer: part, evidence type, score, point, options shown, misconception ids | `evidence_log` | What the student can do, per mark point | Core |
| Derived state: understanding per part, forgetting clock, held misconceptions, review queue, approaches tried, session signals | `part_state` and the derived tables | Choose what to teach and review; rebuilt from the events | Core |
| The plan last issued and the question waiting for an answer | `issued_plan` | Score the next answer | Core |
| Skipped AI-literacy tasks | `literacy_skip` | A skip is missing, not wrong | Core |
| Classes and what each class has been taught (class id, student membership, part, date taught) | `class`, `class_coverage`, `student_coverage` | Start a student's estimate for a part their class has covered; show "taught in class, not yet checked" | Optional (needs a teacher to set up); the class-level estimate is off unless the school instructs in writing, and never below 5 students |
| Cached per-student starting offsets, by session | `learner_offset_cache` | Speed (a rebuild of derived state can recreate it) | Operational; deleted with the student |
| "How sure are you?" ratings (guess, fairly sure, certain) paired with the answer they follow | `confidence_log` | Show the student their own calibration; never feeds the understanding estimate | Optional (the student can skip) |
| Per-answer timing: seconds taken and word counts (never the text, never keystrokes) | `exchange_log`, `evidence_derived.rapid` | Tell a quick guess from a considered answer; suggest a break after a long session | Core; **not biometric and not used to infer emotion**. See decision 0013 |
| Reminder preference | `student_profile.reminders` | Opt-in reminders | Optional, student-set |
| Find-the-error practice results (kind of item, hit or miss) | `evidence_log` (types `find_error`, `ail_find_error`) | Practice feedback on spotting mistakes; **off unless switched on** | Optional |
| Student-set: interests (free text), exam date, answer length | `student_profile` | Examples and pacing the student asked for | Optional, student-set |
| Student-set: their own tests (name, kind, date, topics) | `student_assessment` | Order reviews towards their tests | Optional, student-set |
| Call log: time, tool, duration, result size, error text (cut to 200 characters) | `call_log` | Performance and faults | Operational |

**Not stored:** the student's message text; faces, voice, typing speed or keystrokes; location; emotion or wellbeing labels; any free-text answer.

## Defaults
- **Learning-rate personalisation: off** (`personalisation.enabled = false`). The starting-point adjustments use only the student's own pre-teaching answers, for their own teaching, and are on. See decision 0007.
- **Class estimates and class fatigue curves** (steps 05q and 05s): off unless a school's written instruction turns them on, with a minimum of 5 students. Teacher views are formative and human-reviewed.
- **Pacing, not affect.** "Long-session mode" and "rushing" come from time on task and answers faster than reading time. Synapse does not infer emotions, and uses no biometric data. Under the EU AI Act, Art. 5(1)(f) bans emotion inference in education from biometric data only (Commission guidelines, 4 February 2025); this design uses none. **[COUNSEL]** for response-timing data and territorial scope.
- **AI-literacy levels are formative** practice feedback, not grades, and are shown with the evidence behind them.

## Retention and deletion
- **Settings** (`retention`, judgement calls, schools set their own): call-log detail is deleted after 30 days; a student marked as having left has all their data deleted 90 days later. `python -m edux.cli purge` applies them.
- **Delete:** `delete-student --student <id> --yes` removes every row about the student from every table with a `student_id` column.
- **Export:** `export-student` writes everything stored about a student as JSON (never the key or its hash).
- **Keys** are stored as SHA-256 hashes. The link still carries the key in the URL: a leaked link is a leaked credential. OAuth or header tokens are planned and held. **[COUNSEL]** on whether this is "appropriate" security for pupil data (UK GDPR Art. 32).

## Principles checked
| Principle | How |
|---|---|
| Minimisation (Art. 5(1)(c)) | No message text, no biometrics, no free-text answers; opaque ids |
| Storage limitation (Art. 5(1)(e)) | Retention settings and `purge` |
| Erasure and access (Art. 17, 20) | `delete-student`, `export-student` |
| Profiling off by default (Children's Code, Standard 12) | Learning-rate offset off; class estimates off |
| Transparency (Standard 11) | A plain notice is in `text/chatbot_setup.md` (register C11, #66): what is kept, formative not a grade, no mood inference, how to delete. Wording needs teacher and DPO review **[open]** |
| Detrimental use, nudges (Standards 5 and 13) | Reminders opt-in, no streaks, no guilt wording (step 05u) |

## Open items
- A plain-language notice to students: what is recorded, that levels are practice feedback, and how to ask for deletion.
- A safeguarding pathway (distress or disclosure) before any pupil pilot. Synapse leaves this to the chatbot today.
- A DPIA proper, with the school: lawful basis, the chatbot vendor as a processor or independent controller, international transfers, retention periods, and a review of the key-in-URL design.
