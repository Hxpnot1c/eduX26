# Label-agreement analysis (02a protocol)

`analyse.py` runs the analysis plan in [02a](../../02a-label-agreement-protocol.md) §1.4, §1.6 and §1.8 on a `decisions.csv`. It is stdlib Python. It extends `agree.py` from 02a Appendix C, which it replaces.

> **The only real-looking numbers this script has produced so far are a dry run: proxy vs key.**
> - The key (02a Appendix B) was drafted by a Claude model.
> - The proxy labeller (w5-02r) is a Claude model.
>
> So that run is a pipeline test and a rubric-ambiguity audit, **not agreement evidence**. The script prints a warning whenever the only raters are `key` and `proxy`. See `../../work/w5/w5-02s.md`.

## Wednesday: how to run it

1. Collect the labels into `decisions.csv`, one row per decision: `msg_id,label,unit,rater,value`.
   - **Labels:** `ask_feature`, `answer_point`, `misconception`, `request_type`, `depth`, `engagement`, `asks_recent`, `source_conflict`, `choice`.
   - **Units:**
     - `concept`, `context`, `asks_sources`, `asks_reasoning` for `ask_feature`;
     - `a`–`d` (V items) or `a`–`c` (E items) for `answer_point`;
     - the candidate misconception id for `misconception`, one row per id **listed in the item's context**, 0 or 1;
     - `-` for all other labels.
   - **Raters:** `B`, `C`, `consensus`, `bot1`, `bot2`.
   - **Values:** `0`/`1` for binary labels (yes/no/true/false also accepted). For the others, the category name (`surface`, `active`, `research`, `none` …).
   - **Blank cells (or `NA`) are missing, never 0.** Leave a cell blank when a bot call failed or a rater skipped a decision. The script counts it, and the flow table shows a **!** against the expected n.
   - **Consensus:** enter `consensus` rows only for the adjudicated B–C disagreements if you like. Wherever B equals C and no consensus row exists, the script fills consensus = B, and says how many it filled.
   - **Bot says non-research on an R item:** the bot then sends no features. Leave its feature and `asks_recent` rows out. The script scores them 0, because that is what the server records, and says how many it scored.
   - **Values are checked.** A typo stops the run with the line, msg_id, label, rater and value. For example, `surfce` gives "allowed: surface, mechanism, transfer". Case is ignored.
2. Run it, once after the B/C labels and again after adjudication:

   ```
   python3 analyse.py decisions.csv > results.md
   ```

   Missing raters are skipped. Before adjudication you get B–C only. Run time is about 1 s.
3. Options:
   - `--pairs B-C,bot1-consensus,...` sets the test–reference pairs.
   - `--ask-min 2,3` sets the `ask_min_features` thresholds for the server-level table. 2 is the current setting; 3 is the build-list proposal.
   - `--reps 2000` sets the number of bootstrap resamples.

## What it prints

| Section | 02a reference | Contents |
|---|---|---|
| Notes and flow | Table 1 | Missing values, filled consensus, bot features scored 0; then decisions per label and rater against the expected n (72, 56, 12, 40, 40, 40, 18, 8, 40) |
| Headline binary decisions | Table 2 | Ask features (72 decisions), and answer scoring (56) split into Verify ticks (32) and explain-back points (24). For each: prevalence, % agreement, κ with a 95% cluster-bootstrap CI over messages, the number of resamples where κ was undefined (dropped), AC1, sensitivity and specificity (first rater = test, second = reference) and the 2×2 cells |
| Verdict | §1.6 | Needs B, C, consensus and bot1. Applies the ceiling check, the pass rule (κ ≥ .60, lower bound ≥ .40, mean of bot–B and bot–C within .10 of B–C), the strong band and the specificity guard (< .80) |
| Per feature / tick / point | Table 4 | Descriptive counts, κ and AC1 |
| Secondary labels | Table 3 | `request_type` (Cohen κ), `depth` and `engagement` (unweighted κ, plus quadratic-weighted κ with a CI); confusion matrices |
| Krippendorff's α | §1.4 | Across B, C and bot1: nominal for binary labels and `request_type`, ordinal for `depth` and `engagement` |
| Rare labels | §1.4 | `asks_recent`, `source_conflict`, `misconception`, `choice`: counts, % agreement, AC1 |
| Server-level outcome | Table 5 | Ask score 0–4 per R message (weighted κ; same side of each threshold) and Verify tick count per V answer |
| Disagreements | Tables 6–7 | Every disagreement for the first two pairs. Use them for adjudication and the key-vs-consensus table |

