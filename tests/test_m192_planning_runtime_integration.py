from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.adaptive_cognition import (
    ExecutiveMilestone,
    ExecutiveObjective,
    ExecutivePlan,
    ExecutivePlanStatus,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)
from tests.test_m178_runtime_composition_root import (
    request as pipeline_request,
)
from tests.test_m190_living_conversation_runtime_integration import (
    Source as LivingSource,
)
from tests.test_m190_living_conversation_runtime_integration import (
    integration,
)
from tests.test_m191_reasoning_runtime_integration import (
    Source as ReasoningSource,
)
from tests.test_m191_reasoning_runtime_integration import (
    reasoning_result,
)

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Source:
    result: ExecutivePlan | None
    calls: int = 0

    def __call__(self, **kwargs):
        self.calls += 1
        return self.result


def plan(
    *,
    status=ExecutivePlanStatus.APPROVED,
    owner="Carlos",
    constraints=("No ejecutar acciones",),
):
    objective = ExecutiveObjective(
        "Preparar una respuesta útil",
        ("Mantener claridad", "Preservar gobernanza"),
    )
    milestone = ExecutiveMilestone(
        "Estructurar la respuesta",
        (objective.objective_id,),
        1,
    )
    return ExecutivePlan(
        owner=owner,
        title="Plan del turno",
        purpose="Organizar una respuesta compleja",
        horizon="near",
        objectives=(objective,),
        milestones=(milestone,),
        status=status,
        constraints=constraints,
        reflection_ids=("reflection-1",),
        mental_model_ids=("model-1",),
        knowledge_proposal_ids=("knowledge-1",),
        created_at=NOW,
    )


def request():
    return LLMRequest(prompt="Organizá esto", metadata={"original": "yes"})


def contributor(source):
    return PlanningRuntimeContributor(source)


def test_approved_plan_contributes_governed_structure():
    result = contributor(Source(plan())).contribute(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("Plan ejecutivo" in line for line in result.prompt_lines)
    assert any("Objetivo planificado" in line for line in result.prompt_lines)
    assert any("Hito 1" in line for line in result.prompt_lines)


def test_active_plan_is_publishable_without_executing_it():
    result = contributor(Source(plan(status="active"))).contribute(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("no ejecutar" in line.lower() for line in result.prompt_lines)


@pytest.mark.parametrize(
    "status",
    (
        ExecutivePlanStatus.DRAFT,
        ExecutivePlanStatus.REVIEW_REQUIRED,
        ExecutivePlanStatus.PAUSED,
        ExecutivePlanStatus.COMPLETED,
        ExecutivePlanStatus.CANCELLED,
    ),
)
def test_non_publishable_plan_states_are_skipped(status):
    result = contributor(Source(plan(status=status))).contribute(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == (f"executive_plan_{status.value}",)


def test_missing_plan_is_skipped():
    result = contributor(Source(None)).contribute(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.reference_ids == ()


def test_owner_mismatch_is_contained_by_orchestrator():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(plan(owner="Other"))),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert result.contributions[0].status is CognitiveRuntimeStageStatus.FAILED


def test_plan_references_remain_outside_provider_prompt():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(plan())),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Organizá esto",
        request=request(),
        now=NOW,
    )
    assert "Plan ejecutivo" in result.request.prompt
    assert "reflection-1" not in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == "planning"


def dependencies(**kwargs):
    return RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        **kwargs,
    )


def test_composition_root_builds_official_planning_contributor():
    source = Source(plan())
    composition = RuntimeCompositionRoot(
        dependencies(executive_planning_source=source)
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    assert source.calls == 1
    assert "Plan ejecutivo" in prepared.inference_request.prompt


def test_official_order_is_living_reasoning_planning_then_custom():
    custom = SimpleNamespace(
        name="custom",
        contribute=lambda **kwargs: __import__(
            "core.cognitive_runtime_orchestration",
            fromlist=["CognitiveRuntimeContribution"],
        ).CognitiveRuntimeContribution(
            stage="custom",
            status="applied",
            prompt_lines=("Contexto personalizado.",),
            rationale=("selected",),
        ),
    )
    composition = RuntimeCompositionRoot(
        dependencies(
            living_conversation_source=LivingSource(integration()),
            governed_reasoning_source=ReasoningSource(reasoning_result()),
            executive_planning_source=Source(plan()),
            cognitive_runtime=CognitiveRuntimeOrchestrator((custom,)),
        )
    ).compose()
    prompt = composition.preparation.prepare(
        pipeline_request()
    ).inference_request.prompt
    assert prompt.index("Cadencia conversacional") < prompt.index(
        "Conclusión gobernada"
    )
    assert prompt.index("Conclusión gobernada") < prompt.index("Plan ejecutivo")
    assert prompt.index("Plan ejecutivo") < prompt.index("Contexto personalizado")


def test_non_official_runtime_combination_is_rejected():
    with pytest.raises(TypeError, match="official"):
        RuntimeCompositionRoot(
            dependencies(
                executive_planning_source=Source(plan()),
                cognitive_runtime=SimpleNamespace(),
            )
        ).compose()
