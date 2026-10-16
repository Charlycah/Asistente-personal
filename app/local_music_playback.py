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

    def play(self, path: Path) -> LocalMusicPlaybackExecution:
        resolved = Path(path).resolve(strict=True)
        if not resolved.is_file():
            raise ValueError("music playback path must be a file")
        self._owned_process = self.runner(
            [*self.command, str(resolved)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return LocalMusicPlaybackExecution(
            path=resolved,
            command=self.command,
            started=True,
        )

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
        terminate()
        self._owned_process = None
        return LocalMusicPlaybackStopExecution(
            had_owned_process=True,
            stopped=True,
        )
