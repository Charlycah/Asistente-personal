# ADR-161 — M159 Companion Reliability Model

## Status

Accepted.

## Context

M158 establishes whether explicit permission and consent requirements are satisfied for a governed cross-context conversational continuity. That result does not establish whether the companion path is operationally dependable at the moment of evaluation.

ROBY needs a declarative reliability boundary that can combine explicit observations from the source context, target context, conversation pipeline, permission service, device runtime, and network path without performing monitoring, recovery, routing, or execution.

This concern is distinct from M58 trust and explainability, M59 evolution protection, M77 evidence, M81 conflict and uncertainty, and the existing observability infrastructure. M159 consumes explicit operational observations; it does not infer them or replace those layers.

## Decision

Introduce `core.companion_reliability_model` downstream from M158.

The milestone:

- consumes immutable M158 permission-and-consent results;
- accepts explicit immutable reliability observations;
- evaluates freshness, ownership, context coverage, availability, health, error rate, and latency;
- produces `RELIABLE`, `DEGRADED`, `UNAVAILABLE`, `REVIEW_REQUIRED`, `BLOCKED`, or `NOT_APPLICABLE`;
- preserves exact M158 → M157 → M156 → M155 → M150 lineage;
- uses deterministic immutable identifiers and an append-only repository contract;
- remains declarative and side-effect free.

The reliability score is conservative: the minimum applicable observation score determines the result. Explicit hard failures, excessive errors, or excessive latency make the companion unavailable. Partial M158 consent lineage can produce no stronger than degraded reliability.

## Boundaries

M159 does not:

- collect telemetry or poll components;
- infer hidden operational state;
- repair, retry, fail over, or recover components;
- choose a device, channel, route, or provider;
- transfer context or perform handoff;
- schedule or start a conversation;
- generate prompts or responses;
- call providers, run automation, or mutate platforms;
- redefine semantic confidence, trust, explainability, or uncertainty.

## Consequences

ROBY gains one auditable reliability declaration before later activation or orchestration layers. Operational quality is represented explicitly without allowing reliability assessment to become an execution controller.
