# 0030. The per-student teacher view, and the demo teacher

- **Status:** Proposed
- **Date:** 2026-11-19
- **Decision owner:** Vishnu (what teachers may see is a product call)
- **Updates:** [0024](0024-visual-language-and-what-the-pages-will-not-show.md) ("Teachers see classes, not students")

## Context
Decision 0024 kept the teacher page at class level: no per-student record, cells under 5 students blank, and said a per-student view would need a DPIA first. The demo needs to show what a per-student view would look like, and a school that has done its DPIA may want one. A demo also needs a way in that does not hand out a teacher key.

## Decision
- **A per-student view exists, off by default.** `web.teacher_student_view = false`. A school turns it on after its DPIA, with students and parents told. With it on, a teacher sees, for a class assigned to them, each student's card ("Weak at": parts answered on and not yet secure) and one student's review: what they are unsure about, the wrong idea they hold with its correction and what to try next, how many answers over how many days, taught parts not yet checked, and AI-literacy levels (Ask, Verify, How AI works) with the evidence they rest on.
- **What stays out, as in 0024.** Teachers never see chats or message text (Synapse keeps none). No probabilities, percentages, scores, grades, predictions or rankings; levels only, each with its evidence. No confidence, fatigue, rapid guesses, learning speed, SEND, EAL or demographic data.
- **Class-level parts keep 0024's floor where it matters.** A topic band (few, mixed, most at developing or above) is shown only once 5 students have answered on the topic; otherwise "Not enough answers yet". With the per-student view on, a wrong idea is listed once more than one student holds it, since the cards already show students one by one.
- **Demo mode.** `web.demo_teacher = false`, and `EDUX_DEMO_TEACHER=1` turns it on. It offers "Sign in as demo teacher" on /teacher, which opens a short read-only session (the same mechanism as map-link sessions, decision 0026: stored hashed, never a key, never in a URL). The button refuses, and the per-student routes 404, unless demo mode is on and the class contains only seeded synthetic students (`seed-demo --class`, ids `demo-synth-*`). Demo mode turns the per-student view on for that class only; a real class stays at class level whatever demo mode says.
- **The demo class is synthetic and real-engine.** Twelve made-up names, run through the learner model on whatever pack is loaded, from a fixed random seed, with a class test on the next Friday. It is labelled synthetic on the page.

## Consequences
- A school can turn the view on without code changes, and the default stays as 0024 decided.
- The demo shows the view without a real student's data and without a teacher key.
- The demo session is read-only: "Mark topic as taught" and "Set a test" open the existing forms, and a change is refused with a message.
