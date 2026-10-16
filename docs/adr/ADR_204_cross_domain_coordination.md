# ADR 204 — Cross-Domain Coordination

## Status
Accepted.

## Context
M201 introduced a governed cognitive blackboard, M202 a global cognitive state, and M203 a cognitive event bus. ROBY now needs a consultative layer that correlates those shared signals across cognitive domains without coupling domains directly or acquiring executive authority.

## Decision
Introduce `CrossDomainCoordinator` and an immutable `CrossDomainCoordinationDirective`.

The coordinator:

- reads the M202 global state;
- correlates M203 events scoped to the same owner and session;
- identifies participating domains, constraints, and conflicting values for the same topic;
- emits deterministic priorities and a coordination status;
- publishes a governed candidate into the M201 blackboard;
- remains advisory and does not execute actions, alter plans, mutate memory, choose providers, or arbitrate final authority.

The official runtime order becomes M201 → M202 → M203 → M204.

## Consequences
Cross-domain cooperation now has a stable, traceable interface. M205 can schedule cognitive work from these directives, while M206 remains responsible for executive arbitration.
