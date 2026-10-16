from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_planning import (
    CognitiveTraceAnomalyLifecycleAdvisor,
    CognitiveTraceAnomalyLifecycleGuidancePolicy,
)
from tests.test_rp_22_17_trace_anomaly_lifecycle_assessment import comparison


def assessment():
    kernel, value = comparison()
    return kernel, kernel.assess_trace_anomaly_lifecycle(value)


def test_watch_assessment_produces_routine_guidance() -> None:
    kernel, value = assessment()
    guidance = kernel.advise_trace_anomaly_lifecycle(value)
    assert guidance.schema_version == "rp22.18"
    assert guidance.urgency == "routine"
    assert guidance.requires_human_review is True


def test_stable_assessment_keeps_observation_only() -> None:
    kernel, value = assessment()
    stable = replace(value, status="stable")
    guidance = kernel.advise_trace_anomaly_lifecycle(stable)
    assert guidance.urgency == "none"
    assert guidance.action_codes == ("continue_local_observation",)


def test_critical_assessment_requests_immediate_review() -> None:
    kernel, value = assessment()
    critical = replace(value, status="critical")
    guidance = kernel.advise_trace_anomaly_lifecycle(critical)
    assert guidance.urgency == "immediate"
    assert guidance.requires_human_review is True


def test_policy_limits_action_codes_deterministically() -> None:
    _, value = assessment()
    critical = replace(value, status="critical")
    advisor = CognitiveTraceAnomalyLifecycleAdvisor(
        CognitiveTraceAnomalyLifecycleGuidancePolicy(maximum_action_codes=1)
    )
    assert advisor.advise(critical).action_codes == (
        "inspect_degrading_anomalies",
    )


def test_guidance_is_immutable_serializable_and_redacted() -> None:
    kernel, value = assessment()
    guidance = kernel.advise_trace_anomaly_lifecycle(value)
    assert "prompt" not in str(guidance.as_dict()).lower()
    with pytest.raises(FrozenInstanceError):
        guidance.urgency = "immediate"  # type: ignore[misc]


def test_policy_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError):
        CognitiveTraceAnomalyLifecycleGuidancePolicy(maximum_action_codes=0)
