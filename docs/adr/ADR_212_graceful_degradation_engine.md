# ADR 212 — Graceful Degradation Engine

## Status

Accepted.

## Context

M211 classifies the resilience posture of the unified cognitive architecture but intentionally cannot alter its effective service level. Operational hardening requires a deterministic boundary that translates that posture into bounded capability dispositions while preserving a coherent conversational path and avoiding accidental recovery, repair, provider, tool, or infrastructure authority.

## Decision

Introduce `GracefulDegradationEngine` immediately after M211 in the official cognitive runtime. It activates one of four reversible service modes:

- `full` for robust operation;
- `conservative` for guarded operation;
- `essential` for degraded operation;
- `contained` for blocked or unsafe operation.

Each decision defines a traceable disposition—preserve, limit, or suspend—for conversation continuity, governed reasoning, memory enrichment, executive planning, background cognition, and tool expansion. Conversation continuity is always preserved. The effective mode is published as a governed blackboard constraint and added to runtime context.

M212 does not diagnose new failures, repair components, coordinate retries, restore suspended capabilities, change providers, execute tools, or mutate platform configuration. Recovery authority remains reserved for M213.

## Consequences

- Resilience posture now produces an explicit, deterministic operational service level.
- Nonessential cognition can be bounded without collapsing the user-facing conversation path.
- Every degradation decision retains exact M211 and M210 lineage.
- Recovery and restoration remain isolated behind the forthcoming M213 boundary.
