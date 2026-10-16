from __future__ import annotations

import json
from pathlib import Path

from scripts.hcpdq_v2_h6_h7_held_out_freeze import (
    MANIFEST,
    verify_h6_h7_held_out_freeze,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_v2_held_out_has_only_frozen_h6_h7_scope_and_balanced_difficulty():
    report = verify_h6_h7_held_out_freeze()
    assert report["case_count"] == 30
    assert report["family_counts"] == {"H6": 15, "H7": 15}
    assert report["difficulty_counts"] == {"D1": 10, "D2": 10, "D3": 10}


def test_v2_held_out_ground_truth_is_complete_and_referentially_consistent():
    report = verify_h6_h7_held_out_freeze()
    assert report["unique_case_ids"] is True
    assert report["ground_truth_complete"] is True
    assert report["ground_truth_references_match"] is True


def test_v2_held_out_hashes_match_frozen_manifest():
    report = verify_h6_h7_held_out_freeze()
    assert report["case_hash_matches_manifest"] is True
    assert report["ground_truth_hash_matches_manifest"] is True


def test_v2_held_out_freeze_did_not_expose_or_execute_roby():
    report = verify_h6_h7_held_out_freeze()
    assert report["roby_exposure_occurred"] is False
    assert report["execution_occurred"] is False


def test_v2_held_out_manifest_keeps_exposure_execution_and_comparison_closed():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["roby_exposure_authorized"] is False
    assert manifest["execution_authorized"] is False
    assert manifest["human_comparison_authorized"] is False
    assert manifest["status"] == (
        "FROZEN_PENDING_INDEPENDENT_FREEZE_CERTIFICATION"
    )
