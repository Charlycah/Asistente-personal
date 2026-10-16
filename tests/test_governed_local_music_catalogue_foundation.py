from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.governed_local_music_runtime_wiring import (
    GovernedLocalMusicProvisionStatus,
    build_governed_local_music_runtime_from_environment,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def test_catalogue_is_read_only_bounded_and_ignores_non_music(tmp_path: Path):
    album = tmp_path / "Album"
    album.mkdir()
    (album / "Track One.mp3").write_bytes(b"music")
    (album / "notes.txt").write_text("ignore", encoding="utf-8")

    catalogue = GovernedLocalMusicCatalogueV1(
        GovernedLocalMusicConfig(root=tmp_path)
    ).catalogue()

    assert len(catalogue.entries) == 1
    entry = catalogue.entries[0]
    assert entry.relative_path == "Album/Track One.mp3"
    assert entry.title_hint == "Track One"
    assert entry.album_hint == "Album"
    assert entry.source_reference.startswith("local-music:")
    assert (album / "Track One.mp3").read_bytes() == b"music"


def test_catalogue_rejects_escape_from_authorized_root(tmp_path: Path):
    root = tmp_path / "music"
    root.mkdir()
    catalogue = GovernedLocalMusicCatalogueV1(
        GovernedLocalMusicConfig(root=root)
    )

    try:
        catalogue.resolve_entry(Path("..") / "outside.mp3")
    except PermissionError:
        pass
    else:
        raise AssertionError("catalogue must reject paths outside authorized root")


def test_environment_without_music_root_does_not_register_capability(monkeypatch):
    monkeypatch.delenv("ROBY_LOCAL_MUSIC_ROOT", raising=False)
    registry = OfficialRuntimeCapabilityRegistry()

    wiring = build_governed_local_music_runtime_from_environment(registry)

    assert wiring.status is GovernedLocalMusicProvisionStatus.NOT_PROVISIONED
    assert "music.local_catalogue.read" not in registry.capability_names


def test_environment_provisions_read_only_catalogue_capability(
    tmp_path: Path,
    monkeypatch,
):
    (tmp_path / "Queen - Love of My Life.mp3").write_bytes(b"music")
    monkeypatch.setenv("ROBY_LOCAL_MUSIC_ROOT", str(tmp_path))
    registry = OfficialRuntimeCapabilityRegistry()

    wiring = build_governed_local_music_runtime_from_environment(registry)

    assert wiring.status is GovernedLocalMusicProvisionStatus.PROVISIONED
    registration = registry.registration_for("music.local_catalogue.read")
    assert registration is not None
    assert registration.descriptor.permission_scope.value == "read"
    assert registration.descriptor.effect_class.value == "read_only"


def test_registered_interceptor_searches_metadata_without_playback(
    tmp_path: Path,
    monkeypatch,
):
    (tmp_path / "Queen - Love of My Life.mp3").write_bytes(b"music")
    monkeypatch.setenv("ROBY_LOCAL_MUSIC_ROOT", str(tmp_path))
    registry = OfficialRuntimeCapabilityRegistry()
    wiring = build_governed_local_music_runtime_from_environment(registry)
    assert wiring.interceptor is not None

    result = wiring.interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-test",
            text="buscá música Queen",
        ),
        now=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )

    assert result is not None
    assert "Queen - Love of My Life.mp3" in result.response_text
    assert "reproduc" not in result.response_text.casefold()
