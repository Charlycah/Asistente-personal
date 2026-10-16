# ROBY XI.2 — MODEL/BACKEND BENCHMARK POST-GREEN RECONCILIATION

STATUS: LOCAL DOCUMENTARY RECONCILIATION COMPLETE / OWNER CERTIFICATION PENDING.

## Owner evidence and certified starting point

Owner execution after the E731 surgical fix: Ruff `All checks passed!`;
`pytest -q`: 13,642 PASS / 0 FAIL, 358.37 seconds. The M361
reproducibility test was included in that complete passing suite.
This evidence certifies the preceding SURGICAL GREEN, not this new ZIP.

## Architectural reconciliation

- `memory_gateway` remains the sole governed Memory authority.
- Existing `CognitiveMemoryRecall` remains the productive recall consumer.
- Existing optional reranking integration and deterministic fallback are
  not changed or bypassed.
- `core/cognitive_memory_neural_benchmark.py` remains the synthetic,
  evaluation-only benchmark; no new productive benchmark authority exists.
- `core/cognitive_memory_neural_model_backend_benchmark_contract.py`
  is a pure evidence-validation contract, not a model runner, provider,
  acquisition service, manager, agent, planner or authorization authority.
- RED's eight contract tests are GREEN in the Owner's full suite.
- The Owner-corrected RED imports and E731 local `def rank` remain intact.
- No dependencies, network calls, embeddings, vector database, private
  library traversal, ONNX runtime, model weights or inference were added.

## Contract-to-design consistency

Frozen benchmark candidate: `BAAI/bge-reranker-v2-m3`, Apache-2.0;
benchmark backend: ONNX Runtime CPU / `CPUExecutionProvider`.
These are **selected for future evaluation only**, not installed or admitted.
Manifest validation requires immutable 40-hex revision, artifact hashes,
ONNX digest, CPU provider, corpus/hardware/runtime identification.
Reference parity requires finite values, absolute tolerance `1e-4`,
and identical ranking. Latency evidence requires cold start, warmup,
samples, p50/p95/max, with no universal latency budget.
All governance, offline, privacy, quality and parity gates are conjunctive.
`GO_FOR_ADMISSION_REVIEW` is not authorization for acquisition, model
execution, productive integration or admission. Invalid evidence is NO-GO.

## Delimitations and residual evidence

The GREEN validates synthetic contracts and decision logic. It does NOT
establish that the named model has been pinned, downloaded, licensed for
this deployment, converted to ONNX, verified, benchmarked on Owner CPU,
or measured against reference inference. Artifact manifests and report
values in the RED tests are synthetic; no real model/backend evidence
has been collected. A future benchmark requires separate governed
authorization for each acquisition, verification and offline measurement
phase. Any eventual productive admission requires its own review.

## Change inventory and protected boundaries

PRODUCTIVE_CODE_DELTA: ZERO
CONTRACT_CODE_DELTA: ZERO
TEST_DELTA: ZERO
DEPENDENCY_DELTA: ZERO
DOC_DELTA: THIS POST-GREEN RECONCILIATION + MASTER PLAN ENTRY
MODEL_ACQUISITION: NONE
ONNX_EXPORT: NONE
RUNTIME_INSTALLATION: NONE
REAL_INFERENCE: NONE
NEW_AUTHORITY: NONE

## Decision and STOP

CLOSE the model/backend contract implementation horizon on Owner
certification of this documentary ZIP. NEXT: a separate governed
pre-acquisition readiness/authorization decision, not automatic execution.
STOP before downloading a checkpoint, installing neural runtimes,
exporting ONNX, benchmarking real inference or admitting a provider.
