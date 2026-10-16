# ROBY XI.2 — Long-Horizon Investigation A2 → E2 Execution GREEN

## Certified incoming baseline

13,643 PASS + Ruff clean.

The user-corrected A2 GREEN import ordering remains integrated byte-for-byte before this block.

## Governed cut implemented

The certified exact canonical A2 result now enters the existing
`GovernedMultiStepInvestigationExecutionReentryV1` exactly once. The bridge forwards the exact
`authorization_result.authorization_reentry` object together with the caller-supplied `now`.
It does not instantiate a second execution gateway and does not route through the generic
long-horizon evidence-execution adapter.

The existing E2 owner remains the single execution authority. It performs the one Level-2
read and the canonical episode `record_acquisition` transition. The long-horizon bridge only
validates entry lineage, delegates once, validates the returned E2 lineage, and preserves the
canonical result.

## Exact success semantics

A successful E2 must be canonical `ACQUIRED`, preserve episode/A2/P2/R2/source/snapshot
lineage, use a new execution id, contain the exact evidence envelope returned by the existing
owner, and preserve that owner's exact resulting episode state. The resulting episode must be
step 2, `AWAITING_REENTRY`, with `remaining_acquisitions == 0`, one execution invocation and
one episode-record invocation.

Only that exact recorded E2 may expose
`eligible_for_existing_reasoning_reentry=True`. The bridge does not invoke Reasoning.

## Fail-closed semantics

Non-eligible A2 stops before the E2 owner. Owner exceptions become `REVIEW_REQUIRED` after one
attempt and never retry. Canonical `STOPPED` E2 is preserved without reasoning eligibility.
Unexpected owner status, A2 identity mismatch, or acquired-E2 lineage mismatch becomes
`REVIEW_REQUIRED`; forged evidence is not exposed as trusted evidence.

## Explicit non-capabilities

This block does not plan, authorize, reason, create questions, modify Memory, modify World
Model, retry execution, persist new state independently, or start background work. It does not
create a second executor and it does not perform a second episode-evidence admission.

## Next residual

Exact canonical recorded E2 + `eligible_for_existing_reasoning_reentry` → surgical
reconciliation against the existing second Reasoning re-entry / terminal episode closure owner.
