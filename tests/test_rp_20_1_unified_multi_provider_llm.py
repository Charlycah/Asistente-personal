from __future__ import annotations

from app.llm_provider_factory import (
    build_remote_providers_from_environment,
    preferred_remote_order,
    provider_mode_from_environment,
)
from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    LocalProviderExecutionAction,
    LocalProviderExecutionConfig,
    LocalProviderExecutionRequest,
    LocalProviderExecutionStatus,
)
from core.llm_model_providers import GeminiProvider
from core.llm_provider import ConversationMessage, LLMRequest, LLMResponse
from core.operational_response_assembly import (
    OperationalResponseAssembler,
    OperationalResponseAssemblyRequest,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m173_governed_provider_execution_adapter import (
    RecordingProvider,
    remote_route,
)


class HttpResponse:
    status_code = 200
    text = "ok"

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def test_gemini_rest_adapter_preserves_roles_and_generation_settings():
    calls = []

    def post(url, *, json_payload, headers, timeout):
        calls.append((url, json_payload, headers, timeout))
        return HttpResponse(
            {"candidates": [{"content": {"parts": [{"text": "Listo."}]}}]}
        )

    provider = GeminiProvider(
        api_key="secret",
        default_model="gemini-test",
        http_post=post,
    )
    response = provider.generate(
        LLMRequest(
            prompt="ignorado por mensajes",
            system_prompt="Usá voseo rioplatense.",
            messages=(
                ConversationMessage(role="user", content="Hola"),
                ConversationMessage(role="assistant", content="Hola, Carlos."),
                ConversationMessage(role="user", content="Seguimos"),
            ),
            max_tokens=321,
            temperature=0.25,
        )
    )

    assert response == LLMResponse(
        text="Listo.", provider="gemini", model="gemini-test"
    )
    _, payload, _, _ = calls[0]
    assert payload["systemInstruction"]["parts"][0]["text"] == (
        "Usá voseo rioplatense."
    )
    assert [item["role"] for item in payload["contents"]] == [
        "user",
        "model",
        "user",
    ]
    assert payload["generationConfig"] == {
        "maxOutputTokens": 321,
        "temperature": 0.25,
    }


def test_environment_factory_registers_gemini_and_direct_mistral(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.setenv("MISTRAL_API_KEY", "mistral-secret")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("ROBY_GEMINI_MODEL", "gemini-custom")
    monkeypatch.setenv("ROBY_MISTRAL_MODEL", "mistral-custom")

    registrations = build_remote_providers_from_environment()

    assert tuple(item.provider.name for item in registrations) == (
        "gemini",
        "mistral",
    )
    assert registrations[0].model == "gemini-custom"
    assert registrations[1].model == "mistral-custom"
    assert registrations[1].endpoint == ("https://api.mistral.ai/v1/chat/completions")


def test_environment_factory_can_use_openrouter_for_mistral(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("ROBY_MISTRAL_ENDPOINT", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-secret")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    registrations = build_remote_providers_from_environment()

    assert len(registrations) == 1
    assert registrations[0].provider.name == "mistral"
    assert registrations[0].endpoint == (
        "https://openrouter.ai/api/v1/chat/completions"
    )


def test_remote_execution_is_governed_and_explicitly_enabled():
    provider = RecordingProvider(
        name="gemini",
        response=LLMResponse(
            text="Respuesta remota.",
            provider="gemini",
            model="gemini",
        ),
    )
    adapter = GovernedProviderExecutionAdapter(
        (provider,),
        config=LocalProviderExecutionConfig(allow_remote_execution=True),
    )

    result = adapter.execute(
        LocalProviderExecutionRequest(
            owner="Carlos",
            route=remote_route(),
            inference_request=LLMRequest(prompt="Hola ROBY"),
        ),
        now=NOW,
    )

    assert result.status is LocalProviderExecutionStatus.COMPLETED
    assert result.action is LocalProviderExecutionAction.EXECUTE_REMOTE_PROVIDER
    assert result.network_access_allowed
    assert len(provider.calls) == 1


def test_remote_provider_network_lineage_reaches_operational_response():
    provider = RecordingProvider(
        name="gemini",
        response=LLMResponse(
            text="Respuesta remota.",
            provider="gemini",
            model="gemini",
        ),
    )
    execution = GovernedProviderExecutionAdapter(
        (provider,),
        config=LocalProviderExecutionConfig(allow_remote_execution=True),
    ).execute(
        LocalProviderExecutionRequest(
            owner="Carlos",
            route=remote_route(),
            inference_request=LLMRequest(prompt="Hola ROBY"),
        ),
        now=NOW,
    )

    response = OperationalResponseAssembler().assemble(
        OperationalResponseAssemblyRequest(
            owner="Carlos",
            provider_execution=execution,
        ),
        now=NOW,
    )

    assert response.response_text == "Respuesta remota."
    assert response.provider_call_performed
    assert response.network_access_performed


def test_provider_mode_supports_auto_local_gemini_and_mistral(monkeypatch):
    for raw, expected in (
        ("auto", "auto"),
        ("ollama", "local"),
        ("gemini", "gemini"),
        ("mistral", "mistral"),
    ):
        monkeypatch.setenv("ROBY_LLM_PROVIDER", raw)
        assert provider_mode_from_environment() == expected
    assert preferred_remote_order("mistral") == ("mistral", "gemini")
    assert preferred_remote_order("gemini") == ("gemini", "mistral")
