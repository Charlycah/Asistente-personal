# Post-M409.1 — Governed Comparative Reasoning Method Awareness — ReasoningContextBundle Productive Consumption v1

## Purpose

Expose an already-certified `GovernedComparativeReasoningMethodAwareness` through the existing `ReasoningContextBundle.derived_assessments` carrier so the unified reasoning context can observe descriptive cross-method differences without acquiring evaluation, ranking, selection, recommendation, adaptation, learning, memory, or execution authority.

## Exact reuse

The increment reuses the existing neutral `ReasoningContextDerivedAssessment` structural contract. `ReasoningContextBundle` and `core/governed_reasoning/derived_assessment_contract.py` are not modified.

The app-level consumer accepts one certified comparative awareness artifact and projects it as `GovernedComparativeReasoningMethodAwarenessContextItem`. The projection preserves the Foundation status, source reference, association lineage, method fingerprints, association statuses, observation counts, world snapshot lineage, rationale codes, and source fingerprint.

## Semantic boundary

`compares_methods=True` is preserved because the upstream Foundation already certifies a descriptive comparison between two methods. This does not authorize any stronger conclusion.

The projection and consumption result remain explicitly non-authoritative for truth, falsity, causality, probability, effectiveness, method superiority, ranking, method selection, recommendation, reasoning modification, adaptive reasoning, curiosity, reflection, learning, persistence, memory, action execution, or background processing.

`DIFFERENT_PATTERN` remains a descriptive categorical difference only. `SAME_PATTERN` is not an equivalence claim. `INSUFFICIENT_COMPARATIVE_EVIDENCE` does not authorize a difference inference.

## Productive path

```text
GovernedReasoningMethodOutcomeAssociation A/B
    -> GovernedComparativeReasoningMethodAwarenessFoundationV1
    -> certified GovernedComparativeReasoningMethodAwareness
    -> app-level productive consumer
    -> ReasoningContextBundle.derived_assessments
```

The consumer never receives raw associations for comparison and never re-derives comparative status or rationale.

## Idempotence and identity

The contextual projection derives a deterministic `assessment_id` from the certified `awareness_id` and `source_fingerprint`. Re-consuming an identical awareness returns `ALREADY_AVAILABLE` without replacing the context. Reuse of the same contextual identity with a different serialized payload fails closed.

## Scope exclusions

This increment does not modify the comparative Foundation, `ReasoningContextBundle`, the derived-assessment Protocol, Method Provenance, Method Outcome Association, Learning, Memory, Adaptive Reasoning, Event Bus, runtime orchestration, or persistence.
