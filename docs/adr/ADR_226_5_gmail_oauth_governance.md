# ADR 226.5 — Gmail OAuth Governance

## Status

Accepted.

## Context

M226.1 through M226.4 established the governed Gmail boundary, semantic
capabilities, deterministic intent resolution, and immutable execution planning.
ROBY still lacked a provider-neutral authority for inspecting and controlling the
OAuth credential lifecycle. Directly deserializing Google credential pickles or
binding the architecture to `google-auth` would introduce secret leakage,
provider coupling, and unsafe persistence into the official distribution.

## Decision

Introduce `GmailOAuthGovernance` as a provider-neutral lifecycle boundary. It
loads credential material only through a `GmailCredentialProvider` protocol and
publishes immutable `GmailOAuthSnapshot` values containing fingerprints and
lifecycle metadata, never access tokens, refresh tokens, client secrets, or raw
scopes.

The boundary classifies credentials as absent, ready, expired, revoked, or
insufficient-scope. Refresh and revocation are explicit policy-controlled
operations delegated to the external credential material. No credential file,
OAuth browser flow, Google SDK dependency, or network transport is introduced in
this milestone.

`GmailGovernedIntegration` may receive this governance boundary and report only
its secret-free lifecycle state. Existing construction remains compatible when
OAuth governance is omitted.

## Consequences

- OAuth lifecycle decisions become testable without provider SDKs or network.
- Credential storage and serialization remain outside ROBY's domain boundary.
- Pickle files and real credentials are prohibited from official ZIPs.
- Scope requirements are evaluated while published status contains only hashes.
- Actual Google authorization, token persistence, and API transport remain future
  milestones.
