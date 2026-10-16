from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def _interpret(text: str):
    gateway = OfficialConversationGateway(Runtime())
    return gateway.interpret_applied_conversational_intelligence(text)


def test_red_mostrame_fotos_james_webb_reaches_existing_governed_request() -> None:
    interpretation = _interpret("Roby, mostrame fotos de James Webb.")

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.query_text == "James Webb"
    assert interpretation.matched_topics == frozenset(
        {InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}
    )


def test_red_mostrame_imagenes_nasa_reaches_existing_governed_request() -> None:
    interpretation = _interpret("Roby, mostrame imágenes de NASA.")

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.query_text == "NASA"
    assert InterestTopic.NASA_MISSIONS in interpretation.matched_topics


def test_red_visual_request_without_governed_topic_is_not_intercepted() -> None:
    interpretation = _interpret("Roby, mostrame fotos.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


def test_red_mostrame_without_visual_request_is_not_external_query_key() -> None:
    interpretation = _interpret("Roby, mostrame cómo funciona esto.")

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


def test_red_visual_admission_is_bounded_by_visual_request_semantics() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    )

    assert "mostrame" in source
    assert "fotos" in source
    assert ("imágenes" in source) or ("imagenes" in source)


def test_red_reuses_existing_applied_conversational_authority() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    class_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }

    assert "AppliedConversationalIntelligence" in class_names
    assert "VisualIntentRouter" not in class_names
    assert "ImageSourceSelector" not in class_names
    assert "ExternalImageQueryExecutor" not in class_names


def test_red_existing_gateway_execution_path_remains_the_owner() -> None:
    source = inspect.getsource(
        OfficialConversationGateway.execute_applied_conversational_intelligence
    )

    assert "interpret_applied_conversational_intelligence(text)" in source
    assert "execute_selected_governed_conversational_query(request)" in source


def test_red_does_not_pull_freshness_ordering_into_reachability() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    ).casefold()

    assert "sort(" not in source
    assert "sorted(" not in source
    assert "order_by" not in source
    assert "gsrsort" not in source


def test_red_does_not_modify_certified_visual_presentation_authority() -> None:
    source = Path(
        "app/desktop_external_image_presentation_composition.py"
    ).read_text(encoding="utf-8")

    assert "DesktopVisualTurnCompanion" in source
    assert "compose_external_image_turn" in source
