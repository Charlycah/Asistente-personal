# ADR-096 — Conversational Opportunity Detection

## Status

Accepted for M94.

## Context

M93 introduced the governed boundary that decides whether a prepared
`ConversationOpportunity` may justify intervention, deferral, review or
silence. It intentionally did not define where opportunities come from.

Phase X now needs a deterministic, inspectable way to transform heterogeneous
signals from conversation, memory, reflection, routines and context into
candidate opportunities without granting those candidates authority to speak.

## Decision

Introduce `ConversationalOpportunityDetector` inside
`core.living_conversation`.

The detector:

- accepts immutable, typed `ConversationSignal` instances;
- validates age, relevance, novelty, confidence and sensitivity;
- rejects unsafe or low-value signals with explicit reasons;
- deduplicates source identifiers;
- ranks accepted signals deterministically;
- maps signal kinds to M93 `ConversationOpportunityKind` values;
- preserves source provenance and review requirements;
- persists an immutable `OpportunityDetectionRecord` through a repository
  contract;
- returns only M93-compatible opportunities.

M93 remains the sole boundary that evaluates disposition. M94 does not decide
whether ROBY should speak.

## Invariants

- Detection is not authorization.
- Every accepted opportunity has exactly one source reference.
- Guest contexts accept only public signals.
- Sensitive signals are rejected in sensitive contexts and otherwise retain a
  mandatory review marker.
- Future, stale, low-confidence, low-relevance and low-novelty signals are not
  converted into opportunities.
- Capacity is bounded by policy.
- Equal inputs and timestamps produce equal records.
- No LLM, tool, scheduler, message emitter or memory mutation is involved.

## Consequences

M95 can reason about conversational timing over explicit M94 candidates, while
M96 can later generate content only after both M94 detection and M93 governance
have been satisfied.
