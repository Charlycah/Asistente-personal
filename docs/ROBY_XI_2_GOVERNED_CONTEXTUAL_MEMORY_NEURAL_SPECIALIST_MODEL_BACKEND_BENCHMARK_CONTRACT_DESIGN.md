# ROBY XI.2 — GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST
## MODEL/BACKEND BENCHMARK CONTRACT DESIGN

Status: COMPLETE / PENDING OWNER CERTIFICATION

## Certified entry

- Model/backend candidate reconciliation: CLOSED / OWNER-CERTIFIED.
- Owner baseline: 13,634 PASS / 0 FAIL, Ruff CLEAN.
- `memory_gateway` remains the sole Memory authority.
- `CognitiveMemoryRecall` remains the productive consumer boundary.
- The neural reranker remains advisory and post-eligibility only.

## Purpose

Freeze the experimental contract that a real model/backend pair must satisfy
before any download, runtime installation, inference, or productive admission.
This block defines evidence only. It does not execute the experiment.

## Candidate under contract

- MODEL: `BAAI/bge-reranker-v2-m3`
- MODEL_STATUS: SELECTED_FOR_BENCHMARK_NOT_ADMITTED
- BACKEND: ONNX_RUNTIME_CPU
- BACKEND_STATUS: SELECTED_FOR_BENCHMARK_NOT_ADMITTED
- STRATEGY: LOCAL_OFFLINE_CROSS_ENCODER

The model is evaluated only as a scorer of query/candidate pairs already admitted
by deterministic Memory eligibility. It receives no Memory, Learning,
Authorization, Planning, or Execution authority.

## Phase separation

The experiment must preserve four explicit phases:

1. ACQUISITION: separately authorized retrieval into an isolated experimental
   location; never implicit during benchmark execution.
2. VERIFICATION: revision, license, manifest, hashes, tokenizer/config/model
   identity, and runtime package versions are recorded before inference.
3. OFFLINE BENCHMARK: network disabled; synthetic non-private corpus only.
4. ADMISSION REVIEW: results are reviewed after measurement. A passing benchmark
   does not itself modify requirements or the productive recall path.

No phase may silently authorize the next one.

## Identity and provenance contract

A future executable benchmark must require an immutable experiment manifest with:

- canonical model repository identifier;
- pinned model revision/commit, never an unpinned moving branch;
- license observed for the pinned revision;
- exact filenames used for config, tokenizer and weights/artifacts;
- SHA-256 for every locally consumed model artifact;
- conversion/export tool versions when an ONNX artifact is generated;
- ONNX artifact SHA-256;
- Python and runtime package versions;
- execution provider exactly `CPUExecutionProvider`;
- quantization/optimization mode, or explicit `NONE`;
- benchmark corpus/version identifier;
- Owner hardware/runtime observations required for reproducibility.

A missing, changed, or unverifiable identity field is NO-GO for that run.

## Acquisition boundary

Acquisition and inference are separate operations.

- MODEL_DOWNLOAD_IN_THIS_BLOCK: FORBIDDEN
- RUNTIME_INSTALLATION_IN_THIS_BLOCK: FORBIDDEN
- IMPLICIT_NETWORK_FETCH_DURING_BENCHMARK: FORBIDDEN
- PRIVATE_CONTENT_DURING_ACQUISITION_OR_BENCHMARK: FORBIDDEN
- PRODUCTIVE_MODEL_CACHE_REUSE_WITHOUT_MANIFEST: FORBIDDEN

A later explicitly authorized acquisition may use the network only to obtain the
pinned public artifacts. The measured benchmark must then run offline from the
verified local experimental copy.

## Functional parity contract

The first real experiment must establish a reference scoring path and compare the
candidate ONNX path against it on the same synthetic pairs.

Parity must cover:

- identical tokenizer/config semantics for the measured inputs;
- finite scores for every pair;
- stable mapping of model output into the advisory `[0, 1]` relevance domain;
- ranking agreement sufficient to preserve benchmark decisions;
- explicit numerical-difference reporting, never silent tolerance;
- separate evidence for optimized or quantized variants.

No universal numeric tolerance is invented by this design. The CONTRACT RED must
freeze the tolerance before real inference is executed. If a quantized artifact
changes a benchmark decision or violates quality/governance gates, it is NO-GO
regardless of its latency improvement.

