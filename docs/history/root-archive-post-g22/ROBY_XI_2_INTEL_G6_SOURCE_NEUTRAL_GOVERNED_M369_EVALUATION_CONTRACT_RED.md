# ROBY XI.2 — INTEL-G6 — SOURCE-NEUTRAL GOVERNED M369 EVALUATION — CONTRACT RED

## Baseline

Source of truth: `INTEL-G5 — EVIDENCE → LEARNING CANDIDATE ADMISSION — SURGICAL GREEN — CERTIFIED / CLOSED`.

Official local certification entering this gate:

- 14,088 PASS
- Ruff clean
- 0 FAIL

## Architectural residual

INTEL-G5 now admits exact terminal governed-investigation evidence into the existing M369 learning foundation and stops at a canonical `LearningCandidate` with `REVIEW_REQUIRED`, `accepted_as_knowledge=False`, and `persistence_authorized=False`.

The existing safe-learning authority is already canonical, deterministic, read-only, and unable to accept or persist learning. The remaining seam is therefore not a new learning system and not durable persistence. It is a source-neutral evaluation boundary that can take an already-structured canonical learning candidate, preserve its provenance, evaluate bounded corroborating candidate evidence through the existing `SafeLearningPolicies`, and stop at the resulting safe-learning disposition.

Historical `CuriosityM369LearningEvaluationFoundation` is a source adapter. It must not become the general owner for investigation-derived learning, and investigation provenance must not be rewritten as `curiosity_human_answer`. `PreferenceLearning` is also not the general knowledge authority and must not be used merely to make stable intellectual knowledge look like a preference.

## Frozen seam

```text
G5 LearningCandidate(REVIEW_REQUIRED)
        ↓
EXPLICIT G6 SOURCE-NEUTRAL EVALUATION INVOCATION
        ↓
canonical LearningPolicyCandidate
        ↓
exactly one existing SafeLearningPolicies.evaluate()
        ↓
SafeLearningDecision
        ↓
INSUFFICIENT_EVIDENCE | REVIEW_REQUIRED | REJECTED | EXPIRED
        ↓
STOP
```

## Contract obligations

1. G6 accepts only canonical M369 `LearningCandidate` inputs that remain review-only and non-persistent.
2. Investigation-derived provenance must remain visible through the candidate observation lineage supplied to the boundary; G6 must not fabricate Curiosity provenance.
3. A single candidate is insufficient under the existing M369.6 policy and must remain `INSUFFICIENT_EVIDENCE`.
4. Corroborating candidates may contribute only when they support the same normalized subject and proposed value and are individually canonical, review-only, and non-persistent.
5. Duplicate candidate identities, semantic disagreement, malformed counters, or ineligible source candidates fail closed before the safe-learning authority is invoked.
6. Eligible evidence is represented as one canonical `LearningPolicyCandidate` using the candidate ids as evidence ids and a deterministic aggregate confidence.
7. The boundary calls the existing `SafeLearningPolicies.evaluate()` exactly once for an eligible evaluation.
8. A `REVIEW_REQUIRED` decision authorizes review only. It never authorizes acceptance, persistence, adaptation, durable materialization, or Memory.
9. G6 must not call human approval, M366.6 materialization, `OfficialMemoryGateway`, Library, Services, Planning, execution, research, Curiosity evaluation, or background processes.
10. G6 adds no Learning Manager, Knowledge Manager, Memory Manager, registry, runtime, persistence authority, or parallel learning store.

## Semantic boundary

```text
investigation evidence
    != learning observation
    != learning candidate
    != safe-learning evaluation
    != human-approved learning
    != durable materialization proposal
    != persisted stable knowledge
    != recalled knowledge
```

`REVIEW_REQUIRED` is not approval.

## Intended future seam

The RED contract intentionally expects a future module:

`app.governed_learning_candidate_m369_evaluation`

with a narrow API centered on:

- `GovernedLearningCandidateM369EvaluationStatus`
- `GovernedLearningCandidateM369EvaluationResult`
- `GovernedLearningCandidateM369EvaluationV1`

No productive implementation belongs in CONTRACT RED.

## RED exit condition

The targeted test must fail only because the future seam module does not yet exist. Ruff must remain clean and the quality baseline must be synchronized with the added RED test.

## STOP

Do not implement SURGICAL GREEN until explicit authorization follows local RED validation.
