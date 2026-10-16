from __future__ import annotations

from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from core.adaptive_cognition import AdaptiveCognitionStage, AdaptiveCognitionStageStatus
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning import GovernedReasoningStatus

_NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_TEXT = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."
_OWNER = "Carlos"
_SESSION_ID = "session-cih-2as"


def test_cih_2as_derived_canonical_episode_reaches_adaptive_cognition_exactly_once(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    composition = root.compose()
    request = GovernedConversationPipelineRequest(
        owner=_OWNER,
        session_id=_SESSION_ID,
        text=_TEXT,
    )
    reasoning_gateway = root.dependencies.governed_reasoning_runtime
    adaptive_gateway = root.dependencies.adaptive_cognition_runtime
    end_to_end = root.dependencies.end_to_end_conversation_runtime
    identity = build_governed_conversation_turn_identity(request, _NOW)

    entry_result = end_to_end.evaluate_turn(request, now=_NOW)
    assert entry_result.entry_kind == "comment"
    assert entry_result.entry_action == "route_to_dialogue"
    assert adaptive_gateway.snapshot.cycles == 0

    composition.preparation.prepare_at(request, now=_NOW)

    episode = reasoning_gateway.productive_episode(
        owner=_OWNER,
        session_id=_SESSION_ID,
        turn_id=identity.turn_id,
    )
    assert episode is not None
    assert episode.result.status is GovernedReasoningStatus.DERIVED
    assert reasoning_gateway.snapshot.evaluations == 1

    assert adaptive_gateway.snapshot.cycles == 1
    cycle = adaptive_gateway.manager.last_cycle
    assert cycle is not None
    assert cycle.reasoning_result_id == episode.result.result_id

    stage_statuses = {stage.stage: stage.status for stage in cycle.stages}
    assert (
        stage_statuses[AdaptiveCognitionStage.EPISODIC_MEMORY]
        is AdaptiveCognitionStageStatus.COMPLETED
    )
    assert stage_statuses[AdaptiveCognitionStage.META_REASONING] in {
        AdaptiveCognitionStageStatus.COMPLETED,
        AdaptiveCognitionStageStatus.REVIEW_REQUIRED,
    }
    assert stage_statuses[AdaptiveCognitionStage.REFLECTION] in {
        AdaptiveCognitionStageStatus.COMPLETED,
        AdaptiveCognitionStageStatus.REVIEW_REQUIRED,
    }
    assert (
        stage_statuses[AdaptiveCognitionStage.KNOWLEDGE_EVOLUTION]
        is AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )
    assert (
        stage_statuses[AdaptiveCognitionStage.EXECUTIVE_PLANNING]
        is AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )
    assert (
        stage_statuses[AdaptiveCognitionStage.EXECUTIVE_COORDINATION]
        is AdaptiveCognitionStageStatus.NOT_CONFIGURED
    )

    assert entry_result.entry_action == "route_to_dialogue"
    assert reasoning_gateway.snapshot.evaluations == 1
    assert adaptive_gateway.snapshot.cycles == 1
