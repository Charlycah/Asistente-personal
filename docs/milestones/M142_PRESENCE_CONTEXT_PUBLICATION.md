# M142 — Presence Context Publication

M142 is the canonical publication boundary for integrated presence context.

## Responsibility
Publish a governed M141 `PresenceContextIntegrationResult` as an immutable, versioned presence-context artifact without reinterpreting it or invoking downstream consumers.

## Inputs
- owner;
- one or more M141 integration results;
- canonical publication topic;
- schema version;
- explicit publication declaration.

## Outputs
- published complete context;
- published partial context;
- review required;
- blocked;
- not applicable.

Active publications preserve the exact M141 source object and add only canonical publication metadata and a deterministic payload digest.

## Explicit exclusions
M142 does not perform delivery, subscription, consumer invocation, identity or activity inference, tracking, response decisions, behavior adaptation, sensor access, provider calls, automation, or platform mutation.
