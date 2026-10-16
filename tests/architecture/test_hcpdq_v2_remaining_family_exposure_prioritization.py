from __future__ import annotations

from scripts.hcpdq_v2_remaining_family_exposure_prioritization import (
    audit_and_prioritize,
)


def test_priority_order_prefers_existing_productive_consumers():
    report = audit_and_prioritize()
    assert report["priority_order"] == [
        "H7", "H2", "H8", "H1", "H3", "H4", "H5"
    ]
    assert report["immediate_contract_wave"] == ["H7", "H2", "H8"]


def test_h7_is_highest_priority_but_not_yet_certified():
    report = audit_and_prioritize()
    h7 = report["families"]["H7"]
    assert h7["priority"] == 1
    assert h7["disposition"] == "PROCEED_TO_EXPOSURE_CONTRACT"
    assert h7["held_out_authorized"] is False


def test_h1_h3_require_shadow_observability_audit_before_exposure():
    report = audit_and_prioritize()
    assert report["shadow_observability_wave"] == ["H1", "H3"]
    for family in ("H1", "H3"):
        assert (
            report["families"][family]["disposition"]
            == "AUDIT_OBSERVABLE_SHADOW_PATH_FIRST"
        )


def test_h4_h5_are_deferred_instead_of_forcing_benchmark_facades():
    report = audit_and_prioritize()
    assert report["defer_or_exclude_wave"] == ["H4", "H5"]
    for family in ("H4", "H5"):
        assert report["families"][family]["architectural_risk"] == "HIGH"
        assert "DEFER_OR_EXCLUDE" in report["families"][family]["disposition"]


def test_audit_keeps_all_exposure_safety_gates_closed():
    report = audit_and_prioritize()
    assert report["new_authority_authorized"] is False
    assert report["production_semantic_change_authorized"] is False
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
