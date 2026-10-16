from datetime import datetime, timezone

from app.conversation_entry_runtime import OfficialConversationEntryRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m256", text=text
    )


def test_explicit_question_is_classified_without_execution():
    gateway = OfficialConversationEntryRuntimeGateway()
    result = gateway.intercept(
        request("Clasificá entrada conversacional: Como estás?"), now=NOW
    )
    assert result is not None
    assert "Tipo: question" in result.response_text
    assert "route_to_reasoning" in result.response_text
    assert "no autorizadas" in result.response_text


def test_request_addressed_to_roby_is_detected():
    gateway = OfficialConversationEntryRuntimeGateway()
    result = gateway.intercept(
        request("Evaluá entrada conversacional: ROBY, buscame el informe"),
        now=NOW,
    )
    assert result is not None
    assert "Tipo: request" in result.response_text
    assert "Dirigido a Roby: sí" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    gateway = OfficialConversationEntryRuntimeGateway()
    assert gateway.intercept(request("Hola ROBY"), now=NOW) is None


def test_status_does_not_classify_input():
    gateway = OfficialConversationEntryRuntimeGateway()
    result = gateway.intercept(
        request("Estado del clasificador conversacional"), now=NOW
    )
    assert result is not None
    assert "sin evaluaciones previas" in result.response_text
    assert gateway.snapshot is None


def test_m256_is_registered_after_m255(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    names = root.dependencies.official_capability_registry.capability_names
    assert names.index("context.ambient_runtime") < names.index(
        "conversation.entry_runtime"
    )
