from dataclasses import FrozenInstanceError, replace

import pytest

from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    InMemoryLocalProviderExecutionRepository,
    LocalProviderExecutionAction,
    LocalProviderExecutionConfig,
    LocalProviderExecutionRequest,
    LocalProviderExecutionStatus,
)
from core.governed_provider_routing import (
    GovernedProviderRouter,
    GovernedProviderRoutingRequest,
)
from core.llm_provider import LLMRequest, LLMResponse
from tests.test_m166_provider_health_evaluation import NOW, observation
from tests.test_m166_provider_health_evaluation import evaluate as health
from tests.test_m167_local_first_provider_policy import decide as policy
from tests.test_m167_local_first_provider_policy import workload


class RecordingProvider:
    def __init__(self, name="ollama", response=None, error=None):
        self.name = name
        self.response = response or LLMResponse(
            text="Hola desde el proveedor local.",
            provider=name,
            model="llama3",
        )
        self.error = error
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.response


class InvalidProvider:
    name = "ollama"

    def generate(self, request):
        return {"text": "invalid"}


def local_route():
    decision = policy(
        health_result=health(items=(observation(),)),
    )
    return GovernedProviderRouter().route(
        GovernedProviderRoutingRequest(owner="Carlos", policy_decision=decision),
        now=NOW,
    )


def remote_route():
    source = health(
        items=(
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://example.invalid",
            ),
        )
    )
    decision = policy(
        health_result=source,
        task=workload(remote_required=True),
    )
    return GovernedProviderRouter().route(
        GovernedProviderRoutingRequest(owner="Carlos", policy_decision=decision),
        now=NOW,
    )


def execution_request(*, route=None, inference=None, **changes):
    values = {
        "owner": "Carlos",
        "route": route or local_route(),
        "inference_request": inference or LLMRequest(prompt="Hola ROBY"),
    }
    values.update(changes)
    return LocalProviderExecutionRequest(**values)


def execute(*, provider=None, config=None, request=None):
    provider = provider or RecordingProvider()
    adapter = GovernedProviderExecutionAdapter((provider,), config=config)
    return adapter.execute(request or execution_request(), now=NOW), provider


def test_executes_selected_local_provider():
    result, provider = execute()
    assert result.status is LocalProviderExecutionStatus.COMPLETED
    assert result.action is LocalProviderExecutionAction.EXECUTE_LOCAL_PROVIDER
    assert result.response.text == "Hola desde el proveedor local."
    assert len(provider.calls) == 1


def test_preserves_exact_m168_route_lineage():
    route = local_route()
    result, _ = execute(request=execution_request(route=route))
    assert result.request.route is route


def test_forces_routed_model_into_provider_request():
    result, provider = execute()
    assert result.selected_model_name == "llama3"
    assert provider.calls[0].model == "llama3"


def test_preserves_request_fields_and_metadata():
    request = LLMRequest(
        prompt="Explica esto",
        system_prompt="Sé claro",
        max_tokens=123,
        temperature=0.2,
        metadata={"turn": "7"},
    )
    _, provider = execute(request=execution_request(inference=request))
    call = provider.calls[0]
    assert call.system_prompt == "Sé claro"
    assert call.max_tokens == 123
    assert call.temperature == 0.2
    assert call.metadata == {"turn": "7"}


def test_does_not_mutate_original_inference_request():
    original = LLMRequest(prompt="Hola", metadata={"a": "b"})
    execute(request=execution_request(inference=original))
    assert original.model is None
    assert original.metadata == {"a": "b"}


def test_execution_not_requested_is_not_applicable():
    result, provider = execute(request=execution_request(execution_requested=False))
    assert result.status is LocalProviderExecutionStatus.NOT_APPLICABLE
    assert not provider.calls


def test_configuration_can_withhold_execution():
    config = LocalProviderExecutionConfig(allow_local_execution=False)
    result, provider = execute(config=config)
    assert result.status is LocalProviderExecutionStatus.WITHHELD
    assert not provider.calls


def test_remote_route_is_withheld_without_call():
    provider = RecordingProvider("gemini")
    result, provider = execute(
        provider=provider,
        request=execution_request(route=remote_route()),
    )
    assert result.status is LocalProviderExecutionStatus.WITHHELD
    assert not provider.calls


def test_unregistered_local_provider_is_withheld():
    adapter = GovernedProviderExecutionAdapter(())
    result = adapter.execute(execution_request(), now=NOW)
    assert result.status is LocalProviderExecutionStatus.WITHHELD
    assert not result.provider_call_performed


def test_explicit_model_mismatch_is_withheld():
    inference = LLMRequest(prompt="Hola", model="other-model")
    result, provider = execute(request=execution_request(inference=inference))
    assert result.status is LocalProviderExecutionStatus.WITHHELD
    assert not provider.calls


def test_model_match_can_be_relaxed_but_route_model_still_wins():
    config = LocalProviderExecutionConfig(require_route_model_match=False)
    inference = LLMRequest(prompt="Hola", model="other-model")
    result, provider = execute(
        config=config,
        request=execution_request(inference=inference),
    )
    assert result.status is LocalProviderExecutionStatus.COMPLETED
    assert provider.calls[0].model == "llama3"


