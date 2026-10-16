# Post-M409.1 — Governed Longitudinal Reasoning Assessment — ReasoningContextBundle Productive Consumption v1

## Purpose

Expose a certified `GovernedLongitudinalReasoningAssessment` through the existing
`ReasoningContextBundle.derived_assessments` surface without adding authority,
persistence, temporal semantics, history acquisition, learning, reflection, or action.

## Governed boundary

- Foundation semantics remain frozen in `core.governed_reasoning`.
- Productive projection lives in `app/` and may depend on both the Foundation artifact
  and the existing neutral context contract.
- `ReasoningContextBundle` does not import or know the specialized longitudinal type.
- No new context field, manager, registry, store, authority, or runtime is introduced.
- `INSUFFICIENT_HISTORY` is exposed as information only; it does not acquire history.
- `RECURRENT_LIMITATION` does not invoke Curiosity, Learning, adaptation, or rerun.
- `RECURRENT_REVIEW_REQUIRED` does not authorize review or invoke Reflection.
- Counts are explicit; no score, probability, temporal direction, improving, or degrading
  semantics are introduced.
- No Memory read/write or automatic series construction is performed.

## Projection

The derived context item preserves only the certified longitudinal outcome and compact
lineage needed by later reasoning:

- longitudinal assessment ID;
- status;
- explicit `source_reference`;
- episode count;
- Quality counts;
- Sufficiency counts;
- rationale codes;
- deterministic fingerprint.

The original episode artifacts are not copied into context again.

## Idempotence and collisions

Repeated consumption of the same derived payload reuses the existing context item.
The same derived ID with an incompatible payload fails closed.

## Validation target

Formal certification remains:

1. `python scripts/generate_quality_baseline.py`
2. `ruff check .`
3. `pytest -q`

Baseline entering this increment: 11,797 tests passed, Ruff clean.
