from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H6_PRIMARY_POSTMORTEM_EVALUATION_BOUNDARY_AUDIT.json"
)


def _audit():
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_postmortem_certifies_all_boundary_checks():
    audit = _audit()
    assert all(audit["checks"].values())
    assert audit["measurement_boundary_valid"] is True


def test_postmortem_keeps_primary_authorization_consumed():
    audit = _audit()
    assert audit["checks"]["authorization_consumed_once"] is True
    assert audit["primary_run_repeat_authorized"] is False


def test_postmortem_certifies_sealed_single_attempt_capture_set():
    audit = _audit()
    assert audit["checks"]["exact_record_count"] is True
    assert audit["checks"]["single_attempt"] is True
    assert audit["checks"]["no_retries"] is True
    assert audit["checks"]["all_raw_captures_sealed"] is True
    assert audit["checks"]["raw_hashes_self_consistent"] is True


def test_postmortem_certifies_ground_truth_and_scoring_separation():
    audit = _audit()
    assert audit["checks"]["no_ground_truth_during_run"] is True
    assert audit["checks"]["no_scoring_during_run"] is True
    assert audit["ground_truth_scoring_performed"] is False


def test_postmortem_does_not_itself_authorize_scoring():
    audit = _audit()
    assert audit["ground_truth_scoring_authorized_by_this_gate"] is False
    assert audit["scoring_gate_eligible"] is True
    assert audit["raw_capture_mutation_authorized"] is False


def test_postmortem_emits_pass_and_separate_scoring_gate():
    audit = _audit()
    assert audit["status"] == "BOUNDARY_AUDIT_PASS_SCORING_GATE_ELIGIBLE"
    assert audit["next_gate"].endswith(
        "Ground-Truth Scoring Authorization / Go-No-Go"
    )
