from __future__ import annotations

from scripts.hcpdq_v2_evaluation_exposure_recertification import (
    recertify_evaluation_exposure,
)


def test_exposure_layer_is_causally_recertified_with_zero_authority():
    report = recertify_evaluation_exposure()
    assert report["causal_recertification_passed"] is True
    assert report["zero_authority"] is True
    assert report["zero_mutation"] is True


def test_exposure_layer_does_not_duplicate_or_instantiate_cognitive_authority():
    report = recertify_evaluation_exposure()
    assert report["no_direct_internal_instantiation"] is True
    assert report["family_mapping_metadata_only"] is True
    assert report["ground_truth_firewall"] is True


def test_h6_is_reused_and_remaining_families_stay_fail_closed():
    report = recertify_evaluation_exposure()
    assert report["h6_reuses_existing_certification"] is True
    assert report["remaining_families_fail_closed"] is True


def test_shadow_equivalence_guard_remains_active():
    report = recertify_evaluation_exposure()
    assert report["shadow_equivalence_guard"] is True
    assert report["production_cognitive_change_detected"] is False


def test_recertification_does_not_authorize_held_out_or_human_comparison():
    report = recertify_evaluation_exposure()
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
