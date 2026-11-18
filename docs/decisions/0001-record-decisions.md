# 0001. Record decisions with their research basis

- **Status:** Accepted
- **Date:** 2026-11-18
- **Pull request:** this one

## Context

Synapse is being built against a literature review of 439 source records. Many settings are starting values rather than findings, and some changes depart from what the research suggests. The existing `docs/build/reference/research.md` lists the evidence for each choice, and `settings.md` is meant to label every number as "from research" or "judgement call". Neither explains why a particular *change* was made, what else was considered, or how sure we are.

The competition entry also rests on claims that must stay honest: simulations are synthetic, nothing is "gaming-proof", and personalisation is "starting points first, learning rate only as fast as the evidence allows". Reviewers of the white paper and the pitch need to trace each claim to its basis.

## Decision

Keep short decision records in `docs/decisions/`, one per significant change, written in the same pull request as the change. They use the template in the folder's README, state how well each source is established, and say what the evidence does not show.

A product call (anything that changes what a student or teacher sees, a pitch claim, or a held item) names Vishnu as decision owner and stays *Proposed* until he confirms.

## Research basis

This record is process, not a teaching claim, so it needs no source. It follows the house rule in `settings.md`: no unlabelled numbers.

## Alternatives considered

- **Put the reasoning in pull request descriptions only.** Rejected: descriptions are hard to search and are lost if the repository moves.
- **Extend `research.md`.** Rejected: it is organised by evidence, not by change, and would grow without bound. The records link to it instead.
- **Record every change.** Rejected: refactors and typo fixes add noise. The threshold is in the README.

## Consequences

Each qualifying pull request carries one extra file. Reviewers can check the reasoning without reading the diff. The cost is a little writing per change.

## Verification

Every pull request that alters the learner model, settings, stored data or student-visible text includes a record, and its description ends with "Docs updated: …" naming it.

## What would change our mind

If records stop being read or fall out of date, fold them into pull request descriptions and keep only the register (0002).
