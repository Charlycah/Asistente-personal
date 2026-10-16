from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "benchmarks" / "HCPDQ_V2_H6_GROUND_TRUTH_SCORING_AUTHORIZATION.json"


def _auth():
    return json.loads(AUTH.read_text(encoding="utf-8"))


def test_scoring_authorization_requires_every_boundary_precondition():
    auth = _auth()
    assert all(auth["checks"].values())
    assert auth["go"] is True


def test_scoring_scope_is_exactly_twelve_existing_sealed_captures():
    auth = _auth()
    assert auth["sealed_capture_count_authorized"] == 12
    assert "already sealed raw captures" in auth["authorization_scope"]
    assert "exact frozen H6 ground truth" in auth["authorization_scope"]


def test_scoring_authorization_allows_truth_read_but_never_mutation():
    auth = _auth()
    assert auth["ground_truth_read_authorized"] is True
    assert auth["ground_truth_mutation_authorized"] is False
    assert auth["raw_capture_mutation_authorized"] is False


def test_scoring_authorization_does_not_reopen_roby_execution():
    auth = _auth()
    assert auth["roby_rerun_authorized"] is False
    assert auth["retry_authorized"] is False
    assert auth["learning_or_adaptation_authorized"] is False
    assert auth["memory_writeback_authorized"] is False
    assert auth["benchmark_feedback_authorized"] is False


def test_authorization_gate_does_not_itself_score():
    auth = _auth()
    assert auth["scoring_execution_performed_in_this_gate"] is False
    assert auth["scoring_authorization_reusable"] is False
    assert auth["post_scoring_tuning_authorized"] is False


def test_scoring_authorization_emits_explicit_go_and_next_gate():
    auth = _auth()
    assert auth["status"] == "GROUND_TRUTH_SCORING_AUTHORIZED_GO"
    assert auth["next_gate"].endswith("First Ground-Truth Scoring Execution")
