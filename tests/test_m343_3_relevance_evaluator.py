from __future__ import annotations

import ast
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.relevance_evaluator import (
    RelevanceCandidate,
    RelevanceEvaluator,
    RelevanceRecipient,
)


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()


def test_personal_profiles_distinguish_boca_and_river() -> None:
    center = PersonalInterestCenter()

    assert center.interested_people(InterestTopic.BOCA_JUNIORS) == ("Carlos",)
    assert center.interested_people(InterestTopic.RIVER_PLATE) == ("Cristina",)


def test_technology_and_programming_are_carlos_interests() -> None:
    center = PersonalInterestCenter()

    for topic in (
        InterestTopic.TECHNOLOGY,
        InterestTopic.ARTIFICIAL_INTELLIGENCE,
        InterestTopic.PROGRAMMING,
        InterestTopic.PROGRAMMING_LANGUAGES,
        InterestTopic.SOFTWARE_ENGINEERING,
    ):
        assert center.interested_people(topic) == ("Carlos",)


def test_free_caba_cultural_activity_is_relevant_to_both() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    candidate = RelevanceCandidate(
        title="Concierto gratuito de la Filarmónica",
        topics=frozenset(
            {InterestTopic.CULTURE_CABA, InterestTopic.MUSIC}
        ),
        location="CABA",
        is_free=True,
        time_sensitive=True,
        importance=10,
    )

    decision = evaluator.evaluate(candidate)

    assert decision.recipient is RelevanceRecipient.BOTH
    assert decision.should_share is True
    assert decision.should_interrupt is True
    assert decision.scores == {"Carlos": 95, "Cristina": 95}


def test_boca_news_is_only_for_carlos() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Boca juega esta noche",
            topics=frozenset({InterestTopic.BOCA_JUNIORS}),
            time_sensitive=True,
            importance=10,
        )
    )

    assert decision.recipient is RelevanceRecipient.CARLOS
    assert decision.scores == {"Carlos": 70, "Cristina": 0}
    assert decision.should_interrupt is False


def test_river_news_is_only_for_cristina() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="River confirmó su próximo partido",
            topics=frozenset({InterestTopic.RIVER_PLATE}),
            importance=5,
        )
    )

    assert decision.recipient is RelevanceRecipient.CRISTINA
    assert decision.should_share is True


def test_unrelated_information_is_not_shared() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Información sin relación personal",
            topics=frozenset(),
            importance=20,
        )
    )

    assert decision.recipient is RelevanceRecipient.NOBODY
    assert decision.should_share is False
    assert decision.should_interrupt is False


def test_gateway_exposes_single_relevance_authority() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    assert gateway.relevance_evaluator.schema_version == "m343.3"
    decision = gateway.evaluate_relevance(
        RelevanceCandidate(
            title="Nueva versión de un lenguaje",
            topics=frozenset({InterestTopic.PROGRAMMING_LANGUAGES}),
            importance=10,
        )
    )
    assert decision.recipient is RelevanceRecipient.CARLOS


def test_official_gateway_is_only_production_composition_root() -> None:
    constructors: list[str] = []
    for root in ("app", "application", "core", "domain", "infrastructure"):
        for path in Path(root).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "RelevanceEvaluator"
                ):
                    constructors.append(path.as_posix())

    assert constructors == ["app/official_conversation_gateway.py"]
