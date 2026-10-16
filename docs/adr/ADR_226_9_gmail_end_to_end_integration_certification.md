# ADR 226.9 — Gmail End-to-End Integration Certification

## Status
Accepted.

## Context
M226.1 through M226.8 introduced governed integration, semantic capabilities,
intent resolution, execution planning, OAuth governance, provider transport,
retry governance, and runtime composition. The series required one reproducible
certification boundary that exercises those components together without real
credentials or network access.

## Decision
Add a deterministic in-memory certification harness. It constructs the complete
Gmail runtime graph, registers the governed integration with M61 Tool Gateway,
uses M63 consent, validates semantic plans, and executes canonical provider
operations through OAuth, retry, and transport boundaries.

The harness supports recent, search, read, compose, draft, reply, and send.
Sending requires an idempotency key. Retry certification uses normalized
rate-limit failures and zero-duration deterministic backoff.

## Consequences
- The full Gmail architecture can be tested as one graph.
- No Google SDK, real account, token, pickle, or network access is required.
- Reports and status omit message content, recipients, and idempotency keys.
- The harness is a certification facility, not a production Gmail backend.
- Real provider credentials and live-account acceptance testing remain an
  operational deployment step outside this milestone.
