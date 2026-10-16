from __future__ import annotations

from scripts.hcpdq_v2_h2_h8_causal_lineage_gap_contract import (
    freeze_h2_h8_causal_lineage_gap_contract,
)


def test_h2_h8_gap_contract_is_no_go_not_red_authorization():
    report = freeze_h2_h8_causal_lineage_gap_contract()
    assert report["status"] == (
        "NO_GO_EXCLUDE_H2_H8_FROM_V2_MEASURABLE_SCOPE"
    )
    assert report["preimplementation_red_authorized"] is False
    assert report["minimal_production_implementation_authorized"] is False


def test_h2_has_components_but_no_existing_productive_causal_join():
    report = freeze_h2_h8_causal_lineage_gap_contract()
    h2 = report["families"]["H2"]
    assert h2["existing_components"]
    assert h2["shared_causal_lineage_present"] is False
    assert h2["productive_join_present"] is False
    assert "EXCLUDE" in h2["disposition"]


def test_h8_has_components_but_no_existing_productive_causal_join():
    report = freeze_h2_h8_causal_lineage_gap_contract()
    h8 = report["families"]["H8"]
    assert h8["existing_components"]
    assert h8["shared_causal_lineage_present"] is False
    assert h8["productive_join_present"] is False
    assert "EXCLUDE" in h8["disposition"]


def test_gap_contract_forbids_manufactured_lineage_or_bridge_authority():
    report = freeze_h2_h8_causal_lineage_gap_contract()
    assert report["metadata_only_lineage_patch_authorized"] is False
    assert report["new_bridge_authorized"] is False
    assert report["new_authority_authorized"] is False
    assert report["response_semantic_change_authorized"] is False
    assert report["conflict_policy_change_authorized"] is False


def test_gap_contract_fails_closed_without_claiming_capability_absence():
    report = freeze_h2_h8_causal_lineage_gap_contract()
    assert report["measurement_failure_classification"] == (
        "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"
    )
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
