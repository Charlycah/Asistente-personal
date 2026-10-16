from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = (
    ROOT / "benchmarks" / "HCPDQ_V2_H6_SCORING_POSTMORTEM_COGNITIVE_RESULT_AUDIT.json"
)


def _audit():
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_audit_preserves_sealed_zero_of_twelve_result():
    audit = _audit()
    result = audit["sealed_scoring_result"]
    assert result["pass_count"] == 0
    assert result["fail_count"] == 12
    assert result["accuracy"] == 0.0


def test_audit_localizes_uniform_abstention_to_productive_gcdr_path():
    audit = _audit()
    observed = audit["observed_failure_mode"]
    assert observed["uniform_abstention_count"] == 12
    assert observed["recommended_option_count"] == 0
    assert observed["response_template_branch"] == "INSUFFICIENT_EVIDENCE"


def test_audit_replay_explains_all_twelve_without_roby_rerun():
    audit = _audit()
    replay = audit["causal_replay_without_roby_rerun"]
    assert replay["case_count"] == 12
    assert replay["report_status_all"] == "insufficient_evidence"
    assert replay["recommended_option_all"] is None


def test_audit_distinguishes_nonrequired_and_required_case_patterns():
    audit = _audit()
    replay = audit["causal_replay_without_roby_rerun"]
    assert replay["cases_001_006"]["option_status_pattern"] == (
        "review_required + review_required"
    )
    assert replay["cases_007_012"]["option_status_pattern"] == (
        "one blocked + one review_required"
    )


def test_audit_localizes_productive_policy_gap_not_evaluation_boundary():
    audit = _audit()
    determination = audit["architectural_determination"]
    assert determination["entry_path_failure"] is False
    assert determination["isolation_adapter_failure"] is False
    assert determination["scoring_failure"] is False
    assert determination["ground_truth_mismatch"] is False
    assert determination["productive_cognitive_gap"] is True


def test_audit_does_not_change_production_or_repeat_experiment():
    audit = _audit()
    assert audit["production_change_performed"] is False
    assert audit["roby_rerun_performed"] is False
    assert audit["rescoring_performed"] is False
    assert audit["learning_or_tuning_performed"] is False
    assert audit["next_gate"].endswith("H6 Productive Gap — Contract / Go-No-Go")
