# ROBY XI.2 — INTEL-G7 — G6 EVALUATION → EXPLICIT HUMAN APPROVAL — SURGICAL GREEN

## Certified entry baseline

- INTEL-G6 SURGICAL GREEN: CERTIFIED / CLOSED
- 14,093 PASS
- Ruff clean
- 0 FAIL
- INTEL-G7 CONTRACT RED: VALIDATED / CLOSED with 5 intentional missing-module failures

## Productive change

G7 adds `app/governed_g6_explicit_human_learning_approval.py`, a narrow source-neutral seam
from an eligible G6 `REVIEW_REQUIRED` evaluation into the existing M369 explicit-human-approval
semantics.

The seam preserves exact linkage to the deterministic G6 evaluation fingerprint, source learning
candidate, policy candidate, approval request, human response reference, approver, and scope.
Only an exact explicit approval emits `GovernedApprovedLearningEvidence`.

The existing `M369ExplicitHumanLearningApprovalEvidenceFoundation` receives one small public
classification entry point, `classify_explicit_response()`. Its historical Curiosity contract
continues to use the same vocabulary and behavior; no second approval authority is introduced.

## Contract correction discovered during GREEN

The frozen RED AST test simultaneously required the public class name
`GovernedApprovedLearningEvidence` and rejected the substring `ApprovedLearningEvidence` anywhere
in the module. Those conditions are textually contradictory. The test was corrected minimally to
reject forbidden historical symbols as exact AST identifiers/imports instead of substrings. No
behavioral obligation was weakened.

## Frozen behavior

- Exact-linked G6 `REVIEW_REQUIRED` + explicit approval → `APPROVED` and one source-neutral
  governed approved-learning evidence object.
- Wrong linkage → `ABSTAIN` before approval semantics.
- A non-review G6 state cannot be human-overridden into approval.
- Existing rejection, deferral, uncertainty, and abstention vocabulary is reused.
- No Curiosity or preference provenance is fabricated.
- No M366.6 materialization, Memory, persistence, runtime wiring, Library, Services, Planning,
  execution, research, background work, or parallel manager/authority is added.

## STOP

`APPROVED != PERSISTED`.

G7 stops at source-neutral explicit human-approved learning evidence. Do not extend this gate into
materialization or Memory. Any later durable path requires a separate architectural reconciliation.

## Assistant-side verification

- Frozen G7 contract: 5 PASS.
- Focused G7 + historical M369 approval/materialization/productive wiring/SafeLearning: 55 PASS.
- Syntax validation: PASS.
- M361 quality baseline regenerated and verified separately before packaging.
- Full suite and Ruff remain authoritative in the user's local environment.
