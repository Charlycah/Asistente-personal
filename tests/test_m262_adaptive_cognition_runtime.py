from datetime import datetime, timezone

from app.adaptive_cognition_runtime import OfficialAdaptiveCognitionRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.adaptive_cognition import AdaptiveCognitionStage, AdaptiveCognitionStageStatus
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, tzinfo=timezone.utc)


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m262", text=text
    )


def test_default_runtime_runs_safe_adaptive_cycle_over_governed_reasoning():
    runtime = OfficialAdaptiveCognitionRuntimeGateway()
    cycle = runtime.evaluate_text(owner="Carlos", text="estado de tarea", now=NOW)
    statuses = {item.stage: item.status for item in cycle.stages}
    assert statuses[AdaptiveCognitionStage.EPISODIC_MEMORY] is (
        AdaptiveCognitionStageStatus.COMPLETED
    )
    assert statuses[AdaptiveCognitionStage.META_REASONING] in {
        AdaptiveCognitionStageStatus.COMPLETED,
        AdaptiveCognitionStageStatus.REVIEW_REQUIRED,
    }
    assert runtime.snapshot.cycles == 1
    assert runtime.snapshot.last_owner == "Carlos"


def test_runtime_preserves_advisory_non_automatic_stages():
    runtime = OfficialAdaptiveCognitionRuntimeGateway()
    cycle = runtime.evaluate_text(owner="Carlos", text="estado de tarea", now=NOW)
    statuses = {item.stage: item.status for item in cycle.stages}
    assert statuses[AdaptiveCognitionStage.KNOWLEDGE_EVOLUTION] is (
        AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )
    assert statuses[AdaptiveCognitionStage.EXECUTIVE_PLANNING] is (
        AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )
    assert statuses[AdaptiveCognitionStage.EXECUTIVE_COORDINATION] is (
        AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )


def test_runtime_audit_is_explicit_and_non_executive():
    runtime = OfficialAdaptiveCognitionRuntimeGateway()
    result = runtime.intercept(
        request("Auditá runtime de cognición adaptativa"), now=NOW
    )
    assert result is not None
    assert "Evolución de conocimiento: no automática" in result.response_text
    assert "Acciones operacionales: no autorizadas" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    runtime = OfficialAdaptiveCognitionRuntimeGateway()
    assert runtime.intercept(request("Hola ROBY"), now=NOW) is None


def test_runtime_root_registers_same_official_adaptive_gateway(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "cognition.adaptive_runtime"
    )
    assert registration.interceptor is root.dependencies.adaptive_cognition_runtime
    assert (
        root.dependencies.adaptive_cognition_runtime.reasoning_runtime
        is root.dependencies.governed_reasoning_runtime
    )
