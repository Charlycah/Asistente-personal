# ADR-185 — Memory Runtime Integration

## Status

Accepted

## Context

The operational runtime built in M177–M182 can conduct, persist, trace, and observe local conversations, but its existing cognitive memory capabilities are not part of the official runtime graph. ROBY must reuse those capabilities without collapsing private identities, treating the conversation journal as memory, or introducing hidden work during composition.

## Decision

Add an optional memory runtime dependency to `RuntimeCompositionDependencies`. `GovernedRuntimePreparation` uses it only during turn preparation to enrich the already-built inference request. `EndToEndLocalConversation` invokes its learning operation only after the governed pipeline returns.

The integration reuses M36–M39 contracts. Each owner receives a distinct local SQLite database identified by a one-way digest rather than a readable name. Shared recall uses a separate database and is disabled by default. Writes always target the current owner's private store in M183.

## Consequences

- Existing composition remains idempotent and side-effect free.
- Memory recall occurs before provider inference and learning after pipeline completion.
- Carlos, his spouse, and shared context remain physically and logically separated.
- Memory persists independently from the M180 conversation journal.
- Existing cognitive policies remain authoritative for what may be stored.
- Shared writes, memory management UI, and richer memory trace events remain future work.
