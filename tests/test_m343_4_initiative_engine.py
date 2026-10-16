from __future__ import annotations

import ast
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_initiative_engine import (
    InitiativeContext,
    InitiativeDisposition,
    PersonalInitiativeEngine,
)
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.relevance_evaluator import RelevanceCandidate, RelevanceEvaluator


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()


def _engine() -> PersonalInitiativeEngine:
    return PersonalInitiativeEngine(RelevanceEvaluator(PersonalInterestCenter()))


def test_irrelevant_candidate_is_discarded() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(title="Dato ajeno", topics=frozenset())
    )

    assert proposal.disposition is InitiativeDisposition.DISCARD
    assert proposal.should_speak is False


def test_boca_candidate_initiates_only_for_carlos() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="Boca juega mañana",
            topics=frozenset({InterestTopic.BOCA_JUNIORS}),
            importance=10,
        )
    )

    assert proposal.recipient.value == "carlos"
    assert proposal.disposition is InitiativeDisposition.INITIATE
    assert proposal.should_speak is True


def test_river_candidate_initiates_only_for_cristina() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="River confirmó el equipo",
            topics=frozenset({InterestTopic.RIVER_PLATE}),
            importance=10,
        )
    )

    assert proposal.recipient.value == "cristina"
    assert proposal.disposition is InitiativeDisposition.INITIATE


def test_high_relevance_candidate_can_interrupt() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="Concierto gratuito hoy en CABA",
            topics=frozenset({InterestTopic.CULTURE_CABA, InterestTopic.MUSIC}),
            location="CABA",
            is_free=True,
            time_sensitive=True,
            importance=10,
        )
    )

    assert proposal.recipient.value == "both"
    assert proposal.disposition is InitiativeDisposition.INTERRUPT
    assert proposal.priority == 95


def test_quiet_hours_defer_even_high_relevance() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="Actividad cultural urgente",
            topics=frozenset({InterestTopic.CULTURE_CABA, InterestTopic.MUSIC}),
            location="CABA",
            is_free=True,
            time_sensitive=True,
            importance=10,
        ),
        context=InitiativeContext(quiet_hours=True),
    )

    assert proposal.disposition is InitiativeDisposition.DEFER
    assert proposal.should_speak is False
    assert "quiet_hours" in proposal.reasons


def test_recent_intervention_prevents_repetition() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="Nueva versión de Python",
            topics=frozenset({InterestTopic.PROGRAMMING_LANGUAGES}),
            importance=10,
        ),
        context=InitiativeContext(recently_intervened=True),
    )

    assert proposal.disposition is InitiativeDisposition.DEFER
    assert "recent_intervention" in proposal.reasons


def test_active_conversation_defers_non_interrupting_candidate() -> None:
    proposal = _engine().propose(
        RelevanceCandidate(
            title="Boca juega mañana",
            topics=frozenset({InterestTopic.BOCA_JUNIORS}),
            importance=10,
        ),
        context=InitiativeContext(conversation_active=True),
    )

    assert proposal.disposition is InitiativeDisposition.DEFER
    assert "conversation_active" in proposal.reasons


def test_gateway_exposes_non_executing_initiative_engine() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    assert gateway.initiative_engine.schema_version == "m343.4"
    assert gateway.initiative_engine.execution_enabled is False
    proposal = gateway.propose_initiative(
        RelevanceCandidate(
            title="Boca juega mañana",
            topics=frozenset({InterestTopic.BOCA_JUNIORS}),
            importance=10,
        )
    )
    assert proposal.disposition is InitiativeDisposition.INITIATE


def test_official_gateway_is_only_production_composition_root() -> None:
    constructors: list[str] = []
    for root in ("app", "application", "core", "domain", "infrastructure"):
        for path in Path(root).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "PersonalInitiativeEngine"
                ):
                    constructors.append(path.as_posix())

    assert constructors == ["app/official_conversation_gateway.py"]
