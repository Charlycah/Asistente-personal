# ADR 227.6 — Gmail Production Readiness Certification

## Status
Accepted.

## Context
ROBY has a governed Gmail stack, a concrete API adapter, secure credential storage,
attachment policy and opt-in real-account acceptance. Deployment approval still needs a
single authority that turns observable evidence into an explicit go/no-go decision without
publishing credentials, recipients, payloads or provider diagnostics.

## Decision
Introduce `GmailProductionReadinessCertifier` as the M227.6 authority. It evaluates runtime
and OAuth readiness, bounded retry and transport policies, acceptance-write policy and
explicit live-account acceptance evidence. It produces an immutable, deterministic,
secret-free certificate with `go`, `conditional` or `no_go` status.

A missing live-account acceptance result is `conditional`, not `go`. Any failed operational
control is `no_go`. Write acceptance remains disallowed unless independently approved by
local production policy.

## Consequences
Production approval is explicit, traceable and fail-closed. Normal unit tests remain
network-free. The certifier does not store credentials, execute Gmail operations, or bypass
existing runtime, OAuth, retry, transport or acceptance authorities.
