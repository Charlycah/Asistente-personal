# ADR 224.4 — Conversation Context Curation

## Status

Accepted.

## Context

M224.3 proved that recent session history reaches the governed LLM request and the local provider. The observed failure was caused by contradictory historical answers attached to repeated versions of the current question. Those answers became misleading examples for the model even though a correct declarative fact was also present.

## Decision

ROBY curates the bounded, owner/session-scoped recent context immediately before LLM request enrichment.

The curator:

- normalizes case, accents, whitespace, and punctuation for duplicate comparison;
- removes historical turns whose user message is equivalent to the current message;
- removes duplicate historical user statements while retaining the most recent complete turn;
- never mutates or rewrites the persisted journal;
- does not mix conversational context with persistent memory;
- records input, selected, and dropped turn counts in request metadata.

The change is deliberately deterministic and provider-independent. It does not perform semantic memory extraction and does not decide whether an LLM should be used.

## Consequences

Repeated incorrect answers no longer anchor a new response to the same question. Relevant declarations such as “Mi nombre es Carlos” remain available. Full journal history is retained for audit and future memory processing.
