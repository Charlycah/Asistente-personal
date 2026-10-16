from datetime import datetime, timezone

from app.presence_runtime import OfficialPresenceRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.presence import PresenceMode


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m252",
        text=text,
    )


def test_presence_status_starts_without_inferred_activity():
    result = OfficialPresenceRuntimeGateway().intercept(
        _request("¿Cuál es el estado de tu presencia?"),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert result.rationale == "official_presence_status_completed"
    assert "sin señales registradas" in result.response_text
    assert "no infiere" in result.response_text


def test_explicit_interaction_updates_presence_state():
    gateway = OfficialPresenceRuntimeGateway()
    now = datetime.now(timezone.utc)
    result = gateway.intercept(_request("Registrá mi presencia"), now=now)
    assert result is not None
    assert gateway.snapshot is not None
    assert gateway.snapshot.last_user_seen_at == now
    assert gateway.snapshot.normalized_mode is PresenceMode.RECOVERING
    assert "Autonomía: deshabilitada" in result.response_text


def test_presence_reset_returns_to_dormant():
    gateway = OfficialPresenceRuntimeGateway()
    now = datetime.now(timezone.utc)
    gateway.intercept(_request("Registrá mi presencia"), now=now)
    result = gateway.intercept(_request("Reiniciá la presencia"), now=now)
    assert result is not None
    assert gateway.snapshot is not None
    assert gateway.snapshot.normalized_mode is PresenceMode.DORMANT
    assert gateway.snapshot.continuity_score == 0.0


def test_presence_runtime_is_registered_at_end(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    registry = build_runtime_root().dependencies.official_capability_registry
    capability_names = registry.capability_names
    assert capability_names.count("presence.continuity") == 1


def test_presence_is_available_through_official_registry(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    registry = build_runtime_root().dependencies.official_capability_registry
    result = registry.intercept(
        _request("Registrá mi presencia"),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert result.rationale == "official_presence_observation_completed"
