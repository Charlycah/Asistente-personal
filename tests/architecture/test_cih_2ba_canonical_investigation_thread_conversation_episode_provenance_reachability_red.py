from __future__ import annotations

from datetime import datetime, timezone

from app.governed_long_horizon_investigation_continuity import (
    GovernedLongHorizonInvestigationContinuityV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.runtime_root_factory import build_runtime_root

_NOW = datetime(2026, 9, 14, 20, 0, tzinfo=timezone.utc)
_OWNER = "owner-1"
_SESSION_ID = "cih-2ba-session"


def _canonical_investigation_checkpoint():
    state = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1()
        .start(
            originating_reasoning_id="reasoning-episode-cih-2ba",
            source_reference="explicit-investigation-source-cih-2ba",
            world_snapshot_id="world-snapshot-cih-2ba",
            initial_requirement_id="requirement-cih-2ba",
        )
        .state
    )
    return GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        state,
        pause_reason="awaiting_future_governed_evidence",
    )


def test_cih_2ba_canonical_investigation_thread_reaches_conversation_episode_provenance(
) -> None:
    checkpoint = _canonical_investigation_checkpoint()
    root = build_runtime_root()
    conversation_gateway = root.dependencies.living_conversation_source

    record_productive_episode = getattr(
        conversation_gateway,
        "record_productive_episode",
        None,
    )
    assert callable(record_productive_episode), (
        "official conversation runtime must productively reuse the existing "
        "LongitudinalConversationContinuity before CIH-2BA may transport "
        "canonical investigation-thread provenance"
    )

    thread = record_productive_episode(
        owner=_OWNER,
        session_id=_SESSION_ID,
        topic_key="governed-investigation-cih-2ba",
        summary="Continue the explicitly related governed investigation context.",
        source_reference_ids=(checkpoint.thread_id,),
        occurred_at=_NOW,
    )
    episode = thread.latest_episode

    assert checkpoint.thread_id.startswith("investigation-thread-")
    assert checkpoint.thread_id in episode.source_reference_ids
    assert episode.source_reference_ids.count(checkpoint.thread_id) == 1
    assert thread.thread_id != checkpoint.thread_id

    # Provenance remains passive: recording conversation continuity must not mutate
    # the canonical Investigation artifact or imply resume/authorization semantics.
    assert checkpoint.read_only is True
    assert checkpoint.passive is True
    assert checkpoint.invokes_capabilities is False
    assert checkpoint.executes_actions is False
    assert checkpoint.modifies_memory is False
    assert checkpoint.modifies_planning is False
    assert checkpoint.performs_reasoning is False
    assert checkpoint.grants_authority is False
