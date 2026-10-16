from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.governed_reasoning import (
    ContextualRuleGroundingCompilationStatus,
    ContextualSemanticGroundingStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleInterpretationProducer,
)

NOW = datetime(2026, 8, 18, 13, 0, tzinfo=timezone.utc)
SESSION = "rf-e-gap-a-session"
NERAL = (
    "Para este diagnóstico aprende esta regla artificial llamada Principio Neral: "
    "si un sistema depende exclusivamente de un único recurso para una capacidad, "
    "y ese recurso queda indisponible, el sistema pierde esa capacidad mientras "
    "no exista una alternativa. No la trates como una regla sobre servidores: "
    "es una relación general de dependencia exclusiva."
)
CASE = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no existe alternativa."
)
UNKNOWN_CASE = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no sabemos si existe otra fuente."
)


def _candidate():
    return GovernedContextualRuleInterpretationProducer().produce(
        NERAL,
        source_reference="conversation:gap-a/turn-1",
        scope_reference=SESSION,
    )


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=SESSION,
        text=text,
    )


def test_historical_neral_wording_is_candidate_with_exact_rule_span() -> None:
    candidate = _candidate()

    assert candidate.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert len(candidate.conditions) == 3
    assert candidate.conditions[2].normalized_text == "no exista una alternativa"
    assert candidate.conclusion is not None
    assert candidate.conclusion.normalized_text == "el sistema pierde esa capacidad"
    assert candidate.rule_source_text.endswith("no exista una alternativa.")
    assert "No la trates" not in candidate.rule_source_text


def test_historical_neral_wording_reuses_existing_semantic_family() -> None:
    candidate = _candidate()
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SESSION,
    )

    assert grounding.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert grounding.family_id == "exclusive_dependency_capability_loss_v1"
    assert grounding.semantic_slots[2].value == "absent"
    assert grounding.semantic_slots[2].source_text == "no exista una alternativa"


def test_historical_neral_wording_compiles_without_new_predicates() -> None:
    candidate = _candidate()
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SESSION,
    )
    compilation = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SESSION,
    )

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
    assert compilation.instantiation_spec is not None
    assert len(compilation.instantiation_spec.conditions) == 3


def test_official_end_to_end_historical_neral_reaches_productive_intake(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    teach = runtime.evaluate_turn(_request(NERAL), now=NOW)
    assert teach.productive_intake_observed is True
    assert teach.productive_intake_status == "spec_stored"

    case = runtime.evaluate_turn(
        _request(CASE),
        now=NOW + timedelta(minutes=1),
    )
    assert case.productive_intake_observed is True
    assert case.productive_intake_status == "rule_admitted"
    assert len(reasoning.orchestrator.inference_engine.registry.list()) == 1


def test_historical_neral_keeps_unknown_alternative_fail_closed(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    runtime.evaluate_turn(_request(NERAL), now=NOW)
    case = runtime.evaluate_turn(
        _request(UNKNOWN_CASE),
        now=NOW + timedelta(minutes=1),
    )

    assert case.productive_intake_observed is True
    assert case.productive_intake_status in {
        "case_insufficient",
        "case_unsupported",
    }
    assert reasoning.orchestrator.inference_engine.registry.list() == ()
