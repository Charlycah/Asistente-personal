from dataclasses import FrozenInstanceError, replace

import pytest

from core.knowledge_retrieval_execution import (
    InMemoryKnowledgeRetrievalExecutionRepository,
    KnowledgeExecutionStatus,
    KnowledgeRetrievalArtifact,
    KnowledgeRetrievalExecutionConfig,
    KnowledgeRetrievalExecutionGateway,
    KnowledgeRetrievalExecutionRequest,
    KnowledgeStepExecutionStatus,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
)
from core.knowledge_source_policy import (
    KnowledgeSourceKind,
    KnowledgeSourcePolicyConfig,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m169_knowledge_source_policy import decide, need


class FakeRetriever:
    def __init__(self, *, content="knowledge", error=None, source=None, query=None):
        self.content = content
        self.error = error
        self.source = source
        self.query = query
        self.calls = []

    def retrieve(self, step):
        self.calls.append(step)
        if self.error is not None:
            raise self.error
        return KnowledgeRetrievalArtifact(
            source=self.source or step.source,
            query=self.query or step.query,
            content=self.content,
            references=(f"ref:{step.source.value}",),
        )


def plan(*, source_decision=None, config=None, orchestration_requested=True):
    decision = source_decision or decide()
    return KnowledgeRetrievalOrchestrator(config=config).orchestrate(
        KnowledgeRetrievalRequest(
            owner="Carlos",
            source_decision=decision,
            orchestration_requested=orchestration_requested,
        ),
        now=NOW,
    )


def request(*, retrieval_plan=None, **changes):
    values = {"owner": "Carlos", "plan": retrieval_plan or plan()}
    values.update(changes)
    return KnowledgeRetrievalExecutionRequest(**values)


def execute(*, retrieval_plan=None, retrievers=None, config=None, **changes):
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers=retrievers,
        config=config,
    )
    return gateway.execute(
        request(retrieval_plan=retrieval_plan, **changes),
        now=NOW,
    )


def test_executes_internal_retrieval_through_injected_port():
    retriever = FakeRetriever(content="ROBY internal knowledge")
    result = execute(retrievers={KnowledgeSourceKind.INTERNAL: retriever})
    assert result.status is KnowledgeExecutionStatus.COMPLETED
    assert result.steps[0].status is KnowledgeStepExecutionStatus.SUCCEEDED
    assert result.steps[0].artifact.content == "ROBY internal knowledge"
    assert retriever.calls == [result.steps[0].step]


def test_preserves_exact_m170_plan_lineage():
    retrieval_plan = plan()
    result = execute(
        retrieval_plan=retrieval_plan,
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()},
    )
    assert result.request.plan is retrieval_plan


def test_local_documents_are_allowed_by_default():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need(
                "Que dice mi manual?",
                internal_confidence=0.2,
                local_documents_available=True,
                preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
            )
        )
    )
    result = execute(
        retrieval_plan=retrieval_plan,
        retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: FakeRetriever()},
    )
    assert result.status is KnowledgeExecutionStatus.COMPLETED
    assert result.retrieval_performed
    assert not result.network_access_performed


def test_network_sources_are_withheld_by_default():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need("Noticias de hoy", current_information_required=True)
        )
    )
    result = execute(
        retrieval_plan=retrieval_plan,
        retrievers={
            KnowledgeSourceKind.NEWS: FakeRetriever(),
            KnowledgeSourceKind.WEB: FakeRetriever(),
        },
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD
    assert all(
        item.status is KnowledgeStepExecutionStatus.WITHHELD
        for item in result.steps[:1]
    )
    assert result.steps[1].status is KnowledgeStepExecutionStatus.SKIPPED


def test_network_sources_execute_when_explicitly_allowed():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need("Noticias de hoy", current_information_required=True)
        )
    )
    result = execute(
        retrieval_plan=retrieval_plan,
        config=KnowledgeRetrievalExecutionConfig(allow_network=True),
        retrievers={
            KnowledgeSourceKind.NEWS: FakeRetriever(),
            KnowledgeSourceKind.WEB: FakeRetriever(),
        },
    )
    assert result.status is KnowledgeExecutionStatus.COMPLETED
    assert result.network_access_performed


def test_missing_retriever_produces_governed_failure():
    result = execute()
    assert result.status is KnowledgeExecutionStatus.FAILED
    assert result.steps[0].status is KnowledgeStepExecutionStatus.FAILED
    assert result.steps[0].rationale == ("knowledge_retriever_not_registered",)


def test_adapter_exception_is_captured_without_escaping():
    result = execute(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever(error=RuntimeError())}
    )
    assert result.status is KnowledgeExecutionStatus.FAILED
    assert result.steps[0].rationale == ("knowledge_retriever_failed:RuntimeError",)


def test_direct_required_failure_stops_later_sequential_steps():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need(
                "Busca fuentes",
                current_information_required=True,
                preferred_sources=(KnowledgeSourceKind.NEWS, KnowledgeSourceKind.WEB),
            )
        )
    )
    web = FakeRetriever()
    result = execute(
        retrieval_plan=retrieval_plan,
        config=KnowledgeRetrievalExecutionConfig(allow_network=True),
        retrievers={KnowledgeSourceKind.WEB: web},
    )
    assert result.steps[0].status is KnowledgeStepExecutionStatus.FAILED
    assert result.steps[1].status is KnowledgeStepExecutionStatus.SKIPPED
    assert web.calls == []


