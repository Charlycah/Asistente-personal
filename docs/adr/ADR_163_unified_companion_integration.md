# ADR-163 — M161 Unified Companion Integration

## Status

Accepted.

## Context

M150–M160 progressively establish conversational opportunity, candidate formation, temporal viability, cross-context continuity, unified permission and consent, operational reliability, and longitudinal experience. ROBY needs a single terminal declaration that exposes the governed state of this complete companion path without turning integration into activation or runtime execution.

This concern is distinct from M105 living-conversation integration, which closes the earlier M93–M104 conversational cycle, and from M109, M121, M127, M133, and M146, which integrate device, driving, maps, visual, and ambient concerns within their own bounded contexts.

## Decision

Introduce `core.unified_companion_integration` downstream from M160.

The milestone:

- consumes one immutable M160 result;
- validates owner continuity and explicit integration intent;
- preserves exact M160 → M159 → M158 → M157 → M156 → M155 → M150 lineage;
- calculates a conservative unified confidence from the complete lineage;
- produces `READY`, `DEGRADED`, `HOLD`, `BLOCKED`, or `NOT_APPLICABLE`;
- treats negative experience, unavailable reliability, unsatisfied consent, broken continuity, untimely conditions, or low confidence as hold conditions;
- treats mixed experience and partial/degraded upstream states as degraded when policy permits;
- uses deterministic immutable identifiers and an append-only repository contract;
- remains declarative and side-effect free.

## Boundaries

M161 does not:

- activate ROBY or start a conversation;
- choose a device, channel, route, provider, or clock time;
- perform handoff or context transfer;
- create prompts, responses, notifications, or speech;
- mutate consent, memory, policy, personality, knowledge, or upstream results;
- call providers, execute automation, or modify external platforms;
- replace bounded integrations M105, M109, M121, M127, M133, or M146.

## Consequences

ROBY gains a single auditable declaration of unified companion readiness across devices, contexts, permissions, reliability, and long-term experience. Downstream activation remains a separate future responsibility, preserving low coupling and preventing an integration layer from becoming an execution runtime.
