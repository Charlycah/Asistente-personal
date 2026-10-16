from datetime import datetime, timezone

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.external_retrieval_execution import (
    ExternalRetrievalClientResult,
    ExternalRetrievalExecutionRequest,
    ExternalRetrievalStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind

NOW = datetime(2026, 7, 15, tzinfo=timezone.utc)


class Client:
    def retrieve(self, request):
        return ExternalRetrievalClientResult(
            source=request.source,
            query=request.query,
            content="Contenido externo verificado.",
            references=("https://example.com/source",),
        )


def step(source=KnowledgeSourceKind.WEB):
    return KnowledgeRetrievalStep(source=source, priority=1, query="ROBY M260")


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m260", text=text
    )


def test_runtime_reuses_governed_external_execution_adapter():
    runtime = OfficialExternalRetrievalRuntimeGateway(
        {KnowledgeSourceKind.WEB: Client()}
    )
    result = runtime.execute(
        ExternalRetrievalExecutionRequest("Carlos", step()), now=NOW
    )
    assert result.status is ExternalRetrievalStatus.COMPLETED
    assert result.network_access_performed is True
    assert result.provider_call_performed is False
    assert runtime.snapshot.evaluations == 1


def test_runtime_withholds_when_no_explicit_client_is_registered():
    runtime = OfficialExternalRetrievalRuntimeGateway()
    result = runtime.execute(
        ExternalRetrievalExecutionRequest("Carlos", step()), now=NOW
    )
    assert result.status is ExternalRetrievalStatus.WITHHELD
    assert result.network_access_performed is False


def test_runtime_audit_is_explicit_and_non_operational():
    runtime = OfficialExternalRetrievalRuntimeGateway()
    result = runtime.intercept(
        request("Auditá runtime de recuperación externa"), now=NOW
    )
    assert result is not None
    assert "Acceso de red implícito: no ejecutado" in result.response_text
    assert "Proveedores de inferencia: no invocados" in result.response_text


def test_unrelated_conversation_is_not_intercepted():
    runtime = OfficialExternalRetrievalRuntimeGateway()
    assert runtime.intercept(request("Hola ROBY"), now=NOW) is None


def test_runtime_root_registers_same_official_external_gateway(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "retrieval.external_runtime"
    )
    assert registration.interceptor is root.dependencies.external_retrieval_runtime
