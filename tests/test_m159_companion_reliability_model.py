from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.companion_reliability_model import (
    CompanionReliabilityAction,
    CompanionReliabilityConfig,
    CompanionReliabilityModel,
    CompanionReliabilityRequest,
    CompanionReliabilityStatus,
    InMemoryCompanionReliabilityRepository,
    ReliabilityComponent,
    ReliabilityObservation,
)
from core.unified_permission_consent import UnifiedPermissionConsentStatus
from tests.test_m142_presence_context_publication import NOW
from tests.test_m158_unified_permission_consent import evaluate as permission_evaluate


def permission(*, partial=False, owner="Carlos", now=NOW + timedelta(minutes=4)):
    if partial:
        from core.unified_permission_consent import UnifiedPermissionConsent
        from tests.test_m158_unified_permission_consent import continuity, request

        req = request(results=(continuity(partial=True, owner=owner),), owner=owner)
        return UnifiedPermissionConsent().evaluate(req, now=now)
    return permission_evaluate(owner=owner, now=now)


def observation(
    observation_id="obs:source",
    component=ReliabilityComponent.CONTEXT_SOURCE,
    contexts=("desktop:home",),
    owner="Carlos",
    observed_at=NOW + timedelta(minutes=4),
    availability=0.98,
    health=0.96,
    error_rate=0.01,
    latency_ms=100,
    stale=False,
):
    return ReliabilityObservation(
        observation_id=observation_id,
        owner=owner,
        component=component,
        context_ids=contexts,
        observed_at=observed_at,
        availability=availability,
        health=health,
        error_rate=error_rate,
        latency_ms=latency_ms,
        stale=stale,
    )


def observations(**changes):
    source = observation(**changes)
    target = observation(
        observation_id="obs:target",
        component=ReliabilityComponent.CONTEXT_TARGET,
        contexts=("mobile:walking",),
        **{
            k: v
            for k, v in changes.items()
            if k not in {"observation_id", "component", "contexts"}
        },
    )
    return (source, target)


def request(*, results=None, items=None, owner="Carlos", **changes):
    values = dict(
        owner=owner,
        permission_results=results
        if results is not None
        else (permission(owner=owner),),
        observations=items if items is not None else observations(owner=owner),
    )
    values.update(changes)
    return CompanionReliabilityRequest(**values)


def evaluate(*, config=None, now=NOW + timedelta(minutes=5), **changes):
    return CompanionReliabilityModel(config=config).evaluate(
        request(**changes), now=now
    )


def test_reliable_result():
    result = evaluate()
    assert result.status is CompanionReliabilityStatus.RELIABLE
    assert result.action is CompanionReliabilityAction.DECLARE_RELIABLE
    assert result.reliable and not result.degraded and not result.unavailable


def test_partial_permission_degrades_reliability():
    result = evaluate(results=(permission(partial=True),))
    assert result.status is CompanionReliabilityStatus.DEGRADED


@pytest.mark.parametrize("score", [0.84, 0.7, 0.55])
def test_scores_between_thresholds_are_degraded(score):
    result = evaluate(items=observations(health=score))
    assert result.status is CompanionReliabilityStatus.DEGRADED


@pytest.mark.parametrize("score", [0.54, 0.2, 0.0])
def test_low_health_is_unavailable(score):
    result = evaluate(items=observations(health=score))
    assert result.status is CompanionReliabilityStatus.UNAVAILABLE


def test_zero_availability_is_unavailable():
    assert evaluate(items=observations(availability=0)).unavailable


def test_excessive_error_rate_is_unavailable():
    assert evaluate(items=observations(error_rate=0.21)).unavailable


def test_excessive_latency_is_unavailable():
    assert evaluate(items=observations(latency_ms=5001)).unavailable


def test_latency_boundary_is_degraded_not_hard_failure():
    result = evaluate(items=observations(latency_ms=5000))
    assert result.status is CompanionReliabilityStatus.UNAVAILABLE


def test_no_latency_is_supported():
    result = evaluate(items=observations(latency_ms=None))
    assert result.status is CompanionReliabilityStatus.RELIABLE


def test_not_requested_is_not_applicable():
    assert (
        evaluate(evaluation_requested=False).status
        is CompanionReliabilityStatus.NOT_APPLICABLE
    )


def test_no_permission_result_is_not_applicable():
    assert evaluate(results=()).status is CompanionReliabilityStatus.NOT_APPLICABLE


def test_permission_owner_mismatch_is_blocked():
    assert (
        evaluate(results=(permission(owner="Other"),)).status
        is CompanionReliabilityStatus.BLOCKED
    )


def test_observation_owner_mismatch_is_blocked():
    assert (
        evaluate(items=observations(owner="Other")).status
        is CompanionReliabilityStatus.BLOCKED
    )


def test_stale_permission_requires_review():
    old = permission(now=NOW - timedelta(hours=3))
    assert evaluate(results=(old,)).status is CompanionReliabilityStatus.REVIEW_REQUIRED


