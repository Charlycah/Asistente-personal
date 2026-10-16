from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_source_query import GovernedSourceQueryOrder
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def _interpret(text: str):
    return OfficialConversationGateway(
        Runtime()
    ).interpret_applied_conversational_intelligence(text)


@pytest.mark.parametrize(
    "text",
    (
        "Roby, mostrame las últimas fotos de Saturno.",
        "Roby, mostrame las ultimas fotos de Saturno.",
        "Roby, mostrame las imágenes más recientes de Saturno.",
        "Roby, mostrame las imagenes mas recientes de Saturno.",
    ),
)
def test_red_admits_bounded_spanish_freshness_as_newest_first(text: str) -> None:
    interpretation = _interpret(text)

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    )
    assert interpretation.request.query_text == "Saturno"
    assert interpretation.request.order is GovernedSourceQueryOrder.NEWEST_FIRST
    assert interpretation.request.published_after is None
    assert interpretation.request.published_before is None


def test_red_freshness_control_words_do_not_contaminate_subject() -> None:
    interpretation = _interpret(
        "Roby, mostrame las imágenes más recientes de las pistas de Nazca."
    )

    assert interpretation.request is not None
    assert interpretation.request.query_text == "las pistas de Nazca"
    assert interpretation.request.order is GovernedSourceQueryOrder.NEWEST_FIRST


def test_red_known_topic_preserves_topic_authority_and_adds_only_order() -> None:
    interpretation = _interpret("Roby, mostrame las últimas fotos de James Webb.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.TOPIC_CONSTRAINED
    )
    assert interpretation.request.query_text == "James Webb"
    assert interpretation.request.order is GovernedSourceQueryOrder.NEWEST_FIRST
    assert interpretation.request.published_after is None
    assert interpretation.request.published_before is None
    assert interpretation.matched_topics == frozenset(
        {InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}
    )


def test_red_ordinary_visual_request_keeps_default_order() -> None:
    interpretation = _interpret("Roby, mostrame fotos de Saturno.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.query_text == "Saturno"
    assert interpretation.request.order is None


@pytest.mark.parametrize(
    "text",
    (
        "Roby, mostrame las últimas fotos.",
        "Roby, mostrame las imágenes más recientes.",
        "Roby, mostrame las últimas fotos de ...",
    ),
)
def test_red_subjectless_freshness_requests_fail_closed(text: str) -> None:
    interpretation = _interpret(text)

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


@pytest.mark.parametrize(
    "text",
    (
        "Roby, contame lo último de Saturno.",
        "Roby, contame algo reciente de Saturno.",
        "Roby, show me the latest photos of Saturn.",
        "Roby, show me the newest photos of Saturn.",
    ),
)
def test_red_unbounded_or_english_freshness_does_not_admit_newest_first(
    text: str,
) -> None:
    interpretation = _interpret(text)

    assert interpretation.request is None or (
        interpretation.request.order is not GovernedSourceQueryOrder.NEWEST_FIRST
    )


def test_red_aci_represents_order_without_parallel_freshness_authority() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    classes = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }

    assert "FreshnessIntentParser" not in classes
    assert "FreshnessIntentManager" not in classes
    assert "FreshnessIntentRouter" not in classes
    assert "ImageSourceSelector" not in classes
    assert "ExternalImageQueryExecutor" not in classes
    assert "sorted(" not in source
    assert "order_by" not in source
    assert "published_after=" not in source
    assert "published_before=" not in source
    assert "wikimedia_commons" not in source.casefold()
