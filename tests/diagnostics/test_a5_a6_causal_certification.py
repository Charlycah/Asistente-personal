from __future__ import annotations

from datetime import datetime, timezone

from app.cognitive_runtime_sources import OperationalCognitiveSource
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.executive_cognitive_runtime import ExecutiveCognitiveRuntimeContributor
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.reflection_runtime_integration import ReflectionRuntimeContributor

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _contributors():
    source = OperationalCognitiveSource()
    return (
        ReasoningRuntimeContributor(source.reasoning),
        PlanningRuntimeContributor(source.planning),
        ReflectionRuntimeContributor(source.reflection),
        ExecutiveCognitiveRuntimeContributor(source.coordination),
    )


def _run(text: str, contributors=None):
    runtime = CognitiveRuntimeOrchestrator(
        tuple(contributors) if contributors is not None else _contributors()
    )
    return runtime.enrich(
        owner="Carlos",
        session_id="causal-cert",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    )



def _advisory_request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="causal-cert",
        text=text,
    )

def test_a5_problem_need_causally_changes_selected_stages() -> None:
    cases = {
        "Analizá cognitivamente estas alternativas.": ("reasoning",),
        "Planificá cómo estudiar este problema.": ("planning",),
        "Reflexioná sobre por qué esta explicación fue insuficiente.": (
            "reflection",
        ),
        "Coordiná cognitivamente estas partes.": ("executive",),
        "Analizá las opciones y planificá cómo compararlas.": (
            "reasoning",
            "planning",
        ),
    }
    observed = {text: _run(text).activated_stages for text in cases}
    assert observed == cases


def test_a5_irrelevant_stages_are_explicitly_skipped() -> None:
    result = _run("Analizá cognitivamente estas alternativas.")
    states = {item.stage: item.status for item in result.contributions}
    assert states == {
        "reasoning": CognitiveRuntimeStageStatus.APPLIED,
        "planning": CognitiveRuntimeStageStatus.SKIPPED,
        "reflection": CognitiveRuntimeStageStatus.SKIPPED,
        "executive": CognitiveRuntimeStageStatus.SKIPPED,
    }


def test_a5_ablation_of_relevant_stage_changes_cognitive_context() -> None:
    text = "Analizá cognitivamente las opciones y planificá cómo compararlas."
    full = _run(text)
    without_reasoning = _run(text, contributors=_contributors()[1:])
    assert full.activated_stages == ("reasoning", "planning")
    assert without_reasoning.activated_stages == ("planning",)
    assert full.request.prompt != without_reasoning.request.prompt
    assert full.request.metadata["cognitive_stages"] == "reasoning,planning"
    assert without_reasoning.request.metadata["cognitive_stages"] == "planning"


def test_a5_owner_session_and_rationale_survive_selection() -> None:
    result = _run("Analizá cognitivamente estas alternativas.")
    applied = next(item for item in result.contributions if item.stage == "reasoning")
    assert result.owner == "Carlos"
    assert result.session_id == "causal-cert"
    assert applied.rationale
    assert result.orchestration_id


def test_a6_novel_composition_is_advisory_and_not_scenario_driven() -> None:
    class Registry:
        registrations = ()

        def __init__(self) -> None:
            self.executions = 0

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory path must not execute")

    registry = Registry()
    coordinator = UnifiedCognitiveCoordinator(registry)
    text = (
        "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada."
    )
    assert coordinator._detect_scenario(text) is None
    advice = coordinator.compose_advisory(_advisory_request(text))
    assert advice is not None
    assert advice.needs == ("memory", "weather", "decision")
    assert advice.execution_authorized is False
    assert registry.executions == 0


def test_a6_changed_conditions_causally_recompose_needs() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(
        _advisory_request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
        "para evaluar qué conviene hacer.")
    )
    second = coordinator.compose_advisory(
        _advisory_request(
            "Considerá lo que recordamos de mi restricción; el clima ya no es "
        "relevante para esta decisión.")
    )
    assert first is not None and second is not None
    assert "weather" in first.needs
    assert "weather" not in second.needs
    assert first.needs != second.needs


def test_a6_minimality_excludes_unmentioned_capabilities() -> None:
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        _advisory_request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
        "para evaluar qué conviene hacer.")
    )
    assert advice is not None
    assert "calendar" not in advice.needs
    assert "planning" not in advice.needs
    assert "reflection" not in advice.needs
    assert "coordination" not in advice.needs


def test_a6_historical_scenario_detection_remains_separate() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    assert coordinator._detect_scenario("Organizame el viaje") == "travel"
    assert coordinator.compose_advisory(
        _advisory_request("Organizame el viaje")
    ) is None


def test_a6_advice_preserves_provenance_owner_and_scope() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _advisory_request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
        "para evaluar qué conviene hacer.")
    )
    assert advice is not None
    assert advice.owner == "Carlos"
    assert advice.scope == "causal-cert"
    assert advice.provenance
