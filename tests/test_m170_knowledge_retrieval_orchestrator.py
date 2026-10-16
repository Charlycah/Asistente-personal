from dataclasses import FrozenInstanceError, replace

import pytest

from core.knowledge_retrieval_orchestrator import (
    InMemoryKnowledgeRetrievalRepository,
    KnowledgeRetrievalAction,
    KnowledgeRetrievalConfig,
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalStatus,
    RetrievalStrategy,
)
from core.knowledge_source_policy import (
    KnowledgeSourceKind,
    KnowledgeSourcePolicyConfig,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m169_knowledge_source_policy import decide, need

SOURCE_DECISION = decide()


def request(*, source_decision=SOURCE_DECISION, **changes):
    values = {
        "owner": "Carlos",
        "source_decision": source_decision,
    }
    values.update(changes)
    return KnowledgeRetrievalRequest(**values)


def orchestrate(*, config=None, source_decision=SOURCE_DECISION, **changes):
    orchestrator = KnowledgeRetrievalOrchestrator(config=config)
    return orchestrator.orchestrate(
        request(source_decision=source_decision, **changes),
        now=NOW,
    )


def test_internal_source_prepares_direct_internal_plan():
    result = orchestrate()
    assert result.status is KnowledgeRetrievalStatus.INTERNAL_PLANNED
    assert result.action is KnowledgeRetrievalAction.PREPARE_INTERNAL
    assert result.strategy is RetrievalStrategy.DIRECT
    assert result.steps[0].source is KnowledgeSourceKind.INTERNAL


def test_preserves_exact_m169_lineage():
    result = orchestrate()
    assert result.request.source_decision is SOURCE_DECISION


def test_local_documents_prepare_local_plan():
    source = decide(
        source_need=need(
            "Que dice mi manual?",
            internal_confidence=0.2,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        )
    )
    result = orchestrate(source_decision=source)
    assert result.status is KnowledgeRetrievalStatus.LOCAL_PLANNED
    assert result.steps[0].source is KnowledgeSourceKind.LOCAL_DOCUMENTS


def test_external_sources_prepare_sequential_plan():
    source = decide(
        source_need=need(
            "Que novedades hay hoy sobre la NASA?",
            current_information_required=True,
        )
    )
    result = orchestrate(source_decision=source)
    assert result.status is KnowledgeRetrievalStatus.EXTERNAL_PLANNED
    assert result.strategy is RetrievalStrategy.SEQUENTIAL
    assert tuple(item.source for item in result.steps) == (
        KnowledgeSourceKind.NEWS,
        KnowledgeSourceKind.WEB,
    )


def test_single_external_source_uses_direct_strategy():
    source = decide(
        source_need=need(
            "Buscalo en Internet",
            explicit_external_request=True,
            preferred_sources=(KnowledgeSourceKind.WEB,),
        )
    )
    result = orchestrate(source_decision=source)
    assert result.strategy is RetrievalStrategy.DIRECT


def test_verification_uses_parallel_strategy_by_default():
    source = decide(
        source_need=need(
            "Verifica este dato",
            verification_required=True,
            preferred_sources=(
                KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
                KnowledgeSourceKind.WEB,
            ),
        )
    )
    result = orchestrate(source_decision=source)
    assert result.status is KnowledgeRetrievalStatus.VERIFICATION_PLANNED
    assert result.action is KnowledgeRetrievalAction.PREPARE_VERIFICATION
    assert result.strategy is RetrievalStrategy.PARALLEL
    assert result.verification_required


def test_verification_can_be_sequential():
    config = KnowledgeRetrievalConfig(parallel_verification=False)
    source = decide(
        source_need=need(
            "Verifica este dato",
            verification_required=True,
            preferred_sources=(
                KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
                KnowledgeSourceKind.WEB,
            ),
        )
    )
    result = orchestrate(config=config, source_decision=source)
    assert result.strategy is RetrievalStrategy.SEQUENTIAL


def test_max_sources_limits_retrieval_steps():
    config = KnowledgeRetrievalConfig(max_sources=2)
    source = decide(
        source_need=need(
            "Busca fuentes",
            current_information_required=True,
            preferred_sources=(
                KnowledgeSourceKind.NEWS,
                KnowledgeSourceKind.WEB,
                KnowledgeSourceKind.API,
            ),
        )
    )
    result = orchestrate(config=config, source_decision=source)
    assert len(result.steps) == 2


def test_priorities_are_contiguous():
    source = decide(
        source_need=need(
            current_information_required=True,
            preferred_sources=(
                KnowledgeSourceKind.API,
                KnowledgeSourceKind.WEB,
            ),
        )
    )
    result = orchestrate(source_decision=source)
    assert tuple(item.priority for item in result.steps) == (1, 2)


def test_query_is_propagated_to_every_step():
    source = decide(
        source_need=need(
            "Novedades de James Webb",
            current_information_required=True,
        )
    )
    result = orchestrate(source_decision=source)
    assert all(item.query == "Novedades de James Webb" for item in result.steps)


def test_withheld_source_decision_withholds_orchestration():
    source = decide(
        config=KnowledgeSourcePolicyConfig(allow_external_sources=False),
        source_need=need(current_information_required=True),
    )
    result = orchestrate(source_decision=source)
    assert result.status is KnowledgeRetrievalStatus.WITHHELD
    assert result.action is KnowledgeRetrievalAction.WITHHOLD
    assert result.steps == ()


def test_not_requested_is_not_applicable():
    result = orchestrate(orchestration_requested=False)
    assert result.status is KnowledgeRetrievalStatus.NOT_APPLICABLE
    assert result.action is KnowledgeRetrievalAction.NONE


def test_orchestrator_never_authorizes_retrieval_or_execution():
    source = decide(source_need=need(current_information_required=True))
    result = orchestrate(source_decision=source)
    assert not result.retrieval_allowed
    assert not result.network_access_allowed
    assert not result.provider_call_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_plan_and_exposes_last():
    repository = InMemoryKnowledgeRetrievalRepository()
    orchestrator = KnowledgeRetrievalOrchestrator(repository=repository)
    result = orchestrator.orchestrate(request(), now=NOW)
    assert repository.get(result.plan_id) is result
    assert repository.list_all() == (result,)
    assert orchestrator.last_plan is result


def test_empty_repository_has_no_last_plan():
    assert KnowledgeRetrievalOrchestrator().last_plan is None


def test_duplicate_plan_is_rejected():
    repository = InMemoryKnowledgeRetrievalRepository()
    orchestrator = KnowledgeRetrievalOrchestrator(repository=repository)
    result = orchestrator.orchestrate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_plan_is_immutable():
    result = orchestrate()
    with pytest.raises(FrozenInstanceError):
        result.status = KnowledgeRetrievalStatus.WITHHELD


def test_step_is_immutable():
    result = orchestrate()
    with pytest.raises(FrozenInstanceError):
        result.steps[0].priority = 2


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_source_owner():
    with pytest.raises(ValueError, match="match source owner"):
        request(owner="Other")


def test_maximum_sources_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        KnowledgeRetrievalConfig(max_sources=0)


def test_evaluation_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        KnowledgeRetrievalOrchestrator().orchestrate(
            request(),
            now=NOW.replace(tzinfo=None),
        )


def test_plan_identity_changes_with_timestamp():
    first = orchestrate()
    second = KnowledgeRetrievalOrchestrator().orchestrate(
        request(),
        now=NOW.replace(microsecond=1),
    )
    assert first.plan_id != second.plan_id


def test_plan_id_is_validated():
    result = orchestrate()
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, plan_id="invalid")
