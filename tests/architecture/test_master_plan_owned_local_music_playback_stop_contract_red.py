from __future__ import annotations

import inspect
import typing
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path

from app.governed_local_music_runtime_wiring import (
    GovernedLocalMusicCatalogueInterceptionPort,
)
from app.local_music_playback import (
    LocalCommandMusicPlaybackExecutor,
    LocalMusicPlaybackExecution,
)
from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
    GovernedLocalMusicPlaybackAuthorizationV1,
    GovernedLocalMusicSelectionV1,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class ControllableProcess:
    def __init__(self) -> None:
        self.terminate_calls = 0

    def terminate(self) -> None:
        self.terminate_calls += 1


class ControllableRunner:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.processes: list[ControllableProcess] = []

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        process = ControllableProcess()
        self.processes.append(process)
        return process


def _interceptor(
    tmp_path: Path,
    executor: LocalCommandMusicPlaybackExecutor,
) -> GovernedLocalMusicCatalogueInterceptionPort:
    catalogue = GovernedLocalMusicCatalogueV1(
        GovernedLocalMusicConfig(root=tmp_path)
    )
    return GovernedLocalMusicCatalogueInterceptionPort(
        catalogue,
        GovernedLocalMusicSelectionV1(catalogue),
        GovernedLocalMusicPlaybackAuthorizationV1(),
        executor,
    )


def test_red_1_executor_retains_exact_runner_process_handle(tmp_path: Path):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)

    execution = executor.play(track)

    assert runner.processes
    assert getattr(executor, "_owned_process", None) is runner.processes[0]
    assert execution.started is True


def test_red_2_executor_exposes_bounded_stop_result_and_owned_stop():
    stop = getattr(LocalCommandMusicPlaybackExecutor, "stop", None)

    assert callable(stop)
    annotation = inspect.signature(stop).return_annotation
    assert annotation is not inspect.Signature.empty
    assert "stop" in str(annotation).casefold()
    resolved = typing.get_type_hints(stop)["return"]
    assert {"stopped", "had_owned_process"} <= {
        item.name for item in fields(resolved)
    }


def test_red_3_stop_targets_only_the_retained_owned_handle(tmp_path: Path):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)

    executor.play(track)
    owned = runner.processes[0]
    result = executor.stop()

    assert owned.terminate_calls == 1
    assert result.had_owned_process is True
    assert result.stopped is True
    assert getattr(executor, "_owned_process", None) is None


def test_red_4_stop_without_owned_handle_fails_closed():
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)

    result = executor.stop()

    assert result.had_owned_process is False
    assert result.stopped is False
    assert runner.processes == []


def test_red_5_existing_play_execution_contract_remains_compatible(tmp_path: Path):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)

    result = executor.play(track)

    assert isinstance(result, LocalMusicPlaybackExecution)
    assert result.path == track.resolve()
    assert result.command == ("player",)
    assert result.started is True
    assert runner.calls == [["player", str(track.resolve())]]


def test_red_6_explicit_stop_phrase_reaches_existing_executor(tmp_path: Path):
    track = tmp_path / "Track.mp3"
    track.write_bytes(b"music")
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)
    interceptor = _interceptor(tmp_path, executor)

    started = interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-stop",
            text="reproducí música Track",
        ),
        now=datetime(2026, 10, 4, tzinfo=timezone.utc),
    )
    stopped = interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-stop",
            text="detené la música",
        ),
        now=datetime(2026, 10, 4, tzinfo=timezone.utc),
    )

    assert started is not None
    assert stopped is not None
    assert runner.processes[0].terminate_calls == 1
    assert "det" in stopped.response_text.casefold()
    assert "música" in stopped.response_text.casefold()


def test_red_7_stop_does_not_require_catalogue_selection(tmp_path: Path):
    runner = ControllableRunner()
    executor = LocalCommandMusicPlaybackExecutor(("player",), runner=runner)
    interceptor = _interceptor(tmp_path, executor)

    result = interceptor.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="music-stop",
            text="detené la música",
        ),
        now=datetime(2026, 10, 4, tzinfo=timezone.utc),
    )

    assert result is not None
    assert runner.calls == []
    assert "reproducción" in result.response_text.casefold()


def test_red_8_no_os_process_discovery_or_parallel_playback_authority():
    executor_source = inspect.getsource(LocalCommandMusicPlaybackExecutor)
    wiring_source = inspect.getsource(GovernedLocalMusicCatalogueInterceptionPort)

    forbidden = (
        "tasklist",
        "taskkill",
        "psutil",
        "wmic",
        "PlayerManager",
        "PlaybackSessionManager",
        "MusicManager",
    )
    assert all(token not in executor_source for token in forbidden)
    assert all(token not in wiring_source for token in forbidden)


def test_red_9_richer_controls_remain_out_of_scope():
    executor_source = inspect.getsource(LocalCommandMusicPlaybackExecutor)
    wiring_source = inspect.getsource(GovernedLocalMusicCatalogueInterceptionPort)

    forbidden_methods = (
        "def pause(",
        "def resume(",
        "def next(",
        "def previous(",
        "def set_volume(",
    )
    assert all(token not in executor_source for token in forbidden_methods)
    assert all(token not in wiring_source for token in forbidden_methods)
