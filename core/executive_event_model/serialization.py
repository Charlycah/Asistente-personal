from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from core.executive_event_model.models import (
    AmbientObservationEvent,
    BatteryLowEvent,
    ExecutiveEvent,
    GenericTextEvent,
    ImportantEmailEvent,
    ReminderDueEvent,
    VerifiedNewsEvent,
    VisualCaptureResultEvent,
)

_EVENT_TYPES: dict[str, type[ExecutiveEvent]] = {
    event_type.__name__: event_type
    for event_type in (
        ExecutiveEvent,
        GenericTextEvent,
        BatteryLowEvent,
        ReminderDueEvent,
        AmbientObservationEvent,
        VerifiedNewsEvent,
        ImportantEmailEvent,
        VisualCaptureResultEvent,
    )
}


def _to_plain_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {key: _to_plain_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_plain_value(item) for item in value]
    return value


def event_to_dict(event: ExecutiveEvent) -> dict[str, Any]:
    data = {
        field_info.name: _to_plain_value(getattr(event, field_info.name))
        for field_info in fields(event)
    }
    data["event_type"] = type(event).__name__
    data["schema_version"] = 1
    return data


def event_from_dict(data: Mapping[str, Any]) -> ExecutiveEvent:
    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise ValueError("unsupported executive event schema version")
    event_type_name = data.get("event_type")
    if not isinstance(event_type_name, str) or event_type_name not in _EVENT_TYPES:
        raise ValueError("unknown executive event type")
    event_type = _EVENT_TYPES[event_type_name]
    event_data = {
        key: value
        for key, value in data.items()
        if key not in {"event_type", "schema_version"}
    }
    for timestamp_name in ("occurred_at", "expires_at"):
        value = event_data.get(timestamp_name)
        if isinstance(value, str):
            event_data[timestamp_name] = datetime.fromisoformat(value)
    event_fields = {field_info.name: field_info for field_info in fields(event_type)}
    accepted_fields = {
        field_name for field_name, field_info in event_fields.items() if field_info.init
    }
    fixed_fields = set(event_fields) - accepted_fields
    unexpected_fields = set(event_data) - set(event_fields)
    if unexpected_fields:
        names = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"unexpected executive event fields: {names}")
    for field_name in fixed_fields:
        serialized_value = event_data.pop(field_name, None)
        expected_value = _to_plain_value(event_fields[field_name].default)
        if serialized_value != expected_value:
            raise ValueError(f"executive event field is inconsistent: {field_name}")
    return event_type(**event_data)
