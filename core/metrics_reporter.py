def calculate_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def build_metrics_report(snapshot: dict) -> dict:
    requests_total = snapshot.get("requests_total", 0)

    error_rate = calculate_rate(
        snapshot.get("requests_failed", 0),
        requests_total,
    )

    fallback_rate = calculate_rate(
        snapshot.get("fallbacks_total", 0),
        requests_total,
    )

    retry_rate = calculate_rate(
        snapshot.get("retries_total", 0),
        requests_total,
    )

    return {
        "summary": {
            "requests_total": requests_total,
            "requests_completed": snapshot.get("requests_completed", 0),
            "requests_failed": snapshot.get("requests_failed", 0),
            "error_rate": error_rate,
            "fallback_rate": fallback_rate,
            "retry_rate": retry_rate,
        },
        "raw": snapshot,
    }
