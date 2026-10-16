from __future__ import annotations

from core.cognitive_maturity import (
    ExplicitInnerContinuityEvaluator,
    ExplicitInnerContinuityKind,
    ExplicitInnerContinuityStatus,
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
    UnifiedEpistemicCategory,
)


def _snapshot(
    reference: str,
    *,
    dominant: SimulatedDominantState = SimulatedDominantState.ATTENTIVE,
    concern: SimulatedConcernLevel = SimulatedConcernLevel.NONE,
):
    signal = SimulatedInnerStateSignal(
        source_authority="test_certified_source",
        source_reference=reference,
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=SimulatedAffectiveTone.NEUTRAL,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=concern,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=dominant,
        evidence_codes=(f"evidence:{reference}",),
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def test_m390_3_requires_two_explicit_snapshots() -> None:
    report = ExplicitInnerContinuityEvaluator().compare(None, _snapshot("current"))
    assert report.status is ExplicitInnerContinuityStatus.INSUFFICIENT_EVIDENCE
    assert report.continuity is ExplicitInnerContinuityKind.UNAVAILABLE
    assert report.changed_fields == ()
    assert "missing_explicit_previous_snapshot" in report.uncertainty_codes


def test_m390_3_reports_unchanged_affective_state_without_hidden_history() -> None:
    previous = _snapshot("previous")
    current = _snapshot("current")
    report = ExplicitInnerContinuityEvaluator().compare(previous, current)
    assert report.status is ExplicitInnerContinuityStatus.COMPLETE
    assert report.continuity is ExplicitInnerContinuityKind.UNCHANGED
    assert report.changed_fields == ()
    assert len(report.unchanged_fields) == 6
    assert "source_changed_without_affective_change" in report.evidence_codes


def test_m390_3_reports_explicit_affective_changes() -> None:
    previous = _snapshot("previous")
    current = _snapshot(
        "current",
        dominant=SimulatedDominantState.CONCERNED,
        concern=SimulatedConcernLevel.MODERATE,
    )
    report = ExplicitInnerContinuityEvaluator().compare(previous, current)
    assert report.continuity is ExplicitInnerContinuityKind.CHANGED
    assert report.changed_fields == ("concern_level", "dominant_state")


def test_m390_3_is_deterministic_and_stateless() -> None:
    previous = _snapshot("previous")
    current = _snapshot("current")
    evaluator = ExplicitInnerContinuityEvaluator()
    first = evaluator.compare(previous, current)
    second = evaluator.compare(previous, current)
    assert first == second
    assert evaluator.compare(None, current).continuity is (
        ExplicitInnerContinuityKind.UNAVAILABLE
    )
