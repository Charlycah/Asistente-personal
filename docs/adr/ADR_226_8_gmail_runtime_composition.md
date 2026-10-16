# ADR 226.8 — Gmail Runtime Composition

## Status

Accepted

## Context

M226.1–M226.7 established the governed Gmail integration, semantic capabilities,
intent resolution, execution planning, OAuth governance, provider transport, and
retry/idempotency governance. These components were intentionally kept outside the
official Runtime Composition Root until their contracts stabilized.

## Decision

Add `GmailRuntimeComposition` as the single optional runtime boundary for the full
Gmail stack and expose it through `RuntimeCompositionDependencies` and
`RuntimeComposition`.

The official factory reads only the boolean `ROBY_GMAIL_ENABLED` feature flag. When
Gmail is disabled, the runtime omits it from the composed graph. When enabled but
provider-specific dependencies are absent, it exposes a safe degraded shell with
reason `configuration_missing` rather than failing ROBY startup.

A complete graph must provide integration, OAuth governance, and retry governance
together. Execution is allowed only when the graph is complete and OAuth reports
`ready`.

## Safety and compatibility

- Gmail remains disabled by default.
- No token, credential, account identifier, payload, or provider exception is
  published by runtime status.
- Partial dependency graphs are rejected.
- Existing runtime construction remains valid because all new fields are optional.
- No Google API dependency, interactive OAuth flow, credential file, or network call
  is introduced.
- The conversation pipeline is unchanged.

## Consequences

ROBY now has an official, configurable, observable, and gracefully degradable Gmail
runtime seam. M226.9 can replace the degraded shell with a complete test provider
composition and certify the end-to-end governed path.
