from __future__ import annotations

import json
import subprocess
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.ambient_proactive_coordination import (
    AmbientAction,
    AmbientObservation,
    AmbientProactiveCoordinator,
    AmbientSignalKind,
)
from app.conversational_self_analysis import ConversationalSelfAnalysisReport


class AmbientObservationSource(Protocol):
    def observe(self) -> AmbientObservation | None: ...


@dataclass(frozen=True)
class AmbientProactiveRuntimePolicy:
    poll_interval: timedelta = timedelta(seconds=2)

    def __post_init__(self) -> None:
        if self.poll_interval.total_seconds() <= 0:
            raise ValueError("ambient poll interval must be positive")


@dataclass(frozen=True)
class AmbientProactiveRuntimeSnapshot:
    observations: int
    comments_delivered: int
    visual_captures_requested: int
    failures: int
    running: bool


class LocalCommandAmbientObservationSource:
    """Read one ephemeral ambient event from a configured local command."""

    def __init__(self, command: Sequence[str]) -> None:
        self.command = tuple(item for item in command if str(item).strip())
        if not self.command:
            raise ValueError("ambient observation command must not be empty")

    def observe(self) -> AmbientObservation | None:
        completed = subprocess.run(
            self.command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            return None
        raw = completed.stdout.strip()
        if not raw:
            return None
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("ambient observation output must be a JSON object")
        return AmbientObservation(
            kind=AmbientSignalKind(str(payload["kind"])),
            confidence=float(payload["confidence"]),
            summary=str(payload["summary"]),
            occurred_at=_timestamp(payload.get("occurred_at")),
            involves_private_speech=bool(payload.get("involves_private_speech", False)),
            visual_confirmation_helpful=bool(
                payload.get("visual_confirmation_helpful", False)
            ),
        )


class AmbientProactiveRuntime:
    """Run RP.06 inside ROBY's resident lifecycle."""

    def __init__(
        self,
        source: AmbientObservationSource,
        coordinator: AmbientProactiveCoordinator,
        *,
        notify: Callable[[str], None],
        request_visual_capture: Callable[[str], None] | None = None,
        latest_self_analysis: Callable[[], ConversationalSelfAnalysisReport | None]
        | None = None,
        policy: AmbientProactiveRuntimePolicy | None = None,
    ) -> None:
        self.source = source
        self.coordinator = coordinator
        self.notify = notify
        self.request_visual_capture = request_visual_capture
        self.latest_self_analysis = latest_self_analysis or (lambda: None)
        self.policy = policy or AmbientProactiveRuntimePolicy()
        self._observations = 0
        self._comments = 0
        self._visual_requests = 0
        self._failures = 0
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    @property
    def snapshot(self) -> AmbientProactiveRuntimeSnapshot:
        return AmbientProactiveRuntimeSnapshot(
            observations=self._observations,
            comments_delivered=self._comments,
            visual_captures_requested=self._visual_requests,
            failures=self._failures,
            running=self._running,
        )

    def start(self) -> None:
        if self._running:
            return
        self._stop.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            name="roby-ambient-proactive-runtime",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._stop.set()
        if self._thread is not None:
            self._thread.join(
                timeout=max(1.0, self.policy.poll_interval.total_seconds() * 2)
            )
        self._thread = None
        self._running = False

    def tick(self, *, now: datetime | None = None) -> None:
        observation = self.source.observe()
        if observation is None:
            return
        self._observations += 1
        decision = self.coordinator.evaluate(
            observation,
            self_analysis=self.latest_self_analysis(),
            now=now,
        )
        if decision.action is AmbientAction.COMMENT and decision.comment:
            self.notify(decision.comment)
            self._comments += 1
            return
        if (
            decision.action is AmbientAction.REQUEST_VISUAL_CAPTURE
            and decision.camera_reason
            and self.request_visual_capture is not None
        ):
            self.request_visual_capture(decision.camera_reason)
            self._visual_requests += 1

    def _run(self) -> None:
        interval = self.policy.poll_interval.total_seconds()
        while not self._stop.is_set():
            try:
                self.tick(now=datetime.now(timezone.utc))
            except (
                OSError,
                RuntimeError,
                ValueError,
                KeyError,
                TypeError,
                json.JSONDecodeError,
            ):
                self._failures += 1
            self._stop.wait(interval)


def _timestamp(value: object) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(str(value))
    if parsed.tzinfo is None:
        raise ValueError("ambient observation timestamp must be timezone-aware")
    return parsed
