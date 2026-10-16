from __future__ import annotations

import importlib
import inspect
import math

MODULE = "core.cognitive_memory_neural_model_backend_benchmark_contract"
EXPECTED_MODEL = "BAAI/bge-reranker-v2-m3"
EXPECTED_PROVIDER = "CPUExecutionProvider"
REFERENCE_ABS_TOLERANCE = 1e-4


def _contract():
    return importlib.import_module(MODULE)


def _valid_manifest(contract):
    return contract.ExperimentManifest(
        model_repository=EXPECTED_MODEL,
        model_revision="0123456789abcdef0123456789abcdef01234567",
        license_id="Apache-2.0",
        artifact_hashes=(
            contract.ArtifactHash("config.json", "a" * 64),
            contract.ArtifactHash("tokenizer.json", "b" * 64),
            contract.ArtifactHash("model.onnx", "c" * 64),
        ),
        onnx_artifact_sha256="c" * 64,
        python_version="3.11.0",
        runtime_version="1.0.0",
        execution_provider=EXPECTED_PROVIDER,
        optimization_mode="NONE",
        quantization_mode="NONE",
        corpus_version="synthetic-es-v1",
        hardware_fingerprint="owner-cpu-test",
    )


def _passing_report(contract):
    return contract.ModelBackendBenchmarkReport(
        manifest_verified=True,
        measured_offline=True,
        synthetic_non_private=True,
        candidate_membership_unchanged=True,
        governance_violations=0,
        lexical_exact_regressions=0,
        semantic_mrr_delta=0.10,
        semantic_ndcg_delta=0.10,
        semantic_cases_improved=3,
        semantic_cases_total=4,
        scores_valid=True,
        parity_passed=True,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        max_latency_ms=30.0,
        cold_start_ms=50.0,
        warmup_runs=2,
        measured_samples=6,
        execution_provider=EXPECTED_PROVIDER,
    )


def test_red_contract_freezes_candidate_identity_and_reference_parity():
    contract = _contract()

    assert contract.MODEL_REPOSITORY == EXPECTED_MODEL
    assert contract.EXECUTION_PROVIDER == EXPECTED_PROVIDER
    assert math.isclose(
        contract.REFERENCE_ABS_TOLERANCE,
        REFERENCE_ABS_TOLERANCE,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert contract.GO_DECISION == "GO_FOR_ADMISSION_REVIEW"


def test_red_manifest_requires_pinned_identity_hashes_and_cpu_provider():
    contract = _contract()
    manifest = _valid_manifest(contract)

    assert contract.validate_manifest(manifest) is True

    moving = contract.ExperimentManifest(
        **{**manifest.__dict__, "model_revision": "main"}
    )
    wrong_provider = contract.ExperimentManifest(
        **{**manifest.__dict__, "execution_provider": "OtherProvider"}
    )
    bad_hash = contract.ExperimentManifest(
        **{
            **manifest.__dict__,
            "artifact_hashes": (contract.ArtifactHash("model.onnx", "bad"),),
        }
    )

    assert contract.validate_manifest(moving) is False
    assert contract.validate_manifest(wrong_provider) is False
    assert contract.validate_manifest(bad_hash) is False


def test_red_phase_contract_keeps_acquisition_verification_benchmark_separate():
    contract = _contract()

    assert tuple(contract.EXPERIMENT_PHASES) == (
        "ACQUISITION",
        "VERIFICATION",
        "OFFLINE_BENCHMARK",
        "ADMISSION_REVIEW",
    )
    assert contract.phase_can_authorize_next("ACQUISITION") is False
    assert contract.phase_can_authorize_next("VERIFICATION") is False
    assert contract.phase_can_authorize_next("OFFLINE_BENCHMARK") is False


def test_red_reference_parity_requires_finite_scores_tolerance_and_same_ranking():
    contract = _contract()

    assert (
        contract.reference_parity(
            (0.2, 0.8),
            (0.20005, 0.79995),
        )
        is True
    )
    assert (
        contract.reference_parity(
            (0.2, 0.8),
            (0.2002, 0.7998),
        )
        is False
    )
    assert contract.reference_parity((0.2, 0.8), (0.9, 0.1)) is False
    assert contract.reference_parity((0.2, 0.8), (math.nan, 0.8)) is False


def test_red_go_requires_all_governance_quality_and_offline_gates():
    contract = _contract()
    report = _passing_report(contract)

    assert contract.go_no_go(report) == "GO_FOR_ADMISSION_REVIEW"

    violations = (
        {"manifest_verified": False},
        {"measured_offline": False},
        {"synthetic_non_private": False},
        {"candidate_membership_unchanged": False},
        {"governance_violations": 1},
        {"lexical_exact_regressions": 1},
        {"semantic_mrr_delta": 0.0},
        {"semantic_ndcg_delta": 0.0},
        {"semantic_cases_improved": 2},
        {"scores_valid": False},
        {"parity_passed": False},
        {"execution_provider": "OtherProvider"},
    )
    for changes in violations:
        failed = contract.ModelBackendBenchmarkReport(**{**report.__dict__, **changes})
        assert contract.go_no_go(failed) == "NO-GO"


def test_red_latency_evidence_is_complete_without_universal_budget():
    contract = _contract()
    report = _passing_report(contract)

    assert contract.latency_evidence_complete(report) is True
    assert report.cold_start_ms >= 0.0
    assert 0.0 <= report.p50_latency_ms <= report.p95_latency_ms
    assert report.p95_latency_ms <= report.max_latency_ms
    assert report.warmup_runs > 0
    assert report.measured_samples > 0
    assert not hasattr(contract, "UNIVERSAL_LATENCY_BUDGET_MS")


def test_red_invalid_or_incomplete_evidence_fails_closed():
    contract = _contract()
    report = _passing_report(contract)

    invalid_latency = contract.ModelBackendBenchmarkReport(
        **{**report.__dict__, "p95_latency_ms": -1.0}
    )
    no_samples = contract.ModelBackendBenchmarkReport(
        **{**report.__dict__, "measured_samples": 0}
    )

    assert contract.go_no_go(invalid_latency) == "NO-GO"
    assert contract.go_no_go(no_samples) == "NO-GO"


def test_red_contract_is_model_free_runtime_free_and_non_authoritative():
    contract = _contract()
    source = inspect.getsource(contract).lower()

    forbidden = (
        "onnxruntime",
        "sentence_transformers",
        "sentence-transformers",
        "transformers",
        "torch",
        "requests.",
        "httpx.",
        "memory_gateway.write",
        "learning_gateway.write",
        "authorization.write",
        "execution.write",
        "vector_store",
        "d:\\biblioteca",
        "d:\\documentos",
    )
    assert all(token not in source for token in forbidden)
