# ADR-160 — Unified Permission and Consent

## Status
Accepted

## Context
M157 declares whether a temporally viable Living Conversation candidate preserves semantic continuity between two explicit contexts. Before any later activation or execution layer can act on that continuity, ROBY needs one canonical evaluation of whether the required permissions and consent are valid across the complete source/target context boundary.

M63 already defines the foundational permission and consent semantics for capabilities and scopes. M158 must preserve that model while unifying it with M157 lineage. It must not grant, revoke, request, or execute anything.

## Decision
Add M158 as a pure permission-and-consent evaluation layer downstream from M157.

M158:

- consumes immutable M157 continuity results;
- consumes explicit capability/scope requirements and explicit consent grants;
- evaluates owner, capability, permission scope, context coverage, grant time, expiration, denial, and revocation;
- supports requirements spanning both continuity contexts or an explicit subset;
- emits `SATISFIED`, `SATISFIED_PARTIAL`, `CONSENT_REQUIRED`, `DENIED`, `REVIEW_REQUIRED`, `BLOCKED`, or `NOT_APPLICABLE` outcomes;
- preserves the exact M157, M156, M155, and M150 lineage;
- applies freshness, confidence, partial-continuity, deduplication, and input-limit governance;
- produces deterministic immutable evaluation identifiers.

## Boundaries
M158 does not:

- create, persist, revoke, or mutate permission grants;
- display or send a consent prompt;
- infer consent, identity, intent, activity, context, or ownership;
- authorize conversation start, activation, handoff, context transfer, routing, channel selection, timing, scheduling, prompts, or responses;
- call providers, run automation, or mutate a platform.

## Consequences
ROBY gains a single auditable bridge between cross-context continuity and future authorization layers. Permission and consent remain explicit, scope-aware, context-aware, time-aware, and fully traceable without coupling policy evaluation to user interaction or execution.
