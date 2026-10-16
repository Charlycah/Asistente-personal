from dataclasses import FrozenInstanceError, replace

import pytest

from core.external_retrieval_execution import (
    EXTERNAL_SOURCES,
    ExternalRetrievalAction,
    ExternalRetrievalClientRequest,
    ExternalRetrievalClientResult,
    ExternalRetrievalExecutionAdapter,
    ExternalRetrievalExecutionConfig,
    ExternalRetrievalExecutionRequest,
    ExternalRetrievalStatus,
    InMemoryExternalRetrievalExecutionRepository,
)
from core.knowledge_retrieval_execution import (
    KnowledgeExecutionStatus,
    KnowledgeRetrievalExecutionConfig,
    KnowledgeRetrievalExecutionGateway,
    KnowledgeRetrievalExecutionRequest,
    KnowledgeStepExecutionStatus,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalStep,
)
from core.knowledge_source_policy import KnowledgeSourceKind
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m169_knowledge_source_policy import decide, need


class RecordingClient:
    def __init__(self, *, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def retrieve(self, request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.result or ExternalRetrievalClientResult(
            source=request.source,
            query=request.query,
            content="External knowledge",
            references=("https://example.com/source",),
        )


class InvalidClient:
    def retrieve(self, request):
        return {"content": "invalid"}


def step(source=KnowledgeSourceKind.WEB, query="ROBY architecture"):
    return KnowledgeRetrievalStep(source=source, priority=1, query=query)


def request(*, retrieval_step=None, **changes):
    values = {
        "owner": "Carlos",
        "step": retrieval_step or step(),
    }
    values.update(changes)
    return ExternalRetrievalExecutionRequest(**values)


def execute(*, client=None, config=None, execution_request=None, source=None):
    source = source or (
        execution_request.step.source if execution_request else KnowledgeSourceKind.WEB
    )
    client = client or RecordingClient()
    adapter = ExternalRetrievalExecutionAdapter({source: client}, config=config)
    result = adapter.execute(
        execution_request or request(retrieval_step=step(source)),
        now=NOW,
    )
    return result, client, adapter


def external_plan(source=KnowledgeSourceKind.WEB):
    decision = decide(
        source_need=need(
            "Noticias actuales",
            current_information_required=True,
            preferred_sources=(source,),
        )
    )
    return KnowledgeRetrievalOrchestrator().orchestrate(
        KnowledgeRetrievalRequest(owner="Carlos", source_decision=decision),
        now=NOW,
    )


def test_executes_web_retrieval_through_injected_client():
    result, client, _ = execute()
    assert result.status is ExternalRetrievalStatus.COMPLETED
    assert result.action is ExternalRetrievalAction.EXECUTE_EXTERNAL_RETRIEVAL
    assert len(client.calls) == 1


@pytest.mark.parametrize("source", tuple(EXTERNAL_SOURCES))
def test_supports_every_external_source(source):
    result, _, _ = execute(source=source)
    assert result.status is ExternalRetrievalStatus.COMPLETED
    assert result.client_result.source is source


def test_preserves_exact_m170_step_lineage():
    retrieval_step = step()
    result, _, _ = execute(execution_request=request(retrieval_step=retrieval_step))
    assert result.request.step is retrieval_step


def test_builds_governed_client_request():
    _, client, _ = execute()
    call = client.calls[0]
    assert isinstance(call, ExternalRetrievalClientRequest)
    assert call.source is KnowledgeSourceKind.WEB
    assert call.query == "ROBY architecture"
    assert call.maximum_content_characters == 100_000
    assert call.maximum_references == 32


def test_not_requested_is_not_applicable_without_network():
    result, client, _ = execute(execution_request=request(execution_requested=False))
    assert result.status is ExternalRetrievalStatus.NOT_APPLICABLE
    assert not result.network_access_performed
    assert client.calls == []


def test_disabled_execution_is_withheld_without_network():
    result, client, _ = execute(
        config=ExternalRetrievalExecutionConfig(execution_enabled=False)
    )
    assert result.status is ExternalRetrievalStatus.WITHHELD
    assert client.calls == []


def test_internal_step_is_not_applicable():
    internal = step(KnowledgeSourceKind.INTERNAL)
    adapter = ExternalRetrievalExecutionAdapter({})
    result = adapter.execute(request(retrieval_step=internal), now=NOW)
    assert result.status is ExternalRetrievalStatus.NOT_APPLICABLE
    assert not result.network_access_performed


def test_local_document_step_is_not_applicable():
    local = step(KnowledgeSourceKind.LOCAL_DOCUMENTS)
    adapter = ExternalRetrievalExecutionAdapter({})
    result = adapter.execute(request(retrieval_step=local), now=NOW)
    assert result.status is ExternalRetrievalStatus.NOT_APPLICABLE


def test_disallowed_external_source_is_withheld():
    config = ExternalRetrievalExecutionConfig(
        allowed_sources=(KnowledgeSourceKind.WEB,)
    )
    result, client, _ = execute(
        source=KnowledgeSourceKind.NEWS,
        config=config,
    )
    assert result.status is ExternalRetrievalStatus.WITHHELD
    assert client.calls == []


def test_missing_client_is_withheld():
    adapter = ExternalRetrievalExecutionAdapter({})
    result = adapter.execute(request(), now=NOW)
    assert result.status is ExternalRetrievalStatus.WITHHELD
    assert not result.network_access_performed


def test_query_limit_withholds_before_network():
    config = ExternalRetrievalExecutionConfig(maximum_query_characters=4)
    result, client, _ = execute(
        config=config,
        execution_request=request(retrieval_step=step(query="12345")),
    )
    assert result.status is ExternalRetrievalStatus.WITHHELD
    assert client.calls == []


def test_client_exception_is_contained():
    result, client, _ = execute(client=RecordingClient(error=TimeoutError("slow")))
    assert result.status is ExternalRetrievalStatus.FAILED
    assert result.action is ExternalRetrievalAction.REPORT_FAILURE
    assert result.network_access_performed
    assert result.rationale == ("External retrieval client failed: TimeoutError.",)
    assert len(client.calls) == 1


def test_invalid_client_result_type_is_rejected():
    result, _, _ = execute(client=InvalidClient())
    assert result.status is ExternalRetrievalStatus.REJECTED
    assert result.client_result is None


def test_source_mismatch_is_rejected():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.NEWS,
            query="ROBY architecture",
            content="wrong source",
            references=("https://example.com",),
        )
    )
    result, _, _ = execute(client=client)
    assert result.status is ExternalRetrievalStatus.REJECTED


