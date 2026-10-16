# Post-M409.1 — Governed Hypothesis Update Semantics Productive Consumption v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Make certified `STRENGTHENED`, `WEAKENED`, `UNCHANGED`, `INDETERMINATE` and
`REVIEW_REQUIRED` hypothesis-update semantics available to the existing governed reasoning
context without treating those derived judgments as new evidence.

## Canonical consumption surface
`ReasoningContextBundle` remains the canonical context object. It receives an optional
`derived_assessments` tuple containing immutable `GovernedDerivedEpistemicAssessment`
objects. The extension is backward-compatible: when the tuple is empty, historical context
identity/fingerprints and serialized shape remain unchanged.

## Productive path
certified `GovernedHypothesisUpdateSemanticsReport`
→ `GovernedHypothesisUpdateSemanticsProductiveConsumptionV1.consume(...)`
→ typed derived epistemic assessments
→ explicit caller-supplied existing `ReasoningContextBundle`
→ augmented context available to governed reasoning
→ STOP.

The consumer does not invoke Reasoning. Availability to reasoning is not a new reasoning
cycle.

## Epistemic separation
Derived assessments are explicitly `is_evidence=False` and `is_claim=False`. The original
triggering evidence remains the only evidence. Semantic updates preserve hypothesis id,
BEFORE/AFTER relations, evidence provenance, source and snapshot lineage but do not promote
truth/falsity, assign numeric probability, modify or delete hypotheses, or persist results.

## Idempotence
Re-consuming the same semantic report into an already-augmented context returns
`ALREADY_AVAILABLE` and does not duplicate assessment items. No registry or persistent store
is introduced.

## Hard boundaries
No EvidenceRegistry insertion, Reasoning invocation, Explanation invocation, Curiosity,
Planning, Execution, Learning, Memory write, world-model mutation, Level 2B reopening,
R3/P3/A3/E3, retry, networking, Android execution, scheduler or background loop is added.

## Validation
Focused tests cover typed context consumption, exact semantic/provenance preservation,
evidence separation, backward-compatible empty-context identity/serialization, augmented
serialization, idempotence, truth/falsity/probability protections and absence of downstream
authority calls. Official certification remains `ruff check .` plus complete `pytest -q`.
