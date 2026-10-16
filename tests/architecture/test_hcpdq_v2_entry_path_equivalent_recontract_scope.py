from __future__ import annotations

from scripts.hcpdq_v2_entry_path_equivalent_recontract_scope import (
    freeze_recontract_scope,
)


def test_recontract_scope_freezes_h6_go_and_h7_no_go():
    report = freeze_recontract_scope()
    assert report["status"] == "SCOPE_FROZEN_H6_GO_H7_NO_GO"
    assert report["families"]["H6"]["measurable_now"] is True
    assert report["families"]["H7"]["measurable_now"] is False


def test_h6_scope_uses_only_existing_productive_structured_intake():
    report = freeze_recontract_scope()
    h6 = report["families"]["H6"]
    assert h6["independent_freeze_authorized"] is True
    assert "Decisión/Criterios/Evidencia" in h6["allowed_entry_form"]
    assert "productive GCDR intake" in h6["existing_authority"]


def test_h7_stays_out_until_real_user_entry_path_exists():
    report = freeze_recontract_scope()
    h7 = report["families"]["H7"]
    assert h7["independent_freeze_authorized"] is False
    assert h7["allowed_entry_form"] is None
    assert report["h7_production_work_authorized"] is False


def test_scope_does_not_construct_or_expose_new_held_out_material():
    report = freeze_recontract_scope()
    assert report["new_corpus_constructed"] is False
    assert report["new_ground_truth_constructed"] is False
    assert report["held_out_exposure_occurred"] is False


def test_scope_preserves_independence_and_old_freeze_non_reuse():
    report = freeze_recontract_scope()
    assert report["old_consumed_freeze_reusable"] is False
    assert report["old_held_out_retry_authorized"] is False
    assert report["benchmark_specific_translation_authorized"] is False
    assert report["benchmark_specific_router_authorized"] is False
    assert len(report["independence_requirements"]) == 6
