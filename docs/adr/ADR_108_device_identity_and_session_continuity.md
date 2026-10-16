# ADR 108 — Device Identity and Session Continuity

## Status
Accepted.

## Context
After Phase X, ROBY needs a governed way to recognize devices and determine whether an active companion session may continue on another endpoint. Existing conversation sessions do not establish stable device identity, trust, endpoint freshness, or cross-device eligibility.

## Decision
M106 introduces a separate `core.device_continuity` boundary. Stable device identity, companion session identity, observed endpoint state, policy, and immutable continuity decisions are modeled independently. The engine validates ownership and active-device coherence and can emit an opaque deterministic resume cursor only when the target is eligible.

## Invariants
- device, session, endpoint, request, and decision objects are immutable;
- ownership must match across the whole request;
- the source must be the session's active device;
- untrusted, unavailable, or policy-required unauthenticated endpoints cannot continue;
- stale or merely recognized targets require review under the default policy;
- required capabilities must be present on the target;
- only `ready` decisions expose a resume cursor;
- identifiers are deterministic and auditable.

## Non-goals
M106 does not copy conversation content, synchronize memory, transport credentials, open connections, select a user interface, deliver messages, execute handoff, or implement the full Mobile Companion.
