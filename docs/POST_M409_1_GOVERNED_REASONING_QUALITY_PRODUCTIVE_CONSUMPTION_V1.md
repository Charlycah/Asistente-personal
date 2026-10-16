# Post-M409.1 — Governed Reasoning Quality Assessment — Productive Consumption v1

## Purpose

Expose an already-certified `GovernedReasoningQualityAssessment` to the existing governed
reasoning context without changing the Foundation semantics or creating a second context,
reflection, learning, or reasoning authority.

## Productive path

`GovernedReasoningQualityAssessment`
→ app-layer `GovernedDerivedReasoningQualityContextAssessment`
→ existing `ReasoningContextBundle.derived_assessments`
→ available to governed reasoning.

The context projection is structural and read-only. It preserves assessment identity,
status, source/snapshot lineage, optional update/discrimination lineage, rationale, and a
deterministic fingerprint.

## Semantics preserved

- `ADEQUATE` does not establish truth, correctness, certainty, acceptance, or stopping.
- `LIMITED` does not mean failed reasoning and does not trigger rerun or correction.
- `REVIEW_REQUIRED` does not invoke Reflection or any review workflow automatically.
- Quality context items are neither evidence nor claims.
- Existing Hypothesis Update and Epistemic Sufficiency derived assessments remain intact.

## Authority and side-effect boundary

`governed_reasoning` remains the canonical authority. Productive consumption does not invoke
Reasoning, Reflection, Curiosity, Planning, Learning, or Execution; does not modify
conclusions, hypotheses, world model, or Memory; does not persist; grants no authority; and
starts no background process.

## Import boundary

The app-layer consumer imports both the core quality assessment and the neutral
`ReasoningContextBundle`. The context core does not import the quality capability, and the
quality Foundation does not import the context bundle.
