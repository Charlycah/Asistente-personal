# Post-M409.1 — Governed Reasoning Method Effectiveness Awareness — ReasoningContextBundle Productive Consumption v1

## Purpose

Expose an already-certified `GovernedReasoningMethodEffectivenessAwareness` through the existing `ReasoningContextBundle.derived_assessments` carrier so the unified reasoning context can observe scope-bound support for method adequacy without acquiring causal, global-effectiveness, comparative, scoring, ranking, selection, recommendation, adaptation, learning, memory, or execution authority.

## Exact reuse

The increment reuses the existing neutral `ReasoningContextDerivedAssessment` structural contract. `ReasoningContextBundle` and `core/governed_reasoning/derived_assessment_contract.py` are not modified.

The app-level consumer accepts one certified effectiveness-awareness artifact and projects it as `GovernedReasoningMethodEffectivenessAwarenessContextItem`. The projection preserves the Foundation status, method fingerprint, evaluation scope, source-association lineage and status, observation counts, world-snapshot lineage, rationale codes, and source fingerprint.

## Semantic boundary

`evaluates_observed_support=True` is preserved because the upstream Foundation certifies only a scope-bound interpretation of the observed record. `evaluates_effectiveness=False` remains explicit.

The projection and consumption result do not establish truth, falsity, causality, attribution of outcomes to the method, global effectiveness, cross-method comparison, superiority, probability, scores, rankings, selection, recommendation, reasoning modification, adaptive reasoning, curiosity, reflection, learning, persistence, memory, action execution, or background processing.

`REVIEW_REQUIRED_OBSERVED_RECORD` remains review-required awareness and is never collapsed into ineffectiveness or an automatic Reflection trigger.

## Productive path

```text
GovernedReasoningMethodOutcomeAssociation
    -> GovernedReasoningMethodEffectivenessAwarenessFoundationV1
    -> certified GovernedReasoningMethodEffectivenessAwareness
    -> app-level productive consumer
    -> ReasoningContextBundle.derived_assessments
```

The consumer never receives a raw association for evaluation and never re-derives status, counts, scope, or rationale.

## Idempotence and identity

The contextual projection derives a deterministic `assessment_id` from the certified `awareness_id` and `source_fingerprint`. Re-consuming identical awareness returns `ALREADY_AVAILABLE` without replacing the context. Reuse of the same contextual identity with a different serialized payload fails closed.

## Scope exclusions

This increment does not modify the effectiveness-awareness Foundation, Method Outcome Association, Comparative Awareness, `ReasoningContextBundle`, the derived-assessment Protocol, Learning, Memory, Adaptive Reasoning, Event Bus, runtime orchestration, or persistence.
