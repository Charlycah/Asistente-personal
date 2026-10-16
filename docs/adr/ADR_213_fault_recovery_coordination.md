# ADR 213 — Fault Recovery Coordination

## Status

Accepted.

## Context

M212 establishes the effective cognitive service mode but deliberately cannot coordinate recovery. Operational hardening now requires a deterministic boundary that converts degradation decisions into ordered, traceable recovery work without allowing recovery logic to bypass the safeguards that preserve conversation continuity or to acquire provider, tool, or platform mutation authority.

## Decision

Introduce `FaultRecoveryCoordinator` immediately after M212 in the official cognitive runtime. It translates the effective service mode into one of four recovery states:

- `stable` verifies the full cognitive baseline;
- `observing` verifies capabilities limited by conservative operation;
- `stabilizing` coordinates bounded retries for restricted capabilities;
- `held` preserves containment and prevents premature restoration.

Every plan contains contiguous recovery steps, exact M212/M211/M210 lineage, explicit held or restored capability sets, and a deterministic identity. Conversation continuity is never placed in the held set. The effective recovery state is published as a governed blackboard constraint and added to runtime context.

M213 coordinates recovery intent and sequencing only. It does not restart providers, execute tools, alter infrastructure, mutate platform configuration, bypass degradation policy, or claim long-running stability guarantees. Those operational concerns remain behind later milestones.

## Consequences

- Degraded operation now has an explicit and auditable recovery sequence.
- Containment cannot be silently bypassed by premature restoration.
- Recovery state is available to the unified runtime without external side effects.
- High-load scheduling, long-running stability, and concurrent execution remain isolated for M214-M216.