def test_prompt_limit_withholds_before_call():
    config = LocalProviderExecutionConfig(maximum_prompt_characters=4)
    result, provider = execute(
        config=config,
        request=execution_request(inference=LLMRequest(prompt="12345")),
    )
    assert result.status is LocalProviderExecutionStatus.WITHHELD
    assert not provider.calls


def test_provider_exception_is_contained():
    provider = RecordingProvider(error=RuntimeError("boom"))
    result, provider = execute(provider=provider)
    assert result.status is LocalProviderExecutionStatus.FAILED
    assert result.response.error == "RuntimeError"
    assert len(provider.calls) == 1


def test_invalid_response_type_is_failed():
    result, _ = execute(provider=InvalidProvider())
    assert result.status is LocalProviderExecutionStatus.FAILED
    assert result.response.error == "invalid_response_type"


def test_response_provider_mismatch_is_rejected():
    response = LLMResponse(text="remote", provider="gemini", model="llama3")
    result, _ = execute(provider=RecordingProvider(response=response))
    assert result.status is LocalProviderExecutionStatus.REJECTED
    assert result.response.error == "provider_mismatch"


def test_response_model_mismatch_is_rejected():
    response = LLMResponse(text="wrong", provider="ollama", model="other")
    result, _ = execute(provider=RecordingProvider(response=response))
    assert result.status is LocalProviderExecutionStatus.REJECTED
    assert result.response.error == "model_mismatch"


def test_provider_rejection_is_failed():
    response = LLMResponse(
        text="not accepted",
        provider="ollama",
        model="llama3",
        accepted=False,
        error="local_error",
    )
    result, _ = execute(provider=RecordingProvider(response=response))
    assert result.status is LocalProviderExecutionStatus.FAILED
    assert result.response.error == "local_error"


def test_empty_response_is_rejected():
    response = LLMResponse(text="   ", provider="ollama", model="llama3")
    result, _ = execute(provider=RecordingProvider(response=response))
    assert result.status is LocalProviderExecutionStatus.REJECTED
    assert result.response.error == "empty_response"


def test_response_limit_rejects_large_content():
    config = LocalProviderExecutionConfig(maximum_response_characters=3)
    response = LLMResponse(text="1234", provider="ollama", model="llama3")
    result, _ = execute(config=config, provider=RecordingProvider(response=response))
    assert result.status is LocalProviderExecutionStatus.REJECTED
    assert result.response.error == "response_too_large"


def test_successful_response_is_trimmed_and_normalized():
    response = LLMResponse(text="  contenido  ", provider="OLLAMA", model=None)
    result, _ = execute(provider=RecordingProvider(response=response))
    assert result.response == LLMResponse(
        text="contenido", provider="ollama", model="llama3", accepted=True
    )


def test_execution_never_allows_external_network_or_remote_fallback():
    result, _ = execute()
    assert not result.network_access_allowed
    assert not result.remote_fallback_allowed
    assert not result.platform_mutation_allowed


def test_attempt_flags_are_true_only_after_provider_call():
    completed, _ = execute()
    withheld, _ = execute(request=execution_request(execution_requested=False))
    assert completed.provider_call_performed and completed.inference_performed
    assert not withheld.provider_call_performed
    assert not withheld.inference_performed


def test_repository_stores_execution_and_exposes_last():
    repository = InMemoryLocalProviderExecutionRepository()
    adapter = GovernedProviderExecutionAdapter(
        (RecordingProvider(),), repository=repository
    )
    result = adapter.execute(execution_request(), now=NOW)
    assert repository.get(result.execution_id) is result
    assert repository.list_all() == (result,)
    assert adapter.last_execution is result


def test_empty_adapter_has_no_last_execution():
    assert GovernedProviderExecutionAdapter().last_execution is None


def test_duplicate_execution_is_rejected():
    repository = InMemoryLocalProviderExecutionRepository()
    adapter = GovernedProviderExecutionAdapter(
        (RecordingProvider(),), repository=repository
    )
    request = execution_request()
    adapter.execute(request, now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        adapter.execute(request, now=NOW)


def test_duplicate_provider_registration_is_rejected_case_insensitively():
    with pytest.raises(ValueError, match="unique"):
        GovernedProviderExecutionAdapter(
            (RecordingProvider("ollama"), RecordingProvider("OLLAMA"))
        )


def test_blank_provider_registration_is_rejected():
    with pytest.raises(ValueError, match="name"):
        GovernedProviderExecutionAdapter((RecordingProvider(" "),))


def test_owner_is_required_and_must_match_route():
    with pytest.raises(ValueError, match="owner"):
        execution_request(owner=" ")
    with pytest.raises(ValueError, match="match"):
        execution_request(owner="Other")


def test_prompt_is_required():
    with pytest.raises(ValueError, match="prompt"):
        execution_request(inference=LLMRequest(prompt=" "))


def test_config_limits_must_be_positive():
    with pytest.raises(ValueError, match="prompt"):
        LocalProviderExecutionConfig(maximum_prompt_characters=0)
    with pytest.raises(ValueError, match="response"):
        LocalProviderExecutionConfig(maximum_response_characters=0)


def test_execution_result_is_immutable():
    result, _ = execute()
    with pytest.raises(FrozenInstanceError):
        result.status = LocalProviderExecutionStatus.FAILED


def test_execution_id_detects_tampering():
    result, _ = execute()
    with pytest.raises(ValueError, match="id"):
        replace(result, execution_id="tampered")
