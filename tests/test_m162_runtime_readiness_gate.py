from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.runtime_readiness_gate import (
    InMemoryRuntimeReadinessRepository,
    RuntimeComponentCheck,
    RuntimeComponentKind,
    RuntimeComponentRequirement,
    RuntimeComponentState,
    RuntimeReadinessAction,
    RuntimeReadinessConfig,
    RuntimeReadinessGate,
    RuntimeReadinessRequest,
    RuntimeReadinessStatus,
)
from core.unified_companion_integration import UnifiedCompanionIntegrationStatus
from tests.test_m161_unified_companion_integration import NOW, integrate

BASE = integrate(now=NOW)


def check(
    name,
    kind,
    state=RuntimeComponentState.AVAILABLE,
    requirement=RuntimeComponentRequirement.REQUIRED,
    *,
    provider_name="",
    checked_at=NOW,
):
    return RuntimeComponentCheck(
        name=name,
        kind=kind,
        requirement=requirement,
        state=state,
        provider_name=provider_name,
        checked_at=checked_at,
    )


def checks():
    return (
        check("configuration", RuntimeComponentKind.CONFIGURATION),
        check("memory", RuntimeComponentKind.MEMORY),
        check(
            "ollama llama 3",
            RuntimeComponentKind.PROVIDER,
            provider_name="ollama:llama3",
        ),
        check(
            "internet",
            RuntimeComponentKind.NETWORK,
            requirement=RuntimeComponentRequirement.OPTIONAL,
        ),
    )


def request(*, integration=BASE, component_checks=None, **changes):
    values = {
        "owner": "Carlos",
        "integration_result": integration,
        "component_checks": checks() if component_checks is None else component_checks,
    }
    values.update(changes)
    return RuntimeReadinessRequest(**values)


def evaluate(
    *,
    config=None,
    integration=BASE,
    component_checks=None,
    now=NOW,
    **changes,
):
    gate = RuntimeReadinessGate(config=config)
    return gate.evaluate(
        request(
            integration=integration,
            component_checks=component_checks,
            **changes,
        ),
        now=now,
    )


def replace_check(items, name, **changes):
    return tuple(
        replace(item, **changes, check_id="") if item.name == name else item
        for item in items
    )


def test_ready_when_required_components_and_provider_are_available():
    result = evaluate()
    assert result.status is RuntimeReadinessStatus.READY
    assert result.action is RuntimeReadinessAction.DECLARE_READY
    assert result.ready and not result.degraded and not result.blocked


def test_preserves_exact_m161_lineage():
    result = evaluate()
    assert result.selected_integration_result is BASE
    assert result.request.integration_result is BASE


def test_exposes_available_provider():
    result = evaluate()
    assert result.available_providers == ("ollama:llama3",)
    assert not result.unavailable_providers


def test_optional_unavailable_network_degrades_without_blocking():
    items = replace_check(checks(), "internet", state=RuntimeComponentState.UNAVAILABLE)
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.DEGRADED
    assert result.degraded_checks == (items[-1],)
    assert not result.blocking_checks


def test_degraded_required_component_degrades():
    items = replace_check(checks(), "memory", state=RuntimeComponentState.DEGRADED)
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.DEGRADED
    assert result.degraded_checks == (items[1],)


def test_required_configuration_misconfigured_requests_configuration():
    items = replace_check(
        checks(), "configuration", state=RuntimeComponentState.MISCONFIGURED
    )
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.CONFIGURATION_REQUIRED
    assert result.action is RuntimeReadinessAction.REQUEST_CONFIGURATION
    assert result.configuration_required
    assert result.blocking_checks == (items[0],)


@pytest.mark.parametrize(
    "state",
    [
        RuntimeComponentState.UNAVAILABLE,
        RuntimeComponentState.MISCONFIGURED,
        RuntimeComponentState.UNKNOWN,
    ],
)
def test_required_provider_failure_is_provider_unavailable(state):
    items = replace_check(checks(), "ollama llama 3", state=state)
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.PROVIDER_UNAVAILABLE
    assert result.provider_unavailable
    assert result.unavailable_providers == ("ollama:llama3",)


def test_optional_provider_failure_does_not_block_when_another_provider_is_available():
    items = checks() + (
        check(
            "gemini",
            RuntimeComponentKind.PROVIDER,
            RuntimeComponentState.UNAVAILABLE,
            RuntimeComponentRequirement.OPTIONAL,
            provider_name="gemini",
        ),
    )
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.DEGRADED
    assert result.available_providers == ("ollama:llama3",)
    assert result.unavailable_providers == ("gemini",)


def test_no_provider_available_is_provider_unavailable_even_if_optional():
    items = tuple(
        item for item in checks() if item.kind is not RuntimeComponentKind.PROVIDER
    )
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.PROVIDER_UNAVAILABLE
    assert result.blocking_checks == ()


def test_policy_can_allow_runtime_without_provider():
    items = tuple(
        item for item in checks() if item.kind is not RuntimeComponentKind.PROVIDER
    )
    config = RuntimeReadinessConfig(require_at_least_one_provider=False)
    assert (
        evaluate(config=config, component_checks=items).status
        is RuntimeReadinessStatus.READY
    )


