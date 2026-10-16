from __future__ import annotations

import pytest

from app.runtime_root_factory import build_runtime_root
from core.living_conversation.interests import IntellectualInterestEvidenceKind


def test_cih_2bs_official_conversation_exposes_explicit_topic_declaration_input_seam(
) -> None:
    root = build_runtime_root()
    conversation_gateway = root.dependencies.living_conversation_source

    supply_explicit_longitudinal_topic_declaration = getattr(
        conversation_gateway,
        "supply_explicit_longitudinal_topic_declaration",
        None,
    )
    assert callable(supply_explicit_longitudinal_topic_declaration)

    evidence = supply_explicit_longitudinal_topic_declaration(
        owner="owner-1",
        session_id="session-1",
        turn_id="turn-1",
        topic_key="ROBY architecture",
    )

    assert evidence.topic == "ROBY architecture"
    assert evidence.kind is IntellectualInterestEvidenceKind.EXPLICIT
    assert evidence.source_reference_id == "conversation:session-1/turn:turn-1"

    with pytest.raises(ValueError, match="already be canonical"):
        supply_explicit_longitudinal_topic_declaration(
            owner="owner-1",
            session_id="session-1",
            turn_id="turn-2",
            topic_key="ROBY  architecture",
        )
