# ROBY XI.2 — GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST
## MODEL/BACKEND CANDIDATE BENCHMARK RECONCILIATION

Status: COMPLETE / PENDING OWNER CERTIFICATION

## Certified entry

- Benchmark POST-GREEN reconciliation: CLOSED / OWNER-CERTIFIED.
- Future-horizon reconciliation: CLOSED / OWNER-CERTIFIED.
- Owner baseline: 13,634 PASS / 0 FAIL, Ruff CLEAN.
- CAP-02 / `memory_gateway` remains the sole Memory authority.
- `CognitiveMemoryRecall` remains the productive consumer boundary.

## Scope

This block selects what is worth benchmarking next. It does not install a model,
download weights, add a runtime dependency, execute neural inference, or admit a
provider into the productive recall path.

The existing strategy remains a local/offline cross-encoder over candidates that
have already passed deterministic Memory eligibility.

## Existing dependency reconciliation

The current product does not already integrate the candidate neural runtime
families reviewed for this seam. Therefore model suitability and dependency
admission remain separate decisions. No dependency is added by this block.

## Candidate reconciliation

### Primary model candidate: BAAI/bge-reranker-v2-m3

Classification: SELECTED_FOR_BENCHMARK_FIRST / NOT_ADMITTED.

Reasons:
- cross-encoder/reranker semantics match the existing advisory seam;
- multilingual positioning fits the Spanish-first benchmark requirement;
- Apache-2.0 licensing is compatible with a broadly reusable governed baseline;
- query/passage scoring avoids any requirement for a vector database or durable
  embedding store;
- its published architecture is compatible with the local model family already
  considered by the strategy reconciliation.

The checkpoint is not yet authorized for productive use. Its actual Spanish
quality and Owner-hardware latency must be measured by the governed benchmark.

### Backend candidate: ONNX Runtime CPU

Classification: SELECTED_FOR_BENCHMARK_FIRST / NOT_ADMITTED.

Reasons:
- local/offline CPU inference matches the privacy boundary;
- ONNX Runtime provides an official CPU runtime for Windows;
- CrossEncoder tooling supports ONNX export, optimization, and CPU-oriented
  dynamic quantization.

This selection does not assert that a validated ONNX artifact for the primary
checkpoint already exists in ROBY. Export/conversion fidelity, tokenizer parity,
score parity, packaging, and Owner-hardware latency require a later controlled
benchmark block.

### jinaai/jina-reranker-v2-base-multilingual

Classification: HOLD / NOT_PRIMARY.

It is multilingual and publishes ONNX artifacts, including quantized variants,
but its current model card identifies a non-commercial license and documented
Python loading uses remote custom code. Those constraints are unnecessary for
ROBY's first governed candidate while a permissively licensed alternative exists.

### cross-encoder/ms-marco-MiniLM-L12-v2

Classification: NO-GO_FOR_PRIMARY_SPANISH_BENCHMARK.

It is a compact Apache-2.0 cross-encoder with ONNX support, but its published
language scope is English. It therefore does not satisfy the Spanish-first model
selection criterion for the primary candidate.

## Frozen selection

- STRATEGY: LOCAL_OFFLINE_CROSS_ENCODER
- PRIMARY_MODEL_CANDIDATE: BAAI/bge-reranker-v2-m3
- PRIMARY_BACKEND_CANDIDATE: ONNX_RUNTIME_CPU
- MODEL_STATUS: SELECTED_FOR_BENCHMARK_NOT_ADMITTED
- BACKEND_STATUS: SELECTED_FOR_BENCHMARK_NOT_ADMITTED
- PROVIDER: NONE
- MODEL_DOWNLOAD: NOT_AUTHORIZED_BY_THIS_BLOCK
- RUNTIME_INSTALLATION: NOT_AUTHORIZED_BY_THIS_BLOCK
- PRODUCTIVE_INTEGRATION: NOT_AUTHORIZED
- PRIVATE_DATA_BENCHMARK: FORBIDDEN
- NETWORK_DURING_BENCHMARK_INFERENCE: FORBIDDEN
- VECTOR_STORE: FORBIDDEN
- EMBEDDING_PERSISTENCE: FORBIDDEN
- BACKGROUND_INDEXING: FORBIDDEN
- NEW_AUTHORITY: NONE
- PRODUCTIVE_PYTHON_DELTA: ZERO
- TEST_DELTA: ZERO
- DEPENDENCY_DELTA: ZERO

## Required evidence before admission

The next experimental contract must keep model acquisition separate from offline
benchmark execution and must record the exact checkpoint/artifact identity. It
must demonstrate:

- 100 percent governance invariants;
- zero lexical-exact regressions;
- positive semantic MRR and NDCG delta;
- strict-majority improvement on qualified semantic cases;
- deterministic fallback compatibility;
- unchanged candidate membership;
- p50, p95, and maximum latency on Owner hardware;
- local/offline inference after acquisition;
- score validity and stable mapping into the existing [0, 1] advisory contract;
- parity checks for any converted or quantized artifact;
- no private-content transmission.

No universal latency threshold is invented here. The Owner measurement remains
the basis for a later admission decision.

## Next governed block

GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST — MODEL/BACKEND BENCHMARK CONTRACT
DESIGN

That block may define acquisition provenance and an offline experimental harness,
but it must STOP before model download, runtime installation, or productive
integration unless those actions are separately and explicitly authorized.
