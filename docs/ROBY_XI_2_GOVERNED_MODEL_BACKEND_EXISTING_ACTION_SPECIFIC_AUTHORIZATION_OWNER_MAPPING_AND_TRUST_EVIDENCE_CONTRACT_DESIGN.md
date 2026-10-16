# ROBY XI.2 — Governed Model/Backend Existing Action-Specific Authorization Owner Mapping and Trust-Evidence Contract Design

STATUS: DESIGN COMPLETE / PENDING OWNER CERTIFICATION. ACQUISITION NO-GO.

## Entry and scope

Owner-certified execution-boundary/evidence-gate reconciliation: Ruff CLEAN; pytest 13,650 PASS / 0 FAIL (300.30 s), M361 regenerated. This is a **design-only** change: no new code, test, dependency, downloader, authority, model, network access or inference. Its certification is separate.

## Canonical authority mapping — existing code and documentation

| Action / phase | Existing canonical seam | Exact authority established? | Disposition |
|---|---|---|---|
| Declarative external-resource registration | `core/external_resource_registry.py`; `docs/M394_4_GOVERNED_EXTERNAL_RESOURCE_AUTHORIZATION.md` (`ExternalResourceRegistryAuthority`) | Declarative registration only; NOT OS/network execution | REUSE only for resource declarations; no execution grant |
| Consultative initiative | `app/governed_independence_authorization_boundary.py` (`GovernedIndependenceAuthorizationBoundaryV1`) | Read-only eligibility; `execution_authorized=False` | NOT acquisition permission |
| Long-horizon investigation A2 | `app/governed_long_horizon_investigation_a2_authorization_reentry.py` (`GovernedMultiStepInvestigationAuthorizationReentryV1`) | Investigation-specific authorization; Execution separate | NOT transferable to acquisition |
| Experimental model-acquisition preflight | `core/cognitive_memory_neural_acquisition_authorization_contract.py` | Pure syntactic/structural predicate | DENY or advisory eligibility; never executable |
| `MODEL_ACQUISITION` actual external transfer | No action-specific canonical execution-grant path verified in certified reconciliation | **UNRESOLVED** | NO-GO; no new manager or fallback grant |
| `RUNTIME_INSTALLATION`, `ONNX_EXPORT`, `VERIFICATION`, `OFFLINE_BENCHMARK`, `ADMISSION_REVIEW` | Distinct future action gates, no inherited permission | **UNRESOLVED** | Separate Owner authorization and contracts required |
| Memory write/read | Existing `memory_gateway` authority | Memory only | Never authorize acquisition or expose private data |

Do not infer a general-purpose acquisition permission from a similarly named Authorization class. An exact, reviewed integration seam and its test coverage must be established **before** any implementation of execution gating.

## Trust-evidence contract (design; no implementation)

A future action-specific invocation must bind, in a tamper-evident manner:

1. **Owner identity:** identity verified by the existing trusted human/Owner channel; approval provenance, authentication method and assurance level recorded. A string equal to `owner` is not proof.
2. **Exact request:** unique request ID, action `MODEL_ACQUISITION`, request digest, approved intent, immutable `BAAI/bge-reranker-v2-m3` commit (40-hex *plus independently verified provenance*), permitted artifact names/digests, revision-bound license evidence, source allowlist, isolated destination, privacy and network/resource ceilings.
3. **Approval authenticity:** independently verified signature or equivalent trusted approval record bound to that exact digest, Owner, action and scope. Nonempty `signed_evidence` is insufficient.
4. **Live validity:** trusted current clock, not-before/expiry, authoritative revocation check at invocation time; fail closed if unavailable or stale.
5. **Single-use / replay:** unique invocation identifier, nonce or equivalent replay ledger, atomic consumption by the canonical authority, duplicate/conflicting approval denial.
6. **Scope integrity:** immutable equality between approved request, proposed invocation and actual transfer plan; no source substitution, redirects, extra files, changed revision, implicit caches, credential/telemetry leakage or broadened permissions.
7. **Isolation:** independently resolved filesystem boundary and symlink/redirect protections; lexical relative-path checks alone are insufficient.
8. **Audit:** append-only or tamper-evident decision record including request digest, evidence references, denial reason, execution ID, timestamps, outcome, verification hashes and cleanup/quarantine evidence; no secret/private payloads in logs.
9. **Failure:** missing, unverifiable, revoked, expired, mismatched, ambiguous or replayed evidence => `DENY` and no side effects. Partial transfer => quarantine, no automatic retries or escalation.
10. **Separation:** approval of model acquisition never approves installation, export, benchmark, verification, admission or productive integration.

## Required contract states and transition boundary

`UNMAPPED` / `EVIDENCE_MISSING` / `EVIDENCE_INVALID` / `EXPIRED` / `REVOKED` / `REPLAYED` / `SCOPE_MISMATCH` => **DENY / STOP**. A successful pure preflight remains `ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION` only. A future authenticated canonical Authorization decision, if separately designed and Owner-certified, must still precede a distinct Owner-invoked execution action. No token, credential, approval or execution is issued by this design.

## RED design obligations — conditional future stage

Only after reconciling the actual canonical executable-authorization path, propose deterministic no-network RED fixtures for: forged Owner evidence; wrong request digest; revoked/expired approval at invocation time; stale revocation source; replay; revision/license/source/artifact mutation; symlink escape; unauthorized redirect; privacy and resource-budget violation; audit failure; no inheritance across phases; no side effects. Preserve existing 13,650 passing tests and Owner-corrected import ordering. Do not write a duplicate AuthorizationManager to make RED pass.

## Gate and disposition

DESIGN: COMPLETE / PENDING OWNER CERTIFICATION. Existing action-specific executable acquisition authority: **NOT ESTABLISHED**. Trust-evidence verifier: **NOT IMPLEMENTED**. Candidate model/runtime: **NOT ACQUIRED OR ADMITTED**. Next engineering step requires explicit Owner choice and a surgical reconciliation of the exact existing Authorization-to-Execution seam; this DESIGN alone does not authorize RED, GREEN or acquisition.

STOP: no download, runtime installation, ONNX export, inference, private-data access, benchmark execution, model admission or productive integration.
