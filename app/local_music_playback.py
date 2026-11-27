from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable


@dataclass(frozen=True)
class LocalMusicPlaybackExecution:
    path: Path
    command: tuple[str, ...]
    started: bool


@dataclass(frozen=True)
class LocalMusicPlaybackStopExecution:
    had_owned_process: bool
    stopped: bool


@dataclass(frozen=True)
class LocalMusicVolumeAdjustment:
    level: float
    changed: bool


class LocalCommandMusicPlaybackExecutor:
    """Execute one already-authorized local track through a configured command."""

    def __init__(
        self,
        command: tuple[str, ...],
        runner: Callable[..., subprocess.Popen] = subprocess.Popen,
    ) -> None:
        if not command:
            raise ValueError("music playback command must not be empty")
        self.command = command
        self.runner = runner
        self._owned_process: object | None = None
        self._owned_path: Path | None = None
        self._playlist: Path | None = None

    @property
    def active_path(self) -> Path | None:
        process = self._owned_process
        if process is None:
            return None
        poll = getattr(process, "poll", None)
        if callable(poll) and poll() is not None:
            return None
        return self._owned_path

    def play(self, path: Path) -> LocalMusicPlaybackExecution:
        resolved = Path(path).resolve(strict=True)
        if not resolved.is_file():
            raise ValueError("music playback path must be a file")
        return self._start(self.command, resolved, resolved)

    def play_loop(self, paths: tuple[Path, ...]) -> LocalMusicPlaybackExecution:
        if Path(self.command[0]).stem.casefold() != "vlc":
            raise ValueError("La reproducción continua requiere VLC")
        if not paths or not all(path.is_absolute() and path.is_file() for path in paths):
            raise ValueError("La lista debe contener pistas locales disponibles")
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".m3u8", prefix="roby-", delete=False
        ) as playlist:
            playlist_path = Path(playlist.name)
            try:
                playlist.write("#EXTM3U\n")
                playlist.writelines(f"{path.as_uri()}\n" for path in paths)
            except OSError:
                # Windows releases the file handle when the context exits.
                playlist.close()
                playlist_path.unlink(missing_ok=True)
                raise

        command = (
            *(arg for arg in self.command if arg != "--play-and-exit"),
            "--no-one-instance",
            "--no-play-and-exit",
            "--no-repeat",
            "--loop",
        )
        try:
            execution = self._start(command, playlist_path, paths[0])
        except (OSError, RuntimeError):
            playlist_path.unlink(missing_ok=True)
            raise
        self._playlist = playlist_path
        return execution

    def _start(
        self, command: tuple[str, ...], media: Path, first_track: Path
    ) -> LocalMusicPlaybackExecution:
        if self.active_path is not None and not self.stop().stopped:
            raise RuntimeError("No se pudo detener la pista anterior")
        self._remove_playlist()
        self._owned_process = self.runner(
            [*command, str(media)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._owned_path = first_track
        return LocalMusicPlaybackExecution(
            path=first_track,
            command=command,
            started=True,
        )

    def _remove_playlist(self) -> None:
        if self._playlist is not None:
            self._playlist.unlink(missing_ok=True)
            self._playlist = None

    def adjust_volume(self, delta: float) -> LocalMusicVolumeAdjustment | None:
        """Adjust only the audio session belonging to the active player."""
        if self.active_path is None:
            return None
        pid = getattr(self._owned_process, "pid", None)
        if pid is None:
            return None

        from comtypes import COMError, CoInitialize, CoUninitialize
        from pycaw.pycaw import AudioUtilities

        CoInitialize()
        try:
            for session in AudioUtilities.GetAllSessions():
                if session.ProcessId == pid:
                    volume = session.SimpleAudioVolume
                    previous = volume.GetMasterVolume()
                    requested = min(1.0, max(0.0, previous + delta))
                    if abs(requested - previous) > 0.0001:
                        volume.SetMasterVolume(requested, None)
                    actual = volume.GetMasterVolume()
                    return LocalMusicVolumeAdjustment(
                        level=actual, changed=abs(actual - previous) > 0.0001
                    )
        except COMError as exc:
            raise OSError("No pude ajustar la sesión de audio del reproductor") from exc
        finally:
            CoUninitialize()
        return None

    def stop(self) -> LocalMusicPlaybackStopExecution:
        process = self._owned_process
        if process is None:
            return LocalMusicPlaybackStopExecution(
                had_owned_process=False,
                stopped=False,
            )
        terminate = getattr(process, "terminate", None)
        if not callable(terminate):
            self._owned_process = None
            return LocalMusicPlaybackStopExecution(
                had_owned_process=True,
                stopped=False,
            )
        try:
            terminate()
            wait = getattr(process, "wait", None)
            if callable(wait):
                wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            return LocalMusicPlaybackStopExecution(had_owned_process=True, stopped=False)
        self._owned_process = None
        self._owned_path = None
        self._remove_playlist()
        return LocalMusicPlaybackStopExecution(
            had_owned_process=True,
            stopped=True,
        )
