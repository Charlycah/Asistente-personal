from dataclasses import FrozenInstanceError, replace

import pytest

from core.provider_health_evaluation import (
    InMemoryProviderHealthRepository,
    ProviderCapability,
    ProviderHealthAction,
    ProviderHealthConfig,
    ProviderHealthEvaluator,
    ProviderHealthObservation,
    ProviderHealthRequest,
    ProviderHealthState,
    ProviderHealthStatus,
    ProviderKind,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus
from tests.test_m162_runtime_readiness_gate import NOW
from tests.test_m162_runtime_readiness_gate import evaluate as readiness

READINESS = readiness()


def observation(
    name="ollama",
    kind=ProviderKind.LOCAL,
    state=ProviderHealthState.AVAILABLE,
    *,
    model="llama3",
    endpoint="http://localhost:11434",
    version="0.1",
    capabilities=(ProviderCapability.TEXT, ProviderCapability.CODE),
    latency_ms=120,
    configuration_present=True,
    service_reachable=True,
    detail="",
):
    return ProviderHealthObservation(
        provider_name=name,
        provider_kind=kind,
        state=state,
        model_name=model,
        endpoint=endpoint,
        version=version,
        capabilities=capabilities,
        latency_ms=latency_ms,
        configuration_present=configuration_present,
        service_reachable=service_reachable,
        detail=detail,
        observed_at=NOW,
    )


def observations():
    return (
        observation(),
        observation(
            "gemini",
            ProviderKind.REMOTE,
            model="gemini-1.5-flash",
            endpoint="https://generativelanguage.googleapis.com",
            latency_ms=300,
        ),
        observation(
            "mistral",
            ProviderKind.REMOTE,
            ProviderHealthState.DISABLED,
            model="mistral-7b-instruct",
            endpoint="https://openrouter.ai",
            latency_ms=None,
            service_reachable=False,
        ),
    )


def request(*, readiness_result=READINESS, items=None, **changes):
    values = {
        "owner": "Carlos",
        "readiness_result": readiness_result,
        "observations": observations() if items is None else items,
    }
    values.update(changes)
    return ProviderHealthRequest(**values)


def evaluate(*, config=None, readiness_result=READINESS, items=None, **changes):
    evaluator = ProviderHealthEvaluator(config=config)
    return evaluator.evaluate(
        request(readiness_result=readiness_result, items=items, **changes),
        now=NOW,
    )


def test_reports_degraded_when_some_providers_are_unavailable():
    result = evaluate()
    assert result.status is ProviderHealthStatus.DEGRADED
    assert result.action is ProviderHealthAction.PUBLISH_HEALTH
    assert tuple(item.provider_name for item in result.available_providers) == (
        "ollama",
        "gemini",
    )
    assert tuple(item.provider_name for item in result.unavailable_providers) == (
        "mistral",
    )


def test_reports_healthy_when_all_providers_are_available():
    result = evaluate(items=observations()[:2])
    assert result.status is ProviderHealthStatus.HEALTHY
    assert result.local_available
    assert result.remote_available


def test_preserves_exact_m162_lineage():
    result = evaluate()
    assert result.request.readiness_result is READINESS


def test_local_ollama_can_be_the_only_available_provider():
    result = evaluate(items=(observation(),))
    assert result.status is ProviderHealthStatus.HEALTHY
    assert result.local_available
    assert not result.remote_available


def test_remote_only_health_is_reported():
    gemini = observation("gemini", ProviderKind.REMOTE, model="gemini")
    result = evaluate(items=(gemini,))
    assert not result.local_available
    assert result.remote_available


def test_slow_available_provider_is_normalized_to_degraded():
    slow = observation(latency_ms=3000)
    result = evaluate(items=(slow,))
    assert result.status is ProviderHealthStatus.UNAVAILABLE
    assert result.degraded_providers[0].state is ProviderHealthState.DEGRADED


def test_policy_can_publish_degraded_health_without_available_provider():
    slow = observation(latency_ms=3000)
    config = ProviderHealthConfig(require_at_least_one_available=False)
    result = evaluate(config=config, items=(slow,))
    assert result.status is ProviderHealthStatus.DEGRADED


def test_misconfigured_provider_requests_configuration():
    gemini = observation(
        "gemini",
        ProviderKind.REMOTE,
        ProviderHealthState.MISCONFIGURED,
        model="gemini",
        configuration_present=False,
        service_reachable=False,
        latency_ms=None,
    )
    result = evaluate(items=(observation(), gemini))
    assert result.status is ProviderHealthStatus.CONFIGURATION_REQUIRED
    assert result.action is ProviderHealthAction.REQUEST_CONFIGURATION
    assert result.configuration_required_providers == (gemini,)


def test_configuration_priority_can_be_disabled():
    gemini = observation(
        "gemini",
        ProviderKind.REMOTE,
        ProviderHealthState.MISCONFIGURED,
        model="gemini",
        configuration_present=False,
        service_reachable=False,
        latency_ms=None,
    )
    config = ProviderHealthConfig(configuration_error_has_priority=False)
    result = evaluate(config=config, items=(observation(), gemini))
    assert result.status is ProviderHealthStatus.DEGRADED


def test_no_available_provider_is_unavailable():
    offline = observation(
        state=ProviderHealthState.OFFLINE,
        service_reachable=False,
        latency_ms=None,
    )
    result = evaluate(items=(offline,))
    assert result.status is ProviderHealthStatus.UNAVAILABLE
    assert result.action is ProviderHealthAction.WITHHOLD


@pytest.mark.parametrize(
    "status",
    [
        RuntimeReadinessStatus.BLOCKED,
        RuntimeReadinessStatus.CONFIGURATION_REQUIRED,
        RuntimeReadinessStatus.NOT_APPLICABLE,
    ],
)
def test_non_ready_runtime_withholds_provider_health(status):
    source = replace(
        READINESS,
        status=status,
        action=(
            "none" if status is RuntimeReadinessStatus.NOT_APPLICABLE else "withhold"
        ),
        selected_integration_result=(
            None
            if status is RuntimeReadinessStatus.NOT_APPLICABLE
            else READINESS.selected_integration_result
        ),
        evaluated_checks=(
            ()
            if status is RuntimeReadinessStatus.NOT_APPLICABLE
            else READINESS.evaluated_checks
        ),
        blocking_checks=(),
        degraded_checks=(),
        available_providers=(),
        unavailable_providers=(),
        confidence=(
            0
            if status is RuntimeReadinessStatus.NOT_APPLICABLE
            else READINESS.confidence
        ),
        ready=False,
        degraded=False,
        blocked=status is RuntimeReadinessStatus.BLOCKED,
        configuration_required=status is RuntimeReadinessStatus.CONFIGURATION_REQUIRED,
        provider_unavailable=False,
        rationale=("test",),
        readiness_id="",
    )
    result = evaluate(readiness_result=source)
    assert result.status is ProviderHealthStatus.UNAVAILABLE


def test_not_requested_is_not_applicable():
    result = evaluate(evaluation_requested=False)
    assert result.status is ProviderHealthStatus.NOT_APPLICABLE
    assert result.action is ProviderHealthAction.NONE
    assert not result.evaluated_observations


def test_m166_never_authorizes_external_side_effects():
    result = evaluate()
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryProviderHealthRepository()
    evaluator = ProviderHealthEvaluator(repository=repository)
    result = evaluator.evaluate(request(), now=NOW)
    assert repository.get(result.evaluation_id) is result
    assert repository.list_all() == (result,)
    assert evaluator.last_evaluation is result


def test_empty_repository_has_no_last_evaluation():
    assert ProviderHealthEvaluator().last_evaluation is None


def test_duplicate_result_is_rejected():
    repository = InMemoryProviderHealthRepository()
    evaluator = ProviderHealthEvaluator(repository=repository)
    result = evaluator.evaluate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_observation_is_immutable():
    item = observation()
    with pytest.raises(FrozenInstanceError):
        item.provider_name = "other"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_readiness_owner():
    with pytest.raises(ValueError, match="match readiness owner"):
        request(owner="Other")


def test_provider_name_is_required():
    with pytest.raises(ValueError, match="provider name"):
        observation(name=" ")


def test_duplicate_provider_names_are_rejected():
    first = observation()
    second = replace(first, model_name="other", observation_id="")
    with pytest.raises(ValueError, match="names must be unique"):
        request(items=(first, second))


def test_duplicate_capabilities_are_rejected():
    with pytest.raises(ValueError, match="capabilities must be unique"):
        observation(capabilities=(ProviderCapability.TEXT, ProviderCapability.TEXT))


def test_negative_latency_is_rejected():
    with pytest.raises(ValueError, match="must not be negative"):
        observation(latency_ms=-1)


def test_misconfigured_provider_requires_missing_configuration():
    with pytest.raises(ValueError, match="valid configuration"):
        observation(state=ProviderHealthState.MISCONFIGURED)


def test_offline_provider_cannot_be_reachable():
    with pytest.raises(ValueError, match="reachable service"):
        observation(state=ProviderHealthState.OFFLINE)


def test_available_provider_requires_configuration():
    with pytest.raises(ValueError, match="requires configuration"):
        observation(configuration_present=False)


def test_available_provider_requires_reachable_service():
    with pytest.raises(ValueError, match="reachable service"):
        observation(service_reachable=False)


def test_maximum_latency_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        ProviderHealthConfig(maximum_healthy_latency_ms=0)


def test_observation_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(observation(), observed_at=NOW.replace(tzinfo=None), observation_id="")


def test_evaluation_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        ProviderHealthEvaluator().evaluate(
            request(),
            now=NOW.replace(tzinfo=None),
        )
