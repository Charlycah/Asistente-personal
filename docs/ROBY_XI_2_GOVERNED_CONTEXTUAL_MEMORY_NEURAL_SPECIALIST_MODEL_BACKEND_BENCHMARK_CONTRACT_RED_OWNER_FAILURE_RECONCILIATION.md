# ROBY XI.2 — Model/Backend Benchmark Contract RED Owner Failure Reconciliation

## Status

COMPLETE / PENDING OWNER RECERTIFICATION

## Owner evidence reconciled

The first Owner run correctly observed the eight intentional contract RED
failures, but certification could not close because Ruff reported I001 in the
new RED test and M361 then reported a stale committed snapshot.

## Surgical correction

Only the RED test lint surface and generated M361 snapshot were reconciled.
The test no longer imports pytest solely for one approximate comparison; the
same frozen tolerance assertion uses math.isclose with a strict local numeric
comparison. No RED requirement was weakened or removed.

M361 was regenerated only after the final test correction so its committed
snapshot describes the final reconciled tree.

## Preserved RED contract

- future boundary remains
  core.cognitive_memory_neural_model_backend_benchmark_contract;
- model remains BAAI/bge-reranker-v2-m3, selected for benchmark only;
- backend remains ONNX Runtime CPU / CPUExecutionProvider, not admitted;
- non-quantized reference absolute tolerance remains 1e-4;
- all eight intended RED cases remain active;
- model download, runtime installation, export and real inference remain
  forbidden;
- no productive authority or dependency was added.

## Local reconciliation evidence

- focused RED: 8 FAIL / 0 PASS, all missing future contract module;
- focused RED + M361: 8 FAIL / 5 PASS;
- compileall: PASS;
- RED test maximum line length: 82;
- protected hashes unchanged.

Local Ruff is unavailable in this environment. Owner Ruff is therefore the
certification authority for the I001 correction.

## Owner recertification target

Run the canonical sequence:

1. python scripts/clean_project_caches.py
2. python scripts/generate_quality_baseline.py
3. ruff check .
4. pytest -q

Expected contractual state: Ruff CLEAN and exactly eight intentional RED
failures, with no M361 or other unrelated failure.

STOP before GREEN, model/runtime acquisition, ONNX export, or real inference.
