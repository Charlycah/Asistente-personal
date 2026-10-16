from dataclasses import FrozenInstanceError, replace
from datetime import datetime

import pytest

from core.governed_provider_execution_adapter import (
    LocalProviderExecutionAction,
    LocalProviderExecutionRequest,
    LocalProviderExecutionResult,
    LocalProviderExecutionStatus,
)
from core.knowledge_retrieval_execution import (
    KnowledgeExecutionStatus,
    KnowledgeRetrievalArtifact,
    KnowledgeRetrievalExecution,
    KnowledgeRetrievalExecutionRequest,
    KnowledgeStepExecution,
    KnowledgeStepExecutionStatus,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
)
from core.knowledge_source_policy import KnowledgeSourceKind
from core.llm_provider import LLMRequest, LLMResponse
from core.operational_response_assembly import (
    InMemoryOperationalResponseRepository,
    OperationalEvidence,
    OperationalResponseAction,
    OperationalResponseAssembler,
    OperationalResponseAssemblyConfig,
    OperationalResponseAssemblyRequest,
    OperationalResponseStatus,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m167_local_first_provider_policy import decide as provider_policy
from tests.test_m167_local_first_provider_policy import health
from tests.test_m168_governed_provider_routing import route as build_route
from tests.test_m169_knowledge_source_policy import decide, need


def provider_result(
    *,
    status=LocalProviderExecutionStatus.COMPLETED,
    text="Respuesta operativa",
    accepted=True,
):
    route = build_route(policy_decision=provider_policy(health_result=health()))
    request = LocalProviderExecutionRequest(
        owner="Carlos",
        route=route,
        inference_request=LLMRequest(prompt="Pregunta"),
    )
    response = LLMResponse(
        text=text, provider="ollama", model="llama3", accepted=accepted
    )
    attempted = status in {
        LocalProviderExecutionStatus.COMPLETED,
        LocalProviderExecutionStatus.REJECTED,
        LocalProviderExecutionStatus.FAILED,
    }
    return LocalProviderExecutionResult(
        request=request,
        status=status,
        action=LocalProviderExecutionAction.EXECUTE_LOCAL_PROVIDER
        if status is LocalProviderExecutionStatus.COMPLETED
        else LocalProviderExecutionAction.REPORT_FAILURE,
        response=response,
        selected_provider_name="ollama" if attempted else "",
        selected_model_name="llama3"
        if status is LocalProviderExecutionStatus.COMPLETED
        else "",
        provider_call_performed=attempted,
        inference_performed=attempted,
        network_access_allowed=False,
        remote_fallback_allowed=False,
        platform_mutation_allowed=False,
        rationale=("test_provider_result",),
        created_at=NOW,
    )


def retrieval_result(*, success=True, external=False):
    source = KnowledgeSourceKind.WEB if external else KnowledgeSourceKind.INTERNAL
    decision = decide(
        source_need=need(
            "Consulta",
            current_information_required=external,
            preferred_sources=(source,),
        )
    )
    plan = KnowledgeRetrievalOrchestrator().orchestrate(
        KnowledgeRetrievalRequest(owner="Carlos", source_decision=decision), now=NOW
    )
    steps = []
    for plan_step in plan.steps:
        artifact = (
            KnowledgeRetrievalArtifact(
                source=plan_step.source,
                query=plan_step.query,
                content="Evidencia",
                references=("https://example.com",) if external else (),
            )
            if success
            else None
        )
        steps.append(
            KnowledgeStepExecution(
                step=plan_step,
                status=KnowledgeStepExecutionStatus.SUCCEEDED
                if success
                else KnowledgeStepExecutionStatus.FAILED,
                artifact=artifact,
                rationale=("test_step",),
            )
        )
    return KnowledgeRetrievalExecution(
        request=KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=plan),
        status=KnowledgeExecutionStatus.COMPLETED
        if success
        else KnowledgeExecutionStatus.FAILED,
        steps=tuple(steps),
        retrieval_performed=success,
        network_access_performed=success and external,
        provider_call_performed=False,
        platform_mutation_performed=False,
        rationale=("test_retrieval",),
        created_at=NOW,
    )


def assemble(*, provider=None, retrieval=None, config=None, request_changes=None):
    values = {
        "owner": "Carlos",
        "provider_execution": provider if provider is not None else provider_result(),
        "retrieval_execution": retrieval,
    }
    values.update(request_changes or {})
    request = OperationalResponseAssemblyRequest(**values)
    assembler = OperationalResponseAssembler(config=config)
    return assembler.assemble(request, now=NOW), assembler


def test_assembles_accepted_provider_response():
    result, _ = assemble()
    assert result.status is OperationalResponseStatus.COMPLETED
    assert result.action is OperationalResponseAction.DELIVER_RESPONSE
    assert result.response_text == "Respuesta operativa"


def test_preserves_exact_provider_lineage():
    provider = provider_result()
    result, _ = assemble(provider=provider)
    assert result.request.provider_execution is provider
    assert result.provider_execution_id == provider.execution_id


def test_preserves_exact_retrieval_lineage():
    retrieval = retrieval_result()
    result, _ = assemble(retrieval=retrieval)
    assert result.request.retrieval_execution is retrieval
    assert result.retrieval_execution_id == retrieval.execution_id


def test_successful_retrieval_becomes_evidence():
    result, _ = assemble(retrieval=retrieval_result())
    assert result.evidence[0].content == "Evidencia"
    assert result.retrieval_performed


