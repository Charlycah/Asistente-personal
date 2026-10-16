from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    ExplicitLongitudinalTopicDeclaration,
    GovernedConversationPipelineRequest,
)

_NOW = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
_OWNER = "Carlos"
_SESSION_ID = "session-cih-2dd"
_TOPIC = "ROBY architecture"
_PRIOR_SUMMARY = "Ayer dejamos definida la autoridad longitudinal de conversación."
_CURRENT_TEXT = "Quiero continuar con la arquitectura de ROBY."


def test_cih_2dd_strict_prior_longitudinal_history_reaches_context_read_only() -> None:
    root = build_runtime_root()
    composition = root.compose()
    conversation_gateway = root.dependencies.living_conversation_source

    prior_thread = conversation_gateway.record_productive_episode(
        owner=_OWNER,
        session_id=_SESSION_ID,
        topic_key=_TOPIC,
        summary=_PRIOR_SUMMARY,
        source_reference_ids=("conversation:prior-session/turn:prior-turn",),
        occurred_at=_NOW - timedelta(days=1),
    )
    prior_episode_ids = tuple(episode.episode_id for episode in prior_thread.episodes)

    request = GovernedConversationPipelineRequest(
        owner=_OWNER,
        session_id=_SESSION_ID,
        text=_CURRENT_TEXT,
        explicit_longitudinal_topic_declaration=ExplicitLongitudinalTopicDeclaration(
            topic_key=_TOPIC,
        ),
    )

    prepared = composition.preparation.prepare_at(request, now=_NOW)
    inference_request = prepared.inference_request

    assert _PRIOR_SUMMARY in inference_request.prompt, (
        "the existing Context authority must receive strict-prior retained history "
        "for the caller-supplied exact longitudinal topic before the current episode "
        "is recorded"
    )
    assert "Contexto longitudinal previo" in inference_request.prompt
    assert f"Usuario: {_PRIOR_SUMMARY}" not in inference_request.prompt
    assert f"ROBY: {_PRIOR_SUMMARY}" not in inference_request.prompt
    assert "conversation_context_input_turns" not in inference_request.metadata, (
        "longitudinal context must remain distinct from caller-supplied recent_context"
    )

    threads = conversation_gateway.continuity.thread_repository.list_all()
    assert len(threads) == 1
    thread = threads[0]
    assert thread.topic_key == _TOPIC
    assert (
        tuple(episode.episode_id for episode in thread.episodes[:-1])
        == prior_episode_ids
    )
    assert thread.latest_episode.summary == _CURRENT_TEXT
