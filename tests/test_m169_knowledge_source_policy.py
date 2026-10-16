from dataclasses import FrozenInstanceError, replace

import pytest

from core.knowledge_source_policy import (
    InMemoryKnowledgeSourcePolicyRepository,
    KnowledgeSourceAction,
    KnowledgeSourceKind,
    KnowledgeSourceNeed,
    KnowledgeSourcePolicy,
    KnowledgeSourcePolicyConfig,
    KnowledgeSourcePolicyRequest,
    KnowledgeSourceStatus,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m168_governed_provider_routing import route

ROUTE = route()


def need(query="Quien fue Bach?", **changes):
    values = {"query": query}
    values.update(changes)
    return KnowledgeSourceNeed(**values)


def request(*, provider_route=ROUTE, source_need=None, **changes):
    values = {
        "owner": "Carlos",
        "provider_route": provider_route,
        "need": source_need or need(),
    }
    values.update(changes)
    return KnowledgeSourcePolicyRequest(**values)


def decide(*, config=None, provider_route=ROUTE, source_need=None, **changes):
    policy = KnowledgeSourcePolicy(config=config)
    return policy.decide(
        request(
            provider_route=provider_route,
            source_need=source_need,
            **changes,
        ),
        now=NOW,
    )


def test_internal_knowledge_is_used_when_confidence_is_sufficient():
    result = decide()
    assert result.status is KnowledgeSourceStatus.INTERNAL_SUFFICIENT
    assert result.action is KnowledgeSourceAction.USE_INTERNAL
    assert result.selected_sources == (KnowledgeSourceKind.INTERNAL,)


def test_preserves_exact_m168_lineage():
    result = decide()
    assert result.request.provider_route is ROUTE


def test_current_information_requires_external_sources():
    result = decide(
        source_need=need(
            "Que novedades hay hoy sobre la NASA?",
            current_information_required=True,
        )
    )
    assert result.status is KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED
    assert result.selected_sources == (
        KnowledgeSourceKind.NEWS,
        KnowledgeSourceKind.WEB,
    )
    assert result.external_knowledge_required


def test_explicit_external_request_requires_external_source():
    result = decide(
        source_need=need(
            "Buscalo en Internet",
            explicit_external_request=True,
            preferred_sources=(KnowledgeSourceKind.WEB,),
        )
    )
    assert result.status is KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED
    assert result.selected_sources == (KnowledgeSourceKind.WEB,)


def test_explicit_verification_requires_verification():
    result = decide(
        source_need=need(
            "Verifica este dato",
            verification_required=True,
            preferred_sources=(KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,),
        )
    )
    assert result.status is KnowledgeSourceStatus.VERIFICATION_REQUIRED
    assert result.action is KnowledgeSourceAction.DECLARE_VERIFICATION_REQUIREMENT
    assert result.verification_required


def test_local_documents_are_preferred_before_external_sources():
    result = decide(
        source_need=need(
            "Que dice mi manual?",
            internal_confidence=0.2,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        )
    )
    assert result.status is KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED
    assert result.selected_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)


def test_policy_can_disable_local_document_preference():
    config = KnowledgeSourcePolicyConfig(prefer_local_documents=False)
    result = decide(
        config=config,
        source_need=need(
            "Que dice mi manual?",
            internal_confidence=0.2,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        ),
    )
    assert result.status is KnowledgeSourceStatus.VERIFICATION_REQUIRED
    assert result.selected_sources == (KnowledgeSourceKind.WEB,)


def test_low_internal_confidence_requires_verification_by_default():
    result = decide(source_need=need(internal_confidence=0.2))
    assert result.status is KnowledgeSourceStatus.VERIFICATION_REQUIRED
    assert result.external_knowledge_required


def test_low_confidence_can_require_external_without_verification():
    config = KnowledgeSourcePolicyConfig(require_verification_for_low_confidence=False)
    result = decide(config=config, source_need=need(internal_confidence=0.2))
    assert result.status is KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED
    assert not result.verification_required


