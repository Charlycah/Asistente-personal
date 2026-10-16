# ROBY XI.2 — INTEL-G6 — SOURCE-NEUTRAL GOVERNED M369 EVALUATION — SURGICAL GREEN

## Baseline

Source of truth: locally validated INTEL-G6 CONTRACT RED.

Entering certification state:

- 14,088 PASS
- 5 intentional G6 RED failures
- Ruff clean
- zero unrelated regressions

## Productive change

One productive seam was added:

`app/governed_learning_candidate_m369_evaluation.py`

The seam accepts canonical review-only M369 `LearningCandidate` inputs, validates explicit
corroboration, creates one canonical `LearningPolicyCandidate`, delegates exactly once to the
existing `SafeLearningPolicies.evaluate()` authority, and stops at its disposition.

## Frozen behavior

```text
G5 LearningCandidate(REVIEW_REQUIRED)
        ↓
EXPLICIT G6 SOURCE-NEUTRAL EVALUATION
        ↓
LearningPolicyCandidate
        ↓
existing SafeLearningPolicies.evaluate() exactly once
        ↓
INSUFFICIENT_EVIDENCE | REVIEW_REQUIRED | REJECTED | EXPIRED
        ↓
STOP
```

A single candidate remains insufficient evidence under M369.6. Explicit corroboration may reach
`REVIEW_REQUIRED` only when candidate identities are unique and normalized subject/value semantics
agree. Duplicate identity, malformed age, non-canonical candidate state, or semantic disagreement
fails closed before the policy authority is invoked.

## Architectural invariants

- no automatic acceptance
- no automatic persistence
- no Memory or knowledge write
- no durable materialization
- no human-approval invocation inside G6
- no Curiosity provenance fabrication
- no preference-path substitution
- no runtime or background wiring
- no parallel learning, knowledge, or memory authority

`REVIEW_REQUIRED` remains review authorization only.

## Assistant-side verification

- frozen G6 contract: 5 PASS
- focused M369/downstream regression block: 62 PASS
- M361 quality baseline: 5 PASS after regeneration
- productive module `py_compile`: PASS
- Ruff executable unavailable in the assistant container

Full-suite and Ruff certification remain authoritative in the user's local environment.

## STOP

Do not extend G6 beyond safe-learning evaluation. Do not advance to a later intellectual gate until
local GREEN certification is complete.
