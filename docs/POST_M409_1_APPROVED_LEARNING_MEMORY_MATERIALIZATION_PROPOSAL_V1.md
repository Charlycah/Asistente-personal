# Post-M409.1 — Approved Learning Evidence → Governed Memory Materialization Proposal Foundation v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Transform already-approved, review-authorized M369 preference learning evidence
into an exact, traceable, read-only long-term-memory materialization proposal.
The proposal does not perform persistence.

## Input boundary

This increment does not parse human approval. `ApprovedLearningEvidence` is a
minimal structured input contract for evidence that has already been explicitly
approved. Approval extraction, yes/no interpretation and conversational approval
wiring remain outside this Foundation.

The approval must exactly preserve the M369 evaluation report id, learning
candidate id and preference candidate id.

## Scope

Durable proposal scopes in v1 are `PROJECT`, `CONTEXT`, `PERSONAL`, `HOUSEHOLD`
and `GENERAL`. `SESSION` and `UNSPECIFIED` return `REVIEW_REQUIRED` and cannot
produce a durable proposal.

Only M369 preference learning is supported in v1. Habit and pattern
materialization remain deferred.

## Existing governance reuse

The Foundation consumes the existing M366.6 `MemoryConsolidationFoundation` and
proposes `LONG_TERM` memory. It preserves the M366.6 assessment and explicitly
declares that the eventual writer must be the existing `OfficialMemoryGateway`.

## Non-goals

No `OfficialMemoryGateway` call, SQLite write, `remember()`, `store_explicit()`,
Learning writer, `ExperientialLearningManager`, User Profile mutation, Knowledge
write, Gateway wiring, network, action execution or new authority is introduced.

M410, networking and Residential remain out of scope.
