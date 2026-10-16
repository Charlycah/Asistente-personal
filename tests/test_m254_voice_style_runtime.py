from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from app.voice_style_runtime import OfficialVoiceStyleRuntimeGateway
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m254", text=text
    )


def test_explicit_voice_style_evaluation_uses_existing_policy():
    gateway = OfficialVoiceStyleRuntimeGateway()
    result = gateway.intercept(
        request("Evaluá el estilo de voz: Hola.   Como estás?"), now=NOW
    )
    assert result is not None
    assert "Hola. Como estas?" in result.response_text
    assert gateway.snapshot is not None
    assert gateway.snapshot.normalized


def test_bureaucratic_language_is_withheld():
    gateway = OfficialVoiceStyleRuntimeGateway()
    result = gateway.intercept(
        request("Evaluá el estilo de voz: Comando aceptado."), now=NOW
    )
    assert result is not None
    assert "retenido" in result.response_text
    assert gateway.snapshot.bureaucratic_phrase_detected


def test_unrelated_conversation_is_not_intercepted():
    gateway = OfficialVoiceStyleRuntimeGateway()
    assert gateway.intercept(request("Hola ROBY"), now=NOW) is None


def test_status_is_available_without_implicit_activation():
    gateway = OfficialVoiceStyleRuntimeGateway()
    result = gateway.intercept(request("Estado del estilo de voz"), now=NOW)
    assert result is not None
    assert "solicitud explícita" in result.response_text


def test_m254_is_registered_after_m253(monkeypatch):
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY", "app.runtime_root_factory:build_runtime_root"
    )
    root = build_runtime_root()
    names = root.dependencies.official_capability_registry.capability_names
    assert names.index("conversation.living_runtime") < names.index(
        "voice.style_runtime"
    )
