from core.telemetry import TelemetryEvent


class ObservabilityCollector:
    def __init__(self):
        self.counters = {
            "requests_total": 0,
            "requests_completed": 0,
            "requests_failed": 0,
            "fallbacks_total": 0,
            "retries_total": 0,
            "errors_total": 0,
            "tool_failures_total": 0,
        }
        self.events: list[TelemetryEvent] = []

    def record_event(self, event: TelemetryEvent) -> None:
        self.events.append(event)

        if event.name == "request_completed":
            self.counters["requests_total"] += 1
            self.counters["requests_completed"] += 1

        elif event.name == "request_failed":
            self.counters["requests_total"] += 1
            self.counters["requests_failed"] += 1

        elif event.name == "fallback_used":
            self.counters["fallbacks_total"] += 1

        elif event.name == "retry_used":
            self.counters["retries_total"] += 1

        elif event.name == "error_recorded":
            self.counters["errors_total"] += 1

        elif event.name == "tool_failed":
            self.counters["tool_failures_total"] += 1

    def snapshot(self) -> dict:
        return self.counters.copy()

    def recent_events(self, limit: int = 10) -> list[TelemetryEvent]:
        return self.events[-limit:]
