from __future__ import annotations

from scripts.hcpdq_v2_h1_h3_shadow_observability_audit import (
    audit_h1_h3_shadow_observability,
)


def test_existing_shadow_is_real_observational_and_productively_wired():
    report = audit_h1_h3_shadow_observability()
    assert report["shadow_runtime_is_observer"] is True
    assert report["ordinary_plan_observation_wired"] is True
    assert report["context_observation_wired"] is True
    assert report["capability_observation_wired"] is True


def test_h1_is_excluded_because_shadow_does_not_expose_full_reasoning_path():
    report = audit_h1_h3_shadow_observability()
    h1 = report["families"]["H1"]
    assert h1["ordinary_productive_path_wired"] is True
    assert h1["family_semantics_fully_exposed"] is False
    assert h1["disposition"] == (
        "EXCLUDE_H1_FROM_HCPDQ_V2_MEASURABLE_SCOPE"
    )


def test_h3_is_excluded_because_shadow_lacks_required_semantic_evidence():
    report = audit_h1_h3_shadow_observability()
    h3 = report["families"]["H3"]
    assert h3["ordinary_productive_path_wired"] is True
    assert h3["family_semantics_fully_exposed"] is False
    assert h3["disposition"] == (
        "EXCLUDE_H3_FROM_HCPDQ_V2_MEASURABLE_SCOPE"
    )


def test_h1_h3_resolution_does_not_authorize_red_or_production_changes():
    report = audit_h1_h3_shadow_observability()
    assert report["preimplementation_red_authorized"] is False
    assert report["production_change_authorized"] is False
    assert report["new_authority_authorized"] is False
    assert report["benchmark_semantic_classifier_authorized"] is False


def test_h1_h3_resolution_keeps_held_out_closed_until_final_scope_freeze():
    report = audit_h1_h3_shadow_observability()
    assert report["held_out_authorized"] is False
