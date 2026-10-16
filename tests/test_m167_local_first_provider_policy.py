from dataclasses import FrozenInstanceError, replace

import pytest

from core.local_first_provider_policy import (
    InMemoryLocalFirstProviderRepository,
    LocalFirstProviderConfig,
    LocalFirstProviderPolicy,
    LocalFirstProviderRequest,
    ProviderPolicyAction,
    ProviderPolicyStatus,
    ProviderWorkload,
    ProviderWorkloadKind,
)
from core.provider_health_evaluation import (
    ProviderCapability,
    ProviderHealthConfig,
    ProviderHealthStatus,
)
from tests.test_m166_provider_health_evaluation import (
    NOW,
    observation,
    observations,
)
from tests.test_m166_provider_health_evaluation import (
    evaluate as health,
)

HEALTH = health(items=observations()[:2])


def workload(
    kind=ProviderWorkloadKind.CONVERSATION,
    *,
    capabilities=(ProviderCapability.TEXT,),
    provider_required=True,
    current_information_required=False,
    remote_required=False,
    sensitive=False,
    detail="",
):
    return ProviderWorkload(
        kind=kind,
        required_capabilities=capabilities,
        provider_required=provider_required,
        current_information_required=current_information_required,
        remote_required=remote_required,
        sensitive=sensitive,
        detail=detail,
    )


def request(*, health_result=HEALTH, task=None, **changes):
    values = {
        "owner": "Carlos",
        "health_result": health_result,
        "workload": workload() if task is None else task,
    }
    values.update(changes)
    return LocalFirstProviderRequest(**values)


def decide(*, config=None, health_result=HEALTH, task=None, **changes):
    policy = LocalFirstProviderPolicy(config=config)
    return policy.decide(
        request(health_result=health_result, task=task, **changes),
        now=NOW,
    )


def test_prefers_local_provider_when_local_and_remote_are_available():
    result = decide()
    assert result.status is ProviderPolicyStatus.LOCAL_PREFERRED
    assert result.action is ProviderPolicyAction.DECLARE_LOCAL_PREFERENCE
    assert result.preferred_kind.value == "local"
    assert tuple(item.provider_name for item in result.eligible_local_providers) == (
        "ollama",
    )
    assert tuple(item.provider_name for item in result.eligible_remote_providers) == (
        "gemini",
    )


def test_preserves_exact_m166_lineage():
    result = decide()
    assert result.request.health_result is HEALTH


def test_greeting_can_require_no_provider():
    greeting = workload(provider_required=False, capabilities=())
    result = decide(task=greeting)
    assert result.status is ProviderPolicyStatus.NO_PROVIDER_REQUIRED
    assert result.action is ProviderPolicyAction.DECLARE_NO_PROVIDER_REQUIRED
    assert result.preferred_kind is None
    assert not result.eligible_local_providers
    assert not result.eligible_remote_providers


def test_current_information_declares_remote_fallback():
    task = workload(
        ProviderWorkloadKind.CURRENT_INFORMATION,
        current_information_required=True,
    )
    result = decide(task=task)
    assert result.status is ProviderPolicyStatus.REMOTE_FALLBACK
    assert result.preferred_kind.value == "remote"
    assert result.rationale == ("workload_requires_remote_provider",)


def test_explicit_remote_requirement_declares_remote_fallback():
    task = workload(remote_required=True)
    result = decide(task=task)
    assert result.status is ProviderPolicyStatus.REMOTE_FALLBACK


def test_sensitive_workload_prefers_local_provider():
    result = decide(task=workload(sensitive=True))
    assert result.status is ProviderPolicyStatus.LOCAL_PREFERRED
    assert result.rationale == ("sensitive_workload_prefers_local_provider",)


def test_remote_is_fallback_when_local_is_unavailable():
    remote_only = health(
        items=(
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://example.invalid",
            ),
        )
    )
    result = decide(health_result=remote_only)
    assert result.status is ProviderPolicyStatus.REMOTE_FALLBACK
    assert result.rationale == ("local_provider_unavailable_remote_fallback_declared",)


def test_remote_fallback_can_be_disabled():
    remote_only = health(
        items=(
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://example.invalid",
            ),
        )
    )
    config = LocalFirstProviderConfig(allow_remote_fallback=False)
    result = decide(config=config, health_result=remote_only)
    assert result.status is ProviderPolicyStatus.WITHHELD


def test_remote_required_is_withheld_when_remote_fallback_is_disabled():
    config = LocalFirstProviderConfig(allow_remote_fallback=False)
    result = decide(config=config, task=workload(remote_required=True))
    assert result.status is ProviderPolicyStatus.WITHHELD
    assert result.rationale == ("required_remote_provider_unavailable",)


def test_capabilities_filter_ineligible_local_provider():
    task = workload(
        ProviderWorkloadKind.VISION,
        capabilities=(ProviderCapability.VISION,),
    )
    result = decide(task=task)
    assert result.status is ProviderPolicyStatus.WITHHELD
    assert not result.eligible_local_providers
    assert not result.eligible_remote_providers


