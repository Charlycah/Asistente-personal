from core.metrics_reporter import build_metrics_report


def get_health_status(snapshot: dict) -> dict:
    report = build_metrics_report(snapshot)
    error_rate = report["summary"]["error_rate"]

    if error_rate >= 0.5:
        status = "unhealthy"
    elif error_rate >= 0.1:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "error_rate": error_rate,
    }
