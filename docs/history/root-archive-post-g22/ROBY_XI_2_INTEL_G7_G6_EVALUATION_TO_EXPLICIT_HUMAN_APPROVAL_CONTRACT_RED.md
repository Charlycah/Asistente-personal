# ROBY XI.2 — INTEL-G7 — G6 EVALUATION → EXISTING EXPLICIT HUMAN APPROVAL — CONTRACT RED

## Baseline

Source of truth: `INTEL-G6 — SOURCE-NEUTRAL GOVERNED M369 EVALUATION — SURGICAL GREEN — CERTIFIED / CLOSED`.

Official local certification entering this gate:

- 14,093 PASS
- Ruff clean
- 0 FAIL

## Architectural residual

INTEL-G6 now evaluates canonical review-only M369 learning candidates through the existing
`SafeLearningPolicies` authority and stops at a source-neutral safe-learning disposition.
`REVIEW_REQUIRED` authorizes human review only; it does not accept or persist learning.

The existing explicit human-learning approval authority already owns the bounded semantics for
explicit approval, rejection, deferral, uncertainty, and abstention. Its historical input contract,
however, is shaped around `CuriosityM369LearningEvaluationReport` and requires a
`preference_candidate_id`. G6 intentionally has neither Curiosity provenance nor a
`PreferenceCandidate`.

The residual is therefore a minimal source-neutral seam that presents an eligible G6 evaluation to
the existing human-approval semantics, preserves exact linkage to the G6 source and policy
candidate, emits source-neutral approved-learning evidence only after explicit approval, and stops.
It must not fabricate Curiosity or preference provenance merely to satisfy an older interface.

## Frozen seam

```text
G6 SafeLearning evaluation
        ↓
REVIEW_REQUIRED + review_authorized
        ↓
EXPLICIT EXACT-LINKED HUMAN RESPONSE
        ↓
existing M369 human-approval semantics
        ↓
APPROVED | REJECTED | DEFERRED | UNCLEAR | ABSTAIN
        ↓
source-neutral approved-learning evidence only when APPROVED
        ↓
STOP
```

## Contract obligations

1. G7 accepts only a real G6 evaluation produced from canonical review-only M369 learning candidates.
2. Human approval is eligible only when G6 is `REVIEW_REQUIRED`, its `SafeLearningDecision` is also
   `REVIEW_REQUIRED`, `review_authorized=True`, and acceptance/persistence/adaptation remain false.
3. Exact linkage must cover a deterministic fingerprint of the complete G6 evaluation, the source
   learning-candidate id, and the canonical policy-candidate id.
4. Wrong or missing linkage fails closed as `ABSTAIN` before human-approval semantics are invoked.
5. `INSUFFICIENT_EVIDENCE`, `REJECTED`, `EXPIRED`, or `NOT_ELIGIBLE` G6 states can never become
   approved merely because a human response says yes.
6. Explicit approval/rejection/deferral/uncertainty semantics remain owned by the existing
   `M369ExplicitHumanLearningApprovalEvidenceFoundation`; G7 must not define a competing approval
   vocabulary or manager.
7. Exact explicit approval may emit one source-neutral approved-learning evidence object preserving
   approval request, G6 evaluation fingerprint, learning candidate, policy candidate, human response,
   approver, scope, and source fingerprint.
8. The G7 evidence must not require or fabricate `CuriosityKnowledgeCandidate`,
   `CuriosityM369LearningEvaluationReport`, `PreferenceCandidate`, or `preference_candidate_id`.
9. `APPROVED` means explicit human approval only. It does not mean durable materialization,
   persistence, Memory, knowledge write, adaptation, or runtime activation.
10. G7 must not call M366.6 materialization, `OfficialMemoryGateway`, a memory write adapter,
    productive learning wiring, Library, Services, Planning, execution, research, or background work.
11. G7 adds no Learning Manager, Approval Manager, Knowledge Manager, Memory Manager, registry,
    runtime, persistence authority, or parallel store.

## Semantic boundary

```text
G6 REVIEW_REQUIRED
    != human-approved learning
    != durable materialization proposal
    != persisted stable knowledge
    != recalled knowledge
```

`APPROVED != PERSISTED`.

## Intended future seam

The RED contract intentionally expects a future module:

`app.governed_g6_explicit_human_learning_approval`

with a narrow API centered on:

- `GovernedExplicitHumanLearningApprovalResponse`
- `GovernedApprovedLearningEvidence`
- `GovernedG6HumanLearningApprovalResult`
- `GovernedG6ExplicitHumanLearningApprovalV1`

The existing M369 approval authority may receive a minimal public source-neutral classification
entry point during SURGICAL GREEN, provided its historical Curiosity contract remains behaviorally
unchanged and no second approval authority is created.

## RED exit condition

The targeted G7 contract must fail only because the future productive G7 seam module does not yet
exist. Ruff must remain clean, the quality baseline must be synchronized with the RED test, and all
pre-existing tests must remain unchanged.

## STOP

Do not implement SURGICAL GREEN until explicit authorization follows local RED validation.
