from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pytest

from scripts.advanced_capability_3a_scale_benchmark import (
    DECISIVE_ITEM_COUNT,
    QUERY_LIMIT,
    build_synthetic_dataset,
    run_benchmark,
    run_scale_level,
    write_report,
)


def test_scale_dataset_is_deterministic_and_contains_bounded_decisive_evidence(
) -> None:
    first = build_synthetic_dataset(100)
    second = build_synthetic_dataset(100)

    assert first == second
    assert len(first) == 100
    assert sum("decisive" in item["tags"] for item in first) == DECISIVE_ITEM_COUNT


def test_scale_level_reuses_bounded_pipeline_and_preserves_decisive_evidence() -> None:
    result = run_scale_level(1_000)

    assert result.passed is True
    assert result.input_count == result.processed_count == 1_000
    assert result.query_count == 10
    assert result.max_items_per_query == QUERY_LIMIT == 100
    assert result.rejected_count == 0
    assert result.duplicate_count == 0
    assert result.provenance_integrity is True
    assert result.corrupt_provenance_rejected is True
    assert result.decisive_items_selected == DECISIVE_ITEM_COUNT
    assert result.relevant_evidence_recall == 1.0
    assert len(result.deterministic_digest) == 64


def test_scale_level_has_stable_logical_output_digest() -> None:
    first = run_scale_level(100)
    second = run_scale_level(100)

    assert first.deterministic_digest == second.deterministic_digest
    assert first.selected_count == second.selected_count
    assert first.processed_count == second.processed_count


def test_benchmark_contract_remains_offline_and_under_existing_authority() -> None:
    report = run_benchmark((100, 1_000))

    assert report.status == "pass"
    assert report.certified_max_items == 1_000
    assert report.network_enabled is False
    assert report.automatic_fetch_enabled is False
    assert report.query_limit == 100
    assert report.source_authority == report.normalizer_authority
    assert report.normalizer_authority == report.executor_authority
    assert "OfficialConversationGateway" in report.executor_authority


def test_benchmark_report_write_is_explicit_and_reproducible(tmp_path: Path) -> None:
    report = run_benchmark((100,))
    output = tmp_path / "scale-report.json"

    result = write_report(report, output)

    assert result == output
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert report.report_fingerprint in content
    assert '"certified_max_items": 100' in content


def test_invalid_scale_levels_fail_closed() -> None:
    with pytest.raises(ValueError, match="positive"):
        run_benchmark((0,))
    with pytest.raises(ValueError, match="decisive evidence"):
        build_synthetic_dataset(4)


def test_diagnostic_module_contains_no_productive_mutation_or_external_io() -> None:
    source = Path("scripts/advanced_capability_3a_scale_benchmark.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "requests.",
        "urllib",
        "socket",
        "subprocess",
        "OfficialMemoryGateway",
        "store_governed_learning",
        "write_text(candidate",
        "AUTHORITY_ID",
        "Thread(",
        "Process(",
    )

    for token in forbidden:
        assert token not in source

    assert "GovernedSourceQueryExecutor" in source
    assert "GovernedInformationNormalizer" in source
    assert "RelevanceEvaluator" in source
    assert asdict(run_benchmark((100,)))["status"] == "pass"