def test_remote_provider_can_satisfy_missing_local_capability():
    items = (
        observation(),
        observation(
            "gemini",
            kind="remote",
            model="gemini",
            endpoint="https://example.invalid",
            capabilities=(ProviderCapability.TEXT, ProviderCapability.VISION),
        ),
    )
    source = health(items=items)
    task = workload(
        ProviderWorkloadKind.VISION,
        capabilities=(ProviderCapability.VISION,),
    )
    result = decide(health_result=source, task=task)
    assert result.status is ProviderPolicyStatus.REMOTE_FALLBACK
    assert not result.eligible_local_providers
    assert result.eligible_remote_providers[0].provider_name == "gemini"


def test_degraded_provider_is_ineligible_by_default():
    slow = observation(latency_ms=3000)
    source = health(
        config=None,
        items=(
            slow,
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://example.invalid",
            ),
        ),
    )
    result = decide(health_result=source)
    assert result.status is ProviderPolicyStatus.REMOTE_FALLBACK


def test_policy_can_allow_degraded_provider():
    slow = observation(latency_ms=3000)
    source = health(
        config=ProviderHealthConfig(require_at_least_one_available=False),
        items=(slow,),
    )
    config = LocalFirstProviderConfig(allow_degraded_providers=True)
    result = decide(config=config, health_result=source)
    assert result.status is ProviderPolicyStatus.LOCAL_PREFERRED


@pytest.mark.parametrize(
    "status",
    [
        ProviderHealthStatus.UNAVAILABLE,
        ProviderHealthStatus.CONFIGURATION_REQUIRED,
        ProviderHealthStatus.NOT_APPLICABLE,
    ],
)
def test_unusable_health_withholds_policy(status):
    source = replace(
        HEALTH,
        status=status,
        action=(
            "none" if status is ProviderHealthStatus.NOT_APPLICABLE else "withhold"
        ),
        evaluated_observations=(
            ()
            if status is ProviderHealthStatus.NOT_APPLICABLE
            else HEALTH.evaluated_observations
        ),
        available_providers=(
            ()
            if status is ProviderHealthStatus.NOT_APPLICABLE
            else HEALTH.available_providers
        ),
        degraded_providers=(),
        unavailable_providers=(),
        configuration_required_providers=(),
        local_available=(
            False if status is ProviderHealthStatus.NOT_APPLICABLE else True
        ),
        remote_available=(
            False if status is ProviderHealthStatus.NOT_APPLICABLE else True
        ),
        rationale=("test",),
        evaluation_id="",
    )
    result = decide(health_result=source)
    assert result.status is ProviderPolicyStatus.WITHHELD


def test_not_requested_is_not_applicable():
    result = decide(policy_requested=False)
    assert result.status is ProviderPolicyStatus.NOT_APPLICABLE
    assert result.action is ProviderPolicyAction.NONE


def test_m167_never_authorizes_provider_execution():
    result = decide()
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.routing_allowed
    assert not result.platform_mutation_allowed
    assert result.selected_provider is None


def test_repository_stores_decision_and_exposes_last():
    repository = InMemoryLocalFirstProviderRepository()
    policy = LocalFirstProviderPolicy(repository=repository)
    result = policy.decide(request(), now=NOW)
    assert repository.get(result.decision_id) is result
    assert repository.list_all() == (result,)
    assert policy.last_decision is result


def test_empty_repository_has_no_last_decision():
    assert LocalFirstProviderPolicy().last_decision is None


def test_duplicate_decision_is_rejected():
    repository = InMemoryLocalFirstProviderRepository()
    policy = LocalFirstProviderPolicy(repository=repository)
    result = policy.decide(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_workload_is_immutable():
    item = workload()
    with pytest.raises(FrozenInstanceError):
        item.kind = ProviderWorkloadKind.CODE


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_health_owner():
    with pytest.raises(ValueError, match="match health owner"):
        request(owner="Other")


def test_duplicate_capabilities_are_rejected():
    with pytest.raises(ValueError, match="capabilities must be unique"):
        workload(
            capabilities=(ProviderCapability.TEXT, ProviderCapability.TEXT),
        )


def test_remote_requirement_requires_provider():
    with pytest.raises(ValueError, match="needs a provider"):
        workload(provider_required=False, remote_required=True)


def test_current_information_requires_provider():
    with pytest.raises(ValueError, match="needs a provider"):
        workload(
            provider_required=False,
            current_information_required=True,
        )


def test_timestamp_must_be_timezone_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        LocalFirstProviderPolicy().decide(
            request(),
            now=NOW.replace(tzinfo=None),
        )


def test_decision_is_immutable():
    result = decide()
    with pytest.raises(FrozenInstanceError):
        result.status = ProviderPolicyStatus.WITHHELD
