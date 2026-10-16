from core.health import get_health_status
from core.metrics_reporter import build_metrics_report
from core.observability import ObservabilityCollector
from core.telemetry import TelemetryEvent


def test_observability_collector_records_completed_request():
    collector = ObservabilityCollector()

    collector.record_event(
        TelemetryEvent(
            name="request_completed",
            component="roby",
        )
    )

    snapshot = collector.snapshot()

    assert snapshot["requests_total"] == 1
    assert snapshot["requests_completed"] == 1
    assert snapshot["requests_failed"] == 0


def test_observability_collector_records_failed_request():
    collector = ObservabilityCollector()

    collector.record_event(
        TelemetryEvent(
            name="request_failed",
            component="roby",
        )
    )

    snapshot = collector.snapshot()

    assert snapshot["requests_total"] == 1
    assert snapshot["requests_failed"] == 1


def test_metrics_reporter_calculates_error_rate():
    snapshot = {
        "requests_total": 10,
        "requests_completed": 8,
        "requests_failed": 2,
        "fallbacks_total": 1,
        "retries_total": 3,
    }

    report = build_metrics_report(snapshot)

    assert report["summary"]["error_rate"] == 0.2
    assert report["summary"]["fallback_rate"] == 0.1
    assert report["summary"]["retry_rate"] == 0.3


def test_health_status_is_healthy_when_error_rate_is_low():
    snapshot = {
        "requests_total": 10,
        "requests_completed": 10,
        "requests_failed": 0,
    }

    health = get_health_status(snapshot)

    assert health["status"] == "healthy"
    assert health["error_rate"] == 0.0


def test_health_status_is_degraded_when_error_rate_is_medium():
    snapshot = {
        "requests_total": 10,
        "requests_completed": 8,
        "requests_failed": 2,
    }

    health = get_health_status(snapshot)

    assert health["status"] == "degraded"
    assert health["error_rate"] == 0.2


def test_health_status_is_unhealthy_when_error_rate_is_high():
    snapshot = {
        "requests_total": 10,
        "requests_completed": 4,
        "requests_failed": 6,
    }

    health = get_health_status(snapshot)

    assert health["status"] == "unhealthy"
    assert health["error_rate"] == 0.6
