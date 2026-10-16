# ADR 226.2 — Gmail Capability Layer

## Status

Accepted

## Context

M226.1 established a governed Gmail integration over the existing M66 read adapter,
M67 action adapter, M61 Tool Gateway, and M63 permission/consent boundary. The
physical gateway capabilities remain intentionally provider-neutral as `mail.read`
and `mail.send`.

ROBY now needs finer Gmail semantics without duplicating gateway handlers, changing
permission contracts, or coupling the runtime to Gmail-specific transport details.

## Decision

Add an immutable semantic capability layer inside the Gmail integration boundary.

The layer introduces:

- `gmail.read`;
- `gmail.compose`;
- `gmail.draft`;
- `gmail.reply`;
- `gmail.send`;
- `GmailCapabilityResolver` for deterministic action resolution;
- `GmailCapabilityDecision` for policy, scope, confirmation, mutation, and physical
  gateway routing metadata;
- a secret-free capability catalog exposed separately from the historical status
  contract.

Semantic capabilities resolve onto the existing physical capabilities:

- Gmail read operations resolve to `mail.read`;
- compose, draft, reply, and send resolve to `mail.send`;
- M63 remains authoritative for write consent;
- local Gmail policy remains authoritative for per-action enablement;
- send remains disabled by default and is the only semantic operation marked as
  mutating external state and requiring confirmation.

## Compatibility

M226.2 preserves:

- all M226.1 public behavior;
- existing `mail.read` and `mail.send` gateway registrations;
- the legacy `PermissionError` contract for unknown governed actions;
- the secret-free historical `status()` representation;
- all existing adapters, providers, runtime composition, and transport behavior.

## Boundaries

M226.2 does not:

- register new physical handlers in the Tool Gateway;
- bypass capability registry or consent checks;
- introduce OAuth, Google API dependencies, or network activity in tests;
- add attachment transport;
- mutate the official runtime composition root;
- expose addresses, credentials, recipients, subjects, or bodies in capability
  metadata.

## Consequences

ROBY gains Gmail-specific semantic governance while retaining provider-neutral tool
execution. Future service integrations can adopt the same semantic-to-physical
resolution pattern without changing M61, M62, or M63.
