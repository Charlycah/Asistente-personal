from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TelemetryEvent:
    name: str
    component: str
    trace_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
