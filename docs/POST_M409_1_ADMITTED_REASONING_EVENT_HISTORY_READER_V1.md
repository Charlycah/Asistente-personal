# Post-M409.1 — Admitted Reasoning Event History Reader v1

## Purpose
Provide a read-only bridge from already-admitted M203 reasoning assessment events to the existing neutral longitudinal reasoning observation contract.

## Boundaries
- Reuses M203 `CognitiveEventBus.events()` only.
- Filters by owner/session, `SIGNAL_PUBLISHED`, and the certified versioned reasoning topic.
- Validates exact schema, projection fidelity, lineage, statuses, and provenance.
- Reconstructs only `GovernedReasoningAssessmentObservation`; it never rehydrates full Quality or Sufficiency assessments.
- Does not publish, subscribe, persist, create Memory, create Learning, invoke Reflection/Curiosity, or grant authority.
- M203, the longitudinal Foundation, Memory, Learning, Reflection, and ReasoningContextBundle remain unchanged.

## Productive path
`M203 admitted reasoning events -> read-side validation -> neutral observations -> existing longitudinal Foundation`.
