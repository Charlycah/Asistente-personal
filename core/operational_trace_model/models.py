from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Mapping


class OperationalTraceEventType(str, Enum):
    TURN_STARTED = "turn_started"
    PIPELINE_FINISHED = "pipeline_finished"
    TURN_PERSISTED = "turn_persisted"
    TURN_FAILED = "turn_failed"


class OperationalTraceStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    PARTIAL = "partial"
    WITHHELD = "withheld"
    FAILED = "failed"
    PERSISTED = "persisted"


@dataclass(frozen=True)
class OperationalTraceEvent:
    owner: str
    session_id: str
    turn_sequence: int
    event_sequence: int
    event_type: OperationalTraceEventType | str
    status: OperationalTraceStatus | str
    module: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str = ""
    event_id: str = ""
    parent_event_id: str = ""
    turn_id: str = ""
    pipeline_result_id: str = ""
    operational_response_id: str = ""
    provider_call_performed: bool = False
    retrieval_performed: bool = False
    network_access_performed: bool = False
    platform_mutation_performed: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        module = self.module.strip()
        event_type = OperationalTraceEventType(self.event_type)
        status = OperationalTraceStatus(self.status)
        metadata = {
            str(key).strip(): str(value).strip() for key, value in self.metadata.items()
        }
        if not owner or not session_id or not module:
            raise ValueError("operational trace identity must be complete")
        if self.turn_sequence < 1 or self.event_sequence < 1:
            raise ValueError("operational trace sequences must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("operational trace time must be timezone-aware")
        if any(not key or not value for key, value in metadata.items()):
            raise ValueError("operational trace metadata must be complete")
        expected_trace_id = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    str(self.turn_sequence),
                    self.created_at.isoformat()
                    if self.event_sequence == 1
                    else self.trace_id,
                )
            ).encode()
        ).hexdigest()
        trace_id = self.trace_id or expected_trace_id
        if self.event_sequence > 1 and not self.trace_id:
            raise ValueError("subsequent operational events require trace lineage")
        if (
            self.event_sequence == 1
            and self.trace_id
            and self.trace_id != expected_trace_id
        ):
            raise ValueError("operational trace id is inconsistent")
        if self.event_sequence == 1 and self.parent_event_id:
            raise ValueError("first operational event cannot have a parent")
        if self.event_sequence > 1 and not self.parent_event_id:
            raise ValueError("subsequent operational events require a parent")
        expected_event_id = sha256(
            "|".join(
                (
                    trace_id,
                    str(self.event_sequence),
                    event_type.value,
                    status.value,
                    module,
                    self.created_at.isoformat(),
                    self.parent_event_id,
                    self.turn_id,
                    self.pipeline_result_id,
                    self.operational_response_id,
                    *[f"{key}={metadata[key]}" for key in sorted(metadata)],
                )
            ).encode()
        ).hexdigest()
        if self.event_id and self.event_id != expected_event_id:
            raise ValueError("operational event id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "module", module)
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "trace_id", trace_id)
        object.__setattr__(self, "event_id", expected_event_id)


@dataclass(frozen=True)
class OperationalTurnTrace:
    events: tuple[OperationalTraceEvent, ...]

    def __post_init__(self) -> None:
        if not self.events:
            raise ValueError("operational turn trace must contain events")
        first = self.events[0]
        if first.event_type is not OperationalTraceEventType.TURN_STARTED:
            raise ValueError("operational turn trace must start explicitly")
        for index, event in enumerate(self.events, start=1):
            if event.trace_id != first.trace_id:
                raise ValueError("operational trace lineage must be stable")
            if (event.owner.casefold(), event.session_id, event.turn_sequence) != (
                first.owner.casefold(),
                first.session_id,
                first.turn_sequence,
            ):
                raise ValueError("operational trace turn identity must be stable")
            if event.event_sequence != index:
                raise ValueError("operational trace event sequence must be contiguous")
            if index > 1 and event.parent_event_id != self.events[index - 2].event_id:
                raise ValueError("operational trace causal chain is inconsistent")

    @property
    def trace_id(self) -> str:
        return self.events[0].trace_id

    @property
    def terminal_event(self) -> OperationalTraceEvent:
        return self.events[-1]
