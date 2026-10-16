# ADR-144 — Presence Context Publication

## Status
Accepted — 2026-07-11

## Context
M141 produces a governed, immutable integration of anonymous presence assessment with explicitly declared device, conversation, spatial, and temporal context. ROBY needs a canonical outbound boundary so higher layers can consume that context without coupling to M141 internals or causing the Ambient Context domain to invoke consumers.

## Decision
Introduce M142 as a provider-neutral publication boundary downstream from M141.

M142:
- accepts only governed M141 integration results;
- preserves the selected M141 result exactly;
- validates ownership, freshness, confidence, result limits, deduplication, and ambient lineage;
- publishes complete and explicitly partial contexts distinctly;
- emits canonical topic, schema version, and deterministic payload digest metadata;
- stores immutable publication records behind a repository protocol;
- never invokes consumers or performs delivery, routing, inference, decisions, adaptation, automation, provider calls, or platform mutation.

## Consequences
The Ambient Context presence chain now has a stable canonical exit boundary. Future consumers may depend on the publication contract rather than M141 implementation details, while actual transport, subscription, orchestration, and behavioral use remain separate future responsibilities.
