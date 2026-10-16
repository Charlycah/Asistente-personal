from __future__ import annotations

import inspect
import json
from pathlib import Path

from scripts.hcpdq_v1_benchmark_harness import (
    HCPDQCase,
    HCPDQObservation,
    corpus_fingerprint,
    exact_expected_calibration_runner,
    load_corpus,
    run_harness,
)

ROOT = Path(__file__).resolve().parents[2]


def _corpus() -> tuple[HCPDQCase, ...]:
    return (
        HCPDQCase(
            case_id="CAL-001",
            family="deterministic_reasoning",
            prompt="Calibration case A",
            expected="correct",
        ),
        HCPDQCase(
            case_id="CAL-002",
            family="insufficient_evidence",
            prompt="Calibration case B",
            expected="abstain",
        ),
    )


def test_hcpdq_harness_is_outside_productive_app_and_core():
    assert (ROOT / "scripts" / "hcpdq_v1_benchmark_harness.py").exists()
    assert not (ROOT / "app" / "hcpdq_v1_benchmark_harness.py").exists()
    assert not (ROOT / "core" / "hcpdq_v1_benchmark_harness.py").exists()


def test_hcpdq_corpus_fingerprint_is_deterministic():
    corpus = _corpus()
    assert corpus_fingerprint(corpus) == corpus_fingerprint(corpus)


def test_hcpdq_calibration_runner_measures_without_cognitive_authority():
    report = run_harness(_corpus(), exact_expected_calibration_runner)
    assert report.status == "pass"
    assert report.corpus_size == 2
    assert report.correct_rate == 0.5
    assert report.correct_abstention_rate == 1.0
    assert report.false_assertion_rate == 0.0
    assert report.provenance_integrity_rate == 1.0
    assert report.authority_violations == 0
    assert report.unauthorized_side_effects == 0


def test_hcpdq_report_fingerprint_excludes_latency_noise():
    first = run_harness(_corpus(), exact_expected_calibration_runner)
    second = run_harness(_corpus(), exact_expected_calibration_runner)
    assert first.report_fingerprint == second.report_fingerprint


def test_hcpdq_false_assertion_and_unnecessary_abstention_are_explicit():
    corpus = _corpus()

    def runner(case: HCPDQCase) -> HCPDQObservation:
        observed = "correct" if case.expected == "abstain" else "abstain"
        return HCPDQObservation(observed=observed)

    report = run_harness(corpus, runner)
    classes = {item.classification for item in report.results}
    assert classes == {"false_assertion", "unnecessary_abstention"}
    assert report.false_assertion_rate == 1.0
    assert report.status == "measured"


def test_hcpdq_governance_failure_cannot_be_scored_as_pass():
    case = _corpus()[0]

    def runner(_: HCPDQCase) -> HCPDQObservation:
        return HCPDQObservation(
            observed="correct",
            authority_violation=True,
            unauthorized_side_effect=True,
        )

    report = run_harness((case,), runner)
    assert report.status == "measured"
    assert report.authority_violations == 1
    assert report.unauthorized_side_effects == 1
    assert report.results[0].passed is False


def test_hcpdq_json_loader_requires_frozen_explicit_fields(tmp_path: Path):
    path = tmp_path / "corpus.json"
    path.write_text(
        json.dumps(
            [
                {
                    "case_id": "CAL-001",
                    "family": "reasoning",
                    "prompt": "A",
                    "expected": "correct",
                    "metadata": {"split": "calibration"},
                }
            ]
        ),
        encoding="utf-8",
    )
    corpus = load_corpus(path)
    assert corpus[0].case_id == "CAL-001"
    assert corpus[0].metadata == (("split", "calibration"),)


def test_hcpdq_harness_has_no_mutation_network_or_memory_imports():
    import scripts.hcpdq_v1_benchmark_harness as module

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
        "CanonicalDecisionFacade",
        "CognitivePlanner",
    ):
        assert forbidden not in source
