# ADR-159 — Cross-Context Continuity

## Status
Accepted

## Context
M156 determines whether a governed Living Conversation candidate is temporally viable at the evaluation instant. ROBY still requires an explicit boundary that can preserve the semantic continuity of that candidate when the companion moves between devices, situations, environments, and physical-world contexts.

Existing M106–M109 components govern device identity, session continuity, context-transfer manifests, and active-device arbitration. M157 must not duplicate those responsibilities. It must only declare whether an M156 timing result remains continuous between two explicit context references.

## Decision
Add M157 as a pure cross-context continuity evaluation layer downstream from M156.

M157:

- consumes immutable M156 timing-evaluation results;
- consumes explicit source and target context references without inferring either context;
- supports desktop, mobile, driving, home, work, walking, travel, ambient, physical-world, and unknown context kinds;
- requires distinct source and target context identifiers;
- evaluates explicit temporal order and a configurable maximum context gap;
- optionally requires authenticated contexts, a shared session reference, or a shared continuity thread;
- declares `CONTINUOUS`, `CONTINUOUS_PARTIAL`, or `INTERRUPTED` outcomes;
- preserves the exact M156 timing evaluation, M155 candidate, M150 opportunity, and source/target context objects;
- applies owner, freshness, confidence, partial-context, deduplication, and result-limit governance;
- produces deterministic immutable continuity identifiers.

## Boundaries
M157 does not:

- infer identity, activity, intent, device state, location, or physical-world state;
- discover or select source or target contexts;
- perform device handoff or context transfer;
- arbitrate an active device or select a delivery channel;
- select timing or schedule execution;
- authorize, activate, start, prompt, realize, or execute a conversation;
- call providers, run automation, adapt behavior, or mutate a platform.

## Consequences
ROBY gains a canonical semantic bridge between temporal conversation viability and later cross-device/context execution decisions. The companion can preserve exact lineage while moving among PC, mobile, driving, ambient, map, visual, and physical-world contexts without coupling continuity declaration to transport, routing, authorization, or execution.
