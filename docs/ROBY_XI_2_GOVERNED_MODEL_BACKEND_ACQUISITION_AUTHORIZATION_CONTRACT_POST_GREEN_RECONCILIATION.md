# ROBY XI.2 — Governed Model/Backend Acquisition Authorization Contract Post-GREEN Reconciliation

## Entry and Owner evidence

Previous DESIGN and RED were Owner-certified. SURGICAL GREEN Owner evidence:
`python scripts/clean_project_caches.py`, `python scripts/generate_quality_baseline.py`,
`ruff check .` (All checks passed), `pytest -q` (13,650 passed in 318.17s).
This evidence certifies the previous GREEN baseline, not the new documentation ZIP.

## Contract-to-code reconciliation

- Canonical existing Authorization retains executable authority; the new
  `core.cognitive_memory_neural_acquisition_authorization_contract.py` is
  a pure preflight validator, not a second authorization authority.
- `AcquisitionAuthorizationRequest` and `OwnerAcquisitionApproval` are frozen
  data carriers. `acquisition_authorization_decision` defaults to `DENY`.
- Matching request/owner/approval, explicit action, fixed repository,
  40-character hex revision, declared license and nonempty license evidence,
  source allowlist, exact artifact set, isolated relative paths, positive
  resource bounds, and public-only privacy are checked.
- `phase_can_authorize_next` always returns `False`: no phase inheritance.
- Eight RED tests are now GREEN, within the 13,650 Owner PASS.
- The module contains no download, network, runtime, ONNX, neural inference,
  Memory write, or productive integration entrypoint.

## Explicit boundaries and evidence gaps

- A nonempty `signed_evidence` string is NOT cryptographic verification.
  The RED synthetic fixture uses a synthetic attestation. Real provenance,
  signature authenticity, owner identity and revocation checks are NOT
  implemented by this pure contract.
- Timestamp ordering (`expires_at > decision_timestamp`) is NOT a live
  expiry check. The existing Authorization authority must check actual
  invocation time and revocation immediately before any authorized action.
- A 40-character hex revision is syntactic pinning, not proof of existence,
  repository provenance or actual artifact SHA-256 integrity.
- A declared Apache-2.0 license is not a pinned-revision license audit.
- Lexical path constraints are not a filesystem/symlink sandbox. Real
  destination isolation and filesystem access checks remain external gates.
- Positive `ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION` is a preflight
  assessment ONLY, never executable permission or permission to download.
- The earlier experimental benchmark contract remains separate from
  acquisition, verification, benchmark and admission decisions.

## Architecture and disposition

- `memory_gateway` remains the sole Memory authority. No duplicate manager,
  planner, agent, Authorization authority, or autonomous acquisition loop.
- This reconciliation changes documentation only; no implementation, tests,
  dependencies, network operations, or model artifacts.
- Existing RED/GREEN tests and Owner-corrected imports remain untouched.
- Decision: CONTRACT POST-GREEN RECONCILED, pending Owner certification of
  this documentation package. Acquisition remains NO-GO.
- Next proposed horizon: EXISTING AUTHORIZATION EXECUTION-BOUNDARY AND
  EVIDENCE-GATE RECONCILIATION (documentary first); do not implement or
  execute acquisition without separate Owner approval.

## STOP

No download, ONNX export, runtime installation, inference, Memory integration,
model admission, or transition to another phase is authorized here.
