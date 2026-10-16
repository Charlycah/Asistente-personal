# M18 — Memory Abstraction

## Objective

Introduce the first memory boundary for ROBY without adding a concrete memory backend and without changing `ROBY.process()` behavior.

M18 creates a stable contract for future memory implementations while keeping memory inactive until an explicit later milestone defines when and how ROBY should remember or recall information.

## Scope

### M18.1 — Memory models and interface

Added:

- `MemoryItem`: immutable memory payload with optional metadata.
- `MemoryQuery`: immutable recall query with optional metadata.
- `MemoryStore`: protocol for future memory implementations.

### M18.2 — Null memory implementation

Added:

- `NullMemoryStore`: no-op implementation used as a safe default.

### M18.3 — Optional ROBY integration

Added:

- `memory_store` optional dependency in `ROBY.__init__`.
- `ROBY.memory_store` attribute.
- Default `NullMemoryStore` when no memory store is injected.

This integration is deliberately passive: `ROBY.process()` does not call `remember()` or `recall()` yet.

### M18.4 — Contract tests

Validated:

- memory models expose content/query text and metadata defaults;
- `NullMemoryStore` accepts `remember()` without side effects;
- `NullMemoryStore.recall()` always returns an empty list;
- `ROBY` uses `NullMemoryStore` by default;
- `ROBY` accepts an injected memory store;
- `ROBY.process()` does not use memory yet.

### M18.5 — Documentation

Documented:

- memory boundary;
- current passive integration;
- out-of-scope behavior;
- future extension points.

## Contract

A memory store must support:

```text
remember(MemoryItem) -> None
recall(MemoryQuery) -> list[MemoryItem]
```

`NullMemoryStore` guarantees:

- accepting `remember()` without side effects;
- returning an empty list for every `recall()` call;
- preserving current ROBY behavior until memory is explicitly activated.

`ROBY` guarantees for M18:

- exposing a `memory_store` dependency;
- defaulting safely to `NullMemoryStore`;
- accepting injected stores for future implementations;
- not invoking memory during `process()` yet.

## Architectural decision

Memory is introduced as an abstraction before any persistence, embeddings, semantic search, or conversation integration.

This keeps ROBY aligned with the project method:

1. Architecture first.
2. Tests first.
3. Minimal implementation.
4. No premature behavior changes in `ROBY.process()`.

## Out of scope

M18 does not include:

- semantic memory;
- persistence;
- embeddings;
- automatic memory writes;
- memory retrieval during conversation resolution;
- memory-based response changes;
- UI controls for memory.

Those belong to later milestones.

## Future extension points

Likely next memory increments:

- explicit memory write policies;
- memory recall policies;
- session-scoped memory;
- long-term semantic memory;
- persistent memory backend;
- memory observability events.
