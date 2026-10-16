# ADR 215 — Long-Running Stability

## Status

Accepted.

## Context

M214 provides bounded cognitive admission under load, but a long-lived ROBY session also
needs a deterministic way to observe operational drift across cycles. The runtime must
recognize sustained or abrupt instability, request periodic checkpoints, and preserve a
bounded history without acquiring authority over recovery, concurrent execution, tools,
providers, or operating-system resources.

## Decision

Introduce `LongRunningStabilityMonitor` after M214 in the official cognitive runtime.
The monitor:

- records a bounded, per-owner and per-session history of scheduling observations;
- calculates a deterministic drift score from consecutive load and disposition changes;
- emits `stable`, `observing`, `checkpoint_required`, or `guarded` assessments;
- emits `continue`, `observe`, `checkpoint`, or `stabilize` directives;
- requests deterministic periodic checkpoints through policy only;
- publishes the effective stability state to the unified cognitive blackboard;
- preserves source lineage back through M214 and the unified cognitive chain.

M215 does not execute a checkpoint, repair a provider, restart infrastructure, spawn a
worker, or execute work concurrently. M213 retains recovery coordination authority and
M216 will own concurrent cognitive execution.

## Consequences

Long-lived sessions gain explicit drift detection, bounded state growth, and checkpoint
guidance while preserving milestone boundaries. Runtime integration order becomes
M211 → M212 → M213 → M214 → M215.
