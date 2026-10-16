# ROBY XI.2 — GOVERNED MODEL/BACKEND ACQUISITION AUTHORIZATION CONTRACT DESIGN

STATUS: DESIGN CLOSED / OWNER-CERTIFIED.

## Certified entry and authority reconciliation

PRE-ACQUISITION READINESS RECONCILIATION: CLOSED / OWNER-CERTIFIED.
Owner evidence: Ruff CLEAN, 13,642 PASS / 0 FAIL, M361 PASS.
This DESIGN does not authorize acquisition and does not recertify itself.
Existing Authorization authority is reused; no independent approval engine,
acquisition manager, neural provider, planner, or parallel authority is created.
`memory_gateway` remains sole Memory authority and `CognitiveMemoryRecall`
remains its productive recall consumer. Neural reranking stays optional,
advisory, post-eligibility and bounded by deterministic fallback.

## Scope and frozen candidate

MODEL_REPOSITORY: `BAAI/bge-reranker-v2-m3`.
BACKEND_CANDIDATE: ONNX Runtime CPU / `CPUExecutionProvider`.
STATUS: selected for evaluation only, NOT acquired, verified, admitted or run.
A candidate repository is not an immutable revision or a trusted artifact.

## Authorization request contract — fields required before a decision

A future explicit Owner request MUST include:

1. Unique request identifier, requester, approving Owner, decision timestamp,
   intended experiment and rationale, and bounded authorization expiry.
2. Canonical repository, exact immutable 40-hex commit/revision and approved
   upstream source URLs or domain allowlist; never `main` or moving tags.
3. License evidence tied to that exact revision, permitted use assessment,
   redistribution/attribution constraints and explicit Owner acceptance.
4. Exact expected artifact names, purposes, sizes if known, expected upstream
   digests where verifiable, and allowed tokenizer/config/weight formats.
5. Owner-approved isolated local destination and maximum bytes/files; prohibit
   traversal, symlinks escaping the root, implicit caches and overwrite of
   productive assets or personal library files.
6. Explicit network endpoints, retrieval method, timeout, retry and resource
   limits; no arbitrary redirects, remote code, telemetry or credentials.
7. Privacy declaration: public artifacts only; no private books, conversations,
   Memory contents, local paths, credentials or user data transmitted.
8. Proposed evidence ledger location and hash-verification procedure, with
   immutable request-to-result linkage and denial/failure reasons.
9. Separate decisions for model acquisition, runtime installation, ONNX export,
   verification, offline benchmark and admission review; none is implied.
10. Owner confirmation of whether acquisition may occur now, as a distinct
    explicit action AFTER this design and its contractual RED/GREEN stages.

Unknown revision, missing license proof, ambiguous artifact set, unbounded
network, destination conflict or incomplete privacy controls => NO-GO.
Do not invent pinned commits, hashes, model sizes, licenses at pinned commits,
ONNX availability, package versions, Owner hardware or latency budgets.

## Decision semantics and scope

Default decision: DENY / NO-GO. A later approval is narrowly scoped to the
specified immutable revision, source, artifact set, destination, resource
limits, expiry and action. It is not transferable or reusable for changed
artifacts. Approval must be explicit, auditable, revocable and time-bounded.
Approval of a request does not trigger an automatic download. A separate
Owner-invoked acquisition action and recorded preflight are required.
A failure, revocation, expiration, mismatch, partial acquisition or hash
failure must stop, quarantine incomplete artifacts and record evidence;
never retry by switching to a different source, revision or provider.

## Separation of phase gates

PRE-ACQUISITION AUTHORIZATION: identity, license, privacy, scope, isolation.
ACQUISITION: separate bounded retrieval, only after explicit authorization.
VERIFICATION: independent integrity and provenance review of local artifacts.
ONNX EXPORT: separately authorized conversion, pinned tools and new hashes.
RUNTIME INSTALLATION: separate Owner authorization and package identity.
OFFLINE BENCHMARK: separately approved, synthetic Spanish data, network off,
CPUExecutionProvider, reference/ONNX parity, governance, quality and latency.
ADMISSION REVIEW: independent evidence decision; `GO_FOR_ADMISSION_REVIEW`
never grants productive admission or permission for earlier phases.
No phase automatically authorizes any subsequent phase.

## RED obligations — next authorized engineering horizon

The next CONTRACT RED should be executable without downloads, neural runtime,
weights, credentials or network. Deterministic fixtures must challenge:
missing/expired/revoked approval; unpinned revision; license mismatch;
unapproved file/domain/destination; traversal/symlink escape; unbounded
resources; forbidden private data; scope expansion; partial retrieval;
unauthorized phase transitions; automatic network/download triggers;
forged approval; invalid or missing evidence. Tests should assert DENY and
no side effects, without creating an alternate Authorization authority.
The contract should reuse existing canonical authorization/integration
seams after an explicit pre-RED reconciliation, not invent a new manager.

## Frozen change inventory and STOP

PRODUCTIVE_CODE_DELTA: ZERO
CONTRACT_CODE_DELTA: ZERO
TEST_DELTA: ZERO
DEPENDENCY_DELTA: ZERO
NEW_AUTHORITY: NONE
MODEL_DOWNLOAD: NONE
RUNTIME_INSTALLATION: NONE
ONNX_EXPORT: NONE
REAL_INFERENCE: NONE
PRODUCTIVE_ADMISSION: NONE

NEXT: GOVERNED MODEL/BACKEND ACQUISITION AUTHORIZATION CONTRACT RED,
only after Owner certifies this design and the canonical Authorization seam
is reconciled against actual code and existing tests.
STOP before acquisition, runtime installation, ONNX conversion, inference,
private-data exposure, or productive Memory integration.
