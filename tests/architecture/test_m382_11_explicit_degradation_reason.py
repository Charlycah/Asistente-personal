from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.official_conversation_gateway import ConversationOrigin
from app.unified_brain import PostTurnReflectionObserver
from core.end_to_end_local_conversation import (
    JsonLinesLocalConversationJournal,
    LocalConversationTurn,
)
from core.governed_operational_conversation_pipeline import (
    ConversationDegradationReason,
    ConversationResponsePath,
)


def _turn(reason: ConversationDegradationReason) -> SimpleNamespace:
    return SimpleNamespace(
        status="failed",
        session_id="familia",
        response_path=ConversationResponsePath.DEGRADED,
        degradation_reason=reason,
        provider_call_performed=False,
        retrieval_performed=False,
        network_access_performed=False,
    )


def test_reflection_observes_explicit_degradation_reason() -> None:
    observer = PostTurnReflectionObserver()

    reflection = observer.observe(
        _turn(ConversationDegradationReason.TURN_FAILED_SAFELY),
        origin=ConversationOrigin.INTERNAL,
        session_id=None,
    )

    assert reflection.response_path == "degraded"
    assert reflection.degradation_reason == "turn_failed_safely"


def test_historical_turn_defaults_to_unknown_degradation_reason() -> None:
    historical = LocalConversationTurn(
        owner="Carlos",
        session_id="familia",
        sequence=1,
        user_text="mensaje",
        response_text="",
        status="failed",
        pipeline_result_id="pipeline-id",
        operational_response_id="response-id",
        provider_call_performed=False,
        retrieval_performed=False,
        network_access_performed=False,
        rationale=("historical",),
    )

    assert historical.degradation_reason is ConversationDegradationReason.UNKNOWN


def test_degradation_reason_is_persisted_without_changing_turn_identity() -> None:
    model_source = getsource(LocalConversationTurn._identity_payload)
    journal_source = getsource(JsonLinesLocalConversationJournal.append)

    assert "degradation_reason" not in model_source
    assert '"degradation_reason": turn.degradation_reason.value' in journal_source


def test_pipeline_assigns_reasons_without_message_text_heuristics() -> None:
    from core.governed_operational_conversation_pipeline.pipeline import (
        GovernedOperationalConversationPipeline,
    )

    source = getsource(GovernedOperationalConversationPipeline)

    for reason in ConversationDegradationReason:
        assert reason.name in source or reason is ConversationDegradationReason.UNKNOWN
    assert ".text" not in getsource(PostTurnReflectionObserver.observe)
