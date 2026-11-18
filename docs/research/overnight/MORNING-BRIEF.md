# Morning brief (after wave 2)

**Needs a human:** paste the Challenge 1 brief from the EduX site into `challenge-brief.md`.

## Wednesday: five things, ranked
1. **Merge 05e, fix three bugs, pass the 18:00 gate.** Clamp `p_known` (divide-by-zero crash), break the step-back loop, route "quiz me on what's due" to reviews; then a claude.ai dry run. M. Build lead. ([06](06-settings-simulation.md) recs 1–3)
2. **Fix the give-away MCQs and the content error.** Full-sentence options, matched lengths, no absolute words; fix `externality_tax_eval_m1`. S. An economist. ([04](04-economics-education.md) recs 1–2)
3. **Literacy fixes (branch).** `ask_min_features = 3`, `ail_question` guess .30, `ail_unprompted` .20. Rewrite options without m2. Show How AI works as per-part counts. Ignored tasks = missing. S each. Build team. ([02](02-ai-literacy-assessment.md) recs 2–4, 6)
4. **Film Plan A, web search off.** Teach "a cited source may not exist, or may not say what was claimed"; end on the How AI works counts. Adult-account caption. M. Two people. ([demo-plan](demo-plan.md) recs 12–13)
5. **Build the deck.** Lead with AI-literacy evidence from real use; a school-owned learner model across chatbots is a head start, not a moat. S–M. Pitch lead. ([pitch-notes](pitch-notes.md))

## Three strongest new pitch points
- **Confidence isn't skill.** A quarter of teens confident at spotting AI content failed Ofcom's 2026 test (w2-09-04 ✓).
- **One lesson true either way.** Search off, GPT-4 invented 18% of references (w2-02-30 ✓); search on, about 30% of GPT-4o's statements lacked support (w2-02-34 ✓).
- **We tested our scoring on our code.** With proposed settings, at most 3% of no-skill students ever see "secure", with 20% random label errors (w2-02-08 ✓; simulation).

## Three biggest risks judges will spot
- **"Why not Gemini?"** It now tracks progress and informs teachers (w2-08-01 ✓, -02 ✓).
- **No tested under-18 route.** Copilot Studio is untested, and schools pay credits per turn (w2-05-04 ✓, -06 ~).
- **Self-labels.** Ask and Verify rest on the chatbot's labels, and every trigger on labels it gives itself (w2-02-41 ✓); no audit yet.

## What changed since wave 1
- **230 findings:** 138 ✓, 92 ~, 0 ✗.
- **Gemini caught up:** study notebooks and Classroom teacher insights. The moat line is gone.
- **Under-18 route on paper:** Microsoft 365 Education; Copilot Chat is off by default for 13–17s; eduX via Copilot Studio (w2-05-03 ✓, -04 ✓).
- **Teen usage:** 70.6% of 16–18s used generative AI; 52.0% *of users* weekly (w2-09-01 ~).
- **Literacy simulation on real code:** under lenient labelling, up to 13–15% of no-skill students saw Ask "secure" in chat; three settings cut that to 4–7% (≤3% with 20% random errors). The How AI works level ranks students backwards (w2-02-05 ~).
- **Three bugs** found by simulation, one a demo crash.
