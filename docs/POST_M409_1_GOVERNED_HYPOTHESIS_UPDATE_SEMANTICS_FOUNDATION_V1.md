# Post-M409.1 — Governed Hypothesis Update Semantics Foundation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Classify the already-certified structural `GovernedHypothesisEpistemicDeltaReport` into a
small, conservative semantic vocabulary without re-running reasoning or creating a new
belief authority.

## Input and output
Input: one certified structural epistemic delta report.

Output per hypothesis:
- `STRENGTHENED`
- `WEAKENED`
- `UNCHANGED`
- `INDETERMINATE`
- `REVIEW_REQUIRED`

The report remains under canonical authority `governed_reasoning`.

## Closed transition semantics
Foundation v1 admits only explicitly mapped directional transitions:
- `UNRESOLVED -> COMPATIBLE`: strengthened
- `UNRESOLVED -> CONTRADICTED`: weakened
- `COMPATIBLE -> CONTRADICTED`: weakened
- `CONTRADICTED -> COMPATIBLE`: strengthened

An unchanged structural delta is semantically unchanged. Evidence-only changes, newly
introduced hypotheses, and relation transitions not explicitly mapped are indeterminate.
Missing hypotheses or proposition conflicts require review.

## Hard epistemic limits
Strengthening never establishes truth. Weakening never establishes falsity. Foundation v1
assigns no numeric probability or confidence, deletes no hypothesis, performs no reasoning,
comparison, curiosity, planning, capability execution, persistence, learning, memory write,
world-model mutation, or background processing.

## Validation
Architecture/semantic tests cover every admitted directional transition, unchanged and
evidence-only behavior, new/missing hypotheses, proposition conflict, unmapped transitions,
source review propagation, deterministic provenance preservation, and non-authoritative
contract defaults. Official certification remains `ruff check .` plus complete `pytest -q`.
