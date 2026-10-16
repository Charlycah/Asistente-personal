# ADR-187 — Supervise the official runtime with a local lease and heartbeat

## Status

Accepted for M185.

## Context

M179 can start and stop the composed runtime, while M180–M184 add conversation, traces, observability, memory, and tools. The development runtime now needs to remain active for long laptop sessions without allowing two official processes, losing lifecycle continuity, or assigning cognitive authority to the console.

## Decision

Add `LongLivedRuntimeLifecycle` around the existing `LocalRuntimeBootstrap`. Before starting M179 it atomically acquires a private local lease. It persists private heartbeat metadata, increments a generation for each process incarnation, exposes stale detection, records sanitized degraded state, and always releases the lease during shutdown. The official `main.py` constructs this lifecycle and passes it to the thin console adapter.

## Consequences

- One local process owns the official runtime at a time.
- M179 remains the bootstrap authority and M178 remains the composition authority.
- Heartbeats are operational metadata, not conversation history or cognitive memory.
- Failures are represented without leaking exception messages.
- Restart continuity is explicit through generations and existing persistent stores.
- No background cognition, autonomous recovery, OS daemon installation, or distributed supervision is introduced.
