# ADR-183 — Operational Trace Model

## Status
Accepted

## Context
M180 provides the first persistent end-to-end local conversation, but its JSONL turn
journal is a conversation record rather than a formal operational trace. The runtime
needs causal, per-turn observability lineage before a development console can present
module activation in M182.

## Decision
Introduce a dedicated `core.operational_trace_model` boundary with immutable event and
aggregate models, an injected recorder, and a private local JSONL store.

Each governed turn emits an ordered causal chain:

1. `turn_started` at the M180 execution boundary;
2. `pipeline_finished` with exact M177/M175 lineage and execution flags;
3. `turn_persisted` only when the M180 conversation journal is written.

Trace identity is scoped to owner, session, and turn sequence. Event IDs are
deterministic and each event after the first references its immediate causal parent.
The trace store supports session-scoped listing and exact trace lookup.

Operational traces contain no user prompt or response text. Conversation content
remains exclusively in the M180 journal. Reading traces performs no provider,
retrieval, network, tool, memory, or platform action.

## Consequences
- M182 can render formal traces without reverse-engineering conversation records.
- Trace and conversation retention can be configured independently.
- Interrupted or non-persisted turns can remain visible as two-event traces.
- The local trace file is append-only JSONL with private `0600` creation permissions.
- Cross-process locking, retention policy, and advanced querying remain outside M181.
