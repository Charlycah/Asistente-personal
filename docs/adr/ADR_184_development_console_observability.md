# ADR-184 — Development Console Observability

## Status

Accepted

## Context

M180 introduced the first end-to-end local conversation and M181 introduced formal operational traces. Development now requires a human-readable view of runtime status, activated modules, execution decisions, and lineage. Placing this logic directly in the console would violate the rule that interfaces contain no cognitive or governance logic.

## Decision

Introduce a read-only observability boundary composed of immutable projections, an observer, and a deterministic renderer. The observer reads only existing lifecycle state, persisted turns, runtime composition metadata, and operational traces. The console delegates all inspection to this boundary and only handles command parsing and output.

The projection deliberately excludes conversation text and creates no new trace events. It cannot authorize or repeat provider, retrieval, network, or mutation execution.

## Consequences

- Developers can inspect the official runtime from the same local console.
- Exact M175/M177/M180/M181 lineage remains visible.
- Console behavior remains replaceable and cognitively inert.
- Observability is local and synchronous; richer dashboards and long-lived lifecycle supervision remain future work.
