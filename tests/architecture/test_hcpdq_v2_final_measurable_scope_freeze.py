from __future__ import annotations

from scripts.hcpdq_v2_final_measurable_scope_freeze import (
    freeze_final_measurable_scope,
)


def test_final_scope_is_frozen_to_h6_h7_only():
    report = freeze_final_measurable_scope()
    assert report["measurable_families"] == ["H6", "H7"]
    assert report["pending_families"] == []
    assert report["scope_freeze_complete"] is True


def test_final_scope_excludes_all_non_measurable_families():
    report = freeze_final_measurable_scope()
    assert report["excluded_families"] == [
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H8",
    ]


def test_held_out_is_go_for_new_independent_construction_and_freeze():
    report = freeze_final_measurable_scope()
    assert report["held_out_readiness"] == (
        "GO_FOR_CONSTRUCTION_AND_FREEZE_ONLY"
    )
    assert report["held_out_construction_authorized"] is True
    assert report["held_out_ground_truth_freeze_authorized"] is True
    assert report["v1_corpus_reuse_authorized"] is False


def test_roby_exposure_execution_and_human_comparison_remain_no_go():
    report = freeze_final_measurable_scope()
    assert report["held_out_roby_exposure_authorized"] is False
    assert report["held_out_execution_authorized"] is False
    assert report["human_comparison_authorized"] is False


def test_final_scope_does_not_authorize_production_or_new_authority():
    report = freeze_final_measurable_scope()
    assert report["production_changes_authorized"] is False
    assert report["new_authority_authorized"] is False
