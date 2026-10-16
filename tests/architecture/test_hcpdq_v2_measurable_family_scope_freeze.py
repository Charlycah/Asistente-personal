from __future__ import annotations

from scripts.hcpdq_v2_measurable_family_scope_freeze import (
    freeze_measurable_family_scope,
)


def test_scope_freeze_certifies_only_h6_h7_as_currently_measurable():
    report = freeze_measurable_family_scope()
    assert report["measurable_families"] == ["H6", "H7"]
    assert report["measurable_family_count"] == 2


def test_scope_freeze_excludes_h2_h4_h5_h8_without_claiming_absence():
    report = freeze_measurable_family_scope()
    assert report["excluded_families"] == ["H2", "H4", "H5", "H8"]
    for family in report["excluded_families"]:
        assert report["families"][family]["measurable_in_v2"] is False
        assert "EXCLUDED_" in report["families"][family]["disposition"]


def test_scope_freeze_keeps_h1_h3_pending_for_existing_shadow_audit():
    report = freeze_measurable_family_scope()
    assert report["pending_scope_families"] == ["H1", "H3"]
    assert report["scope_freeze_complete"] is False


def test_held_out_readiness_remains_no_go_until_scope_resolution():
    report = freeze_measurable_family_scope()
    assert report["held_out_readiness"] == "NO_GO"
    assert report["held_out_construction_authorized"] is False
    assert report["held_out_execution_authorized"] is False
    assert report["human_comparison_authorized"] is False


def test_scope_reassessment_does_not_authorize_production_or_new_authority():
    report = freeze_measurable_family_scope()
    assert report["production_changes_authorized"] is False
    assert report["new_authority_authorized"] is False
