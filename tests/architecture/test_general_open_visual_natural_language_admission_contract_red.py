from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionStatus,
)
from app.governed_information_sources import InformationRegion
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from app.wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)


class Runtime:
    pass


def _gateway() -> OfficialConversationGateway:
    return OfficialConversationGateway(Runtime())


def _interpret(text: str):
    return _gateway().interpret_applied_conversational_intelligence(text)


def test_red_saturn_is_admitted_as_open_visual_subject() -> None:
    interpretation = _interpret("Roby, mostrame fotos de Saturno.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    )
    assert interpretation.request.topics == frozenset()
    assert interpretation.request.query_text == "Saturno"
    assert interpretation.request.region is InformationRegion.GLOBAL
    assert interpretation.request.limit == 5


def test_red_nazca_preserves_bounded_meaningful_subject() -> None:
    interpretation = _interpret(
        "Roby, mostrame imágenes de las pistas de Nazca."
    )

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    )
    assert interpretation.request.topics == frozenset()
    assert interpretation.request.query_text == "las pistas de Nazca"


def test_red_known_james_webb_visual_behavior_stays_topic_constrained() -> None:
    interpretation = _interpret("Roby, mostrame fotos de James Webb.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.TOPIC_CONSTRAINED
    )
    assert interpretation.request.query_text == "James Webb"
    assert interpretation.matched_topics == frozenset(
        {InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}
    )


def test_red_known_nasa_visual_behavior_stays_topic_constrained() -> None:
    interpretation = _interpret("Roby, mostrame imágenes de NASA.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.RECOGNIZED
    )
    assert interpretation.request is not None
    assert interpretation.request.mode is (
        GovernedConversationalRequestMode.TOPIC_CONSTRAINED
    )
    assert InterestTopic.NASA_MISSIONS in interpretation.matched_topics


def test_red_subjectless_visual_requests_fail_closed() -> None:
    for text in ("Roby, mostrame fotos.", "Roby, mostrame imágenes."):
        interpretation = _interpret(text)
        assert interpretation.status is (
            AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
        )
        assert interpretation.request is None


def test_red_punctuation_only_visual_subject_fails_closed() -> None:
    interpretation = _interpret("Roby, mostrame fotos de ...")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


def test_red_non_visual_mostrame_remains_not_recognized() -> None:
    interpretation = _interpret("Roby, mostrame cómo funciona esto.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


def test_red_open_visual_admission_does_not_choose_provider() -> None:
    source = inspect.getsource(
        __import__(
            "app.applied_conversational_intelligence",
            fromlist=["AppliedConversationalIntelligence"],
        ).AppliedConversationalIntelligence
    )

    assert "wikimedia_commons" not in source.casefold()
    assert "WikimediaCommonsGovernedSourceAdapter" not in source


def test_red_capable_wikimedia_is_selected_only_downstream() -> None:
    gateway = _gateway()
    gateway.register_governed_source_query_adapter(
        WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
        WikimediaCommonsGovernedSourceAdapter(
            user_agent="ROBY-XI.2 contract-red@example.invalid",
            transport=lambda request, timeout: (
                b'{"query":{"pages":[]}}'
            ),
        ),
    )
    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, mostrame fotos de Saturno."
    )

    assert interpretation.request is not None
    selection = gateway.select_governed_conversational_source(
        interpretation.request
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.source is not None
    assert selection.source.source_id == "wikimedia_commons"


def test_red_without_capable_source_returns_unavailable() -> None:
    interpretation = _interpret("Roby, mostrame fotos de Saturno.")

    assert interpretation.request is not None
    selection = _gateway().select_governed_conversational_source(
        interpretation.request
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE


def test_red_gateway_remains_execution_owner() -> None:
    source = inspect.getsource(
        OfficialConversationGateway.execute_applied_conversational_intelligence
    )

    assert "interpret_applied_conversational_intelligence(text)" in source
    assert "execute_selected_governed_conversational_query(request)" in source


def test_red_no_parallel_visual_authority_is_introduced() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    classes = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }

    assert "VisualIntentRouter" not in classes
    assert "OpenVisualSubjectExtractor" not in classes
    assert "ImageSourceSelector" not in classes
    assert "ExternalImageQueryExecutor" not in classes


def test_red_admission_does_not_execute_or_date_filter_freshness() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    ).casefold()

    assert "sorted(" not in source
    assert "order_by" not in source
    assert "published_after" not in source
