from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path


class LongLivedRuntimeStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class LongLivedRuntimeConfig:
    lease_path: Path | str = Path(".roby/runtime.lease")
    heartbeat_path: Path | str = Path(".roby/runtime_heartbeat.json")
    heartbeat_interval: timedelta = timedelta(seconds=30)
    stale_after: timedelta = timedelta(minutes=2)

    def __post_init__(self) -> None:
        lease_path = Path(self.lease_path)
        heartbeat_path = Path(self.heartbeat_path)
        if self.heartbeat_interval.total_seconds() <= 0:
            raise ValueError("heartbeat interval must be positive")
        if self.stale_after < self.heartbeat_interval:
            raise ValueError("stale threshold must cover heartbeat interval")
        object.__setattr__(self, "lease_path", lease_path)
        object.__setattr__(self, "heartbeat_path", heartbeat_path)


@dataclass(frozen=True)
class LongLivedRuntimeState:
    owner: str
    session_id: str
    process_id: int
    status: LongLivedRuntimeStatus | str
    generation: int = 1
    started_at: datetime | None = None
    heartbeat_at: datetime | None = None
    stopped_at: datetime | None = None
    failure: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        status = LongLivedRuntimeStatus(self.status)
        if not self.owner.strip() or not self.session_id.strip():
            raise ValueError("long-lived runtime identity must be complete")
        if self.process_id < 1 or self.generation < 1:
            raise ValueError(
                "long-lived runtime process and generation must be positive"
            )
        for value in (
            self.started_at,
            self.heartbeat_at,
            self.stopped_at,
            self.updated_at,
        ):
            if value is not None and value.tzinfo is None:
                raise ValueError("long-lived runtime time must be timezone-aware")
        if status in {LongLivedRuntimeStatus.RUNNING, LongLivedRuntimeStatus.DEGRADED}:
            if self.started_at is None or self.heartbeat_at is None:
                raise ValueError("active long-lived runtime requires lifecycle times")
        if status is LongLivedRuntimeStatus.STOPPED and self.stopped_at is None:
            raise ValueError("stopped long-lived runtime requires stop time")
        if status is LongLivedRuntimeStatus.FAILED and not (self.failure or "").strip():
            raise ValueError("failed long-lived runtime requires failure detail")
        object.__setattr__(self, "owner", self.owner.strip())
        object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "status", status)
