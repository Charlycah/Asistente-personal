# ROBY XI.2 — R-CI-SI-S5-C2 — RED CONTRACTUAL

## Governed Self-Epistemic Need Curiosity-Evidence Projection

### Certified predecessor

This contract begins only after the owner-certified S5-C1 determination:

`GovernedSelfEpistemicNeedToAskDetermination`

C1 establishes a governed `NEED_TO_ASK` from actual S5 lineage and a proven
absence of a compatible canonical autonomous resolution route. C1 does not
create a question, determine question-worthiness, assign relevance, invoke
Curiosity, or ask a human.

### Inventory-before-surgery finding

The architecture already owns the target curiosity evidence contract:

`core.cognitive_maturity.governed_epistemic_curiosity.MultisourceKnowledgeGapEvidence`

It also already owns Curiosity itself through
`GovernedEpistemicCuriosityFoundation`. Existing adapters demonstrate the
canonical pattern: project explicit governed gaps into that existing evidence
contract while leaving `EpistemicCuriosityRelevance.UNKNOWN` until a separate
governed relevance step occurs.

S3's `InnerContinuityGapCuriosityEvidenceAdapter` is a precedent, not a reusable
source adapter for C1: it consumes `ExplicitInnerContinuityReport` and expresses
a continuity-specific missing fact. C1 carries a distinct certified lineage and
must not be rewritten as an S3 continuity report.

### Exact transformation

ACTUAL C1 NEED-TO-ASK DETERMINATION
→ EXACT SELF-EPISTEMIC LINEAGE PRESERVATION
→ EXISTING `MultisourceKnowledgeGapEvidence`
→ `relevance = UNKNOWN`
→ STOP BEFORE RELEVANCE

### Required production surface

The RED expects the missing module:

`app.governed_self_epistemic_need_curiosity_evidence_projection`

with:

- `GovernedSelfEpistemicNeedCuriosityEvidenceProjection`
- `GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1`
- owner method `.project(need_to_ask_determination)`

The owner belongs in `app` because its canonical source input C1 resides in
`app`; this preserves the certified prohibition on `core → app` imports.

## Contract R1–R8

### R1 — Actual C1 only; preserve upstream anchors

The owner accepts only an actual
`GovernedSelfEpistemicNeedToAskDetermination`. It preserves by identity the C1
object and its route determination, selection, and authorization report.
Passing B1 directly or an arbitrary object is rejected.

### R2 — Reuse the exact existing Curiosity evidence contract

The projection contains an actual `MultisourceKnowledgeGapEvidence` with:

- `source_kind = REASONING`
- `source_reference = C1.requirement_identity`
- `relevance = UNKNOWN`
- `target_person = None`
- `hypothesis = None`
- `prior_question_reference = None`

C2 does not introduce a parallel epistemic-gap evidence type.

### R3 — Preserve explicit S5 self-epistemic lineage

The projection preserves C1 capability, original source reference,
world-snapshot identity, requirement identity, need status, and route status.
The curiosity evidence carries explicit provenance codes for requirement
identity, world snapshot, and selected capability.

### R4 — Project the proven need, not a question or subjective self-claim

The existing evidence contract receives one explicit unknown element describing
the unresolved self-epistemic need already established by C1. Known elements
include the certified requirement identity and world snapshot. C2 must not
invent missing self facts or claim consciousness, subjective experience, or
real emotion. The C2 result has no `question` field.

### R5 — UNKNOWN relevance must remain fail-closed

C2 does not determine relevance or question-worthiness. Its evidence remains
`UNKNOWN`; if independently presented to the existing Curiosity foundation at
this STOP, Curiosity must yield no question candidate and preserve its existing
`relevance_not_yet_governed` fail-closed behavior.

Required C2 result state:

- `relevance_determined = False`
- `question_worthiness_determined = False`
- `question_candidate = None`

### R6 — Preserve existing downstream authorities

C2 reuses `MultisourceKnowledgeGapEvidence` but does not invoke or replace
Relevance, Curiosity, Initiative, Conversation, or human-question transport.
It does not assign relevance and does not create questions.

### R7 — Deterministic, explicit, heuristic-free projection

Repeated projection of the same C1 object produces equal evidence and rationale.
Rationale includes:

- `projection:explicit_need_to_ask`
- `projection:relevance_unknown`

No text inference, semantic matching, LLM use, retrieval, or hidden capability
matching is allowed.

### R8 — STOP before Relevance / Curiosity / Initiative / Conversation

C2 is read-only and derivational. It must not select/reselect capabilities or
paths, rerun Authorization, plan/acquire evidence, execute, persist, learn,
modify Memory/world model, or create new cognitive/Relevance/Curiosity/
Initiative/Conversation authorities.

It must preserve:

- `relevance_determined = False`
- `question_worthiness_determined = False`
- `question_candidate = None`
- `ask_now = False`

## Permanent distinctions

`NEED_TO_ASK != QUESTION_WORTHINESS`

`NEED_TO_ASK != RELEVANT`

`NEED_TO_ASK != QUESTION_CANDIDATE`

`UNKNOWN RELEVANCE != NEGATIVE RELEVANCE`

`PROJECTION != CURIOSITY INVOCATION`

`QUESTION_CANDIDATE != ASK NOW`

## RED condition

Before GREEN, R1–R8 must fail only because
`app.governed_self_epistemic_need_curiosity_evidence_projection` does not yet
exist. Existing tests must remain unaffected.
