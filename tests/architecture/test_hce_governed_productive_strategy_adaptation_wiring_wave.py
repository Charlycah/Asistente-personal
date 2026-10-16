from __future__ import annotations

from app.runtime_root_factory import build_runtime_root
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_runtime_orchestration import (
    CognitiveStrategyApplicationOutcomeStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="productive-hce",
        text=text,
    )


def test_official_root_injects_same_registered_coordinator_instance(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    coordinator = root.dependencies.cognitive_strategy_coordinator
    assert isinstance(coordinator, UnifiedCognitiveCoordinator)
    registration = root.dependencies.official_capability_registry.registration_for(
        "cognition.unified_coordination_runtime"
    )
    assert registration is not None
    assert registration.interceptor is coordinator


def test_ordinary_preparation_productively_applies_strategy(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    composition = build_runtime_root().compose()
    prepared = composition.preparation.prepare(
        _request(
            "Analizá las alternativas, planificá los pasos y después "
            "reflexioná sobre el enfoque."
        )
    )
    evidence = prepared.strategy_application_evidence
    assert evidence is not None
    assert evidence.status is CognitiveStrategyApplicationOutcomeStatus.APPLIED
    assert evidence.requested_stage_sequence == (
        "reasoning",
        "planning",
        "reflection",
    )
    assert evidence.applied_stage_sequence == evidence.requested_stage_sequence
    assert evidence.persists is False
    assert evidence.creates_memory is False
    assert evidence.creates_learning is False
    assert evidence.executes_actions is False


def test_non_multistep_turn_preserves_runtime_without_strategy_evidence(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    composition = build_runtime_root().compose()
    prepared = composition.preparation.prepare(_request("Analizá este argumento."))
    assert prepared.strategy_application_evidence is None


def test_productive_strategy_does_not_change_provider_route(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    composition = build_runtime_root().compose()
    plain = composition.preparation.prepare(_request("Hola, Roby."))
    strategic = composition.preparation.prepare(
        _request("Analizá las opciones y planificá cómo seguir.")
    )
    assert strategic.provider_route.status == plain.provider_route.status
    assert strategic.provider_route.action == plain.provider_route.action
    assert strategic.provider_route.route_kind == plain.provider_route.route_kind


def test_productive_strategy_application_does_not_execute_registry_capabilities(
    monkeypatch,
):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    before = tuple(registry.capability_names)
    prepared = root.compose().preparation.prepare(
        _request("Recordá lo acordado, analizá las opciones y decidí cuál conviene.")
    )
    assert tuple(registry.capability_names) == before
    evidence = prepared.strategy_application_evidence
    assert evidence is not None
    assert evidence.executes_actions is False
