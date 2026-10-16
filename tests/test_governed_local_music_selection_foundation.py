from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.governed_local_music_runtime_wiring import (
    build_governed_local_music_runtime_from_environment,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
    GovernedLocalMusicSelectionV1,
    GovernedMusicSelectionStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _selection(tmp_path: Path) -> GovernedLocalMusicSelectionV1:
    return GovernedLocalMusicSelectionV1(
        GovernedLocalMusicCatalogueV1(
            GovernedLocalMusicConfig(root=tmp_path)
        )
    )


def test_unique_exact_match_is_selected_without_playback_authority(tmp_path: Path):
    (tmp_path / "Love of My Life.mp3").write_bytes(b"music")
    selection = _selection(tmp_path)

    result = selection.select("Love of My Life")

    assert result.status is GovernedMusicSelectionStatus.SELECTED
    assert result.selected is not None
    assert result.selected.filename == "Love of My Life.mp3"
    assert result.playback_authorized is False


def test_multiple_matches_fail_closed_to_human_disambiguation(tmp_path: Path):
    (tmp_path / "Queen Live.mp3").write_bytes(b"one")
    (tmp_path / "Queen Studio.flac").write_bytes(b"two")
    selection = _selection(tmp_path)

    result = selection.select("Queen")

    assert result.status is GovernedMusicSelectionStatus.AMBIGUOUS
    assert result.selected is None
    assert len(result.candidates) == 2
    assert result.playback_authorized is False


def test_missing_match_does_not_invent_selection(tmp_path: Path):
    (tmp_path / "Queen.mp3").write_bytes(b"music")
    selection = _selection(tmp_path)

    result = selection.select("Mozart")

    assert result.status is GovernedMusicSelectionStatus.NOT_FOUND
    assert result.selected is None
    assert result.candidates == ()


def test_productive_selection_reports_no_playback_authority(
    tmp_path: Path,
    monkeypatch,
):
    (tmp_path / "Love of My Life.mp3").write_bytes(b"music")
    monkeypatch.setenv("ROBY_LOCAL_MUSIC_ROOT", str(tmp_path))
    registry = OfficialRuntimeCapabilityRegistry()
    wiring = build_governed_local_music_runtime_from_environment(registry)
    assert wiring.interceptor is not None
    assert wiring.selection is not None

    result = wiring.interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-selection",
            text="seleccioná música Love of My Life",
        ),
        now=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )

    assert result is not None
    assert "Seleccioné Love of My Life.mp3" in result.response_text
    assert "no autoriza ni inicia reproducción" in result.response_text
