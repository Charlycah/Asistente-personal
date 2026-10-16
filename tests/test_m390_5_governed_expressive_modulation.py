from datetime import UTC, datetime

import pytest

from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptivePersonalityAuthority,
    AdaptivePersonalityRequest,
    AdaptiveResponseDetail,
    AdaptiveResponseStructure,
)
from core.cognitive_maturity import (
    GovernedExpressiveModulation,
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
from core.stable_personality import (
    PersonalityExpression,
    PersonalityTrait,
    StablePersonalitySnapshot,
)

NOW = datetime(2026, 8, 7, 10, 0, tzinfo=UTC)


def stable(
    expression: PersonalityExpression = PersonalityExpression.NEUTRAL,
) -> StablePersonalitySnapshot:
    return StablePersonalitySnapshot(
        expression=expression,
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
        created_at=NOW,
        snapshot_id="stable-m390-5",
    )


def inner_state(
    *,
    tone: SimulatedAffectiveTone,
    concern: SimulatedConcernLevel,
    dominant: SimulatedDominantState,
):
    signal = SimulatedInnerStateSignal(
        source_authority="m390_5_test_source",
        source_reference="explicit-signal",
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=tone,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=concern,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=dominant,
        evidence_codes=("explicit_m390_5_test_evidence",),
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def test_m390_5_missing_inner_state_does_not_modulate_request() -> None:
    base = AdaptivePersonalityRequest(task_complexity=0.8, urgency=0.2)
    result = GovernedExpressiveModulation().modulate(None, base)
    assert result == base
    assert result.affective_delivery_tone is None
    assert result.affective_source_reference is None


def test_m390_5_supportive_state_can_offer_warm_delivery_signal() -> None:
    snapshot = inner_state(
        tone=SimulatedAffectiveTone.POSITIVE,
        concern=SimulatedConcernLevel.LOW,
        dominant=SimulatedDominantState.SUPPORTIVE,
    )
    request = GovernedExpressiveModulation().modulate(snapshot)
    assert request.affective_delivery_tone is AdaptiveDeliveryTone.WARM
    assert request.affective_source_reference == snapshot.snapshot_id
    profile = AdaptivePersonalityAuthority().adapt(stable(), request)
    assert profile.normalized_tone is AdaptiveDeliveryTone.WARM
    assert profile.stable_expression is PersonalityExpression.NEUTRAL
    assert profile.identity_changed is False
    assert "simulated_affective_modulation_applied" in profile.rationale


def test_m390_5_concerned_state_is_limited_to_careful_delivery() -> None:
    snapshot = inner_state(
        tone=SimulatedAffectiveTone.NEGATIVE,
        concern=SimulatedConcernLevel.HIGH,
        dominant=SimulatedDominantState.CONCERNED,
    )
    request = GovernedExpressiveModulation().modulate(snapshot)
    assert request.affective_delivery_tone is AdaptiveDeliveryTone.CAREFUL
    profile = AdaptivePersonalityAuthority().adapt(stable(), request)
    assert profile.normalized_tone is AdaptiveDeliveryTone.CAREFUL


def test_m390_5_explicit_detail_and_structure_are_preserved() -> None:
    snapshot = inner_state(
        tone=SimulatedAffectiveTone.POSITIVE,
        concern=SimulatedConcernLevel.NONE,
        dominant=SimulatedDominantState.ENCOURAGED,
    )
    base = AdaptivePersonalityRequest(
        requested_detail=AdaptiveResponseDetail.BRIEF,
        requested_structure=AdaptiveResponseStructure.PLAIN,
    )
    request = GovernedExpressiveModulation().modulate(snapshot, base)
    profile = AdaptivePersonalityAuthority().adapt(stable(), request)
    assert profile.normalized_detail is AdaptiveResponseDetail.BRIEF
    assert profile.normalized_structure is AdaptiveResponseStructure.PLAIN


def test_m390_5_stable_repairing_expression_keeps_priority() -> None:
    snapshot = inner_state(
        tone=SimulatedAffectiveTone.POSITIVE,
        concern=SimulatedConcernLevel.NONE,
        dominant=SimulatedDominantState.SUPPORTIVE,
    )
    request = GovernedExpressiveModulation().modulate(snapshot)
    profile = AdaptivePersonalityAuthority().adapt(
        stable(PersonalityExpression.REPAIRING),
        request,
    )
    assert profile.normalized_tone is AdaptiveDeliveryTone.REPAIRING


def test_m390_5_affective_input_cannot_request_direct_or_repairing() -> None:
    with pytest.raises(ValueError):
        AdaptivePersonalityRequest(
            affective_delivery_tone=AdaptiveDeliveryTone.DIRECT,
            affective_source_reference="inner-state",
        )
    with pytest.raises(ValueError):
        AdaptivePersonalityRequest(
            affective_delivery_tone=AdaptiveDeliveryTone.REPAIRING,
            affective_source_reference="inner-state",
        )