def test_external_requirement_is_withheld_when_external_is_disabled():
    config = KnowledgeSourcePolicyConfig(allow_external_sources=False)
    result = decide(
        config=config,
        source_need=need(current_information_required=True),
    )
    assert result.status is KnowledgeSourceStatus.WITHHELD
    assert result.action is KnowledgeSourceAction.WITHHOLD
    assert result.selected_sources == ()


def test_withheld_provider_route_withholds_source_policy():
    withheld_route = replace(
        ROUTE,
        status="withheld",
        action="withhold",
        selected_provider=None,
        fallback_providers=(),
        route_kind=None,
        route_declared=False,
        route_id="",
    )
    result = decide(provider_route=withheld_route)
    assert result.status is KnowledgeSourceStatus.WITHHELD
    assert result.rationale == ("provider_route_not_available",)


def test_not_requested_is_not_applicable():
    result = decide(policy_requested=False)
    assert result.status is KnowledgeSourceStatus.NOT_APPLICABLE
    assert result.action is KnowledgeSourceAction.NONE


def test_preferred_sources_are_preserved_for_external_requirement():
    result = decide(
        source_need=need(
            current_information_required=True,
            preferred_sources=(
                KnowledgeSourceKind.API,
                KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
            ),
        )
    )
    assert result.selected_sources == (
        KnowledgeSourceKind.API,
        KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
    )


def test_internal_source_is_removed_from_external_selection():
    result = decide(
        source_need=need(
            current_information_required=True,
            preferred_sources=(
                KnowledgeSourceKind.INTERNAL,
                KnowledgeSourceKind.WEB,
            ),
        )
    )
    assert result.selected_sources == (KnowledgeSourceKind.WEB,)


def test_policy_never_authorizes_retrieval_or_execution():
    result = decide(source_need=need(current_information_required=True))
    assert not result.retrieval_allowed
    assert not result.network_access_allowed
    assert not result.provider_call_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_decision_and_exposes_last():
    repository = InMemoryKnowledgeSourcePolicyRepository()
    policy = KnowledgeSourcePolicy(repository=repository)
    result = policy.decide(request(), now=NOW)
    assert repository.get(result.decision_id) is result
    assert repository.list_all() == (result,)
    assert policy.last_decision is result


def test_empty_repository_has_no_last_decision():
    assert KnowledgeSourcePolicy().last_decision is None


def test_duplicate_decision_is_rejected():
    repository = InMemoryKnowledgeSourcePolicyRepository()
    policy = KnowledgeSourcePolicy(repository=repository)
    result = policy.decide(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_decision_is_immutable():
    result = decide()
    with pytest.raises(FrozenInstanceError):
        result.external_knowledge_required = True


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_route_owner():
    with pytest.raises(ValueError, match="match route owner"):
        request(owner="Other")


def test_query_is_required():
    with pytest.raises(ValueError, match="query"):
        need(" ")


def test_internal_confidence_must_be_bounded():
    with pytest.raises(ValueError, match="between zero and one"):
        need(internal_confidence=1.1)


def test_minimum_internal_confidence_must_be_bounded():
    with pytest.raises(ValueError, match="between zero and one"):
        KnowledgeSourcePolicyConfig(minimum_internal_confidence=-0.1)


def test_preferred_sources_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        need(
            preferred_sources=(
                KnowledgeSourceKind.WEB,
                KnowledgeSourceKind.WEB,
            )
        )


def test_evaluation_timestamp_must_be_aware():
    policy = KnowledgeSourcePolicy()
    with pytest.raises(ValueError, match="timezone-aware"):
        policy.decide(request(), now=NOW.replace(tzinfo=None))


def test_decision_id_is_deterministic():
    first = decide()
    second = decide()
    assert first.decision_id == second.decision_id


def test_inconsistent_decision_id_is_rejected():
    result = decide()
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, decision_id="wrong")


def test_inactive_policy_cannot_select_sources():
    result = decide(policy_requested=False)
    with pytest.raises(ValueError, match="cannot select sources"):
        replace(
            result,
            selected_sources=(KnowledgeSourceKind.INTERNAL,),
            decision_id="",
        )


def test_external_flag_must_match_status():
    result = decide()
    with pytest.raises(ValueError, match="external knowledge flag"):
        replace(result, external_knowledge_required=True, decision_id="")
