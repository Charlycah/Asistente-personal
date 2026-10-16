from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Protocol

from .models import BatteryAwarenessPolicy, BatterySnapshot


class BatterySensor(Protocol):
    def read(self) -> BatterySnapshot | None: ...


class BatteryAwarenessService:
    """Observes battery state and emits governed, non-repetitive interventions."""

    def __init__(
        self,
        sensor: BatterySensor,
        *,
        notify: Callable[[str], None],
        owner: str = "Carlos",
        policy: BatteryAwarenessPolicy | None = None,
        clock: Callable[[], datetime] | None = None,
        wait: Callable[[float], bool] | None = None,
    ) -> None:
        self.sensor = sensor
        self.notify = notify
        self.owner = owner.strip() or "Carlos"
        self.policy = policy or BatteryAwarenessPolicy()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._stop = threading.Event()
        self._wait = wait or self._stop.wait
        self._thread: threading.Thread | None = None
        self._low_episode = False
        self._last_notification_at: datetime | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="roby-battery-awareness",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)
        self._thread = None

    def check_once(self, *, now: datetime | None = None) -> str | None:
        try:
            snapshot = self.sensor.read()
        except Exception:
            return None
        if snapshot is None:
            return None

        timestamp = now or self._clock()
        if timestamp.tzinfo is None:
            raise ValueError("battery awareness time must be timezone-aware")

        recovery_level = self.policy.low_threshold + self.policy.recovery_margin
        if snapshot.charging or snapshot.percent >= recovery_level:
            self._low_episode = False
            self._last_notification_at = None
            return None
        if snapshot.percent > self.policy.low_threshold:
            return None

        should_notify = not self._low_episode
        if self._last_notification_at is not None:
            should_notify = (
                timestamp - self._last_notification_at >= self.policy.repeat_after
            )
        self._low_episode = True
        if not should_notify:
            return None

        self._last_notification_at = timestamp
        message = (
            f"{self.owner}, la batería está en {snapshot.percent} %. "
            "Conviene conectar el cargador."
        )
        self.notify(message)
        return message

    def _run(self) -> None:
        self.check_once()
        interval = self.policy.poll_interval.total_seconds()
        while not self._wait(interval):
            self.check_once()