def test_parallel_verification_attempts_all_steps_after_failure():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need(
                "Verifica esto",
                verification_required=True,
                preferred_sources=(
                    KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
                    KnowledgeSourceKind.WEB,
                ),
            )
        )
    )
    web = FakeRetriever()
    result = execute(
        retrieval_plan=retrieval_plan,
        config=KnowledgeRetrievalExecutionConfig(allow_network=True),
        retrievers={KnowledgeSourceKind.WEB: web},
    )
    assert result.status is KnowledgeExecutionStatus.PARTIAL
    assert result.steps[0].status is KnowledgeStepExecutionStatus.FAILED
    assert result.steps[1].status is KnowledgeStepExecutionStatus.SUCCEEDED
    assert len(web.calls) == 1


def test_execution_can_be_disabled():
    result = execute(
        config=KnowledgeRetrievalExecutionConfig(execution_enabled=False),
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()},
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD
    assert result.steps[0].status is KnowledgeStepExecutionStatus.WITHHELD


def test_internal_retrieval_can_be_disabled_independently():
    result = execute(
        config=KnowledgeRetrievalExecutionConfig(allow_internal=False),
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()},
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD


def test_local_document_retrieval_can_be_disabled_independently():
    retrieval_plan = plan(
        source_decision=decide(
            source_need=need(
                internal_confidence=0.1,
                local_documents_available=True,
                preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
            )
        )
    )
    result = execute(
        retrieval_plan=retrieval_plan,
        config=KnowledgeRetrievalExecutionConfig(allow_local_documents=False),
        retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: FakeRetriever()},
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD


def test_not_requested_is_not_applicable():
    result = execute(execution_requested=False)
    assert result.status is KnowledgeExecutionStatus.NOT_APPLICABLE
    assert all(
        item.status is KnowledgeStepExecutionStatus.SKIPPED for item in result.steps
    )


def test_withheld_plan_remains_withheld_without_adapter_calls():
    retrieval_plan = plan(
        source_decision=decide(
            config=KnowledgeSourcePolicyConfig(allow_external_sources=False),
            source_need=need(current_information_required=True),
        )
    )
    retriever = FakeRetriever()
    result = execute(
        retrieval_plan=retrieval_plan,
        retrievers={KnowledgeSourceKind.WEB: retriever},
    )
    assert result.status is KnowledgeExecutionStatus.WITHHELD
    assert result.steps == ()
    assert retriever.calls == []


def test_artifact_source_mismatch_is_rejected_as_adapter_failure():
    result = execute(
        retrievers={
            KnowledgeSourceKind.INTERNAL: FakeRetriever(source=KnowledgeSourceKind.WEB)
        }
    )
    assert result.status is KnowledgeExecutionStatus.FAILED
    assert result.steps[0].rationale == ("knowledge_retriever_failed:ValueError",)


def test_artifact_query_mismatch_is_rejected_as_adapter_failure():
    result = execute(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever(query="other")}
    )
    assert result.status is KnowledgeExecutionStatus.FAILED


def test_artifact_content_limit_is_enforced():
    result = execute(
        config=KnowledgeRetrievalExecutionConfig(max_content_characters=3),
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever(content="long")},
    )
    assert result.status is KnowledgeExecutionStatus.FAILED


def test_provider_calls_and_platform_mutation_remain_forbidden():
    result = execute(retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()})
    assert not result.provider_call_performed
    assert not result.platform_mutation_performed


def test_repository_stores_execution_and_exposes_last():
    repository = InMemoryKnowledgeRetrievalExecutionRepository()
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()},
        repository=repository,
    )
    result = gateway.execute(request(), now=NOW)
    assert repository.get(result.execution_id) is result
    assert repository.list_all() == (result,)
    assert gateway.last_execution is result


def test_empty_repository_has_no_last_execution():
    assert KnowledgeRetrievalExecutionGateway().last_execution is None


def test_duplicate_execution_is_rejected():
    repository = InMemoryKnowledgeRetrievalExecutionRepository()
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()},
        repository=repository,
    )
    result = gateway.execute(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_execution_is_immutable():
    result = execute(retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()})
    with pytest.raises(FrozenInstanceError):
        result.status = KnowledgeExecutionStatus.FAILED


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_plan_owner():
    with pytest.raises(ValueError, match="match retrieval plan owner"):
        request(owner="Other")


def test_maximum_content_characters_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        KnowledgeRetrievalExecutionConfig(max_content_characters=0)


def test_execution_timestamp_must_be_timezone_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        KnowledgeRetrievalExecutionGateway().execute(
            request(), now=NOW.replace(tzinfo=None)
        )


def test_execution_identity_changes_with_timestamp():
    gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()}
    )
    first = gateway.execute(request(), now=NOW)
    second_gateway = KnowledgeRetrievalExecutionGateway(
        retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()}
    )
    second = second_gateway.execute(request(), now=NOW.replace(microsecond=1))
    assert first.execution_id != second.execution_id


def test_execution_id_is_validated():
    result = execute(retrievers={KnowledgeSourceKind.INTERNAL: FakeRetriever()})
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, execution_id="invalid")
