# Demo script

A walkthrough for the demo video: which student and which question show each feature. It assumes `scripts/demo.sh` is running against `example-mini` and each demo student is connected in its own chat (or chatbot account) with the set-up text pasted in.

All questions below are written by us in the style of Pearson Edexcel A level Economics A (9EC0) data and short-answer questions. They are not taken from Pearson's papers, and no Pearson text appears in the video (the papers are © Pearson Education Limited). Where a real paper is mentioned, mention it by reference only (for example "the kind of short calculation set on Paper 1, Markets and business behaviour").

## What changed on 19 November (read this before you film)
The demo path has these differences from the earlier script. Each is on a pull request; none is merged yet.
- **"How sure are you?" (step 05z, decision 0027).** Asked only on the *second rapid-guess answer in a row* to a check, review or prerequisite check (answered faster than the question can be read, which needs the chatbot to send the word count), and at most once a session. The chatbot asks "How sure are you: guess, fairly sure or certain? (You can skip this.)" and gives the feedback on the next message; the break offer for rushing then waits until a later answer is rushed again. At normal speed it never appears in the takes below. Skip it by saying "skip", or turn it off for filming with `EDUX_CONFIDENCE=0` on the server. The progress view shows a calibration line only after 5 rated answers in a level, so it will not appear in a short take.
- **"Taught in class" (step 05q).** The demo class has covered the first two Theme 1 concepts (PED, PES), so parts the student has not answered on show "taught in class, not yet checked" in `get_my_progress`, never "developing" or "secure". `state --student …` marks covered parts with `*`.
- **A bridge question (step 05t).** When a part finishes, the reply can end with a short lead-in question on a linked, untaught part ("this links to what's next in class"), then a teaching step that says they can stop or switch.
- **Study pattern is gone (step 05s).** Section 5 no longer says "your answers drop after about 35 minutes": that line came from a rule our own simulation found unreliable.
- **Personalisation is off by default (step 05m)** and find-the-error practice is built but off (`EDUX_FIND_ERROR=1` to show it; say on camera that it is untested at this age).
- **Film with web search off.** Plan A was **re-run on 19 November against the full stack** (the overnight `run_episode.py`, all six scenarios, with one line changed in the harness copy because it read the plaintext key that step 05x removed): Verify ends at **0.740, "developing"**, the same as the overnight run, Ask at 0.528, and no result went over budget. The margin below "secure" (0.75) is **0.01**, so do not add a Verify task to the take; re-run before filming if anything in `settings.toml` changes.

- **Two open questions after every multiple-choice question (decision 0028).** After any lettered question, the next two questions are written ones: a point check asks you to explain that point in your own words, and a review asks you to recall it. So in section 2, the check after the pre-question is written; in section 4, the first review is lettered and the next two are written recall questions. While rushing, lettered questions come straight away. Set `EDUX_QUESTION_GAP=0` on the server to film the old all-lettered flow.

## The web pages (new: about 3 minutes, optional)
Synapse now has three pages beside the chatbot connector, served by the same server. They are on pull requests #72 to #77 and are not merged. See [step 09](build/steps/09-web.md).
1. **Seed with a class:** `python -m edux.cli seed-demo --reset --pupils 8`, then `python -m edux.cli teacher add --name "Ms Demo"` and `python -m edux.cli teacher assign --teacher <id> --class demo-class`. The 8 pupils are synthetic and the page says so.
2. **The course map** at `/map` needs no sign-in for the example pack. Show the three views (Map, Path, List), then select PED: formula and calculation: its detail shows what it needs first and what it is related to, and links are drawn only for the part you are on. Say: "colour will mean one thing only: how well a part is known."
3. **A student's page** at `/me#key=<demo-weak key>`: the same map coloured by what they have practised (dashed ring: taught in class, not yet checked; a marked disc: needs review, got right before and fading; fainter: longer since last answered), what to do next, what is ready for a check and why, the mock coming up with a plan, and what is recorded about them and how to have it deleted. Say: "no score, no rank, no streak: levels with the evidence behind them."
4. **A teacher's page** at `/teacher#key=<teacher key>`: the class map in bands, never a count per level; common wrong ideas held by five or more students; the help-seeking pattern with its caution; and the "what this page does not show" list. Say: "teachers see a class, never one student, and nothing under five."
5. **Sign-in:** the key is in the link's fragment, which a browser never sends to a server, and the page forgets it when the tab closes.
- Say on camera that the dashboards are **not shown to improve outcomes** (Kaliisa et al., 2023), that the teacher view is a first version, and that the class data is **seeded, synthetic**.
- Not yet done: a screen-reader or keyboard-only walkthrough by a person, and a check on a phone (the layout was checked at 390 px in a desktop browser only).

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
| demo-weak | no question on the formula; first checks what PED means with one quick question. Once they answer: feedback, then corrects "divide the change in price by the change in quantity demanded to get PED" | `check_prereq`, then `feedback` (with the held misconception) |
| demo-showme | asks the question first, unless they've said "just show me" this session; has reviews booked from earlier "just show me" turns | `prequestion` |

