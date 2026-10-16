from dataclasses import FrozenInstanceError, replace
from datetime import datetime

import pytest

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineConfig,
    GovernedConversationPipelineRequest,
    GovernedConversationPipelineStatus,
    GovernedConversationPreparation,
    GovernedOperationalConversationPipeline,
    InMemoryGovernedConversationPipelineRepository,
)
from core.governed_provider_execution_adapter import GovernedProviderExecutionAdapter
from core.knowledge_retrieval_execution import KnowledgeRetrievalExecutionGateway
from core.knowledge_source_policy import KnowledgeSourceKind
from core.llm_provider import LLMRequest
from core.operational_response_assembly import OperationalResponseStatus
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m171_knowledge_retrieval_execution import FakeRetriever, plan
from tests.test_m173_governed_provider_execution_adapter import (
    RecordingProvider,
    local_route,
)


class PreparationPort:
    def __init__(self, *, route=None, retrieval_plan=None, error=None):
        self.route = route or local_route()
        self.retrieval_plan = retrieval_plan
        self.error = error
        self.calls = []

    def prepare(self, request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return GovernedConversationPreparation(
            owner=request.owner,
            session_id=request.session_id,
            text=request.text,
            provider_route=self.route,
            inference_request=LLMRequest(prompt=request.text),
            retrieval_plan=self.retrieval_plan,
        )


class BadPreparationPort(PreparationPort):
    def prepare(self, request):
        prepared = super().prepare(request)
        return replace(prepared, session_id="other")


def request(**changes):
    values = {"owner": "Carlos", "session_id": "desktop-main", "text": "Explica ROBY"}
    values.update(changes)
    return GovernedConversationPipelineRequest(**values)


def pipeline(*, preparation=None, provider=None, retrieval_executor=None, **changes):
    provider = provider or RecordingProvider()
    preparation = preparation or PreparationPort()
    runtime = GovernedOperationalConversationPipeline(
        preparation_port=preparation,
        provider_executor=GovernedProviderExecutionAdapter((provider,)),
        retrieval_executor=retrieval_executor,
        **changes,
    )
    return runtime, preparation, provider


def test_process_executes_prepared_local_provider_turn():
    runtime, preparation, provider = pipeline()
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.COMPLETED
    assert len(preparation.calls) == 1
    assert len(provider.calls) == 1


def test_execute_implements_m176_operational_pipeline_contract():
    runtime, _, _ = pipeline()
    response = runtime.execute(owner="Carlos", session_id="s1", text="Hola")
    assert response.status is OperationalResponseStatus.COMPLETED


def test_exact_preparation_lineage_is_preserved():
    port = PreparationPort()
    runtime, _, _ = pipeline(preparation=port)
    result = runtime.process(request(), now=NOW)
    assert result.preparation.provider_route is port.route


def test_exact_provider_execution_lineage_reaches_m175():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    assert (
        result.operational_response.request.provider_execution
        is result.provider_execution
    )


def test_provider_text_is_delivered_without_rewriting():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    assert result.operational_response.response_text == "Hola desde el proveedor local."


def test_optional_retrieval_plan_runs_through_m171():
    retrieval_plan = plan()
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever(content="evidence")}
    )
    runtime, _, _ = pipeline(
        preparation=PreparationPort(retrieval_plan=retrieval_plan),
        retrieval_executor=gateway,
    )
    result = runtime.process(request(), now=NOW)
    assert result.retrieval_execution.request.plan is retrieval_plan
    assert result.retrieval_performed


def test_retrieval_evidence_reaches_operational_response():
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever(content="evidence")}
    )
    runtime, _, _ = pipeline(
        preparation=PreparationPort(retrieval_plan=plan()),
        retrieval_executor=gateway,
    )
    result = runtime.process(request(), now=NOW)
    assert result.operational_response.evidence[0].content == "evidence"


def test_retrieval_can_be_disabled_without_losing_provider_response():
    runtime, _, _ = pipeline(
        preparation=PreparationPort(retrieval_plan=plan()),
        config=GovernedConversationPipelineConfig(execute_retrieval=False),
    )
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.COMPLETED
    assert result.retrieval_execution is None


