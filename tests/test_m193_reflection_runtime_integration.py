from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.adaptive_cognition import (
    ReflectionImportance,
    ReflectionObservation,
    ReflectionOutcome,
    ReflectionRecord,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest
from core.reflection_runtime_integration import ReflectionRuntimeContributor
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
from tests.test_m192_planning_runtime_integration import (
    Source as PlanningSource,
)
from tests.test_m192_planning_runtime_integration import (
    plan,
)

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Source:
    result: ReflectionRecord | None
    calls: int = 0

    def __call__(self, **kwargs):
        self.calls += 1
        return self.result


def observation(*, importance=ReflectionImportance.MEDIUM):
    return ReflectionObservation(
        kind="score_trend",
        description="La respuesta puede beneficiarse de una revisión final.",
        importance=importance,
        confidence=0.8,
        source_ids=("assessment-1",),
    )


def reflection(
    *,
    outcome=ReflectionOutcome.STABLE,
    importance=ReflectionImportance.MEDIUM,
    recommendations=("Verificar límites antes de responder",),
):
    return ReflectionRecord(
        outcome=outcome,
        summary="La estrategia del turno se mantiene coherente.",
        assessment_ids=("assessment-1",),
        observations=(observation(importance=importance),),
        recommendations=recommendations,
        episode_ids=("episode-1",),
        mental_model_ids=("model-1",),
        created_at=NOW,
    )


def request():
    return LLMRequest(prompt="Revisá esta respuesta", metadata={"original": "yes"})


def contributor(source):
    return ReflectionRuntimeContributor(source)


def test_stable_reflection_contributes_review_context():
    result = contributor(Source(reflection())).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("Reflexión adaptativa" in line for line in result.prompt_lines)
    assert any("no reescribir" in line for line in result.prompt_lines)


def test_improving_reflection_is_publishable():
    result = contributor(
        Source(reflection(outcome=ReflectionOutcome.IMPROVING))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("improving" in line for line in result.prompt_lines)


def test_insufficient_reflection_applies_caution_without_pattern_claims():
    result = contributor(
        Source(reflection(outcome=ReflectionOutcome.INSUFFICIENT))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert result.rationale == ("adaptive_reflection_insufficient_applied",)
    assert any("insuficiente" in line for line in result.prompt_lines)


@pytest.mark.parametrize(
    "outcome",
    (ReflectionOutcome.MIXED, ReflectionOutcome.DEGRADING),
)
def test_review_required_outcomes_are_skipped(outcome):
    result = contributor(Source(reflection(outcome=outcome))).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert "requires_review" in result.rationale[0]


def test_high_importance_observation_requires_review():
    result = contributor(
        Source(reflection(importance=ReflectionImportance.HIGH))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED


def test_missing_reflection_is_skipped():
    result = contributor(Source(None)).contribute(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.reference_ids == ()


def test_reflection_references_remain_outside_provider_prompt():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(reflection())),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Revisá esta respuesta",
        request=request(),
        now=NOW,
    )
    assert "Reflexión adaptativa" in result.request.prompt
    assert "assessment-1" not in result.request.prompt
    assert "episode-1" not in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == "reflection"


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


def test_composition_root_builds_official_reflection_contributor():
    source = Source(reflection())
    composition = RuntimeCompositionRoot(
        dependencies(adaptive_reflection_source=source)
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    assert source.calls == 1
    assert "Reflexión adaptativa" in prepared.inference_request.prompt


def test_official_order_places_reflection_after_planning_then_custom():
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
            adaptive_reflection_source=Source(reflection()),
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
    assert prompt.index("Reflexión adaptativa") < prompt.index("Contexto personalizado")


def test_non_official_runtime_combination_is_rejected():
    with pytest.raises(TypeError, match="official"):
        RuntimeCompositionRoot(
            dependencies(
                adaptive_reflection_source=Source(reflection()),
                cognitive_runtime=SimpleNamespace(),
            )
        ).compose()