## Quality contract

The existing Owner-certified synthetic Spanish benchmark remains authoritative.
The real candidate must satisfy all existing gates:

- GOVERNANCE_INVARIANTS: 100_PERCENT
- CANDIDATE_MEMBERSHIP: UNCHANGED
- NEURAL_ADMISSION: FORBIDDEN
- LEXICAL_EXACT_REGRESSIONS: ZERO
- SEMANTIC_MRR_DELTA: POSITIVE_REQUIRED
- SEMANTIC_NDCG_DELTA: POSITIVE_REQUIRED
- SEMANTIC_CASE_IMPROVEMENT: STRICT_MAJORITY_REQUIRED
- NONFINITE_OR_INVALID_SCORE: NO_GO
- UNKNOWN_CANDIDATE_ID: NO_GO

The benchmark cannot add positives that were absent from deterministic eligibility.
A model that fails quality cannot be rescued by faster execution.

## Runtime and latency contract

Measurements must be made on Owner hardware with the verified local artifacts.
The report must include at least:

- cold-start/session-creation time separately from inference;
- warm-up policy and number of warm-up runs;
- measured sample count;
- per-case or per-batch latency observations;
- p50, p95 and maximum inference latency;
- candidate count and relevant input-length characteristics;
- execution provider confirmation;
- runtime/version identity;
- optimization/quantization identity.

`CPUExecutionProvider` is the only selected provider for the first experiment.
Fallback to another provider is not allowed silently.

No universal latency budget is frozen before Owner measurement. Latency is an
admission-review input, not permission to weaken quality or governance.

## Failure and fallback contract

Experimental model/backend failure must remain non-authoritative. The productive
recall contract continues to require exact deterministic fallback for absence,
unavailability, exception, abstention, invalid evidence, or rejected evidence.

The experimental harness must fail closed and report the reason when identity,
provenance, offline status, score validity, membership, parity, or quality gates
cannot be established.

## GO / NO-GO semantics

`GO_FOR_ADMISSION_REVIEW` means only that the measured candidate has produced the
required evidence. It does not mean productive admission.

Immediate `NO-GO` includes any:

- governance or membership violation;
- lexical-exact regression;
- non-positive required semantic quality delta;
- failure of strict-majority semantic improvement;
- invalid/non-finite scoring;
- unverified artifact identity or provenance;
- network access during measured inference;
- private-data use or transmission;
- unauthorized provider/runtime fallback;
- parity failure under the tolerance frozen before inference.

Only a later governed admission block may decide whether a benchmark-passing
model/backend becomes an optional injected specialist.

## RED obligations

The next CONTRACT RED must be executable without model weights or neural runtime.
It must use deterministic fakes/fixtures to prove that the future harness requires:

- pinned identity and artifact hashes;
- phase separation and offline measurement;
- exact CPU provider declaration;
- parity evidence and pre-frozen tolerance;
- all existing quality/governance gates;
- latency-report completeness;
- fail-closed GO/NO-GO semantics;
- no productive Memory/Learning/Authorization/Execution writes.

RED must fail because this model/backend experiment contract is not yet
implemented, never because a model cannot be downloaded or a runtime is absent.

## Frozen boundaries

- NEW_AUTHORITY: NONE
- PRODUCTIVE_PYTHON_DELTA: ZERO
- TEST_DELTA: ZERO
- DEPENDENCY_DELTA: ZERO
- MODEL_DOWNLOAD: FORBIDDEN
- RUNTIME_INSTALLATION: FORBIDDEN
- REAL_INFERENCE: FORBIDDEN
- PRODUCTIVE_INTEGRATION: FORBIDDEN
- VECTOR_STORE: FORBIDDEN
- EMBEDDING_PERSISTENCE: FORBIDDEN
- BACKGROUND_INDEXING: FORBIDDEN
- EXTERNAL_PRIVATE_CONTENT_TRANSMISSION: NOT_AUTHORIZED
- STOP_BEFORE_MODEL_OR_RUNTIME_ACQUISITION: YES

## Next governed block

GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST — MODEL/BACKEND BENCHMARK CONTRACT
RED

STOP before model download, runtime installation, ONNX export, or real neural
inference.
