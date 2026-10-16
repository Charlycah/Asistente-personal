# Post-M409.1 — Governed Epistemic Sufficiency Assessment — Productive Consumption v1

## Purpose

Expose the already-certified Governed Epistemic Sufficiency Assessment to the existing
`ReasoningContextBundle` as a read-only derived context assessment.

## Reuse

- Reuses `GovernedEpistemicSufficiencyAssessment` without changing its semantics.
- Reuses `ReasoningContextBundle.derived_assessments` through the neutral
  `ReasoningContextDerivedAssessment` structural contract.
- Follows the existing app-layer productive-consumption pattern used by governed
  hypothesis update semantics.

## Governed boundary

The consumer does not register evidence or claims, establish truth/falsity, close
reasoning, authorize stopping, invoke reasoning/curiosity/planning/execution, persist
Memory/Learning, modify hypotheses/world model, grant authority, or start background
work. `SUFFICIENT`, `INSUFFICIENT`, and `INDETERMINATE` remain contextual epistemic
assessments only.

## Import boundary

The productive adapter lives in `app/`. `core.governed_reasoning.context` does not
import the sufficiency capability, and the sufficiency foundation does not import the
context bundle.

## Validation gate

After applying this delta to the certified baseline:

```text
ruff check .
pytest -q
```
