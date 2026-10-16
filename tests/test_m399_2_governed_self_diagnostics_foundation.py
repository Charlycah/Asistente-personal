from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticAnomalyStatus,
    DiagnosticObservation,
    DiagnosticThreshold,
    DiagnosticTrendDirection,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 10, 13, 0, tzinfo=timezone.utc)


def _observation(
    index: int,
    value: float,
    **overrides: object,
) -> DiagnosticObservation:
    values: dict[str, object] = {
        "observation_id": f"obs-{index}",
        "source_authority": "runtime_health_readiness",
        "metric": "failed_residents",
        "value": value,
        "observed_at": NOW + timedelta(minutes=index),
        "evidence_codes": (f"runtime_snapshot:{index}",),
    }
    values.update(overrides)
    return DiagnosticObservation(**values)  # type: ignore[arg-type]


def test_m399_2_observation_requires_explicit_identity_and_source() -> None:
    with pytest.raises(ValueError, match="observation_id"):
        _observation(1, 0.0, observation_id=" ")
    with pytest.raises(ValueError, match="source_authority"):
        _observation(1, 0.0, source_authority=" ")


def test_m399_2_observation_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _observation(1, 0.0, observed_at=datetime(2026, 8, 10, 13, 0))


def test_m399_2_foundation_has_single_explicit_authority_id() -> None:
    diagnostic = GovernedSelfDiagnostics()
    assert diagnostic.authority_id == "self_diagnostics"


def test_m399_2_requires_explicit_observations() -> None:
    with pytest.raises(ValueError, match="explicit observations"):
        GovernedSelfDiagnostics().diagnose(())


def test_m399_2_does_not_merge_different_source_authorities() -> None:
    observations = (
        _observation(1, 0.0),
        _observation(2, 1.0, source_authority="provider_health"),
    )
    with pytest.raises(ValueError, match="source authorities"):
        GovernedSelfDiagnostics().diagnose(observations)


def test_m399_2_does_not_merge_different_metrics() -> None:
    observations = (
        _observation(1, 0.0),
        _observation(2, 1.0, metric="failed_requests"),
    )
    with pytest.raises(ValueError, match="different metrics"):
        GovernedSelfDiagnostics().diagnose(observations)


def test_m399_2_rejects_duplicate_evidence_ids() -> None:
    observations = (
        _observation(1, 0.0),
        _observation(2, 1.0, observation_id="obs-1"),
    )
    with pytest.raises(ValueError, match="ids must be unique"):
        GovernedSelfDiagnostics().diagnose(observations)


def test_m399_2_one_sample_is_insufficient_for_trend() -> None:
    report = GovernedSelfDiagnostics().diagnose((_observation(1, 1.0),))
    assert report.trend.direction is DiagnosticTrendDirection.INSUFFICIENT_EVIDENCE
    assert report.trend.sample_count == 1


def test_m399_2_detects_increasing_trend_from_explicit_values() -> None:
    report = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 0.0), _observation(2, 1.0), _observation(3, 2.0))
    )
    assert report.trend.direction is DiagnosticTrendDirection.INCREASING
    assert report.trend.first_value == 0.0
    assert report.trend.last_value == 2.0


def test_m399_2_detects_decreasing_and_stable_trends() -> None:
    decreasing = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 2.0), _observation(2, 1.0))
    )
    stable = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 2.0), _observation(2, 2.0))
    )
    assert decreasing.trend.direction is DiagnosticTrendDirection.DECREASING
    assert stable.trend.direction is DiagnosticTrendDirection.STABLE


def test_m399_2_threshold_must_match_metric() -> None:
    threshold = DiagnosticThreshold(metric="latency_ms", limit=500.0, direction="above")
    with pytest.raises(ValueError, match="must match"):
        GovernedSelfDiagnostics().diagnose((_observation(1, 0.0),), threshold=threshold)


def test_m399_2_anomaly_requires_reproducible_consecutive_violations() -> None:
    threshold = DiagnosticThreshold(
        metric="failed_residents",
        limit=0.0,
        direction="above",
        minimum_consecutive_samples=2,
    )
    report = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 0.0), _observation(2, 1.0), _observation(3, 1.0)),
        threshold=threshold,
    )
    assert report.anomaly is not None
    assert report.anomaly.status is DiagnosticAnomalyStatus.OBSERVED
    assert report.anomaly.consecutive_violations == 2
    assert report.anomaly.observation_ids == ("obs-2", "obs-3")


def test_m399_2_single_violation_does_not_satisfy_two_sample_policy() -> None:
    threshold = DiagnosticThreshold(
        metric="failed_residents",
        limit=0.0,
        direction="above",
        minimum_consecutive_samples=2,
    )
    report = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 0.0), _observation(2, 1.0)),
        threshold=threshold,
    )
    assert report.anomaly is not None
    assert report.anomaly.status is DiagnosticAnomalyStatus.CLEAR
    assert report.anomaly.consecutive_violations == 1


def test_m399_2_anomaly_preserves_no_cause_inference_boundary() -> None:
    threshold = DiagnosticThreshold(
        metric="failed_residents",
        limit=0.0,
        direction="above",
    )
    report = GovernedSelfDiagnostics().diagnose(
        (_observation(1, 1.0),), threshold=threshold
    )
    assert report.anomaly is not None
    assert "no_cause_inferred" in report.anomaly.rationale
    assert "no_corrective_action_performed" in report.anomaly.rationale
    for forbidden in ("cause", "hypothesis", "fix", "patch", "proposal", "sandbox"):
        assert not hasattr(report, forbidden)


def test_m399_2_exposes_no_mutation_or_background_methods() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in (
        "repair",
        "fix",
        "patch",
        "apply",
        "propose",
        "sandbox",
        "start",
        "stop",
        "poll",
        "monitor",
        "run_forever",
    ):
        assert not hasattr(diagnostic, name)


def test_m399_2_does_not_replace_existing_unified_brain_diagnostics() -> None:
    source = Path("app/unified_brain.py").read_text(encoding="utf-8")
    assert "class UnifiedBrainDiagnosticSnapshot" in source
    assert "def diagnostics" in source


def test_m399_2_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M399_2_GOVERNED_SELF_DIAGNOSTICS_FOUNDATION.md").read_text(
        encoding="utf-8"
    )
    assert "Observación → tendencia → anomalía" in document
    assert "predicción ≠ certeza" in document
    assert "no formula hipótesis" in document
    assert "UnifiedBrain.diagnostics" in document
    assert "Milestone M399.2 — Governed Self-Diagnostics Foundation" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.2 — Governed Self-Diagnostics Foundation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.2 — Regla de Self-Diagnostics gobernado" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
