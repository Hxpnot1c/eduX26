# Gaming eduX's scoring rules (w5-06g)

Method: from security red-teaming and mechanism design. The scoring rules are treated as a mechanism. A student's
"payoff" is the displayed level (new / developing / secure). The aim is to find deviations from honest play that
pay more per minute of effort than honest play does.

Synthetic students play each strategy against the **real service layer**: `service.tutor_turn` with the labels an
honest chatbot would send, then `learner.part_p` / `service.my_progress` for what is displayed. The code under test
is a fresh copy of `/tmp/claude-1000/edux-05e-ff` with `sims/fixes/combined/0001–0005` applied. There are 30
students per strategy and 40 messages each, all in one session, starting 6 months before the exam.

**Every effort number and truth-model number is our choice** (`gaming_sim.py`, `EFFORT` and the truth constants).
The literacy skill rates come from `sims/literacy/lit_model.py` `TRUTH`, which were also our choice in wave 2. No
real students or data are involved. These are simulation results about how the rules behave, not learning results.

## Files
- `gaming_sim.py`: strategies, the honest-chatbot labeller (`literal` = ticks whatever the student's words contain;
  `skeptical` = doesn't tick what only repeats the chatbot's own reply), metrics and signals.
- `run_variant.sh <code copy> <label> [n] [turns]`: runs every strategy in its own process and writes
  `results/<label>/<strategy>-<labeller>.json.gz`. Set `ONLY=`/`ONLY_SK=` to run a subset.
- `summarise.py results/<label>`: writes `summary.md` and `summary.json`. The column meanings are in its docstring.
- `counters/c1.diff`, `c1s.diff`, `c2.diff`, `c12.diff`: the counters tested, as diffs of the fixed tree
  (`patch -p1` from the repo root).
- `check.sh <copy> <port> <out>`: the copy's own `scripts/check_mcp.py` on localhost. This is
  `combined/harness/check.sh` with the data path moved to `/tmp/claude-1000/w5-06g/`.
- `results/check_c{1,2,12}.txt`: check_mcp passes **74/74** on all three counter copies, with no expectation changed.
- `results/planA_c2.txt` and `results/planA/`: the Plan A takes from `sims/demo-05e/run_episode.py` on s5 and on c2.

## Strategies
| id | strategy |
|---|---|
| C0 | honest course student: reads each point (40 s), answers from true knowledge, writes real explain-backs, moves on after 2 re-teaches |
| C1 | never reads, answers every MCQ "A", switches topic at every explain-back |
| C2 | "I know this", picks the longest option, switches topic at explain-back |
| C2m | as C2, but drops the longest and shortest options and guesses among the rest |
| C3 | "just show me", then picks the option that repeats the point just shown; at explain-back says "just show me" again (once the part is secure, moves to the next part) |
| C4 | honest teaching, but the explain-back is the chatbot's own text pasted back |
| C5 | knows half of each part; answers only when sure, otherwise switches topic (dodge) |
| L0 / L0s | honest research student, partial / strong skill |
| L1 | 2-feature template question; every verify task gets "the link is broken" |
| L1d | as L1, adding the publisher and date copied from the chatbot's citation |
| L2 | restates the chatbot's answer as the verify-task answer |
| L3 | restates the answer as an unprompted check after every research answer |
| L4 | pastes a 4-feature template question, ignores tasks |
| L5 | vague questions with 0 features, ignores tasks |
| L6 | honest questions, ignores every task and check |

