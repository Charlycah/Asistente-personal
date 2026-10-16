# ROBY XI.2 — Canonical Authorization → Execution Surgical Reconciliation

STATUS: RECONCILIATION COMPLETE / PENDING OWNER CERTIFICATION. MODEL_ACQUISITION: NO-GO.

## Baseline and scope

Owner-certified previous action-specific mapping DESIGN: Ruff CLEAN, 13,650 PASS, 0 FAIL. This is documentary, evidence-based surgical reconciliation, not an implementation, authorization, or network operation. No new Authorization/Execution manager, planner, loop, module or test is introduced.

## Existing canonical paths inspected

| Existing seam | Contractual evidence | Authority limit for model acquisition |
|---|---|---|
| `app/governed_independence_authorization_boundary.py` / `GovernedIndependenceAuthorizationBoundaryV1` | `GovernedIndependenceAuthorizationReport` is `consultative=True`, `read_only=True`, `execution_authorized=False`, `executes_actions=False` | Not an executable acquisition approval |
| `app/governed_independence_authorization_productive_consumption.py` | Governed read-only authorization consumption | No transfer of permissions to new action classes |
| `app/governed_long_horizon_investigation_a2_authorization_reentry.py` | A2 admission names `GovernedMultiStepInvestigationAuthorizationReentryV1` as canonical authority; forbids execution and background work | Investigation-specific; cannot grant `MODEL_ACQUISITION` |
| `app/governed_long_horizon_investigation_e2_execution_reentry.py` | E2 admission names `GovernedMultiStepInvestigationExecutionReentryV1`; checks lineage from A2 | Existing investigation A2→E2 is not a general-purpose download seam |
| `app/governed_level2_read_only_execution_gateway.py` | `GovernedLevel2ReadOnlyExecutionGatewayV1` executes one-shot Level 2 read through existing official runtime capability gateway | Read-only evidence execution, not write/download/install permission |
| `app/runtime_capability_registry.py`, `core/capability_registry.py` | Capability metadata and execution eligibility must be checked against exact declared effects and permission scope | No inferred registration or action-specific acquisition grant |
| `core/external_resource_registry.py` | External resource registry owns declarations | Declaration is not network execution |
| `core/cognitive_memory_neural_acquisition_authorization_contract.py` | Pure immutable request/approval preflight; returns DENY or advisory eligibility | Nonempty synthetic attestation, static timestamp ordering and lexical path checks do not prove authentic live permission |

## Canonical ownership conclusion

The existing A2→E2 bridge **is real and specific to investigation**, but there is **no verified general action-specific Owner authentication, live revocation, replay prevention, request-digest binding and executable transfer gate for `MODEL_ACQUISITION`**. Do not rename/reuse investigation permission as model-acquisition permission. No new authority is justified by a naming gap. Preserve single Authority → Execution lineage and existing registry effects/permission rules; map any future action to a verified existing official runtime capability entry only after an explicit Owner design decision.

## Exact trust-evidence gap and required sequence

1. Owner request with immutable action, repository, pinned revision, artifact hashes, destination, source allowlist and resource/privacy bounds.
2. Independently trusted Owner authentication and tamper-evident approval tied to request digest. Synthetic `signed_evidence` strings cannot satisfy this.
3. Trusted current-time validity, live revocation and atomic replay check by an identified canonical Authorization authority.
4. Separate action-specific authorization result bound to one exact invocation; no cross-phase inheritance.
5. Existing official Execution gateway verifies scope, capability effects, provenance, redirects, symlinks, destination and byte/file ceilings immediately before and during any transfer.
6. Audit evidence, failure quarantine and explicit post-execution verification; never imply installation, ONNX export, benchmarking or product admission.

At present steps 2–5 are **not established for this action**. Outcome: `UNMAPPED / DENY / STOP`. No network call, model download, runtime install, ONNX export, inference or integration is authorized.

## Surgical disposition

- **REUSE:** current registry and existing Authorization/Execution architecture only within their certified scope.
- **DO NOT REUSE AS GRANT:** investigation A2→E2, Level 2 read-only gateway, resource registry or neural preflight for `MODEL_ACQUISITION`.
- **OPEN:** identify an exact canonical action-specific trust-evidence gate and Owner authentication mechanism; reconcile actual registry permissions and official runtime execution effects before any RED tests.
- **NO CODE CHANGE:** preserve certified Python, tests, imports, line lengths, protected architecture changelog and capability inventory.
- **NEXT GATE:** Owner review of this reconciliation and explicit decision whether to design a bounded extension of an existing canonical authorization/execution path; no RED/GREEN or acquisition authorized by this document.

STOP: ACQUISITION NO-GO.
