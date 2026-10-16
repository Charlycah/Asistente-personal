# ADR 226.6 — Gmail Provider Transport

## Status

Accepted.

## Context

M226.1 through M226.5 established governed Gmail composition, semantic
capabilities, deterministic intent resolution, immutable execution planning, and
provider-neutral OAuth lifecycle governance. ROBY still lacked an explicit
boundary for provider calls. Direct SDK, HTTP, IMAP, or SMTP failures could
otherwise leak provider details, bypass OAuth readiness checks, or couple domain
logic to one client library.

## Decision

Introduce `GmailProviderTransport` as an OAuth-aware, provider-neutral boundary.
It accepts only canonical operations, validates payload shape and local limits,
requires a `ready` OAuth snapshot before backend invocation, applies a bounded
local timeout, and returns an immutable `GmailTransportResult`.

Provider implementations conform to `GmailProviderBackend`. The boundary
normalizes provider failures into a secret-free taxonomy:

- `authentication`
- `timeout`
- `rate_limited`
- `unavailable`
- `rejected`
- `invalid_response`

Transport status exposes counters and operation names only. It does not expose
credential material, OAuth scopes, request payload values, provider exception
text, recipients, subjects, bodies, or message identifiers.

The existing IMAP/SMTP adapters and Tool Gateway contracts remain unchanged.
No Google SDK dependency, runtime composition mutation, or live network call is
introduced in this milestone.

## Consequences

ROBY now has a deterministic seam where a future Gmail API backend can be
inserted without changing intent, capability, policy, consent, or execution
planning. Provider-specific retry and idempotency behavior remain deferred to
later milestones.
