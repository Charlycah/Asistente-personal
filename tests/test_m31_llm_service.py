import pytest

from core.llm_model_providers import OllamaProvider
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService, LLMServiceDefaults
from core.provider_router import ProviderRouter, ProviderRouterSnapshot


class RecordingProvider:
    def __init__(self, name: str = "local") -> None:
        self.name = name
        self.calls: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(
            text=f"{self.name}: {request.prompt}",
            provider=self.name,
            model=request.model,
        )


class ExplodingProvider:
    name = "broken"

    def generate(self, request: LLMRequest) -> LLMResponse:
        raise RuntimeError("provider failed")


class FakeHttpResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = ""

    def json(self) -> dict:
        return self._payload


class RecordingHttpClient:
    def __init__(self, response: FakeHttpResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def __call__(self, url: str, **kwargs) -> FakeHttpResponse:
        self.calls.append({"url": url, **kwargs})
        return self.response


def test_provider_router_starts_empty():
    router = ProviderRouter()

    assert router.snapshot == ProviderRouterSnapshot(
        default_provider=None,
        providers=(),
    )


def test_provider_router_registers_first_provider_as_default():
    provider = RecordingProvider("ollama")
    router = ProviderRouter([provider])

    assert router.resolve() is provider
    assert router.snapshot == ProviderRouterSnapshot(
        default_provider="ollama",
        providers=("ollama",),
    )


def test_provider_router_can_switch_default_provider():
    ollama = RecordingProvider("ollama")
    gemini = RecordingProvider("gemini")
    router = ProviderRouter([ollama, gemini])

    router.set_default("gemini")

    assert router.resolve() is gemini
    assert router.snapshot.default_provider == "gemini"


def test_provider_router_rejects_empty_provider_names():
    router = ProviderRouter()

    with pytest.raises(ValueError, match="proveedor LLM"):
        router.register(RecordingProvider("   "))


def test_provider_router_rejects_unknown_default_provider():
    router = ProviderRouter([RecordingProvider("ollama")])

    with pytest.raises(KeyError, match="Proveedor LLM no registrado"):
        router.set_default("mistral")


def test_llm_service_generates_with_default_provider():
    provider = RecordingProvider("ollama")
    service = LLMService(ProviderRouter([provider]))

    result = service.generate("  Hola ROBY  ")

    assert provider.calls == [LLMRequest(prompt="Hola ROBY")]
    assert result == LLMResponse(text="ollama: Hola ROBY", provider="ollama")


def test_llm_service_can_route_to_explicit_provider_without_switching_default():
    ollama = RecordingProvider("ollama")
    mistral = RecordingProvider("mistral")
    router = ProviderRouter([ollama, mistral])
    service = LLMService(router)

    result = service.generate("Responder", provider="mistral")

    assert ollama.calls == []
    assert mistral.calls == [LLMRequest(prompt="Responder")]
    assert result.provider == "mistral"
    assert router.snapshot.default_provider == "ollama"


def test_llm_service_applies_defaults_and_call_overrides():
    provider = RecordingProvider("gemini")
    service = LLMService(
        ProviderRouter([provider]),
        defaults=LLMServiceDefaults(
            system_prompt="Sos ROBY",
            model="base-model",
            max_tokens=256,
            temperature=0.4,
            metadata={"source": "default"},
        ),
    )

    service.generate(
        "Planificar",
        model="override-model",
        metadata={"milestone": "M31"},
    )

    assert provider.calls == [
        LLMRequest(
            prompt="Planificar",
            system_prompt="Sos ROBY",
            model="override-model",
            max_tokens=256,
            temperature=0.4,
            metadata={"source": "default", "milestone": "M31"},
        ),
    ]


def test_llm_service_returns_safe_result_for_empty_prompt_without_touching_provider():
    provider = RecordingProvider("ollama")
    service = LLMService(ProviderRouter([provider]))

    result = service.generate("   ")

    assert provider.calls == []
    assert result == LLMResponse(
        text="Necesito un prompt para consultar el modelo.",
        provider="ollama",
        accepted=False,
        error="empty_prompt",
    )


def test_llm_service_returns_safe_result_without_registered_provider():
    service = LLMService(ProviderRouter())

    result = service.generate("Hola")

    assert result == LLMResponse(
        text="No hay proveedor LLM configurado.",
        provider="none",
        accepted=False,
        error="missing_provider",
    )


def test_llm_service_returns_safe_result_for_unknown_provider():
    service = LLMService(ProviderRouter([RecordingProvider("ollama")]))

    result = service.generate("Hola", provider="gemini")

    assert result == LLMResponse(
        text="Proveedor LLM no registrado: gemini",
        provider="gemini",
        accepted=False,
        error="unknown_provider",
    )


def test_llm_service_turns_provider_failures_into_safe_results():
    service = LLMService(
        ProviderRouter([ExplodingProvider()]),
        defaults=LLMServiceDefaults(model="test-model"),
    )

    result = service.generate("Hola")

    assert result == LLMResponse(
        text="Ocurrió un error al consultar el servicio LLM.",
        provider="broken",
        model="test-model",
        accepted=False,
        error="provider_error",
    )


def test_llm_service_integrates_with_m30_ollama_provider():
    http_client = RecordingHttpClient(
        FakeHttpResponse(200, {"response": " respuesta local "})
    )
    service = LLMService(ProviderRouter([OllamaProvider(http_post=http_client)]))

    result = service.generate("Hola", model="llama3.1")

    assert result == LLMResponse(
        text="respuesta local",
        provider="ollama",
        model="llama3.1",
    )
    assert http_client.calls[0]["json_payload"]["model"] == "llama3.1"
    assert http_client.calls[0]["json_payload"]["prompt"] == "Hola"
