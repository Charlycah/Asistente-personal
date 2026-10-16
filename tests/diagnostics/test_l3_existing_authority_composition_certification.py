from __future__ import annotations

from app.canonical_decision_facade import CANONICAL_DECISION_COMPONENTS
from app.canonical_planning_facade import CANONICAL_PLANNING_COMPONENTS
from app.cognitive_runtime_sources import OperationalCognitiveSource
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_planning import CognitivePlanner, ToolRequirement
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.executive_cognitive_runtime import ExecutiveCognitiveRuntimeContributor
from core.llm_provider import LLMRequest
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.reflection_runtime_integration import ReflectionRuntimeContributor
from scripts.diagnostics.l3_existing_authority_composition_certification import (
    NOW,
    Status,
    evaluate,
)


def _runtime() -> CognitiveRuntimeOrchestrator:
    source = OperationalCognitiveSource()
    return CognitiveRuntimeOrchestrator(
        (
            ReasoningRuntimeContributor(source.reasoning),
            PlanningRuntimeContributor(source.planning),
            ReflectionRuntimeContributor(source.reflection),
            ExecutiveCognitiveRuntimeContributor(source.coordination),
        )
    )


def _stages(text: str) -> tuple[str, ...]:
    return _runtime().enrich(
        owner="Carlos",
        session_id="diagnostic",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    ).activated_stages


def test_a5_non_cognitive_turn_skips_the_official_cognitive_bundle() -> None:
    assert _stages("Hola, contame algo breve.") == ()


def test_a5_distinct_cognitive_needs_activate_distinct_stages() -> None:
    assert _stages(
        "Analizá cognitivamente si estas alternativas son equivalentes."
    ) == ("reasoning",)
    assert _stages(
        "Planificá cómo estudiar este problema sin ejecutar ninguna acción."
    ) == ("planning",)
    assert _stages(
        "Reflexioná sobre por qué esta explicación podría estar incompleta."
    ) == ("reflection",)


def test_a6_shadow_planner_can_represent_multineed_composition() -> None:
    plan = CognitivePlanner().plan(
        "¿Te acordás de nuestra restricción anterior y qué clima hay hoy "
        "para evaluar la decisión?"
    )
    assert plan.required_tools == (
        ToolRequirement.MEMORY,
        ToolRequirement.WEATHER,
    )


def test_a6_shadow_planner_remains_nonoperational_by_contract() -> None:
    component = next(
        item for item in CANONICAL_PLANNING_COMPONENTS
        if item.key == "cognitive_planner_shadow"
    )
    assert component.role.value == "shadow"
    assert component.operational is False


def test_a6_primary_decision_does_not_claim_novel_scenario() -> None:
    primary = next(
        item for item in CANONICAL_DECISION_COMPONENTS
        if item.key == "unified_cognitive_coordination"
    )
    assert primary.role.value == "primary"
    assert primary.operational is True
    assert UnifiedCognitiveCoordinator._detect_scenario(
        "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada."
    ) is None


def test_certification_keeps_a5_and_a6_partial_without_production_change() -> None:
    report = evaluate()
    statuses = {item["gate_id"]: item["status"] for item in report["gates"]}
    assert statuses["A5"] == Status.PARTIAL
    assert statuses["A6"] == Status.PARTIAL
    assert statuses["G1"] == Status.PASS_BY_DESIGN
    assert report["production_fingerprint_preserved"] is True
    assert report["production_authorized"] is False
    assert report["architectural_result"] == "MINIMAL_PRODUCTION_CONTRACT_JUSTIFIED"
