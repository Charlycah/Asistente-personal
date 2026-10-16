from __future__ import annotations

import threading
from collections.abc import Callable

from core.long_lived_runtime_lifecycle import LongLivedRuntimeLifecycle


class RuntimeHeartbeatSupervisor:
    """Maintains lifecycle metadata without performing cognitive work."""

    def __init__(
        self,
        lifecycle: LongLivedRuntimeLifecycle,
        *,
        wait: Callable[[float], bool] | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._wait = wait or self._stop.wait

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="roby-runtime-heartbeat",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)
        self._thread = None

    def _run(self) -> None:
        interval = self.lifecycle.config.heartbeat_interval.total_seconds()
        while not self._wait(interval):
            try:
                if self.lifecycle.is_running:
                    self.lifecycle.heartbeat()
            except Exception as exc:
                if self.lifecycle.is_running:
                    self.lifecycle.mark_degraded(exc)
                return