Optionally show the plans side by side (`python -m edux.cli context --student <id> --message "..."` shows the blocks they're built from) to make the difference explicit.

## 2. Pre-question and misconception correction (demo-secure, about 1 minute)
1. The chatbot asks the multiple-choice question about the PED formula. Answer with the wrong option **"Divide the change in price by the change in quantity demanded to get PED"**.
2. The answer reaches the server at the start of that reply, so the plan is `feedback` then `teach`. The chatbot names that wrong idea, says why it's wrong (quantity goes on top, and it uses percentage changes), then gives a short worked example. It closes with "try this one, or ask for a hint", rather than offering a choice after showing everything.
3. In the terminal, `state --student demo-secure`: the target now has evidence and the misconception is active. Ask the same question again: no pre-question this time.

## 3. Worked example, then explain-back (demo-weak, about 2 minutes)
1. After the worked example, ask the chatbot to set one. Use this question:

   > **Question (2 marks).** The price of a cinema ticket rises from £8.00 to £10.00 and weekly ticket sales fall from 500 to 450. Calculate the price elasticity of demand for cinema tickets.

   The answer: quantity −10%, price +25%, so PED = −0.4 (inelastic).
2. Answer correctly, then say "I've got it". The chatbot should ask for the idea in your own words.
3. Give an explanation that misses one point, e.g. "you divide the change in quantity by the change in price". The chatbot ticks the points you made, and the server scores them (points met / points). The plan is `feedback` then `reteach` with only the missing point: the chatbot says what was good, re-teaches just the missing point and asks you to try again.

## 4. Reviews: recall and transfer (demo-secure, about 1 minute)
Ask **"Quiz me on what's due"** (the `review_due` prompt). Each answer gets its feedback at once ("how sure are you?" comes only after rapid guesses). Three reviews are due:
- `tax_incidence_split`, needs review (answered right once, now below `levels.new`): a **recall** question ("who bears an indirect tax, and what decides the split?")
- `tax_supply_shift`, developing after several right answers, now due: a **transfer** question
- `pes_definition`, developing: a **transfer** question in a new context, e.g. a linked idea from the graph

Whether the answer is right or wrong, the feedback should explain why.

### 4b. A review picked for a test (demo-weak, about 30 seconds)
The seed gives demo-weak a mock in 5 days on the market-failure topic, and one part of it answered 8 days ago, so it is due now.
1. In demo-weak's chat, ask **"Quiz me on what's due"**. The review is on that part, and the chatbot says it's for the mock, e.g. "Quick review of shifting supply, for your mock on Monday".
2. Say on camera: **"Synapse knows this student has a mock on Monday, so of what's due it picks what the mock covers and the student is weakest on, and says why. It never makes something due just because a test is coming: no cramming."**
3. Optionally, in the terminal, `state --student demo-weak` lists the mock and the top candidates with their values.

## 5. Offloading and study pattern (demo-showme, about 1.5 minutes)
1. Ask about interpreting PED values, and when offered the choice say **"just show me"**. The chatbot labels the message `just_show_me`, and the plan is a single `show` step: a short worked example and nothing else.
2. Ask the PED calculation question again: no pre-question now, because they chose "just show me" this session.
3. Ask **"How am I doing?"** (`get_my_progress`). It should mention:
   - asking to be shown answers more often recently (`trends.just_show_me: up`)
   - reviews due on the parts they were shown
   - the AI-literacy levels *with the evidence behind them* ("from N checks over D days: practice feedback, not a grade")
   - parts the class covered but they haven't answered on, as "taught in class, not yet checked"

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
