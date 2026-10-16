from __future__ import annotations

from scripts.hcpdq_v2_h6_entry_path_equivalent_freeze_contract import (
    freeze_h6_independent_construction_contract,
)


def test_h6_freeze_contract_is_frozen_without_constructing_cases():
    report = freeze_h6_independent_construction_contract()
    assert report["construction_contract_frozen"] is True
    assert report["construction_authorized"] is False
    assert report["case_content_created"] is False
    assert report["ground_truth_created"] is False


def test_h6_contract_requires_existing_structured_productive_entry():
    report = freeze_h6_independent_construction_contract()
    assert report["family"] == "H6"
    assert report["entry_path"] == (
        "existing explicit Decisión/Criterios/Evidencia intake grammar"
    )
    assert "productive GCDR intake" in report["existing_authority"]


def test_h6_contract_forbids_reuse_paraphrase_router_and_translation():
    report = freeze_h6_independent_construction_contract()
    assert report["consumed_v2_case_reuse_authorized"] is False
    assert report["consumed_v2_case_paraphrase_authorized"] is False
    assert report["benchmark_translation_authorized"] is False
    assert report["benchmark_router_authorized"] is False


def test_h6_contract_keeps_exposure_execution_and_changes_closed():
    report = freeze_h6_independent_construction_contract()
    assert report["roby_exposure_authorized"] is False
    assert report["primary_execution_authorized"] is False
    assert report["human_comparison_authorized"] is False
    assert report["production_change_authorized"] is False


def test_h6_contract_requires_dry_probe_gate_before_construction():
    report = freeze_h6_independent_construction_contract()
    assert report["dry_probe_cases_are_held_out"] is False
    assert report["case_count_frozen"] is False
    assert report["difficulty_distribution_frozen"] is False
    assert "dry probes" in report["next_required_decision"]
    assert report["status"] == (
        "CONTRACT_FROZEN_CONSTRUCTION_NOT_YET_AUTHORIZED"
    )
