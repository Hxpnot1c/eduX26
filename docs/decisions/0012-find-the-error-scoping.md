# 0012. Find-the-error practice: scoping (Part 2 G), not built

- **Status:** Held (scoped; build only when Vishnu approves it as Part 2 G, after F and the audit items, before the C7 stretch)
- **Date:** 2026-11-19
- **Decision owner:** Vishnu
- **Pull request:** #56 (this record only)
- **Audit item:** C9 in [0002](0002-research-alignment-register.md)

## Context

The research review says the field's main gap is measuring whether a student can tell a wrong claim from a right one when an AI states both fluently (seeded errors with clean controls; appropriate reliance). Synapse today measures source-checking behaviour and why chatbots fail, not error detection. The team asked for planted false claims to be built if the research backs them. This record checks the evidence, scopes the feature, and says what it would cost. **It does not build it.** The evidence is thinner than our own notes claimed, and Vishnu's decision of 18 November is to scope first.

## What the evidence shows, after checking

A research pass on 19 November (search results and abstracts; very little full text) found:

- **The Fan & Chang (2026) citation did not say what `research.md` said it did.** The paper exists: Fan, M. & Chang, P. (2026), "Telling Students to Evaluate Does Not Make It Happen: Task Stage, Offloading Tendency, and Error Detection in AI-Assisted Student Writing", *Behavioral Sciences* 16(9), 1671, DOI 10.3390/bs16091671. It planted 12 errors in AI-assisted writing; students caught about 54% of them, and being told to evaluate did not make it happen. A figure of 0.35 appears in a contrast table but we could not tell what it measures. It is **not** an effect of planted-error practice on learning. `research.md` is corrected in this pull request, and no effect size is claimed.
- **Erroneous examples** (worked examples that contain an error for the learner to find) have a small positive pooled effect: Alemdag, Eichelmann & Narciss (2025, *Review of Educational Research*; 42 papers, 177 effect sizes) g = .136, larger when the errors are explained or self-explained (abstract only). McLaren, Adams & Mayer (2015; 390 middle schoolers, decimals) found no immediate gain but a delayed gain (d = .33 on gain scores), and students liked the format less. Booth et al. (2013) found incorrect examples helped conceptual understanding in algebra (abstract only).
- **Prior knowledge as a moderator conflicts:** Große & Renkl (2007) and Heemsoth & Heinze (2014) found benefits mainly for higher prior knowledge; Barbieri & Booth (2016) found them for lower prior knowledge; Durkin & Rittle-Johnson (2012) found no interaction.
- **People miss planted errors in AI output:** about 15% reported in a chatbot study with adult learners (a press release only), about 54% in Fan & Chang, a quarter of 30 engineering students catching none of three planted errors. All are undergraduate or adult samples. We found **no study of 16 to 18 year olds, of economics, or of whether error-spotting training transfers to real AI output.**
- **Risk of learning the error:** generic warnings did not reduce reliance on false statements in readers, while per-item "is there an error?" prompts did (Marsh & Fazio, 2006, abstract only), and highlighted errors can sometimes backfire (Eslick, Fazio & Marsh, 2011). So the correct statement must always follow the answer.
- **No evidence** on the right share of clean controls, on one error per item, on whether blanket suspicion is rewarded in learning tasks (signal-detection logic says it is unless clean items and false alarms are scored), or on whether the practice label changes outcomes.

**Reading.** The design is defensible as a **rare, low-risk, exploratory practice activity with strong scaffolding**, scored with signal-detection logic. It is **not directly evidenced** for this age group or subject, and the pitch and white paper must say "untested for A-level Economics", not cite an effect size.

## Proposed design (to approve, not built)

- **Always labelled as practice:** "This answer may contain one mistake, or none." Never presented as the chatbot's real answer.
- **Items** built from the pack's existing `misconceptions.csv`: a short correct explanation of a part, with one sentence swapped for that part's misconception; the clean control is the same explanation unswapped. Marked "not yet signed off by a teacher".
- **One planted error per item,** about one idea. **Clean controls: 30 to 50% of items** (a **judgement call, starting value**; no source gives a ratio). Rotated forms so a student does not see the same item twice.
- **Scoring (server side, from the student's structured reply, not the chatbot's labels):** on an error item, the student must say where the error is and what is right (hit); naming the wrong place or saying "no error" is a miss. On a clean item, "no error" scores (correct rejection); naming an error is a false alarm. "There's a mistake" alone scores nothing. Hits and false alarms are recorded separately so sensitivity can be reported.
- **Always show the correct statement afterwards,** with a one-line why (self-explanation of the error mattered in the meta-analysis). Never leave the planted error uncorrected.
- **Evidence:** for the economics part (doubling as refutation of the misconception), and for Verify as its **own evidence type** (`find_error` already exists in `settings.toml` with slip 0.15 and guess 0.25, but has no producer), so it does not inflate Verify from real moments. Not shown as a level on its own; counts and trends only.
- **Rare:** at most one per session, only on a part at developing or above (so the student has seen a correct version first), never in long-session or rushing mode.
- **Cost:** a new move section (about 30 words) in the server instructions, which are at 899 of 900. It needs cuts elsewhere first, and only if that fails a rise to 950 with the reason in `settings.md`.
- **Settings:** `find_error.clean_share` (0.4), `find_error.max_per_session` (1), `find_error.min_level` (developing), each labelled.
- **Tests:** the scoring matrix (hit, miss, false alarm, correct rejection, "there's a mistake" alone); the once-per-session and level limits; rotation; a clean item is a true copy of the explanation; no item in long-session mode; rebuild identical.
- **Demo moment:** one item on a developing part for `demo-secure`, with the practice label on screen.
- **Open before building:** who signs off the items (a teacher); whether to write items by hand (about a dozen to start) or generate and check them; the migration for item and attempt records.

## Alternatives considered

- **Build it now.** Rejected: the evidence is weak and the instructions have one word spare; the 18 November decisions say scope first.
- **Use real chatbot mistakes** (the existing Verify moments) only. They are uncontrolled, rare and not clean controls, which is why the review recommends planted items.
- **Drop it.** Rejected: it is the strongest research-backed gap in the product, and the cost is moderate.

## Consequences

Nothing changes in the product from this record. The white paper should describe error detection as planned and untested, not as a result.

## Verification

Not applicable until built.

## What would change our mind

A full-text read of Fan & Chang that shows a real effect of practice, or a pilot showing students at this level do not benefit; either would move this to "held" or "drop".
