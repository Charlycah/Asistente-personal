from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.local_provider_factory import build_local_provider_from_environment
from core.llm_provider import LLMRequest
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
    LocalProviderRuntimeState,
    LocalProviderTransportError,
    TransportResponse,
)


class FakeTransport:
    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise LocalProviderTransportError(self.error)
        return self.responses.pop(0)


def settings(**changes):
    values = {
        "provider_name": "ollama-local",
        "endpoint": "http://127.0.0.1:11434/v1/",
        "model": "llama3.2",
        "timeout_seconds": 10,
        "health_timeout_seconds": 2,
    }
    values.update(changes)
    return LocalProviderRuntimeSettings(**values)


def completion(text="Hola Carlos", model="llama3.2"):
    return TransportResponse(
        200,
        {"model": model, "choices": [{"message": {"content": text}}]},
    )


def test_settings_normalize_endpoint():
    assert settings().endpoint == "http://127.0.0.1:11434/v1"


def test_settings_are_immutable():
    with pytest.raises(FrozenInstanceError):
        settings().model = "otro"


@pytest.mark.parametrize("endpoint", ["localhost:11434/v1", "file:///tmp/model"])
def test_settings_reject_non_http_endpoint(endpoint):
    with pytest.raises(ValueError, match="http"):
        settings(endpoint=endpoint)


@pytest.mark.parametrize("field", ["timeout_seconds", "health_timeout_seconds"])
def test_settings_reject_non_positive_timeouts(field):
    with pytest.raises(ValueError, match="positive"):
        settings(**{field: 0})


def test_health_reports_available_models_and_latency():
    transport = FakeTransport(
        [TransportResponse(200, {"data": [{"id": "llama3.2"}, {"id": "qwen"}]})]
    )
    health = LocalProviderRuntimeAdapter(settings(), transport=transport).health()
    assert health.state is LocalProviderRuntimeState.AVAILABLE
    assert health.available_models == ("llama3.2", "qwen")
    assert health.latency_ms is not None
    assert transport.calls[0]["url"].endswith("/models")
    assert transport.calls[0]["timeout"] == 2


def test_health_reports_configured_model_missing():
    transport = FakeTransport([TransportResponse(200, {"data": [{"id": "qwen"}]})])
    health = LocalProviderRuntimeAdapter(settings(), transport=transport).health()
    assert health.state is LocalProviderRuntimeState.MISCONFIGURED
    assert health.error_code == "model_unavailable"


def test_health_contains_transport_failure():
    health = LocalProviderRuntimeAdapter(
        settings(), transport=FakeTransport(error="unreachable")
    ).health()
    assert health.state is LocalProviderRuntimeState.UNAVAILABLE
    assert health.error_code == "unreachable"


def test_generate_uses_chat_completions_and_normalizes_response():
    transport = FakeTransport([completion()])
    provider = LocalProviderRuntimeAdapter(settings(), transport=transport)
    result = provider.generate(LLMRequest(prompt="  Hola ROBY  "))
    assert result.text == "Hola Carlos"
    assert result.provider == "ollama-local"
    assert result.model == "llama3.2"
    assert result.accepted
    call = transport.calls[0]
    assert call["url"].endswith("/chat/completions")
    assert call["payload"]["messages"][-1] == {
        "role": "user",
        "content": "Hola ROBY",
    }
    assert call["timeout"] == 10


def test_request_overrides_model_and_generation_settings():
    transport = FakeTransport([completion(model="qwen")])
    provider = LocalProviderRuntimeAdapter(settings(), transport=transport)
    result = provider.generate(
        LLMRequest(prompt="Hola", model="qwen", max_tokens=42, temperature=0.3)
    )
    payload = transport.calls[0]["payload"]
    assert payload["model"] == "qwen"
    assert payload["max_tokens"] == 42
    assert payload["temperature"] == 0.3
    assert result.model == "qwen"


def test_settings_supply_defaults_when_request_omits_them():
    transport = FakeTransport([completion()])
    configured = settings(max_tokens=128, temperature=0.7)
    LocalProviderRuntimeAdapter(configured, transport=transport).generate(
        LLMRequest(prompt="Hola")
    )
    payload = transport.calls[0]["payload"]
    assert payload["max_tokens"] == 128
    assert payload["temperature"] == 0.7


def test_api_key_is_only_sent_as_bearer_header():
    transport = FakeTransport([completion()])
    provider = LocalProviderRuntimeAdapter(
        settings(api_key="secret"), transport=transport
    )
    provider.generate(LLMRequest(prompt="Hola"))
    call = transport.calls[0]
    assert call["headers"]["Authorization"] == "Bearer secret"
    assert "secret" not in str(call["payload"])


def test_transport_error_becomes_typed_llm_failure():
    provider = LocalProviderRuntimeAdapter(
        settings(), transport=FakeTransport(error="timeout")
    )
    result = provider.generate(LLMRequest(prompt="Hola"))
    assert not result.accepted
    assert result.error == "timeout"
    assert result.text == ""


def test_invalid_provider_payload_is_contained():
    provider = LocalProviderRuntimeAdapter(
        settings(), transport=FakeTransport([TransportResponse(200, {})])
    )
    result = provider.generate(LLMRequest(prompt="Hola"))
    assert not result.accepted
    assert result.error == "invalid_response"


def test_missing_model_is_rejected_without_transport_call():
    transport = FakeTransport()
    provider = LocalProviderRuntimeAdapter(settings(model=""), transport=transport)
    result = provider.generate(LLMRequest(prompt="Hola"))
    assert result.error == "missing_model"
    assert not transport.calls


def test_cancellation_before_inference_prevents_transport_call():
    transport = FakeTransport()
    provider = LocalProviderRuntimeAdapter(settings(), transport=transport)
    provider.cancel()
    result = provider.generate(LLMRequest(prompt="Hola"))
    assert result.error == "cancelled"
    assert not transport.calls


def test_cancellation_can_be_reset():
    transport = FakeTransport([completion()])
    provider = LocalProviderRuntimeAdapter(settings(), transport=transport)
    provider.cancel()
    provider.reset_cancellation()
    assert provider.generate(LLMRequest(prompt="Hola")).accepted


def test_environment_factory_builds_configured_adapter(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_NAME", "lm-studio")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENDPOINT", "http://localhost:1234/v1")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "local-model")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_TIMEOUT_SECONDS", "9")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_TEMPERATURE", "0.25")
    provider = build_local_provider_from_environment()
    assert provider.name == "lm-studio"
    assert provider.settings.model == "local-model"
    assert provider.settings.timeout_seconds == 9
    assert provider.settings.temperature == 0.25


def test_environment_factory_rejects_invalid_number(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_TIMEOUT_SECONDS", "many")
    with pytest.raises(ValueError, match="numeric"):
        build_local_provider_from_environment()
