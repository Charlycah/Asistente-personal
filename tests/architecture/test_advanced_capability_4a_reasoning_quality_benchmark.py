from __future__ import annotations

import inspect
from pathlib import Path

from scripts.advanced_capability_4a_reasoning_quality_benchmark import (
    build_corpus,
    corpus_fingerprint,
    run_benchmark,
)

ROOT = Path(__file__).resolve().parents[2]


def test_4a_corpus_is_predeclared_deterministic_and_exactly_80_cases():
    first = build_corpus()
    second = build_corpus()
    assert first == second
    assert len(first) == 80
    assert len({case.case_id for case in first}) == 80
    assert corpus_fingerprint(first) == corpus_fingerprint(second)


def test_4a_dimension_distribution_matches_contract():
    corpus = build_corpus()
    dimensions = {case.dimension for case in corpus}
    counts = {
        dimension: sum(case.dimension == dimension for case in corpus)
        for dimension in dimensions
    }
    assert counts == {
        "correctness": 16,
        "abstention": 16,
        "transfer": 16,
        "gcdr": 16,
        "provenance": 8,
        "noise": 8,
    }


def test_4a_benchmark_reports_separate_quality_metrics():
    report = run_benchmark()
    assert report.corpus_size == 80
    assert 0.0 <= report.correct_rate <= 1.0
    assert 0.0 <= report.correct_abstention_rate <= 1.0
    assert 0.0 <= report.false_assertion_rate <= 1.0
    assert 0.0 <= report.transfer_success_rate <= 1.0
    assert 0.0 <= report.gcdr_decision_accuracy <= 1.0
    assert 0.0 <= report.provenance_integrity_rate <= 1.0
    assert 0.0 <= report.noise_robustness_rate <= 1.0
    assert report.median_latency_ms >= 0.0
    assert report.p95_latency_ms >= 0.0


def test_4a_hard_governance_invariants_hold():
    report = run_benchmark()
    assert report.provenance_integrity_rate == 1.0
    assert report.authority_violations == 0
    assert report.unauthorized_side_effects == 0


def test_4a_false_assertion_metric_is_explicit_and_zero_for_certified_corpus():
    report = run_benchmark()
    assert report.false_assertion_rate == 0.0


def test_4a_runner_is_diagnostic_and_does_not_import_mutation_or_network_surfaces():
    import scripts.advanced_capability_4a_reasoning_quality_benchmark as module

    source = inspect.getsource(module)
    for forbidden in (
        "OfficialMemoryGateway",
        "remember_governed_learning",
        "requests.",
        "httpx.",
        "subprocess",
        "os.system",
        "write_bytes(",
        "git apply",
        "apply_patch",
    ):
        assert forbidden not in source


def test_4a_is_outside_productive_app_and_core():
    path = ROOT / "scripts" / "advanced_capability_4a_reasoning_quality_benchmark.py"
    assert path.exists()
    assert not (
        ROOT / "app" / "advanced_capability_4a_reasoning_quality_benchmark.py"
    ).exists()
    assert not (
        ROOT / "core" / "advanced_capability_4a_reasoning_quality_benchmark.py"
    ).exists()


def test_4a_schema_and_report_fingerprint_are_stable_logically():
    first = run_benchmark()
    second = run_benchmark()
    assert (
        first.schema_version
        == "advanced-capability-4a-reasoning-quality-benchmark-v1"
    )
    assert first.corpus_fingerprint == second.corpus_fingerprint
    assert first.report_fingerprint == second.report_fingerprint
