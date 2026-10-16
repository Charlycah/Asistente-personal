# ROBY XI.2 — GOVERNED MODEL/BACKEND ACQUISITION AUTHORIZATION CONTRACT RED

STATUS: CONTRACT RED / OWNER CERTIFICATION PENDING.

## Certified entry and surgical authority reconciliation

Owner certified the acquisition authorization CONTRACT DESIGN with Ruff CLEAN,
13,642 PASS / 0 FAIL. The DESIGN is the normative source for this RED.
`memory_gateway` remains sole Memory authority. Existing Authorization and
Official Runtime Capability Registry own permission and execution gates; the
existing `core/cognitive_maturity/governed_authorization_input_correspondence.py`
is read-only correspondence, explicitly NOT a new authorization decision owner.
Do not route approval through that correspondence or create a second authority.
The future named module below is a pure, non-executing validation contract,
not an approval engine or acquisition manager. The Owner remains the approver.

## Contract boundary and intentional RED

Eight deterministic synthetic tests live at
`tests/architecture/test_governed_model_backend_acquisition_authorization_contract_red.py`.
They import the deliberately absent
`core.cognitive_memory_neural_acquisition_authorization_contract`.
Expected RED: eight `ModuleNotFoundError` failures, all unrelated tests green,
Ruff clean. The future GREEN must implement only pure request/approval
validation, reusing existing Authorization decisions rather than minting them.

The fixture defines `AcquisitionAuthorizationRequest`,
`OwnerAcquisitionApproval`, `acquisition_authorization_decision`, and
`phase_can_authorize_next` as future contract expectations, not product APIs.
The synthetic positive result `ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION`
means only preflight eligibility, never permission to fetch automatically.

Test coverage: explicit request/approval binding; expiry, revocation and
forgery; pinned revision and license evidence; allowlisted source and artifact
scope; destination traversal/private roots; resource and privacy bounds;
immutable evidence linkage and phase mismatch; pure, offline and no automatic
phase transition. Tests must not use network, weights, credentials or runtime.

## Deliberate STOP

NO MODEL DOWNLOAD; NO ONNX EXPORT; NO RUNTIME INSTALL; NO REAL INFERENCE;
NO PRODUCTIVE MEMORY INTEGRATION; NO AUTOMATIC ACQUISITION.
The eight expected RED failures are not permission to advance without Owner
certification. After RED Owner certification: surgical GREEN only.