## Headline results (fixed tree; `results/base/summary.md`)
| strategy | effort (min) | shown at the end | false-secure | to first secure | what exposes it |
|---|---|---|---|---|---|
| C0 honest | 40.8 | 4.1/9 parts secure, all truly known | – | 2.4 min | – |
| **C3 show me + match** | 6.7 | **9/9 parts secure** (6 still secure at +7 days) | 100% | 0.5 min | `trends.just_show_me` recent 0.40 (shown, no flag) |
| C2m middle-length cue | 4.3 | 4.4 parts secure, 58% of MCQs right (chance about 31%) | 100% | 0.3 min | nothing |
| C2 longest option | 4.2 | 1 part secure (ped_values for 30/30, whose key is its longest option); 14% of MCQs right | 100% | 1.3 min | nothing |
| C1 always "A" | 4.0 | 0.8 parts secure | 53% of students | 1.6 min | top-letter share 1.0 (logged, not shown) |
| C5 selective / dodge | 14.9 | 2.0 parts secure; 42% of them have points the student doesn't know | 13% (a part under half known) | 2.8 min | nothing: 26 dodges per student, none recorded |
| C4 copy explain-back | 30.7 | 3.8 parts (literal labeller) vs 0.6 (skeptical) | – | 1.6 min | nothing |
| L0 honest partial | 52.2 | Verify secure in 53% of students, Ask in 47% | – | 18.7 min (V) | – |
| **L1 "link is broken"** | 8.6 | **Verify secure in 100%** | 100% | **0.8 min (V)** | source_conflict count 11 (logged, not shown) |
| L2 / L3 restate | 12–13 | Verify secure 100% (literal), 0% (skeptical) | 100% / 0% | 1.3 min | nothing |
| L4 4-feature template | 10.0 | Ask secure 100% | 100% | – | all-4-features share 1.0 in question_features |
| L5 vague | 6.7 | nothing gained | 0 | – | – |
| L6 ignore all | 30.0 | nothing gained | – | – | **skipped.verify 0.57 for about 34 ignored tasks** |

Gain per effort-minute (displayed level steps): C0 0.22, C3 2.70, C2m 2.38, C1 0.93; L0 0.06, L1 0.25, L4 0.20.

## Counters tested (`results/<label>/summary.md`)
| counter | change | gamer effect | honest cost | check_mcp |
|---|---|---|---|---|
| **c1** (rule) | `learner.py`: evidence scored as `immediate` (straight after a worked example or hint) can't raise p_known past `levels.secure - 0.01` (or above where it already was) | C3 9 → **0** parts; C2m 4.4 → 2.1; C1 false-secure 53% → 23%; C5 2.0 → 0.6 parts | C0 4.1 → 1.3 parts secure in session; first secure 2.4 → 12.3 min; at +7 days 2.9 → 0.6 | 74/74 |
| c1s (setting) | `immediate.guess` 0.30 → 0.60 | C3 9 → 7 parts: **not enough** | C0 4.1 → 2.5 | not run |
| **c2** (rule) | `learner.found_problem`: a report counts as opening the source and saying whether it matched (points 1 and 4); anything else found is ticked as usual; a bare report with nothing more is **no evidence** (the task closes, and the exchange is still logged with source_conflict) | L1 Verify secure 100% → **0%**; L1d 100% (literal) → 0% (skeptical, needs the text line) | L0 Verify secure 53% → 47% (noise at N=30 is about ±18 points) | 74/74 |
| text (not code) | tutor_turn.md: tick a verify point only for what the student found on the source itself, never for what repeats your reply or its citation | modelled by the skeptical labeller: L2/L3 100% → 0%, L1d 100% → 0% under c2 | none modelled | – |
| c12 | c1 + c2 | the c1 and c2 rows combined (`results/c12`) | as above | 74/74 |

**Residual after c12:** guessers still gain more level steps per minute than honest students (C1 0.76, C2m 1.74,
C0 0.15). That gain is now mostly "developing", not "secure". So "cheap tricks no longer reach secure" is true and
"gaming-proof" is not.

Plan A under c1: all six takes (final, then_ped, recommended, plan_now, final_ticks_ad, clean) are unchanged, with
identical steps, levels and p_now (`results/planA_c1.txt`).

**With wave-5 patches:** `c1.diff` and `c2.diff` both apply cleanly (with offsets) on top of `combined/0001–0006c`
(dry-run). 0006b adds a `points_met` labelling rule (tick a for "wouldn't load", d for a verdict). That matches
c2's automatic points 1 and 4, so a bare report is still no evidence. Append the "not what repeats your reply"
sentence to that bullet.

Plan A under c2: the `final` and `recommended` takes (the 4c line says what the page shows, answer a,c,d) still end
Verify **developing** (0.636, was 0.748). The `clean` take (a bare "the page doesn't exist") now ends **new**, so use
the `final` wording.

## Caveats
- C3's 100% hit rate is an upper bound. It assumes the chatbot shows the point near-verbatim (`show.md` asks for
  data.point "with one short worked line"). A paraphrase lowers it.
- Effort weights are our choice. Scaling every weight by the same factor leaves the honest-vs-gamer ratios
  unchanged. Only the ordering of very different actions, such as a real 3-minute check against an 8-second claim,
  matters, and that gap is large.
- One session only. The decay figures at +1.5 and +7 days assume no further study.
- The literal and skeptical labellers bracket real chatbots. We did not test what Claude or ChatGPT actually ticks.
