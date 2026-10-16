from __future__ import annotations

from scripts.hcpdq_v2_h6_freeze_certification_exposure_authorization import (
    certify_h6_freeze_for_exposure,
)


def test_frozen_corpus_and_truth_hashes_remain_exact():
    report = certify_h6_freeze_for_exposure()
    assert report["corpus_hash_match"] is True
    assert report["ground_truth_hash_match"] is True


def test_case_ids_remain_unique_and_ground_truth_aligned():
    report = certify_h6_freeze_for_exposure()
    assert report["case_count"] == 12
    assert report["case_ids_aligned"] is True
    assert report["case_ids_unique"] is True


def test_all_frozen_cases_satisfy_certified_h6_entry_path():
    report = certify_h6_freeze_for_exposure()
    assert report["entry_path_equivalent"] is True
    assert set(report["entry_path_statuses"].values()) == {"complete"}


def test_freeze_certification_authorizes_only_read_only_exposure():
    report = certify_h6_freeze_for_exposure()
    assert report["freeze_certified"] is True
    assert report["exposure_authorized"] is True
    assert report["ground_truth_exposure_authorized"] is False
    assert report["scoring_authorized_during_exposure"] is False


def test_certification_keeps_execution_adaptation_and_mutation_closed():
    report = certify_h6_freeze_for_exposure()
    assert report["primary_execution_authorized"] is False
    assert report["learning_or_adaptation_authorized"] is False
    assert report["production_change_authorized"] is False
    assert report["benchmark_translation_authorized"] is False
    assert report["benchmark_router_authorized"] is False
    assert report["corpus_mutation_authorized"] is False
    assert report["ground_truth_mutation_authorized"] is False


def test_certification_confirms_no_pre_certification_exposure():
    report = certify_h6_freeze_for_exposure()
    assert report["pre_certification_exposure_absent"] is True
    assert report["status"] == "FREEZE_CERTIFIED_EXPOSURE_AUTHORIZED"
