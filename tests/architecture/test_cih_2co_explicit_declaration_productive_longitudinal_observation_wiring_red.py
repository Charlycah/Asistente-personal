from __future__ import annotations

from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    ExplicitLongitudinalTopicDeclaration,
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)

_NOW = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
_OWNER = "Carlos"
_SESSION_ID = "session-cih-2co"
_TOPIC = "ROBY architecture"
_TEXT = "Quiero seguir trabajando sobre la arquitectura de ROBY."


def test_cih_2co_explicit_declaration_reaches_productive_longitudinal_observation() -> (
    None
):
    root = build_runtime_root()
    composition = root.compose()
    conversation_gateway = root.dependencies.living_conversation_source
    request = GovernedConversationPipelineRequest(
        owner=_OWNER,
        session_id=_SESSION_ID,
        text=_TEXT,
        explicit_longitudinal_topic_declaration=ExplicitLongitudinalTopicDeclaration(
            topic_key=_TOPIC,
        ),
    )
    identity = build_governed_conversation_turn_identity(request, _NOW)

    assert conversation_gateway.continuity.thread_repository.list_all() == ()

    composition.preparation.prepare_at(request, now=_NOW)

    threads = conversation_gateway.continuity.thread_repository.list_all()
    assert len(threads) == 1, (
        "the existing productive preparation boundary must laterally transport the "
        "caller-supplied explicit longitudinal topic declaration through the "
        "existing 2BT -> 2BN observation path"
    )
    thread = threads[0]
    episode = thread.latest_episode
    turn_reference = f"conversation:{_SESSION_ID}/turn:{identity.turn_id}"

    assert thread.owner == _OWNER
    assert thread.topic_key == _TOPIC
    assert episode.summary == _TEXT
    assert episode.occurred_at == _NOW
    assert episode.source_reference_ids.count(turn_reference) == 1
