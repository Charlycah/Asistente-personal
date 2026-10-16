from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import (
    OperationalTraceEvent,
    OperationalTraceEventType,
    OperationalTraceStatus,
)
from .store import OperationalTraceStore


class OperationalTraceRecorder:
    def __init__(self, store: OperationalTraceStore) -> None:
        self.store = store

    def start_turn(
        self,
        *,
        owner: str,
        session_id: str,
        turn_sequence: int,
        now: datetime | None = None,
    ) -> OperationalTraceEvent:
        event = OperationalTraceEvent(
            owner=owner,
            session_id=session_id,
            turn_sequence=turn_sequence,
            event_sequence=1,
            event_type=OperationalTraceEventType.TURN_STARTED,
            status=OperationalTraceStatus.STARTED,
            module="end_to_end_local_conversation",
            created_at=now or datetime.now(timezone.utc),
        )
        self.store.append(event)
        return event

    def finish_pipeline(
        self,
        *,
        started: OperationalTraceEvent,
        turn: Any,
        platform_mutation_performed: bool,
        now: datetime | None = None,
    ) -> OperationalTraceEvent:
        event = OperationalTraceEvent(
            owner=started.owner,
            session_id=started.session_id,
            turn_sequence=started.turn_sequence,
            event_sequence=2,
            event_type=OperationalTraceEventType.PIPELINE_FINISHED,
            status=OperationalTraceStatus(turn.status.value),
            module="governed_operational_conversation_pipeline",
            created_at=now or turn.created_at,
            trace_id=started.trace_id,
            parent_event_id=started.event_id,
            turn_id=turn.turn_id,
            pipeline_result_id=turn.pipeline_result_id,
            operational_response_id=turn.operational_response_id,
            provider_call_performed=turn.provider_call_performed,
            retrieval_performed=turn.retrieval_performed,
            network_access_performed=turn.network_access_performed,
            platform_mutation_performed=platform_mutation_performed,
        )
        self.store.append(event)
        return event

    def record_persistence(
        self,
        *,
        pipeline_event: OperationalTraceEvent,
        turn: Any,
        now: datetime | None = None,
    ) -> OperationalTraceEvent:
        event = OperationalTraceEvent(
            owner=pipeline_event.owner,
            session_id=pipeline_event.session_id,
            turn_sequence=pipeline_event.turn_sequence,
            event_sequence=3,
            event_type=OperationalTraceEventType.TURN_PERSISTED,
            status=OperationalTraceStatus.PERSISTED,
            module="local_conversation_journal",
            created_at=now or datetime.now(timezone.utc),
            trace_id=pipeline_event.trace_id,
            parent_event_id=pipeline_event.event_id,
            turn_id=turn.turn_id,
            pipeline_result_id=turn.pipeline_result_id,
            operational_response_id=turn.operational_response_id,
            metadata={"journal": "jsonl"},
        )
        self.store.append(event)
        return event
