from datetime import datetime, timezone

from app.context_continuity_runtime import OfficialContextContinuityRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def turn(user: str, assistant: str) -> ConversationalContextTurn:
    return ConversationalContextTurn(user_text=user, assistant_text=assistant)


def request(text: str, *, context=()):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m257",
        text=text,
        recent_context=context,
    )


def test_explicit_evaluation_reuses_sanitization_and_curation():
    gateway = OfficialContextContinuityRuntimeGateway()
    result = gateway.intercept(
        request(
            "Evaluá continuidad contextual",
            context=(
                turn("Mi nombre es Carlos.", "Entendido, Carlos."),
                turn("Evaluá continuidad contextual", "Respuesta anterior."),
            ),
        ),
        now=NOW,
    )
    assert result is not None
    assert "Turnos recibidos: 2" in result.response_text
    assert "Turnos seleccionados: 1" in result.response_text
    assert "Proveedores, red y mutaciones: no ejecutados" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    gateway = OfficialContextContinuityRuntimeGateway()
    assert gateway.intercept(request("Hola ROBY"), now=NOW) is None


def test_status_does_not_create_snapshot():
    gateway = OfficialContextContinuityRuntimeGateway()
    result = gateway.intercept(request("Estado de continuidad contextual"), now=NOW)
    assert result is not None
    assert "sin evaluaciones previas" in result.response_text
    assert gateway.snapshot is None


def test_runtime_root_uses_same_gateway_for_registry_and_preparation(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    assert "conversation.context_continuity_runtime" in registry.capability_names
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "conversation.context_continuity_runtime"
    )
    assert registration.interceptor is root.dependencies.context_continuity_runtime


def test_official_preparation_applies_context_and_updates_snapshot(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    prepared = root.compose().preparation.prepare(
        request(
            "¿Cómo me llamo?",
            context=(turn("Mi nombre es Carlos.", "Entendido, Carlos."),),
        ),
        now=NOW,
    )
    assert "Usuario: Mi nombre es Carlos." in prepared.inference_request.prompt
    gateway = root.dependencies.context_continuity_runtime
    assert gateway.snapshot is not None
    assert gateway.snapshot.selected_turns == 1
    assert gateway.snapshot.context_applied
