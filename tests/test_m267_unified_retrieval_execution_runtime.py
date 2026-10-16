from datetime import datetime, timezone

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.external_retrieval_execution import ExternalRetrievalClientResult
from core.knowledge_retrieval_execution import (
    KnowledgeRetrievalExecutionConfig,
    KnowledgeRetrievalExecutionRequest,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
)
from core.knowledge_source_policy import KnowledgeSourceKind
from tests.test_m169_knowledge_source_policy import decide, need

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class Client:
    def retrieve(self, request):
        return ExternalRetrievalClientResult(
            source=request.source,
            query=request.query,
            content="Resultado validado.",
            references=("https://example.com/source",),
        )


def _plan():
    decision = decide(
        source_need=need(
            "ROBY M267",
            current_information_required=True,
            preferred_sources=(KnowledgeSourceKind.WEB,),
        )
    )
    return KnowledgeRetrievalOrchestrator().orchestrate(
        KnowledgeRetrievalRequest(owner="Carlos", source_decision=decision),
        now=NOW,
    )


def _unified(external):
    return OfficialUnifiedRetrievalExecutionRuntimeGateway(
        external,
        config=KnowledgeRetrievalExecutionConfig(allow_network=True),
    )


def test_external_steps_delegate_to_the_same_m260_runtime():
    external = OfficialExternalRetrievalRuntimeGateway(
        {KnowledgeSourceKind.WEB: Client()}
    )
    unified = _unified(external)
    result = unified.execute(
        KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=_plan()), now=NOW
    )
    assert result.network_access_performed is True
    assert external.snapshot.evaluations == 1
    assert unified.snapshot.evaluations == 1


def test_missing_external_client_is_withheld_by_m260_validation():
    external = OfficialExternalRetrievalRuntimeGateway()
    unified = _unified(external)
    result = unified.execute(
        KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=_plan()), now=NOW
    )
    assert result.network_access_performed is False
    assert external.snapshot.last_status == "withheld"


def test_unified_gateway_keeps_provider_and_platform_boundaries_closed():
    external = OfficialExternalRetrievalRuntimeGateway(
        {KnowledgeSourceKind.WEB: Client()}
    )
    result = _unified(external).execute(
        KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=_plan()), now=NOW
    )
    assert result.provider_call_performed is False
    assert result.platform_mutation_performed is False


def test_runtime_root_registers_unified_retrieval_authority(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    runtime = root.dependencies.unified_retrieval_execution_runtime
    registration = registry.registration_for("retrieval.unified_execution_runtime")
    assert registration is not None
    assert registration.interceptor is runtime


def test_unified_runtime_reuses_exact_m260_instance(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    unified = root.dependencies.unified_retrieval_execution_runtime
    assert unified.external_runtime is root.dependencies.external_retrieval_runtime
