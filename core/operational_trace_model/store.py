from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from core.platform_runtime_compatibility import apply_private_file_permissions

from .models import OperationalTraceEvent, OperationalTurnTrace


@runtime_checkable
class OperationalTraceStore(Protocol):
    def append(self, event: OperationalTraceEvent) -> None: ...
    def list_for_session(
        self, owner: str, session_id: str
    ) -> tuple[OperationalTraceEvent, ...]: ...
    def get_trace(self, trace_id: str) -> OperationalTurnTrace | None: ...


class JsonLinesOperationalTraceStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def append(self, event: OperationalTraceEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": event.created_at.isoformat(),
            "event_id": event.event_id,
            "event_sequence": event.event_sequence,
            "event_type": event.event_type.value,
            "metadata": dict(event.metadata),
            "module": event.module,
            "network_access_performed": event.network_access_performed,
            "operational_response_id": event.operational_response_id,
            "owner": event.owner,
            "parent_event_id": event.parent_event_id,
            "pipeline_result_id": event.pipeline_result_id,
            "platform_mutation_performed": event.platform_mutation_performed,
            "provider_call_performed": event.provider_call_performed,
            "retrieval_performed": event.retrieval_performed,
            "session_id": event.session_id,
            "status": event.status.value,
            "trace_id": event.trace_id,
            "turn_id": event.turn_id,
            "turn_sequence": event.turn_sequence,
        }
        line = json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            os.write(descriptor, line.encode("utf-8"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        apply_private_file_permissions(self.path)

    def list_for_session(
        self, owner: str, session_id: str
    ) -> tuple[OperationalTraceEvent, ...]:
        return tuple(
            event
            for event in self._read_all()
            if event.owner.casefold() == owner.strip().casefold()
            and event.session_id == session_id.strip()
        )

    def get_trace(self, trace_id: str) -> OperationalTurnTrace | None:
        events = tuple(
            event for event in self._read_all() if event.trace_id == trace_id
        )
        if not events:
            return None
        return OperationalTurnTrace(
            tuple(sorted(events, key=lambda item: item.event_sequence))
        )

    def _read_all(self) -> tuple[OperationalTraceEvent, ...]:
        if not self.path.exists():
            return ()
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["created_at"] = datetime.fromisoformat(payload["created_at"])
            events.append(OperationalTraceEvent(**payload))
        return tuple(events)