def test_external_network_flag_is_lineage_only():
    result, _ = assemble(retrieval=retrieval_result(external=True))
    assert result.network_access_performed
    assert not result.platform_mutation_performed


def test_not_requested_is_not_applicable():
    result, _ = assemble(request_changes={"assembly_requested": False})
    assert result.status is OperationalResponseStatus.NOT_APPLICABLE
    assert not result.response_text


def test_disabled_assembly_is_withheld():
    result, _ = assemble(
        config=OperationalResponseAssemblyConfig(assembly_enabled=False)
    )
    assert result.status is OperationalResponseStatus.WITHHELD


def test_missing_provider_is_withheld_by_default():
    request = OperationalResponseAssemblyRequest(
        owner="Carlos", provider_execution=None
    )
    result = OperationalResponseAssembler().assemble(request, now=NOW)
    assert result.status is OperationalResponseStatus.WITHHELD


def test_missing_provider_can_be_reported_as_failure():
    request = OperationalResponseAssemblyRequest(
        owner="Carlos", provider_execution=None
    )
    result = OperationalResponseAssembler(
        config=OperationalResponseAssemblyConfig(require_provider_response=False)
    ).assemble(request, now=NOW)
    assert result.status is OperationalResponseStatus.FAILED


@pytest.mark.parametrize(
    "status",
    [LocalProviderExecutionStatus.FAILED, LocalProviderExecutionStatus.REJECTED],
)
def test_non_deliverable_provider_result_fails(status):
    result, _ = assemble(provider=provider_result(status=status, accepted=False))
    assert result.status is OperationalResponseStatus.FAILED
    assert result.action is OperationalResponseAction.REPORT_FAILURE


def test_response_limit_withholds_delivery():
    result, _ = assemble(
        config=OperationalResponseAssemblyConfig(maximum_response_characters=3)
    )
    assert result.status is OperationalResponseStatus.WITHHELD
    assert "response_character_limit_exceeded" in result.limitations


def test_failed_retrieval_yields_partial_response():
    result, _ = assemble(retrieval=retrieval_result(success=False))
    assert result.status is OperationalResponseStatus.PARTIAL
    assert result.action is OperationalResponseAction.DELIVER_WITH_LIMITATIONS


def test_zero_evidence_limit_marks_partial():
    result, _ = assemble(
        retrieval=retrieval_result(),
        config=OperationalResponseAssemblyConfig(maximum_evidence_items=0),
    )
    assert result.status is OperationalResponseStatus.PARTIAL
    assert not result.evidence


def test_evidence_character_limit_marks_partial():
    result, _ = assemble(
        retrieval=retrieval_result(),
        config=OperationalResponseAssemblyConfig(maximum_evidence_characters=1),
    )
    assert result.status is OperationalResponseStatus.PARTIAL
    assert "evidence_character_limit_reached" in result.limitations


def test_repository_records_result():
    repository = InMemoryOperationalResponseRepository()
    assembler = OperationalResponseAssembler(repository=repository)
    request = OperationalResponseAssemblyRequest(
        owner="Carlos", provider_execution=provider_result()
    )
    result = assembler.assemble(request, now=NOW)
    assert repository.get(result.response_id) is result
    assert repository.list_all() == (result,)


def test_duplicate_repository_record_is_rejected():
    repository = InMemoryOperationalResponseRepository()
    result, _ = assemble()
    repository.add(result)
    with pytest.raises(ValueError):
        repository.add(result)


def test_models_are_immutable():
    result, _ = assemble()
    with pytest.raises(FrozenInstanceError):
        result.response_text = "changed"


def test_owner_must_match_provider_execution():
    with pytest.raises(ValueError):
        OperationalResponseAssemblyRequest(
            owner="Other", provider_execution=provider_result()
        )


def test_owner_must_match_retrieval_execution():
    with pytest.raises(ValueError):
        OperationalResponseAssemblyRequest(
            owner="Other", retrieval_execution=retrieval_result()
        )


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError):
        OperationalResponseAssemblyRequest(owner=" ")


def test_naive_timestamp_is_rejected():
    request = OperationalResponseAssemblyRequest(
        owner="Carlos", provider_execution=provider_result()
    )
    with pytest.raises(ValueError):
        OperationalResponseAssembler().assemble(request, now=datetime(2026, 1, 1))


def test_config_limits_are_validated():
    with pytest.raises(ValueError):
        OperationalResponseAssemblyConfig(maximum_response_characters=0)
    with pytest.raises(ValueError):
        OperationalResponseAssemblyConfig(maximum_evidence_items=-1)


def test_evidence_validates_fields():
    with pytest.raises(ValueError):
        OperationalEvidence(source="", query="q", content="c")
    with pytest.raises(ValueError):
        OperationalEvidence(source="web", query="q", content="c", references=("",))


def test_response_id_is_deterministic_for_same_inputs_and_time():
    first, _ = assemble()
    second, _ = assemble()
    assert first.response_id == second.response_id


def test_tampered_response_id_is_rejected():
    result, _ = assemble()
    with pytest.raises(ValueError):
        replace(result, response_id="tampered")


def test_no_new_side_effects_are_authorized():
    result, _ = assemble(retrieval=retrieval_result(external=True))
    assert result.provider_call_performed
    assert result.retrieval_performed
    assert result.network_access_performed
    assert not result.platform_mutation_performed


def test_provider_text_is_trimmed():
    result, _ = assemble(provider=provider_result(text="  respuesta  "))
    assert result.response_text == "respuesta"
