from __future__ import annotations

from scripts.hcpdq_v2_h7_h2_h8_exposure_recertification import (
    recertify_wave1_exposure,
)


def test_wave1_exposure_is_causally_recertified_with_zero_authority():
    report = recertify_wave1_exposure()
    assert report["causal_recertification_passed"] is True
    assert report["zero_authority"] is True
    assert report["zero_mutation"] is True


def test_wave1_exposure_does_not_instantiate_or_replace_existing_authorities():
    report = recertify_wave1_exposure()
    assert report["no_direct_internal_authority_instantiation"] is True
    assert report["family_mapping_metadata_only"] is True
    assert report["ground_truth_blind"] is True


def test_h7_h2_h8_causal_joins_are_independently_recertified():
    report = recertify_wave1_exposure()
    assert report["h7_join_certified"] is True
    assert report["h2_join_certified"] is True
    assert report["h8_join_certified"] is True


def test_wave1_recertification_remains_fail_closed():
    report = recertify_wave1_exposure()
    assert report["fail_closed_measurement"] is True
    assert report["production_cognitive_change_detected"] is False


def test_wave1_recertification_keeps_held_out_and_human_comparison_no_go():
    report = recertify_wave1_exposure()
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
