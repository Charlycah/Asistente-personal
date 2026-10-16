# ADR 227.2 — Gmail API Backend Adapter

## Status

Accepted.

## Context

M226.6 defined a provider-neutral `GmailProviderBackend` contract and M227.1
introduced external Google OAuth credential loading. ROBY still required a
concrete adapter translating canonical transport operations into Gmail API
resource calls without importing Google SDKs into the domain or test runtime.

## Decision

Introduce `GoogleGmailApiBackend` behind `GmailProviderBackend` and a lazy
`GoogleApiClientFactory` deployment helper.

The adapter:

- maps `list_recent` and `search` to `users.messages.list`;
- maps `read` to `users.messages.get(format="full")`;
- maps `create_draft` to `users.drafts.create`;
- maps `send` to `users.messages.send`;
- builds RFC 5322 messages using the standard library and Gmail URL-safe base64;
- preserves an optional Gmail `threadId` for replies;
- normalizes HTTP-like provider failures before they cross the backend boundary;
- exposes only payload-free operational counters through `status()`;
- imports `googleapiclient.discovery.build` only when a deployment constructs a
  real service.

The existing transport remains responsible for OAuth readiness, payload policy,
timeouts, retry classification, and public error taxonomy.

## Consequences

ROBY now has a concrete Gmail API backend that can be connected to deployment
credentials without changing the governed domain. Unit and full-suite tests use
in-memory service doubles and perform no network calls. The Google SDK remains an
optional deployment dependency rather than a mandatory project dependency.
