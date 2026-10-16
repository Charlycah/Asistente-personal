from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


class LocalRuntimeStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class LocalRuntimeBootstrapConfig:
    owner: str
    session_id: str = "desktop-main"
    state_path: Path | str = Path(".roby/runtime_state.json")

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner:
            raise ValueError("local runtime owner must not be blank")
        if not session_id:
            raise ValueError("local runtime session id must not be blank")
        path = Path(self.state_path)
        if not str(path).strip():
            raise ValueError("local runtime state path must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "state_path", path)


@dataclass(frozen=True)
class LocalRuntimeState:
    owner: str
    session_id: str
    status: LocalRuntimeStatus | str
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    failure: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        status = LocalRuntimeStatus(self.status)
        if self.updated_at.tzinfo is None:
            raise ValueError("local runtime update time must be timezone-aware")
        for value in (self.started_at, self.stopped_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("local runtime lifecycle time must be timezone-aware")
        if status is LocalRuntimeStatus.RUNNING and self.started_at is None:
            raise ValueError("running local runtime requires start time")
        if status is LocalRuntimeStatus.STOPPED and self.stopped_at is None:
            raise ValueError("stopped local runtime requires stop time")
        if status is LocalRuntimeStatus.FAILED and not (self.failure or "").strip():
            raise ValueError("failed local runtime requires failure detail")
        object.__setattr__(self, "status", status)
