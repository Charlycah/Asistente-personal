from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_planning import (
    CognitiveTraceAnomalyLifecycleAssessmentPolicy,
    CognitiveTraceAnomalyLifecycleAssessor,
)
from tests.test_rp_22_16_trace_anomaly_lifecycle_comparison import snapshots


def comparison():
    kernel, previous, current = snapshots()
    return kernel, kernel.compare_trace_anomaly_lifecycle(previous, current)


def test_assessment_classifies_degradation_as_watch() -> None:
    kernel, value = comparison()
    assessment = kernel.assess_trace_anomaly_lifecycle(value)
    assert assessment.schema_version == "rp22.17"
    assert assessment.status == "watch"
    assert "degradation_detected" in assessment.rationale_codes


def test_assessment_reports_net_direction_and_counts() -> None:
    kernel, value = comparison()
    assessment = kernel.assess_trace_anomaly_lifecycle(value)
    assert assessment.changed_count == value.changed_count
    assert assessment.net_direction == value.improving_count - value.degrading_count


def test_empty_comparison_is_stable() -> None:
    kernel, previous, _ = snapshots()
    value = kernel.compare_trace_anomaly_lifecycle(previous, previous)
    assessment = kernel.assess_trace_anomaly_lifecycle(value)
    assert assessment.status == "stable"
    assert assessment.rationale_codes == ("no_changes", "balanced_direction")


def test_explicit_threshold_can_classify_critical() -> None:
    _, value = comparison()
    assessor = CognitiveTraceAnomalyLifecycleAssessor(
        CognitiveTraceAnomalyLifecycleAssessmentPolicy(
            critical_degrading_count=1,
            watch_degrading_count=1,
        )
    )
    assert assessor.assess(value).status == "critical"


def test_assessment_is_immutable_serializable_and_redacted() -> None:
    kernel, value = comparison()
    assessment = kernel.assess_trace_anomaly_lifecycle(value)
    assert "prompt" not in str(assessment.as_dict()).lower()
    with pytest.raises(FrozenInstanceError):
        assessment.status = "critical"  # type: ignore[misc]


def test_policy_validation_and_truncation_reason() -> None:
    _, value = comparison()
    truncated = replace(value, truncated_count=1)
    assessment = CognitiveTraceAnomalyLifecycleAssessor().assess(truncated)
    assert "presentation_truncated" in assessment.rationale_codes
    with pytest.raises(ValueError):
        CognitiveTraceAnomalyLifecycleAssessmentPolicy(
            critical_degrading_count=1,
            watch_degrading_count=2,
        )