def test_required_non_provider_unavailable_blocks():
    items = replace_check(checks(), "memory", state=RuntimeComponentState.UNAVAILABLE)
    result = evaluate(component_checks=items)
    assert result.status is RuntimeReadinessStatus.BLOCKED
    assert result.blocking_checks == (items[1],)


def test_hold_integration_blocks_gate():
    source = replace(
        BASE,
        status=UnifiedCompanionIntegrationStatus.HOLD,
        action="hold",
        ready=False,
        degraded=False,
        hold=True,
        confirmation_required=True,
        integration_id="",
    )
    result = evaluate(integration=source)
    assert result.status is RuntimeReadinessStatus.BLOCKED
    assert result.rationale == ("unified_companion_integration_not_ready",)


def test_degraded_integration_degrades_by_default():
    source = replace(
        BASE,
        status=UnifiedCompanionIntegrationStatus.DEGRADED,
        action="declare_degraded",
        ready=False,
        degraded=True,
        hold=False,
        confirmation_required=False,
        integration_id="",
    )
    assert evaluate(integration=source).status is RuntimeReadinessStatus.DEGRADED


def test_policy_can_reject_degraded_integration():
    source = replace(
        BASE,
        status=UnifiedCompanionIntegrationStatus.DEGRADED,
        action="declare_degraded",
        ready=False,
        degraded=True,
        hold=False,
        confirmation_required=False,
        integration_id="",
    )
    config = RuntimeReadinessConfig(allow_degraded_companion=False)
    assert (
        evaluate(config=config, integration=source).status
        is RuntimeReadinessStatus.BLOCKED
    )


def test_low_component_confidence_blocks():
    items = tuple(
        replace(item, state=RuntimeComponentState.DEGRADED, check_id="")
        for item in checks()
    )
    config = RuntimeReadinessConfig(minimum_confidence=0.8)
    result = evaluate(config=config, component_checks=items)
    assert result.status is RuntimeReadinessStatus.BLOCKED
    assert result.rationale == ("runtime_readiness_confidence_below_threshold",)


def test_confidence_is_conservative_minimum():
    result = evaluate()
    assert result.confidence == BASE.confidence


def test_not_requested_is_not_applicable():
    result = evaluate(readiness_requested=False)
    assert result.status is RuntimeReadinessStatus.NOT_APPLICABLE
    assert result.selected_integration_result is None
    assert not result.evaluated_checks


def test_gate_never_authorizes_runtime_execution():
    result = evaluate()
    assert not result.activation_allowed
    assert not result.service_start_allowed
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.conversation_start_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryRuntimeReadinessRepository()
    gate = RuntimeReadinessGate(repository=repository)
    result = gate.evaluate(request(), now=NOW)
    assert repository.get(result.readiness_id) is result
    assert repository.list_all() == (result,)
    assert gate.last_evaluation is result


def test_empty_repository_has_no_last_evaluation():
    assert RuntimeReadinessGate().last_evaluation is None


def test_duplicate_result_is_rejected():
    repository = InMemoryRuntimeReadinessRepository()
    gate = RuntimeReadinessGate(repository=repository)
    result = gate.evaluate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_component_check_is_immutable():
    item = checks()[0]
    with pytest.raises(FrozenInstanceError):
        item.name = "other"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_integration_owner():
    with pytest.raises(ValueError, match="match integration owner"):
        request(owner="Other")


def test_cycle_label_is_required():
    with pytest.raises(ValueError, match="cycle label"):
        request(cycle_label=" ")


def test_component_name_is_required():
    with pytest.raises(ValueError, match="component name"):
        check(" ", RuntimeComponentKind.MEMORY)


def test_provider_name_is_required_for_provider_component():
    with pytest.raises(ValueError, match="requires provider name"):
        check("ollama", RuntimeComponentKind.PROVIDER)


def test_provider_name_is_rejected_for_non_provider_component():
    with pytest.raises(ValueError, match="only valid"):
        check("memory", RuntimeComponentKind.MEMORY, provider_name="ollama")


def test_duplicate_component_names_are_rejected():
    first = check("memory", RuntimeComponentKind.MEMORY)
    second = replace(first, checked_at=NOW + timedelta(seconds=1), check_id="")
    with pytest.raises(ValueError, match="names must be unique"):
        request(component_checks=(first, second))


def test_duplicate_component_checks_are_rejected():
    first = check("memory", RuntimeComponentKind.MEMORY)
    with pytest.raises(ValueError, match="must not contain duplicates"):
        request(component_checks=(first, first))


def test_minimum_confidence_must_be_bounded():
    with pytest.raises(ValueError, match="between zero and one"):
        RuntimeReadinessConfig(minimum_confidence=1.1)


def test_component_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        check(
            "memory",
            RuntimeComponentKind.MEMORY,
            checked_at=NOW.replace(tzinfo=None),
        )


def test_evaluation_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        evaluate(now=NOW.replace(tzinfo=None))
