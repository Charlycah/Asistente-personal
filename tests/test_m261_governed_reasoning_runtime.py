from datetime import datetime, timezone

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.governed_reasoning import GovernedReasoningStatus

NOW = datetime(2026, 7, 15, tzinfo=timezone.utc)


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m261", text=text
    )


def test_default_runtime_abstains_without_registered_governed_knowledge():
    runtime = OfficialGovernedReasoningRuntimeGateway()
    result = runtime.evaluate_text(owner="Carlos", text="estado de tarea", now=NOW)
    assert result.status is GovernedReasoningStatus.ABSTAINED
    assert runtime.snapshot.evaluations == 1
    assert runtime.snapshot.last_owner == "Carlos"


def test_runtime_preserves_traceable_decision_and_explanation():
    runtime = OfficialGovernedReasoningRuntimeGateway()
    result = runtime.evaluate_text(owner="Carlos", text="estado de tarea", now=NOW)
    assert result.decision.query_id == result.context.query.query_id
    assert result.explanation.decision_id == result.decision.decision_id


def test_runtime_audit_is_explicit_and_non_operational():
    runtime = OfficialGovernedReasoningRuntimeGateway()
    result = runtime.intercept(
        request("Auditá runtime de razonamiento gobernado"), now=NOW
    )
    assert result is not None
    assert "Abstención: obligatoria" in result.response_text
    assert "Acciones operacionales: no autorizadas" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    runtime = OfficialGovernedReasoningRuntimeGateway()
    assert runtime.intercept(request("Hola ROBY"), now=NOW) is None


def test_runtime_root_registers_same_official_reasoning_gateway(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "reasoning.governed_runtime"
    )
    assert registration.interceptor is root.dependencies.governed_reasoning_runtime