def test_query_mismatch_is_rejected():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="different",
            content="wrong query",
            references=("https://example.com",),
        )
    )
    result, _, _ = execute(client=client)
    assert result.status is ExternalRetrievalStatus.REJECTED


def test_content_limit_rejects_after_network():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="ROBY architecture",
            content="12345",
            references=("https://example.com",),
        )
    )
    config = ExternalRetrievalExecutionConfig(maximum_content_characters=4)
    result, _, _ = execute(client=client, config=config)
    assert result.status is ExternalRetrievalStatus.REJECTED
    assert result.network_access_performed


def test_reference_limit_rejects_after_network():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="ROBY architecture",
            content="ok",
            references=("https://a.example", "https://b.example"),
        )
    )
    config = ExternalRetrievalExecutionConfig(maximum_references=1)
    result, _, _ = execute(client=client, config=config)
    assert result.status is ExternalRetrievalStatus.REJECTED


def test_http_reference_is_rejected_by_default():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="ROBY architecture",
            content="ok",
            references=("http://example.com",),
        )
    )
    result, _, _ = execute(client=client)
    assert result.status is ExternalRetrievalStatus.REJECTED


def test_relative_reference_is_rejected_by_default():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="ROBY architecture",
            content="ok",
            references=("/docs/source",),
        )
    )
    result, _, _ = execute(client=client)
    assert result.status is ExternalRetrievalStatus.REJECTED