def test_missing_gateway_for_requested_retrieval_fails_safely():
    runtime, _, provider = pipeline(preparation=PreparationPort(retrieval_plan=plan()))
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.FAILED
    assert result.operational_response.status is OperationalResponseStatus.WITHHELD
    assert len(provider.calls) == 1


def test_preparation_exception_fails_without_provider_call():
    runtime, _, provider = pipeline(
        preparation=PreparationPort(error=RuntimeError("planning failed"))
    )
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.FAILED
    assert provider.calls == []


def test_mismatched_preparation_is_rejected_safely():
    runtime, _, provider = pipeline(preparation=BadPreparationPort())
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.FAILED
    assert provider.calls == []


def test_disabled_pipeline_withholds_before_preparation():
    runtime, preparation, provider = pipeline(
        config=GovernedConversationPipelineConfig(execution_enabled=False)
    )
    result = runtime.process(request(), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.WITHHELD
    assert preparation.calls == []
    assert provider.calls == []


def test_input_limit_withholds_before_preparation():
    runtime, preparation, _ = pipeline(
        config=GovernedConversationPipelineConfig(maximum_input_characters=3)
    )
    result = runtime.process(request(text="abcd"), now=NOW)
    assert result.status is GovernedConversationPipelineStatus.WITHHELD
    assert preparation.calls == []


def test_network_flag_is_lineage_only():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    assert (
        result.network_access_performed
        is result.operational_response.network_access_performed
    )
    assert not result.platform_mutation_performed


def test_repository_records_result():
    repository = InMemoryGovernedConversationPipelineRepository()
    runtime, _, _ = pipeline(repository=repository)
    result = runtime.process(request(), now=NOW)
    assert repository.get(result.result_id) is result


def test_repository_is_append_only():
    repository = InMemoryGovernedConversationPipelineRepository()
    runtime, _, _ = pipeline(repository=repository)
    result = runtime.process(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_last_result_exposes_latest_record():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    assert runtime.last_result is result


@pytest.mark.parametrize("field", ["owner", "session_id", "text"])
def test_request_identity_is_required(field):
    with pytest.raises(ValueError):
        request(**{field: " "})


def test_request_is_normalized():
    item = request(owner=" Carlos ", session_id=" s1 ", text=" hello ")
    assert (item.owner, item.session_id, item.text) == ("Carlos", "s1", "hello")


def test_config_rejects_non_positive_limit():
    with pytest.raises(ValueError, match="positive"):
        GovernedConversationPipelineConfig(maximum_input_characters=0)


def test_naive_timestamp_is_rejected():
    runtime, _, _ = pipeline()
    with pytest.raises(ValueError, match="timezone-aware"):
        runtime.process(request(), now=datetime(2026, 1, 1))


def test_result_is_immutable():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = GovernedConversationPipelineStatus.FAILED


def test_result_identity_is_deterministic():
    first, _, _ = pipeline()
    second, _, _ = pipeline()
    assert (
        first.process(request(), now=NOW).result_id
        == second.process(request(), now=NOW).result_id
    )


def test_result_rejects_platform_mutation():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    with pytest.raises(ValueError, match="cannot mutate"):
        replace(result, platform_mutation_performed=True, result_id="")


def test_result_rejects_broken_provider_lineage():
    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    with pytest.raises(ValueError, match="provider call lineage"):
        replace(result, provider_call_performed=False, result_id="")


def test_provider_answer_is_classified_as_general_knowledge():
    from core.governed_operational_conversation_pipeline import (
        ResponseConfidence,
        ResponseOrigin,
    )

    runtime, _, _ = pipeline()
    result = runtime.process(request(), now=NOW)
    assert result.response_origin.origin is ResponseOrigin.GENERAL_KNOWLEDGE
    assert result.response_origin.confidence is ResponseConfidence.MEDIUM
    assert result.response_origin.freshness == "not_guaranteed_current"
    assert result.response_origin.verifiable is False