**Scope rules** (from 02a §1.2):
- Rows outside a label's message block are dropped and counted, e.g. `ask_feature` on an E item. P1–P3 are always dropped.
- `web_access`, `conflict_flagged` and `pushback_changed` are not analysed.

## Other modes

- `python3 analyse.py --dryrun [--write-csv F]` builds proxy-vs-key decisions from `work/w5/w5-02r-labels.md` (JSON) and 02a Appendix B, then analyses them. It also prints how often disagreements fall on decisions the proxy marked unsure or the key marked `*`, and lists every disagreement with the proxy's notes. The default CSV path is `/tmp/claude-1000/w5-02s/dryrun_decisions.csv`.
  - **Hand-mapped:** the key's notes column was mapped to specific decisions in `KEY_NOTE_FLAGS`.
  - **Rerun on the rewritten messages:** update that map and the Appendix A/B blocks first.
- `python3 analyse.py --synth F` writes a **synthetic** five-rater file. It flips the key at random (seed 7). Use it only to test the B/C/consensus/bot1/bot2 code paths. The numbers mean nothing.

## What has been tested (18 Nov 2026)

All of the tests below used throwaway files in `/tmp/claude-1000/w5-02s/`.

- **End to end:**
  - `--dryrun` (two raters).
  - `--synth`, then the full report on the synthetic five-rater file: all five pairs, α, Table 5 and the disagreement lists.
  - A "Wednesday-like" file, made from the synthetic one with these changes:
    - consensus rows only where B ≠ C;
    - four blank bot2 ticks;
    - bot1 labelling R02 as `Concept` (capitalised) with no feature rows.
    - The notes, the consensus fill, the 0-scoring and the flow-table **!** all worked.
  - A typo file. It stopped with the expected message.
  - Both `/usr/bin/python3` and `/home/vishnu/edux26/.venv/bin/python` ran it.
- **Verdict branches that fired:** "CEILING FAILS", "FAIL" and "STRONG" (bot1 set equal to consensus).
  - PASS uses the same conditions as STRONG, but with κ < .80. It wasn't hit by a test file.
  - Note that the ceiling test compares unrounded κs, so a printed ".68 vs .78" can fail by a rounding hair.
- **Checked against references:**
  - Quadratic-weighted κ matches scikit-learn's `cohen_kappa_score` (dry-run `depth`: .8819 both).
  - Krippendorff's α reproduces the textbook examples: two-rater nominal .095; the four-observer, 12-unit example with missing data, nominal .743 and ordinal .815.
- **Not checked against an outside implementation:** AC1 (q = the label's full category set), and the percentile bootstrap. The bootstrap is Appendix C's, plus a count of undefined resamples.
- **Not implemented:** Fleiss' κ. α is the three-rater statistic.

## Known limits

- **Percentile bootstrap with few messages.** Verify has only 8 messages, so its CI is rough. When every resample is identical, κ can be undefined; the "NaN resamples" column counts these.
- **Explain-back points are pooled with Verify ticks** in the headline row, as the protocol specifies. Read the Verify-only row before saying "Verify labels agree".
- **`request_type` on V items** has no defined right answer in the tool text yet (02a Appendix B note). Expect it to pull `request_type` κ down until the definition is fixed.
