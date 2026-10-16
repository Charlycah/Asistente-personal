# Post-M409.1 — Governed Reasoning Method ↔ Epistemic Outcome Association — ReasoningContextBundle Productive Consumption v1

## Purpose
Expose a certified `GovernedReasoningMethodOutcomeAssociation` through the existing `ReasoningContextBundle.derived_assessments` carrier without changing the Bundle or the association Foundation.

## Boundary
The app-level consumer projects only the certified association result: association identity, status, method fingerprint, source reference, categorical counts, rationale codes and source fingerprint. It does not transport source observations or reconstruct Method Provenance, Quality, Sufficiency, Deepening, or M203 history.

## Governance
The projection remains derived, read-only, non-evidence and non-claim context. It does not establish truth or causality, assign probability, evaluate effectiveness, compare/rank/select/recommend methods, modify or rerun reasoning, invoke Adaptive Reasoning/Curiosity/Reflection, create Learning/Memory, persist results, execute actions, grant authority, or start background work.

## Identity and idempotence
Context identity is derived from `association_id` plus its certified source fingerprint, never from `method_fingerprint`. Re-consuming the same association is idempotent; an identical context identity with a different payload fails closed.

## Preserved architecture
No changes are made to `ReasoningContextBundle`, the derived-assessment protocol, Method Provenance, Reasoning Quality, Epistemic Sufficiency, Longitudinal Reasoning, M203, Memory, Learning, or Adaptive Reasoning.
