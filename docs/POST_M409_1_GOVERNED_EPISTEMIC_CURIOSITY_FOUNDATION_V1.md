# Post-M409.1 — Governed Epistemic Curiosity Foundation v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Materialize a pure, read-only, multisource knowledge-gap to question-candidate
foundation. Curiosity is not a new cognitive authority. It receives structured
evidence from an existing source and preserves that source's ownership.

## v1 contract

The foundation accepts evidence originating from conversation, audio, visual
perception, world model, memory, organization, reasoning, external evidence or
another explicitly identified source. It never captures those sources itself.

The governed outcomes are:

- `NO_GAP`: no explicit missing knowledge exists.
- `GAP_NOT_RELEVANT`: a gap exists but was explicitly classified not relevant.
- `QUESTION_CANDIDATE`: an explicit relevant gap can become a traceable question.
- `ABSTAIN`: relevance is unresolved or a supplied prior-question reference
  suppresses repetition.

Questions are classified as clarification, learning or hypothesis-check
candidates. Question generation is deterministic and preserves source
provenance.

## Authority and reuse

This foundation adds no `CuriosityAuthority`, manager, gateway, repository,
runtime root or persistence. Existing epistemic, judgment, relevance,
initiative, conversation, knowledge, memory and learning owners remain
unchanged. Productive consumption by those capabilities is deliberately
deferred to later gates.

## Explicit non-goals

v1 does not wire camera or microphone acquisition, inspect free text, query an
LLM, search the network, persist questions, write memory, create learning
candidates, modify knowledge, create goals, start background curiosity,
schedule work or execute actions.

Visual and audio are supported only as provenance kinds for already structured
evidence. Human answers are not learned automatically in v1.

M410, networking and Residential remain out of scope.
