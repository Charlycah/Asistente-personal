from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.adaptive_cognition import (
    CoordinationStatus,
    ExecutiveCoordination,
    ExecutiveDirective,
    ExecutivePriority,
    ExecutiveSubsystem,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.executive_cognitive_runtime import (
    ExecutiveCognitiveRuntimeContributor,
)
from core.llm_provider import LLMRequest
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
from tests.test_m190_living_conversation_runtime_integration import integration
from tests.test_m191_reasoning_runtime_integration import (
    Source as ReasoningSource,
)
from tests.test_m191_reasoning_runtime_integration import reasoning_result
from tests.test_m192_planning_runtime_integration import (
    Source as PlanningSource,
)
from tests.test_m192_planning_runtime_integration import plan
from tests.test_m193_reflection_runtime_integration import (
    Source as ReflectionSource,
)
from tests.test_m193_reflection_runtime_integration import reflection

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Source:
    result: ExecutiveCoordination | None
    calls: int = 0

    def __call__(self, **kwargs):
        self.calls += 1
        return self.result


def coordination(
    *,
    status=CoordinationStatus.APPROVED,
    owner="Carlos",
    subsystem=ExecutiveSubsystem.REASONING,
    priority=ExecutivePriority.HIGH,
):
    directive = ExecutiveDirective(
        title="Coordinar la respuesta del turno",
        subsystem=subsystem,
        milestone_id="milestone-1",
        sequence=1,
        priority=priority,
        constraints=("Preservar gobernanza",),
    )
    return ExecutiveCoordination(
        owner=owner,
        plan_id="plan-1",
        directives=(directive,),
        status=status,
        constraints=("No ejecutar acciones",),
        created_at=NOW,
    )


def request():
    return LLMRequest(
        prompt="Coordiná esta respuesta",
        metadata={"original": "yes"},
    )


def contributor(source):
    return ExecutiveCognitiveRuntimeContributor(source)


def test_approved_coordination_contributes_executive_context():
    result = contributor(Source(coordination())).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("Coordinación ejecutiva" in line for line in result.prompt_lines)
    assert any("Directiva ejecutiva 1" in line for line in result.prompt_lines)
    assert any("no ejecutar" in line.lower() for line in result.prompt_lines)


def test_active_coordination_is_publishable():
    result = contributor(
        Source(coordination(status=CoordinationStatus.ACTIVE))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("active" in line for line in result.prompt_lines)


@pytest.mark.parametrize(
    "status",
    (
        CoordinationStatus.DRAFT,
        CoordinationStatus.REVIEW_REQUIRED,
        CoordinationStatus.PAUSED,
        CoordinationStatus.COMPLETED,
        CoordinationStatus.CANCELLED,
    ),
)
def test_non_publishable_coordination_states_are_skipped(status):
    result = contributor(Source(coordination(status=status))).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED


def test_sensitive_subsystem_requires_review_even_if_approved():
    result = contributor(
        Source(coordination(subsystem=ExecutiveSubsystem.AUTONOMY))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("executive_coordination_requires_review",)


def test_critical_directive_requires_review():
    result = contributor(
        Source(coordination(priority=ExecutivePriority.CRITICAL))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED


def test_missing_coordination_is_skipped():
    result = contributor(Source(None)).contribute(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.reference_ids == ()


def test_owner_mismatch_is_contained_by_orchestrator():
    runtime = CognitiveRuntimeOrchestrator(
        (contributor(Source(coordination(owner="Other"))),)
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.contributions[0].status is CognitiveRuntimeStageStatus.FAILED


def test_internal_references_remain_outside_provider_prompt():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(coordination())),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Coordiná esta respuesta",
        request=request(),
        now=NOW,
    )
    assert "Coordinación ejecutiva" in result.request.prompt
    assert "plan-1" not in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == "executive"


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


def test_composition_root_builds_official_executive_contributor():
    source = Source(coordination())
    composition = RuntimeCompositionRoot(
        dependencies(executive_coordination_source=source)
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    assert source.calls == 1
    assert "Coordinación ejecutiva" in prepared.inference_request.prompt


def test_official_order_places_executive_after_reflection_then_custom():
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
            executive_planning_source=PlanningSource(plan()),
            adaptive_reflection_source=ReflectionSource(reflection()),
            executive_coordination_source=Source(coordination()),
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
    assert prompt.index("Plan ejecutivo") < prompt.index("Reflexión adaptativa")
    assert prompt.index("Reflexión adaptativa") < prompt.index("Coordinación ejecutiva")
    assert prompt.index("Coordinación ejecutiva") < prompt.index(
        "Contexto personalizado"
    )


def test_non_official_runtime_combination_is_rejected():
    with pytest.raises(TypeError, match="official"):
        RuntimeCompositionRoot(
            dependencies(
                executive_coordination_source=Source(coordination()),
                cognitive_runtime=SimpleNamespace(),
            )
        ).compose()
