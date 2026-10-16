# ADR 226.7 — Gmail Error & Retry Governance

## Status
Accepted

## Context
M226.6 established an OAuth-aware provider transport and a stable, secret-free error taxonomy. Operational retries must not be implemented inside provider backends or callers because that would fragment policy, leak provider details, and risk duplicate external mutations.

## Decision
Introduce `GmailRetryGovernance` as a bounded authority above `GmailProviderTransport`.

The authority:

- retries only normalized errors marked `retryable`;
- uses deterministic exponential backoff capped by local policy;
- stops immediately for definitive errors;
- requires a non-empty idempotency key for `send` by default;
- publishes only counts, canonical operation, attempt count, decision, and timestamp;
- never publishes payloads, provider exception text, credentials, or idempotency keys.

## Consequences
Provider transports remain single-attempt boundaries. Retry behavior is centrally testable and provider-neutral. Send operations cannot enter the retry loop without an idempotency key. Durable cross-process idempotency storage remains outside this milestone.
