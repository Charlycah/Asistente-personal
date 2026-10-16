from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)

NOW = datetime(2026, 8, 27, 20, 0, tzinfo=timezone.utc)
OWNER = "Carlos"
SESSION = "hcc-ordinary-productive"
SCOPE = "scope:hcc-ordinary-productive"


def _r1(subject: str, resource: str, capability: str) -> str:
    return (
        f"Regla temporal: si el sistema {subject} depende exclusivamente de un recurso "
        f"{resource} para una función {capability} y ese recurso queda indisponible "
        "y no hay alternativa, entonces ese sistema pierde esa capacidad."
    )


def _r2(prerequisite: str, dependent: str) -> str:
    return (
        f"Regla temporal: si capacidad {prerequisite} es requisito indispensable para "
        f"capacidad {dependent} y la capacidad requisito queda indisponible, entonces "
        "la capacidad dependiente queda impedida."
    )


def _turn(text: str, now: datetime) -> str:
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=SESSION,
        text=text,
    )
    return build_governed_conversation_turn_identity(request, now).turn_id


def _evaluate(
    gateway: OfficialGovernedReasoningRuntimeGateway,
    text: str,
    minute: int,
) -> str:
    now = NOW + timedelta(minutes=minute)
    turn_id = _turn(text, now)
    gateway.evaluate_productive_episode(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
        turn_id=turn_id,
        scope_reference=SCOPE,
    )
    return turn_id


def test_ordinary_runtime_composes_distinct_r1_r2_into_productive_concept() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    _evaluate(gateway, _r1("A", "B", "C"), 0)
    r1_turn = _evaluate(gateway, _r1("D", "E", "F"), 1)
    assert (
        gateway.productive_abstraction_episode(
            owner=OWNER,
            session_id=SESSION,
            turn_id=r1_turn,
        )
        is not None
    )
    assert (
        gateway.productive_concept_episode(
            owner=OWNER,
            session_id=SESSION,
            turn_id=r1_turn,
        )
        is None
    )

    _evaluate(gateway, _r2("alfa", "beta"), 2)
    concept_turn = _evaluate(gateway, _r2("gamma", "delta"), 3)

    r2_episode = gateway.productive_abstraction_episode(
        owner=OWNER,
        session_id=SESSION,
        turn_id=concept_turn,
    )
    concept = gateway.productive_concept_episode(
        owner=OWNER,
        session_id=SESSION,
        turn_id=concept_turn,
    )
    assert r2_episode is not None
    assert concept is not None
    assert concept.canonical_authority == "governed_reasoning"
    assert concept.scope_reference == SCOPE
    assert len(concept.source_abstraction_episode_ids) == 2
    assert r2_episode.episode_id in concept.source_abstraction_episode_ids
    pairs = {
        (
            component.relation,
            component.outcome,
        )
        for component in concept.concept_candidate.components
    }
    assert pairs == {
        ("required_for", "blocked_when_unavailable"),
        ("required_for", "blocked_when_prerequisite_unavailable"),
    }


def test_same_family_repetition_never_fabricates_hcc_diversity() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    turns = [
        _evaluate(gateway, _r1("A", "B", "C"), 10),
        _evaluate(gateway, _r1("D", "E", "F"), 11),
        _evaluate(gateway, _r1("G", "H", "I"), 12),
    ]
    assert any(
        gateway.productive_abstraction_episode(
            owner=OWNER,
            session_id=SESSION,
            turn_id=turn_id,
        )
        is not None
        for turn_id in turns
    )
    assert all(
        gateway.productive_concept_episode(
            owner=OWNER,
            session_id=SESSION,
            turn_id=turn_id,
        )
        is None
        for turn_id in turns
    )


def test_scope_and_session_isolate_ordinary_composition() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _evaluate(gateway, _r1("A", "B", "C"), 20)
    _evaluate(gateway, _r1("D", "E", "F"), 21)

    other_session = "hcc-other-session"
    text1 = _r2("alfa", "beta")
    text2 = _r2("gamma", "delta")
    for minute, text in ((22, text1), (23, text2)):
        now = NOW + timedelta(minutes=minute)
        request = GovernedConversationPipelineRequest(
            owner=OWNER,
            session_id=other_session,
            text=text,
        )
        turn_id = build_governed_conversation_turn_identity(request, now).turn_id
        gateway.evaluate_productive_episode(
            owner=OWNER,
            session_id=other_session,
            text=text,
            now=now,
            turn_id=turn_id,
            scope_reference=SCOPE,
        )
        assert (
            gateway.productive_concept_episode(
                owner=OWNER,
                session_id=other_session,
                turn_id=turn_id,
            )
            is None
        )


def test_productive_concept_reaches_same_turn_consultative_reasoning_source() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    _evaluate(gateway, _r1("A", "B", "C"), 30)
    _evaluate(gateway, _r1("D", "E", "F"), 31)
    _evaluate(gateway, _r2("alfa", "beta"), 32)

    text = _r2("gamma", "delta")
    now = NOW + timedelta(minutes=33)
    turn_id = _turn(text, now)
    gateway.evaluate_productive_episode(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
        turn_id=turn_id,
        scope_reference=SCOPE,
    )

    lines = source.concept_context_lines(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
    )
    refs = source.reference_ids(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
    )
    concept = gateway.productive_concept_episode(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert concept is not None
    assert "Concepto jerárquico gobernado disponible" in lines[0]
    assert "no establece verdad" in lines[1]
    assert concept.episode_id in refs
    assert concept.concept_candidate.concept_id in refs


def test_ordinary_productive_concept_preserves_governance_boundaries() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _evaluate(gateway, _r1("A", "B", "C"), 40)
    _evaluate(gateway, _r1("D", "E", "F"), 41)
    _evaluate(gateway, _r2("alfa", "beta"), 42)
    turn_id = _evaluate(gateway, _r2("gamma", "delta"), 43)
    concept = gateway.productive_concept_episode(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert concept is not None
    assert concept.read_only is True
    assert concept.session_local is True
    assert concept.persists is False
    assert concept.creates_memory is False
    assert concept.creates_learning is False
    assert concept.modifies_world_model is False
    assert concept.modifies_personal_knowledge is False
    assert concept.executes_transfer is False
    assert concept.registers_rule is False
    assert concept.executes_actions is False
    assert concept.grants_authority is False
