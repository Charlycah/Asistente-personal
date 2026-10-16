from core.llm_model_providers import GeminiProvider, MistralProvider, OllamaProvider
from core.llm_provider import LLMRequest, LLMResponse


class FakeHttpResponse:
    def __init__(self, status_code: int, payload: dict, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> dict:
        return self._payload


class RecordingHttpClient:
    def __init__(self, response: FakeHttpResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def __call__(self, url: str, **kwargs) -> FakeHttpResponse:
        self.calls.append({"url": url, **kwargs})
        return self.response


class FakeGeminiResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeGeminiModel:
    def __init__(self, text: str = "respuesta gemini") -> None:
        self.text = text
        self.prompts: list[str] = []

    def generate_content(self, prompt: str) -> FakeGeminiResponse:
        self.prompts.append(prompt)
        return FakeGeminiResponse(self.text)


def test_ollama_provider_generates_normalized_response():
    http_client = RecordingHttpClient(
        FakeHttpResponse(200, {"response": " hola roby "})
    )
    provider = OllamaProvider(http_post=http_client)

    result = provider.generate(LLMRequest(prompt="Saludar", model="llama3.1"))

    assert result == LLMResponse(text="hola roby", provider="ollama", model="llama3.1")
    assert http_client.calls == [
        {
            "url": "http://localhost:11434/api/generate",
            "json_payload": {
                "model": "llama3.1",
                "prompt": "Saludar",
                "stream": False,
            },
            "headers": {"Content-Type": "application/json"},
            "timeout": 30.0,
        },
    ]


def test_ollama_provider_supports_system_prompt_without_cache_coupling():
    http_client = RecordingHttpClient(FakeHttpResponse(200, {"response": "ok"}))
    provider = OllamaProvider(http_post=http_client)

    provider.generate(LLMRequest(prompt="Responder", system_prompt="Sé breve"))

    assert http_client.calls[0]["json_payload"]["prompt"] == "Sé breve\n\nResponder"


def test_ollama_provider_returns_safe_error_for_http_failure():
    http_client = RecordingHttpClient(FakeHttpResponse(500, {}, "boom"))
    provider = OllamaProvider(http_post=http_client)

    result = provider.generate(LLMRequest(prompt="Hola"))

    assert result == LLMResponse(
        text="Ollama no aceptó la solicitud.",
        provider="ollama",
        model="llama3",
        accepted=False,
        error="ollama_http_error",
    )


def test_mistral_provider_generates_chat_completion_request():
    http_client = RecordingHttpClient(
        FakeHttpResponse(
            200,
            {"choices": [{"message": {"content": " respuesta mistral "}}]},
        ),
    )
    provider = MistralProvider(api_key="secret", http_post=http_client)

    result = provider.generate(
        LLMRequest(
            prompt="Hola",
            system_prompt="Sos ROBY",
            model="mistral-small",
            max_tokens=128,
            temperature=0.2,
        ),
    )

    assert result == LLMResponse(
        text="respuesta mistral",
        provider="mistral",
        model="mistral-small",
    )
    assert http_client.calls[0]["json_payload"] == {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "Sos ROBY"},
            {"role": "user", "content": "Hola"},
        ],
        "max_tokens": 128,
        "temperature": 0.2,
    }
    assert http_client.calls[0]["headers"]["Authorization"] == "Bearer secret"


def test_mistral_provider_requires_api_key():
    provider = MistralProvider(api_key="")

    result = provider.generate(LLMRequest(prompt="Hola"))

    assert result == LLMResponse(
        text="No hay API key configurada para Mistral.",
        provider="mistral",
        model="mistral-7b-instruct",
        accepted=False,
        error="missing_api_key",
    )


def test_gemini_provider_uses_injected_model_client():
    model = FakeGeminiModel(" respuesta gemini ")
    provider = GeminiProvider(model_client=model, default_model="gemini-test")

    result = provider.generate(LLMRequest(prompt="Hola", system_prompt="Sos ROBY"))

    assert result == LLMResponse(
        text="respuesta gemini",
        provider="gemini",
        model="gemini-test",
    )
    assert model.prompts == ["Sos ROBY\n\nHola"]


def test_gemini_provider_returns_safe_error_without_client_or_api_key():
    provider = GeminiProvider(api_key=None)

    result = provider.generate(LLMRequest(prompt="Hola"))

    assert result == LLMResponse(
        text="No hay cliente Gemini configurado.",
        provider="gemini",
        model="gemini-1.5-flash",
        accepted=False,
        error="missing_client",
    )
