# ROBY XI.2 — Existing Authorization Execution-Boundary and Evidence-Gate Reconciliation

STATUS: RECONCILIATION COMPLETE / PENDING OWNER CERTIFICATION. Acquisition NO-GO.

## Certified entry

Owner-certified acquisition authorization POST-GREEN: `ruff check .` CLEAN; `pytest -q`: 13,650 PASS / 0 FAIL (307.14s); M361 regenerated. This documentation increment requires its own Owner certification.

## Existing authorities and non-duplication

- `core/cognitive_memory_neural_acquisition_authorization_contract.py` is a **pure preflight predicate**, not an execution authority, identity provider, signature verifier, downloader, or grant issuer. Its positive outcome `ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION` is not executable authorization.
- `docs/M394_4_GOVERNED_EXTERNAL_RESOURCE_AUTHORIZATION.md` documents `ExternalResourceRegistryAuthority` as the canonical declarative resource registry/authorization authority for M394. Its `authorized` state is explicitly not connection, activation or operating-system permission. Do not reuse this registry as a downloader or treat its declarative authorization as sufficient executable permission.
- `app/governed_independence_authorization_boundary.py` has `GovernedIndependenceAuthorizationBoundaryV1`: read-only/consultative initiative eligibility with `execution_authorized=False`, `executes_actions=False`. This is not model-acquisition permission.
- `app/governed_long_horizon_investigation_a2_authorization_reentry.py` identifies `GovernedMultiStepInvestigationAuthorizationReentryV1` as the canonical investigation Authorization authority and explicitly separates A2 from Execution. Investigation authorization must not be silently repurposed into external model acquisition.
- Existing governed external resource, capability and Execution boundaries must be reviewed for **exact action-specific ownership** before wiring any acquisition path. No universal model-acquisition execution grant authority has been established by this reconciliation.
- `memory_gateway` remains the sole Memory authority. No new AuthorizationManager, acquisition agent, autonomous loop or parallel authority.

## Execution boundary: required sequence, not implemented

1. An Owner-specified action-specific acquisition request must be bound to immutable repository revision, source, artifact allowlist, destination, network and resource budget, privacy and evidence ledger.
2. Pure preflight validation may deny or mark the request eligible for separate Owner invocation. It cannot issue a credential or start execution.
3. Existing canonical executable-authorization path must be positively identified, with explicit Owner identity and scope verification, before an acquisition operation can be designed. Missing canonical mapping => STOP / NO-GO.
4. At execution time, authoritative checks must verify authentic Owner approval, request-to-approval cryptographic or equivalent trustworthy provenance, current clock expiry, revocation, replay protection and exact immutable scope. Nonempty synthetic `signed_evidence` is not verification.
5. A distinct, explicit Owner invocation is required after successful authorization. This step does not exist here and is NOT authorized.
6. Artifact transfer, quarantine, digest verification, benchmark, ONNX export, runtime installation and admission each require independent later gates. No approval carries forward implicitly.

## Evidence gate matrix

| Gate | Current evidence | Disposition |
|---|---|---|
| RED/GREEN pure preflight contract | 8 contractual tests GREEN; 13,650 Owner PASS | CLOSED for pure predicate only |
| Owner identity and signed attestation authenticity | Synthetic nonempty evidence field only | OPEN / NO-GO |
| Current-time expiry and revocation | Timestamp ordering and boolean fixture only | OPEN / NO-GO |
| Replay protection and request binding | Matching IDs, no verified unique execution token | OPEN / NO-GO |
| Immutable upstream revision and actual provenance | 40-hex syntax; no verified upstream commit | OPEN / NO-GO |
| Revision-specific license and artifact inventory | Declared license and exact names; no independent audit | OPEN / NO-GO |
| Artifact SHA-256 / tokenizer-config provenance | No acquired or verified files | OPEN / NO-GO |
| Destination sandbox, symlinks and implicit caches | Lexical path validation only | OPEN / NO-GO |
| Network endpoints, redirects, telemetry and resource enforcement | Declared constraints, no executor | OPEN / NO-GO |
| Owner hardware, reference/ONNX parity and benchmark | No model/runtime/measurements | OPEN / NO-GO |
| Productive Memory integration or model admission | Not requested, not authorized | NO-GO |

## Surgical reconciliation decision

Documentation only. No changes to production code, tests, imports, dependencies, acquisition runtime, model artifacts, network or productive capabilities. Preserve RED/GREEN and Owner-corrected imports. The architectural distinction between declarative eligibility, canonical authorization, and executable invocation is mandatory. Next possible stage is a narrow **EXISTING ACTION-SPECIFIC AUTHORIZATION OWNER MAPPING AND TRUST-EVIDENCE CONTRACT DESIGN**, only after Owner certification of this reconciliation. That stage would design gates, not download or install anything.

## STOP

No acquisition, downloads, ONNX export, runtime installation, inference, model admission or autonomous external action. A preflight positive result never overrides a missing execution authorization.
