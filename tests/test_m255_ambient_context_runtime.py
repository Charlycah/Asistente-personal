from datetime import datetime, timezone

from app.ambient_context_runtime import OfficialAmbientContextRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m255", text=text
    )


def test_explicit_ambient_context_is_governed_without_automation():
    gateway = OfficialAmbientContextRuntimeGateway()
    result = gateway.intercept(
        request("Registrá contexto ambiental: estoy trabajando en el escritorio"),
        now=NOW,
    )
    assert result is not None
    assert "Automatización: deshabilitada" in result.response_text
    assert gateway.snapshot is not None
    assert gateway.snapshot.status == "ready"
    assert not gateway.snapshot.automation_allowed


def test_unrelated_conversation_is_not_intercepted():
    gateway = OfficialAmbientContextRuntimeGateway()
    assert gateway.intercept(request("Hola ROBY"), now=NOW) is None


def test_status_does_not_activate_observation():
    gateway = OfficialAmbientContextRuntimeGateway()
    result = gateway.intercept(request("Estado del contexto ambiental"), now=NOW)
    assert result is not None
    assert "No usa sensores" in result.response_text
    assert gateway.snapshot is None


def test_empty_observation_requires_text():
    gateway = OfficialAmbientContextRuntimeGateway()
    result = gateway.intercept(request("Registrá contexto ambiental:"), now=NOW)
    assert result is not None
    assert "después de los dos puntos" in result.response_text


def test_m255_is_registered_after_m254(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    names = root.dependencies.official_capability_registry.capability_names
    assert names.index("voice.style_runtime") < names.index("context.ambient_runtime")
