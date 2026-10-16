from __future__ import annotations

from scripts.hcpdq_v2_h7_h2_h8_exposure_contract import (
    freeze_wave1_contract,
)


def test_wave1_contract_is_conditional_go_to_red_only():
    report = freeze_wave1_contract()
    assert report["status"] == (
        "CONTRACT_FROZEN_CONDITIONAL_GO_HELD_OUT_NO_GO"
    )
    assert report["wave"] == ["H7", "H2", "H8"]
    assert report["go_to_preimplementation_red"] is True
    assert report["minimal_production_implementation_authorized"] is False


def test_h7_contract_uses_existing_planning_reentry_not_new_planner():
    report = freeze_wave1_contract()
    h7 = report["families"]["H7"]
    assert h7["existing_authority"] == "planning_foundation"
    assert "PlanningReentry" in h7["productive_surface"]
    assert "planning_invocation_count" in h7["exposure_may_observe"]
    assert h7["held_out_authorized"] is False


def test_h2_contract_keeps_epistemic_context_and_abstention_distinct():
    report = freeze_wave1_contract()
    h2 = report["families"]["H2"]
    assert "EpistemicSufficiency" in h2["productive_surface"]
    assert "ResponseConfidenceRecord" in h2["productive_surface"]
    assert any(
        "itself caused abstention" in item
        for item in h2["exposure_must_not_infer"]
    )


def test_h8_contract_observes_existing_conflict_resolution_without_selecting():
    report = freeze_wave1_contract()
    h8 = report["families"]["H8"]
    assert "Provenance" in h8["productive_surface"]
    assert "conflict identifiers" in h8["exposure_may_observe"]
    assert any(
        "may rank sources or select claims" in item
        for item in h8["exposure_must_not_infer"]
    )


def test_wave1_contract_preserves_all_global_safety_boundaries():
    report = freeze_wave1_contract()
    for field in (
        "new_authority_authorized",
        "benchmark_specific_routing_authorized",
        "direct_internal_authority_instantiation_authorized",
        "ground_truth_available_to_exposure",
        "persistence_or_adaptation_authorized",
        "held_out_construction_authorized",
        "human_comparison_authorized",
        "cross_family_substitution_authorized",
    ):
        assert report[field] is False


def test_wave1_contract_requires_causal_join_and_fail_closed_semantics():
    report = freeze_wave1_contract()
    assert "actually participated" in report["causal_join_rule"]
    assert "metadata presence alone is insufficient" in report["causal_join_rule"]
    assert "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2" in report["failure_rule"]
    assert "CAPABILITY_ABSENT" in report["failure_rule"]
