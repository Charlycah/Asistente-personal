from dataclasses import replace
from datetime import UTC, datetime

from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptivePersonalityAuthority,
)
from core.cognitive_maturity import (
    ExplicitInnerContinuityEvaluator,
    GovernedExpressiveModulation,
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedFunctionalRegulation,
    SimulatedFunctionalRegulationMode,
    SimulatedFunctionalRegulationStatus,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
    UnifiedEpistemicCategory,
)
from core.stable_personality import (
    PersonalityExpression,
    PersonalityTrait,
    StablePersonalitySnapshot,
)


def snapshot(
    *,
    source_authority: str = "functional_psychology",
    tone: SimulatedAffectiveTone = SimulatedAffectiveTone.NEUTRAL,
    activation: SimulatedActivationLevel = SimulatedActivationLevel.MODERATE,
    stability: SimulatedStabilityLevel = SimulatedStabilityLevel.STABLE,
    concern: SimulatedConcernLevel = SimulatedConcernLevel.LOW,
    openness: SimulatedRelationalOpenness = SimulatedRelationalOpenness.BALANCED,
    dominant: SimulatedDominantState = SimulatedDominantState.ATTENTIVE,
    risk_codes: tuple[str, ...] = (),
):
    signal = SimulatedInnerStateSignal(
        source_authority=source_authority,
        source_reference="explicit-source",
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=tone,
        activation_level=activation,
        stability_level=stability,
        concern_level=concern,
        relational_openness=openness,
        dominant_state=dominant,
        evidence_codes=("explicit_m390_6_test_evidence",),
        risk_codes=risk_codes,
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def test_m390_6_missing_current_state_is_not_inferred() -> None:
    report = SimulatedFunctionalRegulation().regulate(None)
    assert report.status is SimulatedFunctionalRegulationStatus.INSUFFICIENT_EVIDENCE
    assert report.mode is SimulatedFunctionalRegulationMode.UNAVAILABLE
    assert report.delivery_tone_limit is None


def test_m390_6_stable_state_passes_through_without_modulation() -> None:
    current = snapshot()
    report = SimulatedFunctionalRegulation().regulate(current)
    assert report.status is SimulatedFunctionalRegulationStatus.COMPLETE
    assert report.mode is SimulatedFunctionalRegulationMode.PASSTHROUGH
    assert report.delivery_tone_limit is None


def test_m390_6_broad_explicit_change_requests_stabilization() -> None:
    previous = snapshot()
    current = snapshot(
        tone=SimulatedAffectiveTone.POSITIVE,
        activation=SimulatedActivationLevel.HIGH,
        concern=SimulatedConcernLevel.MODERATE,
        dominant=SimulatedDominantState.ENCOURAGED,
    )
    continuity = ExplicitInnerContinuityEvaluator().compare(previous, current)
    report = SimulatedFunctionalRegulation().regulate(current, continuity)
    assert len(continuity.changed_fields) >= 3
    assert report.mode is SimulatedFunctionalRegulationMode.STABILIZE
    assert report.delivery_tone_limit is AdaptiveDeliveryTone.CAREFUL
    assert "broad_explicit_change_stabilized" in report.evidence_codes


def test_m390_6_instability_or_risk_is_cautious() -> None:
    current = snapshot(
        stability=SimulatedStabilityLevel.UNSTABLE,
        risk_codes=("explicit_risk",),
    )
    report = SimulatedFunctionalRegulation().regulate(current)
    assert report.mode is SimulatedFunctionalRegulationMode.CAUTIOUS
    assert report.delivery_tone_limit is AdaptiveDeliveryTone.CAREFUL
    assert "explicit_risk" in report.risk_codes


def test_m390_6_single_relational_source_cannot_escalate_expression() -> None:
    current = snapshot(
        source_authority="relational_affective_context",
        tone=SimulatedAffectiveTone.POSITIVE,
        dominant=SimulatedDominantState.SUPPORTIVE,
    )
    report = SimulatedFunctionalRegulation().regulate(current)
    assert report.mode is SimulatedFunctionalRegulationMode.STABILIZE
    assert report.delivery_tone_limit is AdaptiveDeliveryTone.CAREFUL
    assert "single_relational_source_not_allowed_to_escalate" in report.evidence_codes


def test_m390_6_degraded_state_is_not_rewritten() -> None:
    current = SimulatedInnerStateAuthority().evaluate_safely((None,))
    report = SimulatedFunctionalRegulation().regulate(current)
    assert report.status is SimulatedFunctionalRegulationStatus.DEGRADED
    assert report.mode is SimulatedFunctionalRegulationMode.DEGRADED
    assert report.delivery_tone_limit is None


def test_m390_6_regulation_is_deterministic() -> None:
    current = snapshot()
    first = SimulatedFunctionalRegulation().regulate(current)
    second = SimulatedFunctionalRegulation().regulate(current)
    assert first == second
    assert replace(first) == first


def test_m390_6_regulation_can_only_limit_existing_expressive_signal() -> None:
    previous = snapshot()
    current = snapshot(
        tone=SimulatedAffectiveTone.POSITIVE,
        activation=SimulatedActivationLevel.HIGH,
        concern=SimulatedConcernLevel.MODERATE,
        dominant=SimulatedDominantState.ENCOURAGED,
    )
    continuity = ExplicitInnerContinuityEvaluator().compare(previous, current)
    regulation = SimulatedFunctionalRegulation().regulate(current, continuity)
    request = GovernedExpressiveModulation().modulate(
        current,
        regulation=regulation,
    )
    assert request.affective_delivery_tone is AdaptiveDeliveryTone.CAREFUL
    assert request.affective_regulation_reference == regulation.report_id

    stable = StablePersonalitySnapshot(
        expression=PersonalityExpression.NEUTRAL,
        active_traits=(
            PersonalityTrait.CALM,
            PersonalityTrait.PRECISE,
            PersonalityTrait.SUPPORTIVE,
            PersonalityTrait.RESPECTFUL,
            PersonalityTrait.CONSISTENT,
        ),
        consistency_score=0.9,
        reason="identidad estable",
        guidance=("preservar identidad",),
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=UTC),
        snapshot_id="stable-m390-6",
    )
    profile = AdaptivePersonalityAuthority().adapt(stable, request)
    assert profile.normalized_tone is AdaptiveDeliveryTone.CAREFUL
    assert "simulated_functional_regulation_applied" in profile.rationale
