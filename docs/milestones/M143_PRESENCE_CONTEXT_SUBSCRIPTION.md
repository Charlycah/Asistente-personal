# M143 — Presence Context Subscription

M143 is the declarative subscription boundary for canonical presence context.

## Responsibility
Register a governed subscription over an immutable M142 `PresenceContextPublicationResult` without delivering or processing the published context.

## Inputs
- owner;
- one or more M142 publication results;
- subscriber identifier;
- accepted publication topic;
- accepted schema versions;
- complete-only or partial-inclusive filter;
- active or paused lifecycle;
- explicit subscription declaration.

## Outputs
- active subscription;
- paused subscription;
- review required;
- blocked;
- not applicable.

Registered subscriptions preserve the exact M142 source object and add only declarative subscription metadata.

## Explicit exclusions
M143 does not perform delivery, callback invocation, consumer processing, routing execution, identity or activity inference, response decisions, behavior adaptation, provider calls, automation, or platform mutation.
