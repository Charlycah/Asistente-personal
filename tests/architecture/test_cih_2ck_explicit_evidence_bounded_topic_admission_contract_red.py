from __future__ import annotations

from app.runtime_root_factory import build_runtime_root
from core.living_conversation.interests import (
    IntellectualInterestEvidence,
    IntellectualInterestEvidenceKind,
)


def test_cih_2ck_bounded_topic_admission_accepts_only_explicit_topic_evidence() -> None:
    root = build_runtime_root()
    conversation_gateway = root.dependencies.living_conversation_source

    explicit = conversation_gateway.supply_explicit_longitudinal_topic_declaration(
        owner="owner-1",
        session_id="session-1",
        turn_id="turn-1",
        topic_key="ROBY architecture",
    )
    admitted = conversation_gateway.admit_longitudinal_topic(
        evidence=explicit,
        topic_key=explicit.topic,
    )

    assert admitted.status.value == "admitted"
    assert admitted.topic_key == explicit.topic
    assert admitted.source_reference_ids == (explicit.source_reference_id,)

    non_explicit = IntellectualInterestEvidence(
        topic="ROBY architecture",
        kind=IntellectualInterestEvidenceKind.SYSTEM_OBSERVATION,
        confidence=1.0,
        source_reference_id="conversation:session-1/turn:turn-2",
        note="not_an_explicit_longitudinal_topic_declaration",
    )
    abstained = conversation_gateway.admit_longitudinal_topic(
        evidence=non_explicit,
        topic_key=non_explicit.topic,
    )

    assert abstained.status.value == "abstain"
    assert abstained.topic_key is None
    assert abstained.source_reference_ids == ()
