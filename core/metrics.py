class MetricsCollector:
    def __init__(self):
        self.counters = {
            "errors_total": 0,
            "retries_total": 0,
            "fallbacks_total": 0,
            "recoveries_total": 0,
            "user_visible_errors_total": 0,
            "tool_failures_total": 0,
        }

    def increment(self, metric: str) -> None:
        if metric not in self.counters:
            self.counters[metric] = 0

        self.counters[metric] += 1

    def snapshot(self) -> dict:
        return self.counters.copy()


metrics = MetricsCollector()