def test_low_confidence_permission_requires_review():
    source = permission()
    source = replace(source, confidence=0.6, evaluation_id="")
    assert (
        evaluate(results=(source,)).status is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


@pytest.mark.parametrize(
    "status",
    [
        UnifiedPermissionConsentStatus.CONSENT_REQUIRED,
        UnifiedPermissionConsentStatus.DENIED,
    ],
)
def test_non_satisfied_permission_requires_review(status):
    source = permission()
    source = replace(
        source,
        status=status,
        action=(
            "request_explicit_consent"
            if status is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
            else "declare_denial"
        ),
        consent_satisfied=False,
        partial_consent=False,
        explicit_consent_required=status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED,
        consent_denied=status is UnifiedPermissionConsentStatus.DENIED,
        confirmation_required=status
        in {
            UnifiedPermissionConsentStatus.CONSENT_REQUIRED,
        },
        evaluation_id="",
    )
    assert (
        evaluate(results=(source,)).status is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


def test_missing_context_coverage_requires_review():
    assert (
        evaluate(items=(observation(),)).status
        is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


def test_context_coverage_can_be_optional():
    config = CompanionReliabilityConfig(require_context_coverage=False)
    assert (
        evaluate(items=(observation(),), config=config).status
        is CompanionReliabilityStatus.RELIABLE
    )


def test_stale_observations_require_review():
    assert (
        evaluate(items=observations(stale=True)).status
        is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


def test_old_observations_require_review():
    assert (
        evaluate(items=observations(observed_at=NOW - timedelta(hours=1))).status
        is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


def test_future_observations_require_review():
    assert (
        evaluate(items=observations(observed_at=NOW + timedelta(hours=1))).status
        is CompanionReliabilityStatus.REVIEW_REQUIRED
    )


def test_duplicate_observations_are_deduplicated():
    items = observations()
    result = evaluate(items=(items[0], items[0], items[1]))
    assert result.matched_observation_ids == ("obs:source", "obs:target")


def test_duplicate_permission_results_are_deduplicated():
    source = permission()
    result = evaluate(results=(source, source))
    assert result.selected_permission_result is source


def test_permission_result_limit_is_enforced():
    source = permission()
    config = CompanionReliabilityConfig(maximum_permission_results=1)
    assert (
        evaluate(results=(source, source), config=config).status
        is CompanionReliabilityStatus.BLOCKED
    )


def test_observation_limit_is_enforced():
    config = CompanionReliabilityConfig(maximum_observations=1)
    assert evaluate(config=config).status is CompanionReliabilityStatus.BLOCKED


def test_exact_lineage_is_preserved():
    source = permission()
    result = evaluate(results=(source,))
    assert result.selected_permission_result is source
    assert result.selected_continuity is source.selected_continuity
    assert result.selected_timing_evaluation is source.selected_timing_evaluation
    assert result.selected_candidate is source.selected_candidate
    assert result.selected_opportunity is source.selected_opportunity


def test_result_is_immutable():
    result = evaluate()
    with pytest.raises(FrozenInstanceError):
        result.reliable = False


def test_observation_is_immutable():
    item = observation()
    with pytest.raises(FrozenInstanceError):
        item.health = 0


def test_repository_round_trip():
    repository = InMemoryCompanionReliabilityRepository()
    model = CompanionReliabilityModel(repository=repository)
    result = model.evaluate(request(), now=NOW + timedelta(minutes=5))
    assert repository.get(result.reliability_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_result():
    repository = InMemoryCompanionReliabilityRepository()
    model = CompanionReliabilityModel(repository=repository)
    req = request()
    model.evaluate(req, now=NOW + timedelta(minutes=5))
    with pytest.raises(ValueError, match="already exists"):
        model.evaluate(req, now=NOW + timedelta(minutes=5))


def test_identifier_is_deterministic():
    req = request()
    one = CompanionReliabilityModel().evaluate(req, now=NOW + timedelta(minutes=5))
    two = CompanionReliabilityModel().evaluate(req, now=NOW + timedelta(minutes=5))
    assert one.reliability_id == two.reliability_id


@pytest.mark.parametrize(
    "field",
    [
        "conversation_start_allowed",
        "conversational_activation_allowed",
        "device_handoff_allowed",
        "context_transfer_allowed",
        "channel_selection_allowed",
        "scheduling_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    ],
)
def test_downstream_capabilities_remain_forbidden(field):
    assert getattr(evaluate(), field) is False


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_observation_rejects_invalid_health(value):
    with pytest.raises(ValueError):
        observation(health=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_observation_rejects_invalid_availability(value):
    with pytest.raises(ValueError):
        observation(availability=value)


def test_observation_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        observation(observed_at=NOW.replace(tzinfo=None))


def test_evaluation_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        CompanionReliabilityModel().evaluate(request(), now=NOW.replace(tzinfo=None))


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        request(owner=" ")


def test_config_rejects_unordered_thresholds():
    with pytest.raises(ValueError):
        CompanionReliabilityConfig(reliable_threshold=0.5, degraded_threshold=0.6)


def test_rationale_is_explicit():
    assert evaluate().rationale == ("companion_reliability_satisfied",)
