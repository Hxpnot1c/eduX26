# Demo script

A walkthrough for the demo video: which student and which question show each feature. It assumes `scripts/demo.sh` is running against `example-mini` and each demo student is connected in its own chat (or chatbot account) with the set-up text pasted in.

All questions below are written by us in the style of A-level Economics data and short-answer questions. They are not taken from any exam board's papers, and no exam-board text appears in the video. Where a real paper is mentioned, mention it by reference only (for example "the kind of short calculation set on Paper 1").

## Before recording
- Run `scripts/demo.sh` and note the roles it prints. On `example-mini` they are:
  - target `ped_formula`
  - prereq `ped_definition`
  - misconception `ped_formula_m1`
  - anchor `pes_formula`
  - confusable `yed_definition`

  On another pack, swap in the parts it prints.
- Reseed shortly before recording. The histories are dated back from the moment of seeding, and the keys stay the same.
- Keep a terminal open for `python -m edux.cli state --student <id>`, to show the record changing after a turn, and for `python -m edux.cli calls`, to show the server's time per turn.
- Each reply should come from one `tutor_turn` call, with a plan of one or two steps, and be about 120 words or fewer.

## 1. Same question, three students (the main point, about 2 minutes)
Ask each student, in their own chat: **"How do I calculate price elasticity of demand?"**

| student | what the chatbot should do | plan |
|---|---|---|
| demo-secure | asks a multiple-choice question first and nothing else | `prequestion` |
| demo-weak | no question on the formula; first checks what PED means with one quick question. Once they answer: feedback, then corrects "divide the change in price by the change in quantity" | `check_prereq`, then `feedback` (with the held misconception) |
| demo-showme | asks the question first, unless they've said "just show me" this session; has reviews booked from earlier "just show me" turns | `prequestion` |

Optionally show the plans side by side (`python -m edux.cli context --student <id> --message "..."` shows the blocks they're built from) to make the difference explicit.

## 2. Pre-question and misconception correction (demo-secure, about 1 minute)
1. The chatbot asks the multiple-choice question about the PED formula. Answer with the wrong option **"Divide the change in price by the change in quantity"**.
2. The answer reaches the server at the start of that reply, so the plan is `feedback` then `teach`. The chatbot names that wrong idea, says why it's wrong (quantity goes on top, and it uses percentage changes), then gives a short worked example. It closes with "try this one, or ask for a hint", rather than offering a choice after showing everything.
3. In the terminal, `state --student demo-secure`: the target now has evidence and the misconception is active. Ask the same question again: no pre-question this time.

## 3. Worked example, then explain-back (demo-weak, about 2 minutes)
1. After the worked example, ask the chatbot to set one. Use this question:

   > **Question (2 marks).** The price of a cinema ticket rises from £8.00 to £10.00 and weekly ticket sales fall from 500 to 450. Calculate the price elasticity of demand for cinema tickets.

   The answer: quantity −10%, price +25%, so PED = −0.4 (inelastic).
2. Answer correctly, then say "I've got it". The chatbot should ask for the idea in your own words.
3. Give an explanation that misses one point, e.g. "you divide the change in quantity by the change in price". The chatbot ticks the points you made, and the server scores them (points met / points). The plan is `feedback` then `reteach` with only the missing point: the chatbot says what was good, re-teaches just the missing point and asks you to try again.

## 4. Reviews: recall and transfer (demo-secure, about 1 minute)
Ask **"Quiz me on what's due"** (the `review_due` prompt). Three reviews are due:
- `tax_incidence_split`, weak: a **recall** question ("who bears an indirect tax, and what decides the split?")
- `pes_definition` and `tax_supply_shift`, developing: **transfer** questions in a new context, e.g. a linked idea from the graph

Whether the answer is right or wrong, the feedback should explain why.

## 5. Offloading and study pattern (demo-showme, about 1.5 minutes)
1. Ask about interpreting PED values, and when offered the choice say **"just show me"**. The chatbot labels the message `just_show_me`, and the plan is a single `show` step: a short worked example and nothing else.
2. Ask the PED calculation question again: no pre-question now, because they chose "just show me" this session.
3. Ask **"How am I doing?"** (`get_my_progress`). It should mention:
   - asking to be shown answers more often recently (`trends.just_show_me: up`)
   - "your answers tend to drop after about 35 minutes of studying" (`study_pattern`)
   - reviews due on the parts they were shown

## 6. Harder question when earned (any student, about 1 minute)
On a part they're developing on, answer a question correctly. A later turn's plan adds an `extend` step after the teaching step, and the chatbot asks one harder question:

> **Question (4 marks).** Using the idea of price elasticity of demand, explain why a cinema might raise revenue by cutting ticket prices on weekday mornings but not on Saturday evenings.

## 7. Context profiles (terminal plus any student, about 30 seconds)
```bash
python -m edux.cli set-profile --student demo-weak --profile minimal
```
Ask the same PED question: the chatbot now gets only the focus and notes, with no plan, and teaches generically. Switch back with `--profile default`.

## Checks before publishing the video
- No exam-board question or mark-scheme text on screen. The `example-mini` questions are labelled synthetic.
- No real student data. Only the three demo students.
- Keys aren't readable on screen. Blur them, or after recording delete `learner.db` and reseed to get new keys (`seed-demo --reset` keeps the old ones).
