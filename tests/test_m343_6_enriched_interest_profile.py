from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import (
    InterestDomain,
    InterestPreference,
    InterestPriority,
    InterestTopic,
    PersonalInterestCenter,
    PersonalInterestProfile,
)
from app.relevance_evaluator import (
    RelevanceCandidate,
    RelevanceEvaluator,
    RelevanceRecipient,
)


def test_carlos_has_high_priority_hard_science_fiction_interest() -> None:
    profile = PersonalInterestCenter().profile_for("Carlos")

    preference = profile.preference_for(InterestTopic.HARD_SCIENCE_FICTION)

    assert preference is not None
    assert preference.domain is InterestDomain.AUDIOVISUAL
    assert preference.priority is InterestPriority.VERY_HIGH
    assert "scientifically_plausible" in preference.tags


def test_audiovisual_profile_covers_movies_series_and_releases() -> None:
    profile = PersonalInterestCenter().profile_for("Carlos")

    assert {
        InterestTopic.CINEMA,
        InterestTopic.SERIES,
        InterestTopic.RELEASES,
        InterestTopic.SCIENCE_FICTION,
        InterestTopic.HARD_SCIENCE_FICTION,
    }.issubset(profile.topics)


def test_healthy_eating_is_shared_household_interest() -> None:
    center = PersonalInterestCenter()

    assert center.interested_people(InterestTopic.HEALTHY_EATING) == (
        "Carlos",
        "Cristina",
    )


def test_cristina_has_healthy_recipe_and_mediterranean_preferences() -> None:
    profile = PersonalInterestCenter().profile_for("Cristina")

    assert profile.priority_for(InterestTopic.HEALTHY_RECIPES) is (
        InterestPriority.HIGH
    )
    assert profile.priority_for(InterestTopic.MEDITERRANEAN_CUISINE) is (
        InterestPriority.HIGH
    )


def test_legacy_topic_without_metadata_keeps_medium_priority() -> None:
    profile = PersonalInterestCenter().profile_for("Carlos")

    assert profile.priority_for(InterestTopic.BOCA_JUNIORS) is (
        InterestPriority.MEDIUM
    )


def test_preferences_must_reference_existing_profile_topics() -> None:
    with pytest.raises(ValueError, match="reference profile topics"):
        PersonalInterestProfile(
            person="Test",
            topics=frozenset({InterestTopic.CINEMA}),
            preferences=(
                InterestPreference(
                    topic=InterestTopic.HEALTHY_EATING,
                    domain=InterestDomain.HEALTH_AND_WELLBEING,
                ),
            ),
        )


def test_relevance_evaluator_uses_new_topics_without_parallel_authority() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    candidate = RelevanceCandidate(
        title="Estreno confirmado de ciencia ficción dura",
        topics=frozenset(
            {
                InterestTopic.RELEASES,
                InterestTopic.HARD_SCIENCE_FICTION,
            }
        ),
    )

    decision = evaluator.evaluate(candidate)

    assert decision.recipient is RelevanceRecipient.CARLOS
    assert decision.should_share is True


def test_shared_healthy_information_is_relevant_to_both_people() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    candidate = RelevanceCandidate(
        title="Nueva guía pública de alimentación saludable",
        topics=frozenset(
            {
                InterestTopic.HEALTHY_EATING,
                InterestTopic.EVIDENCE_BASED_NUTRITION,
            }
        ),
    )

    decision = evaluator.evaluate(candidate)

    assert decision.recipient is RelevanceRecipient.BOTH


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()


def test_gateway_exposes_only_the_enriched_canonical_profile() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    assert gateway.personal_interest_center.schema_version == "m343.2"
    assert gateway.personal_interest_center.profile_for("Carlos").preference_for(
        InterestTopic.HARD_SCIENCE_FICTION
    )


def test_single_interest_center_composition_root_remains_in_gateway() -> None:
    source = Path("app/official_conversation_gateway.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    constructors = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "PersonalInterestCenter"
    ]

    assert len(constructors) == 1
