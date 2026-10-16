# M201 — Unified Cognitive Blackboard

M201 begins ROBY's unified cognitive architecture phase by introducing a governed shared blackboard for cognitive signals.

## Capabilities

- Immutable blackboard entries with deterministic lineage.
- Explicit cognitive domains and entry kinds.
- Owner/session isolation.
- Bounded per-session retention.
- Idempotent publication.
- Domain-filtered snapshots and latest-value lookup.
- Session-local cleanup.
- Official runtime contribution immediately after M200.
- Publication of M200's consolidated conversational readiness state.

## Governance

The blackboard is an advisory exchange surface. It does not execute actions, grant permissions, select providers, persist private runtime data outside the process, alter plans, or bypass existing operational controls.

## Runtime order

`M196 → M197 → M198 → M199 → M200 → M201 → existing cognitive contributors`

## Validation

M201 adds focused tests for immutability, deterministic identity, isolation, bounded retention, filtering, idempotence, runtime ordering, request preservation, M200 publication, and session cleanup.
