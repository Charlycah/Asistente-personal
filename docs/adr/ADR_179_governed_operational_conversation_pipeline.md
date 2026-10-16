# ADR-179 — Governed Operational Conversation Pipeline

## Status

Accepted

## Context

M176 connects the desktop surface to an injected operational pipeline, while M173, M171, and M175 already provide governed execution and response boundaries. ROBY needs one official turn-level orchestrator before concrete runtime composition is introduced in M178.

## Decision

Introduce `GovernedOperationalConversationPipeline` as the application-level orchestration boundary for operational turns.

The pipeline receives an immutable request and delegates upstream interpretation and planning to an injected `GovernedConversationPreparationPort`. The returned preparation must contain the exact governed provider route, inference request, and optional retrieval plan. M177 validates owner, session, and text continuity, executes the local provider exclusively through M173, executes optional retrieval exclusively through M171, and assembles the response exclusively through M175.

The pipeline exposes both a rich `process()` result and an `execute()` compatibility method matching the M176 desktop contract. Results are immutable, deterministic for equal inputs and timestamps, append-only, and preserve exact downstream lineage.

## Consequences

M177 creates a single official operational conversation path without becoming a composition root or adding cognitive logic. M178 can now wire provider health, policy, routing, knowledge-source policy, retrieval planning, concrete adapters, and readiness into the preparation port. Failures remain contained and no platform mutation is authorized.
