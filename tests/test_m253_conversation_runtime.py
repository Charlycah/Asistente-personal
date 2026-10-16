from __future__ import annotations

from datetime import datetime, timezone

from app.conversation_runtime import OfficialConversationRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeContributor,
    LivingConversationRuntimeProjection,
)
from core.llm_provider import LLMRequest

NOW = datetime(2026, 7, 15, 21, 0, tzinfo=timezone.utc)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m253",
        text=text,
    )


def test_conversation_runtime_requires_explicit_activation():
    gateway = OfficialConversationRuntimeGateway()
    assert (
        gateway.resolve(
            owner="Carlos",
            session_id="m253",
            text="Hola, ¿cómo estás?",
            now=NOW,
        )
        is None
    )


def test_explicit_activation_reuses_official_living_conversation_contributor():
    gateway = OfficialConversationRuntimeGateway()
    projection = gateway.resolve(
        owner="Carlos",
        session_id="m253",
        text="Adaptá la conversación a este tema",
        now=NOW,
    )
    assert isinstance(projection, LivingConversationRuntimeProjection)
    assert projection.source_kind == "official_conversation_runtime"
    result = LivingConversationRuntimeContributor(gateway).contribute(
        owner="Carlos",
        session_id="m253",
        text="Adaptá la conversación a este tema",
        request=LLMRequest(prompt="Adaptá la conversación a este tema"),
        now=NOW,
    )
    assert result.status.value == "applied"
    assert "Cadencia conversacional: steady." in result.prompt_lines
    assert any("preservar siempre el turno" in line for line in result.prompt_lines)


def test_status_is_operational_and_does_not_trigger_adaptation():
    gateway = OfficialConversationRuntimeGateway()
    result = gateway.intercept(
        _request("¿Cuál es el estado del runtime conversacional?"),
        now=NOW,
    )
    assert result is not None
    assert result.rationale == "official_conversation_runtime_status_completed"
    assert "únicamente por solicitud explícita" in result.response_text


def test_runtime_root_connects_same_gateway_to_registry_and_cognitive_path(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    assert "conversation.living_runtime" in registry.capability_names
    assert root.dependencies.living_conversation_source is not None
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "conversation.living_runtime"
    )
    assert registration.interceptor is root.dependencies.living_conversation_source


def test_explicit_conversation_request_is_enriched_by_official_runtime(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    composition = root.compose()
    prepared = composition.preparation.prepare(
        _request("Activá conversación viva para explorar esta idea")
    )
    assert "Cadencia conversacional: steady." in prepared.inference_request.prompt
    assert (
        "Próximo movimiento conversacional: explore."
        in prepared.inference_request.prompt
    )
