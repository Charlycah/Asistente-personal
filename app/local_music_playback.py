from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
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
        if self.active_path is not None and not self.stop().stopped:
            raise RuntimeError("No se pudo detener la pista anterior")
        self._owned_process = self.runner(
            [*self.command, str(resolved)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._owned_path = resolved
        return LocalMusicPlaybackExecution(
            path=resolved,
            command=self.command,
            started=True,
        )

    def adjust_volume(self, delta: float) -> float | None:
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
                    level = min(1.0, max(0.0, volume.GetMasterVolume() + delta))
                    volume.SetMasterVolume(level, None)
                    return level
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
        return LocalMusicPlaybackStopExecution(
            had_owned_process=True,
            stopped=True,
        )
