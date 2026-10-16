# ADR 226.4 — Gmail Execution Planning

## Status

Accepted

## Context

M226.3 introduced deterministic Gmail intent resolution before semantic capability
resolution. The integration still moved directly from resolved intent and capability
decisions into Tool Gateway request construction. ROBY needs an explicit, auditable
planning boundary that validates request shape before execution without exposing
payload values or weakening M61, M62, or M63.

## Decision

Add an immutable Gmail execution-planning layer between capability resolution and
Tool Gateway request construction.

The layer introduces:

- `GmailExecutionPlan`, an immutable and secret-free execution description;
- `GmailExecutionPlanner`, a deterministic planner and payload-shape validator;
- validation of required payload fields before any gateway invocation;
- consistency checks between intent and capability decisions;
- explicit mutation and confirmation metadata;
- a public `plan()` method that performs governance without execution.

The resulting order is:

1. intent normalization;
2. semantic capability resolution;
3. local Gmail policy evaluation;
4. execution planning and payload-shape validation;
5. M61 Tool Gateway routing;
6. M63 permission and consent enforcement;
7. existing mail adapter execution.

## Compatibility

M226.4 preserves:

- all canonical actions and aliases from M226.3;
- semantic `gmail.*` and physical `mail.*` capability contracts;
- local send-disabled-by-default policy;
- gateway registration and permission enforcement;
- secret-free status and audit boundaries;
- runtime composition and provider transport behavior.

## Boundaries

M226.4 does not:

- inspect, retain, or expose payload values in plans;
- execute plans outside the Tool Gateway;
- introduce OAuth, Google API dependencies, attachments, or network tests;
- perform natural-language or probabilistic planning;
- mutate the official Runtime Composition Root.

## Consequences

Gmail requests now have a complete pre-execution governance chain: intent,
capability, policy, and immutable plan. Future provider transport and OAuth work can
consume validated plans without coupling authorization or payload semantics to
provider-specific code.
