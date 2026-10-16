from datetime import datetime, timezone

from app.conversation_intelligence_runtime import (
    OfficialConversationIntelligenceRuntimeGateway,
)
from app.runtime_root_factory import build_runtime_root
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalAction,
    AdaptiveConversationOperationalState,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, tzinfo=timezone.utc)


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m263", text=text
    )


def test_default_runtime_consolidates_full_conversation_intelligence_chain():
    runtime = OfficialConversationIntelligenceRuntimeGateway()
    result = runtime.evaluate_text(
        owner="Carlos",
        session_id="m263",
        text="Implementa el runtime con pruebas",
        now=NOW,
    )
    assert result.operational.state is AdaptiveConversationOperationalState.READY
    assert result.operational.action is AdaptiveConversationOperationalAction.PROCEED
    assert len(result.operational.source_reference_ids) == 4
    assert runtime.snapshot.assessments == 1
    assert runtime.snapshot.last_turn_count == 1


def test_runtime_preserves_session_continuity_and_detects_repair():
    runtime = OfficialConversationIntelligenceRuntimeGateway()
    runtime.evaluate_text(
        owner="Carlos", session_id="m263", text="Revisa la arquitectura", now=NOW
    )
    result = runtime.evaluate_text(
        owner="Carlos", session_id="m263", text="No, corrige solo los tests", now=NOW
    )
    assert result.adaptive.state.turn_count == 2
    assert result.operational.state is (
        AdaptiveConversationOperationalState.REPAIR_REQUIRED
    )
    assert result.operational.action is (
        AdaptiveConversationOperationalAction.APPLY_REPAIR
    )


def test_runtime_audit_is_explicit_and_non_executive():
    runtime = OfficialConversationIntelligenceRuntimeGateway()
    result = runtime.intercept(
        request("Auditá runtime de inteligencia conversacional"), now=NOW
    )
    assert result is not None
    assert "Grounding: exige alcance compartido" in result.response_text
    assert "no generativa ni ejecutiva" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    runtime = OfficialConversationIntelligenceRuntimeGateway()
    assert runtime.intercept(request("Hola ROBY"), now=NOW) is None


def test_runtime_root_registers_same_official_conversation_gateway(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "conversation.intelligence_runtime"
    )
    assert registration.interceptor is (
        root.dependencies.conversation_intelligence_runtime
    )
