# ADR 227.5 — Real Account Acceptance Tests

## Status
Accepted.

## Context
ROBY already has deterministic end-to-end certification and a concrete Gmail API backend, but production readiness requires an explicit acceptance boundary for a deployment-owned Gmail account. Real-account tests must never run implicitly, must not embed credentials, and must distinguish read-only validation from externally mutating validation.

## Decision
Introduce `GmailRealAccountAcceptance` as an opt-in harness controlled by deployment configuration. Preflight requires the Gmail runtime to be ready. Read-only acceptance lists, searches and conditionally reads a message. Write acceptance is separately enabled, requires an explicit recipient, creates a draft and sends using an idempotency key.

The live pytest entry point is skipped unless `ROBY_GMAIL_ACCEPTANCE_ENABLED` is explicitly enabled. A deployment must also provide its composed real-account fixture. Unit tests use only deterministic fake runtimes and perform no network access.

## Consequences
- Normal test runs remain deterministic and network-free.
- No real account is accessed accidentally.
- Write acceptance cannot run without an explicit recipient.
- Reports and status omit query text, recipients, message content and credentials.
- Production deployments can replace the fixture guard with their composed Gmail runtime without changing domain code.
