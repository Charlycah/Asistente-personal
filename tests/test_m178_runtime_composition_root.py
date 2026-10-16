from dataclasses import FrozenInstanceError

import pytest

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedConversationPipelineStatus,
)
from core.knowledge_source_policy import KnowledgeSourceKind, KnowledgeSourceNeed
from core.llm_provider import LLMRequest
from core.local_first_provider_policy import ProviderWorkload, ProviderWorkloadKind
from core.runtime_composition_root import (
    GovernedRuntimePreparation,
    RuntimeCompositionConfig,
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from tests.test_m162_runtime_readiness_gate import evaluate as readiness
from tests.test_m166_provider_health_evaluation import observation
from tests.test_m171_knowledge_retrieval_execution import FakeRetriever
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider


class ReadinessPort:
    def __init__(self, value=None):
        self.value = value or readiness()
        self.calls = []

    def resolve(self, request):
        self.calls.append(request)
        return self.value


class ObservationsPort:
    def __init__(self, value=None):
        self.value = value or (observation(),)
        self.calls = []

    def observe(self, request):
        self.calls.append(request)
        return self.value


class WorkloadPort:
    def __init__(self, value=None):
        self.value = value or ProviderWorkload(ProviderWorkloadKind.CONVERSATION)
        self.calls = []

    def describe(self, request):
        self.calls.append(request)
        return self.value


class NeedPort:
    def __init__(self, value=None):
        self.value = value or KnowledgeSourceNeed(query="Explica ROBY")
        self.calls = []

    def describe(self, request):
        self.calls.append(request)
        return self.value


class InferencePort:
    def __init__(self):
        self.calls = []

    def build(self, request):
        self.calls.append(request)
        return LLMRequest(prompt=request.text, metadata={"session": request.session_id})


def dependencies(*, provider=None, need=None, retrievers=None):
    return RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(need),
        inference_request_port=InferencePort(),
        local_providers=(provider or RecordingProvider(),),
        retrievers=(
            retrievers
            if retrievers is not None
            else {
                KnowledgeSourceKind.INTERNAL: FakeRetriever(content="runtime evidence")
            }
        ),
    )


def request():
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="desktop-main", text="Explica ROBY"
    )


def test_compose_builds_single_official_runtime_graph():
    composition = RuntimeCompositionRoot(dependencies()).compose()
    assert isinstance(composition.preparation, GovernedRuntimePreparation)
    assert composition.conversation_pipeline.preparation_port is composition.preparation
    assert (
        composition.conversation_pipeline.provider_executor
        is composition.provider_executor
    )
    assert (
        composition.conversation_pipeline.response_assembler
        is composition.response_assembler
    )


def test_build_returns_m177_pipeline():
    root = RuntimeCompositionRoot(dependencies())
    assert root.build() is root.compose().conversation_pipeline


def test_compose_is_idempotent():
    root = RuntimeCompositionRoot(dependencies())
    assert root.compose() is root.compose()


def test_composition_is_empty_before_compose():
    root = RuntimeCompositionRoot(dependencies())
    assert root.composition is None


def test_composition_is_exposed_after_compose():
    root = RuntimeCompositionRoot(dependencies())
    composition = root.compose()
    assert root.composition is composition


def test_end_to_end_turn_runs_through_composed_pipeline():
    provider = RecordingProvider()
    result = (
        RuntimeCompositionRoot(dependencies(provider=provider))
        .build()
        .process(request())
    )
    assert result.status is GovernedConversationPipelineStatus.COMPLETED
    assert result.operational_response.response_text == "Hola desde el proveedor local."
    assert len(provider.calls) == 1


def test_all_preparation_input_ports_receive_exact_request():
    deps = dependencies()
    item = request()
    RuntimeCompositionRoot(deps).build().process(item)
    ports = (
        deps.readiness_port,
        deps.observations_port,
        deps.workload_port,
        deps.knowledge_need_port,
        deps.inference_request_port,
    )
    assert all(port.calls == [item] for port in ports)


def test_preparation_preserves_m166_to_m170_lineage():
    composition = RuntimeCompositionRoot(dependencies()).compose()
    prepared = composition.preparation.prepare(request())
    route = prepared.provider_route
    policy = route.request.policy_decision
    health = policy.request.health_result
    plan = composition.retrieval_orchestrator.last_plan
    source = plan.request.source_decision
    assert policy.request.health_result is health
    assert route.request.policy_decision is policy
    assert source.request.provider_route is route
    assert plan.request.source_decision is source


def test_inference_request_is_built_by_injected_port():
    deps = dependencies()
    prepared = RuntimeCompositionRoot(deps).compose().preparation.prepare(request())
    assert prepared.inference_request.prompt == "Explica ROBY"
    assert prepared.inference_request.metadata == {"session": "desktop-main"}


def test_internal_sufficient_plan_is_executed_when_retrieval_enabled():
    result = RuntimeCompositionRoot(dependencies()).build().process(request())
    assert result.retrieval_performed


def test_retrieval_can_be_disabled_at_root():
    root = RuntimeCompositionRoot(
        dependencies(), config=RuntimeCompositionConfig(retrieval_enabled=False)
    )
    composition = root.compose()
    result = composition.conversation_pipeline.process(request())
    assert composition.retrieval_executor is None
    assert not result.retrieval_performed
    assert result.status is GovernedConversationPipelineStatus.COMPLETED


def test_input_limit_is_propagated_to_m177():
    pipeline = RuntimeCompositionRoot(
        dependencies(), config=RuntimeCompositionConfig(maximum_input_characters=3)
    ).build()
    result = pipeline.process(request())
    assert result.status is GovernedConversationPipelineStatus.WITHHELD


def test_duplicate_provider_names_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        RuntimeCompositionDependencies(
            readiness_port=ReadinessPort(),
            observations_port=ObservationsPort(),
            workload_port=WorkloadPort(),
            knowledge_need_port=NeedPort(),
            inference_request_port=InferencePort(),
            local_providers=(RecordingProvider(), RecordingProvider()),
        )


def test_blank_provider_name_is_rejected():
    with pytest.raises(ValueError, match="names"):
        dependencies(provider=RecordingProvider(name=" "))


def test_config_rejects_non_positive_limit():
    with pytest.raises(ValueError, match="positive"):
        RuntimeCompositionConfig(maximum_input_characters=0)


def test_dependencies_are_immutable():
    deps = dependencies()
    with pytest.raises(FrozenInstanceError):
        deps.local_providers = ()


def test_composition_is_immutable():
    composition = RuntimeCompositionRoot(dependencies()).compose()
    with pytest.raises(FrozenInstanceError):
        composition.preparation = None


def test_root_does_not_call_provider_during_composition():
    provider = RecordingProvider()
    RuntimeCompositionRoot(dependencies(provider=provider)).compose()
    assert provider.calls == []


def test_root_does_not_resolve_turn_inputs_during_composition():
    deps = dependencies()
    RuntimeCompositionRoot(deps).compose()
    assert deps.readiness_port.calls == []
    assert deps.observations_port.calls == []
    assert deps.workload_port.calls == []
    assert deps.knowledge_need_port.calls == []
    assert deps.inference_request_port.calls == []


def test_root_never_authorizes_platform_mutation():
    result = RuntimeCompositionRoot(dependencies()).build().process(request())
    assert not result.platform_mutation_performed
