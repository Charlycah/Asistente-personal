from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from app.official_conversation_gateway import ConversationOrigin
from app.unified_brain import PostTurnReflectionObserver, UnifiedBrain
from core.governed_operational_conversation_pipeline import ConversationResponsePath


class Turn:
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = True
    retrieval_performed = False
    network_access_performed = True
    response_path = ConversationResponsePath.PROVIDER


class ConversationGatewayStub:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def submit(self, text: str, **kwargs) -> Turn:
        if self.error is not None:
            raise self.error
        return Turn()


class LegacyTurn:
    status = "completed"
    session_id = "legacy-session"


class LegacyConversationGatewayStub:
    def submit(self, text: str, **kwargs) -> LegacyTurn:
        return LegacyTurn()


def test_reflection_runs_after_turn_without_replacing_the_result() -> None:
    observer = PostTurnReflectionObserver()
    brain = UnifiedBrain(ConversationGatewayStub(), reflection_observer=observer)

    result = brain.process(
        "contenido privado",
        origin=ConversationOrigin.DESKTOP_TEXT,
        session_id="familia",
    )

    assert isinstance(result, Turn)
    assert observer.snapshot.observed_turns == 1
    assert brain.reflection_snapshot is not observer.snapshot
    assert brain.reflection_snapshot == observer.snapshot


def test_reflection_contains_only_safe_structured_metadata() -> None:
    brain = UnifiedBrain(ConversationGatewayStub())
    brain.process(
        "contenido privado",
        origin=ConversationOrigin.DESKTOP_TEXT,
        session_id="familia",
    )
    reflection = brain.reflection_snapshot.last_reflection

    assert reflection is not None
    assert {item.name for item in fields(reflection)} == {
        "status",
        "origin",
        "session_id",
        "response_path",
        "degradation_reason",
        "provider_call_performed",
        "retrieval_performed",
        "network_access_performed",
    }
    assert reflection.status == "completed"
    assert reflection.origin is ConversationOrigin.DESKTOP_TEXT
    assert reflection.session_id == "familia"
    assert reflection.response_path == "provider"
    assert reflection.degradation_reason == "not_applicable"
    assert reflection.provider_call_performed is True
    assert reflection.retrieval_performed is False
    assert reflection.network_access_performed is True
    assert "contenido privado" not in repr(reflection)


def test_failed_submission_produces_no_reflection() -> None:
    expected = RuntimeError("gateway failed")
    brain = UnifiedBrain(ConversationGatewayStub(error=expected))

    with pytest.raises(RuntimeError) as captured:
        brain.process("contenido privado")

    assert captured.value is expected
    assert brain.reflection_snapshot.observed_turns == 0
    assert brain.reflection_snapshot.last_reflection is None


def test_missing_optional_lineage_metadata_never_breaks_a_valid_turn() -> None:
    brain = UnifiedBrain(LegacyConversationGatewayStub())

    result = brain.process("mensaje compatible")
    reflection = brain.reflection_snapshot.last_reflection

    assert isinstance(result, LegacyTurn)
    assert reflection is not None
    assert reflection.response_path == "degraded"
    assert reflection.degradation_reason == "unknown"
    assert reflection.provider_call_performed is False
    assert reflection.retrieval_performed is False
    assert reflection.network_access_performed is False


def test_reflection_is_immutable_and_has_no_operational_methods() -> None:
    brain = UnifiedBrain(ConversationGatewayStub())
    brain.process("mensaje")
    reflection = brain.reflection_snapshot.last_reflection

    assert reflection is not None
    with pytest.raises(FrozenInstanceError):
        reflection.status = "changed"
    for method in ("remember", "recall", "decide", "execute", "intercept"):
        assert not hasattr(reflection, method)
