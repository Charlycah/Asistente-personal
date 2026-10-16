from __future__ import annotations

import importlib
from pathlib import Path

import pytest

MODULE = "core.cognitive_memory_neural_benchmark"
REQUIRED_FAMILIES = {
    "semantic_paraphrase_weak_lexical",
    "lexical_exact_preservation",
    "hard_distractor",
    "multi_relevant",
    "spanish_morphology_paraphrase",
    "tie_stability",
}


def _benchmark_module():
    return importlib.import_module(MODULE)


def test_red_benchmark_contract_exposes_synthetic_non_private_corpus():
    benchmark = _benchmark_module()

    corpus = benchmark.synthetic_benchmark_corpus()

    assert corpus
    assert {case.family for case in corpus} >= REQUIRED_FAMILIES
    assert all(case.synthetic for case in corpus)
    assert all(not case.private_content for case in corpus)
    assert len({case.case_id for case in corpus}) == len(corpus)


def test_red_benchmark_contract_keeps_candidate_membership_immutable():
    benchmark = _benchmark_module()
    case = benchmark.synthetic_benchmark_corpus()[0]

    observation = benchmark.evaluate_case(case, tuple(reversed(case.candidates)))

    assert observation.candidate_ids == tuple(
        candidate.candidate_id for candidate in case.candidates
    )
    assert observation.membership_changed is False


def test_red_benchmark_contract_reports_baseline_and_reranked_quality():
    benchmark = _benchmark_module()
    report = benchmark.evaluate_benchmark(
        benchmark.synthetic_benchmark_corpus(),
        reranker=benchmark.identity_reranker,
    )

    assert 0.0 <= report.baseline_mrr <= 1.0
    assert 0.0 <= report.reranked_mrr <= 1.0
    assert 0.0 <= report.baseline_ndcg <= 1.0
    assert 0.0 <= report.reranked_ndcg <= 1.0
    assert report.mrr_delta == pytest.approx(0.0)
    assert report.ndcg_delta == pytest.approx(0.0)


def test_red_go_no_go_requires_zero_governance_regressions():
    benchmark = _benchmark_module()
    report = benchmark.BenchmarkReport(
        baseline_mrr=0.40,
        reranked_mrr=0.80,
        baseline_ndcg=0.45,
        reranked_ndcg=0.82,
        semantic_cases_improved=4,
        semantic_cases_total=5,
        lexical_exact_regressions=0,
        governance_violations=1,
        p50_latency_ms=1.0,
        p95_latency_ms=2.0,
        max_latency_ms=3.0,
    )

    assert benchmark.go_no_go(report) == "NO-GO"


def test_red_go_no_go_rejects_lexical_exact_regression():
    benchmark = _benchmark_module()
    report = benchmark.BenchmarkReport(
        baseline_mrr=0.40,
        reranked_mrr=0.80,
        baseline_ndcg=0.45,
        reranked_ndcg=0.82,
        semantic_cases_improved=4,
        semantic_cases_total=5,
        lexical_exact_regressions=1,
        governance_violations=0,
        p50_latency_ms=1.0,
        p95_latency_ms=2.0,
        max_latency_ms=3.0,
    )

    assert benchmark.go_no_go(report) == "NO-GO"


def test_red_go_no_go_requires_positive_semantic_quality_delta():
    benchmark = _benchmark_module()
    report = benchmark.BenchmarkReport(
        baseline_mrr=0.70,
        reranked_mrr=0.70,
        baseline_ndcg=0.75,
        reranked_ndcg=0.75,
        semantic_cases_improved=0,
        semantic_cases_total=5,
        lexical_exact_regressions=0,
        governance_violations=0,
        p50_latency_ms=1.0,
        p95_latency_ms=2.0,
        max_latency_ms=3.0,
    )

    assert benchmark.go_no_go(report) == "NO-GO"


def test_red_benchmark_records_latency_distribution_without_hardcoded_budget():
    benchmark = _benchmark_module()
    report = benchmark.evaluate_benchmark(
        benchmark.synthetic_benchmark_corpus(),
        reranker=benchmark.identity_reranker,
    )

    assert report.p50_latency_ms >= 0.0
    assert report.p95_latency_ms >= report.p50_latency_ms
    assert report.max_latency_ms >= report.p95_latency_ms
    assert not hasattr(benchmark, "UNIVERSAL_LATENCY_BUDGET_MS")


def test_red_source_forbids_provider_runtime_and_private_data_dependencies():
    path = Path("core/cognitive_memory_neural_benchmark.py")
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    folded = source.casefold()

    forbidden = (
        "sentence_transformers",
        "sentence-transformers",
        "torch",
        "onnxruntime",
        "transformers",
        "faiss",
        "chroma",
        "requests.",
        "httpx.",
        "d:\\biblioteca",
        "d:\\documentos",
        "neuralmanager",
        "vector_store",
        "memory_gateway.write",
    )
    assert all(token not in folded for token in forbidden)
