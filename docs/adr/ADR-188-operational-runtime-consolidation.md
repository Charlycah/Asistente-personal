# ADR-188: Consolidate the official local runtime path

## Status
Accepted

## Decision

Keep the terminal as an adapter, forward governed `/tool` requests to the runtime, maintain heartbeat metadata through a dedicated daemon supervisor, recover a lease only when its PID is absent and heartbeat stale, and type memory/tool composition dependencies through protocols.

## Consequences

Idle runtimes remain healthy without background cognition. Active leases cannot be stolen. Identity is visible and consistent at the UI boundary. Tool and memory integrations remain governed by their existing modules.
