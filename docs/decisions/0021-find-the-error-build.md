# 0021. Build find-the-error practice, off by default

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (must approve before it is switched on)
- **Pull request:** #64
- **Audit item:** C9 in [0002](0002-research-alignment-register.md); scoped in [0012](0012-find-the-error-scoping.md) (pull request #56)

## Context

Decision 0012 scoped planted-error practice and held it for Vishnu, after a research check found the evidence thinner than our notes said: the Fan & Chang (2026) paper measures how many planted errors undergraduates caught (about 54%), not an effect of practice; erroneous-example studies show small effects (g about .14) in younger learners and maths; nothing was found for 16 to 18 year olds, economics, or transfer to real AI output. The standing instruction since is to build it. So it is built, to the scoping rules, and **left off** until Vishnu approves it.

## Decision

Build exactly what 0012 scoped, with these concrete choices:
- Items come from the part's own mark points and misconceptions: no new content to author, and nothing exam-board is added. They are marked as not yet signed off by a teacher.
- 40% clean controls (**judgement call**; no study gives a ratio), one planted error, rotation, at most one a session, only on a part at developing or above, never while rushing.
- Scoring is deterministic on the server from four letters that are identical for every item, hits and false alarms apart, so "there is a mistake" alone and blanket suspicion earn nothing.
- Always labelled as practice; the correct statement is always given afterwards, naming the planted wrong idea and the right one (the misinformation-retention caution).
- The sentence the student named is checked by the server too, when the chatbot sends its number as `answer.choice` (found while auditing: letters alone let a tick stand for any sentence).
- Evidence on the part and on Verify as its own type (`ail_find_error`); it is not counted as checking a source, and activates no misconception.
- A shared two-line move (`say_line`) with the confidence question, so no instruction words are added (898 of 900).
- **Off by default** (`find_error.enabled = false`; `EDUX_FIND_ERROR=1` switches it on).

## Research basis

See 0012 for the checked evidence and its limits. In short: planted-error detection is low in adults (about 54% in Fan & Chang's undergraduates, about 15% in a chatbot study with adult learners); erroneous examples with error explanation give a small pooled effect (Alemdag, Eichelmann & Narciss, 2025, g = .136; McLaren, Adams & Mayer, 2015, delayed d = .33 in decimals); prior knowledge as a moderator conflicts (Große & Renkl, 2007; Heemsoth & Heinze, 2014 against Barbieri & Booth, 2016); generic warnings do not reduce reliance on false statements but per-item prompts do (Marsh & Fazio, 2006), hence the correction always follows. Signal-detection scoring is standard logic here, not a finding about learning. The design is defensible as a rare, low-risk exploratory activity; it is **not directly evidenced** for this age group or subject, and the pitch and white paper must say so.

## Alternatives considered

- **On by default.** Rejected: the evidence is thin and Vishnu's rule was to approve first.
- **Multiple-choice options for where the mistake is.** Recognition, not the production the design asks for, and it shows the sentences are candidates.
- **Generate items with a model.** Needs a teacher check and fluent-wrong risk; the pack's own content is safer.
- **A level for error detection.** Not shown as a level: counts only, as with the other literacy practice.

## Consequences

- Nothing changes for students until it is switched on. When on, a student occasionally sees one practice explanation at the end of a reply and a short correction after.
- The standard demo path is unchanged when off (checked); when on, the finished-part ending in the bridge run is replaced by the practice item, so the bridge check is skipped in that mode.
- No migration, no word-cap change. Result size: an item adds about 500 characters to a reply that is already near the 2,400 limit; reference blocks drop first.
- **Open:** a teacher must sign off items; log hits, misses and false alarms before making any claim.

## Verification

`tests/test_find_error.py` (29 tests): off by default; needs an answered part at developing or above; labelled; exactly one sentence swapped, or none; about 40% clean; the full scoring matrix; the letters; rare and rotating; not on literacy parts; the whole turn (recorded on the part and on Verify, misconception never activated, false alarm on a clean item). `scripts/check_mcp.py` (find_error_run) in both modes; rebuild identical.

## What would change our mind

A full read of Fan & Chang showing a real practice effect, or a pilot showing students at this level do not benefit; either would move it to dropped. Real use showing blanket suspicion or confusion with a real answer would mean rewriting the label.
