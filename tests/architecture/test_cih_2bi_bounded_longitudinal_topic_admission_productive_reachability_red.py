from __future__ import annotations

from app.runtime_root_factory import build_runtime_root
from core.living_conversation.interests import (
    SharedIntellectualInterest,
    SharedIntellectualInterestStrength,
)


def _explicit_governed_topic_evidence() -> SharedIntellectualInterest:
    return SharedIntellectualInterest(
        topic="ROBY governed architecture",
        score=0.94,
        strength=SharedIntellectualInterestStrength.CORE,
        evidence_count=2,
        source_reference_ids=(
            "conversation:cih-2bi-session/turn:explicit-topic-1",
            "conversation:cih-2bi-session/turn:explicit-topic-2",
        ),
        explicit=True,
    )


def test_cih_2bi_official_conversation_exposes_bounded_topic_admission_seam() -> None:
    root = build_runtime_root()
    conversation_gateway = root.dependencies.living_conversation_source

    admit_longitudinal_topic = getattr(
        conversation_gateway,
        "admit_longitudinal_topic",
        None,
    )
    assert callable(admit_longitudinal_topic), (
        "official conversation runtime must expose one bounded longitudinal "
        "topic-admission seam before governed explicit topic evidence may reach "
        "ConversationEpisode.topic_key without semantic reinference"
    )

    evidence = _explicit_governed_topic_evidence()
    admitted = admit_longitudinal_topic(
        evidence=evidence,
        topic_key=evidence.topic,
    )
    assert admitted.status.value == "admitted"
    assert admitted.topic_key == evidence.topic
    assert admitted.source_reference_ids == evidence.source_reference_ids

    absent = admit_longitudinal_topic(evidence=None, topic_key=None)
    assert absent.status.value == "abstain"
    assert absent.topic_key is None
    assert absent.source_reference_ids == ()

    mismatched = admit_longitudinal_topic(
        evidence=evidence,
        topic_key="ROBY architecture",
    )
    assert mismatched.status.value == "abstain"
    assert mismatched.topic_key is None
