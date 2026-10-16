# ROBY XI.2 — Governed Model/Backend Action-Specific Authorization Extension Contract DESIGN

STATUS: DESIGN COMPLETE / OWNER CERTIFICATION PENDING. MODEL_ACQUISITION: NO-GO.

## Authority and source baseline

Entry: Owner-certified `GOVERNED MODEL/BACKEND CANONICAL AUTHORIZATION → EXECUTION SURGICAL RECONCILIATION`: Ruff CLEAN, 13,650 PASS / 0 FAIL (290.45 s). Consulted that reconciliation, prior Owner-mapping DESIGN, acquisition preflight contract, existing A2→E2 investigation boundary, official runtime capability registry, external-resource registry, and Level 2 read-only execution gateway. This document is **only a conditional extension contract design**. It neither identifies a proven executable `MODEL_ACQUISITION` grant nor grants one.

## Canonical ownership decision

1. **No second Authorization authority:** `GovernedMultiStepInvestigationAuthorizationReentryV1` is canonical **for investigation**; its scope must not be silently generalized to downloads. `GovernedMultiStepInvestigationExecutionReentryV1` remains investigation-specific.
2. **No second Execution authority:** `GovernedLevel2ReadOnlyExecutionGatewayV1` is read-only; it is not a model downloader. Official runtime capability registry entries must be reviewed for exact side-effect and permission declarations before any proposed action mapping.
3. `ExternalResourceRegistryAuthority` governs declarations, not network transfer. `GovernedIndependenceAuthorizationBoundaryV1` is consultative. `acquisition_authorization_decision` remains a pure preflight predicate; its positive result is never an executable token.
4. **UNMAPPED:** no existing Owner-authenticated, live-revocation-aware, replay-safe executable action gate for `MODEL_ACQUISITION` has been proven. The Owner must select and certify an existing canonical seam and its scope **before** a RED implementation can be specified. Absence of a seam is a STOP, not a reason to invent a new manager.

## Proposed extension contract — conditional, not implemented

The following requirements attach to a **future separately Owner-approved action-specific extension of the verified canonical Authorization→Execution path**, not to existing investigation permissions:

| Contract boundary | Mandatory input / verification | Failure behavior |
|---|---|---|
| Canonical action mapping | Exact registered capability ID, authority, declared side effects, action `MODEL_ACQUISITION`, Owner-approved integration point | UNMAPPED → DENY |
| Immutable request | Request ID and digest, action, Owner, repository `BAAI/bge-reranker-v2-m3`, independently verified pinned commit, artifact allowlist + SHA-256, isolated destination, license provenance, network/resource/privacy limits | Missing/mismatch → DENY |
| Owner trust evidence | Authenticated Owner approval from an independently trusted channel, verifiable attestation bound to digest, action, scope and intended invocation | Synthetic/nonempty string alone → DENY |
| Invocation-time validity | Trusted current time, expiry/not-before, authoritative live revocation, fail-closed unavailable source | Expired/revoked/stale → DENY |
| Single-use authorization | Nonce/invocation ID, atomic replay ledger, exact approval-to-execution binding; no implicit multi-use grant | Duplicate/replay → DENY |
| Execution handoff | Distinct action-scoped decision checked by official Execution boundary; actual source, redirects, paths/symlinks, file/byte/time ceilings verified before and during effects | No execution, quarantine any partial result |
| Audit | Tamper-evident decision and outcome evidence, no secrets/private payloads; failure of required audit is fail-closed | DENY / STOP |
| Phase separation | Acquisition only, never automatic runtime install, ONNX export, verification, benchmark, admission or production | Independent Owner gate required |

## Contractual state machine (non-executable)

`UNMAPPED` → STOP. Once a canonical mapping is **separately** certified, `REQUESTED` → `PREFLIGHT_ELIGIBLE` or `DENIED`. `PREFLIGHT_ELIGIBLE` is not executable. Only an authenticated, live, non-revoked, non-replayed action-specific Owner decision could yield `AUTHORIZED_FOR_EXACT_INVOCATION` at the canonical Authorization boundary. A separate Owner-invoked Execution boundary must revalidate the exact scope and record `EXECUTED_VERIFIED` or `FAILED_QUARANTINED`. No phase inherits another phase's grant. This document implements **none** of these states or transitions.

## Negative contract examples for future RED, contingent on Owner approval

Reject forged Owner approval, wrong digest, changed model revision, license or artifact digest, expired or revoked approval, unavailable revocation source, replay, unauthorized redirect, symlink escape, extra artifact, resource overflow, private-data access, missing audit, and attempted transition to runtime installation/ONNX export/inference. Fixtures must be deterministic, offline and without side effects. Tests must target the **verified existing authority seam**, not a new AuthorizationManager or downloader.

## Required Owner decisions before RED

1. Identify the exact existing canonical Authorization boundary, registry capability entry and official Execution integration point that can legally own this side-effectful action, or explicitly keep `UNMAPPED / NO-GO`.
2. Select the already governed Owner identity, approval evidence, revocation and replay authorities; if absent, reconcile them under existing governance before code.
3. Certify immutable scope and independent provenance/license/hash verification policy, including audit and filesystem/network isolation.
4. Explicitly authorize only the **contractual RED** after reviewing the above mapping; RED is not permission to acquire anything.

## Change and certification record

Document and master-plan update only. No Python, test, dependency, model, runtime, registry entry or product capability changes. Preserve protected architecture changelog, capability inventories, ordered imports, line-length limits and M361. Owner commands: `python scripts/clean_project_caches.py`; `python scripts/generate_quality_baseline.py`; `ruff check .`; `pytest -q`. Expected existing suite: 13,650 PASS / 0 FAIL, subject to Owner verification.

**STOP: MODEL_ACQUISITION NO-GO. No downloads, runtime installation, ONNX export, inference, benchmark execution, model admission or productive integration.**
