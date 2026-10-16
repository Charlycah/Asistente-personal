# M378.1 — CCI-08 Source-Owned Explainability Certification Evidence Reconciliation

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Scope

This surgery reconciles the cross-capability certification evidence exposed as stale by the M378 retirement. It changes diagnostic/certification evidence and current governance documentation only. It does not change production code, authority, persistence, stores, writers or runtime wiring.

## CCI-08 current meaning

CCI-08 remains `PASS_BY_DESIGN`: adaptive delivery cannot change cognitive identity/authority, while source-owned explainability derives presentation from canonical decision evidence without re-deciding it. The scenario does not claim a productive M377-to-explainability integration.

## Retired evidence

`core/intelligent_explanations.py`, the `explanation_profile` stage and its `AdaptivePersonalityProfile` dependency are removed from the current CCI-08 evidence contract.

## Current evidence

- `core/adaptive_personality.py`
- `core/governed_reasoning/explanations.py`
- `tests/test_m377_adaptive_personality.py`

Owner certification remains mandatory using the official ROBY quality gate.
