from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.governed_local_music_runtime_wiring import (
    GovernedLocalMusicCatalogueInterceptionPort,
    build_governed_local_music_runtime_from_environment,
)
from app.local_music_playback import LocalCommandMusicPlaybackExecutor
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
    GovernedLocalMusicPlaybackAuthorizationV1,
    GovernedLocalMusicSelectionV1,
    GovernedMusicPlaybackAuthorizationStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class RecordingRunner:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        return object()


def _components(tmp_path: Path):
    catalogue = GovernedLocalMusicCatalogueV1(
        GovernedLocalMusicConfig(root=tmp_path)
    )
    selection = GovernedLocalMusicSelectionV1(catalogue)
    authorization = GovernedLocalMusicPlaybackAuthorizationV1()
    return catalogue, selection, authorization


def test_selection_alone_never_authorizes_playback(tmp_path: Path):
    (tmp_path / "Track.mp3").write_bytes(b"music")
    _, selection, authorization = _components(tmp_path)

    selected = selection.select("Track")
    denied = authorization.authorize(
        selected,
        explicit_human_request=False,
    )

    assert denied.status is GovernedMusicPlaybackAuthorizationStatus.DENIED
    assert denied.authorized is False


def test_explicit_human_request_authorizes_unique_selection(tmp_path: Path):
    (tmp_path / "Track.mp3").write_bytes(b"music")
    _, selection, authorization = _components(tmp_path)

    selected = selection.select("Track")
    result = authorization.authorize(
        selected,
        explicit_human_request=True,
    )

    assert result.status is GovernedMusicPlaybackAuthorizationStatus.AUTHORIZED
    assert result.authorized is True
    assert result.entry_id == selected.selected.entry_id


def test_playback_executor_receives_only_resolved_selected_file(tmp_path: Path):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    runner = RecordingRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)

    result = executor.play(track)

    assert result.started is True
    assert runner.calls == [["player", str(track.resolve())]]


def test_productive_playback_requires_explicit_command_and_unique_selection(
    tmp_path: Path,
):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    catalogue, selection, authorization = _components(tmp_path)
    runner = RecordingRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)
    interceptor = GovernedLocalMusicCatalogueInterceptionPort(
        catalogue,
        selection,
        authorization,
        executor,
    )

    result = interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-playback",
            text="reproducí música Track",
        ),
        now=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )

    assert result is not None
    assert result.response_text == "Reproduciendo Track.mp3."
    assert runner.calls == [["player", str(track.resolve())]]


def test_ambiguous_playback_fails_closed_without_execution(tmp_path: Path):
    (tmp_path / "Queen Live.mp3").write_bytes(b"one")
    (tmp_path / "Queen Studio.mp3").write_bytes(b"two")
    catalogue, selection, authorization = _components(tmp_path)
    runner = RecordingRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)
    interceptor = GovernedLocalMusicCatalogueInterceptionPort(
        catalogue,
        selection,
        authorization,
        executor,
    )

    result = interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-playback",
            text="reproducí música Queen",
        ),
        now=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )

    assert result is not None
    assert "varias opciones" in result.response_text
    assert runner.calls == []


def test_playback_capability_registers_only_when_command_is_configured(
    tmp_path: Path,
    monkeypatch,
):
    (tmp_path / "Track.mp3").write_bytes(b"music")
    monkeypatch.setenv("ROBY_LOCAL_MUSIC_ROOT", str(tmp_path))
    monkeypatch.delenv("ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND", raising=False)
    registry = OfficialRuntimeCapabilityRegistry()

    build_governed_local_music_runtime_from_environment(registry)

    assert "music.local_catalogue.read" in registry.capability_names
    assert "music.local_playback.execute" not in registry.capability_names

    monkeypatch.setenv("ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND", "player")
    registry = OfficialRuntimeCapabilityRegistry()
    build_governed_local_music_runtime_from_environment(registry)

    assert "music.local_playback.execute" in registry.capability_names
    registration = registry.registration_for("music.local_playback.execute")
    assert registration is not None
    assert registration.descriptor.permission_scope.value == "device"
    assert registration.descriptor.effect_class.value == "state_changing"
