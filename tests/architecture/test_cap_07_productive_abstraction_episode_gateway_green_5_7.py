from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)


def _rule(subject: str, resource: str, capability: str) -> str:
    return (
        f"Regla temporal: si el sistema {subject} depende exclusivamente de un recurso "
        f"{resource} para una función {capability} y ese recurso queda "
        "indisponible y no hay alternativa, "
        "entonces ese sistema pierde esa capacidad."
    )


def _turn(owner: str, session: str, text: str, now: datetime) -> str:
    request = GovernedConversationPipelineRequest(
        owner=owner,
        session_id=session,
        text=text,
    )
    return build_governed_conversation_turn_identity(request, now).turn_id


def test_green_5_gateway_wires_two_grounded_turns_into_canonical_episode() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    owner = "Carlos"
    session = "cap07-green57"
    now = datetime(2026, 8, 27, 17, 0, tzinfo=timezone.utc)
    first_text = _rule("A", "B", "C")
    second_text = _rule("D", "E", "F")

    gateway.evaluate_productive_episode(
        owner=owner,
        session_id=session,
        text=first_text,
        now=now,
        turn_id=_turn(owner, session, first_text, now),
        scope_reference=session,
    )
    second_turn = _turn(owner, session, second_text, now)
    gateway.evaluate_productive_episode(
        owner=owner,
        session_id=session,
        text=second_text,
        now=now,
        turn_id=second_turn,
        scope_reference=session,
    )

    episode = gateway.productive_abstraction_episode(
        owner=owner,
        session_id=session,
        turn_id=second_turn,
    )
    assert episode is not None
    assert episode.canonical_authority == "governed_reasoning"
    assert episode.read_only is True
    assert episode.persists is False
    assert episode.creates_memory is False
    assert episode.creates_learning is False
    assert episode.executes_transfer is False


def test_green_5_gateway_does_not_wire_abstraction_when_intake_is_disabled() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    now = datetime(2026, 8, 27, 17, 1, tzinfo=timezone.utc)
    text = _rule("A", "B", "C")
    gateway.evaluate_productive_episode(
        owner="Carlos",
        session_id="disabled",
        text=text,
        now=now,
        turn_id="turn-disabled",
        scope_reference="disabled",
        observe_productive_intake=False,
    )
    assert (
        gateway.productive_abstraction_episode(
            owner="Carlos",
            session_id="disabled",
            turn_id="turn-disabled",
        )
        is None
    )


def test_green_6_source_exposes_same_turn_abstraction_as_references_and_context() -> (
    None
):
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    owner = "Carlos"
    session = "cap07-source"
    now = datetime(2026, 8, 27, 17, 2, tzinfo=timezone.utc)
    first_text = _rule("A", "B", "C")
    second_text = _rule("D", "E", "F")

    for text in (first_text, second_text):
        gateway.evaluate_productive_episode(
            owner=owner,
            session_id=session,
            text=text,
            now=now,
            turn_id=_turn(owner, session, text, now),
            scope_reference=session,
        )

    refs = source.reference_ids(
        owner=owner,
        session_id=session,
        text=second_text,
        now=now,
    )
    lines = source.abstraction_context_lines(
        owner=owner,
        session_id=session,
        text=second_text,
        now=now,
    )

    assert any(ref.startswith("productive-abstraction:") for ref in refs)
    assert len(lines) == 2
    assert "Abstracción relacional gobernada disponible" in lines[0]
    assert "no establece verdad" in lines[1]


def test_green_6_context_is_exact_turn_scoped() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    owner = "Carlos"
    session = "cap07-turn-scope"
    now = datetime(2026, 8, 27, 17, 3, tzinfo=timezone.utc)
    first_text = _rule("A", "B", "C")
    second_text = _rule("D", "E", "F")

    for text in (first_text, second_text):
        gateway.evaluate_productive_episode(
            owner=owner,
            session_id=session,
            text=text,
            now=now,
            turn_id=_turn(owner, session, text, now),
            scope_reference=session,
        )

    assert (
        source.abstraction_context_lines(
            owner=owner,
            session_id=session,
            text=first_text,
            now=now,
        )
        == ()
    )


def test_green_7_existing_source_reuses_prepared_episode_without_double_admission() -> (
    None
):
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    owner = "Carlos"
    session = "cap07-no-double"
    now = datetime(2026, 8, 27, 17, 4, tzinfo=timezone.utc)
    first_text = _rule("A", "B", "C")
    second_text = _rule("D", "E", "F")

    for text in (first_text, second_text):
        gateway.evaluate_productive_episode(
            owner=owner,
            session_id=session,
            text=text,
            now=now,
            turn_id=_turn(owner, session, text, now),
            scope_reference=session,
        )

    before = gateway.productive_abstraction_episode(
        owner=owner,
        session_id=session,
        turn_id=_turn(owner, session, second_text, now),
    )
    source(owner=owner, session_id=session, text=second_text, now=now)
    after = gateway.productive_abstraction_episode(
        owner=owner,
        session_id=session,
        turn_id=_turn(owner, session, second_text, now),
    )
    assert before is not None
    assert after == before
