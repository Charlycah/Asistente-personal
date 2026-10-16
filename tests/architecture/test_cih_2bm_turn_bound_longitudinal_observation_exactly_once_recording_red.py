from __future__ import annotations

from app.runtime_root_factory import build_runtime_root


def test_cih_2bm_official_conversation_exposes_turn_bound_observation_seam() -> None:
    root = build_runtime_root()
    conversation_gateway = root.dependencies.living_conversation_source

    observe_longitudinal_productive_turn = getattr(
        conversation_gateway,
        "observe_longitudinal_productive_turn",
        None,
    )
    assert callable(observe_longitudinal_productive_turn), (
        "official conversation runtime must expose one turn-bound longitudinal "
        "observation seam before ADMITTED topic identity may record exactly one "
        "ConversationEpisode for one canonical productive turn"
    )
