# Step 05j: Reply length follows mastery, diagrams follow content

Branch `build/reply-style`.

## What
1. **Reply length follows mastery.** `style.max_words` (or the student's saved `answer_length`) stays the ceiling for the session. Each step gets its own word target, sent as `data.max_words` only when it's below the ceiling:
   - a new point: the ceiling (nothing sent);
   - a review or check (`ask_mcq` with purpose `check`, `review` or `prereq`) on a part at developing or above: `style.length_known_share` (0.5) of the ceiling;
   - every step while the fatigue signal is on: `style.length_fatigued_share` (0.4).
2. **The student's own request always wins.** When they ask for shorter or more detailed replies, the chatbot calls `update_my_profile(answer_length=…)`. From then on nothing is shrunk for that student, and `teach_point`'s word budget becomes their length.
3. **A `diagram` flag per part.** It's an optional `diagram` column in `nodes.csv` (`true` / `false`, default `false`).
   - Steps on a diagram part carry `data.diagram: true`.
   - The first one on each part gets a short cue line: draw a labelled diagram if the interface can show one, otherwise have the student sketch it, saying which curve moves, which way, and what happens to price and quantity.

## Why, with sources
- **Expertise reversal effect** (Kalyuga et al., 2003). Full explanations help novices but slow down students who already know the material, so reviews and checks on known parts get shorter replies.
- **Diagrams follow the content, never the student.** Matching format to a student's "learning style" has no good evidence (Pashler et al., 2008). There is no per-student "visual learner" setting, and the docs don't describe the flag that way.
- **The student sketches, then explains.** When the interface can't show a diagram, the cue has the student sketch it and say which curve moves, which way, and what happens to price and quantity (Leutner & Biele, 2025, *Educational Psychology Review* 37, https://doi.org/10.1007/s10648-025-10067-7). That source supports the sketch-and-explain part only; the chatbot drawing the diagram isn't claimed from it.

## Files
- `ingest/registry.py`, `edux/content_schema.sql`: the `diagram` column, validated as `true` / `false`.
- `edux/graph.py`: `is_diagram`.
- `coursepacks/example-mini/nodes.csv`: `diagram = true` on `tax_supply_shift` (the supply shift), `tax_incidence_split` (the tax wedge) and `externality_tax_eval` (externalities). The AI-literacy mini pack has no diagram content, so it keeps the column out; it is optional.
- `edux/service.py`: `reply_style`, applied to the final plan.
- `text/style.md`: "Keep each step under data.max_words, else the reply under style.max_words…" (one word shorter).
- `text/cues/diagram.md`: the diagram cue line. It is not a move section, so the instructions don't grow.
- `text/tools/update_my_profile.md`: set `answer_length` when the student asks for shorter or longer replies.
- `scripts/check_mcp.py`: a `reply_style` run.

## Settings
```toml
[style]
max_words = 120
length_known_share = 0.5
length_fatigued_share = 0.4
```

## Done when
- A review on a secure part carries `max_words` at about half the ceiling.
- A fatigued turn carries the fatigued share.
- With `answer_length` set, no step carries a smaller `max_words`.
- A step on a `diagram` part carries `diagram: true`, and a step on another part doesn't.
- Results stay under 2,400 characters, and the instructions stay at or under 900 words (894).

## Tests
All in `scripts/check_mcp.py` (`reply_style`):
- the length rules are checked on steps built in-process, for demo-secure and a throwaway student;
- the diagram flag is checked end to end through `tutor_turn`.
