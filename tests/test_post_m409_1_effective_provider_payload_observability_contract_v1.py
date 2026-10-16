from __future__ import annotations

from core.development_console_observability import (
    DevelopmentConsoleObserver,
    DevelopmentConsoleRenderer,
)
from core.llm_provider import (
    ConversationMessage,
    LLMRequest,
    ProviderPayloadObservation,
)
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
    TransportResponse,
)
from tests.test_m173_governed_provider_execution_adapter import (
    RecordingProvider,
    execute,
    execution_request,
)
from tests.test_m224_2_conversational_context_continuity import NOW, runtime


class RecordingTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return TransportResponse(
            200,
            {
                "model": "llama3",
                "choices": [{"message": {"content": "ok"}}],
            },
        )


class PayloadAwareProvider(RecordingProvider):
    def __init__(self) -> None:
        super().__init__()
        self.last_payload_observation = None

    def generate(self, request):
        self.last_payload_observation = ProviderPayloadObservation(
            endpoint_path="/chat/completions",
            message_roles=("system", "user"),
            effective_system_prompt_characters=len(request.system_prompt or ""),
            request_system_prompt_included=bool(request.system_prompt),
        )
        return super().generate(request)


def test_local_adapter_observes_effective_post_adapter_message_roles() -> None:
    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            model="llama3",
            system_prompt="Base local.",
        ),
        transport=transport,
    )

    provider.generate(
        LLMRequest(
            prompt="fallback",
            system_prompt="Grounding gobernado.",
            messages=(ConversationMessage(role="user", content="Hola"),),
        )
    )

    observation = provider.last_payload_observation
    assert observation is not None
    assert observation.endpoint_path == "/chat/completions"
    assert observation.message_roles == ("system", "user")
    assert observation.system_message_count == 1
    assert observation.request_system_prompt_included is True
    assert observation.effective_system_prompt_characters > len("Base local.")


def test_effective_payload_observation_exposes_no_prompt_or_message_content() -> None:
    fields = ProviderPayloadObservation.__dataclass_fields__

    assert "message_contents" not in fields
    assert "system_prompt" not in fields
    assert "headers" not in fields
    assert "api_key" not in fields


def test_execution_result_carries_effective_provider_observation() -> None:
    provider = PayloadAwareProvider()
    result, _ = execute(
        provider=provider,
        request=execution_request(
            inference=LLMRequest(prompt="Hola", system_prompt="Grounding gobernado.")
        ),
    )

    observation = result.provider_payload_observation
    assert observation is not None
    assert observation.message_roles == ("system", "user")
    assert observation.request_system_prompt_included is True


def test_console_observer_projects_effective_provider_observation(tmp_path) -> None:
    provider = PayloadAwareProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)

    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)

    assert observation is not None
    assert observation.provider_message_roles == ("user",)
    assert observation.effective_provider_message_roles == ("system", "user")
    assert observation.effective_provider_system_message_count == 1


def test_renderer_distinguishes_pre_adapter_from_effective_payload(tmp_path) -> None:
    provider = PayloadAwareProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)
    assert observation is not None

    rendered = DevelopmentConsoleRenderer().render_turn(
        observation,
        reveal_prompt=True,
    )

    assert "inference_request_roles=user" in rendered
    effective = next(
        line for line in rendered if line.startswith("effective_provider_payload ")
    )
    assert "endpoint=/chat/completions" in effective
    assert "roles=system,user" in effective
    assert "system=1" in effective
    assert "request_system_included=no" in effective
    assert "effective_provider_payload_verified" in rendered