def test_https_requirement_can_be_relaxed():
    client = RecordingClient(
        result=ExternalRetrievalClientResult(
            source=KnowledgeSourceKind.WEB,
            query="ROBY architecture",
            content="ok",
            references=("http://example.com",),
        )
    )
    config = ExternalRetrievalExecutionConfig(require_https_references=False)
    result, _, _ = execute(client=client, config=config)
    assert result.status is ExternalRetrievalStatus.COMPLETED


def test_retrieve_port_returns_m171_artifact():
    adapter = ExternalRetrievalExecutionAdapter(
        {KnowledgeSourceKind.WEB: RecordingClient()}
    )
    artifact = adapter.retrieve(step())
    assert artifact.source is KnowledgeSourceKind.WEB
    assert artifact.query == "ROBY architecture"
    assert artifact.content == "External knowledge"


def test_retrieve_port_raises_for_governed_failure():
    adapter = ExternalRetrievalExecutionAdapter({})
    with pytest.raises(RuntimeError):
        adapter.retrieve(step())


def test_integrates_with_m171_gateway_when_network_is_allowed():
    plan = external_plan()
    adapter = ExternalRetrievalExecutionAdapter(
        {KnowledgeSourceKind.WEB: RecordingClient()}
    )
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.WEB: adapter},
        config=KnowledgeRetrievalExecutionConfig(allow_network=True),
    )
    result = gateway.execute(
        KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=plan),
        now=NOW,
    )
    assert result.status is KnowledgeExecutionStatus.COMPLETED
    assert result.steps[0].status is KnowledgeStepExecutionStatus.SUCCEEDED
    assert result.network_access_performed


def test_m171_still_blocks_adapter_when_network_is_not_allowed():
    plan = external_plan()
    client = RecordingClient()
    adapter = ExternalRetrievalExecutionAdapter({KnowledgeSourceKind.WEB: client})
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.WEB: adapter},
    )
    result = gateway.execute(
        KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=plan),
        now=NOW,
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD
    assert client.calls == []


def test_no_inference_provider_call_or_platform_mutation():
    result, _, _ = execute()
    assert not result.provider_call_performed
    assert not result.platform_mutation_performed


def test_repository_stores_and_reads_result():
    repository = InMemoryExternalRetrievalExecutionRepository()
    adapter = ExternalRetrievalExecutionAdapter(
        {KnowledgeSourceKind.WEB: RecordingClient()},
        repository=repository,
    )
    result = adapter.execute(request(), now=NOW)
    assert repository.get(result.execution_id) is result
    assert repository.list_all() == (result,)
    assert adapter.last_execution is result


def test_repository_rejects_duplicate_result():
    repository = InMemoryExternalRetrievalExecutionRepository()
    result, _, _ = execute()
    repository.add(result)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_execution_result_is_immutable():
    result, _, _ = execute()
    with pytest.raises(FrozenInstanceError):
        result.status = ExternalRetrievalStatus.FAILED


def test_execution_id_is_deterministic_and_protected():
    result, _, _ = execute()
    clone = replace(result, execution_id="")
    assert clone.execution_id == result.execution_id
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, execution_id="wrong")


def test_naive_timestamp_is_rejected():
    from datetime import datetime

    adapter = ExternalRetrievalExecutionAdapter(
        {KnowledgeSourceKind.WEB: RecordingClient()}
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        adapter.execute(request(), now=datetime(2026, 1, 1))


def test_blank_gateway_owner_is_rejected():
    with pytest.raises(ValueError, match="must not be blank"):
        ExternalRetrievalExecutionAdapter({}, gateway_owner=" ")


def test_internal_client_registration_is_rejected():
    with pytest.raises(ValueError, match="external sources"):
        ExternalRetrievalExecutionAdapter(
            {KnowledgeSourceKind.INTERNAL: RecordingClient()}
        )


def test_duplicate_allowed_sources_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        ExternalRetrievalExecutionConfig(
            allowed_sources=(KnowledgeSourceKind.WEB, KnowledgeSourceKind.WEB)
        )
