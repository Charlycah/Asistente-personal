from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning import GovernedReasoningStatus
from core.llm_provider import LLMRequest
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
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

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Source:
    result: object | None
    calls: int = 0

    def __call__(self, **kwargs):
        self.calls += 1
        return self.result


def reasoning_result(
    *,
    status=GovernedReasoningStatus.COMPLETED,
    owner="Carlos",
    limitations=(),
    assumptions=(),
):
    return SimpleNamespace(
        status=status,
        result_id="reasoning-result-1",
        context=SimpleNamespace(
            context_id="context-1",
            query=SimpleNamespace(owner=owner),
        ),
        inference_run=SimpleNamespace(run_id="run-1"),
        conflict_analysis=SimpleNamespace(analysis_id="analysis-1"),
        decision=SimpleNamespace(
            decision_id="decision-1",
            conclusion="La evidencia respalda una respuesta prudente.",
            confidence_score=0.78,
            limitations=limitations,
            assumptions=assumptions,
        ),
        explanation=SimpleNamespace(
            answer_id="answer-1",
            confidence_label="moderate",
            summary="La conclusión conserva incertidumbre explícita.",
        ),
    )


def request():
    return LLMRequest(prompt="Analizá esto", metadata={"original": "yes"})


def contributor(source):
    return ReasoningRuntimeContributor(source)


def test_completed_reasoning_contributes_explainable_context():
    result = contributor(Source(reasoning_result())).contribute(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert any("Conclusión gobernada" in line for line in result.prompt_lines)
    assert any("0.78" in line for line in result.prompt_lines)
    assert result.reference_ids[0] == "reasoning-result-1"


def test_limitations_and_assumptions_are_exposed_as_governed_context():
    source = Source(
        reasoning_result(
            limitations=("evidencia parcial",),
            assumptions=("datos vigentes",),
        )
    )
    result = contributor(source).contribute(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert any("evidencia parcial" in line for line in result.prompt_lines)
    assert any("datos vigentes" in line for line in result.prompt_lines)


def test_abstention_applies_caution_without_inventing_conclusion():
    source = Source(reasoning_result(status=GovernedReasoningStatus.ABSTAINED))
    result = contributor(source).contribute(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert "evidencia insuficiente" in result.prompt_lines[0]
    assert not any("Conclusión gobernada" in line for line in result.prompt_lines)


@pytest.mark.parametrize(
    ("status", "rationale"),
    (
        (
            GovernedReasoningStatus.BLOCKED,
            "governed_reasoning_blocked",
        ),
        (
            GovernedReasoningStatus.REVIEW_REQUIRED,
            "governed_reasoning_requires_review",
        ),
    ),
)
def test_non_publishable_reasoning_is_skipped(status, rationale):
    source = Source(reasoning_result(status=status))
    result = contributor(source).contribute(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == (rationale,)


def test_missing_reasoning_is_skipped():
    result = contributor(Source(None)).contribute(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.reference_ids == ()


def test_owner_mismatch_is_contained_by_cognitive_orchestrator():
    runtime = CognitiveRuntimeOrchestrator(
        (contributor(Source(reasoning_result(owner="Other"))),)
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert result.contributions[0].status is CognitiveRuntimeStageStatus.FAILED


def test_orchestrator_includes_reasoning_without_exposing_reference_ids():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(reasoning_result())),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Analizá esto",
        request=request(),
        now=NOW,
    )
    assert "Conclusión gobernada" in result.request.prompt
    assert "decision-1" not in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == "reasoning"


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


def test_composition_root_builds_official_reasoning_contributor():
    source = Source(reasoning_result())
    composition = RuntimeCompositionRoot(
        dependencies(governed_reasoning_source=source)
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    assert source.calls == 1
    assert "Conclusión gobernada" in prepared.inference_request.prompt


def test_living_conversation_precedes_reasoning_in_official_order():
    from tests.test_m190_living_conversation_runtime_integration import (
        Source as LivingSource,
    )
    from tests.test_m190_living_conversation_runtime_integration import (
        integration,
    )

    composition = RuntimeCompositionRoot(
        dependencies(
            living_conversation_source=LivingSource(integration()),
            governed_reasoning_source=Source(reasoning_result()),
        )
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    prompt = prepared.inference_request.prompt
    assert prompt.index("Cadencia conversacional") < prompt.index(
        "Conclusión gobernada"
    )


def test_existing_cognitive_contributors_remain_after_reasoning():
    existing = SimpleNamespace(
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
    runtime = CognitiveRuntimeOrchestrator((existing,))
    composition = RuntimeCompositionRoot(
        dependencies(
            governed_reasoning_source=Source(reasoning_result()),
            cognitive_runtime=runtime,
        )
    ).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    prompt = prepared.inference_request.prompt
    assert prompt.index("Conclusión gobernada") < prompt.index("Contexto personalizado")


def test_non_official_cognitive_runtime_combination_is_rejected():
    with pytest.raises(TypeError, match="official"):
        RuntimeCompositionRoot(
            dependencies(
                governed_reasoning_source=Source(reasoning_result()),
                cognitive_runtime=SimpleNamespace(),
            )
        ).compose()
