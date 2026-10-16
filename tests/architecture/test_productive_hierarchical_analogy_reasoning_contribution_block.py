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

NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
OWNER = "Carlos"
SESSION = "productive-hierarchical-analogy"
SCOPE = "scope:productive-hierarchical-analogy"


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


def _evaluate(
    gateway: OfficialGovernedReasoningRuntimeGateway,
    text: str,
    minute: int,
    *,
    session_id: str = SESSION,
    scope: str = SCOPE,
) -> tuple[str, datetime]:
    now = NOW + timedelta(minutes=minute)
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=session_id,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, now).turn_id
    gateway.evaluate_productive_episode(
        owner=OWNER,
        session_id=session_id,
        text=text,
        now=now,
        turn_id=turn_id,
        scope_reference=scope,
    )
    return turn_id, now


def _build_first_concept(
    gateway: OfficialGovernedReasoningRuntimeGateway,
) -> str:
    _evaluate(gateway, _r1("A", "B", "C"), 0)
    _evaluate(gateway, _r1("D", "E", "F"), 1)
    _evaluate(gateway, _r2("alfa", "beta"), 2)
    turn_id, _ = _evaluate(gateway, _r2("gamma", "delta"), 3)
    assert (
        gateway.productive_concept_episode(
            owner=OWNER,
            session_id=SESSION,
            turn_id=turn_id,
        )
        is not None
    )
    return turn_id


def test_second_ordinary_hcc_concept_reaches_productive_analogy() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    first_turn = _build_first_concept(gateway)
    assert (
        gateway.productive_hierarchical_analogy_candidate(
            owner=OWNER,
            session_id=SESSION,
            turn_id=first_turn,
        )
        is None
    )

    turn_id, _ = _evaluate(gateway, _r1("G", "H", "I"), 4)
    analogy = gateway.productive_hierarchical_analogy_candidate(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert analogy is not None
    assert analogy.source_concept_episode_id != analogy.target_concept_episode_id
    assert len(analogy.component_correspondences) == 2


def test_productive_analogy_reaches_same_turn_reasoning_source() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    _build_first_concept(gateway)
    text = _r1("G", "H", "I")
    turn_id, now = _evaluate(gateway, text, 4)

    lines = source.hierarchical_analogy_context_lines(
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
    analogy = gateway.productive_hierarchical_analogy_candidate(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert analogy is not None
    assert "Analogía jerárquica gobernada disponible" in lines[0]
    assert "no establece verdad" in lines[1]
    assert analogy.source_fingerprint in refs
    assert analogy.source_concept_episode_id in refs
    assert analogy.target_concept_episode_id in refs


def test_same_session_scope_history_is_required() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _build_first_concept(gateway)

    other = "other-session"
    _evaluate(gateway, _r1("J", "K", "L"), 10, session_id=other)
    _evaluate(gateway, _r1("M", "N", "O"), 11, session_id=other)
    _evaluate(gateway, _r2("uno", "dos"), 12, session_id=other)
    turn_id, _ = _evaluate(
        gateway,
        _r2("tres", "cuatro"),
        13,
        session_id=other,
    )
    assert (
        gateway.productive_hierarchical_analogy_candidate(
            owner=OWNER,
            session_id=other,
            turn_id=turn_id,
        )
        is None
    )


def test_non_matching_concept_is_not_exposed_as_productive_analogy() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _build_first_concept(gateway)
    # A same-scope R1 update still composes the certified R1/R2 topology and matches.
    # A different scope starts its own concept history.
    other_scope = "scope:isolated"
    _evaluate(gateway, _r1("P", "Q", "R"), 20, scope=other_scope)
    _evaluate(gateway, _r1("S", "T", "U"), 21, scope=other_scope)
    _evaluate(gateway, _r2("cinco", "seis"), 22, scope=other_scope)
    turn_id, _ = _evaluate(
        gateway,
        _r2("siete", "ocho"),
        23,
        scope=other_scope,
    )
    assert (
        gateway.productive_hierarchical_analogy_candidate(
            owner=OWNER,
            session_id=SESSION,
            turn_id=turn_id,
        )
        is None
    )


def test_productive_analogy_preserves_non_authoritative_boundaries() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _build_first_concept(gateway)
    turn_id, _ = _evaluate(gateway, _r1("G", "H", "I"), 4)
    analogy = gateway.productive_hierarchical_analogy_candidate(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert analogy is not None
    assert analogy.read_only is True
    assert analogy.session_local is True
    assert analogy.persists is False
    assert analogy.creates_memory is False
    assert analogy.creates_learning is False
    assert analogy.establishes_truth is False
    assert analogy.authorizes_inference is False
    assert analogy.executes_transfer is False
    assert analogy.registers_rule is False
    assert analogy.executes_actions is False
    assert analogy.grants_authority is False
